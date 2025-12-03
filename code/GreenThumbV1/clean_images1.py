from pathlib import Path
from typing import Iterable, Set
import shutil

from PIL import Image, UnidentifiedImageError

# Folder to read images from
ROOT = Path(r"E:\CUNY\Fall 25\senior design\practice server\received_images")
# Where to store the converted copy (separate output folder)
OUTPUT_DIR = Path(r"E:\CUNY\Fall 25\senior design\practice server\cleaned_output")
# Extensions that count as images
VALID_EXTS: Set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def iter_images(dirpath: Path, exts: Iterable[str]) -> list[Path]:
    """Return all image files under dirpath matching the given extensions."""
    wanted = {e.lower() for e in exts}
    return [p for p in dirpath.rglob("*") if p.is_file() and p.suffix.lower() in wanted]


def get_latest_image(dirpath: Path, exts: Iterable[str]) -> Path:
    """Return the newest image path in dirpath based on modification time."""
    images = iter_images(dirpath, exts)
    if not images:
        raise ValueError(f"No valid images in {dirpath}")
    return max(images, key=lambda p: p.stat().st_mtime)


def convert_to_jpg(path: Path) -> Path:
    """Convert image to JPG (RGB). Returns output path; removes original if needed."""
    with Image.open(path) as im:
        im = im.convert("RGB")
        out = path.with_suffix(".jpg")
        im.save(out, "JPEG", quality=92)
    if out != path:
        path.unlink(missing_ok=True)
    return out


def save_to_folder(path: Path, dest_dir: Path) -> Path:
    """Copy path into dest_dir, creating the folder if needed."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / path.name
    shutil.copy2(path, dest_path)
    return dest_path


def main() -> None:
    try:
        newest = get_latest_image(ROOT, VALID_EXTS)
    except ValueError as exc:
        print(exc)
        return

    kept = bad = 0
    out_path: Path | None = None
    try:
        out_path = convert_to_jpg(newest)
        kept += 1
    except (UnidentifiedImageError, OSError):
        newest.unlink(missing_ok=True)
        bad += 1

    print(f"Converted/kept: {kept}  |  removed bad files: {bad}")

    if not out_path:
        return

    # Save the converted image to the output folder
    saved_path = save_to_folder(out_path, OUTPUT_DIR)
    print(f"Saved converted image to: {saved_path}")

    # Preview the newest image after conversion
    try:
        with Image.open(out_path) as img:
            img.show()
    except (UnidentifiedImageError, OSError) as exc:
        print(f"Unable to preview image: {exc}")


if __name__ == "__main__":
    main()
