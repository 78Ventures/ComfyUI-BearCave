############################
# lora_training_config.py
############################
# Training configuration templates optimized for M4 Mac Mini with 64GB RAM
############################

import os
from typing import Dict, Any, Optional

class LoRaTrainingConfig:
    """Configuration templates for LoRa training optimized for Apple Silicon M4 Mac Mini"""
    
    # M4 Mac Mini optimized defaults
    DEFAULT_CONFIG = {
        # Model and data settings
        "resolution": 1024,
        "batch_size": 2,  # Conservative for 64GB RAM
        "max_train_epochs": 15,
        "save_every_n_epochs": 5,
        
        # Network architecture
        "network_dim": 32,  # Good balance of quality/size
        "network_alpha": 16,  # Half of network_dim (standard practice)
        "network_module": "networks.lora",
        
        # Learning rate and optimization
        "learning_rate": 1e-4,  # Conservative, good results
        "lr_scheduler": "cosine_with_restarts",
        "lr_warmup_steps": 100,
        "optimizer_type": "AdamW8bit",  # Memory efficient
        
        # Mixed precision and memory optimization
        "mixed_precision": "fp16",  # Faster on Apple Silicon
        "gradient_checkpointing": True,  # Save memory
        "gradient_accumulation_steps": 1,
        
        # Data loading
        "train_data_dir": "",  # Will be set dynamically
        "output_dir": "",      # Will be set dynamically
        "logging_dir": "",     # Will be set dynamically
        
        # Regularization and quality
        "noise_offset": 0.1,
        "adaptive_noise_scale": 0.00357,
        "multires_noise_iterations": 10,
        "multires_noise_discount": 0.1,
        
        # Sampling and validation
        "sample_every_n_epochs": 5,
        "sample_prompts": "",  # Will be set based on subject
        
        # Apple Silicon specific optimizations
        "enable_bucket": True,
        "bucket_no_upscale": True,
        "bucket_reso_steps": 64,
        "min_bucket_reso": 256,
        "max_bucket_reso": 1024,
        
        # Logging and monitoring
        "log_with": "tensorboard",
        "logging_dir": "",
        "log_prefix": "bc_lora",
        
        # Safety and stability
        "max_grad_norm": 1.0,
        "scale_v_pred_loss_like_noise_pred": True,
        "min_snr_gamma": 5.0,
        
        # File handling
        "save_model_as": "safetensors",
        "save_precision": "fp16",
        "save_state": True,
        "resume": "",  # Path to resume from if needed
    }
    
    @classmethod
    def create_config(cls, 
                     project_name: str,
                     project_path: str,
                     subject_name: str,
                     trigger_words: str = "",
                     custom_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a complete training configuration
        
        Args:
            project_name: Name of the LoRa project
            project_path: Base path to the project directory
            subject_name: Name of the subject being trained
            trigger_words: Trigger words for the LoRa
            custom_settings: Override default settings
        
        Returns:
            Complete configuration dictionary
        """
        config = cls.DEFAULT_CONFIG.copy()
        
        # Set up paths based on your folder structure
        conform_path = os.path.join(project_path, "02_conform")
        output_path = os.path.join(project_path, "03_output")
        logs_path = os.path.join(output_path, "logs")
        
        # Update paths
        config.update({
            "train_data_dir": conform_path,
            "output_dir": output_path,
            "logging_dir": logs_path,
            "output_name": f"{project_name}_{subject_name}",
        })
        
        # Set up sample prompts based on subject and trigger words
        if trigger_words:
            sample_prompts = [
                f"{trigger_words}, portrait, high quality",
                f"{trigger_words}, smiling, professional photo",
                f"{trigger_words}, looking at camera, studio lighting"
            ]
            config["sample_prompts"] = "\n".join(sample_prompts)
        
        # Apply custom settings if provided
        if custom_settings:
            config.update(custom_settings)
        
        return config
    
    @classmethod
    def get_performance_config(cls, performance_mode: str = "balanced") -> Dict[str, Any]:
        """
        Get performance-specific configurations
        
        Args:
            performance_mode: "fast", "balanced", or "quality"
        
        Returns:
            Performance-specific settings
        """
        configs = {
            "fast": {
                "batch_size": 4,
                "max_train_epochs": 10,
                "network_dim": 16,
                "network_alpha": 8,
                "learning_rate": 2e-4,
                "gradient_accumulation_steps": 1,
            },
            "balanced": {
                "batch_size": 2,
                "max_train_epochs": 15,
                "network_dim": 32,
                "network_alpha": 16,
                "learning_rate": 1e-4,
                "gradient_accumulation_steps": 1,
            },
            "quality": {
                "batch_size": 1,
                "max_train_epochs": 25,
                "network_dim": 64,
                "network_alpha": 32,
                "learning_rate": 5e-5,
                "gradient_accumulation_steps": 2,
            }
        }
        
        return configs.get(performance_mode, configs["balanced"])
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate configuration settings
        
        Args:
            config: Configuration dictionary to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required paths
        if not config.get("train_data_dir"):
            errors.append("train_data_dir is required")
        elif not os.path.exists(config["train_data_dir"]):
            errors.append(f"train_data_dir does not exist: {config['train_data_dir']}")
        
        if not config.get("output_dir"):
            errors.append("output_dir is required")
        
        # Validate numeric ranges
        if config.get("batch_size", 0) < 1:
            errors.append("batch_size must be >= 1")
        
        if config.get("network_dim", 0) < 1:
            errors.append("network_dim must be >= 1")
        
        if config.get("learning_rate", 0) <= 0:
            errors.append("learning_rate must be > 0")
        
        # Check for M4 Mac specific optimizations
        if config.get("mixed_precision") not in ["fp16", "bf16", "no"]:
            errors.append("mixed_precision must be 'fp16', 'bf16', or 'no'")
        
        return len(errors) == 0, errors
    
    @classmethod
    def to_kohya_args(cls, config: Dict[str, Any]) -> list[str]:
        """
        Convert configuration dictionary to kohya-ss command line arguments
        
        Args:
            config: Configuration dictionary
        
        Returns:
            List of command line arguments
        """
        args = []
        
        # Map config keys to kohya-ss argument names
        arg_mapping = {
            "train_data_dir": "--train_data_dir",
            "output_dir": "--output_dir",
            "logging_dir": "--logging_dir",
            "resolution": "--resolution",
            "batch_size": "--train_batch_size",
            "max_train_epochs": "--max_train_epochs",
            "save_every_n_epochs": "--save_every_n_epochs",
            "network_dim": "--network_dim",
            "network_alpha": "--network_alpha",
            "network_module": "--network_module",
            "learning_rate": "--learning_rate",
            "lr_scheduler": "--lr_scheduler",
            "lr_warmup_steps": "--lr_warmup_steps",
            "optimizer_type": "--optimizer_type",
            "mixed_precision": "--mixed_precision",
            "output_name": "--output_name",
            "save_model_as": "--save_model_as",
            "save_precision": "--save_precision",
        }
        
        # Convert config to arguments
        for config_key, arg_name in arg_mapping.items():
            if config_key in config and config[config_key] is not None:
                value = config[config_key]
                if isinstance(value, bool):
                    if value:
                        args.append(arg_name)
                else:
                    args.extend([arg_name, str(value)])
        
        # Add boolean flags
        boolean_flags = [
            "gradient_checkpointing",
            "enable_bucket",
            "bucket_no_upscale",
            "save_state",
            "scale_v_pred_loss_like_noise_pred"
        ]
        
        for flag in boolean_flags:
            if config.get(flag, False):
                args.append(f"--{flag}")
        
        return args
