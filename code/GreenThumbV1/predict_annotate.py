# predict_annotate.py  — annotate images with top-3 MobileNetV3 species predictions
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tensorflow import keras
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input

# ---- Paths (adjust tag here if you change experiment name) ----
ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "species" / "experiments" / "ft224_cw" / "best.keras"
LABELS_TXT = ROOT / "models" / "species" / "release" / "labels.txt"   # preferred

OUT = ROOT / "predictions_out"
OUT.mkdir(exist_ok=True)

# ---- Load model safely (handles Lambda(preprocess_input) + ignores optimizer) ----
model = keras.models.load_model(
    MODEL,
    custom_objects={"preprocess_input": preprocess_input},
    compile=False
)
H, W = model.input_shape[1:3]

# ---- Load labels (fallbacks if labels.txt is missing) ----
def load_labels():
    if LABELS_TXT.exists():
        return [l.strip() for l in LABELS_TXT.read_text(encoding="utf-8").splitlines() if l.strip()]
    # fallback 1: meta/class_names.json (from earlier scripts)
    meta_json = ROOT / "models" / "species" / "meta" / "class_names.json"
    if meta_json.exists():
        import json
        return json.loads(meta_json.read_text(encoding="utf-8"))
    # fallback 2: alphabetical dirs from training split
    train_dir = ROOT / "data" / "splits" / "train"
    return sorted([d.name for d in train_dir.iterdir() if d.is_dir()])

labels = load_labels()

# ---- Prediction helpers ----
def predict_probs(img_path):
    img = keras.utils.load_img(img_path, target_size=(H, W))
    x = keras.utils.img_to_array(img)
    x = preprocess_input(x)[None, ...].astype("float32")
    probs = model.predict(x, verbose=0)[0]
    return probs

def topk_preds(probs, k=3):
    idxs = np.argsort(probs)[-k:][::-1]
    return [(labels[i], float(probs[i])) for i in idxs]

# ---- Drawing ----
def draw_label_bar(im: Image.Image, lines, pad=8):
    draw = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("arial.ttf", size=max(18, im.width // 32))
    except Exception:
        font = ImageFont.load_default()

    # compute text block size
    widths = []
    heights = []
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            w, h = draw.textlength(line, font=font), int(font.size * 1.4)
        widths.append(w); heights.append(h)
    box_w = max(widths) + pad * 2
    box_h = sum(heights) + pad * (len(lines) + 1)

    # black rectangle at top-left
    draw.rectangle([0, 0, box_w, box_h], fill=(0, 0, 0))
    # write each line
    y = pad
    for line, h in zip(lines, heights):
        draw.text((pad, y), line, fill=(255, 255, 255), font=font)
        y += h + pad

def annotate_one(src_path: Path, k=3) -> Path:
    probs = predict_probs(src_path)
    preds = topk_preds(probs, k=k)
    im = Image.open(src_path).convert("RGB")
    lines = [f"{name} ({p:.2f})" for name, p in preds]
    draw_label_bar(im, lines)
    out = OUT / (src_path.stem + "_pred.jpg")
    im.save(out, "JPEG", quality=92)
    return out

# ---- CLI ----
def main():
    if len(sys.argv) < 2:
        print("Usage: python src/predict_annotate.py <image_or_folder>")
        sys.exit(1)
    target = Path(sys.argv[1])
    if not target.exists():
        print("Path does not exist:", target)
        sys.exit(1)

    if target.is_file():
        out = annotate_one(target)
        print("Wrote", out)
    else:
        exts = {".jpg", ".jpeg", ".png", ".bmp"}
        files = [p for p in target.rglob("*") if p.suffix.lower() in exts]
        if not files:
            print("No images found in", target)
            sys.exit(0)
        for f in files:
            out = annotate_one(f)
            print("Wrote", out)

if __name__ == "__main__":
    main()
