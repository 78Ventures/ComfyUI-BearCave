# bear_nodes_batch.py - Comprehensive connection points
############################
import os
import folder_paths
import numpy as np
import torch
from PIL import Image
from pathlib import Path

try:
    from comfy.utils import ProgressBar
except ImportError:
    class ProgressBar:
        def __init__(self, total):
            self.total = total
            self.current = 0
        def update(self, n=1):
            self.current += n

def get_all_directories():
    """Get comprehensive list of available directories"""
    directories = []
    
    try:
        directories.extend(["input", "output"])
        
        input_dir = folder_paths.get_input_directory()
        if os.path.exists(input_dir):
            for root, dirs, files in os.walk(input_dir):
                for dir_name in sorted(dirs):
                    rel_path = os.path.relpath(os.path.join(root, dir_name), input_dir)
                    directories.append(f"input/{rel_path}")
        
        output_dir = folder_paths.get_output_directory()
        if os.path.exists(output_dir):
            for root, dirs, files in os.walk(output_dir):
                for dir_name in sorted(dirs):
                    rel_path = os.path.relpath(os.path.join(root, dir_name), output_dir)
                    directories.append(f"output/{rel_path}")
                    
        home_dir = str(Path.home())
        directories.extend([
            f"CUSTOM_PATH|{home_dir}/Desktop",
            f"CUSTOM_PATH|{home_dir}/Documents", 
            f"CUSTOM_PATH|{home_dir}/Downloads",
        ])
        
    except Exception as e:
        print(f"Error scanning directories: {e}")
        directories = ["input", "output"]
    
    return directories

