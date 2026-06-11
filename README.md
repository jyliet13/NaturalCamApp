# Modelo naturalCam

Proyecto de clasificacion de fosiles con una CNN basada en transferencia de aprendizaje con `MobileNetV2`.

## Resumen

El repositorio contiene todo el flujo para:

- limpiar el dataset original;
- organizarlo en `train`, `val` y `test`;
- entrenar el clasificador en dos fases;
- guardar las clases y el modelo final;
- exponer una API Flask para inferencia.

## Que clasifica el modelo

El modelo final trabaja con 13 clases:

- Ammonites
- Belemnites
- Corals
- Crinoids
- Leaf fossils
- Trilobites
- bivalves
- dinosaurs
- echinoderms
- fishes
- forams
- gastropods
- plants

El orden exacto de clases se guarda en `class_names.npy` y es el que usa la API al devolver la prediccion.

## Datasets incluidos

La pipeline de entrenamiento usa la carpeta:

`Dataset/Dataset_Fosiles_Completo/split`

Estructura esperada:

- `train_balanced`
- `val`
- `test`

Conteo de archivos que hay actualmente en el repo:

- `train_balanced`: 1833 imagenes, 141 por clase
- `val`: 312 imagenes
- `test`: 327 imagenes

Nota: `train_balanced` esta balanceado por clase. `val` y `test` no tienen exactamente la misma cantidad por clase.

## Como se construyo el modelo

### 1. Limpieza del dataset

El script `Dataset/limpieza.py` revisa el dataset original y elimina archivos corruptos o invalidos antes de generar el split.

- ruta usada por el script: `Dataset_Fosiles_Completo/all_images`
- validacion con `PIL.Image.verify()` y con TensorFlow
- si detecta un archivo problemático, lo elimina

### 2. Preparacion de datos

El entrenamiento principal se hace desde `CNN_Models.py` y `CNN_Models53.py`.

Parametros usados:

- tamano de imagen: `224 x 224`
- batch size: `32`
- semilla: `123`
- formatos leidos: `jpg`, `jpeg`, `png`, `gif`, `bmp`

La carga de imagen hace lo siguiente:

- lee el archivo desde disco;
- decodifica la imagen en 3 canales;
- redimensiona a `224 x 224`;
- normaliza a rango `0-1`;
- si una imagen falla, devuelve un tensor cero y etiqueta `-1` como fallback.

### 3. Aumento de datos

Antes de entrar a la red base se aplica augmentation con:

- `RandomFlip("horizontal")`
- `RandomRotation(0.1)`
- `RandomZoom(0.1)`
- `RandomContrast(0.2)`

### 4. Arquitectura

La red se construye con transferencia de aprendizaje sobre `MobileNetV2` preentrenada en ImageNet.

Arquitectura general:

```text
Input(224, 224, 3)
-> Data Augmentation
-> preprocess_input de MobileNetV2
-> MobileNetV2(include_top=False, weights='imagenet')
-> GlobalAveragePooling2D
-> Dense(128, activation='relu', kernel_regularizer=l2(0.005))
-> Dropout(0.5)
-> Dense(13, activation='softmax')
```

Datos verificados de los modelos `.keras` guardados en el repo:

- input shape: `(None, 224, 224, 3)`
- output shape: `(None, 13)`
- parametros totales: `2,423,629`

Los archivos actuales con el mismo esquema son:

- `fossil_classifier_finetuned.keras`
- `fossil_classifier_finetuned_2par50%.keras`
- `fossil_classifier_finetuned_2par55%.keras`

### 5. Entrenamiento por fases

El entrenamiento principal se hace en dos fases:

#### Fase 1: base congelada

- epocas: `15`
- optimizador: `Adam`
- learning rate: `0.0001`
- loss: `sparse_categorical_crossentropy`
- metricas: `accuracy`
- la base de `MobileNetV2` permanece congelada

#### Fase 2: fine-tuning

- epocas adicionales: `250`
- optimizador: `Adam`
- learning rate: `0.00001`
- loss: `sparse_categorical_crossentropy`
- metricas: `accuracy`
- la base se descongela, pero se vuelven a congelar todas las capas excepto las ultimas 70

### 6. Datasets de entrenamiento

La construccion de `tf.data.Dataset` usa:

- `shuffle(buffer_size=1000, seed=123)` para entrenamiento;
- `batch(32)`;
- `prefetch(tf.data.AUTOTUNE)`;
- `cache()` en validacion y test;
- `repeat()` en entrenamiento.

Importante: los pasos se calculan con division entera, asi que si el numero de muestras no es multiplo exacto del batch size, el ultimo lote parcial puede no usarse en cada epoca/evaluacion.

### 7. Evaluacion y guardado

Al terminar el entrenamiento:

- se evalua el modelo en `test`;
- se imprime `accuracy` y `loss` finales;
- se guarda el modelo en formato `.keras`;
- se exporta el orden de clases en `class_names.npy`.

## API de inferencia

`Api.py` expone una API Flask con CORS activado.

### Endpoint

- `POST /predict`

### Formato esperado

- campo del archivo: `file`
- extensiones permitidas: `png`, `jpg`, `jpeg`, `gif`, `webp`

### Respuesta

Devuelve un JSON con:

- `prediction`: clase predicha
- `confidence`: confianza de la prediccion
- `all_probabilities`: probabilidad por clase

### Modelo cargado por defecto

La API carga por defecto:

- `fossil_classifier_finetuned_2par50%.keras`

Si quieres usar otra version, cambia `MODEL_FILENAME` dentro de `Api.py`.

## Analisis adicional

El repo tambien incluye scripts de analisis y validacion:

- `analisis.py`
- `analisis.ipynb`

Ese analisis usa un flujo distinto con `image_dataset_from_directory`, `validation_split=0.2`, imagenes de `150 x 150` y el modelo `fossil_classifier.keras`, por lo que parece un experimento o version anterior del pipeline.

## Logs

Las corridas de entrenamiento dejaron logs de TensorBoard en `logs/fit/`.

Para revisarlos:

```bash
tensorboard --logdir logs/fit
```

## Archivos principales del proyecto

- `CNN_Models.py`: pipeline principal de entrenamiento
- `CNN_Models53.py`: copia/variacion del pipeline principal
- `Api.py`: API Flask para prediccion
- `Dataset/limpieza.py`: limpieza de imagenes corruptas
- `class_names.npy`: orden de clases exportado por el entrenamiento
- `fossil_classifier_finetuned*.keras`: modelos entrenados

## Requisitos

Dependencias usadas en el proyecto:

- `tensorflow`
- `numpy`
- `flask`
- `flask-cors`
- `pillow`
- `werkzeug`

## Ejecucion rapida

### Entrenar

```bash
python CNN_Models.py
```

### Levantar la API

```bash
python Api.py
```

### Ver analisis de clasificacion

```bash
python analisis.py
```

## Notas

- El repositorio tiene varias versiones del modelo guardado; la mas nueva en fecha no necesariamente es la que usa la API por defecto.
- `CNN_Models.py` y `CNN_Models53.py` contienen la misma receta base en el estado actual del repo.
- Si cambias el numero de clases o reentrenas el modelo, recuerda volver a generar `class_names.npy` y revisar `Api.py`.
