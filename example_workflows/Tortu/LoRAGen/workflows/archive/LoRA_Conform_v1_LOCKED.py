import os
import piexif
import imagehash
from PIL import Image
from deepface import DeepFace

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
