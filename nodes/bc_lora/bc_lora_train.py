############################
# bc_lora_train.py
############################
# Training configuration & execution with background processing and progress monitoring
############################

import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Callable

class BC_LORA_TRAIN:
    """Execute LoRa training with background processing and progress monitoring"""
    
    # Class-level training state management
    _active_trainings = {}
    _training_lock = threading.Lock()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "training_config": ("STRING", {"forceInput": True}),
                "conform_path": ("STRING", {"forceInput": True}),
                "output_path": ("STRING", {"forceInput": True}),
                "start_training": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                # Connection points from other nodes
                "project_metadata": ("STRING", {"forceInput": True}),
                "caption_files": ("STRING", {"forceInput": True}),
                # Training control
                "stop_training": ("BOOLEAN", {"default": False}),
                "resume_from_checkpoint": ("STRING", {"default": ""}),
                # Monitoring options
                "enable_progress_monitoring": ("BOOLEAN", {"default": True}),
                "save_samples": ("BOOLEAN", {"default": True}),
                "sample_frequency": ("INT", {"default": 5, "min": 1, "max": 50}),
                # Advanced options
                "custom_args": ("STRING", {"default": "", "multiline": True}),
                "dry_run": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = (
        "STRING",    # Training status
        "STRING",    # Progress percentage
        "STRING",    # Current epoch info
        "STRING",    # Training metrics (JSON)
        "STRING",    # Model output path
        "STRING",    # Training log
        "BOOLEAN",   # Training active
        "STRING",    # Status message
        "STRING",    # Training results (JSON)
    )
    
    RETURN_NAMES = (
        "training_status",
        "progress_percentage",
        "epoch_info",
        "training_metrics",
        "model_path",
        "training_log",
        "training_active",
        "status_message",
        "training_results"
    )
    
    FUNCTION = "execute_training"
    CATEGORY = "🐻 Bear Cave/LoRa"
    OUTPUT_NODE = True

    def execute_training(self, training_config, conform_path, output_path, start_training, **kwargs):
        try:
            # Extract optional parameters
            project_metadata = kwargs.get('project_metadata', '{}')
            caption_files = kwargs.get('caption_files', '[]')
            stop_training = kwargs.get('stop_training', False)
            resume_from_checkpoint = kwargs.get('resume_from_checkpoint', '')
            enable_progress_monitoring = kwargs.get('enable_progress_monitoring', True)
            save_samples = kwargs.get('save_samples', True)
            sample_frequency = kwargs.get('sample_frequency', 5)
            custom_args = kwargs.get('custom_args', '')
            dry_run = kwargs.get('dry_run', False)
            
            # Parse input data
            try:
                config = json.loads(training_config) if training_config != '{}' else {}
                project_meta = json.loads(project_metadata) if project_metadata != '{}' else {}
                captions = json.loads(caption_files) if caption_files != '[]' else []
            except json.JSONDecodeError as e:
                return self._error_return(f"Invalid JSON input: {e}")
            
            # Generate unique training ID
            training_id = self._generate_training_id(output_path)
            
            # Handle stop training request
            if stop_training:
                return self._handle_stop_training(training_id)
            
            # Check if training is already active for this project
            if training_id in self._active_trainings:
                return self._get_training_status(training_id)
            
            # Start new training if requested
            if start_training:
                return self._start_new_training(
                    training_id, config, conform_path, output_path,
                    project_meta, captions, resume_from_checkpoint,
                    enable_progress_monitoring, save_samples, sample_frequency,
                    custom_args, dry_run
                )
            
            # Return idle state if no action requested
            return self._idle_return("Training ready - set 'start_training' to begin")
            
        except Exception as e:
            print(f"🐻 Bear Cave LoRa: Error in execute_training: {e}")
            return self._error_return(f"Training execution failed: {str(e)}")
    
    def _generate_training_id(self, output_path: str) -> str:
        """Generate unique training ID based on output path"""
        import hashlib
        return hashlib.md5(output_path.encode()).hexdigest()[:8]
    
    def _handle_stop_training(self, training_id: str):
        """Handle stop training request"""
        with self._training_lock:
            if training_id in self._active_trainings:
                training_state = self._active_trainings[training_id]
                wrapper = training_state.get('wrapper')
                
                if wrapper:
                    success, message = wrapper.stop_training()
                    if success:
                        # Clean up training state
                        del self._active_trainings[training_id]
                        return self._status_return(
                            "stopped", "0", "Training stopped", {}, "", 
                            "Training stopped by user", False, message, {}
                        )
                    else:
                        return self._error_return(f"Failed to stop training: {message}")
                else:
                    # Clean up orphaned state
                    del self._active_trainings[training_id]
                    return self._status_return(
                        "stopped", "0", "Training stopped", {}, "", 
                        "Training state cleared", False, "Training stopped", {}
                    )
            else:
                return self._error_return("No active training found to stop")
    
    def _get_training_status(self, training_id: str):
        """Get current training status"""
        with self._training_lock:
            if training_id not in self._active_trainings:
                return self._idle_return("No active training")
            
            training_state = self._active_trainings[training_id]
            wrapper = training_state.get('wrapper')
            
            if not wrapper:
                # Clean up orphaned state
                del self._active_trainings[training_id]
                return self._idle_return("Training state corrupted - cleared")
            
            # Get current status from wrapper
            status = wrapper.get_training_status()
            
            # Check if training completed or failed
            if not wrapper.is_training_active():
                if status['status'] == 'completed':
                    # Find output models
                    output_models = wrapper.find_output_models(training_state['output_path'])
                    model_path = output_models[0] if output_models else ""
                    
                    # Create training results
                    results = self._create_training_results(status, model_path, training_state)
                    
                    # Clean up training state
                    del self._active_trainings[training_id]
                    
                    return self._status_return(
                        "completed", "100", f"Training completed - {status['total_epochs']} epochs",
                        status, model_path, training_state.get('log', ''),
                        False, "Training completed successfully", results
                    )
                else:
                    # Training failed or stopped
                    error_msg = status.get('error_message', 'Training failed')
                    del self._active_trainings[training_id]
                    
                    return self._error_return(f"Training failed: {error_msg}")
            
            # Training is still active - return current status
            progress = f"{status['progress_percentage']:.1f}"
            epoch_info = f"Epoch {status['current_epoch']}/{status['total_epochs']}"
            
            return self._status_return(
                status['status'], progress, epoch_info, status, "",
                training_state.get('log', ''), True, 
                f"Training in progress - {epoch_info}", {}
            )
    
    def _start_new_training(self, training_id: str, config: Dict[str, Any], 
                           conform_path: str, output_path: str, project_meta: Dict[str, Any],
                           captions: list, resume_from_checkpoint: str,
                           enable_progress_monitoring: bool, save_samples: bool,
                           sample_frequency: int, custom_args: str, dry_run: bool):
        """Start new training process"""
        try:
            # Import kohya wrapper
            from .utils.kohya_wrapper import KohyaWrapper
            from .utils.lora_training_config import LoRaTrainingConfig
            
            # Validate configuration
            is_valid, errors = LoRaTrainingConfig.validate_config(config)
            if not is_valid:
                return self._error_return(f"Invalid training config: {'; '.join(errors)}")
            
            # Update config with current paths
            config.update({
                'train_data_dir': conform_path,
                'output_dir': output_path,
                'logging_dir': os.path.join(output_path, 'logs')
            })
            
            # Add resume checkpoint if provided
            if resume_from_checkpoint and os.path.exists(resume_from_checkpoint):
                config['resume'] = resume_from_checkpoint
            
            # Add sample settings
            if save_samples:
                config['sample_every_n_epochs'] = sample_frequency
                samples_dir = os.path.join(output_path, 'samples')
                os.makedirs(samples_dir, exist_ok=True)
            
            # Add custom arguments
            if custom_args:
                # Parse custom args and add to config
                custom_config = self._parse_custom_args(custom_args)
                config.update(custom_config)
            
            # Create wrapper and progress callback
            wrapper = KohyaWrapper()
            
            # Set up progress callback if monitoring enabled
            progress_callback = None
            if enable_progress_monitoring:
                progress_callback = lambda status: self._update_training_log(training_id, status)
            
            # Dry run - just validate and return
            if dry_run:
                prepared, prep_message = wrapper.prepare_training_environment(config)
                if not prepared:
                    return self._error_return(f"Dry run failed: {prep_message}")
                
                return self._status_return(
                    "dry_run", "0", "Dry run completed", {}, "",
                    f"Dry run successful: {prep_message}", False,
                    "Configuration validated successfully", {}
                )
            
            # Start actual training
            success, message = wrapper.start_training(config, progress_callback)
            
            if not success:
                return self._error_return(f"Failed to start training: {message}")
            
            # Store training state
            with self._training_lock:
                self._active_trainings[training_id] = {
                    'wrapper': wrapper,
                    'config': config,
                    'output_path': output_path,
                    'start_time': time.time(),
                    'log': f"Training started: {message}\n"
                }
            
            return self._status_return(
                "starting", "0", "Training starting", {}, "",
                f"Training started: {message}", True, message, {}
            )
            
        except Exception as e:
            return self._error_return(f"Failed to start training: {str(e)}")
    
    def _parse_custom_args(self, custom_args: str) -> Dict[str, Any]:
        """Parse custom arguments string into config dictionary"""
        config = {}
        try:
            # Simple parsing - each line should be key=value
            for line in custom_args.strip().split('\n'):
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Try to convert to appropriate type
                    if value.lower() in ['true', 'false']:
                        config[key] = value.lower() == 'true'
                    elif value.isdigit():
                        config[key] = int(value)
                    elif '.' in value and value.replace('.', '').isdigit():
                        config[key] = float(value)
                    else:
                        config[key] = value
        except Exception as e:
            print(f"🐻 Bear Cave LoRa: Warning - error parsing custom args: {e}")
        
        return config
    
    def _update_training_log(self, training_id: str, status: Dict[str, Any]):
        """Update training log with progress information"""
        try:
            with self._training_lock:
                if training_id in self._active_trainings:
                    training_state = self._active_trainings[training_id]
                    
                    # Add status update to log
                    timestamp = time.strftime("%H:%M:%S")
                    if status.get('status') == 'training':
                        log_entry = f"[{timestamp}] Epoch {status['current_epoch']}/{status['total_epochs']} - Loss: {status['current_loss']:.4f} - Progress: {status['progress_percentage']:.1f}%\n"
                    elif status.get('status') == 'saving':
                        log_entry = f"[{timestamp}] Saving checkpoint...\n"
                    else:
                        log_entry = f"[{timestamp}] Status: {status.get('status', 'unknown')}\n"
                    
                    training_state['log'] = training_state.get('log', '') + log_entry
        except Exception as e:
            print(f"🐻 Bear Cave LoRa: Error updating training log: {e}")
    
    def _create_training_results(self, status: Dict[str, Any], model_path: str, 
                                training_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create training results summary"""
        start_time = training_state.get('start_time', time.time())
        training_time = time.time() - start_time
        
        results = {
            "model_path": model_path,
            "training_completed": True,
            "final_epoch": status.get('current_epoch', 0),
            "final_loss": status.get('current_loss', 0.0),
            "training_time_seconds": training_time,
            "total_steps": status.get('total_steps', 0),
            "model_size_mb": 0.0,  # Will be calculated if model exists
            "sample_images": [],
            "training_log": training_state.get('log', ''),
            "error_message": ""
        }
        
        # Calculate model size if it exists
        if model_path and os.path.exists(model_path):
            try:
                model_size_bytes = os.path.getsize(model_path)
                results["model_size_mb"] = model_size_bytes / (1024 * 1024)
            except Exception as e:
                print(f"🐻 Bear Cave LoRa: Could not get model size: {e}")
        
        # Find sample images
        try:
            samples_dir = os.path.join(training_state['output_path'], 'samples')
            if os.path.exists(samples_dir):
                sample_files = []
                for ext in ['.png', '.jpg', '.jpeg']:
                    sample_files.extend([str(f) for f in Path(samples_dir).glob(f'*{ext}')])
                results["sample_images"] = sorted(sample_files)
        except Exception as e:
            print(f"🐻 Bear Cave LoRa: Could not find sample images: {e}")
        
        return results
    
    def _status_return(self, status: str, progress: str, epoch_info: str, 
                      metrics: Dict[str, Any], model_path: str, log: str,
                      active: bool, message: str, results: Dict[str, Any]):
        """Return training status"""
        return (
            status,
            progress,
            epoch_info,
            json.dumps(metrics, indent=2),
            model_path,
            log,
            active,
            message,
            json.dumps(results, indent=2)
        )
    
    def _idle_return(self, message: str):
        """Return idle state"""
        return self._status_return(
            "idle", "0", "No training active", {}, "", "", False, message, {}
        )
    
    def _error_return(self, message: str):
        """Return error state"""
        return self._status_return(
            "error", "0", "Error", {}, "", message, False, message, {}
        )

# Node registration
NODE_CLASS_MAPPINGS = {
    "BC_LORA_TRAIN": BC_LORA_TRAIN
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BC_LORA_TRAIN": "🐻 Train LoRa Model"
}
