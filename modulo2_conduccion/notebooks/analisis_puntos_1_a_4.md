# Módulo 2 · Conducción distractiva

## 1. Caso de uso

El conductor del bus intermunicipal recibe la primera alerta en la cabina. Con el vehículo en movimiento y el rostro y las manos visibles, el sistema examina cinco imágenes por segundo. Como hipótesis de diseño para un piloto, si detecta distracción en al menos tres de las cinco observaciones recientes, emite un sonido breve. El conductor corrige la acción, por ejemplo, suelta el teléfono y vuelve a mirar la vía. Si la distracción persiste o se repite en el mismo recorrido, se registra un evento para que el centro de operaciones lo revise y contacte al conductor cuando hacerlo sea seguro. El sistema no acciona frenos ni dirección. Un giro normal se interpreta en contexto y no dispara una alerta por sí solo.

Se propone una cámara fija orientada al rostro, manos y volante, con campo de visión que permita ver el teléfono cerca del regazo, soporte firme contra vibraciones y capacidad para trabajar con contraluz y de noche. Un equipo embebido a bordo procesa imágenes localmente para que la alerta funcione sin cobertura. Como presupuesto inicial del piloto se fija un máximo de 200 ms por imagen en el percentil 95, incluyendo captura, preprocesamiento e inferencia. La decisión debería llegar en alrededor de un segundo una vez que la distracción sea visible y sostenida. Son requisitos de diseño por comprobar en el hardware de la flota. Una cámara tapada, un rostro fuera de cuadro o una imagen inutilizable generan un estado de disponibilidad separado. Para una revisión operativa basta guardar hora, vehículo y tipo de evento. Cualquier conservación de imágenes requiere una política de acceso y retención.

## 2. Análisis descriptivo

### Procedencia y aumento

Afridi et al. describen capturas en Dhaka, Bangladesh, en buses públicos y vehículos particulares con dos cámaras de teléfono, con diferentes ángulos y condiciones lumínicas. El artículo menciona 178 conductores, 30 días de observación y anotación manual en cinco carpetas. En su descripción del conjunto indican que las imágenes expandidas se almacenaron junto a las originales conservando la etiqueta. Mencionan rotación, espejo horizontal, zoom, cambios de brillo y recorte. En el protocolo experimental también describen aumento en línea durante el entrenamiento con giros de hasta 15 grados, espejo y ajustes de brillo. El ZIP no proporciona una relación verificable entre archivos publicados y fotos de origen, así que auditamos la similitud visual antes de dividir.

Fuentes: [conjunto oficial, versión 1](https://doi.org/10.17632/mzb4b6dff3.1) · [artículo de Data in Brief](https://doi.org/10.1016/j.dib.2025.111529).
