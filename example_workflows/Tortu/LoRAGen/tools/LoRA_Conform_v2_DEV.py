import os
import sys
import subprocess

# Lightweight installer so this script can self-resolve deps
REQUIREMENTS = [
    ("piexif", "piexif"),
    ("imagehash", "ImageHash"),
    ("PIL", "Pillow"),
    ("deepface", "deepface"),
]

def _is_installed(import_name: str) -> bool:
    try:
        __import__(import_name)
        return True
    except Exception:
        return False

def _pip_install(spec: str) -> bool:
    cmds = [
        [sys.executable, "-m", "pip", "install", spec],
        [sys.executable, "-m", "pip", "install", "--user", spec],
        [sys.executable, "-m", "pip", "install", "--no-cache-dir", spec],
    ]
    for i, cmd in enumerate(cmds, 1):
        try:
            print(f"Installing {spec} (attempt {i})...")
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if r.returncode == 0:
                return True
            else:
                # Show brief error tail to avoid noise
                tail = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or [""]
                print(f"  Failed: {tail[0]}")
        except subprocess.TimeoutExpired:
            print("  Timed out")
        except Exception as e:
            print(f"  Error: {e}")
    return False

def install_missing_dependencies() -> bool:
    print("Checking and installing required dependencies...")
    ok = True
    for import_name, pkg_spec in REQUIREMENTS:
        if _is_installed(import_name):
            print(f"✓ {import_name} already installed")
            continue
        print(f"→ Installing {pkg_spec} (for import '{import_name}')")
        if not _pip_install(pkg_spec):
            print(f"✗ Could not install {pkg_spec}")
            ok = False
    if ok:
        print("All dependencies are satisfied.")
    else:
        print("Some dependencies failed to install. You may need to install them manually.")
    return ok

# Defer heavy imports until after optional --install handling
if __name__ == "__main__" and "--install" in sys.argv:
    success = install_missing_dependencies()
    sys.exit(0 if success else 1)

# Optional diagnostics to verify interpreter and TF stack
if __name__ == "__main__" and "--diagnose" in sys.argv:
    print("Python:", sys.executable)
    try:
        import tensorflow as tf  # type: ignore
        print("TensorFlow:", getattr(tf, "__version__", "?"))
        try:
            from tensorflow import keras as tf_keras  # type: ignore
            print("tensorflow.keras present")
        except Exception as e:
            print("tensorflow.keras import failed:", e)
    except Exception as e:
        print("TensorFlow import failed:", e)
    try:
        import deepface  # type: ignore
        print("DeepFace:", getattr(deepface, "__version__", "?"))
    except Exception as e:
        print("DeepFace import failed:", e)
    sys.exit(0)

# Now import runtime dependencies, with a helpful message on failure
# Ensure TensorFlow is importable before DeepFace triggers it implicitly
import tensorflow as tf
from tensorflow import keras as tf_keras
import piexif
import imagehash
from PIL import Image
from deepface import DeepFace
except ImportError as e:
print(f"Missing dependency: {e}")
print("Tip: verify you are using the intended venv.")
print("- Current Python:", sys.executable)
print('- Quick check: python -c "import tensorflow as tf; print(tf.version)"')
print("If TensorFlow is missing, install the pinned stack (Apple Silicon):")
print(" pip install 'numpy<2' 'protobuf==4.25.8' 'keras<3' 'tensorboard<2.20' 'tensorflow-macos==2.15.1' 'tensorflow-metal==1.*'")
print("Then re-run: python LoRA_Conform_v2_DEV.py")
sys.exit(1)

def write_exif(image_path, subject, expression):
    try:
        img = Image.open(image_path)
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        comment_str = f"Subject={subject};Expression={expression};Pose=POSE;Note=NOTE"
        encoded_comment = b'\x55\x00\x4e\x00\x49\x00\x43\x00\x4f\x00\x44\x00\x45\x00\x00\x00'
        encoded_comment += comment_str.encode('utf-16le')
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = encoded_comment
        exif_bytes = piexif.dump(exif_dict)
        img.save(image_path, "jpeg", exif=exif_bytes)
    except Exception as e:
        print(f"[EXIF ERROR] {image_path}: {e}")

def detect_expression(image_path, min_confidence=0.30, min_margin=0.15):
    try:
        result = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=False)
        emotions = result[0]['emotion']
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)

        top_emotion, top_score = sorted_emotions[0]
        second_emotion, second_score = sorted_emotions[1]

        if top_score > 1:
            top_score /= 100
            second_score /= 100

        if top_score >= min_confidence or (top_score - second_score) >= min_margin:
            return top_emotion.lower(), True
        else:
            print(f"⚠️ Low confidence: {top_emotion} ({top_score:.2f}) vs {second_emotion} ({second_score:.2f})")
            return top_emotion.lower(), False

    except Exception as e:
        print(f"[EMOTION ERROR] {image_path}: {e}")
        return "unknown", False

def convert_to_jpeg(src_path, dst_path):
    try:
        img = Image.open(src_path).convert("RGB")
        img.save(dst_path, "JPEG")
    except Exception as e:
        print(f"[CONVERT ERROR] {src_path}: {e}")

def hash_image(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        return str(imagehash.phash(img))
    except Exception as e:
        print(f"[HASH ERROR] {image_path}: {e}")
        return None

def main():
    print("=== LoRA Expression Tagger with Emotion Folders + NOTE Placeholder ===")

    base_dir = os.path.dirname(os.path.realpath(__file__))
    project_name = input("Enter project folder name (e.g. 'Trump'): ").strip()
    subject_label = input("Enter subject label for filenames (e.g. 'trump'): ").strip().lower()

    source_folder = os.path.join(base_dir, project_name, "00_SOURCE")
    expressions_root = os.path.join(base_dir, project_name, "01_EXPRESSIONS")
    review_folder = os.path.join(expressions_root, "_REVIEW")

    if not os.path.isdir(source_folder):
        print(f"❌ Source folder not found: {source_folder}")
        return

    os.makedirs(expressions_root, exist_ok=True)
    os.makedirs(review_folder, exist_ok=True)

    supported_ext = ('.jpg', '.jpeg', '.png', '.webp', '.avif')
    files = [f for f in os.listdir(source_folder) if f.lower().endswith(supported_ext)]
    files.sort()

    seen_hashes = set()
    counter = 1

    for filename in files:
        full_path = os.path.join(source_folder, filename)
        print(f"\n🔍 Processing [{counter}]: {filename}")

        img_hash = hash_image(full_path)
        if not img_hash:
            continue
        if img_hash in seen_hashes:
            print("⚠️ Duplicate detected, skipping.")
            continue
        seen_hashes.add(img_hash)

        # Detect expression
        expression, is_confident = detect_expression(full_path)
        filename_out = f"{subject_label}_{counter:03}_{expression}_POSE_NOTE.jpg"

        # Choose output folder
        if not is_confident:
            out_folder = review_folder
        else:
            out_folder = os.path.join(expressions_root, expression)
            os.makedirs(out_folder, exist_ok=True)

        output_path = os.path.join(out_folder, filename_out)

        # Convert and save
        convert_to_jpeg(full_path, output_path)
        write_exif(output_path, subject_label, expression)

        print(f"✅ Saved as: {filename_out} → {out_folder}")
        counter += 1

    print(f"\n🏁 Done!\nMain output: {expressions_root}\nReview folder: {review_folder}")

if __name__ == "__main__":
    main()
