import tensorflow as tf
from tensorflow.keras import layers, models, regularizers
from tensorflow.keras.applications import MobileNetV2
import numpy as np
import os
import glob
import datetime

# --- Parámetros de Configuración ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_SPLIT_ROOT = os.path.join(SCRIPT_DIR, 'Dataset', 'Dataset_Fosiles_Completo', 'split')
train_dir = os.path.join(DATASET_SPLIT_ROOT, 'train_balanced')
val_dir = os.path.join(DATASET_SPLIT_ROOT, 'val')
test_dir = os.path.join(DATASET_SPLIT_ROOT, 'test')

IMG_HEIGHT = 224
IMG_WIDTH = 224

BATCH_SIZE = 32
EPOCHS_PHASE1 = 15 # Épocas para la fase de base congelada
EPOCHS_PHASE2 = 250 # Épocas adicionales para el fine-tuning (REDUCIDO A 150)
SEED = 123 # Para reproducibilidad

# --- Función de carga y preprocesamiento de imágenes ---
def _load_and_preprocess_image_py_func(image_path_tensor, label_tensor):
    image_path = image_path_tensor.numpy().decode('utf-8')
    label = label_tensor.numpy()
    try:
        img_bytes = tf.io.read_file(image_path)
        img = tf.image.decode_image(img_bytes, channels=3, expand_animations=False)
        img = tf.image.resize(img, [IMG_HEIGHT, IMG_WIDTH])
        img = tf.cast(img, tf.float32) / 255.0
        return img, label
    except Exception as e:
        print(f"!!! ERROR al procesar la imagen: {image_path}. Error: {e}")
        return tf.zeros((IMG_HEIGHT, IMG_WIDTH, 3), dtype=tf.float32), -1

def load_and_preprocess_image_tf_func(image_path_tensor, label_tensor):
    img, label = tf.py_function(
        _load_and_preprocess_image_py_func,
        inp=[image_path_tensor, label_tensor],
        Tout=[tf.float32, tf.int64]
    )
    img.set_shape([IMG_HEIGHT, IMG_WIDTH, 3])
    label.set_shape([])
    return img, label

# --- Función para obtener rutas de imágenes y etiquetas ---
def get_image_paths_and_labels(data_root_dir, class_names_list):
    all_image_paths = []
    all_image_labels = []
    class_to_idx = {name: i for i, name in enumerate(class_names_list)}
    print(f"Buscando imágenes en: {data_root_dir}")
    for class_name in class_names_list:
        class_path = os.path.join(data_root_dir, class_name)
        if not os.path.isdir(class_path):
            print(f"  Advertencia: La carpeta de clase '{class_name}' no existe en '{data_root_dir}'. Saltando.")
            continue
        label_idx = class_to_idx[class_name]
        current_class_paths = glob.glob(os.path.join(class_path, '*.jpg')) + \
                              glob.glob(os.path.join(class_path, '*.jpeg')) + \
                              glob.glob(os.path.join(class_path, '*.png')) + \
                              glob.glob(os.path.join(class_path, '*.gif')) + \
                              glob.glob(os.path.join(class_path, '*.bmp'))
        all_image_paths.extend(current_class_paths)
        all_image_labels.extend([label_idx] * len(current_class_paths))
        print(f"  Encontradas {len(current_class_paths)} imágenes para '{class_name}'")
    print(f"Total de imágenes encontradas en {data_root_dir}: {len(all_image_paths)}")
    return all_image_paths, all_image_labels

# --- Obtener nombres de clases y número de clases ---
class_names = sorted([d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))])
num_classes = len(class_names)
print(f"\nNombres de clases detectadas: {class_names}")
print(f"Número total de clases: {num_classes}")

class_names_path = os.path.join(SCRIPT_DIR, "class_names.npy")
np.save(class_names_path, np.array(class_names))
print(f"Clases guardadas como '{class_names_path}'")

AUTOTUNE = tf.data.AUTOTUNE

# --- Construcción de los Datasets de TensorFlow ---
train_image_paths, train_labels = get_image_paths_and_labels(train_dir, class_names)
train_ds = tf.data.Dataset.from_tensor_slices((tf.constant(train_image_paths), tf.constant(train_labels, dtype=tf.int64)))
train_ds = train_ds.map(load_and_preprocess_image_tf_func, num_parallel_calls=AUTOTUNE)
train_ds = train_ds.shuffle(buffer_size=1000, seed=SEED).batch(BATCH_SIZE).prefetch(buffer_size=AUTOTUNE).repeat()

