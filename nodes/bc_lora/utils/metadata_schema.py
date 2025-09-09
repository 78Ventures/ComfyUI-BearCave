############################
# metadata_schema.py
############################
# JSON schemas for LoRa metadata validation and structure
############################

from typing import Dict, Any, List, Optional
import json
import jsonschema
from jsonschema import validate, ValidationError

class LoRaMetadataSchema:
    """JSON schemas for validating LoRa training metadata"""
    
    # Schema for project definition
    PROJECT_SCHEMA = {
        "type": "object",
        "properties": {
            "project_name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100,
                "pattern": "^[a-zA-Z0-9_-]+$"
            },
            "subject_name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100
            },
            "trigger_words": {
                "type": "string",
                "maxLength": 500
            },
            "description": {
                "type": "string",
                "maxLength": 1000
            },
            "project_path": {
                "type": "string",
                "minLength": 1
            },
            "base_model": {
                "type": "string",
                "enum": [
                    "sd15", "sd21", "sdxl", "custom"
                ]
            },
            "performance_mode": {
                "type": "string",
                "enum": ["fast", "balanced", "quality"]
            },
            "created_date": {
                "type": "string",
                "format": "date-time"
            },
            "version": {
                "type": "string",
                "pattern": "^\\d+\\.\\d+\\.\\d+$"
            }
        },
        "required": [
            "project_name", "subject_name", "project_path", "base_model"
        ],
        "additionalProperties": False
    }
    
    # Schema for training configuration
    TRAINING_CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "resolution": {
                "type": "integer",
                "minimum": 256,
                "maximum": 2048,
                "multipleOf": 64
            },
            "batch_size": {
                "type": "integer",
                "minimum": 1,
                "maximum": 16
            },
            "max_train_epochs": {
                "type": "integer",
                "minimum": 1,
                "maximum": 1000
            },
            "network_dim": {
                "type": "integer",
                "minimum": 1,
                "maximum": 1024
            },
            "network_alpha": {
                "type": "integer",
                "minimum": 1,
                "maximum": 1024
            },
            "learning_rate": {
                "type": "number",
                "minimum": 1e-6,
                "maximum": 1e-1
            },
            "optimizer_type": {
                "type": "string",
                "enum": [
                    "AdamW", "AdamW8bit", "Lion", "SGD", "DAdaptation"
                ]
            },
            "mixed_precision": {
                "type": "string",
                "enum": ["fp16", "bf16", "no"]
            },
            "save_model_as": {
                "type": "string",
                "enum": ["safetensors", "ckpt", "diffusers"]
            }
        },
        "required": [
            "resolution", "batch_size", "max_train_epochs", 
            "network_dim", "network_alpha", "learning_rate"
        ],
        "additionalProperties": True
    }
    
    # Schema for image metadata
    IMAGE_METADATA_SCHEMA = {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "minLength": 1
            },
            "caption": {
                "type": "string",
                "maxLength": 2000
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string",
                    "maxLength": 100
                },
                "maxItems": 50
            },
            "trigger_words": {
                "type": "array",
                "items": {
                    "type": "string",
                    "maxLength": 100
                },
                "maxItems": 10
            },
            "quality_score": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 10.0
            },
            "face_detected": {
                "type": "boolean"
            },
            "face_confidence": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0
            },
            "resolution": {
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "minimum": 1},
                    "height": {"type": "integer", "minimum": 1}
                },
                "required": ["width", "height"]
            },
            "processing_info": {
                "type": "object",
                "properties": {
                    "cropped": {"type": "boolean"},
                    "resized": {"type": "boolean"},
                    "crop_method": {"type": "string"},
                    "resize_method": {"type": "string"}
                }
            }
        },
        "required": ["filename", "caption"],
        "additionalProperties": True
    }
    
    # Schema for training results
    TRAINING_RESULTS_SCHEMA = {
        "type": "object",
        "properties": {
            "model_path": {
                "type": "string",
                "minLength": 1
            },
            "training_completed": {
                "type": "boolean"
            },
            "final_epoch": {
                "type": "integer",
                "minimum": 0
            },
            "final_loss": {
                "type": "number",
                "minimum": 0
            },
            "training_time_seconds": {
                "type": "number",
                "minimum": 0
            },
            "total_steps": {
                "type": "integer",
                "minimum": 0
            },
            "model_size_mb": {
                "type": "number",
                "minimum": 0
            },
            "sample_images": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "training_log": {
                "type": "string"
            },
            "error_message": {
                "type": "string"
            }
        },
        "required": ["training_completed"],
        "additionalProperties": True
    }
    
    @classmethod
    def validate_project_metadata(cls, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate project metadata against schema"""
        return cls._validate_against_schema(data, cls.PROJECT_SCHEMA)
    
    @classmethod
    def validate_training_config(cls, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate training configuration against schema"""
        return cls._validate_against_schema(data, cls.TRAINING_CONFIG_SCHEMA)
    
    @classmethod
    def validate_image_metadata(cls, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate image metadata against schema"""
        return cls._validate_against_schema(data, cls.IMAGE_METADATA_SCHEMA)
    
    @classmethod
    def validate_training_results(cls, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate training results against schema"""
        return cls._validate_against_schema(data, cls.TRAINING_RESULTS_SCHEMA)
    
    @classmethod
    def _validate_against_schema(cls, data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Generic validation method"""
        errors = []
        try:
            validate(instance=data, schema=schema)
            return True, []
        except ValidationError as e:
            errors.append(f"Validation error: {e.message}")
            if e.path:
                errors.append(f"Path: {' -> '.join(str(p) for p in e.path)}")
            return False, errors
        except Exception as e:
            errors.append(f"Schema validation failed: {str(e)}")
            return False, errors
    
    @classmethod
    def create_project_metadata_template(cls, 
                                       project_name: str,
                                       subject_name: str,
                                       project_path: str) -> Dict[str, Any]:
        """Create a template project metadata structure"""
        from datetime import datetime
        
        return {
            "project_name": project_name,
            "subject_name": subject_name,
            "trigger_words": f"{subject_name.lower().replace(' ', '_')}",
            "description": f"LoRa training project for {subject_name}",
            "project_path": project_path,
            "base_model": "sd15",
            "performance_mode": "balanced",
            "created_date": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    @classmethod
    def create_image_metadata_template(cls, filename: str, caption: str = "") -> Dict[str, Any]:
        """Create a template image metadata structure"""
        return {
            "filename": filename,
            "caption": caption or f"photo of {filename.split('.')[0]}",
            "tags": [],
            "trigger_words": [],
            "quality_score": 5.0,
            "face_detected": False,
            "face_confidence": 0.0,
            "resolution": {"width": 1024, "height": 1024},
            "processing_info": {
                "cropped": False,
                "resized": False,
                "crop_method": "none",
                "resize_method": "none"
            }
        }
    
    @classmethod
    def create_training_results_template(cls) -> Dict[str, Any]:
        """Create a template training results structure"""
        return {
            "model_path": "",
            "training_completed": False,
            "final_epoch": 0,
            "final_loss": 0.0,
            "training_time_seconds": 0.0,
            "total_steps": 0,
            "model_size_mb": 0.0,
            "sample_images": [],
            "training_log": "",
            "error_message": ""
        }
    
    @classmethod
    def save_metadata_to_file(cls, metadata: Dict[str, Any], filepath: str) -> bool:
        """Save metadata to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"🐻 Bear Cave LoRa: Failed to save metadata to {filepath}: {e}")
            return False
    
    @classmethod
    def load_metadata_from_file(cls, filepath: str) -> Optional[Dict[str, Any]]:
        """Load metadata from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"🐻 Bear Cave LoRa: Failed to load metadata from {filepath}: {e}")
            return None
    
    @classmethod
    def merge_metadata(cls, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Merge metadata dictionaries, with updates taking precedence"""
        merged = base.copy()
        
        for key, value in updates.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = cls.merge_metadata(merged[key], value)
            else:
                merged[key] = value
        
        return merged
