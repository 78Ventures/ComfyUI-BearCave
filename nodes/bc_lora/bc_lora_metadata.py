############################
# bc_lora_metadata.py
############################
# Kohya-ss specific metadata handling and caption generation
############################

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

class BC_LORA_METADATA:
    """Generate kohya-ss compatible captions and metadata for LoRa training"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "conform_path": ("STRING", {"forceInput": True}),
                "trigger_words": ("STRING", {"default": ""}),
                "base_caption": ("STRING", {"default": "photo of"}),
                "caption_style": (["simple", "detailed", "tags"], {"default": "simple"}),
            },
            "optional": {
                # Connection points from other nodes
                "project_metadata": ("STRING", {"forceInput": True}),
                "image_list": ("STRING", {"forceInput": True}),
                "face_data": ("STRING", {"forceInput": True}),
                "face_count": ("INT", {"forceInput": True}),
                "detection_status": ("STRING", {"forceInput": True}),
                # Caption customization
                "include_quality_tags": ("BOOLEAN", {"default": True}),
                "include_style_tags": ("BOOLEAN", {"default": True}),
                "custom_tags": ("STRING", {"default": "", "multiline": True}),
                "caption_prefix": ("STRING", {"default": ""}),
                "caption_suffix": ("STRING", {"default": ""}),
                # Processing options
                "overwrite_existing": ("BOOLEAN", {"default": False}),
                "create_backup": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = (
        "STRING",    # Caption files created count
        "STRING",    # Metadata JSON
        "STRING",    # Processing log
        "BOOLEAN",   # Success status
        "STRING",    # Status message
        "STRING",    # Caption files list (JSON)
    )
    
    RETURN_NAMES = (
        "caption_count",
        "metadata_json",
        "processing_log",
        "success",
        "status_message",
        "caption_files"
    )
    
    FUNCTION = "generate_captions"
    CATEGORY = "🐻 Bear Cave/LoRa"

    def generate_captions(self, conform_path, trigger_words, base_caption, caption_style, **kwargs):
        try:
            # Extract optional parameters
            project_metadata = kwargs.get('project_metadata', '{}')
            image_list = kwargs.get('image_list', '[]')
            face_data = kwargs.get('face_data', '{}')
            include_quality_tags = kwargs.get('include_quality_tags', True)
            include_style_tags = kwargs.get('include_style_tags', True)
            custom_tags = kwargs.get('custom_tags', '')
            caption_prefix = kwargs.get('caption_prefix', '')
            caption_suffix = kwargs.get('caption_suffix', '')
            overwrite_existing = kwargs.get('overwrite_existing', False)
            create_backup = kwargs.get('create_backup', True)
            
            # Parse input data
            try:
                project_meta = json.loads(project_metadata) if project_metadata != '{}' else {}
                images = json.loads(image_list) if image_list != '[]' else []
                face_info = json.loads(face_data) if face_data != '{}' else {}
            except json.JSONDecodeError as e:
                return self._error_return(f"Invalid JSON input: {e}")
            
            # Validate conform path
            conform_dir = Path(conform_path)
            if not conform_dir.exists():
                return self._error_return(f"Conform directory does not exist: {conform_path}")
            
            # Find images if not provided
            if not images:
                images = self._find_training_images(conform_dir)
            
            if not images:
                return self._error_return("No training images found in conform directory")
            
            # Generate captions for each image
            processing_log = []
            caption_files = []
            created_count = 0
            
            for image_path in images:
                try:
                    success, caption_file, log_entry = self._process_image_caption(
                        image_path, conform_dir, trigger_words, base_caption,
                        caption_style, include_quality_tags, include_style_tags,
                        custom_tags, caption_prefix, caption_suffix,
                        overwrite_existing, create_backup, face_info
                    )
                    
                    processing_log.append(log_entry)
                    
                    if success:
                        caption_files.append(caption_file)
                        created_count += 1
                        
                except Exception as e:
                    processing_log.append(f"Error processing {image_path}: {e}")
            
            # Create metadata summary
            metadata = {
                "caption_generation": {
                    "trigger_words": trigger_words,
                    "base_caption": base_caption,
                    "caption_style": caption_style,
                    "total_images": len(images),
                    "captions_created": created_count,
                    "include_quality_tags": include_quality_tags,
                    "include_style_tags": include_style_tags,
                    "custom_tags": custom_tags.split(',') if custom_tags else [],
                    "processing_timestamp": self._get_timestamp()
                },
                "files_processed": caption_files
            }
            
            # Save metadata file
            metadata_file = conform_dir / "caption_metadata.json"
            try:
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                processing_log.append(f"Saved metadata to {metadata_file}")
            except Exception as e:
                processing_log.append(f"Warning: Could not save metadata file: {e}")
            
            # Success return
            status_message = f"Generated {created_count} caption files for LoRa training"
            processing_log_str = "\n".join(processing_log)
            
            return (
                str(created_count),
                json.dumps(metadata, indent=2),
                processing_log_str,
                True,
                status_message,
                json.dumps(caption_files)
            )
            
        except Exception as e:
            print(f"🐻 Bear Cave LoRa: Error in generate_captions: {e}")
            return self._error_return(f"Caption generation failed: {str(e)}")
    
    def _find_training_images(self, conform_dir: Path) -> List[str]:
        """Find training images in conform directory"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
        images = []
        
        for ext in image_extensions:
            images.extend([str(f) for f in conform_dir.glob(f'*{ext}')])
            images.extend([str(f) for f in conform_dir.glob(f'*{ext.upper()}')])
        
        return sorted(images)
    
    def _process_image_caption(self, image_path: str, conform_dir: Path, 
                              trigger_words: str, base_caption: str, caption_style: str,
                              include_quality_tags: bool, include_style_tags: bool,
                              custom_tags: str, caption_prefix: str, caption_suffix: str,
                              overwrite_existing: bool, create_backup: bool,
                              face_info: Dict) -> Tuple[bool, str, str]:
        """Process caption for a single image"""
        try:
            image_file = Path(image_path)
            caption_file = image_file.with_suffix('.txt')
            
            # Check if caption already exists
            if caption_file.exists() and not overwrite_existing:
                return False, str(caption_file), f"Caption already exists: {caption_file.name}"
            
            # Create backup if requested
            if caption_file.exists() and create_backup:
                backup_file = caption_file.with_suffix('.txt.bak')
                try:
                    backup_file.write_text(caption_file.read_text(encoding='utf-8'), encoding='utf-8')
                except Exception as e:
                    print(f"🐻 Bear Cave LoRa: Warning - could not create backup: {e}")
            
            # Generate caption based on style
            caption = self._generate_caption_content(
                image_file.stem, trigger_words, base_caption, caption_style,
                include_quality_tags, include_style_tags, custom_tags,
                caption_prefix, caption_suffix, face_info
            )
            
            # Write caption file
            caption_file.write_text(caption, encoding='utf-8')
            
            return True, str(caption_file), f"Created caption: {caption_file.name}"
            
        except Exception as e:
            return False, "", f"Failed to process {image_path}: {e}"
    
    def _generate_caption_content(self, image_name: str, trigger_words: str,
                                 base_caption: str, caption_style: str,
                                 include_quality_tags: bool, include_style_tags: bool,
                                 custom_tags: str, caption_prefix: str, caption_suffix: str,
                                 face_info: Dict) -> str:
        """Generate the actual caption content"""
        caption_parts = []
        
        # Add prefix if provided
        if caption_prefix:
            caption_parts.append(caption_prefix.strip())
        
        # Build main caption based on style
        if caption_style == "simple":
            main_caption = self._generate_simple_caption(trigger_words, base_caption)
        elif caption_style == "detailed":
            main_caption = self._generate_detailed_caption(trigger_words, base_caption, image_name, face_info)
        elif caption_style == "tags":
            main_caption = self._generate_tag_caption(trigger_words, base_caption)
        else:
            main_caption = f"{trigger_words}, {base_caption}" if trigger_words else base_caption
        
        caption_parts.append(main_caption)
        
        # Add quality tags
        if include_quality_tags:
            quality_tags = self._get_quality_tags()
            caption_parts.extend(quality_tags)
        
        # Add style tags
        if include_style_tags:
            style_tags = self._get_style_tags()
            caption_parts.extend(style_tags)
        
        # Add custom tags
        if custom_tags:
            custom_tag_list = [tag.strip() for tag in custom_tags.split(',') if tag.strip()]
            caption_parts.extend(custom_tag_list)
        
        # Add suffix if provided
        if caption_suffix:
            caption_parts.append(caption_suffix.strip())
        
        # Join with commas and clean up
        caption = ', '.join(caption_parts)
        caption = self._clean_caption(caption)
        
        return caption
    
    def _generate_simple_caption(self, trigger_words: str, base_caption: str) -> str:
        """Generate simple caption format"""
        if trigger_words:
            return f"{trigger_words}, {base_caption}"
        return base_caption
    
    def _generate_detailed_caption(self, trigger_words: str, base_caption: str, 
                                  image_name: str, face_info: Dict) -> str:
        """Generate detailed caption with context"""
        parts = []
        
        if trigger_words:
            parts.append(trigger_words)
        
        # Add base description
        parts.append(base_caption)
        
        # Add face-related descriptions if available
        if face_info and image_name in face_info:
            face_data = face_info[image_name]
            if face_data.get('face_detected', False):
                parts.append("portrait")
                
                # Add pose information if available
                if 'pose' in face_data:
                    pose = face_data['pose']
                    if pose in ['front', 'center']:
                        parts.append("looking at camera")
                    elif pose in ['left', 'right']:
                        parts.append(f"looking {pose}")
        
        return ', '.join(parts)
    
    def _generate_tag_caption(self, trigger_words: str, base_caption: str) -> str:
        """Generate tag-style caption"""
        tags = []
        
        if trigger_words:
            # Split trigger words into individual tags
            trigger_tags = [tag.strip() for tag in trigger_words.split(',') if tag.strip()]
            tags.extend(trigger_tags)
        
        # Add base caption as tags
        base_tags = [tag.strip() for tag in base_caption.split(',') if tag.strip()]
        tags.extend(base_tags)
        
        return ', '.join(tags)
    
    def _get_quality_tags(self) -> List[str]:
        """Get quality-related tags"""
        return [
            "high quality",
            "detailed",
            "sharp focus"
        ]
    
    def _get_style_tags(self) -> List[str]:
        """Get style-related tags"""
        return [
            "professional photo",
            "studio lighting"
        ]
    
    def _clean_caption(self, caption: str) -> str:
        """Clean up caption formatting"""
        # Remove extra spaces and normalize commas
        caption = ', '.join([part.strip() for part in caption.split(',') if part.strip()])
        
        # Remove duplicate consecutive words
        words = caption.split(', ')
        cleaned_words = []
        for word in words:
            if not cleaned_words or word != cleaned_words[-1]:
                cleaned_words.append(word)
        
        return ', '.join(cleaned_words)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _error_return(self, message: str):
        """Return error state"""
        return ("0", "{}", message, False, message, "[]")

# Node registration
NODE_CLASS_MAPPINGS = {
    "BC_LORA_METADATA": BC_LORA_METADATA
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BC_LORA_METADATA": "🐻 Generate LoRa Captions"
}
