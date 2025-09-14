############################
# directory_organizer.py
############################
# Organize images into emotion-based directories for LoRA training
############################

import os
import shutil
from pathlib import Path
import torch

class TORTU_DIRECTORY_ORGANIZER:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_directory": ("STRING", {"default": ""}),
                "project_name": ("STRING", {"default": "lora_project"}),
            },
            "optional": {
                # Connection points from other nodes
                "filename": ("STRING", {"forceInput": True}),
                "relative_path": ("STRING", {"forceInput": True}),
                "primary_emotion": ("STRING", {"forceInput": True}),
                "high_confidence": ("BOOLEAN", {"forceInput": True}),
                "should_process": ("BOOLEAN", {"forceInput": True}),
                "image_batch": ("IMAGE", {"forceInput": True}),
                # Organization options
                "create_review_folder": ("BOOLEAN", {"default": True}),
                "low_confidence_to_review": ("BOOLEAN", {"default": True}),
                "organize_by_emotion": ("BOOLEAN", {"default": True}),
                "create_source_backup": ("BOOLEAN", {"default": False}),
                "dry_run": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = (
        "STRING",    # Target directory path
        "STRING",    # Organized filename
        "BOOLEAN",   # File moved/organized
        "STRING",    # Organization status
        "STRING",    # Full output path
        "STRING",    # Target emotion folder
        "INT",       # Files processed count
    )
    
    RETURN_NAMES = (
        "target_directory",
        "organized_filename", 
        "file_organized",
        "status",
        "full_output_path",
        "emotion_folder",
        "processed_count"
    )
    
    FUNCTION = "organize_directories"
    CATEGORY = "🐢 TORTU/LoRa"

    def __init__(self):
        self.processed_count = 0

    def organize_directories(self, base_directory, project_name, **kwargs):
        # Extract optional inputs
        filename = kwargs.get('filename', '')
        relative_path = kwargs.get('relative_path', '')
        primary_emotion = kwargs.get('primary_emotion', 'unknown')
        high_confidence = kwargs.get('high_confidence', False)
        should_process = kwargs.get('should_process', True)
        image_batch = kwargs.get('image_batch', None)
        
        create_review_folder = kwargs.get('create_review_folder', True)
        low_confidence_to_review = kwargs.get('low_confidence_to_review', True)
        organize_by_emotion = kwargs.get('organize_by_emotion', True)
        create_source_backup = kwargs.get('create_source_backup', False)
        dry_run = kwargs.get('dry_run', False)
        
        if not base_directory.strip():
            return (
                "", "", False, "No base directory provided", "", "", self.processed_count
            )
        
        if not should_process:
            return (
                "", "", False, "Skipped - should not process", "", "", self.processed_count
            )
        
        try:
            # Create project structure
            base_path = Path(base_directory) / project_name
            expressions_root = base_path / "01_EXPRESSIONS"
            review_folder = expressions_root / "_REVIEW"
            source_backup = base_path / "00_SOURCE_BACKUP"
            
            # Determine target directory
            if organize_by_emotion and high_confidence and not low_confidence_to_review:
                # High confidence - organize by emotion
                target_dir = expressions_root / primary_emotion.lower()
                emotion_folder = primary_emotion.lower()
            elif organize_by_emotion and not high_confidence and low_confidence_to_review and create_review_folder:
                # Low confidence - send to review folder
                target_dir = review_folder
                emotion_folder = "_REVIEW"
            elif organize_by_emotion:
                # Organize by emotion regardless of confidence
                target_dir = expressions_root / primary_emotion.lower()
                emotion_folder = primary_emotion.lower()
            else:
                # No emotion organization - everything goes to expressions root
                target_dir = expressions_root
                emotion_folder = "expressions"
            
            # Create directories in dry run to show structure
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                if create_source_backup:
                    source_backup.mkdir(parents=True, exist_ok=True)
                if create_review_folder:
                    review_folder.mkdir(parents=True, exist_ok=True)
            
            # Generate organized filename
            if filename:
                base_name = Path(filename).stem
                extension = Path(filename).suffix or '.jpg'
            else:
                base_name = f"image_{self.processed_count:03d}"
                extension = '.jpg'
            
            # Create organized filename with emotion and pose placeholders
            organized_filename = f"{base_name}_{primary_emotion.lower()}_POSE_NOTE{extension}"
            full_output_path = str(target_dir / organized_filename)
            
            file_organized = False
            status = f"DRY RUN: Would organize to {emotion_folder}/" if dry_run else ""
            
            if not dry_run and image_batch is not None:
                # This is a planning node - actual file operations would be handled 
                # by the metadata writer or a separate file writer node
                file_organized = True
                status = f"Organized to {emotion_folder}/ folder"
            elif not dry_run:
                status = "Directory structure created, no image to process"
            
            # Track processed files
            if should_process:
                self.processed_count += 1
            
            return (
                str(target_dir),
                organized_filename,
                file_organized,
                status,
                full_output_path,
                emotion_folder,
                self.processed_count
            )
            
        except Exception as e:
            print(f"🐢 TORTU: Error in directory organization: {e}")
            return (
                "", "", False, f"Organization error: {str(e)}", 
                "", "", self.processed_count
            )

    @classmethod
    def create_project_structure(cls, base_directory, project_name):
        """Utility method to create the full LoRA project structure"""
        try:
            base_path = Path(base_directory) / project_name
            
            # Create main directories
            (base_path / "00_SOURCE").mkdir(parents=True, exist_ok=True)
            (base_path / "01_EXPRESSIONS").mkdir(parents=True, exist_ok=True)
            (base_path / "01_EXPRESSIONS" / "_REVIEW").mkdir(parents=True, exist_ok=True)
            (base_path / "02_TRAINING").mkdir(parents=True, exist_ok=True)
            (base_path / "03_OUTPUT").mkdir(parents=True, exist_ok=True)
            
            # Create common emotion folders
            emotions = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral']
            expressions_root = base_path / "01_EXPRESSIONS"
            for emotion in emotions:
                (expressions_root / emotion).mkdir(parents=True, exist_ok=True)
            
            return str(base_path)
            
        except Exception as e:
            print(f"🐢 TORTU: Error creating project structure: {e}")
            return None

NODE_CLASS_MAPPINGS = {
    "TORTU_DIRECTORY_ORGANIZER": TORTU_DIRECTORY_ORGANIZER
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TORTU_DIRECTORY_ORGANIZER": "🐢 Directory Organizer"
}