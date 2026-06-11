import splitfolders
import os

# Ruta a tu dataset unificado y sin duplicados
INPUT_FOLDER = 'Dataset_Fosiles_Completo/all_images'

# Ruta donde se creará la nueva estructura Train/Val/Test
# Se creará dentro de Dataset_Fosiles_Completo una nueva carpeta 'split'
OUTPUT_FOLDER = 'Dataset_Fosiles_Completo/split'

# Proporciones para la división: (entrenamiento, validación, test)
# Por ejemplo: 0.8 para train, 0.1 para val, 0.1 para test
# Puedes ajustar estos valores según necesites, pero 80/10/10 es un buen punto de partida.
SPLIT_RATIOS = (0.8, 0.1, 0.1)

if __name__ == '__main__':
    # Obtenemos la ruta absoluta del directorio del script para mayor robustez
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    FULL_INPUT_PATH = os.path.join(SCRIPT_DIR, INPUT_FOLDER)
    FULL_OUTPUT_PATH = os.path.join(SCRIPT_DIR, OUTPUT_FOLDER)

    print(f"Dividiendo dataset desde: {FULL_INPUT_PATH}")
    print(f"Creando estructura Train/Validation/Test en: {FULL_OUTPUT_PATH}")
    print(f"Proporciones de división: Train={SPLIT_RATIOS[0]}, Validation={SPLIT_RATIOS[1]}, Test={SPLIT_RATIOS[2]}")

    # La función splitfolders.ratio moverá los archivos
    # Se usa 'seed' para asegurar que la división sea la misma cada vez que se ejecute.
    splitfolders.ratio(FULL_INPUT_PATH,
                       output=FULL_OUTPUT_PATH,
                       ratio=SPLIT_RATIOS,
                       seed=42,
                       group_prefix=None) # No es necesario un prefijo de grupo aquí

    print("\n¡División del dataset completada!")
    print(f"Ahora tu dataset está organizado en:")
    print(f"  - {FULL_OUTPUT_PATH}/train")
    print(f"  - {FULL_OUTPUT_PATH}/val")
    print(f"  - {FULL_OUTPUT_PATH}/test")

    # Opcional: imprimir el número de archivos en cada subcarpeta para verificar
    for set_name in ['train', 'val', 'test']:
        set_path = os.path.join(FULL_OUTPUT_PATH, set_name)
        if os.path.exists(set_path):
            print(f"\nContenido de {set_name.upper()} set:")
            for class_folder in sorted(os.listdir(set_path)):
                class_folder_path = os.path.join(set_path, class_folder)
                if os.path.isdir(class_folder_path):
                    num_files = len([f for f in os.listdir(class_folder_path) if os.path.isfile(os.path.join(class_folder_path, f))])
                    print(f"  {class_folder}: {num_files} imágenes")