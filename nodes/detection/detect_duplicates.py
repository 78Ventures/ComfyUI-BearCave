############################
# detect_duplicates.py
############################
# Detect duplicate images using perceptual hashing
############################

import numpy as np
import torch
from PIL import Image

try:
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    print("ImageHash not available. Duplicate detection will not work.")

class TORTU_DETECT_DUPLICATES:
    def __init__(self):
        # Store hashes in class to persist across calls
        self.seen_hashes = set()
        self.hash_to_filename = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_batch": ("IMAGE",),
            },
            "optional": {
                # Connection points from other nodes
                "filename": ("STRING", {"forceInput": True}),
                "relative_path": ("STRING", {"forceInput": True}),
                "source_directory": ("STRING", {"forceInput": True}),
                # Processing options
                "hash_size": ("INT", {"default": 8, "min": 4, "max": 32, "step": 4}),
                "hash_method": (["phash", "ahash", "dhash", "whash"], {"default": "phash"}),
                "similarity_threshold": ("INT", {"default": 5, "min": 0, "max": 20, "step": 1}),
                "reset_cache": ("BOOLEAN", {"default": False}),
                "skip_duplicates": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = (
        "IMAGE",     # Pass-through image (or empty if duplicate and skip enabled)
        "BOOLEAN",   # Is duplicate
        "STRING",    # Hash value
        "STRING",    # Similar image filename (if duplicate)
        "INT",       # Hash distance to most similar
        "STRING",    # Filename (pass-through)
        "STRING",    # Relative path (pass-through)
        "STRING",    # Detection status
        "INT",       # Total unique images seen
        "BOOLEAN",   # Should process (not duplicate or not skipping)
    )
    
    RETURN_NAMES = (
        "image_batch",
        "is_duplicate",
        "image_hash",
        "similar_filename",
        "hash_distance",
        "filename",
        "relative_path",
        "status",
        "unique_count",
        "should_process"
    )
    
    FUNCTION = "detect_duplicates"
    CATEGORY = "🐢 TORTU/Detection"

    def detect_duplicates(self, image_batch, **kwargs):
        # Extract optional inputs
        filename = kwargs.get('filename', '')
        relative_path = kwargs.get('relative_path', '')
        source_directory = kwargs.get('source_directory', '')
        hash_size = kwargs.get('hash_size', 8)
        hash_method = kwargs.get('hash_method', 'phash')
        similarity_threshold = kwargs.get('similarity_threshold', 5)
        reset_cache = kwargs.get('reset_cache', False)
        skip_duplicates = kwargs.get('skip_duplicates', True)
        
        if not IMAGEHASH_AVAILABLE:
            return (
                image_batch, False, "unavailable", "", 999, filename, relative_path,
                "imagehash_unavailable", 0, True
            )
        
        # Reset cache if requested
        if reset_cache:
            self.seen_hashes.clear()
            self.hash_to_filename.clear()
        
        try:
            # Convert ComfyUI tensor to PIL Image
            if isinstance(image_batch, torch.Tensor):
                img_np = image_batch[0].cpu().numpy()
            else:
                img_np = image_batch[0] if len(image_batch.shape) == 4 else image_batch
            
            # Convert from [0,1] to [0,255] and to uint8
            img_np = (img_np * 255).clip(0, 255).astype(np.uint8)
            img_pil = Image.fromarray(img_np, mode="RGB")
            
            # Calculate hash based on selected method
            hash_functions = {
                'phash': lambda img: imagehash.phash(img, hash_size=hash_size),
                'ahash': lambda img: imagehash.average_hash(img, hash_size=hash_size),
                'dhash': lambda img: imagehash.dhash(img, hash_size=hash_size),
                'whash': lambda img: imagehash.whash(img, hash_size=hash_size)
            }
            
            hash_func = hash_functions.get(hash_method, hash_functions['phash'])
            current_hash = hash_func(img_pil)
            hash_str = str(current_hash)
            
            # Check for duplicates/similar images
            is_duplicate = False
            min_distance = 999
            similar_filename = ""
            
            for seen_hash_str in self.seen_hashes:
                try:
                    seen_hash = imagehash.hex_to_hash(seen_hash_str)
                    distance = current_hash - seen_hash
                    
                    if distance <= similarity_threshold:
                        is_duplicate = True
                        if distance < min_distance:
                            min_distance = distance
                            similar_filename = self.hash_to_filename.get(seen_hash_str, "unknown")
                        
                        if distance == 0:
                            # Exact duplicate, no need to check further
                            break
                            
                except Exception as e:
                    # Skip malformed hashes
                    continue
            
            # Store this hash if it's not a duplicate
            if not is_duplicate:
                self.seen_hashes.add(hash_str)
                self.hash_to_filename[hash_str] = filename
            
            # Determine processing status
            should_process = not (is_duplicate and skip_duplicates)
            
            if is_duplicate:
                if min_distance == 0:
                    status = f"Exact duplicate of {similar_filename}"
                else:
                    status = f"Similar to {similar_filename} (distance: {min_distance})"
                if skip_duplicates:
                    status += " - SKIPPED"
            else:
                status = f"Unique image ({hash_method}:{hash_str[:8]}...)"
            
            # Return empty tensor if skipping duplicate
            output_image = image_batch
            if is_duplicate and skip_duplicates:
                # Create empty tensor with same shape but zero values
                empty_tensor = torch.zeros_like(image_batch)
                output_image = empty_tensor
            
            return (
                output_image,
                is_duplicate,
                hash_str,
                similar_filename,
                min_distance if is_duplicate else 0,
                filename,
                relative_path,
                status,
                len(self.seen_hashes),
                should_process
            )
            
        except Exception as e:
            print(f"🐢 TORTU: Error in duplicate detection: {e}")
            return (
                image_batch, False, "error", "", 999, filename, relative_path,
                f"Detection error: {str(e)}", len(self.seen_hashes), True
            )

    @classmethod
    def reset_hash_cache(cls):
        """Utility method to reset the hash cache globally"""
        # This would need to be called externally if you want to reset between different batches
        pass

NODE_CLASS_MAPPINGS = {
    "TORTU_DETECT_DUPLICATES": TORTU_DETECT_DUPLICATES
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TORTU_DETECT_DUPLICATES": "🐢 Detect Duplicates"
}