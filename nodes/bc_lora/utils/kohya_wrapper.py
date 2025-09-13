############################
# kohya_wrapper.py
############################
# Wrapper for kohya-ss functionality with progress monitoring
############################

import os
import sys
import subprocess
import threading
import queue
import re
import json
import time
from typing import Dict, Any, Optional, Callable, Tuple
from pathlib import Path

class KohyaTrainingMonitor:
    """Monitor kohya-ss training progress and provide real-time updates"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.is_running = False
        self.current_epoch = 0
        self.total_epochs = 0
        self.current_step = 0
        self.total_steps = 0
        self.current_loss = 0.0
        self.learning_rate = 0.0
        self.eta_seconds = 0
        self.status = "idle"
        self.error_message = ""
        
        # Regex patterns for parsing kohya-ss output
        self.patterns = {
            'epoch': re.compile(r'epoch (\d+)/(\d+)'),
            'step': re.compile(r'step (\d+)/(\d+)'),
            'loss': re.compile(r'loss: ([\d.]+)'),
            'lr': re.compile(r'lr: ([\d.e-]+)'),
            'eta': re.compile(r'eta: ([\d:]+)'),
            'saving': re.compile(r'saving.*model'),
            'error': re.compile(r'error|exception|failed', re.IGNORECASE),
        }
    
    def parse_training_output(self, line: str) -> Dict[str, Any]:
        """Parse a line of kohya-ss training output"""
        updates = {}
        
        # Parse epoch information
        epoch_match = self.patterns['epoch'].search(line)
        if epoch_match:
            self.current_epoch = int(epoch_match.group(1))
            self.total_epochs = int(epoch_match.group(2))
            updates['epoch'] = self.current_epoch
            updates['total_epochs'] = self.total_epochs
        
        # Parse step information
        step_match = self.patterns['step'].search(line)
        if step_match:
            self.current_step = int(step_match.group(1))
            self.total_steps = int(step_match.group(2))
            updates['step'] = self.current_step
            updates['total_steps'] = self.total_steps
        
        # Parse loss
        loss_match = self.patterns['loss'].search(line)
        if loss_match:
            self.current_loss = float(loss_match.group(1))
            updates['loss'] = self.current_loss
        
        # Parse learning rate
        lr_match = self.patterns['lr'].search(line)
        if lr_match:
            self.learning_rate = float(lr_match.group(1))
            updates['learning_rate'] = self.learning_rate
        
        # Check for saving status
        if self.patterns['saving'].search(line):
            self.status = "saving"
            updates['status'] = "saving"
        
        # Check for errors
        if self.patterns['error'].search(line):
            self.status = "error"
            self.error_message = line.strip()
            updates['status'] = "error"
            updates['error'] = self.error_message
        
        return updates
    
    def get_progress_percentage(self) -> float:
        """Calculate overall training progress percentage"""
        if self.total_epochs == 0:
            return 0.0
        
        epoch_progress = (self.current_epoch - 1) / self.total_epochs
        if self.total_steps > 0:
            step_progress = self.current_step / self.total_steps / self.total_epochs
            return min(100.0, (epoch_progress + step_progress) * 100)
        
        return min(100.0, epoch_progress * 100)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get current training status summary"""
        return {
            'status': self.status,
            'current_epoch': self.current_epoch,
            'total_epochs': self.total_epochs,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'progress_percentage': self.get_progress_percentage(),
            'current_loss': self.current_loss,
            'learning_rate': self.learning_rate,
            'eta_seconds': self.eta_seconds,
            'error_message': self.error_message,
            'is_running': self.is_running
        }

