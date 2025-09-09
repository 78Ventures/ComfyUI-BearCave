###################################
# bc_fileman.py
###################################
# File management utilities
###################################

# CREDITS
###################################
# IF_Load_Images_Node.py is an original work by Impact Frames (https://github.com/if-ai).
# Special thanks to Impact Frames for their contributions to the ComfyUI ecosystem.

# LOAD LIBRARIES
###################################
import os
import re
import torch
import glob
import hashlib
import logging
import numpy as np
from PIL import Image, ImageOps, ImageSequence
import folder_paths
import shutil
from typing import Tuple, List, Dict, Optional
from pathlib import Path

# UTILITIES
###################################
logger = logging.getLogger(__name__)

def numerical_sort_key(path):
    parts = re.split('([0-9]+)', os.path.basename(path))
    parts[1::2] = map(int, parts[1::2])
    return parts

# LOAD IMAGES
###################################
# Wrapper node for IF_Load_Images_Node.py from Impact Frames
###################################
try:
    from nodes.bc_fileman.IF_Load_Images_Node import IFLoadImagess
    _delegate_class = IFLoadImagess
except ImportError:
    # Fallback: try common variations in case upstream changes
    try:
        from nodes.bc_fileman.IF_Load_Images_Node import IF_LoadImagess
        _delegate_class = IF_LoadImagess
    except ImportError:
        try:
            from nodes.bc_fileman.IF_Load_Images_Node import IFLoadImages
            _delegate_class = IFLoadImages
        except ImportError:
            # Create a stub class if all imports fail
            class _StubLoadImages:
                @classmethod
                def INPUT_TYPES(cls):
                    return {"required": {"error": ("STRING", {"default": "IF_Load_Images_Node not available"})}}
                RETURN_TYPES = ("STRING",)
                RETURN_NAMES = ("error",)
                OUTPUT_IS_LIST = (False,)
                FUNCTION = "error"
                CATEGORY = "🐻 Bear Cave/Error"
                @classmethod
                def IS_CHANGED(cls, *args, **kwargs):
                    return float("NaN")
                def error(self, *args, **kwargs):
                    return ("IF_Load_Images_Node class not found. Please check the import.",)
            _delegate_class = _StubLoadImages

class BC_LOAD_IMAGES:
    def __init__(self):
        if hasattr(_delegate_class, '__init__'):
            self._delegate = _delegate_class()
        else:
            self._delegate = _delegate_class

    @classmethod
    def INPUT_TYPES(cls):
        return _delegate_class.INPUT_TYPES()

    RETURN_TYPES = _delegate_class.RETURN_TYPES
    RETURN_NAMES = _delegate_class.RETURN_NAMES
    OUTPUT_IS_LIST = _delegate_class.OUTPUT_IS_LIST
    FUNCTION = _delegate_class.FUNCTION
    CATEGORY = "🐻 Bear Cave/Images"  # Override category

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return _delegate_class.IS_CHANGED(*args, **kwargs)

    def load_images(self, *args, **kwargs):
        return self._delegate.load_images(*args, **kwargs)

# SAVE IMAGES
###################################
# Comprehensive batch image saver with extensive connection points
###################################
from nodes.bc_fileman.IF_Load_Images_Node import ImageManager

class BC_SAVE_IMAGES:
    def __init__(self):
        pass
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "output_path": ("STRING", {"default": ""}),
                "file_prefix": ("STRING", {"default": "image"}),
                "filename_text": ("STRING", {"default": ""}),
                "file_format": (["png", "jpg", "webp"],),
                "quality": ("INT", {"default": 100, "min": 1, "max": 100}),
                "sort_method": (["alphabetical", "numerical", "date_created", "date_modified"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "save_images"
    CATEGORY = "🐻 Bear Cave/Images"

    def save_images(self, images, output_path="", file_prefix="image", filename_text="", file_format="png", quality=100, sort_method="numerical"):
        saved_paths = []
        
        try:
            # Use ImageManager to normalize and validate the output path
            output_path = ImageManager.normalize_path(output_path)
            if not os.path.isabs(output_path):
                output_path = os.path.abspath(os.path.join(folder_paths.get_output_directory(), output_path))

            # Create output directory if it doesn't exist
            os.makedirs(output_path, exist_ok=True)

            # Generate filenames using ImageManager's sanitize method
            base_filename = ImageManager.sanitize_path_component(file_prefix)
            if filename_text:
                base_filename += "_" + ImageManager.sanitize_path_component(filename_text)

            # Save each image
            for idx, image in enumerate(images):
                # Convert image tensor to PIL Image
                image_array = 255. * image.cpu().numpy()
                img = Image.fromarray(np.clip(image_array, 0, 255).astype(np.uint8))
                
                # Generate filename
                filename = f"{base_filename}_{idx:05d}.{file_format}"
                filepath = os.path.join(output_path, filename)
                
                # Save with appropriate format and quality
                if file_format == "png":
                    img.save(filepath, "PNG")
                elif file_format == "jpg":
                    img.save(filepath, "JPEG", quality=quality)
                elif file_format == "webp":
                    img.save(filepath, "WEBP", quality=quality)
                
                saved_paths.append(filepath)

            # Sort the saved paths using ImageManager's sort method
            saved_paths = ImageManager.sort_files(saved_paths, sort_method)
            
            return (saved_paths,)

        except Exception as e:
            logger.error(f"Error saving images: {str(e)}")
            return ([str(e)],)

# NODE MAPPINGS
###################################
NODE_CLASS_MAPPINGS = {
    "BC_LOAD_IMAGES": BC_LOAD_IMAGES,
    "BC_SAVE_IMAGES": BC_SAVE_IMAGES,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BC_LOAD_IMAGES": "🐻 Load Images",
    "BC_SAVE_IMAGES": "🐻 Save Images",
}