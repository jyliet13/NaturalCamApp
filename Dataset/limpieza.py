import os
import tensorflow as tf
from PIL import Image # Usaremos PIL para una verificación más robusta
import glob

def clean_dataset_images(dataset_root_dir):
    print(f"Iniciando limpieza de imágenes en: {dataset_root_dir}")
    total_cleaned = 0
    total_errors = 0

    # Iterar sobre las carpetas de clases (asumiendo que cada subcarpeta es una clase)
    for class_name in os.listdir(dataset_root_dir):
        class_path = os.path.join(dataset_root_dir, class_name)
        if not os.path.isdir(class_path):
            continue

        print(f"\nProcesando clase: {class_name}")
        image_files = glob.glob(os.path.join(class_path, '*')) # Obtener todos los archivos, sin importar la extensión

        for image_path in image_files:
            if os.path.isfile(image_path): # Asegurarse de que sea un archivo
                try:
                    # Intentar abrir con PIL para una verificación más robusta de formato
                    # y si el archivo está completo
                    with Image.open(image_path) as img:
                        img.verify() # Verifica que el archivo no está corrupto

                    # También intentar cargar con TensorFlow para atrapar otros problemas
                    img_bytes = tf.io.read_file(image_path)
                    _ = tf.image.decode_image(img_bytes, channels=3, expand_animations=False)

                except (tf.errors.InvalidArgumentError, tf.errors.OutOfRangeError, IOError, SyntaxError) as e:
                    print(f"!!! Detectado archivo problemático: {image_path}. Error: {e}")
                    # --- ¡AQUÍ ESTÁ EL CAMBIO CLAVE! ---
                    try:
                        os.remove(image_path)
                        print(f"--- Archivo eliminado: {image_path}")
                        total_cleaned += 1
                    except OSError as os_e:
                        print(f"Error al intentar eliminar el archivo {image_path}: {os_e}")
                    total_errors += 1
                except Exception as e:
                    print(f"Otro tipo de error con {image_path}: {e}")
                    total_errors += 1

    print(f"\n--- Limpieza completada en {dataset_root_dir} ---")
    print(f"Total de archivos problemáticos encontrados y eliminados: {total_cleaned}")
    print(f"Total de errores detectados (incluyendo los no eliminados): {total_errors}")

# --- RUTAS DE TUS DATASETS ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Asegúrate de que esta ruta sea la que apunta a la raíz de tu dataset original
# ANTES de que se divida en train/val/test
# Si tu dataset original está en 'Dataset/Fossil/Geo Fossils-I Dataset', úsala.
# Si el 'Dataset_Fosiles_Completo' es el original antes del split, úsala.
original_dataset_root = os.path.join(SCRIPT_DIR, 'Dataset_Fosiles_Completo', 'all_images') # Ajusta esta ruta si es diferente

# Ejecutar la limpieza en el dataset ORIGINAL
clean_dataset_images(original_dataset_root)

print("\nAhora que el dataset original está limpio, por favor, vuelve a ejecutar el split-folders.")