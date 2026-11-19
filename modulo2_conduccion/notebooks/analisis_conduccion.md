# Módulo 2 · Conducción distractiva

## 1. Caso de uso

El conductor del bus intermunicipal recibe la primera alerta en la cabina. Con el vehículo en movimiento y el rostro y las manos visibles, el sistema examina cinco imágenes por segundo. Como hipótesis de diseño para un piloto, si detecta distracción en al menos tres de las cinco observaciones recientes, emite un sonido breve. El conductor corrige la acción, por ejemplo, suelta el teléfono y vuelve a mirar la vía. Si la distracción persiste o se repite en el mismo recorrido, se registra un evento para que el centro de operaciones lo revise y contacte al conductor cuando hacerlo sea seguro. El sistema no acciona frenos ni dirección. Un giro normal se interpreta en contexto y no dispara una alerta por sí solo.

Se propone una cámara fija orientada al rostro, manos y volante, con campo de visión que permita ver el teléfono cerca del regazo, soporte firme contra vibraciones y capacidad para trabajar con contraluz y de noche. Un equipo embebido a bordo procesa imágenes localmente para que la alerta funcione sin cobertura. Como presupuesto inicial del piloto se fija un máximo de 200 ms por imagen en el percentil 95, incluyendo captura, preprocesamiento e inferencia. La decisión debería llegar en alrededor de un segundo una vez que la distracción sea visible y sostenida. Son requisitos de diseño por comprobar en el hardware de la flota. Una cámara tapada, un rostro fuera de cuadro o una imagen inutilizable generan un estado de disponibilidad separado. Para una revisión operativa basta guardar hora, vehículo y tipo de evento. Cualquier conservación de imágenes requiere una política de acceso y retención.

## 2. Análisis descriptivo

### Procedencia y aumento

Afridi et al. describen capturas en Dhaka, Bangladesh, en buses públicos y vehículos particulares con dos cámaras de teléfono, con diferentes ángulos y condiciones lumínicas. El artículo menciona 178 conductores, 30 días de observación y anotación manual en cinco carpetas. En su descripción del conjunto indican que las imágenes expandidas se almacenaron junto a las originales conservando la etiqueta. Mencionan rotación, espejo horizontal, zoom, cambios de brillo y recorte. En el protocolo experimental también describen aumento en línea durante el entrenamiento con giros de hasta 15 grados, espejo y ajustes de brillo. El ZIP no proporciona una relación verificable entre archivos publicados y fotos de origen, así que auditamos la similitud visual antes de dividir.

