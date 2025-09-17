import os
import sys
import subprocess

# Lightweight installer so this script can self-resolve deps
REQUIREMENTS = [
    ("piexif", "piexif"),
    ("imagehash", "ImageHash"),
    ("PIL", "Pillow"),
    ("deepface", "deepface"),
    ("easyocr", "easyocr"),
    ("cv2", "opencv-python"),
    ("rembg", "rembg"),
    ("skimage", "scikit-image"),
    ("onnxruntime", "onnxruntime"),
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

# Show help before any heavy imports
if __name__ == "__main__" and ("--help" in sys.argv or "-h" in sys.argv):
    print("LoRA Conform v4 - Image Processing for LoRA Training")
    print("\nUsage: python LoRA_Conform_v4_DEV.py [options]")
    print("\nProcessing flags:")
    print("  --face              Enable face detection for face-centered cropping")
    print("  --exp, --expressions Enable face detection + expression analysis (creates expressions folders)")
    print("  --fnk               Preserve original filename (default: rewrite with trigger_word+increment)")
    print("  --text-no           Enable text removal (default: disabled)")
    print("  --bg-remove         Remove background (default: disabled)")
    print("  --pad               Use edge-aware padding instead of black fill (default: disabled)")
    print("  --sidecar-no        Disable Kohya .txt caption files (default: enabled)")
    print("  --sidecar-keep      Preserve existing sidecars (default: overwrite existing caption files)")
    print("  --caption \"text\"     Set custom caption text")
    print("\nUtility flags:")
    print("  --install           Install missing dependencies and exit")
    print("  --diagnose          Show system diagnostics and exit")
    print("  --help, -h          Show this help message")
    sys.exit(0)

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
try:
    import tensorflow as tf
    from tensorflow import keras as tf_keras
    import piexif
    import imagehash
    from PIL import Image
    from deepface import DeepFace
    import easyocr
    import cv2
    import numpy as np
    from rembg import remove
    from skimage import segmentation, color
    import json
    from pathlib import Path
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Tip: verify you are using the intended venv.")
    print("- Current Python:", sys.executable)
    print('- Quick check: python -c "import tensorflow as tf; print(tf.version)"')
    print("If TensorFlow is missing, install the pinned stack (Apple Silicon):")
    print(" pip install 'numpy<2' 'protobuf==4.25.8' 'keras<3' 'tensorboard<2.20' 'tensorflow-macos==2.15.1' 'tensorflow-metal==1.*'")
    print("Then re-run: python LoRA_Conform_v2_DEV.py")
    sys.exit(1)

def sidecar_update(image_path: str, *, overwrite=False, caption=None):
    """
    Create/update Kohya-compliant .txt caption file next to the image.
    If caption file exists and overwrite=False, keep existing content.
    If caption file exists and overwrite=True, replace with new caption.
    If caption is not None, use it; otherwise write placeholder.
    """
    # Get .txt file path (same name as image, different extension)
    txt_path = os.path.splitext(image_path)[0] + ".txt"
    
    # Determine caption to use
    if caption is not None:
        use_caption = caption
    else:
        use_caption = "girallon, monster, white fur, four arms, four armed gorilla with tail, fierce expression, no horns, no tusks, fantasy creature, dnd, d&d"
    
    # Check if txt file exists
    if os.path.exists(txt_path) and not overwrite:
        # Keep existing caption
        return
    
    # Write caption file
    try:
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(use_caption)
    except IOError as e:
        print(f"[SIDECAR ERROR] Could not write {txt_path}: {e}")

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

def detect_face_for_cropping(image_path):
    """Detect face for cropping purposes using DeepFace."""
    try:
        result = DeepFace.analyze(img_path=image_path, actions=['emotion'], enforce_detection=True)
        # Get face region if detected
        if 'region' in result[0]:
            region = result[0]['region']
            return {
                'x': region['x'],
                'y': region['y'], 
                'w': region['w'],
                'h': region['h']
            }
        return None
    except Exception as e:
        print(f"[FACE DETECTION ERROR] {image_path}: {e}")
        return None

def detect_expression(image_path, min_confidence=0.30, min_margin=0.15, skip_detection=False):
    if skip_detection:
        return "neutral", True
    
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

def convert_to_jpeg(src_path, dst_path, remove_text=True, remove_bg=False, smart_pad=False, face_region=None):
    try:
        img = Image.open(src_path).convert("RGB")
        
        # Crop to face region if provided
        if face_region:
            print("  👤 Cropping to face region...")
            x, y, w, h = face_region['x'], face_region['y'], face_region['w'], face_region['h']
            # Add some padding around the face (20% on each side)
            padding = 0.2
            pad_x = int(w * padding)
            pad_y = int(h * padding)
            crop_x = max(0, x - pad_x)
            crop_y = max(0, y - pad_y)
            crop_w = min(img.width - crop_x, w + 2 * pad_x)
            crop_h = min(img.height - crop_y, h + 2 * pad_y)
            img = img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
        
        # Remove text if enabled
        if remove_text:
            print("  📝 Removing text...")
            img = remove_text_from_image(img)
        
        # Background processing
        if remove_bg:
            print("  🎭 Removing background...")
            img = remove_background(img)
        
        # Resize to 1024x1024 square with appropriate padding
        target_size = 1024
        width, height = img.size
        
        if width != height:
            if smart_pad and not remove_bg:
                print("  🎨 Smart padding...")
                img = smart_pad_image(img)
            else:
                # Default padding (black for normal, neutral for background removal)
                pad_color = (240, 240, 240) if remove_bg else (0, 0, 0)
                max_side = max(width, height)
                new_img = Image.new('RGB', (max_side, max_side), pad_color)
                paste_x = (max_side - width) // 2
                paste_y = (max_side - height) // 2
                new_img.paste(img, (paste_x, paste_y))
                img = new_img
        
        # Resize to target size
        img = img.resize((target_size, target_size), Image.LANCZOS)
        img.save(dst_path, "JPEG")
    except Exception as e:
        print(f"[CONVERT ERROR] {src_path}: {e}")

def remove_background(img, neutral_color=(240, 240, 240)):
    try:
        # Convert PIL to bytes for rembg
        import io
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        # Remove background
        result_bytes = remove(img_bytes)
        
        # Convert back to PIL
        result_img = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
        
        # Create new image with neutral background
        neutral_bg = Image.new("RGB", result_img.size, neutral_color)
        neutral_bg.paste(result_img, mask=result_img.split()[-1])  # Use alpha as mask
        
        return neutral_bg
        
    except Exception as e:
        print(f"[BACKGROUND REMOVAL ERROR]: {e}")
        return img

def smart_pad_image(img):
    try:
        width, height = img.size
        max_side = max(width, height)
        
        # Convert to numpy for edge detection
        img_np = np.array(img)
        
        # Get edge colors by sampling border pixels
        top_edge = img_np[0, :, :].mean(axis=0)
        bottom_edge = img_np[-1, :, :].mean(axis=0)
        left_edge = img_np[:, 0, :].mean(axis=0)
        right_edge = img_np[:, -1, :].mean(axis=0)
        
        # Average all edge colors for padding
        avg_edge_color = np.mean([top_edge, bottom_edge, left_edge, right_edge], axis=0)
        pad_color = tuple(int(c) for c in avg_edge_color)
        
        # Create padded image
        new_img = Image.new('RGB', (max_side, max_side), pad_color)
        paste_x = (max_side - width) // 2
        paste_y = (max_side - height) // 2
        new_img.paste(img, (paste_x, paste_y))
        
        return new_img
        
    except Exception as e:
        print(f"[SMART PAD ERROR]: {e}")
        # Fallback to black padding
        max_side = max(img.size)
        new_img = Image.new('RGB', (max_side, max_side), (0, 0, 0))
        paste_x = (max_side - img.size[0]) // 2
        paste_y = (max_side - img.size[1]) // 2
        new_img.paste(img, (paste_x, paste_y))
        return new_img

def remove_text_from_image(img):
    try:
        # Convert PIL image to numpy array for OpenCV
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Initialize EasyOCR reader (English only for speed)
        reader = easyocr.Reader(['en'], gpu=False)
        
        # Detect text regions
        results = reader.readtext(img_cv)
        
        if not results:
            return img  # No text detected
        
        # Create a mask for text regions
        mask = np.zeros(img_cv.shape[:2], dtype=np.uint8)
        
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # Only remove high-confidence text detections
                # Convert bbox to integer coordinates
                bbox = np.array(bbox, dtype=np.int32)
                cv2.fillPoly(mask, [bbox], 255)
        
        # Inpaint text regions with surrounding background
        inpainted = cv2.inpaint(img_cv, mask, 3, cv2.INPAINT_TELEA)
        
        # Convert back to PIL
        result_img = Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))
        return result_img
        
    except Exception as e:
        print(f"[TEXT REMOVAL ERROR]: {e}")
        return img  # Return original if text removal fails

