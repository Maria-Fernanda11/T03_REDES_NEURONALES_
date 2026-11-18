# Trabajo 3 — Redes neuronales para series de tiempo, imágenes y recomendación

Sistema inteligente integrado para una empresa de transporte intermunicipal:
pronóstico de demanda y planeación de flota, detección de conducción distractiva
y recomendación de destinos de viaje.

Instrucciones completas: [`docs/instrucciones_trabajo_3.pdf`](docs/instrucciones_trabajo_3.pdf)

## Estructura del repositorio

```
T03/
├── docs/                      # Enunciado y documentos de apoyo
├── modulo1_demanda/           # Módulo 1: pronóstico de demanda y flota (series de tiempo)
├── modulo2_conduccion/        # Módulo 2: clasificación de conducción distractiva (imágenes)
├── modulo3_recomendacion/     # Módulo 3: recomendación de destinos (sistemas de recomendación)
├── app/                       # Aplicación web que integra los tres módulos
└── reporte/                   # Reporte técnico (entrada de blog) y sus figuras
```

Cada módulo usa la misma estructura interna:

| Carpeta            | Contenido                                                                 |
|--------------------|---------------------------------------------------------------------------|
| `data/raw/`        | Datos originales descargados (NO se suben a git si son pesados)            |
| `data/processed/`  | Datos procesados que usan los modelos (SÍ se suben; comprimidos si pesan) |
| `notebooks/`       | Exploración y análisis descriptivo                                        |
| `src/`             | Código reutilizable: preprocesamiento, modelos, entrenamiento, inferencia |
| `configs/`         | Archivos YAML con hiperparámetros y parámetros operativos                 |
| `models/`          | Modelos entrenados guardados (la app los carga sin reentrenar)            |
| `figures/`         | Figuras generadas desde el código                                         |
| `results/`         | Tablas de métricas, resultados de búsqueda y de las 30 semillas           |

## Reglas comunes para todos los módulos

- **Un solo comando** por experimento principal y un **modo demo** que tarde < 2 min
  (ej. `python -m modulo1_demanda.src.train --config modulo1_demanda/configs/demo.yaml`).
- Todos los parámetros se cambian desde la línea de comandos o el YAML, **sin editar código**.
- Semillas fijas y documentadas; configuración final entrenada con **30 semillas**.
- Mismos datos y particiones para red neuronal y modelos de referencia.
- Reportar nº de configuraciones probadas, tiempo de cómputo y nº de parámetros entrenables.
- Commits frecuentes (no un único commit al final).
- Documentar cada error de la IA que encuentren → sección «Cacería de la alucinación»
  (mínimo uno por módulo).

## Instalación

_Pendiente: se completará con `requirements.txt` con versiones fijas y el comando para levantar la app._
