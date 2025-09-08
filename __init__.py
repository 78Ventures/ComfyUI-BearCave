# __init__.py 
# Bear Cave Nodes with Auto-Install
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
    from .bear_nodes_batch import NODE_CLASS_MAPPINGS as BATCH_NODES, NODE_DISPLAY_NAME_MAPPINGS as BATCH_DISPLAY
    NODE_CLASS_MAPPINGS.update(BATCH_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(BATCH_DISPLAY)
    print("🐻 Bear Cave: Batch nodes loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave: Failed to load batch nodes: {e}")

try:
    from .bear_nodes_image import NODE_CLASS_MAPPINGS as IMAGE_NODES, NODE_DISPLAY_NAME_MAPPINGS as IMAGE_DISPLAY
    NODE_CLASS_MAPPINGS.update(IMAGE_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(IMAGE_DISPLAY)
    print("🐻 Bear Cave: Image nodes loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave: Failed to load image nodes: {e}")

try:
    from .bear_nodes_exif import NODE_CLASS_MAPPINGS as EXIF_NODES, NODE_DISPLAY_NAME_MAPPINGS as EXIF_DISPLAY
    NODE_CLASS_MAPPINGS.update(EXIF_NODES)
    NODE_DISPLAY_NAME_MAPPINGS.update(EXIF_DISPLAY)
    print("🐻 Bear Cave: EXIF nodes loaded successfully")
except Exception as e:
    print(f"🐻 Bear Cave: Failed to load EXIF nodes: {e}")

# Detection nodes load last (since they need MediaPipe)
if deps_ok:
    try:
        from .bear_nodes_detection import NODE_CLASS_MAPPINGS as DETECTION_NODES, NODE_DISPLAY_NAME_MAPPINGS as DETECTION_DISPLAY
        NODE_CLASS_MAPPINGS.update(DETECTION_NODES)
        NODE_DISPLAY_NAME_MAPPINGS.update(DETECTION_DISPLAY)
        print("🐻 Bear Cave: Detection nodes loaded successfully")
    except Exception as e:
        print(f"🐻 Bear Cave: Failed to load detection nodes: {e}")
else:
    print("🐻 Bear Cave: Skipping detection nodes due to missing dependencies")

total_nodes = len(NODE_CLASS_MAPPINGS)
print(f"🐻 Bear Cave: Total nodes loaded: {total_nodes}")

if total_nodes == 0:
    print("🐻 Bear Cave: No nodes loaded! Check the errors above.")
elif not deps_ok and total_nodes > 0:
    print("🐻 Bear Cave: Some nodes loaded, but detection features unavailable without MediaPipe.")