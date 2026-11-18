# Módulo 2 — Clasificación de conducción distractiva

Datos: *Multi-Class Driver Behavior Image Dataset* (Afridi et al., 2024),
Mendeley Data DOI 10.17632/mzb4b6dff3.1; artículo en *Data in Brief* DOI 10.1016/j.dib.2025.111529.

Ver el enunciado completo en `docs/instrucciones_trabajo_3.pdf` (páginas 4–5).

> Las imágenes originales van en `data/raw/` y **no** se suben a git (son pesadas).
> En `data/processed/` dejen solo los archivos de partición y una muestra pequeña.

## Lo que este módulo debe entregar para la aplicación web

La app debe permitir: **subir una imagen → ver la clase asignada, la probabilidad de cada
clase, la decisión de alerta según el umbral elegido y el mapa de interpretabilidad (Grad-CAM)**.
Para eso necesitamos:

### 1. Modelo guardado (`models/`)
- [ ] Mejor modelo final (CNN propia o transfer learning) guardado (`.keras` / `.pt`).
      Preferir una arquitectura liviana (MobileNet, EfficientNet-B0, ResNet-18…), porque la
      app se publicará en un servidor gratuito con poca memoria (idealmente < 100 MB).
- [ ] Modelo de referencia (regresión logística sobre características congeladas), `joblib`.
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
- [ ] Evidencia de partición sin fuga (método de detección de duplicados/casi duplicados).
- [ ] Resultados de las 30 semillas (media, desv. estándar, mejor, peor).
- [ ] 10 aciertos y 10 errores con su explicación; mapas Grad-CAM.
- [ ] Figuras mínimas del módulo + figuras comunes (arquitectura, curvas de aprendizaje,
      búsqueda de hiperparámetros, diagramas de caja de las 30 semillas).
- [ ] Respuestas a las 3 preguntas de negocio.
- [ ] Al menos un hallazgo de «Cacería de la alucinación» documentado.
