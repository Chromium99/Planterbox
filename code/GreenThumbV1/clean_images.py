from pathlib import Path
from PIL import Image, UnidentifiedImageError

# path to your split dataset
root = Path(r"C:\Users\rodri\Documents\Planterbox\data\splits")

kept = bad = 0
for p in root.rglob("*"):
    if not p.is_file():
        continue
    if p.suffix.lower() not in (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"):
        continue
    try:
        im = Image.open(p)
        im = im.convert("RGB")  # forces 3-channel RGB
        out = p.with_suffix(".jpg")  # always save as .jpg
        im.save(out, "JPEG", quality=92)
        if out != p:
            p.unlink(missing_ok=True)  # delete old version if needed
        kept += 1
    except (UnidentifiedImageError, OSError):
        # broken or unreadable → delete
        p.unlink(missing_ok=True)
        bad += 1

print(f"Converted/kept: {kept}  |  removed bad files: {bad}")
