import os

# Ruta al directorio donde están todas tus imágenes unificadas (con posibles duplicados _1, _2, etc.)
DATASET_PATH = 'Dataset_Fosiles_Completo/all_images'


def delete_suffixed_duplicates(dataset_root_path):
    """
    Elimina archivos que parecen ser duplicados generados por el script de unificación,
    identificándolos por la presencia de un guion bajo seguido de un número y extensión
    (ej. 'imagen_1.jpg', 'foto_2.png').
    """
    print(f"Buscando y eliminando duplicados con sufijo '_' en: {dataset_root_path}")
    removed_count = 0

    for class_name in os.listdir(dataset_root_path):
        class_path = os.path.join(dataset_root_path, class_name)
        if os.path.isdir(class_path):
            print(f"Procesando clase: {class_name}")
            for filename in os.listdir(class_path):
                # Patrón para identificar los duplicados generados:
                # Busca un guion bajo seguido de uno o más dígitos, antes de la extensión.
                # Ejemplo: "imagen_1.jpg", "fossil_02.png"
                name_parts = os.path.splitext(filename)
                base_name = name_parts[0]
                extension = name_parts[1]

                # Comprueba si el nombre base termina con _ + número
                if '_' in base_name:
                    last_part = base_name.split('_')[-1]
                    if last_part.isdigit():
                        # Intenta eliminar el archivo
                        filepath_to_delete = os.path.join(class_path, filename)
                        try:
                            os.remove(filepath_to_delete)
                            removed_count += 1
                            # print(f"  Eliminado: {filepath_to_delete}") # Descomentar para depuración detallada
                        except Exception as e:
                            print(f"  Error al eliminar {filepath_to_delete}: {e}")

    print(f"\n--- Resumen de Eliminación de Duplicados por Nombre ---")
    print(f"Total de imágenes duplicadas (con sufijo '_') eliminadas: {removed_count}")
    print(f"Proceso completado en: {dataset_root_path}")


if __name__ == "__main__":
    # Asegúrate de que DATASET_PATH apunte a la carpeta 'all_images'
    # Obtenemos la ruta absoluta para mayor robustez
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    FULL_DATASET_PATH = os.path.join(SCRIPT_DIR, DATASET_PATH)

    delete_suffixed_duplicates(FULL_DATASET_PATH)