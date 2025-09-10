############################
# bc_lora_define.py
############################
# Subject/project definition node for LoRa training setup
############################

import os
import json
from pathlib import Path
from typing import Dict, Any, Tuple
from datetime import datetime

class BC_LORA_DEFINE:
    """Define LoRa training project with folder structure and configuration"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_name": ("STRING", {"default": "my_lora_project"}),
                "subject_name": ("STRING", {"default": "subject"}),
                "project_base_path": ("STRING", {"default": "", "placeholder": "Double-click to browse for project folder..."}),
                "trigger_words": ("STRING", {"default": ""}),
                "base_model": (["sd15", "sd21", "sdxl", "custom"], {"default": "sd15"}),
                "performance_mode": (["fast", "balanced", "quality"], {"default": "balanced"}),
            },
            "optional": {
                "description": ("STRING", {"default": "", "multiline": True}),
                "custom_base_model_path": ("STRING", {"default": ""}),
                "create_folders": ("BOOLEAN", {"default": True}),
                "overwrite_existing": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = (
        "STRING",    # Project path
        "STRING",    # Source folder path (01_source)
        "STRING",    # Conform folder path (02_conform)
        "STRING",    # Output folder path (03_output)
        "STRING",    # Project metadata JSON
        "STRING",    # Training config JSON
        "BOOLEAN",   # Setup successful
        "STRING",    # Status message
    )
    
    RETURN_NAMES = (
        "project_path",
        "source_path",
        "conform_path",
        "output_path",
        "project_metadata",
        "training_config",
        "setup_successful",
        "status_message"
    )
    
    FUNCTION = "define_project"
    CATEGORY = "🐻 Bear Cave/LoRa"

    def define_project(self, project_name, subject_name, project_base_path, 
                      trigger_words, base_model, performance_mode, **kwargs):
        try:
            # Extract optional parameters
            description = kwargs.get('description', '')
            custom_base_model_path = kwargs.get('custom_base_model_path', '')
            create_folders = kwargs.get('create_folders', True)
            overwrite_existing = kwargs.get('overwrite_existing', False)
            
            # Sanitize project name
            safe_project_name = self._sanitize_filename(project_name)
            if not safe_project_name:
                return self._error_return("Invalid project name")
            
            # Create project path
            project_path = Path(project_base_path) / safe_project_name
            
            # Check if project already exists
            if project_path.exists() and not overwrite_existing:
                return self._error_return(f"Project already exists: {project_path}")
            
            # Define folder structure
            source_path = project_path / "01_source"
            conform_path = project_path / "02_conform"
            output_path = project_path / "03_output"
            
            # Create folders if requested
            if create_folders:
                success, message = self._create_project_folders(
                    project_path, source_path, conform_path, output_path
                )
                if not success:
                    return self._error_return(message)
            
            # Create project metadata
            project_metadata = self._create_project_metadata(
                safe_project_name, subject_name, str(project_path),
                trigger_words, base_model, performance_mode, description,
                custom_base_model_path
            )
            
            # Create training configuration
            training_config = self._create_training_config(
                safe_project_name, subject_name, str(project_path),
                trigger_words, performance_mode
            )
            
            # Save metadata files if folders were created
            if create_folders:
                self._save_project_files(project_path, project_metadata, training_config)
            
            # Success return
            status_message = f"Project '{safe_project_name}' defined successfully"
            if create_folders:
                status_message += f" at {project_path}"
            
            return (
                str(project_path),
                str(source_path),
                str(conform_path),
                str(output_path),
                json.dumps(project_metadata, indent=2),
                json.dumps(training_config, indent=2),
                True,
                status_message
            )
            
        except Exception as e:
            print(f"🐻 Bear Cave LoRa: Error in define_project: {e}")
            return self._error_return(f"Project definition failed: {str(e)}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe filesystem use"""
        import re
        # Remove or replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'\s+', '_', sanitized)  # Replace spaces with underscores
        sanitized = sanitized.strip('._')  # Remove leading/trailing dots and underscores
        return sanitized[:100]  # Limit length
    
    def _create_project_folders(self, project_path: Path, source_path: Path, 
                               conform_path: Path, output_path: Path) -> Tuple[bool, str]:
        """Create the project folder structure"""
        try:
            # Create main project directory
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            source_path.mkdir(exist_ok=True)
            conform_path.mkdir(exist_ok=True)
            output_path.mkdir(exist_ok=True)
            
            # Create additional subdirectories in output
            (output_path / "logs").mkdir(exist_ok=True)
            (output_path / "samples").mkdir(exist_ok=True)
            
            # Create README files
            self._create_readme_files(source_path, conform_path, output_path)
            
            print(f"🐻 Bear Cave LoRa: Created project folders at {project_path}")
            return True, "Folders created successfully"
            
        except Exception as e:
            return False, f"Failed to create folders: {str(e)}"
    
    def _create_readme_files(self, source_path: Path, conform_path: Path, output_path: Path):
        """Create README files explaining each folder's purpose"""
        readme_contents = {
            source_path / "README.md": """# 01_source

This folder contains the original source images for LoRa training.

- Place your raw images here in any format (JPG, PNG, etc.)
- Images can be any aspect ratio and resolution
- These will be processed and conformed for training

## Guidelines:
- Use high-quality images (at least 512x512)
- Ensure good variety in poses, expressions, lighting
- 10-50 images typically work well for person LoRas
""",
            conform_path / "README.md": """# 02_conform

This folder contains processed images ready for LoRa training.

- Images are automatically cropped to square format
- Resized to 1024x1024 for optimal training
- Face-centered cropping when faces are detected

## Contents:
- Processed training images (.png/.jpg)
- Caption files (.txt) with same base name as images
- Metadata files for training configuration
""",
            output_path / "README.md": """# 03_output

This folder contains the final LoRa model and training outputs.

## Contents:
- **Final LoRa model** (.safetensors file)
- **logs/** - Training logs and TensorBoard data
- **samples/** - Sample images generated during training
- **training_config.json** - Configuration used for training
- **training_results.json** - Training statistics and results
"""
        }
        
        for filepath, content in readme_contents.items():
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                print(f"🐻 Bear Cave LoRa: Warning - could not create {filepath}: {e}")
    
    def _create_project_metadata(self, project_name: str, subject_name: str, 
                                project_path: str, trigger_words: str, base_model: str,
                                performance_mode: str, description: str, 
                                custom_base_model_path: str) -> Dict[str, Any]:
        """Create project metadata structure"""
        from .utils.metadata_schema import LoRaMetadataSchema
        
        # Create base metadata
        metadata = LoRaMetadataSchema.create_project_metadata_template(
            project_name, subject_name, project_path
        )
        
        # Update with provided values
        metadata.update({
            "trigger_words": trigger_words or f"{subject_name.lower().replace(' ', '_')}",
            "base_model": base_model,
            "performance_mode": performance_mode,
            "description": description or f"LoRa training project for {subject_name}",
        })
        
        if custom_base_model_path:
            metadata["custom_base_model_path"] = custom_base_model_path
        
        return metadata
    
    def _create_training_config(self, project_name: str, subject_name: str,
                               project_path: str, trigger_words: str,
                               performance_mode: str) -> Dict[str, Any]:
        """Create training configuration"""
        from .utils.lora_training_config import LoRaTrainingConfig
        
        # Get performance-specific settings
        perf_config = LoRaTrainingConfig.get_performance_config(performance_mode)
        
        # Create full configuration
        config = LoRaTrainingConfig.create_config(
            project_name=project_name,
            project_path=project_path,
            subject_name=subject_name,
            trigger_words=trigger_words,
            custom_settings=perf_config
        )
        
        return config
    
    def _save_project_files(self, project_path: Path, project_metadata: Dict[str, Any],
                           training_config: Dict[str, Any]):
        """Save project metadata and configuration files"""
        try:
            # Save project metadata
            metadata_file = project_path / "project_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(project_metadata, f, indent=2, ensure_ascii=False)
            
            # Save training configuration
            config_file = project_path / "training_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(training_config, f, indent=2, ensure_ascii=False)
            
            print(f"🐻 Bear Cave LoRa: Saved project files to {project_path}")
            
        except Exception as e:
            print(f"🐻 Bear Cave LoRa: Warning - could not save project files: {e}")
    
    def _error_return(self, message: str):
        """Return error state"""
        return ("", "", "", "", "{}", "{}", False, message)

# Node registration
NODE_CLASS_MAPPINGS = {
    "BC_LORA_DEFINE": BC_LORA_DEFINE
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BC_LORA_DEFINE": "🐻 Define LoRa Project"
}