def hash_image(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        return str(imagehash.phash(img))
    except Exception as e:
        print(f"[HASH ERROR] {image_path}: {e}")
        return None

def main():
    # Parse face and expression flags
    enable_face_detection = "--face" in sys.argv
    enable_expressions = "--expressions" in sys.argv or "--exp" in sys.argv
    preserve_filename = "--fnk" in sys.argv
    remove_text = "--text-no" in sys.argv  # Default: disabled, --text-no to enable
    remove_bg = "--bg-remove" in sys.argv  # Default: disabled, --bg-remove to enable
    smart_pad = "--pad" in sys.argv  # Default: disabled, --pad to enable edge-aware padding
    enable_sidecar = "--sidecar-no" not in sys.argv  # Default: enabled, --sidecar-no to disable
    sidecar_overwrite = "--sidecar-keep" not in sys.argv  # Default: overwrite, --sidecar-keep to preserve
    
    # Parse custom caption from command line
    custom_caption = None
    for i, arg in enumerate(sys.argv):
        if arg == "--caption" and i + 1 < len(sys.argv):
            custom_caption = sys.argv[i + 1]
            break
    
    if enable_expressions:
        print("=== LoRA Expression Tagger with Emotion Folders + NOTE Placeholder ===")
        print("👤 Face detection: ENABLED (for expression analysis)")
        print("😊 Expression analysis: ENABLED (creates emotion subfolders)")
    elif enable_face_detection:
        print("=== LoRA Face-Centered Cropping Tagger ===")
        print("👤 Face detection: ENABLED (for cropping only)")
        print("😊 Expression analysis: DISABLED")
    else:
        print("=== LoRA Conform Tagger (No Face Detection) ===")
        print("👤 Face detection: DISABLED")
        print("😊 Expression analysis: DISABLED")
    
    if remove_text:
        print("📝 Text removal: ENABLED")
    else:
        print("📝 Text removal: DISABLED")
    
    if remove_bg:
        print("🎭 Background removal: ENABLED (default - neutral background)")
    elif smart_pad:
        print("🎨 Smart padding: ENABLED (edge-aware fill)")
    else:
        print("⬛ Standard padding: ENABLED (black fill)")
    
    if enable_sidecar:
        if custom_caption:
            print(f"📋 Kohya caption files: ENABLED (custom: '{custom_caption}', overwrite={sidecar_overwrite})")
        else:
            print(f"📋 Kohya caption files: ENABLED (default placeholder, overwrite={sidecar_overwrite})")
    else:
        print("📋 Kohya caption files: DISABLED")

    base_dir = os.path.dirname(os.path.realpath(__file__))
    project_name = input("Enter project folder name (e.g. 'Trump'): ").strip()
    subject_label = input("Enter subject label for filenames (e.g. 'trump'): ").strip().lower()

    source_folder = os.path.join(base_dir, project_name, "00_SOURCE")
    conform_root = os.path.join(base_dir, project_name, "01_CONFORM")
    
    if enable_expressions:
        expressions_root = os.path.join(conform_root, "expressions")
        review_folder = os.path.join(expressions_root, "_REVIEW")
    else:
        expressions_root = conform_root
        review_folder = None

    if not os.path.isdir(source_folder):
        print(f"❌ Source folder not found: {source_folder}")
        return

    os.makedirs(expressions_root, exist_ok=True)
    if review_folder:
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

        # Handle face detection for cropping
        face_region = None
        if enable_face_detection:
            face_region = detect_face_for_cropping(full_path)
            if not face_region:
                print("⚠️ No face detected for cropping, using full image")
        
        # Detect expression if expressions enabled
        if enable_expressions:
            expression, is_confident = detect_expression(full_path, skip_detection=False)
        else:
            expression, is_confident = "neutral", True
        
        # Generate filename
        if preserve_filename:
            base_name = os.path.splitext(filename)[0]
            filename_out = f"{base_name}_C.jpg"
        else:
            filename_out = f"{subject_label}_{counter:03d}.jpg"

        # Choose output folder
        if enable_expressions:
            if not is_confident:
                out_folder = review_folder
            else:
                out_folder = os.path.join(expressions_root, expression)
                os.makedirs(out_folder, exist_ok=True)
        else:
            # No expressions - everything goes to conform root
            out_folder = expressions_root

        output_path = os.path.join(out_folder, filename_out)

        # Create Kohya caption file if enabled
        if enable_sidecar:
            sidecar_update(output_path, overwrite=sidecar_overwrite, caption=custom_caption)

        # Convert and save
        convert_to_jpeg(full_path, output_path, remove_text=remove_text, remove_bg=remove_bg, smart_pad=smart_pad, face_region=face_region)
        write_exif(output_path, subject_label, expression)

        print(f"✅ Saved as: {filename_out} → {out_folder}")
        counter += 1

    if enable_expressions:
        print(f"\n🏁 Done!\nMain output: {expressions_root}\nReview folder: {review_folder}")
    else:
        print(f"\n🏁 Done!\nOutput folder: {expressions_root}")

if __name__ == "__main__":
    main()
