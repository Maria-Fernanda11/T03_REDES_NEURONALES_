# Módulo 2 — Clasificación de conducción distractiva

Datos: *Multi-Class Driver Behavior Image Dataset* (Afridi et al., 2024),
Mendeley Data DOI 10.17632/mzb4b6dff3.1; artículo en *Data in Brief* DOI 10.1016/j.dib.2025.111529.

Ver el enunciado completo en `docs/instrucciones_trabajo_3.pdf` (páginas 4–5).

> Las imágenes originales van en `data/raw/` y **no** se suben a git (son pesadas).
> En `data/processed/` dejen solo los archivos de partición y una muestra pequeña.

## Análisis y modelo de referencia

El [informe del módulo](notebooks/analisis_conduccion.md) reúne el caso de
uso, el perfil del conjunto, la auditoría de la partición y los resultados de la
regresión logística. Los experimentos posteriores deben reutilizar
[`data/processed/particiones.csv`](data/processed/particiones.csv).

Ejecuta estos comandos desde la raíz del repositorio con Python 3.12 y un entorno
virtual activo. Para instalar las versiones de CPU de PyTorch y las demás dependencias:

```bash
python -m pip install torch==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r modulo2_conduccion/requirements.txt
```

Para la demo sin descargar datos ni pesos, usa la muestra de características
congeladas incluida en el repositorio. El directorio de salida mantiene separados
los resultados de demostración y los definitivos.

```bash
python -m modulo2_conduccion.src.train --config modulo2_conduccion/configs/demo.yaml --output /tmp/t03-demo
```

Para reproducir el experimento completo, descarga el [ZIP de Mendeley Data, versión
1](https://doi.org/10.17632/mzb4b6dff3.1) y guárdalo como
`modulo2_conduccion/data/raw/dataset.zip`. Se lee directamente del ZIP. Su SHA-256
es `427fec9d689a22856c51c7773adc6024158d5b228e36b2c9b58a13ce9af41c8c`.
Torchvision descarga automáticamente los pesos ImageNet de MobileNetV3-Small si
aún no están en su caché local.

```bash
python -m modulo2_conduccion.src.prepare
python -m modulo2_conduccion.src.train --config modulo2_conduccion/configs/baseline.yaml
```

`prepare` regenera el manifiesto, inventario y figuras descriptivas. `train` guarda
el clasificador, su especificación de características, las métricas y la matriz de
confusión. Se pueden cambiar los parámetros de agrupamiento con `prepare --help` y
los parámetros de ajuste con el YAML.

## Lo que este módulo debe entregar para la aplicación web

La app debe permitir: **subir una imagen → ver la clase asignada, la probabilidad de cada
clase, la decisión de alerta según el umbral elegido y el mapa de interpretabilidad (Grad-CAM)**.
Para eso necesitamos:

### 1. Modelo guardado (`models/`)
- [ ] Mejor modelo final (CNN propia o transfer learning) guardado (`.keras` / `.pt`).
      Preferir una arquitectura liviana (MobileNet, EfficientNet-B0, ResNet-18…), porque la
      app se publicará en un servidor gratuito con poca memoria (idealmente < 100 MB).
- [x] Modelo de referencia (regresión logística sobre características congeladas), `joblib`.
- [ ] `models/metadata.json` con:
  ```json
  {
    "clases": ["safe_driving", "turning", "texting_phone", "talking_phone", "other_activities"],
    "tamano_entrada": [224, 224],
    "normalizacion": {"media": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225]},
    "capa_gradcam": "nombre_de_la_ultima_capa_convolucional",
    "framework": "pytorch | tensorflow"
  }
  ```
  (el **orden** de las clases debe coincidir exactamente con la salida del modelo).

### 2. Funciones de inferencia (`src/predict.py`)
```python
def predecir(imagen: PIL.Image.Image) -> dict[str, float]:
    """Devuelve la probabilidad de cada clase (suman 1)."""

def gradcam(imagen: PIL.Image.Image, clase: int | None = None) -> np.ndarray:
    """Devuelve el mapa de calor (H x W, valores en [0, 1]) o la imagen superpuesta."""
```
El preprocesamiento debe estar **dentro** de estas funciones (redimensionar, normalizar),
para que la app solo pase la imagen tal como la sube el usuario.

### 3. Política de alertas (`configs/alertas.yaml`)
- [ ] Agrupación de clases en «sin alerta» y «con alerta», con su justificación.
- [ ] Umbral recomendado.
- [ ] `results/umbrales.csv`: para varios umbrales, falsas alarmas y distracciones no
      detectadas por cada 1.000 imágenes (la app puede mostrar esta tabla/curva).

### 4. Imágenes de ejemplo (`data/processed/ejemplos/`)
- [ ] 2–3 imágenes de **prueba** por clase para que el usuario de la app pueda probar sin
      tener imágenes propias.

### 5. Resultados para el reporte (`results/`, `figures/`)
- [ ] Exactitud, F1 macro, precisión y sensibilidad por clase, matriz de confusión.
- [x] Evidencia de la auditoría de duplicados y casi duplicados de la partición.
- [ ] Resultados de las 30 semillas (media, desv. estándar, mejor, peor).
- [ ] 10 aciertos y 10 errores con su explicación; mapas Grad-CAM.
- [ ] Figuras mínimas del módulo + figuras comunes (arquitectura, curvas de aprendizaje,
      búsqueda de hiperparámetros, diagramas de caja de las 30 semillas).
- [ ] Respuestas a las 3 preguntas de negocio.
- [x] Al menos un hallazgo de «Cacería de la alucinación» documentado.
