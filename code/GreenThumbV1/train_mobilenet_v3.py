from pathlib import Path
import os, random, shutil, json
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input

random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
RAW_SPECIES = ROOT / "data" / "species"
SPLITS = ROOT / "data" / "splits"
MODEL_DIR = ROOT / "models" / "species"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

IMG_SIZE = (224, 224)
BATCH = 32
EPOCHS = 12

def make_splits_if_needed():
    if (SPLITS / "train").exists() and (SPLITS / "val").exists():
        print("✔ Splits already exist. Skipping split step.")
        return
    print("⏳ Creating 80/10/10 train/val/test splits...")
    for sp in ["train","val","test"]:
        (SPLITS / sp).mkdir(parents=True, exist_ok=True)
    for cls_dir in RAW_SPECIES.iterdir():
        if not cls_dir.is_dir(): continue
        files = [p for p in cls_dir.iterdir() if p.suffix.lower() in {".jpg",".jpeg",".png",".bmp",".gif"}]
        if not files: continue
        random.shuffle(files)
        n = len(files); tr = int(0.8*n); va = int(0.9*n)
        split_map = {"train": files[:tr], "val": files[tr:va], "test": files[va:]}
        for sp, items in split_map.items():
            out = SPLITS / sp / cls_dir.name
            out.mkdir(parents=True, exist_ok=True)
            for p in items:
                shutil.copy2(p, out / p.name)
    print("✔ Splits created under", SPLITS)

make_splits_if_needed()

train_ds = keras.utils.image_dataset_from_directory(
    SPLITS / "train", image_size=IMG_SIZE, batch_size=BATCH, label_mode="int", shuffle=True
)
val_ds = keras.utils.image_dataset_from_directory(
    SPLITS / "val", image_size=IMG_SIZE, batch_size=BATCH, label_mode="int", shuffle=False
)

class_names = train_ds.class_names
(MODEL_DIR / "meta").mkdir(exist_ok=True, parents=True)
with open(MODEL_DIR / "meta" / "class_names.json", "w", encoding="utf-8") as f:
    json.dump(class_names, f, ensure_ascii=False, indent=2)

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(2048).prefetch(AUTOTUNE)
val_ds   = val_ds.cache().prefetch(AUTOTUNE)

base = keras.applications.MobileNetV3Small(
    input_shape=IMG_SIZE + (3,), include_top=False, weights="imagenet"
)
base.trainable = False

inp = keras.Input(shape=IMG_SIZE + (3,))
x = layers.RandomFlip("horizontal")(inp)
x = layers.RandomRotation(0.05)(x)
x = layers.RandomZoom(0.1)(x)
x = layers.RandomContrast(0.1)(x)
x = layers.Lambda(preprocess_input)(x)   # <- correct scaling for MobileNetV3
x = base(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.2)(x)
out = layers.Dense(len(class_names), activation="softmax")(x)
model = keras.Model(inp, out)

model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

ckpt_path = MODEL_DIR / "best.keras"
callbacks = [
    keras.callbacks.ModelCheckpoint(ckpt_path, monitor="val_accuracy", save_best_only=True),
    keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True)
]

history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)

# ---------- Fine-tune last ~30 layers ----------
base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(1e-4),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

ft_callbacks = [
    keras.callbacks.ReduceLROnPlateau(monitor="val_accuracy", factor=0.5, patience=2, verbose=1),
    keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True),
    keras.callbacks.ModelCheckpoint(ckpt_path, monitor="val_accuracy", save_best_only=True)
]

model.fit(train_ds, validation_data=val_ds, epochs=8, callbacks=ft_callbacks)
model.save(MODEL_DIR / "best.keras")

# Optional quick test
test_dir = SPLITS / "test"
if test_dir.exists():
    test_ds = keras.utils.image_dataset_from_directory(
        test_dir, image_size=IMG_SIZE, batch_size=BATCH, label_mode="int", shuffle=False
    ).cache().prefetch(AUTOTUNE)
    test_metrics = model.evaluate(test_ds, verbose=0)
    print(f"Test loss={test_metrics[0]:.4f}  acc={test_metrics[1]:.4f}")

# Export TFLite of the fine-tuned model
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_bytes = converter.convert()
(MODEL_DIR / "model.tflite").write_bytes(tflite_bytes)
print("✔ Wrote TF-Lite model to", MODEL_DIR / "model.tflite")
