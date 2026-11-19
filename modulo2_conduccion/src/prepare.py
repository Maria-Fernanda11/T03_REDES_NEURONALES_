"""Inventariar el ZIP y construir particiones por grupos de similitud visual."""

import argparse
from collections import Counter
import csv
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import time
from zipfile import ZipFile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
from scipy.fft import dctn
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ["safe_driving", "turning", "texting_phone", "talking_phone", "other_activities"]
SPLITS = ["train", "val", "test"]


def label_for(path):
    components = [part.lower().replace(" ", "_").replace("-", "_") for part in PurePosixPath(path).parts[:-1]]
    aliases = {
        "safe_driving": "safe_driving", "turning": "turning", "texting": "texting_phone",
        "texting_phone": "texting_phone", "talking_phone": "talking_phone",
        "talking_on_phone": "talking_phone", "other_activities": "other_activities",
        "other": "other_activities", "others": "other_activities",
    }
    for part in reversed(components):
        if part in aliases:
            return aliases[part]
    raise ValueError(f"Carpeta de clase desconocida: {path}")


def phash(gray):
    pixels = np.asarray(gray.resize((32, 32), Image.Resampling.LANCZOS), dtype=np.float32)
    coefficients = dctn(pixels, norm="ortho")[:8, :8].ravel()[1:]
    bits = np.packbits(coefficients > np.median(coefficients))
    return int.from_bytes(bits.tobytes(), "big")


def views(gray):
    """Vistas para verificar espejo, giros y recortes centrales moderados."""
    yield gray
    for crop in [0, 6]:
        view = gray.crop((crop, crop, 64 - crop, 64 - crop))
        for flipped in [False, True]:
            oriented = ImageOps.mirror(view) if flipped else view
            for angle in [-15, -7, 0, 7, 15]:
                if crop == 0 and not flipped and angle == 0:
                    continue
                yield oriented.rotate(angle, resample=Image.Resampling.BILINEAR,
                                      fillcolor=int(np.asarray(oriented).mean()))


def descriptor(view):
    pixels = np.asarray(view.resize((32, 32), Image.Resampling.LANCZOS), dtype=np.float32)
    # El centro reduce la influencia de los bordes introducidos por la rotación.
    pixels = pixels[3:-3:2, 3:-3:2].ravel()
    pixels -= pixels.mean()
    norm = np.linalg.norm(pixels)
    return pixels / norm if norm else pixels


def inspect(archive):
    rows, fingerprints, descriptors, unreadable = [], [], [], []
    for path in sorted(archive.namelist()):
        if PurePosixPath(path).suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        if any(part.startswith((".", "__MACOSX")) for part in PurePosixPath(path).parts):
            continue
        raw = archive.read(path)
        try:
            with Image.open(BytesIO(raw)) as image:
                width, height = image.size
                image.draft("L", (160, 160))
                gray = ImageOps.exif_transpose(image).convert("L").resize((64, 64), Image.Resampling.LANCZOS)
        except (UnidentifiedImageError, OSError) as error:
            unreadable.append({"path": path, "reason": str(error).split(" <_io.")[0]})
            continue
        luminance = np.asarray(gray)
        rows.append({"path": path, "class": label_for(path), "width": width, "height": height,
                     "luminance": round(float(luminance.mean()), 2), "contrast": round(float(luminance.std()), 2),
                     "sha256": hashlib.sha256(raw).hexdigest()})
        variants = list(views(gray))
        fingerprints.append([phash(view) for view in variants])
        descriptors.append([descriptor(view) for view in variants])
    if set(row["class"] for row in rows) != set(CLASSES):
        raise ValueError("El ZIP debe contener las cinco clases.")
    return rows, np.asarray(fingerprints, dtype=np.uint64), np.asarray(descriptors), unreadable


def candidate_pairs(fingerprints, descriptors, threshold, min_correlation):
    """Buscar todas las vistas con pHash cercano y apariencia corroborada."""
    original = fingerprints[:, 0]
    original_pixels = descriptors[:, 0]
    count = len(original)
    batches = []
    for start in range(0, count, 128):
        block = fingerprints[start:start + 128]
        for view, variant in enumerate(block.T):
            distance = np.bitwise_count(variant[:, None] ^ original[None, :])
            left, right = np.where(distance <= threshold)
            left += start
            keep = left != right
            left, right = left[keep], right[keep]
            similarity = np.einsum("ij,ij->i", descriptors[left, view], original_pixels[right])
            keep = similarity >= min_correlation
            a, b = left[keep], right[keep]
            batches.append(np.minimum(a, b) * count + np.maximum(a, b))
    encoded = np.unique(np.concatenate(batches))
    return encoded // count, encoded % count


def exact_pairs(rows):
    first, left, right = {}, [], []
    for i, row in enumerate(rows):
        digest = row["sha256"]
        if digest in first:
            left.append(first[digest])
            right.append(i)
        else:
            first[digest] = i
    return np.asarray(left, dtype=int), np.asarray(right, dtype=int)


