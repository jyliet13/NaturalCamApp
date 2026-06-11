import os
import shutil
import random
import numpy as np

def balance_train_dataset(train_dir_path, target_samples_per_class=None):
    """
    Balancea el número de muestras en el conjunto de entrenamiento.
    Submuestra las clases mayoritarias para que tengan un número similar de imágenes.

    Args:
        train_dir_path (str): Ruta al directorio 'train' de tu dataset dividido.
        target_samples_per_class (int, optional): Número deseado de muestras por clase.
                                                  Si es None, se usará la cantidad de muestras
                                                  de la clase con menos imágenes.
    """
    print(f"Iniciando balanceo del dataset de entrenamiento en: {train_dir_path}")

    class_counts = {}
    for class_name in os.listdir(train_dir_path):
        class_path = os.path.join(train_dir_path, class_name)
        if os.path.isdir(class_path):
            images = [f for f in os.listdir(class_path) if os.path.isfile(os.path.join(class_path, f))]
            class_counts[class_name] = len(images)
        else:
            print(f"Saltando {class_name} (no es un directorio).")

    if not class_counts:
        print("No se encontraron clases en el directorio de entrenamiento. Asegúrate de que la ruta sea correcta.")
        return

    print("\nConteo original de imágenes por clase en el conjunto de entrenamiento:")
    for class_name, count in class_counts.items():
        print(f"  {class_name}: {count} imágenes")

    if target_samples_per_class is None:
        min_samples = min(class_counts.values())
        target_samples_per_class = min_samples
        print(f"\nUsando la clase minoritaria para el objetivo: {target_samples_per_class} imágenes por clase.")
    else:
        print(f"\nObjetivo de muestras por clase: {target_samples_per_class} imágenes.")

    output_train_balanced_dir = train_dir_path + "_balanced"
    if os.path.exists(output_train_balanced_dir):
        print(f"Eliminando directorio existente: {output_train_balanced_dir}")
        shutil.rmtree(output_train_balanced_dir)
    os.makedirs(output_train_balanced_dir)
    print(f"Creando nuevo directorio para el dataset balanceado: {output_train_balanced_dir}")

    total_moved = 0
    total_kept = 0

    for class_name, count in class_counts.items():
        class_original_path = os.path.join(train_dir_path, class_name)
        class_balanced_path = os.path.join(output_train_balanced_dir, class_name)
        os.makedirs(class_balanced_path)

        all_images = [f for f in os.listdir(class_original_path) if os.path.isfile(os.path.join(class_original_path, f))]
        random.shuffle(all_images) # Mezclar para selección aleatoria

        if count > target_samples_per_class:
            images_to_keep = all_images[:target_samples_per_class]
            images_to_move_out = all_images[target_samples_per_class:]
            print(f"  {class_name}: Original: {count}, Manteniendo: {len(images_to_keep)}, Excedente: {len(images_to_move_out)}")
        else:
            images_to_keep = all_images
            images_to_move_out = []
            print(f"  {class_name}: Original: {count}, Menor o igual al objetivo, manteniendo todas.")

        for img_name in images_to_keep:
            src = os.path.join(class_original_path, img_name)
            dst = os.path.join(class_balanced_path, img_name)
            shutil.copy(src, dst) # Copiar las imágenes seleccionadas
            total_kept += 1

        # No necesitamos mover las imágenes excedentes a una nueva carpeta de "excedente"
        # para este propósito. Simplemente no las usamos.
        total_moved += len(images_to_move_out)

    print("\nBalanceo completado.")
    print(f"Total de imágenes copiadas al dataset balanceado: {total_kept}")
    print(f"Total de imágenes ignoradas (excedente): {total_moved}")
    print(f"\nAhora, tu modelo de entrenamiento debe usar el directorio '{output_train_balanced_dir}' para el conjunto de entrenamiento.")

# --- Ruta a tu directorio 'train' actual ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Asegúrate de que esta ruta apunte a tu carpeta 'train'
TRAIN_DATASET_PATH = os.path.join(SCRIPT_DIR, 'Dataset_Fosiles_Completo', 'split', 'train')

# --- EJECUTAR EL BALANCEO ---
# Puedes especificar un número objetivo si quieres (ej. 30 imágenes por clase)
# balance_train_dataset(TRAIN_DATASET_PATH, target_samples_per_class=30)
# O dejarlo en None para usar la clase minoritaria como objetivo:
balance_train_dataset(TRAIN_DATASET_PATH)