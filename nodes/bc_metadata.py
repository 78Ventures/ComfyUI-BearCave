# bc_metadata.py
############################
# Manage metadata (e.g. EXIF) when processing and saving images
###################################
import os
import torch
import numpy as np
from PIL import Image, PngImagePlugin
from pathlib import Path
import folder_paths

class BC_EXIF_WRITER:
    def __init__(self):
        self.image_counter = {}

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "expression": ("STRING", {"default": "neutral"}),
                "pose": ("STRING", {"default": "center"}),
                "note": ("STRING", {"default": "NOTE"}),
                "subject": ("STRING", {"default": "subject"}),
                "output_dir": ("STRING", {"default": "output"}),
            },
            "optional": {
                # Connection points from batch operations
                "filename": ("STRING", {"forceInput": True}),
                "relative_path": ("STRING", {"forceInput": True}),
                "source_directory": ("STRING", {"forceInput": True}),
                "full_path": ("STRING", {"forceInput": True}),
                "width": ("INT", {"forceInput": True}),
                "height": ("INT", {"forceInput": True}),
                "file_size": ("INT", {"forceInput": True}),
                "creation_date": ("STRING", {"forceInput": True}),
                "face_pose": ("STRING", {"forceInput": True}),  # From detection
                # Additional metadata
                "age": ("STRING", {"default": ""}),
                "gender": ("STRING", {"default": ""}),
                "ethnicity": ("STRING", {"default": ""}),
                "lighting": ("STRING", {"default": ""}),
                "background": ("STRING", {"default": ""}),
                "camera_angle": ("STRING", {"default": ""}),
                "quality_rating": ("INT", {"default": 0, "min": 0, "max": 10}),
                "tags": ("STRING", {"default": ""}),
                "dataset_name": ("STRING", {"default": ""}),
                "training_weight": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = (
        "STRING",    # File path
        "STRING",    # Filename
        "STRING",    # Metadata JSON
        "STRING",    # Tags list
        "STRING",    # Full metadata string
        "BOOLEAN",   # Save successful
        "INT",       # File size
        "STRING",    # Save timestamp
    )
    
    RETURN_NAMES = (
        "file_path",
        "filename", 
        "metadata_json",
        "tags",
        "full_metadata",
        "save_successful",
        "file_size",
        "save_timestamp"
    )
    
    FUNCTION = "write"
    CATEGORY = "🐻 Bear Cave/EXIF"
    OUTPUT_NODE = True

    def write(self, image, expression, pose, note, subject, output_dir, **kwargs):
        import json
        from datetime import datetime
        
        # Extract optional connected inputs
        filename = kwargs.get('filename', '')
        relative_path = kwargs.get('relative_path', '')
        source_directory = kwargs.get('source_directory', '')
        full_path = kwargs.get('full_path', '')
        width = kwargs.get('width', 0)
        height = kwargs.get('height', 0)
        file_size = kwargs.get('file_size', 0)
        creation_date = kwargs.get('creation_date', '')
        face_pose = kwargs.get('face_pose', pose)  # Use detected pose if available
        
        # Additional metadata
        age = kwargs.get('age', '')
        gender = kwargs.get('gender', '')
        ethnicity = kwargs.get('ethnicity', '')
        lighting = kwargs.get('lighting', '')
        background = kwargs.get('background', '')
        camera_angle = kwargs.get('camera_angle', '')
        quality_rating = kwargs.get('quality_rating', 0)
        tags = kwargs.get('tags', '')
        dataset_name = kwargs.get('dataset_name', '')
        training_weight = kwargs.get('training_weight', 1.0)
        
        try:
            # Convert ComfyUI tensor to PIL Image
            if isinstance(image, torch.Tensor):
                img_np = image[0].cpu().numpy()
            else:
                img_np = image[0] if len(image.shape) == 4 else image
            
            img_np = (img_np * 255).clip(0, 255).astype(np.uint8)
            pil_img = Image.fromarray(img_np, mode="RGB")

            # Use provided filename or generate one
            if filename:
                base_filename = filename
            else:
                # Generate filename
                key = f"{output_dir}/{expression}"
                count = self.image_counter.get(key, 0)
                self.image_counter[key] = count + 1
                index = f"{count:03d}"
                base_filename = f"{subject}_{expression}_{face_pose}_{note}_{index}"

            # Define base path
            try:
                if relative_path and relative_path != ".":
                    base_path = Path(folder_paths.get_output_directory()) / output_dir / expression / relative_path
                else:
                    base_path = Path(folder_paths.get_output_directory()) / output_dir / expression
            except:
                base_path = Path(output_dir) / expression
                
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Final filename and path
            final_filename = f"{base_filename}.png"
            full_save_path = base_path / final_filename

            # Create comprehensive metadata
            save_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            metadata = {
                # Basic info
                "subject": str(subject),
                "expression": str(expression),
                "pose": str(face_pose),
                "note": str(note),
                
                # Technical info
                "width": width if width > 0 else pil_img.size[0],
                "height": height if height > 0 else pil_img.size[1],
                "original_filename": filename if filename else base_filename,
                "source_directory": str(source_directory),
                "relative_path": str(relative_path),
                "original_full_path": str(full_path),
                "original_creation_date": str(creation_date),
                "original_file_size": int(file_size) if file_size > 0 else 0,
                
                # Additional metadata
                "age": str(age),
                "gender": str(gender),
                "ethnicity": str(ethnicity),
                "lighting": str(lighting),
                "background": str(background),
                "camera_angle": str(camera_angle),
                "quality_rating": int(quality_rating),
                "tags": str(tags),
                "dataset_name": str(dataset_name),
                "training_weight": float(training_weight),
                
                # Processing info
                "processed_timestamp": save_timestamp,
                "processed_by": "Bear Cave EXIF Writer",
                "processing_version": "1.0"
            }

            # Write metadata to PNG
            meta = PngImagePlugin.PngInfo()
            
            # Add individual fields
            for key, value in metadata.items():
                if value:  # Only add non-empty values
                    meta.add_text(key.title().replace("_", " "), str(value))
            
            # Add JSON metadata
            meta.add_text("BearCave_Metadata_JSON", json.dumps(metadata, indent=2))
            
            # Create tags string
            tags_list = []
            if expression: tags_list.append(f"expression:{expression}")
            if face_pose: tags_list.append(f"pose:{face_pose}")
            if age: tags_list.append(f"age:{age}")
            if gender: tags_list.append(f"gender:{gender}")
            if tags: tags_list.extend([t.strip() for t in tags.split(",") if t.strip()])
            
            tags_string = ", ".join(tags_list)
            if tags_string:
                meta.add_text("Tags", tags_string)

            # Save image with metadata
            pil_img.save(full_save_path, pnginfo=meta)
            
            # Get final file size
            final_file_size = full_save_path.stat().st_size
            
            # Create full metadata string for output
            full_metadata_string = "\n".join([f"{k}: {v}" for k, v in metadata.items() if v])
            
            print(f"🐻 Bear Cave: Saved image with comprehensive EXIF: {full_save_path}")
            
            return (
                str(full_save_path),
                final_filename,
                json.dumps(metadata, indent=2),
                tags_string,
                full_metadata_string,
                True,
                int(final_file_size),
                save_timestamp
            )
            
        except Exception as e:
            print(f"🐻 Bear Cave: Error in BearExifWriter: {e}")
            return ("error", "error", "{}", "", str(e), False, 0, "")

# Node registration
NODE_CLASS_MAPPINGS = {
    "BC_EXIF_WRITER": BC_EXIF_WRITER
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BC_EXIF_WRITER": "🐻 Write EXIF Data"
}