# __init__.py 
# ComfyUI-TORTU
######################################

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Check for dependencies and auto-install if needed
def check_and_install_dependencies():
    """Check if dependencies are available, install if missing"""
    missing_deps = []
    
    try:
        import mediapipe
    except ImportError:
        missing_deps.append("mediapipe")
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    # Check for DeepFace (for emotion detection)
    try:
        import deepface
    except ImportError:
        missing_deps.append("deepface")
    
    # Check for imagehash (for duplicate detection)
    try:
        import imagehash
    except ImportError:
        missing_deps.append("imagehash")
    
    # Check for piexif (for EXIF metadata writing)
    try:
        import piexif
    except ImportError:
        missing_deps.append("piexif")
    
    # Check for kohya-ss (for LoRa training)
    try:
        import kohya_ss
    except ImportError:
        missing_deps.append("kohya-ss")
    
    # Check for jsonschema (for LoRa metadata validation)
    try:
        import jsonschema
    except ImportError:
        missing_deps.append("jsonschema")
    
    if missing_deps:
        print(f"🐢 TORTU: Missing dependencies: {', '.join(missing_deps)}")
        print("🐢 TORTU: Attempting automatic installation...")
        
        try:
            from . import install
            if hasattr(install, 'install_requirements'):
                success = install.install_requirements()
                if success:
                    print("🐢 TORTU: Dependencies installed! Please restart ComfyUI.")
                else:
                    print("🐢 TORTU: Auto-install failed. Please install manually:")
                    print("   - mediapipe>=0.10.0")
                    print("   - opencv-python>=4.5.0")
                    print("   - deepface>=0.0.75")
                    print("   - imagehash>=4.3.0")
                    print("   - piexif>=1.1.3")
                    print("   - kohya-ss>=23.0.0")
            return len(missing_deps) == 0
        except Exception as e:
            print(f"🐢 TORTU: Auto-install error: {e}")
            print("🐢 TORTU: Please install dependencies manually.")
            return False
    
    return True

# Check dependencies first
deps_ok = check_and_install_dependencies()

# Try to import each module individually to avoid total failure
try:
    from .detection.detect_faces import NODE_CLASS_MAPPINGS as FACE_NODES, NODE_DISPLAY_NAME_MAPPINGS as FACE_DISPLAY
    NODE_CLASS_MAPPINGS.update(FACE_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(FACE_DISPLAY)
    print("🐢 TORTU: Face detection nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Failed to load face detection nodes: {e}")

try:
    from .detection.detect_emotion import NODE_CLASS_MAPPINGS as EMOTION_NODES, NODE_DISPLAY_NAME_MAPPINGS as EMOTION_DISPLAY
    NODE_CLASS_MAPPINGS.update(EMOTION_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(EMOTION_DISPLAY)
    print("🐢 TORTU: Emotion detection nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Failed to load emotion detection nodes: {e}")

try:
    from .detection.detect_duplicates import NODE_CLASS_MAPPINGS as DUP_NODES, NODE_DISPLAY_NAME_MAPPINGS as DUP_DISPLAY
    NODE_CLASS_MAPPINGS.update(DUP_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(DUP_DISPLAY)
    print("🐢 TORTU: Duplicate detection nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Failed to load duplicate detection nodes: {e}")

try:
    from .metadata.write_exif import NODE_CLASS_MAPPINGS as EXIF_NODES, NODE_DISPLAY_NAME_MAPPINGS as EXIF_DISPLAY
    NODE_CLASS_MAPPINGS.update(EXIF_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(EXIF_DISPLAY)
    print("🐢 TORTU: EXIF writer nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Failed to load EXIF writer nodes: {e}")

try:
    from .fileman.organize_images import NODE_CLASS_MAPPINGS as ORG_NODES, NODE_DISPLAY_NAME_MAPPINGS as ORG_DISPLAY
    NODE_CLASS_MAPPINGS.update(ORG_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(ORG_DISPLAY)
    print("🐢 TORTU: Image organizer nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Failed to load image organizer nodes: {e}")

# Load LoRa-specific nodes
try:
    from .lora.lora_conform import NODE_CLASS_MAPPINGS as CONFORM_NODES, NODE_DISPLAY_NAME_MAPPINGS as CONFORM_DISPLAY
    NODE_CLASS_MAPPINGS.update(CONFORM_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(CONFORM_DISPLAY)
    print("🐢 TORTU: LoRa conform nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Failed to load LoRa conform nodes: {e}")

try:
    from .lora.lora_define import NODE_CLASS_MAPPINGS as DEFINE_NODES, NODE_DISPLAY_NAME_MAPPINGS as DEFINE_DISPLAY
    NODE_CLASS_MAPPINGS.update(DEFINE_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(DEFINE_DISPLAY)
    print("🐢 TORTU: LoRa define nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Failed to load LoRa define nodes: {e}")

try:
    from .lora.lora_train import NODE_CLASS_MAPPINGS as TRAIN_NODES, NODE_DISPLAY_NAME_MAPPINGS as TRAIN_DISPLAY
    NODE_CLASS_MAPPINGS.update(TRAIN_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(TRAIN_DISPLAY)
    print("🐢 TORTU: LoRa train nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Failed to load LoRa train nodes: {e}")

try:
    from .lora.lora_metadata import NODE_CLASS_MAPPINGS as METADATA_NODES, NODE_DISPLAY_NAME_MAPPINGS as METADATA_DISPLAY
    NODE_CLASS_MAPPINGS.update(METADATA_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(METADATA_DISPLAY)
    print("🐢 TORTU: LoRa metadata nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Failed to load LoRa metadata nodes: {e}")


# Try to load legacy nodes for backwards compatibility
try:
    from .bc_metadata import NODE_CLASS_MAPPINGS as META_NODES, NODE_DISPLAY_NAME_MAPPINGS as META_DISPLAY
    NODE_CLASS_MAPPINGS.update(META_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(META_DISPLAY)
    print("🐢 TORTU: Legacy metadata nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Legacy metadata nodes not found: {e}")

try:
    from .bc_fileman import NODE_CLASS_MAPPINGS as FILEMAN_NODES, NODE_DISPLAY_NAME_MAPPINGS as FILEMAN_DISPLAY
    NODE_CLASS_MAPPINGS.update(FILEMAN_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(FILEMAN_DISPLAY)
    print("🐢 TORTU: Legacy file manager nodes loaded successfully")
except Exception as e:
    print(f"🐢 TORTU: Legacy file manager nodes not found: {e}")


total_nodes = len(NODE_CLASS_MAPPINGS)
print(f"🐢 TORTU: Total nodes loaded: {total_nodes}")

if total_nodes == 0:
    print("🐢 TORTU: No nodes loaded! Check the errors above.")
elif not deps_ok and total_nodes > 0:
    print("🐢 TORTU: Some nodes loaded, but detection features unavailable without MediaPipe.")
