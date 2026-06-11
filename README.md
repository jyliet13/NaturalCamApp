# NaturalCam

NaturalCam es una aplicación de escritorio desarrollada con **Electron** para clasificar imágenes de fósiles mediante un modelo de **IA con TensorFlow/Keras**.  
La app arranca una interfaz de escritorio, levanta una API local en **Flask** y utiliza esa API para enviar imágenes y recibir la predicción de la clase del fósil.

## Qué hace el proyecto

- Permite seleccionar una imagen de un fósil desde el equipo.
- Envía la imagen a una API local de Python para obtener una clasificación.
- Muestra la clase predicha, el nivel de confianza y las probabilidades por clase.
- Guarda un historial de clasificaciones en la sesión y también en `localStorage`.
- Incluye una sección informativa con fichas de fósiles y un chatbot básico con respuestas predefinidas.
- Está pensado como proyecto académico / TFG.

## Modelo de IA

El sistema de clasificación se construyó a partir de una red CNN con **transfer learning** usando `MobileNetV2` como base preentrenada y aplicando después **fine-tuning** para adaptar el modelo al conjunto de fósiles del proyecto.

En su versión final, el modelo trabaja con **13 clases** de fósiles y alcanza una **precisión aproximada del 60%**.

## Tecnologías usadas

- **Electron** para la aplicación de escritorio.
- **Node.js** para el proceso principal de Electron.
- **Python 3.11** para la API local.
- **Flask** y **flask-cors** para exponer el endpoint de predicción.
- **TensorFlow / Keras** para cargar y ejecutar el modelo de clasificación.
- **NumPy** y **Pillow** para procesar las imágenes.
- **HTML, CSS y JavaScript** para la interfaz.

## Flujo de la aplicación

1. `src/Main.js` inicia la app de Electron.
2. Electron abre `public/index.html`.
3. El proceso principal lanza `src/backend/Api.py`.
4. La API carga el modelo desde `models/fossil_classifier_finetuned_2par50%.keras` y las clases desde `models/class_names.npy`.
5. El usuario sube una imagen y el frontend la envía a `http://127.0.0.1:5000/predict`.
6. Flask devuelve la predicción y la interfaz muestra el resultado.

## Clases que reconoce

El modelo está preparado para reconocer estas categorías:

- `Ammonites`
- `Belemnites`
- `Corals`
- `Crinoids`
- `Leaf fossils`
- `Trilobites`
- `bivalves`
- `dinosaurs`
- `echinoderms`
- `fishes`
- `forams`
- `gastropods`
- `plants`

## Estructura del repositorio

- `src/Main.js`: proceso principal de Electron, abre la ventana y arranca la API de Python.
- `src/backend/Api.py`: API Flask que carga el modelo y devuelve predicciones.
- `public/index.html`: interfaz principal de la app.
- `src/renderer/`: scripts auxiliares del frontend.
- `src/renderer/pages/`: vistas HTML secundarias como historial, información y chatbot.
- `src/renderer/styles/` y `pages/styles/`: estilos CSS.
- `models/`: modelo entrenado y nombres de clases.
- `assets/` y `pages/assets/`: iconos e imágenes de la interfaz.

## Requisitos

- **Node.js** compatible con Electron 29.
- **Python 3.11** o similar.
- Una virtualenv de Python recomendada para el backend.

## Instalación

1. Instala las dependencias de Node:

```bash
npm install
```

2. Crea y activa una virtualenv de Python:

```bash
python -m venv .venv
```

3. Instala las dependencias de Python:

```bash
pip install flask flask-cors numpy pillow tensorflow keras
```

> Nota: este repositorio no incluye `requirements.txt`, así que las dependencias anteriores se deducen del código de la API.

## Ejecutar en local

Desde la raíz del proyecto:

```bash
npm start
```

Eso abrirá Electron y arrancará automáticamente la API de Python.

## Compilación

El proyecto incluye scripts para empaquetar la app con Electron Builder:

```bash
npm run build-win
npm run build-linux
npm run build-mac
```

## API local

Si quieres probar el backend por separado, puedes ejecutar:

```bash
python src/backend/Api.py
```

El endpoint principal es:

- `POST /predict`

El campo esperado en la petición es:

- `file`

## Observaciones

- La app usa imágenes y recursos locales incluidos en el repositorio.
- La interfaz principal carga Tailwind desde CDN en `public/index.html`, así que conviene tener conexión a internet si no lo has empaquetado localmente.
- La carpeta `uploads/` se crea automáticamente si no existe.
- El backend está configurado para funcionar en CPU y evitar problemas de GPU en Windows.

## Autor

**Juliet Acevedo**
