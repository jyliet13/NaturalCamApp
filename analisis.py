#%%
import tensorflow as tf
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

#%% md
# CARGAR MODELO ENTRENADO
#%%
model = tf.keras.models.load_model("fossil_classifier.keras")
#%% md
# cagar las clases
#%%
class_names = np.load("class_names.npy")
#%% md
# RUTA AL DATASET
#%%
dataset_dir = "Dataset/Fossil/Geo Fossils-I Dataset"
img_size = (150, 150)
batch_size = 32
#%%
# Cargar dataset de validación
val_ds = tf.keras.utils.image_dataset_from_directory(
    dataset_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=img_size,
    batch_size=batch_size
).cache().prefetch(buffer_size=tf.data.AUTOTUNE)
#%%
# Obtener etiquetas verdaderas y predicciones
y_true = []
y_pred = []

for images, labels in val_ds:
    preds = model.predict(images)
    y_true.extend(labels.numpy())
    y_pred.extend(np.argmax(preds, axis=1))
#%%
# Reporte de clasificación
print("Reporte de clasificación:\n")
print(classification_report(y_true, y_pred, target_names=class_names))
#%%
# Matriz de confusión
print("Matriz de confusión:")
print(confusion_matrix(y_true, y_pred))
#%%
#  Gráfica de matriz de confusión
import seaborn as sns
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt="d", xticklabels=class_names, yticklabels=class_names, cmap="Blues")
plt.xlabel("Predicción")
plt.ylabel("Real")
plt.title("Matriz de Confusión")
plt.show()