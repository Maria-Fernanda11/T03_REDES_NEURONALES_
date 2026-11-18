# Módulo 1 — Pronóstico de demanda y planeación de la operación

Datos: «Operación de pasajeros y despacho de vehículos en la modalidad de transporte de
pasajeros por carretera» (Superintendencia de Transporte, datos.gov.co) + DIVIPOLA (DANE).

Ver el enunciado completo en `docs/instrucciones_trabajo_3.pdf` (páginas 2–4).

## Lo que este módulo debe entregar para la aplicación web

La app debe permitir: **elegir una ruta → ver el pronóstico a 30 días con banda de
incertidumbre → ver flota y conductores requeridos → cambiar al menos dos parámetros
(ocupación objetivo y cuantil) y ver cómo cambian**. Para eso necesitamos:

### 1. Modelos guardados (`models/`)
- [ ] Mejor red neuronal final (MLP o LSTM/GRU/CNN-1D) guardada (`.keras` / `.pt`).
- [ ] Mejor modelo de referencia guardado (SARIMA/ETS/regresión, con `joblib`/`pickle`).
- [ ] Escaladores / codificadores usados en el preprocesamiento (`scaler.joblib`, etc.).

### 2. Pronósticos precalculados (`results/pronosticos_30d.csv`) — **lo más importante**
Una tabla con el pronóstico de los próximos 30 días para **cada ruta**, con varios cuantiles,
para que la app pueda cambiar el cuantil sin ejecutar el modelo:

| ruta_id | fecha | modelo | p50 (o media) | p75 | p90 | p95 | real (si es periodo de prueba) |
|---------|-------|--------|---------------|-----|-----|-----|-------------------------------|

### 3. Función de inferencia (`src/predict.py`)
```python
def predecir(ruta_id: str, fecha_inicio: str, horizonte: int = 30) -> pd.DataFrame:
    """Devuelve columnas: fecha, p50, p75, p90, p95."""
```

### 4. Función de dimensionamiento (`src/flota.py`) — función pura, sin dependencias del modelo
```python
def dimensionar(demanda: pd.Series, params: dict) -> pd.DataFrame:
    """Para cada día devuelve: despachos, vehiculos, conductores."""
```
Debe recibir como parámetros (no fijos en el código): capacidad por clase de vehículo,
ocupación objetivo, tiempo de ciclo por ruta, horas de operación, jornada máxima,
descansos, ausentismo y costos.

### 5. Configuración operativa (`configs/operacion.yaml`)
Todos los parámetros operativos anteriores, **con la cita de la norma/fuente primaria**
(por ejemplo, la normativa de jornada de conductores) en comentarios del YAML.

### 6. Datos procesados (`data/processed/`)
- [ ] `series_diarias.csv` (o `.parquet`): `ruta_id, fecha, pasajeros` (+ variables exógenas).
- [ ] `rutas.csv`: `ruta_id, origen, destino, divipola_origen, divipola_destino, sentido`
      (nombres legibles para el selector de la app).
- [ ] `festivos.csv` u otras exógenas usadas, con su fuente.

### 7. Resultados para el reporte (`results/`, `figures/`)
- [ ] Tabla de métricas MAE, RMSE, MASE por ruta y agregadas; error por horizonte; cobertura y pérdida cuantílica.
- [ ] Resultados de las 30 semillas (media, desv. estándar, mejor, peor).
- [ ] Figuras mínimas del módulo + figuras comunes (arquitectura, curvas de aprendizaje,
      búsqueda de hiperparámetros, diagramas de caja de las 30 semillas).
- [ ] Respuestas a las 4 preguntas de negocio.
- [ ] Al menos un hallazgo de «Cacería de la alucinación» documentado.
