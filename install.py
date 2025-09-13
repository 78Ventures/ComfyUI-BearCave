# install.py
# Pinokio-compatible auto-installer for TORTU nodes
############################
import subprocess
import sys
import os
import importlib.util
from pathlib import Path
import platform

def find_pinokio_python():
    """Find Python executable in Pinokio environment"""
    current_dir = Path.cwd()
    
    # Common Pinokio Python locations
    potential_paths = [
        sys.executable,  # Current running Python (most reliable)
        current_dir / "bin" / "python",
        current_dir / "bin" / "python3",
        current_dir / "Scripts" / "python.exe",  # Windows
        current_dir.parent / "bin" / "python",
        current_dir.parent / "bin" / "python3",
        # Pinokio-specific paths
        Path.home() / "pinokio" / "bin" / "python",
        Path.home() / "pinokio" / "api" / "comfy.git" / "bin" / "python",
        # Look for conda/mamba in Pinokio
        current_dir / "conda" / "bin" / "python",
        current_dir / "miniconda" / "bin" / "python",
    ]
    
    for python_path in potential_paths:
        if Path(python_path).exists() and Path(python_path).is_file():
            try:
                # Test if this Python can actually run
                result = subprocess.run([str(python_path), "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return str(python_path)
            except:
                continue
    
    return sys.executable  # Fallback

def is_package_installed(package_name, python_exe=None):
    """Check if package is installed"""
    if python_exe is None:
        python_exe = sys.executable
        
    try:
        result = subprocess.run([python_exe, "-c", f"import {package_name}"], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def install_package_with_fallback(package, python_exe):
    """Try multiple installation methods for Pinokio compatibility"""
    install_methods = [
        # Method 1: Standard pip
        [python_exe, "-m", "pip", "install", package],
        # Method 2: User install (if permissions issue)
        [python_exe, "-m", "pip", "install", "--user", package],
        # Method 3: Force reinstall
        [python_exe, "-m", "pip", "install", "--force-reinstall", package],
        # Method 4: No cache (for network issues)
        [python_exe, "-m", "pip", "install", "--no-cache-dir", package],
    ]
    
    for i, cmd in enumerate(install_methods, 1):
        try:
            print(f"  Attempt {i}: {' '.join(cmd[2:])}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"  ✓ Success with method {i}")
                return True
            else:
                print(f"  ✗ Method {i} failed: {result.stderr[:100]}...")
                
        except subprocess.TimeoutExpired:
            print(f"  ✗ Method {i} timed out")
        except Exception as e:
            print(f"  ✗ Method {i} error: {str(e)[:50]}...")
    
    return False

def get_system_info():
    """Get system information for debugging"""
    return {
        'platform': platform.system(),
        'machine': platform.machine(), 
        'python_version': sys.version,
        'executable': sys.executable,
        'cwd': os.getcwd()
    }

def install_requirements():
    """Smart installer for Pinokio environments"""
    print("🐢 TORTU Nodes - Pinokio Environment Installer")
    print("=" * 65)
    
    # System info
    info = get_system_info()
    print(f"Platform: {info['platform']} {info['machine']}")
    print(f"Current directory: {info['cwd']}")
    print(f"Running Python: {info['executable']}")
    
    # Find the best Python
    python_exe = find_pinokio_python()
    print(f"Target Python: {python_exe}")
    
    # Check if we can run pip
    try:
        pip_check = subprocess.run([python_exe, "-m", "pip", "--version"], 
                                 capture_output=True, text=True, timeout=10)
        if pip_check.returncode != 0:
            print("⚠️  Warning: pip not working with this Python")
            python_exe = sys.executable  # Fallback to current
    except:
        print("⚠️  Warning: Cannot test pip, using current Python")
        python_exe = sys.executable
    
    print("\n" + "-" * 50)
    
    # Dependencies to install
    requirements = [
        ("mediapipe", "mediapipe>=0.10.0"),
        ("cv2", "opencv-python>=4.5.0")
    ]
    
    success_count = 0
    
    for import_name, package_spec in requirements:
        print(f"\nChecking {import_name}...")
        
        if is_package_installed(import_name, python_exe):
            print(f"✓ {import_name} already installed")
            success_count += 1
            continue
        
        print(f"Installing {package_spec}...")
        if install_package_with_fallback(package_spec, python_exe):
            # Verify installation
            if is_package_installed(import_name, python_exe):
                print(f"✓ {import_name} installed and verified")
                success_count += 1
            else:
                print(f"✗ {import_name} installation failed verification")
        else:
            print(f"✗ Failed to install {package_spec}")
    
    print("\n" + "=" * 65)
    
    if success_count == len(requirements):
        print("🎉 All dependencies installed successfully!")
        print("Restart ComfyUI in Pinokio to use TORTU nodes.")
    elif success_count > 0:
        print(f"⚠️  Partial success: {success_count}/{len(requirements)} dependencies installed")
        print("Some TORTU nodes may not work properly.")
    else:
        print("❌ Installation failed. Manual steps:")
        print(f"1. Open terminal in Pinokio")
        print(f"2. Try: {python_exe} -m pip install mediapipe opencv-python")
        print("3. Or contact TORTU support with the above system info")
    
    return success_count == len(requirements)

# Auto-run when ComfyUI loads (if dependencies missing)
def auto_install_check():
    """Automatically check and install dependencies when module loads"""
    try:
        import mediapipe
        import cv2
        return True  # All good
    except ImportError:
        print("🐢 TORTU: Missing dependencies detected, attempting auto-install...")
        return install_requirements()

if __name__ == "__main__":
    install_requirements()
else:
    # This runs when the module is imported by ComfyUI
    # Uncomment the next line if you want auto-install on import
    # auto_install_check()
    pass