class BearBatchLoader:
    """
    Comprehensive batch image loader with extensive connection points
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source_directory": (get_all_directories(), {"default": "input"}),
                "custom_path": ("STRING", {"default": "", "placeholder": "Or enter custom path"}),
                "recursive": ("BOOLEAN", {"default": True}),
                "file_filter": (["all", "png", "jpg", "jpeg", "bmp", "tiff", "webp"], {"default": "all"}),
                "max_images": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
                "sort_order": (["name_asc", "name_desc", "date_asc", "date_desc", "size_asc", "size_desc"], {"default": "name_asc"}),
                "skip_count": ("INT", {"default": 0, "min": 0, "max": 1000, "step": 1}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1}),
            },
            "optional": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "override_width": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 8}),
                "override_height": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 8}),
            }
        }

    RETURN_TYPES = (
        "IMAGE",        # Primary images
        "STRING",       # Filenames  
        "STRING",       # Relative paths
        "STRING",       # Full file paths
        "STRING",       # File extensions
        "STRING",       # Source directory
        "INT",          # Image widths
        "INT",          # Image heights
        "INT",          # File sizes
        "STRING",       # Creation dates
        "INT",          # Total count
        "INT",          # Current batch
        "BOOLEAN",      # Has more batches
        "STRING",       # Status message
    )
    
    RETURN_NAMES = (
        "images",
        "filenames", 
        "relative_paths",
        "full_paths",
        "extensions",
        "source_directory",
        "widths",
        "heights", 
        "file_sizes",
        "creation_dates",
        "total_count",
        "current_batch",
        "has_more",
        "status"
    )
    
    FUNCTION = "load_images"
    CATEGORY = "🐻 Bear Cave/Batch"
    OUTPUT_IS_LIST = (True, True, True, True, True, False, True, True, True, True, False, False, False, False)

    def load_images(self, source_directory, custom_path, recursive, file_filter, max_images, sort_order, skip_count, batch_size, seed=0, override_width=0, override_height=0):
        from datetime import datetime
        
        # Resolve directory path
        source_path = self._resolve_directory_path(source_directory, custom_path)
        
        if not source_path or not Path(source_path).exists():
            return self._empty_return(f"Directory not found: {source_path}")

        source_dir = Path(source_path)
        
        # Collect all files
        extensions = self._get_file_extensions(file_filter)
        all_files = []
        
        for ext in extensions:
            if recursive:
                all_files.extend(source_dir.rglob(ext))
            else:
                all_files.extend(source_dir.glob(ext))

        if not all_files:
            return self._empty_return(f"No {file_filter} images found")

        # Sort files
        all_files = self._sort_files(all_files, sort_order)
        
        # Apply skip and limit
        if skip_count > 0:
            all_files = all_files[skip_count:]
        if max_images > 0:
            all_files = all_files[:max_images]
            
        if not all_files:
            return self._empty_return("No files after filtering")

        # Process files
        images, filenames, relative_paths, full_paths, extensions_out = [], [], [], [], []
        widths, heights, file_sizes, creation_dates = [], [], [], []
        
        print(f"🐻 Bear Cave: Loading {len(all_files)} images from {source_dir}")
        pbar = ProgressBar(len(all_files))

        for file_path in all_files:
            try:
                # Load image
                img = Image.open(file_path)
                original_size = img.size
                
                # Apply size overrides if specified
                if override_width > 0 or override_height > 0:
                    new_width = override_width if override_width > 0 else original_size[0]
                    new_height = override_height if override_height > 0 else original_size[1]
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                
                img = img.convert("RGB")
                img_np = np.array(img).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_np).unsqueeze(0)

                # Collect data
                images.append(img_tensor)
                filenames.append(file_path.stem)
                relative_paths.append(str(file_path.relative_to(source_dir).parent))
                full_paths.append(str(file_path))
                extensions_out.append(file_path.suffix.lower())
                widths.append(img.size[0])
                heights.append(img.size[1])
                
                # File metadata
                stat = file_path.stat()
                file_sizes.append(int(stat.st_size))
                creation_dates.append(datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"))
                
            except Exception as e:
                print(f"🐻 Bear Cave: Error loading {file_path}: {e}")
                continue
                
            pbar.update(1)

        total_loaded = len(images)
        current_batch = 1
        has_more = False  # This implementation loads all at once
        status = f"Loaded {total_loaded} images successfully"
        
        print(f"🐻 Bear Cave: {status}")
        
        return (
            images, filenames, relative_paths, full_paths, extensions_out,
            str(source_dir), widths, heights, file_sizes, creation_dates,
            total_loaded, current_batch, has_more, status
        )

    def _empty_return(self, message):
        """Return empty results with error message"""
        return ([], [], [], [], [], "", [], [], [], [], 0, 0, False, message)

    def _resolve_directory_path(self, directory_selection, custom_path):
        """Resolve the actual directory path from selection"""
        if custom_path.strip():
            return custom_path.strip()
            
        if directory_selection.startswith("CUSTOM_PATH|"):
            return directory_selection.split("|", 1)[1]
            
        if directory_selection.startswith("input"):
            base_dir = folder_paths.get_input_directory()
            relative = directory_selection.replace("input", "").lstrip("/\\")
            return str(Path(base_dir) / relative) if relative else base_dir
        elif directory_selection.startswith("output"):
            base_dir = folder_paths.get_output_directory() 
            relative = directory_selection.replace("output", "").lstrip("/\\")
            return str(Path(base_dir) / relative) if relative else base_dir
        else:
            return directory_selection

    def _get_file_extensions(self, file_filter):
        """Get file extensions based on filter"""
        filter_map = {
            "png": ["*.png", "*.PNG"],
            "jpg": ["*.jpg", "*.JPG"],
            "jpeg": ["*.jpeg", "*.JPEG"],
            "bmp": ["*.bmp", "*.BMP"],
            "tiff": ["*.tiff", "*.TIFF", "*.tif", "*.TIF"],
            "webp": ["*.webp", "*.WEBP"]
        }
        
        if file_filter == "all":
            extensions = []
            for ext_list in filter_map.values():
                extensions.extend(ext_list)
            return extensions
        else:
            return filter_map.get(file_filter, ["*.png"])

    def _sort_files(self, files, sort_order):
        """Sort files according to specified order"""
        if sort_order == "name_asc":
            return sorted(files, key=lambda x: x.name.lower())
        elif sort_order == "name_desc":
            return sorted(files, key=lambda x: x.name.lower(), reverse=True)
        elif sort_order == "date_asc":
            return sorted(files, key=lambda x: x.stat().st_mtime)
        elif sort_order == "date_desc":
            return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
        elif sort_order == "size_asc":
            return sorted(files, key=lambda x: x.stat().st_size)
        elif sort_order == "size_desc":
            return sorted(files, key=lambda x: x.stat().st_size, reverse=True)
        else:
            return sorted(files, key=lambda x: x.name.lower())


class BearSaveBatch:
    """
    Comprehensive batch image saver with extensive connection points
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filenames": ("STRING",),
                "relative_paths": ("STRING",),
                "output_directory": (get_all_directories(), {"default": "output"}),
                "custom_output_path": ("STRING", {"default": ""}),
                "subfolder_name": ("STRING", {"default": "processed"}),
                "file_extension": (["png", "jpg", "jpeg", "bmp", "tiff", "webp"], {"default": "png"}),
                "preserve_structure": ("BOOLEAN", {"default": True}),
                "add_timestamp": ("BOOLEAN", {"default": False}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "optimize": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "source_directory": ("STRING", {"forceInput": True}),
                "full_paths": ("STRING", {"forceInput": True}),
                "extensions": ("STRING", {"forceInput": True}),
                "widths": ("INT", {"forceInput": True}),
                "heights": ("INT", {"forceInput": True}),
                "file_sizes": ("INT", {"forceInput": True}),
                "creation_dates": ("STRING", {"forceInput": True}),
                "prefix": ("STRING", {"default": ""}),
                "suffix": ("STRING", {"default": ""}),
                "start_index": ("INT", {"default": 0, "min": 0, "max": 9999}),
            }
        }

    RETURN_TYPES = (
        "STRING",    # Output directory
        "STRING",    # Saved filenames
        "STRING",    # Saved relative paths  
        "STRING",    # Full saved paths
        "STRING",    # Final extensions used
        "INT",       # Saved count
        "INT",       # Failed count
        "STRING",    # Success filenames
        "STRING",    # Failed filenames
        "STRING",    # Status message
        "BOOLEAN",   # All successful
        "INT",       # Total file size
        "STRING",    # Save timestamp
    )
    
    RETURN_NAMES = (
        "output_directory",
        "saved_filenames", 
        "saved_relative_paths",
        "saved_full_paths",
        "saved_extensions",
        "saved_count",
        "failed_count", 
        "success_files",
        "failed_files",
        "status",
        "all_successful",
        "total_size",
        "save_timestamp"
    )
    
    FUNCTION = "save_images"
    CATEGORY = "🐻 Bear Cave/Batch"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (False, True, True, True, True, False, False, True, True, False, False, False, False)

    def save_images(self, images, filenames, relative_paths, output_directory, custom_output_path, subfolder_name, file_extension, preserve_structure, add_timestamp, quality, optimize, **kwargs):
        from datetime import datetime
        
        # Extract optional inputs
        source_directory = kwargs.get('source_directory', '')
        full_paths = kwargs.get('full_paths', [])
        extensions = kwargs.get('extensions', [])
        widths = kwargs.get('widths', [])
        heights = kwargs.get('heights', [])
        file_sizes = kwargs.get('file_sizes', [])
        creation_dates = kwargs.get('creation_dates', [])
        prefix = kwargs.get('prefix', '')
        suffix = kwargs.get('suffix', '')
        start_index = kwargs.get('start_index', 0)
        
        # Resolve output path
        loader_instance = BearBatchLoader()
        output_path = loader_instance._resolve_directory_path(output_directory, custom_output_path)
        
        if not output_path:
            output_path = folder_paths.get_output_directory()
            
        output_base = Path(output_path)
        
        # Add subfolder with timestamp if requested
        if subfolder_name.strip():
            subfolder = subfolder_name.strip()
            if add_timestamp:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                subfolder = f"{subfolder}_{timestamp}"
            output_base = output_base / subfolder

        # Ensure inputs are lists
        if not isinstance(images, list):
            images = [images]
        if not isinstance(filenames, list):
            filenames = [filenames] 
        if not isinstance(relative_paths, list):
            relative_paths = [relative_paths]

        # Initialize tracking
        saved_filenames, saved_relative_paths, saved_full_paths, saved_extensions = [], [], [], []
        success_files, failed_files = [], []
        saved_count, failed_count = 0, 0
        total_size = 0
        save_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for i, (img, fname, rel_path) in enumerate(zip(images, filenames, relative_paths)):
            try:
                # Determine final directory
                if preserve_structure and rel_path and rel_path != ".":
                    final_dir = output_base / rel_path
                else:
                    final_dir = output_base
                    
                final_dir.mkdir(parents=True, exist_ok=True)
                
                # Create filename with prefix/suffix/index
                final_filename = fname
                if prefix:
                    final_filename = f"{prefix}{final_filename}"
                if suffix:
                    final_filename = f"{final_filename}{suffix}"
                if start_index > 0:
                    final_filename = f"{final_filename}_{start_index + i:04d}"
                
                save_path = final_dir / f"{final_filename}.{file_extension}"
                
                # Handle filename conflicts
                counter = 1
                original_save_path = save_path
                while save_path.exists():
                    stem = original_save_path.stem
                    suffix_ext = original_save_path.suffix
                    save_path = original_save_path.parent / f"{stem}_{counter:03d}{suffix_ext}"
                    counter += 1

                # Convert tensor to PIL and save
                if isinstance(img, torch.Tensor):
                    img_np = img[0].cpu().numpy()
                else:
                    img_np = img[0] if len(img.shape) == 4 else img
                
                img_np = (img_np * 255).clip(0, 255).astype(np.uint8)
                img_pil = Image.fromarray(img_np)
                
                # Save with appropriate options
                save_kwargs = {}
                if file_extension.lower() in ['jpg', 'jpeg']:
                    save_kwargs.update({'quality': quality, 'optimize': optimize})
                elif file_extension.lower() == 'png':
                    save_kwargs.update({'optimize': optimize})
                
                img_pil.save(save_path, **save_kwargs)
                
                # Track success
                saved_count += 1
                saved_filenames.append(save_path.stem)
                saved_relative_paths.append(str(save_path.relative_to(output_base).parent))
                saved_full_paths.append(str(save_path))
                saved_extensions.append(file_extension)
                success_files.append(fname)
                total_size += save_path.stat().st_size
                
            except Exception as e:
                print(f"🐻 Bear Cave: Error saving {fname}: {e}")
                failed_count += 1
                failed_files.append(fname)
                continue

        # Create status
        all_successful = failed_count == 0
        status = f"Saved {saved_count}/{saved_count + failed_count} images"
        if failed_count > 0:
            status += f" ({failed_count} failed)"
        
        print(f"🐻 Bear Cave: {status} to {output_base}")
        
        return (
            str(output_base), saved_filenames, saved_relative_paths, saved_full_paths,
            saved_extensions, saved_count, failed_count, success_files, failed_files,
            status, all_successful, total_size, save_timestamp
        )

NODE_CLASS_MAPPINGS = {
    "BearBatchLoader": BearBatchLoader,
    "BearSaveBatch": BearSaveBatch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BearBatchLoader": "🐻 Batch Load",
    "BearSaveBatch": "🐻 Batch Save",
}