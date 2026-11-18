# Aplicación web

Integra los tres módulos usando los **modelos guardados, sin reentrenar**, y debe poder
levantarse localmente con un solo comando y estar publicada (link requerido).

```
app/
├── pages/    # Una página por módulo (demanda, conducción, recomendación)
├── utils/    # Carga de modelos y funciones compartidas
└── assets/   # Logos, imágenes de ejemplo, estilos
```

La app solo importa las funciones de inferencia de cada módulo:

| Módulo | Importa de                              | Funciones                                   |
|--------|-----------------------------------------|---------------------------------------------|
| 1      | `modulo1_demanda/src/predict.py`, `flota.py` | `predecir`, `dimensionar`                   |
| 2      | `modulo2_conduccion/src/predict.py`     | `predecir`, `gradcam`                       |
| 3      | `modulo3_recomendacion/src/predict.py`  | `recomendar_usuario`, `recomendar_perfil_nuevo`, `historial` |

Debe incluir enlaces al reporte técnico, al video promocional y a los videos de
contribución individual.
