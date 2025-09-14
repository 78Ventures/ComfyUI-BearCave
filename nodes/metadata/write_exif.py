############################
# write_exif.py
############################
# Write EXIF metadata to images for LoRA training
############################

import numpy as np
import torch
from PIL import Image
import tempfile
import os

try:
    import piexif
    PIEXIF_AVAILABLE = True
except ImportError:
    PIEXIF_AVAILABLE = False
    print("piexif not available. EXIF metadata writing will not work.")

class TORTU_WRITE_EXIF:
    def __init__(self):
        self.temp_files = []

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_batch": ("IMAGE",),
                "output_path": ("STRING", {"default": ""}),
            },
            "optional": {
                # Connection points from other nodes
                "filename": ("STRING", {"forceInput": True}),
                "relative_path": ("STRING", {"forceInput": True}),
                "source_directory": ("STRING", {"forceInput": True}),
                "primary_emotion": ("STRING", {"forceInput": True}),
                "face_pose": ("STRING", {"forceInput": True}),
                "detection_confidence": ("FLOAT", {"forceInput": True}),
                "face_detected": ("BOOLEAN", {"forceInput": True}),
                # Metadata fields
                "subject": ("STRING", {"default": "subject"}),
                "pose": ("STRING", {"default": "POSE"}),
                "note": ("STRING", {"default": "NOTE"}),
                "quality": ("INT", {"default": 95, "min": 60, "max": 100, "step": 5}),
                "format": (["JPEG", "PNG"], {"default": "JPEG"}),
                "overwrite_existing": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = (
        "IMAGE",     # Pass-through image
        "STRING",    # Output file path
        "STRING",    # EXIF comment written
        "BOOLEAN",   # Write successful
        "STRING",    # Status message
        "STRING",    # Filename (pass-through)
        "STRING",    # Relative path (pass-through)
        "INT",       # File size (bytes)
    )
    
    RETURN_NAMES = (
        "image_batch",
        "output_path",
        "exif_comment",
        "write_success",
        "status",
        "filename",
        "relative_path",
        "file_size"
    )
    
    FUNCTION = "write_exif"
    CATEGORY = "🐢 TORTU/Metadata"

    def write_exif(self, image_batch, output_path, **kwargs):
        # Extract optional inputs
        filename = kwargs.get('filename', 'image')
        relative_path = kwargs.get('relative_path', '')
        source_directory = kwargs.get('source_directory', '')
        primary_emotion = kwargs.get('primary_emotion', '')
        face_pose = kwargs.get('face_pose', '')
        detection_confidence = kwargs.get('detection_confidence', 0.0)
        face_detected = kwargs.get('face_detected', False)
        
        subject = kwargs.get('subject', 'subject')
        pose = kwargs.get('pose', 'POSE')
        note = kwargs.get('note', 'NOTE')
        quality = kwargs.get('quality', 95)
        format_type = kwargs.get('format', 'JPEG')
        overwrite_existing = kwargs.get('overwrite_existing', False)
        
        if not PIEXIF_AVAILABLE:
            return (
                image_batch, "", "", False, "piexif_unavailable",
                filename, relative_path, 0
            )
        
        if not output_path.strip():
            return (
                image_batch, "", "", False, "No output path provided",
                filename, relative_path, 0
            )
        
        try:
            # Convert ComfyUI tensor to PIL Image
            if isinstance(image_batch, torch.Tensor):
                img_np = image_batch[0].cpu().numpy()
            else:
                img_np = image_batch[0] if len(image_batch.shape) == 4 else image_batch
            
            # Convert from [0,1] to [0,255] and to uint8
            img_np = (img_np * 255).clip(0, 255).astype(np.uint8)
            img_pil = Image.fromarray(img_np, mode="RGB")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Check if file exists and handle overwrite
            if os.path.exists(output_path) and not overwrite_existing:
                return (
                    image_batch, output_path, "", False, 
                    f"File exists and overwrite disabled: {output_path}",
                    filename, relative_path, 0
                )
            
            # Replace placeholders in metadata fields
            actual_emotion = primary_emotion if primary_emotion and primary_emotion != 'error' else 'unknown'
            actual_pose = face_pose if face_pose and face_pose not in ['error', 'unknown'] else pose
            
            # Create EXIF comment string matching LoRA_Prep.py format
            comment_str = f"Subject={subject};Expression={actual_emotion};Pose={actual_pose};Note={note}"
            
            # Create EXIF dictionary
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            
            # Encode comment as UTF-16LE with Unicode prefix (matching original)
            encoded_comment = b'\\x55\\x00\\x4e\\x00\\x49\\x00\\x43\\x00\\x4f\\x00\\x44\\x00\\x45\\x00\\x00\\x00'
            encoded_comment += comment_str.encode('utf-16le')
            
            # Add user comment to EXIF
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = encoded_comment
            
            # Add additional metadata
            if face_detected and detection_confidence > 0:
                # Add detection confidence as a string in ImageDescription
                description = f"Face detection confidence: {detection_confidence:.3f}"
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = description.encode('utf-8')
            
            # Add software tag
            exif_dict["0th"][piexif.ImageIFD.Software] = "ComfyUI-TORTU".encode('utf-8')
            
            # Generate EXIF bytes
            exif_bytes = piexif.dump(exif_dict)
            
            # Save image with metadata
            save_kwargs = {"exif": exif_bytes}
            if format_type.upper() == "JPEG":
                save_kwargs["quality"] = quality
                img_pil.save(output_path, "JPEG", **save_kwargs)
            else:
                # PNG doesn't support EXIF in PIL, save as metadata
                pnginfo = Image.new('RGB', (1,1)).info
                pnginfo['exif_comment'] = comment_str
                img_pil.save(output_path, "PNG", pnginfo=pnginfo)
            
            # Get file size
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            
            status = f"Saved {format_type} with metadata: {os.path.basename(output_path)}"
            
            return (
                image_batch,
                output_path,
                comment_str,
                True,
                status,
                filename,
                relative_path,
                file_size
            )
            
        except Exception as e:
            print(f"🐢 TORTU: Error writing metadata: {e}")
            return (
                image_batch, output_path, "", False, 
                f"Write error: {str(e)}", filename, relative_path, 0
            )

    def __del__(self):
        # Cleanup temp files on destruction
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass

NODE_CLASS_MAPPINGS = {
    "TORTU_WRITE_EXIF": TORTU_WRITE_EXIF
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TORTU_WRITE_EXIF": "🐢 Write EXIF"
}