Fuentes: [conjunto oficial, versión 1](https://doi.org/10.17632/mzb4b6dff3.1) · [artículo de Data in Brief](https://doi.org/10.1016/j.dib.2025.111529).

### Inventario y balance

El ZIP de Mendeley contiene 7.286 archivos con extensión de imagen. Diez JPEG se
excluyeron porque Pillow no los pudo decodificar (seis de `other_activities` y
cuatro de `turning`). El inventario lista los nombres y el error. De las 7.276
imágenes legibles, 6.629 (91,1 %) miden 640 × 480 píxeles, 183 miden 683 × 384 y
182 miden 3.072 × 4.096. El ancho varía entre 576 y 4.096 píxeles y el alto entre
384 y 4.160. Son dimensiones tal como se almacenan en el ZIP, antes de corregir
la orientación EXIF. El artículo cita una resolución de 400 × 600 y referencia
un depósito en Zenodo. Para este trabajo prevalece el inventario del ZIP de
Mendeley que pide el enunciado.

| Clase | Archivos publicados | Imágenes legibles | % legibles | Luminancia P10 / P50 / P90 |
|---|---:|---:|---:|---:|
| Conducción segura | 1.679 | 1.679 | 23,1 | 81,74 / 91,18 / 107,45 |
| Giro | 1.343 | 1.339 | 18,4 | 81,86 / 92,48 / 112,57 |
| Escribir por teléfono | 1.561 | 1.561 | 21,5 | 79,76 / 91,09 / 104,12 |
| Hablar por teléfono | 1.513 | 1.513 | 20,8 | 80,19 / 91,51 / 104,89 |
| Otras actividades | 1.190 | 1.184 | 16,3 | 82,38 / 95,84 / 118,96 |

La clase más frecuente tiene 1,42 veces el tamaño de la menor. Las clases de
teléfono muestran las medianas de luminancia más próximas. Otras actividades
presenta el mayor intervalo P10–P90, de 36,58 puntos. Estas medidas resumen
intensidad de grises por imagen en una escala de 0 a 255. Una ventana brillante
puede elevar la media aunque la cara del conductor quede en sombra.

[Inventario completo](../results/inventario.json) · [Distribución por clase y partición](../figures/distribucion.png)

### Iluminación, vista y vehículo

En la [muestra de prueba](../figures/muestra_clases.jpg) se puede comparar el
encuadre lateral, que suele dejar ver ambas manos, con vistas oblicuas y más
cerradas, en las que el volante o el marco pueden ocultar el regazo. Cabinas,
volantes, ventanas y fondos exteriores se repiten en diferentes clases. También
hay contraluces con ventanas claras y rostros oscurecidos. La fila 1290 muestra
una cabina amplia con asiento de conductor y parabrisas de bus. En la fila 1185
se ve una cabina de automóvil, con el volante mucho más cerca de la cámara.
La documentación menciona automóviles y buses, pero el ZIP etiqueta la conducta y carece de
variables verificadas para vehículo, ángulo y sesión. Las observaciones sobre
encuadre y cabina son cualitativas y la luminancia cuantifica solo una parte de
la variabilidad.

**Hipótesis.** Giro y conducción segura se pueden parecer si solo cambia la
dirección de la mirada. Escribir por teléfono y otras actividades se pueden
confundir cuando el objeto está oculto o el conductor mira hacia abajo. Hablar por
teléfono se puede confundir con cubrirse la boca o apoyar la mano en la cara.
Otras actividades agrupa gestos diversos, por lo que su menor tamaño y la
heterogeneidad visual podrían reducir la sensibilidad.

Las miniaturas se redimensionaron y compusieron a partir de imágenes de Arafat
Sahin Afridi, Arafath Kafy, Nazmun Nessa Moon y Md. Shahriar Shakil, con licencia
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) y atribución al
[conjunto de Mendeley Data](https://doi.org/10.17632/mzb4b6dff3.1).

### Cacería de la alucinación · código

1. **Fragmento literal del prompt:** «Primero tenemos q tener en cuenta el readme que hay ahi».
2. **Respuesta examinada:** la primera implementación de la IA aceptaba los pares visuales con la condición `left, right = np.where(minimum <= threshold)`. Construía los grupos con pHash y un umbral de Hamming de 10.
3. **Sospecha:** con una cámara en posición similar, el interior del vehículo puede dominar el pHash aunque cambien el conductor o la actividad.
4. **Evidencia:** la primera corrida reportó 642.710 pares candidatos, 439.646 de ellos con etiquetas distintas. Encadenar los pares creó un grupo con 6.624 de las 7.276 imágenes y dejó 429 en entrenamiento, 68 en validación y 6.779 en prueba. La partición resultó inutilizable para el diseño previsto.
5. **Corrección:** se exige además correlación de la apariencia tras alinear las variantes. El informe conserva la distribución final y el recuento de pares que cruzaban las particiones exploratorias y el resultado de la auditoría final.
6. **Lección:** comprobar la distribución de tamaños de grupo y el balance real de la partición cuando un algoritmo agrupa por componentes conexas. Una cadena de coincidencias débiles puede unir muchas imágenes distintas.

[Ver la primera implementación](https://github.com/Marianaruiz11/T03_REDES_NEURONALES_/blob/5d83009/modulo2_conduccion/src/prepare.py)

## 3. Partición sin fuga por duplicados detectables

**Criterio.** Primero se compara SHA-256 de los archivos. Para comparar contenido
se lleva cada imagen a grises y se usa un hash perceptual de 63 bits basado en
los coeficientes de baja frecuencia de una transformada discreta del coseno.
Se compara exhaustivamente cada imagen original con hasta 20 vistas de cada
otra imagen, incluyendo espejo, giros de −15°, −7°, 7° y 15° y un recorte
central que aproxima un zoom. Una coincidencia visual requiere distancia
Hamming de hasta 20 bits y correlación de píxeles centrales de al menos 0,94
en la misma vista. Centrar y normalizar los píxeles reduce el efecto de cambios
uniformes de brillo y contraste.

**Elección del umbral.** Una corrida exploratoria (12 bits y correlación de
0,975) dejó 354 candidatos entre particiones al ampliar la búsqueda a 14 bits y
0,97. Una segunda corrida (18 bits y 0,95) dejó 410 candidatos con el criterio
de 20 bits y 0,94. Revisamos visualmente 18 pares de cada corrida, elegidos con
semilla 42. Aparecieron fotogramas de la misma persona y cabina con diferencias
pequeñas de pose, así que se adoptó el criterio más amplio antes del ajuste
definitivo. Las similitudes transitivas quedan en el mismo grupo y se preservan
las etiquetas publicadas incluso si dos vecinos tienen etiquetas distintas.

**División.** Con semilla 42 se construyeron diez pliegues estratificados por clase
y agrupados por componente conexa. Siete pliegues se usan para ajustar la
regresión y sus transformaciones, uno para escoger hiperparámetros y dos para
evaluar. Se conserva aproximadamente 70 % / 10 % / 20 % con todas las clases en
cada conjunto. El manifiesto es la referencia común para modelos posteriores.

| Clase | Entrenamiento | Validación | Prueba |
|---|---:|---:|---:|
| Conducción segura | 1.175 | 168 | 336 |
| Giro | 944 | 132 | 263 |
| Escribir por teléfono | 1.077 | 152 | 332 |
| Hablar por teléfono | 1.064 | 147 | 302 |
| Otras actividades | 829 | 119 | 236 |
| **Total** | **5.089** | **718** | **1.469** |

**Auditoría.** Se detectaron 99.449 pares por la regla visual, de los cuales
28.929 tenían etiquetas distintas. Esos candidatos incluyen capturas de una
misma cabina con gestos distintos. Se formaron 890 grupos, 256 con más de una
imagen. El mayor tuvo 631. Una segunda búsqueda exhaustiva de pares después
de asignar las particiones dio cero cruces por similitud visual. La búsqueda
por SHA-256 también dio cero cruces. La verificación cubre las
transformaciones y umbrales descritos. El ZIP carece de identificadores de
sesión, vehículo y conductor, así que la partición puede conservar dependencias
entre capturas que queden fuera de la regla visual.

[Manifiesto de partición](../data/processed/particiones.csv) · [Auditoría](../results/inventario.json)

## 4. Modelo de referencia

Se usa MobileNetV3-Small con pesos `IMAGENET1K_V1` de Torchvision. Se quita su
clasificador ImageNet y se conservan las 576 características tras el
`average pooling` global. La red mantiene sus pesos congelados y trabaja en modo
evaluación, con media y desviación de ImageNet. Se convierte cada imagen a RGB,
se redimensiona su lado corto a 256 píxeles, se hace un recorte central de
224 × 224 y se normalizan los canales. No se aplica aumento adicional.

El ajuste usa una tubería `StandardScaler → LogisticRegression`. El
estandarizador aprende sus estadísticas en entrenamiento. Para una
representación estandarizada $z$, la regresión da a cada clase $k$ el
puntaje $w_k^\mathsf{T}z+b_k$. Softmax convierte los cinco puntajes en
probabilidades que suman uno. Minimizar la suma de los logaritmos negativos de
las probabilidades asignadas a las etiquetas observadas equivale a maximizar
la verosimilitud multinomial. Se añade una penalización L2 a los pesos y se
controla su fuerza inversa con `C`.

Se probaron `C ∈ {0.01, 0.1, 1.0}` mediante F1 macro en validación. Ante empate
se elige el menor `C`, que penaliza más los coeficientes. Para medir la
variabilidad numérica se repitió el ajuste con semillas 0–29, permutando solo
el orden del conjunto de entrenamiento. L-BFGS es determinista para este
problema y esas repeticiones no estiman variación por conductor, sesión o
partición. El clasificador seleccionado se ajusta con la semilla 42 sobre el
mismo entrenamiento y se evalúa una vez en prueba.

Se seleccionó **C = 0,01**. En validación, la exactitud fue de **64,76 %** y el F1 macro fue de **0,652**. En las 1.469 imágenes de prueba, la exactitud fue de **66,10 %** y el F1 macro fue de **0,674**.

| Clase | Precisión | Sensibilidad | Imágenes de prueba |
|---|---:|---:|---:|
| Conducción segura | 71,37 % | 48,21 % | 336 |
| Giro | 88,07 % | 81,37 % | 263 |
| Escribir por teléfono | 83,79 % | 73,19 % | 332 |
| Hablar por teléfono | 82,38 % | 66,56 % | 302 |
| Otras actividades | 32,47 % | 63,98 % | 236 |

La clase con menor sensibilidad fue **conducción segura**. La confusión más frecuente fue predecir **otras actividades** para imágenes etiquetadas como **conducción segura** (143 casos).

Se probaron 3 configuraciones. El ajuste tiene 2.885 coeficientes e interceptos entrenables y cero parámetros entrenables en MobileNetV3-Small. En CPU con 2 hilos, extraer las características tomó 116,9 s y el experimento completo tomó 163,5 s, incluidas las 30 repeticiones de validación.

En las 30 repeticiones, el F1 macro de validación tuvo media 0,651889, desviación estándar 0,000000 y rango 0,651889–0,651889.

[Métricas completas](../results/baseline_metricas.json) · [Búsqueda de C](../results/baseline_busqueda.csv) · [Resultados de las 30 semillas](../results/baseline_semillas.csv) · [Matriz de confusión](../figures/baseline_confusion.png) · [Clasificador guardado](../models/baseline.joblib)