val_image_paths, val_labels = get_image_paths_and_labels(val_dir, class_names)
val_ds = tf.data.Dataset.from_tensor_slices((tf.constant(val_image_paths), tf.constant(val_labels, dtype=tf.int64)))
val_ds = val_ds.map(load_and_preprocess_image_tf_func, num_parallel_calls=AUTOTUNE)
val_ds = val_ds.cache().batch(BATCH_SIZE).prefetch(buffer_size=AUTOTUNE)

test_image_paths, test_labels = get_image_paths_and_labels(test_dir, class_names)
test_ds = tf.data.Dataset.from_tensor_slices((tf.constant(test_image_paths), tf.constant(test_labels, dtype=tf.int64)))
test_ds = test_ds.map(load_and_preprocess_image_tf_func, num_parallel_calls=AUTOTUNE)
test_ds = test_ds.cache().batch(BATCH_SIZE).prefetch(buffer_size=AUTOTUNE)

# --- CAPAS DE AUMENTO DE DATOS ---
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
    layers.RandomContrast(0.2),
], name="data_augmentation")


# --- FASE 1: Entrenamiento de las capas de clasificación (Transferencia de Aprendizaje con Base Congelada) ---
print("\n--- FASE 1: Entrenamiento de las capas de clasificación (Base Congelada) ---")

base_model = MobileNetV2(
    input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False # Congelar la base

model = models.Sequential([
    layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
    data_augmentation,
    layers.Lambda(tf.keras.applications.mobilenet_v2.preprocess_input),
    base_model, # Aquí el base_model ya está congelado
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.005)),
    layers.Dropout(0.5),
    layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), # Tasa de aprendizaje de la Fase 1
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

log_dir_phase1 = os.path.join(SCRIPT_DIR, "logs", "fit", "phase1_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback_phase1 = tf.keras.callbacks.TensorBoard(log_dir=log_dir_phase1, histogram_freq=1)

steps_per_epoch = len(train_image_paths) // BATCH_SIZE
validation_steps = len(val_image_paths) // BATCH_SIZE

print(f"\nIniciando FASE 1 por {EPOCHS_PHASE1} épocas...")
history_phase1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_PHASE1,
    steps_per_epoch=steps_per_epoch,
    validation_steps=validation_steps,
    callbacks=[tensorboard_callback_phase1]
)

# --- FASE 2: Afinamiento Fino (Fine-tuning) ---
print("\n--- FASE 2: Afinamiento Fino (Fine-tuning) del modelo base ---")

# Descongelar las últimas capas del modelo base
base_model.trainable = True # Primero, se permite el entrenamiento de la base completa

# Congelar todas las capas excepto las últimas 50 (AUMENTADO EL NÚMERO DE CAPAS DESCONGELADAS)
for layer in base_model.layers[:-70]: # ¡Cambio aquí! De -30 a -50
    layer.trainable = False

# IMPORTANTE: Recompilar el modelo después de cambiar base_model.trainable
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001), # TASA DE APRENDIZAJE DE 1e-5
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

model.summary() # Revisa el summary para ver los nuevos parámetros entrenables

log_dir_phase2 = os.path.join(SCRIPT_DIR, "logs", "fit", "phase2_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard_callback_phase2 = tf.keras.callbacks.TensorBoard(log_dir=log_dir_phase2, histogram_freq=1)


print(f"\nIniciando FASE 2 (Fine-tuning) por {EPOCHS_PHASE2} épocas adicionales...")
history_phase2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_PHASE1 + EPOCHS_PHASE2, # Continuar desde las épocas de la Fase 1
    initial_epoch=history_phase1.epoch[-1] + 1, # Continuar desde la última época de la Fase 1
    steps_per_epoch=steps_per_epoch,
    validation_steps=validation_steps,
    callbacks=[tensorboard_callback_phase2]
)

# --- Evaluación del Modelo Final en el conjunto de prueba ---
print("\n--- Evaluando el modelo final en el conjunto de prueba ---")
test_steps = len(test_image_paths) // BATCH_SIZE
loss, accuracy = model.evaluate(
    test_ds,
    steps=test_steps,
    verbose=1
)
print(f"\nPrecisión final en el conjunto de prueba: {accuracy*100:.2f}%")
print(f"Pérdida final en el conjunto de prueba: {loss:.4f}")

# --- Guardar el Modelo Entrenado Final ---
model_save_path = os.path.join(SCRIPT_DIR, "fossil_classifier_finetuned_2par50%.keras")
model.save(model_save_path)
print(f"\nModelo final guardado como '{model_save_path}'")