class KohyaWrapper:
    """Wrapper for kohya-ss training with progress monitoring and ComfyUI integration"""
    
    def __init__(self):
        self.monitor = KohyaTrainingMonitor()
        self.process = None
        self.output_queue = queue.Queue()
        self.training_thread = None
        
    def check_kohya_installation(self) -> Tuple[bool, str]:
        """Check if kohya-ss is properly installed"""
        try:
            import kohya_ss
            return True, "kohya-ss is installed"
        except ImportError:
            return False, "kohya-ss is not installed. Please install with: pip install kohya-ss"
    
    def prepare_training_environment(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """Prepare the training environment and validate configuration"""
        try:
            # Create output directories
            output_dir = Path(config['output_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logs_dir = Path(config['logging_dir'])
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Validate training data directory
            train_dir = Path(config['train_data_dir'])
            if not train_dir.exists():
                return False, f"Training data directory does not exist: {train_dir}"
            
            # Check for training images
            image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
            image_files = [f for f in train_dir.rglob('*') 
                          if f.suffix.lower() in image_extensions]
            
            if not image_files:
                return False, f"No training images found in: {train_dir}"
            
            print(f"🐢 TORTU LoRa: Found {len(image_files)} training images")
            return True, f"Training environment prepared successfully"
            
        except Exception as e:
            return False, f"Failed to prepare training environment: {str(e)}"
    
    def start_training(self, config: Dict[str, Any], 
                      progress_callback: Optional[Callable] = None) -> Tuple[bool, str]:
        """Start kohya-ss training in background"""
        try:
            # Check installation
            installed, message = self.check_kohya_installation()
            if not installed:
                return False, message
            
            # Prepare environment
            prepared, prep_message = self.prepare_training_environment(config)
            if not prepared:
                return False, prep_message
            
            # Set up monitor with callback
            if progress_callback:
                self.monitor.progress_callback = progress_callback
            
            # Convert config to kohya arguments
            from .lora_training_config import LoRaTrainingConfig
            args = LoRaTrainingConfig.to_kohya_args(config)
            
            # Start training in background thread
            self.training_thread = threading.Thread(
                target=self._run_training_process,
                args=(args,),
                daemon=True
            )
            self.training_thread.start()
            
            return True, "Training started successfully"
            
        except Exception as e:
            return False, f"Failed to start training: {str(e)}"
    
    def _run_training_process(self, args: list[str]):
        """Run the actual kohya-ss training process"""
        try:
            self.monitor.is_running = True
            self.monitor.status = "starting"
            
            # Build command - using python -m to run kohya-ss
            cmd = [sys.executable, "-m", "kohya_ss.train_network"] + args
            
            print(f"🐢 TORTU LoRa: Starting training with command:")
            print(f"  {' '.join(cmd)}")
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.monitor.status = "training"
            
            # Monitor output
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    print(f"🐢 Kohya: {line.strip()}")
                    
                    # Parse progress
                    updates = self.monitor.parse_training_output(line)
                    
                    # Call progress callback if provided
                    if self.monitor.progress_callback and updates:
                        try:
                            self.monitor.progress_callback(self.monitor.get_status_summary())
                        except Exception as e:
                            print(f"🐢 TORTU LoRa: Progress callback error: {e}")
            
            # Wait for process to complete
            return_code = self.process.wait()
            
            if return_code == 0:
                self.monitor.status = "completed"
                print("🐢 TORTU LoRa: Training completed successfully!")
            else:
                self.monitor.status = "error"
                self.monitor.error_message = f"Training failed with return code: {return_code}"
                print(f"🐢 TORTU LoRa: Training failed with return code: {return_code}")
            
        except Exception as e:
            self.monitor.status = "error"
            self.monitor.error_message = str(e)
            print(f"🐢 TORTU LoRa: Training process error: {e}")
        
        finally:
            self.monitor.is_running = False
            if self.process:
                self.process = None
    
    def stop_training(self) -> Tuple[bool, str]:
        """Stop the current training process"""
        try:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                
                # Wait a bit for graceful termination
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                
                self.monitor.status = "stopped"
                self.monitor.is_running = False
                return True, "Training stopped successfully"
            else:
                return False, "No training process is currently running"
                
        except Exception as e:
            return False, f"Failed to stop training: {str(e)}"
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get current training status"""
        return self.monitor.get_status_summary()
    
    def is_training_active(self) -> bool:
        """Check if training is currently active"""
        return self.monitor.is_running and self.process and self.process.poll() is None
    
    def find_output_models(self, output_dir: str) -> list[str]:
        """Find generated LoRa model files in output directory"""
        try:
            output_path = Path(output_dir)
            if not output_path.exists():
                return []
            
            # Look for safetensors files (preferred) and ckpt files
            model_extensions = {'.safetensors', '.ckpt', '.pt'}
            model_files = []
            
            for ext in model_extensions:
                model_files.extend(output_path.glob(f'*{ext}'))
            
            # Sort by modification time (newest first)
            model_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return [str(f) for f in model_files]
            
        except Exception as e:
            print(f"🐢 TORTU LoRa: Error finding output models: {e}")
            return []
