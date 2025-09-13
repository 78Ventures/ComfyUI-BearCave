############################
# bc_face_detection.py
############################
# Detect face orientation using MediaPipe
############################

import cv2
import numpy as np
import torch

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("MediaPipe not available. BearDetectFaceOrientation will not work.")

class BC_DETECT_FACE_ORIENTATION:
    def __init__(self):
        if MEDIAPIPE_AVAILABLE:
            self.face_detection = mp.solutions.face_detection.FaceDetection(
                model_selection=1, 
                min_detection_confidence=0.5
            )
        else:
            self.face_detection = None

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
                "detection_confidence": ("FLOAT", {"default": 0.5, "min": 0.1, "max": 1.0, "step": 0.1}),
                "model_selection": ("INT", {"default": 1, "min": 0, "max": 1, "step": 1}),
            }
        }

    RETURN_TYPES = (
        "IMAGE",     # Pass-through image
        "FLOAT",     # Detection confidence
        "STRING",    # Detailed results JSON
        "FLOAT",     # Face center X
        "FLOAT",     # Face center Y
        "INT",       # Number of faces detected
        "BOOLEAN",   # Face detected
        "FLOAT",     # Face height
        "STRING",    # Face pose
        "FLOAT",     # Face width
        "STRING",    # Filename (pass-through)
        "STRING",    # Relative path (pass-through)
        "STRING",    # Detection status
    )
    
    RETURN_NAMES = (
        "image_batch",
        "confidence",
        "detection_data",
        "face_center_x",
        "face_center_y",
        "face_count",
        "face_detected",
        "face_height",
        "face_pose",
        "face_width",
        "filename",
        "relative_path",
        "status"
    )
    
    FUNCTION = "detect_face_orientation"
    CATEGORY = "🐢 TORTU/Detection"

    def detect_face_orientation(self, image_batch, **kwargs):
        import json
        
        # Extract optional inputs
        filename = kwargs.get('filename', '')
        relative_path = kwargs.get('relative_path', '')
        source_directory = kwargs.get('source_directory', '')
        detection_confidence = kwargs.get('detection_confidence', 0.5)
        model_selection = kwargs.get('model_selection', 1)
        
        # Update detection settings if different
        if MEDIAPIPE_AVAILABLE and (
            self.face_detection.min_detection_confidence != detection_confidence or 
            model_selection != 1  # Current default
        ):
            self.face_detection = mp.solutions.face_detection.FaceDetection(
                model_selection=model_selection,
                min_detection_confidence=detection_confidence
            )
        
        if not MEDIAPIPE_AVAILABLE or self.face_detection is None:
            return (
                image_batch, "mediapipe_unavailable", 0.0, 0, False, 
                "MediaPipe not available", 0.0, 0.0, 0.0, 0.0,
                '{"error": "MediaPipe not available"}', filename, relative_path
            )
        
        try:
            # Convert ComfyUI tensor to numpy array
            if isinstance(image_batch, torch.Tensor):
                image_np = image_batch[0].cpu().numpy()
            else:
                image_np = image_batch[0] if len(image_batch.shape) == 4 else image_batch
            
            # Convert from [0,1] to [0,255] and to uint8
            image_np = (image_np * 255).astype(np.uint8)
            
            # MediaPipe expects RGB format
            results = self.face_detection.process(image_np)
            
            # Initialize return values
            pose = "unknown"
            confidence = 0.0
            face_count = 0
            face_detected = False
            status = "No faces detected"
            face_center_x = 0.0
            face_center_y = 0.0
            face_width = 0.0
            face_height = 0.0
            detection_data = {}

            if results.detections:
                face_count = len(results.detections)
                face_detected = True
                status = f"Detected {face_count} face(s)"
                
                # Process first detection (main face)
                detection = results.detections[0]
                confidence = detection.score[0] if detection.score else 0.0
                
                # Get bounding box
                bbox = detection.location_data.relative_bounding_box
                face_center_x = bbox.xmin + bbox.width / 2
                face_center_y = bbox.ymin + bbox.height / 2
                face_width = bbox.width
                face_height = bbox.height
                
                # Estimate pose using keypoints if available
                if hasattr(detection.location_data, 'relative_keypoints') and detection.location_data.relative_keypoints:
                    keypoints = detection.location_data.relative_keypoints
                    
                    if len(keypoints) >= 2:
                        left_eye = keypoints[0]
                        right_eye = keypoints[1]
                        
                        eye_dx = right_eye.x - left_eye.x
                        if eye_dx > 0.07:
                            pose = "left_profile"
                        elif eye_dx < -0.07:
                            pose = "right_profile"
                        else:
                            pose = "frontal"
                        
                        # Create detailed detection data
                        detection_data = {
                            "pose": pose,
                            "confidence": float(confidence),
                            "face_count": face_count,
                            "bounding_box": {
                                "x": float(bbox.xmin),
                                "y": float(bbox.ymin),
                                "width": float(bbox.width),
                                "height": float(bbox.height)
                            },
                            "face_center": {
                                "x": float(face_center_x),
                                "y": float(face_center_y)
                            },
                            "keypoints": [
                                {"x": float(kp.x), "y": float(kp.y)} for kp in keypoints
                            ],
                            "eye_distance": float(abs(eye_dx)),
                            "filename": filename,
                            "relative_path": relative_path,
                            "source_directory": source_directory
                        }
                    else:
                        pose = "face_detected_no_keypoints"
                        detection_data = {
                            "pose": pose,
                            "confidence": float(confidence),
                            "face_count": face_count,
                            "bounding_box": {
                                "x": float(bbox.xmin),
                                "y": float(bbox.ymin),
                                "width": float(bbox.width),
                                "height": float(bbox.height)
                            },
                            "face_center": {
                                "x": float(face_center_x),
                                "y": float(face_center_y)
                            },
                            "status": "No keypoints available"
                        }
                else:
                    pose = "face_detected"
                    detection_data = {
                        "pose": pose,
                        "confidence": float(confidence),
                        "face_count": face_count,
                        "bounding_box": {
                            "x": float(bbox.xmin),
                            "y": float(bbox.ymin),
                            "width": float(bbox.width),
                            "height": float(bbox.height)
                        },
                        "status": "Basic detection only"
                    }

        except Exception as e:
            print(f"🐢 TORTU: Error in face detection: {e}")
            return (
                image_batch, "error", 0.0, 0, False, f"Detection error: {str(e)}",
                0.0, 0.0, 0.0, 0.0, f'{{"error": "{str(e)}"}}', filename, relative_path
            )

        return (
            image_batch, pose, confidence, face_count, face_detected, status,
            face_center_x, face_center_y, face_width, face_height,
            json.dumps(detection_data, indent=2), filename, relative_path
        )


NODE_CLASS_MAPPINGS = {
    "BC_DETECT_FACE_ORIENTATION": BC_DETECT_FACE_ORIENTATION,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BC_DETECT_FACE_ORIENTATION": "🐢 Face Orientation",
}