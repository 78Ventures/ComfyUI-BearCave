# __init__.py 
# ComfyUI-BearCave
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
    
    if missing_deps:
        print(f"🐻 Bear Cave: Missing dependencies: {', '.join(missing_deps)}")
        print("🐻 Bear Cave: Attempting automatic installation...")
        
        try:
            from . import install
            if hasattr(install, 'install_requirements'):
                success = install.install_requirements()
                if success:
                    print("🐻 Bear Cave: Dependencies installed! Please restart ComfyUI.")
                else:
                    print("🐻 Bear Cave: Auto-install failed. Please install manually:")
                    print("   - mediapipe>=0.10.0")
                    print("   - opencv-python>=4.5.0")
            return len(missing_deps) == 0
        except Exception as e:
            print(f"🐻 Bear Cave: Auto-install error: {e}")
            print("🐻 Bear Cave: Please install dependencies manually.")
            return False
    
    return True

# Check dependencies first
deps_ok = check_and_install_dependencies()

# Try to import each module individually to avoid total failure
try:
    from .bc_face_detection import NODE_CLASS_MAPPINGS as FACE_NODES, NODE_DISPLAY_NAME_MAPPINGS as FACE_DISPLAY
    NODE_CLASS_MAPPINGS.update(FACE_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(FACE_DISPLAY)
    print("🐻 Bear Cave: Face detection nodes loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave: Failed to load face detection nodes: {e}")

try:
    from .bc_metadata import NODE_CLASS_MAPPINGS as META_NODES, NODE_DISPLAY_NAME_MAPPINGS as META_DISPLAY
    NODE_CLASS_MAPPINGS.update(META_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(META_DISPLAY)
    print("🐻 Bear Cave: Metadata nodes loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave: Failed to load metadata nodes: {e}")

try:
    from .bc_fileman import NODE_CLASS_MAPPINGS as FILEMAN_NODES, NODE_DISPLAY_NAME_MAPPINGS as FILEMAN_DISPLAY
    NODE_CLASS_MAPPINGS.update(FILEMAN_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(FILEMAN_DISPLAY)
    print("🐻 Bear Cave: File manager nodes loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave: Failed to load file manager nodes: {e}")

# Load LoRa-specific nodes
try:
    from .bc_lora import NODE_CLASS_MAPPINGS as LORA_NODES, NODE_DISPLAY_NAME_MAPPINGS as LORA_DISPLAY
    NODE_CLASS_MAPPINGS.update(LORA_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(LORA_DISPLAY)
    print("🐻 Bear Cave: LoRa nodes loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave: Failed to load LoRa nodes: {e}")


total_nodes = len(NODE_CLASS_MAPPINGS)
print(f"🐻 Bear Cave: Total nodes loaded: {total_nodes}")

if total_nodes == 0:
    print("🐻 Bear Cave: No nodes loaded! Check the errors above.")
elif not deps_ok and total_nodes > 0:
    print("🐻 Bear Cave: Some nodes loaded, but detection features unavailable without MediaPipe.")
