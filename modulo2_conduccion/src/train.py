"""Extraer características congeladas y entrenar la referencia multinomial."""

import argparse
import csv
from io import BytesIO
import json
from pathlib import Path
import time
from zipfile import ZipFile

import joblib
import numpy as np
from PIL import Image, ImageOps
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small
import yaml

from .prepare import CLASSES, ROOT, SPLITS, write_csv

import matplotlib.pyplot as plt

WEIGHTS = MobileNet_V3_Small_Weights.IMAGENET1K_V1


class DriverImages(Dataset):
    def __init__(self, archive_path, rows, transform):
        self.archive_path = archive_path
        self.rows = rows
        self.transform = transform
        self.archive = None

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        if self.archive is None:
            self.archive = ZipFile(self.archive_path)
        row = self.rows[index]
        with Image.open(BytesIO(self.archive.read(row["path"]))) as image:
            image.draft("RGB", (256, 256))
            tensor = self.transform(ImageOps.exif_transpose(image).convert("RGB"))
        return tensor, CLASSES.index(row["class"])

    def close(self):
        if self.archive is not None:
            self.archive.close()


def backbone(device):
    model = mobilenet_v3_small(weights=WEIGHTS)
    model.classifier = nn.Identity()
    return model.eval().requires_grad_(False).to(device)


def select_rows(rows, limit, seed):
    if not limit:
        return rows
    rng = np.random.default_rng(seed)
    sample = []
    for split in SPLITS:
        for label in CLASSES:
            candidates = [row for row in rows if row["split"] == split and row["class"] == label]
            sample.extend(candidates[i] for i in rng.permutation(len(candidates))[:limit])
    return sample


def extract(archive_path, rows, config, device):
    model = backbone(device)
    dataset = DriverImages(archive_path, rows, WEIGHTS.transforms())
    loader = DataLoader(dataset, batch_size=config["batch_size"], num_workers=config["workers"])
    features, labels = [], []
    try:
        with torch.inference_mode():
            for i, (images, batch_labels) in enumerate(loader):
                features.append(model(images.to(device)).cpu().numpy())
                labels.append(batch_labels.numpy())
                if i % 50 == 0:
                    print(f"Imágenes procesadas: {min((i + 1) * config['batch_size'], len(rows))}/{len(rows)}",
                          flush=True)
    finally:
        dataset.close()
    return np.concatenate(features), np.concatenate(labels)


def fit(features, labels, c, config, seed):
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=c, solver="lbfgs", max_iter=config["max_iter"], random_state=seed),
    )
    order = np.random.default_rng(seed).permutation(len(labels))
    return model.fit(features[order], labels[order])


def metrics(model, features, labels):
    prediction = model.predict(features)
    return {"accuracy": float(accuracy_score(labels, prediction)),
            "f1_macro": float(f1_score(labels, prediction, average="macro"))}


