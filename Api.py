import os
import io # Importamos io para manejar los bytes de la imagen directamente
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import numpy as np
import tensorflow as tf
from PIL import Image # Pillow library
from flask_cors import CORS # Importamos CORS para permitir peticiones desde el frontend

# --- Configuración de la API ---
# Es buena práctica poner la ruta completa o que los archivos estén en la misma carpeta que este script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(SCRIPT_DIR, 'uploads') # Carpeta para guardar temporalmente las imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app) # Habilitar CORS para permitir que tu frontend (que estará en un origen diferente) acceda a esta API

# --- Rutas a tu modelo y nombres de clases ---
MODEL_FILENAME = 'fossil_classifier_finetuned_2par50%.keras' # Nombre de tu modelo
CLASS_NAMES_FILENAME = 'class_names.npy'

MODEL_PATH = os.path.join(SCRIPT_DIR, MODEL_FILENAME)
CLASS_NAMES_PATH = os.path.join(SCRIPT_DIR, CLASS_NAMES_FILENAME)

# --- Parámetros de imagen esperados por tu modelo Keras ---
IMG_HEIGHT = 224
IMG_WIDTH = 224

# --- Cargar el modelo y los nombres de las clases al iniciar la aplicación ---
model = None
class_names = None

try:
    print(f"Cargando modelo desde: {MODEL_PATH}")
    # CRÍTICO: Pasamos la función preprocess_input como un objeto personalizado al cargar el modelo.
    # Esto le dice a Keras cómo resolver la función dentro de la capa Lambda.
    custom_objects = {
        'preprocess_input': tf.keras.applications.mobilenet_v2.preprocess_input
    }
    model = tf.keras.models.load_model(MODEL_PATH, custom_objects=custom_objects)
    print(f"Modelo '{MODEL_FILENAME}' cargado exitosamente.")

    print(f"Cargando nombres de clases desde: {CLASS_NAMES_PATH}")
    class_names = np.load(CLASS_NAMES_PATH)
    print(f"Clases detectadas: {class_names}")

    if model.output_shape[-1] != len(class_names):
        print(f"ADVERTENCIA: El número de clases del modelo ({model.output_shape[-1]}) no coincide con las clases cargadas ({len(class_names)}). Esto puede ser un problema si el modelo fue reentrenado con un número diferente de clases.")

    # --- Print de depuración: Input shape esperado por el modelo ---
    print(f"Input shape esperado por el modelo: {model.input_shape}")

except Exception as e:
    print(f"ERROR FATAL: No se pudo cargar el modelo o los nombres de clases.")
    print(f"Asegúrate de que las rutas '{MODEL_PATH}' y '{CLASS_NAMES_PATH}' sean correctas y los archivos existan.")
    print(f"Detalles del error: {e}")
    import sys
    sys.exit(1) # Salir si el modelo no se carga, la API no puede funcionar sin él

# --- Función de utilidad para verificar extensiones de archivo ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Ruta de la API para la predicción ---
@app.route('/predict', methods=['POST'])
def predict():
    if model is None or class_names is None:
        return jsonify({"error": "El servidor no pudo cargar el modelo de IA. Contacta al administrador."}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo de imagen en la solicitud. Asegúrate de usar 'file' como nombre de campo en tu POST."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo de imagen."}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            print(f"Carpeta '{app.config['UPLOAD_FOLDER']}' creada.")

        file.save(filepath) # Guarda el archivo temporalmente

        try:
            img = Image.open(filepath).resize((IMG_WIDTH, IMG_HEIGHT)) # Redimensionar con PIL
            img_array = tf.keras.preprocessing.image.img_to_array(img)

            print(f"\n--- Depuración de Imagen ---")
            print(f"Imagen cargada: {filename}")
            print(f"Tamaño de la imagen cargada (img_array.shape) ANTES de expand_dims: {img_array.shape}")
            print(f"Tipo de datos (dtype) ANTES de normalización: {img_array.dtype}")
            print(f"Valores máximos/mínimos ANTES de normalización: Min={np.min(img_array)}, Max={np.max(img_array)}")

            img_array = tf.expand_dims(img_array, 0) # Añadir dimensión de batch: (1, 224, 224, 3)
            img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array) # Preprocesamiento específico de MobileNetV2

            print(f"Tamaño de la imagen lista para el modelo (img_array.shape) DESPUÉS de expand_dims y preprocesamiento: {img_array.shape}")
            print(f"Valores máximos/mínimos DESPUÉS de preprocesamiento: Min={np.min(img_array)}, Max={np.max(img_array)}")

            predictions = model.predict(img_array)
            probabilities = predictions[0]

            print(f"Probabilidades (output del modelo): {probabilities}")
            print(f"Suma de probabilidades (debería ser ~1.0): {np.sum(probabilities)}")
            print(f"--- Fin Depuración de Imagen ---\n")

            predicted_class_index = np.argmax(probabilities)
            predicted_class_name = class_names[predicted_class_index]
            confidence = float(np.max(probabilities)) * 100

            os.remove(filepath) # Eliminar el archivo temporal

            return jsonify({
                "prediction": predicted_class_name,
                "confidence": round(confidence, 2),
                "all_probabilities": {name: round(float(prob)*100, 2) for name, prob in zip(class_names, probabilities)}
            }), 200

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            print(f"Error interno al procesar la imagen: {e}")
            return jsonify({"error": f"Error al procesar la imagen o realizar la predicción: {str(e)}"}), 500
    else:
        return jsonify({"error": "Tipo de archivo no permitido. Solo se aceptan .png, .jpg, .jpeg, .gif, .webp."}), 400

# --- Inicio de la aplicación Flask ---
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Carpeta de subidas '{UPLOAD_FOLDER}' creada o ya existente.")

    app.run(host='0.0.0.0', port=5000, debug=True)