def assign(rows, groups, seed):
    # Siete de diez pliegues para entrenamiento, uno para validación y dos para prueba.
    labels = np.asarray([row["class"] for row in rows])
    folds = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=seed)
    assignments = np.empty(len(rows), dtype="U5")
    for fold, (_, indices) in enumerate(folds.split(labels, labels, groups)):
        assignments[indices] = "test" if fold < 2 else "val" if fold == 2 else "train"
    for split in SPLITS:
        if set(labels[assignments == split]) != set(CLASSES):
            raise ValueError(f"La partición {split} debe contener todas las clases.")
    return assignments


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def figures(rows, archive, rng, destination):
    labels = np.asarray([row["class"] for row in rows])
    counts = Counter((row["class"], row["split"]) for row in rows)
    x = np.arange(len(CLASSES))
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), layout="constrained")
    for i, split in enumerate(SPLITS):
        axes[0].bar(x + (i - 1) * 0.25, [counts[c, split] for c in CLASSES], width=0.25, label=split)
    axes[0].set(xticks=x, xticklabels=CLASSES, ylabel="Imágenes")
    axes[0].legend()
    axes[1].boxplot([[r["luminance"] for r in rows if r["class"] == c] for c in CLASSES],
                    tick_labels=CLASSES)
    axes[1].set(ylabel="Luminancia media por imagen (0–255)")
    fig.savefig(destination / "distribucion.png", dpi=130)
    plt.close(fig)

    fig, axes = plt.subplots(len(CLASSES), 4, figsize=(10, 10), layout="constrained")
    for c, line in zip(CLASSES, axes):
        candidates = [i for i in np.flatnonzero(labels == c) if rows[i]["split"] == "test"]
        chosen = []
        for i in rng.permutation(candidates):
            if rows[i]["group"] not in {rows[j]["group"] for j in chosen}:
                chosen.append(i)
            if len(chosen) == len(line):
                break
        for ax in line:
            ax.axis("off")
        for ax, i in zip(line, chosen):
            with Image.open(BytesIO(archive.read(rows[i]["path"]))) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.thumbnail((300, 300))
                ax.imshow(image)
            ax.set_title(f"{c}\nFila {i + 1}", fontsize=8)
    fig.savefig(destination / "muestra_clases.jpg", dpi=120)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, default=ROOT / "data/raw/dataset.zip")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--threshold", type=int, default=12)
    parser.add_argument("--audit-threshold", type=int, default=14)
    parser.add_argument("--min-correlation", type=float, default=0.975)
    parser.add_argument("--audit-correlation", type=float, default=0.970)
    args = parser.parse_args()
    if not 0 <= args.threshold <= args.audit_threshold <= 63:
        parser.error("Se espera 0 ≤ threshold ≤ audit-threshold ≤ 63.")
    if not 0 <= args.audit_correlation <= args.min_correlation <= 1:
        parser.error("Se espera 0 ≤ audit-correlation ≤ min-correlation ≤ 1.")
    start = time.perf_counter()
    with ZipFile(args.zip) as archive:
        rows, fingerprints, descriptors, unreadable = inspect(archive)
        print(f"Inventario: {len(rows)} imágenes", flush=True)
        near = candidate_pairs(fingerprints, descriptors, args.threshold, args.min_correlation)
        exact = exact_pairs(rows)
        edges = tuple(np.concatenate([a, b]) for a, b in zip(near, exact))
        graph = coo_matrix((np.ones(len(edges[0]), dtype=np.uint8), edges), shape=(len(rows), len(rows)))
        n_groups, groups = connected_components(graph, directed=False)
        assignments = assign(rows, groups, args.seed)
        for row, group, assignment in zip(rows, groups, assignments):
            row.update(group=int(group), split=assignment)
        # Segunda pasada independiente del grafo y con umbral relajado como sensibilidad.
        relaxed = candidate_pairs(fingerprints, descriptors, args.audit_threshold, args.audit_correlation)
        audited = candidate_pairs(fingerprints, descriptors, args.threshold, args.min_correlation)
        cross_near = int(np.count_nonzero(assignments[audited[0]] != assignments[audited[1]]))
        cross_exact = int(np.count_nonzero(assignments[exact[0]] != assignments[exact[1]]))
        if cross_near or cross_exact:
            raise RuntimeError("La auditoría encontró coincidencias entre particiones.")
        cross_relaxed = assignments[relaxed[0]] != assignments[relaxed[1]]
        processed = ROOT / "data/processed"
        write_csv(processed / "particiones.csv", rows)
        figures(rows, archive, np.random.default_rng(args.seed), ROOT / "figures")

    group_sizes = Counter(groups)
    counts = Counter((row["class"], row["split"]) for row in rows)
    summary = {
        "seed": args.seed, "images": len(rows), "unreadable": unreadable,
        "resolutions": dict(Counter(f"{row['width']}x{row['height']}" for row in rows)),
        "classes": {c: {s: counts[c, s] for s in SPLITS} for c in CLASSES},
        "luminance_quantiles_10_50_90": {
            c: np.quantile([r["luminance"] for r in rows if r["class"] == c], [0.1, 0.5, 0.9]).round(2).tolist()
            for c in CLASSES},
        "groups": n_groups, "groups_with_multiple_images": sum(size > 1 for size in group_sizes.values()),
        "largest_group": max(group_sizes.values()), "exact_extra_files": len(exact[0]),
        "near_threshold": args.threshold, "min_correlation": args.min_correlation,
        "near_pairs": len(near[0]),
        "near_pairs_with_different_labels": sum(rows[a]["class"] != rows[b]["class"] for a, b in zip(*near)),
        "cross_split_exact": cross_exact, "cross_split_near": cross_near,
        "relaxed_threshold": args.audit_threshold, "relaxed_correlation": args.audit_correlation,
        "cross_split_relaxed": int(cross_relaxed.sum()),
        "elapsed_seconds": round(time.perf_counter() - start, 2),
    }
    (ROOT / "results/inventario.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
