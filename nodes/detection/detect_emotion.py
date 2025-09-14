############################
# detect_emotion.py
############################
# Detect emotions using DeepFace for LoRA training
############################

import numpy as np
import torch
from PIL import Image
import tempfile
import os

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("DeepFace not available. Emotion detection will not work.")

class TORTU_DETECT_EMOTION:
    def __init__(self):
        self.temp_files = []

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
                "face_detected": ("BOOLEAN", {"forceInput": True}),
                "face_center_x": ("FLOAT", {"forceInput": True}),
                "face_center_y": ("FLOAT", {"forceInput": True}),
                # Detection parameters
                "min_confidence": ("FLOAT", {"default": 0.30, "min": 0.1, "max": 1.0, "step": 0.05}),
                "min_margin": ("FLOAT", {"default": 0.15, "min": 0.05, "max": 0.5, "step": 0.05}),
                "enforce_detection": ("BOOLEAN", {"default": False}),
                "model_name": (["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace"], {"default": "VGG-Face"}),
            }
        }

    RETURN_TYPES = (
        "IMAGE",     # Pass-through image
        "STRING",    # Primary emotion
        "FLOAT",     # Primary emotion confidence
        "STRING",    # Secondary emotion
        "FLOAT",     # Secondary emotion confidence
        "BOOLEAN",   # High confidence detection
        "STRING",    # All emotions JSON
        "STRING",    # Filename (pass-through)
        "STRING",    # Relative path (pass-through)
        "STRING",    # Detection status
        "BOOLEAN",   # Face detected (pass-through)
        "FLOAT",     # Face center X (pass-through)
        "FLOAT",     # Face center Y (pass-through)
    )
    
    RETURN_NAMES = (
        "image_batch",
        "primary_emotion",
        "primary_confidence",
        "secondary_emotion", 
        "secondary_confidence",
        "high_confidence",
        "all_emotions",
        "filename",
        "relative_path",
        "status",
        "face_detected",
        "face_center_x",
        "face_center_y"
    )
    
    FUNCTION = "detect_emotion"
    CATEGORY = "🐢 TORTU/Detection"

    def detect_emotion(self, image_batch, **kwargs):
        import json
        
        # Extract optional inputs
        filename = kwargs.get('filename', '')
        relative_path = kwargs.get('relative_path', '')
        source_directory = kwargs.get('source_directory', '')
        face_detected = kwargs.get('face_detected', False)
        face_center_x = kwargs.get('face_center_x', 0.0)
        face_center_y = kwargs.get('face_center_y', 0.0)
        min_confidence = kwargs.get('min_confidence', 0.30)
        min_margin = kwargs.get('min_margin', 0.15)
        enforce_detection = kwargs.get('enforce_detection', False)
        model_name = kwargs.get('model_name', 'VGG-Face')
        
        if not DEEPFACE_AVAILABLE:
            return (
                image_batch, "unknown", 0.0, "unknown", 0.0, False,
                '{"error": "DeepFace not available"}', filename, relative_path,
                "deepface_unavailable", face_detected, face_center_x, face_center_y
            )
        
        try:
            # Convert ComfyUI tensor to PIL Image and save temporarily
            if isinstance(image_batch, torch.Tensor):
                img_np = image_batch[0].cpu().numpy()
            else:
                img_np = image_batch[0] if len(image_batch.shape) == 4 else image_batch
            
            # Convert from [0,1] to [0,255] and to uint8
            img_np = (img_np * 255).clip(0, 255).astype(np.uint8)
            img_pil = Image.fromarray(img_np, mode="RGB")
            
            # Save to temporary file (DeepFace requires file path)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                temp_path = tmp_file.name
                img_pil.save(temp_path, 'JPEG')
                self.temp_files.append(temp_path)
            
            # Perform emotion analysis
            result = DeepFace.analyze(
                img_path=temp_path, 
                actions=['emotion'], 
                enforce_detection=enforce_detection,
                model_name=model_name,
                silent=True
            )
            
            # Extract emotions from result
            if isinstance(result, list):
                emotions = result[0]['emotion']
            else:
                emotions = result['emotion']
                
            # Sort emotions by confidence
            sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
            
            primary_emotion, primary_score = sorted_emotions[0]
            secondary_emotion, secondary_score = sorted_emotions[1] if len(sorted_emotions) > 1 else ("none", 0.0)
            
            # Normalize scores if they're percentages (> 1)
            if primary_score > 1:
                primary_score /= 100
                secondary_score /= 100
            
            # Determine if this is a high confidence detection
            confidence_margin = primary_score - secondary_score
            high_confidence = (primary_score >= min_confidence) and (confidence_margin >= min_margin)
            
            # Create detailed emotion data
            normalized_emotions = {}
            for emotion, score in emotions.items():
                normalized_emotions[emotion] = float(score / 100 if score > 1 else score)
            
            emotion_data = {
                "primary_emotion": primary_emotion.lower(),
                "primary_confidence": float(primary_score),
                "secondary_emotion": secondary_emotion.lower(),
                "secondary_confidence": float(secondary_score),
                "confidence_margin": float(confidence_margin),
                "high_confidence": high_confidence,
                "all_emotions": normalized_emotions,
                "detection_params": {
                    "min_confidence": min_confidence,
                    "min_margin": min_margin,
                    "model_name": model_name,
                    "enforce_detection": enforce_detection
                },
                "filename": filename,
                "relative_path": relative_path,
                "source_directory": source_directory
            }
            
            status = f"Detected: {primary_emotion.lower()} ({primary_score:.2f})"
            if not high_confidence:
                status += f" [LOW CONFIDENCE vs {secondary_emotion.lower()} ({secondary_score:.2f})]"
            
            return (
                image_batch, 
                primary_emotion.lower(), 
                float(primary_score),
                secondary_emotion.lower(),
                float(secondary_score),
                high_confidence,
                json.dumps(emotion_data, indent=2),
                filename,
                relative_path,
                status,
                face_detected,
                face_center_x,
                face_center_y
            )
            
        except Exception as e:
            print(f"🐢 TORTU: Error in emotion detection: {e}")
            return (
                image_batch, "error", 0.0, "error", 0.0, False,
                f'{{"error": "{str(e)}"}}', filename, relative_path,
                f"Detection error: {str(e)}", face_detected, face_center_x, face_center_y
            )
        
        finally:
            # Clean up temporary files
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
            self.temp_files.clear()

    def __del__(self):
        # Cleanup on destruction
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass

NODE_CLASS_MAPPINGS = {
    "TORTU_DETECT_EMOTION": TORTU_DETECT_EMOTION
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TORTU_DETECT_EMOTION": "🐢 Detect Emotion"
}