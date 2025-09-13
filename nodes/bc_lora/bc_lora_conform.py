############################
# bc_lora_conform.py
############################
# FCrop and resize images to conform to LoRA training requirements
############################
import numpy as np
import torch
from PIL import Image

class BC_IMAGE_LORA_CONFORM:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_batch": ("IMAGE",),
                "size": ("INT", {"default": 1024, "min": 64, "max": 4096, "step": 64}),
                "resize_method": (["LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"], {"default": "LANCZOS"}),
                "crop_method": (["center", "smart", "face_center", "top", "bottom"], {"default": "center"}),
            },
            "optional": {
                # Connection points from other nodes
                "filename": ("STRING", {"forceInput": True}),
                "relative_path": ("STRING", {"forceInput": True}),
                "source_directory": ("STRING", {"forceInput": True}),
                "face_center_x": ("FLOAT", {"forceInput": True}),
                "face_center_y": ("FLOAT", {"forceInput": True}),
                "face_width": ("FLOAT", {"forceInput": True}),
                "face_height": ("FLOAT", {"forceInput": True}),
                "face_pose": ("STRING", {"forceInput": True}),
                "detection_confidence": ("FLOAT", {"forceInput": True}),
                "face_detected": ("BOOLEAN", {"forceInput": True}),
                # Additional processing options
                "maintain_aspect": ("BOOLEAN", {"default": False}),
                "padding_color": (["black", "white", "transparent", "blur"], {"default": "black"}),
                "upscale_threshold": ("FLOAT", {"default": 1.5, "min": 1.0, "max": 4.0, "step": 0.1}),
                "quality_enhancement": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = (
        "IMAGE",     # Processed image
        "STRING",    # Crop coordinates (JSON)
        "FLOAT",     # Detection confidence (pass-through)
        "BOOLEAN",   # Face detected (pass-through)
        "STRING",    # Face pose (pass-through)
        "STRING",    # Filename (pass-through)
        "INT",       # Final height
        "STRING",    # Processing method used
        "STRING",    # Processing log
        "STRING",    # Relative path (pass-through)
        "FLOAT",     # Scale factor applied
        "BOOLEAN",   # Was cropped
        "BOOLEAN",   # Was upscaled
        "INT",       # Final width
    )
    
    RETURN_NAMES = (
        "image_batch",
        "crop_info",
        "detection_confidence",
        "face_detected",
        "face_pose",
        "filename",
        "height",
        "method_used",
        "process_log",
        "relative_path",
        "scale_factor",
        "was_cropped",
        "was_upscaled",
        "width"
    )
    
    FUNCTION = "crop_and_resize"
    CATEGORY = "🐢 TORTU/LoRa"

    def crop_and_resize(self, image_batch, size, resize_method, crop_method, **kwargs):
        import json
        
        # Extract optional inputs
        filename = kwargs.get('filename', '')
        relative_path = kwargs.get('relative_path', '')
        source_directory = kwargs.get('source_directory', '')
        face_center_x = kwargs.get('face_center_x', 0.5)
        face_center_y = kwargs.get('face_center_y', 0.5)
        face_width = kwargs.get('face_width', 0.0)
        face_height = kwargs.get('face_height', 0.0)
        face_pose = kwargs.get('face_pose', '')
        detection_confidence = kwargs.get('detection_confidence', 0.0)
        face_detected = kwargs.get('face_detected', False)
        maintain_aspect = kwargs.get('maintain_aspect', False)
        padding_color = kwargs.get('padding_color', 'black')
        upscale_threshold = kwargs.get('upscale_threshold', 1.5)
        quality_enhancement = kwargs.get('quality_enhancement', True)
        
        try:
            # Convert ComfyUI tensor to PIL
            if isinstance(image_batch, torch.Tensor):
                img_np = image_batch[0].cpu().numpy()
            else:
                img_np = image_batch[0] if len(image_batch.shape) == 4 else image_batch
            
            img_np = (img_np * 255).clip(0, 255).astype(np.uint8)
            img_pil = Image.fromarray(img_np, mode="RGB")
            
            original_size = img_pil.size
            original_width, original_height = original_size
            
            # Initialize processing log
            process_log = []
            process_log.append(f"Original size: {original_width}x{original_height}")
            
            # Add face detection info to processing log
            if face_detected and face_pose:
                process_log.append(f"Face detected: {face_pose} (confidence: {detection_confidence:.2f})")
                process_log.append(f"Face bounds: center({face_center_x:.3f}, {face_center_y:.3f}) size({face_width:.3f}, {face_height:.3f})")
            elif face_pose:
                process_log.append(f"Face pose data: {face_pose}")
            else:
                process_log.append("No face detection data provided")
            
            # Determine if we need to upscale
            scale_factor = size / max(original_width, original_height)
            was_upscaled = scale_factor > upscale_threshold
            was_cropped = False
            crop_info = {"method": crop_method, "applied": False}
            
            if was_upscaled and quality_enhancement:
                # Use higher quality resampling for upscaling
                actual_resize_method = Image.LANCZOS
                process_log.append(f"Upscaling detected (factor: {scale_factor:.2f}), using LANCZOS")
            else:
                # Map resize method string to PIL constant
                resize_methods = {
                    "LANCZOS": Image.LANCZOS,
                    "BICUBIC": Image.BICUBIC, 
                    "BILINEAR": Image.BILINEAR,
                    "NEAREST": Image.NEAREST
                }
                actual_resize_method = resize_methods.get(resize_method, Image.LANCZOS)
                process_log.append(f"Using resize method: {resize_method}")
            
            # Handle different crop methods
            if crop_method == "smart" or (crop_method == "face_center" and face_width > 0):
                # Smart crop or face-centered crop
                img_processed, crop_details = self._smart_crop(
                    img_pil, size, face_center_x, face_center_y, 
                    face_width, face_height, crop_method == "face_center"
                )
                was_cropped = True
                crop_info.update(crop_details)
                crop_info["applied"] = True
                process_log.append(f"Applied {crop_method} crop")
                
            elif maintain_aspect:
                # Resize maintaining aspect ratio with padding
                img_processed = self._resize_with_padding(
                    img_pil, size, padding_color, actual_resize_method
                )
                process_log.append(f"Resized with aspect ratio maintained, padding: {padding_color}")
                
            else:
                # Standard crop methods
                if crop_method in ["top", "bottom", "center"]:
                    img_cropped = self._crop_by_method(img_pil, crop_method)
                    was_cropped = True
                    crop_info["applied"] = True
                    crop_info["method"] = crop_method
                    process_log.append(f"Applied {crop_method} crop before resize")
                else:
                    img_cropped = img_pil
                    
                # Resize to target size
                img_processed = img_cropped.resize((size, size), actual_resize_method)
            
            final_size = img_processed.size
            process_log.append(f"Final size: {final_size[0]}x{final_size[1]}")
            
            # Convert back to ComfyUI tensor
            img_np_final = np.array(img_processed).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_np_final).unsqueeze(0)
            
            # Create processing summary
            method_used = f"{crop_method}_{resize_method}"
            if maintain_aspect:
                method_used += "_aspect_maintained"
            if was_upscaled and quality_enhancement:
                method_used += "_quality_enhanced"
                
            process_log_str = "; ".join(process_log)
            
            return (
                img_tensor, filename, relative_path,
                final_size[0], final_size[1], scale_factor, method_used,
                was_upscaled, was_cropped, json.dumps(crop_info),
                process_log_str, face_pose, detection_confidence, face_detected
            )
            
        except Exception as e:
            print(f"🐢 TORTU: Error in BearImageLoRAConform: {e}")
            return (
                image_batch, filename, relative_path,
                0, 0, 1.0, "error", False, False, '{"error": true}',
                f"Processing failed: {str(e)}", face_pose, detection_confidence, face_detected
            )

    def _smart_crop(self, img, target_size, face_x, face_y, face_w, face_h, use_face_center):
        """Perform smart cropping based on face detection or content analysis"""
        width, height = img.size
        
        if use_face_center and face_w > 0 and face_h > 0:
            # Use face center for cropping
            center_x = int(face_x * width)
            center_y = int(face_y * height)
        else:
            # Default to image center
            center_x = width // 2
            center_y = height // 2
        
        # Calculate crop box for square crop
        crop_size = min(width, height)
        half_crop = crop_size // 2
        
        # Adjust center point to keep crop within image bounds
        left = max(0, min(center_x - half_crop, width - crop_size))
        top = max(0, min(center_y - half_crop, height - crop_size))
        right = left + crop_size
        bottom = top + crop_size
        
        cropped_img = img.crop((left, top, right, bottom))
        resized_img = cropped_img.resize((target_size, target_size), Image.LANCZOS)
        
        crop_details = {
            "left": left, "top": top, "right": right, "bottom": bottom,
            "center_x": center_x, "center_y": center_y,
            "crop_size": crop_size, "face_guided": use_face_center and face_w > 0
        }
        
        return resized_img, crop_details

    def _crop_by_method(self, img, method):
        """Apply specific crop method"""
        width, height = img.size
        crop_size = min(width, height)
        
        if method == "center":
            left = (width - crop_size) // 2
            top = (height - crop_size) // 2
        elif method == "top":
            left = (width - crop_size) // 2
            top = 0
        elif method == "bottom":
            left = (width - crop_size) // 2
            top = height - crop_size
        else:
            # Default to center
            left = (width - crop_size) // 2
            top = (height - crop_size) // 2
        
        return img.crop((left, top, left + crop_size, top + crop_size))

    def _resize_with_padding(self, img, target_size, padding_color, resize_method):
        """Resize image maintaining aspect ratio with padding"""
        width, height = img.size
        ratio = min(target_size / width, target_size / height)
        
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Resize image
        img_resized = img.resize((new_width, new_height), resize_method)
        
        # Create new image with padding
        if padding_color == "transparent":
            new_img = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
            img_resized = img_resized.convert("RGBA")
        else:
            color_map = {
                "black": (0, 0, 0),
                "white": (255, 255, 255),
                "blur": None  # Special case
            }
            
            if padding_color == "blur":
                # Create blurred background
                bg = img.resize((target_size, target_size), Image.LANCZOS)
                bg = bg.filter(Image.BLUR)
                new_img = bg
            else:
                new_img = Image.new("RGB", (target_size, target_size), color_map[padding_color])
        
        # Paste resized image in center
        paste_x = (target_size - new_width) // 2
        paste_y = (target_size - new_height) // 2
        new_img.paste(img_resized, (paste_x, paste_y))
        
        return new_img.convert("RGB")

# Required for ComfyUI to register this node
NODE_CLASS_MAPPINGS = {
    "BC_IMAGE_LORA_CONFORM": BC_IMAGE_LORA_CONFORM
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BC_IMAGE_LORA_CONFORM": "🐢 Conform for LoRA"
}