def dump(path, content):
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/baseline.yaml")
    parser.add_argument("--zip", type=Path, default=ROOT / "data/raw/dataset.zip")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/processed/particiones.csv")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--demo-features", type=Path, default=ROOT / "data/processed/demo_features.npz")
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())
    limit = config["limit_per_class_split"]
    if limit and args.output is None:
        parser.error("Indica --output para guardar la demostración por separado.")
    output = args.output or ROOT
    device = torch.device(config["device"])
    torch.set_num_threads(config["threads"])
    torch.manual_seed(config["seed"])
    with args.manifest.open(newline="", encoding="utf-8") as stream:
        rows = select_rows(list(csv.DictReader(stream)), limit, config["seed"])
    splits = np.asarray([row["split"] for row in rows])
    started = time.perf_counter()
    from_cache = False
    if limit and args.demo_features.exists():
        with np.load(args.demo_features, allow_pickle=False) as cache:
            from_cache = np.array_equal(cache["paths"], [row["path"] for row in rows])
            if from_cache:
                x = cache["features"]
                y = np.asarray([CLASSES.index(row["class"]) for row in rows])
    if not from_cache:
        x, y = extract(args.zip, rows, config, device)
    extraction_seconds = time.perf_counter() - started
    x_train, y_train = x[splits == "train"], y[splits == "train"]
    x_val, y_val = x[splits == "val"], y[splits == "val"]
    x_test, y_test = x[splits == "test"], y[splits == "test"]

    search, repeats = [], []
    with threadpool_limits(limits=config["threads"]):
        for c in config["candidates_c"]:
            start = time.perf_counter()
            current = fit(x_train, y_train, c, config, config["seed"])
            search.append({"C": c, **metrics(current, x_val, y_val), "seconds": time.perf_counter() - start})
        best = max(search, key=lambda row: (row["f1_macro"], -row["C"]))
        model = fit(x_train, y_train, best["C"], config, config["seed"])
        for seed in config["repeat_seeds"]:
            repeated = fit(x_train, y_train, best["C"], config, seed)
            repeats.append({"seed": seed, **metrics(repeated, x_val, y_val)})
        prediction = model.predict(x_test)
        report = classification_report(y_test, prediction, labels=list(range(len(CLASSES))),
                                       target_names=CLASSES, output_dict=True, zero_division=0)
        test = {**metrics(model, x_test, y_test), "report": report,
                "confusion_matrix": confusion_matrix(y_test, prediction, labels=list(range(len(CLASSES)))).tolist()}
    seeds_summary = {}
    for key in ["accuracy", "f1_macro"]:
        values = np.asarray([row[key] for row in repeats])
        seeds_summary[key] = {"mean": float(values.mean()), "std": float(values.std()),
                              "min": float(values.min()), "max": float(values.max())}
    demo_count = config.get("export_demo_per_class_split")
    if demo_count and not limit:
        demo_rows = select_rows(rows, demo_count, config["seed"])
        row_indices = {row["path"]: i for i, row in enumerate(rows)}
        paths = [row["path"] for row in demo_rows]
        processed = output / "data/processed"
        processed.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(processed / "demo_features.npz", paths=paths,
                            features=x[[row_indices[path] for path in paths]])

    models, results = output / "models", output / "results"
    models.mkdir(parents=True, exist_ok=True)
    results.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, models / "baseline.joblib")
    transform = WEIGHTS.transforms()
    dump(models / "baseline_metadata.json", {
        "clases": CLASSES, "framework": "pytorch + scikit-learn", "tamano_entrada": [224, 224],
        "normalizacion": {"media": transform.mean, "std": transform.std},
        "resize_short_side": transform.resize_size[0],
        "backbone": "mobilenet_v3_small", "weights": WEIGHTS.name, "features": x.shape[1],
    })
    write_csv(results / "baseline_busqueda.csv", search)
    write_csv(results / "baseline_semillas.csv", repeats)
    classifier = model.named_steps["logisticregression"]
    summary = {"seed": config["seed"], "configurations": len(search), "best_c": best["C"],
               "trainable_parameters": classifier.coef_.size + classifier.intercept_.size,
               "backbone_trainable_parameters": 0, "device": str(device), "threads": config["threads"],
               "partition_sizes": {split: int((splits == split).sum()) for split in SPLITS},
               "feature_extraction_seconds": round(extraction_seconds, 2),
               "total_seconds": round(time.perf_counter() - started, 2), "validation": metrics(model, x_val, y_val),
               "seed_repeats_validation": seeds_summary, "test": test}
    summary["features_from_demo_cache"] = from_cache
    dump(results / "baseline_metricas.json", summary)
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 6), layout="constrained")
    ConfusionMatrixDisplay(np.asarray(test["confusion_matrix"]), display_labels=CLASSES).plot(
        ax=ax, xticks_rotation=25, cmap="Blues", colorbar=False)
    ax.set(xlabel="Clase predicha", ylabel="Clase real", title="Regresión logística multinomial · prueba")
    fig.savefig(figures / "baseline_confusion.png", dpi=130)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
