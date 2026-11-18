# Módulo 3 — Recomendación de destinos de viaje

Datos: *Travel Recommendation Dataset* (India Travel Recommender System Dataset),
Aman Mehra, Kaggle: https://www.kaggle.com/datasets/amanmehra23/travel-recommendation-dataset

Ver el enunciado completo en `docs/instrucciones_trabajo_3.pdf` (páginas 5–7).

## Lo que este módulo debe entregar para la aplicación web

La app debe permitir: **elegir un usuario existente o crear un perfil nuevo (con un listado de
preferencias para elegir) → ver sus K destinos recomendados junto con su historial**.

### 1. Modelos guardados (`models/`)
- [ ] Recomendador neuronal final (NCF o dos torres, con al menos una variable de contenido).
- [ ] Referencias: popularidad y filtrado colaborativo clásico (KNN o factorización de matrices).
- [ ] Codificadores de IDs de usuarios/destinos y de variables de contenido.

### 2. Funciones de inferencia (`src/predict.py`)
```python
def recomendar_usuario(user_id, k: int = 10) -> pd.DataFrame: ...
def recomendar_perfil_nuevo(preferencias: dict, k: int = 10) -> pd.DataFrame: ...
def historial(user_id) -> pd.DataFrame: ...
```

### 3. Datos procesados (`data/processed/`)
- [ ] Usuarios, destinos (con sus atributos para mostrar en la app) e interacciones.
- [ ] Particiones de entrenamiento, validación y prueba.
- [ ] Lista de valores posibles de preferencias (para el formulario de perfil nuevo).

### 4. Resultados para el reporte (`results/`, `figures/`)
- [ ] Precision, Recall y NDCG@K, cobertura, desempeño por grupo de usuarios (pocas/muchas interacciones).
- [ ] Resultados de las 30 semillas; recomendaciones para ≥ 5 usuarios con perfiles distintos.
- [ ] Figuras mínimas del módulo + figuras comunes; t-SNE/UMAP de los embeddings de destinos.
- [ ] Respuestas a las 3 preguntas de negocio.
- [ ] Al menos un hallazgo de «Cacería de la alucinación» documentado.
