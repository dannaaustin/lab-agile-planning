# PPE Detection Module (EXTENSIÓN OPCIONAL — no core del proyecto)

Este módulo responde al punto del JD de Schneider: *"automatización con IA de EPI's"*.
Se mantiene deliberadamente separado del proyecto principal de analítica (ver
`docs/business_case.md` — decisión de scope) para no convertir un proyecto de Business
Analytics en un proyecto de Computer Vision.

## Qué es

Un modelo de detección de equipos de protección individual (casco, chaleco reflectante,
gafas) sobre imágenes, usando YOLOv8 fine-tuned sobre un dataset público de PPE
detection (Roboflow Universe o Kaggle — no incluido en este repo por tamaño y licencia).

## Por qué NO está entrenado dentro de este repo

- Requiere descargar un dataset externo (Roboflow/Kaggle) con su propia licencia —
  no se redistribuye aquí.
- Entrenar un YOLOv8 razonable necesita GPU; no es el foco del proyecto principal.
- Meterlo "a la fuerza" en el mismo repo diluye el mensaje: este proyecto es sobre
  convertir datos operacionales en decisiones, no sobre visión artificial.

## Cómo lo montarías si quieres completarlo (pasos, no código de producción)

1. Descargar dataset público de PPE detection (buscar "hard hat detection dataset" o
   "PPE detection dataset" en Roboflow Universe — varios con licencia CC/uso académico).
2. `pip install ultralytics`
3. Entrenar con transfer learning sobre un checkpoint YOLOv8n (rápido, suficiente para demo):
   ```python
   from ultralytics import YOLO
   model = YOLO("yolov8n.pt")
   model.train(data="ppe_dataset/data.yaml", epochs=30, imgsz=640)
   ```
4. Inferencia sobre imagen/vídeo de ejemplo, output: % de compliance de EPI detectado.
5. (Opcional) Envolver en una demo simple con Gradio para poder enseñarlo en vivo en
   entrevista sin depender de notebook.

## Cómo hablar de esto en entrevista si no lo terminas

Es perfectamente defendible decir: "Lo dejé documentado como extensión con los pasos
claros de cómo lo montaría, pero prioricé cerrar bien la parte de analítica y risk
scoring, que es el núcleo real del problema de negocio." Eso demuestra criterio de
producto, no vagancia — mejor eso que un modelo a medio entrenar sin validar.
