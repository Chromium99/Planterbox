import argparse, json, random, shutil
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

random.seed(42)
tf.get_logger().setLevel('ERROR')

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ROOT / "data" / "splits"
OUTDIR = ROOT / "models" / "species" / "experiments"
OUTDIR.mkdir(parents=True, exist_ok=True)

def build_ds(img_size, batch):
    train = keras.utils.image_dataset_from_directory(SPLITS/"train", image_size=img_size, batch_size=batch, label_mode="int", shuffle=True)
    val   = keras.utils.image_dataset_from_directory(SPLITS/"val",   image_size=img_size, batch_size=batch, label_mode="int", shuffle=False)
    test  = keras.utils.image_dataset_from_directory(SPLITS/"test",  image_size=img_size, batch_size=batch, label_mode="int", shuffle=False)
    AUTOTUNE=tf.data.AUTOTUNE
    return (train.cache().shuffle(2048).prefetch(AUTOTUNE),
            val.cache().prefetch(AUTOTUNE),
            test.cache().prefetch(AUTOTUNE),
            train.class_names)

def class_weights(train_root, classes):
    counts=[]
    for i,c in enumerate(classes):
        p = (train_root/c)
        n = len([x for x in p.iterdir() if x.suffix.lower() in (".jpg",".jpeg",".png",".bmp",".gif")])
        counts.append(n)
    total=sum(counts)
    return {i: total/(len(classes)*n) for i,n in enumerate(counts)}, counts

def build_model(num_classes, img_size, freeze_bn=False):
    base = keras.applications.MobileNetV3Small(input_shape=img_size+(3,), include_top=False, weights="imagenet")
    # augmentation
    aug = keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.07),
        layers.RandomZoom(0.15),
        layers.RandomContrast(0.15),
        layers.GaussianNoise(0.02),
    ])
    inp = keras.Input(shape=img_size+(3,))
    x = aug(inp)
    x = layers.Lambda(preprocess_input)(x)      # [-1,1] scaling
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    out = layers.Dense(num_classes, activation="softmax")(x)
    model = keras.Model(inp, out)
    return model, base

def eval_and_log(model, ds_test, classes, out_dir, tag):
    # collect preds/labels
    y_true=[]; y_prob=[]
    for xb, yb in ds_test:
        y_true.append(yb.numpy())
        y_prob.append(model.predict(xb, verbose=0))
    y_true = np.concatenate(y_true)
    y_prob = np.concatenate(y_prob)
    y_pred = y_prob.argmax(1)

    rep = classification_report(y_true, y_pred, target_names=classes, output_dict=True, zero_division=0)
    cm  = confusion_matrix(y_true, y_pred)
    acc = rep['accuracy']; macro_f1 = rep['macro avg']['f1-score']

    # save metrics
    pd.DataFrame(rep).to_csv(out_dir/f"{tag}_report.csv")
    pd.DataFrame(cm, index=classes, columns=classes).to_csv(out_dir/f"{tag}_confusion.csv")
    with open(out_dir/f"{tag}_summary.json","w") as f:
        json.dump({"accuracy":acc, "macro_f1":macro_f1}, f, indent=2)
    print(f"Test accuracy={acc:.4f}  macroF1={macro_f1:.4f}")
    return acc, macro_f1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", type=int, default=224)                # 224 or 256
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--epochs", type=int, default=12)
    ap.add_argument("--finetune", action="store_true")             # add fine-tuning phase
    ap.add_argument("--unfreeze_last", type=int, default=30)       # how many layers to unfreeze
    ap.add_argument("--freeze_bn", action="store_true")            # keep BN frozen during finetune
    ap.add_argument("--class_weight", action="store_true")         # use class weighting
    ap.add_argument("--tag", default="run")                        # name for logs/artifacts
    args = ap.parse_args()

    img_size=(args.img,args.img)
    train_ds, val_ds, test_ds, classes = build_ds(img_size, args.batch)

    model, base = build_model(len(classes), img_size)
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    out_dir = OUTDIR/args.tag
    if out_dir.exists(): shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    cw=None; counts=None
    if args.class_weight:
        cw, counts = class_weights(SPLITS/"train", classes)
        print("Using class weights.")

    cb = [
        keras.callbacks.ModelCheckpoint(out_dir/"best.keras", monitor="val_accuracy", save_best_only=True),
        keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True),
    ]

    print("== Baseline training ==")
    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=cb, class_weight=cw)

    # Optional fine-tune
    if args.finetune:
        print("== Fine-tuning ==")
        base.trainable = True
        # freeze BN layers if requested
        for layer in base.layers:
            if args.freeze_bn and isinstance(layer, layers.BatchNormalization):
                layer.trainable = False
        for layer in base.layers[:-args.unfreeze_last]:
            if not (args.freeze_bn and isinstance(layer, layers.BatchNormalization)):
                layer.trainable = False

        steps_per_epoch = int(np.ceil(sum(counts or [1])*0.8 / args.batch))
        schedule = keras.optimizers.schedules.CosineDecayRestarts(
            initial_learning_rate=1e-4, first_decay_steps=max(1, steps_per_epoch*3)
        )
        model.compile(optimizer=keras.optimizers.Adam(schedule),
                      loss="sparse_categorical_crossentropy", metrics=["accuracy"])
        ft_cb = [
            keras.callbacks.ReduceLROnPlateau(monitor="val_accuracy", factor=0.5, patience=2, verbose=1),
            keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True),
            keras.callbacks.ModelCheckpoint(out_dir/"best.keras", monitor="val_accuracy", save_best_only=True)
        ]
        model.fit(train_ds, validation_data=val_ds, epochs=8, callbacks=ft_cb, class_weight=cw)

    # Evaluate + export
    acc, macro_f1 = eval_and_log(model, test_ds, classes, out_dir, args.tag)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations=[tf.lite.Optimize.DEFAULT]
    tfl = converter.convert()
    (out_dir/"model.tflite").write_bytes(tfl)
    print("Wrote", out_dir/"model.tflite")

if __name__ == "__main__":
    main()
