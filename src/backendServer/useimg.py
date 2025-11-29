from PIL import Image
import os
import sys

IMAGES_DIR = "received_images"


def get_latest_image(directory):
    try:
        files = [os.path.join(directory, f) for f in os.listdir(directory)
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp'))]
        if not files:
            return None
        latest = max(files, key=os.path.getmtime)
        return latest
    except Exception:
        return None


def main():
    # Optional: pass a path or filename as first argument
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isdir(path):
            target = get_latest_image(path)
            if not target:
                print(f"No images found in directory: {path}")
                sys.exit(1)
        elif os.path.isfile(path):
            target = path
        else:
            print(f"Path not found: {path}")
            sys.exit(1)
    else:
        if not os.path.exists(IMAGES_DIR):
            print(f"Directory '{IMAGES_DIR}' not found.")
            sys.exit(1)
        target = get_latest_image(IMAGES_DIR)
        if not target:
            print(f"No image files found in '{IMAGES_DIR}'.")
            sys.exit(1)

    print(f"Opening image: {target}")
    try:
        img = Image.open(target)
        print(f"Format: {img.format}, Size: {img.size}, Mode: {img.mode}")
        img.show()
    except Exception as e:
        print(f"Failed to open image: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
