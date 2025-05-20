"""
Dataset Processor Module.

This module handles dataset processing, augmentation, and preparation for studio use.
"""

import os
import shutil
import zipfile
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Union
import numpy as np
from PIL import Image

try:
    import imgaug.augmenters as iaa
except ImportError:
    print("Warning: imgaug not installed. To use image augmentation, install with: pip install imgaug")

# Default canvas size for final images
DEFAULT_CANVAS_SIZE = (640, 480)


class DatasetProcessor:
    """
    Handles dataset processing, augmentation, and preparation for studio use.
    """
    
    def __init__(self, canvas_size: Tuple[int, int] = DEFAULT_CANVAS_SIZE):
        """
        Initialize the dataset processor.
        
        Args:
            canvas_size: Target size for processed images (width, height).
        """
        self.canvas_size = canvas_size
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required dependencies are installed."""
        try:
            import imgaug
            self.imgaug_available = True
        except ImportError:
            self.imgaug_available = False
    
    def create_augmented_dataset(
        self, 
        source_dir: Union[str, Path], 
        output_file: Union[str, Path], 
        num_images: int = 100,
        temp_dir: str = 'temp_cam0'
    ) -> None:
        """
        Create an augmented dataset from source images and package as a ZIP file.
        
        Args:
            source_dir: Directory containing source images.
            output_file: Path to the output ZIP file.
            num_images: Number of augmented images to generate.
            temp_dir: Temporary directory for processing.
        
        Raises:
            RuntimeError: If imgaug is not available.
        """
        if not self.imgaug_available:
            raise RuntimeError(
                "imgaug is required for image augmentation. "
                "Please install it with: pip install imgaug"
            )
        
        import imgaug.augmenters as iaa
        
        # Convert paths to Path objects
        source_dir = Path(source_dir)
        output_file = Path(output_file)
        temp_dir = Path(temp_dir)
        cam0_dir = temp_dir / 'Cam0'
        
        # Clean up temp directory if it exists
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        cam0_dir.mkdir(parents=True, exist_ok=True)
        
        # Find source images
        image_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        image_paths = sorted([
            p for p in source_dir.iterdir() 
            if p.suffix.lower() in image_exts
        ])
        total_src = len(image_paths)
        
        print(f"Found {total_src} images in '{source_dir}'")
        if total_src == 0:
            print("No images to process. Exiting.")
            return
        
        # Load images into memory
        print("Loading images into memory...")
        images = []
        for path in image_paths:
            with Image.open(path) as img:
                img = img.convert('RGB')
                images.append(np.array(img))
        print(f"Loaded {len(images)} images")
        
        # Define augmentation pipeline
        seq = iaa.Sequential([
            iaa.Affine(rotate=(-15, 15)),  # random rotation between -15 and 15 degrees
            iaa.CropAndPad(percent=(-0.05, 0.1), keep_size=True),
            iaa.GaussianBlur((0.0, 3.0)),
            iaa.AdditiveGaussianNoise(scale=(0, 0.05*255)),
            iaa.LinearContrast((0.75, 1.5)),
            iaa.Multiply((0.8, 1.2), per_channel=0.2)
        ], random_order=True)
        
        # Generate augmented images
        print(f"Generating {num_images} augmented images...")
        count = 0
        batch_size = min(16, num_images)  # smaller batches are sometimes faster
        
        # Generate and save all images
        for start in range(0, num_images, batch_size):
            end = min(num_images, start + batch_size)
            size = end - start
            idxs = np.random.choice(total_src, size=size, replace=True)
            batch = [images[i] for i in idxs]
            batch_aug = seq(images=batch)
            
            for img_arr in batch_aug:
                count += 1
                # Convert to PIL Image and resize
                im = Image.fromarray(img_arr)
                im_resized = im.resize(self.canvas_size, Image.LANCZOS)
                
                # Save to temp directory
                out_name = f"{count}.png"
                out_path = cam0_dir / out_name
                im_resized.save(out_path)
                
                if count % 10 == 0 or count == num_images:
                    print(f"  [{count}/{num_images}] images generated")
        
        # Create the ZIP file
        print("Creating ZIP file...")
        with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for file_path in sorted(cam0_dir.glob('**/*')):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        # Clean up temporary files
        shutil.rmtree(temp_dir)
        print(f"Created ZIP '{output_file}' with {num_images} images.")
    
    def resize_images(
        self, 
        source_dir: Union[str, Path], 
        output_dir: Union[str, Path], 
        size: Optional[Tuple[int, int]] = None
    ) -> List[Path]:
        """
        Resize all images in a directory to the specified size.
        
        Args:
            source_dir: Directory containing source images.
            output_dir: Directory to save resized images.
            size: Target size (width, height). If None, uses the default canvas size.
            
        Returns:
            List of paths to the resized images.
        """
        # Use default size if none specified
        size = size or self.canvas_size
        
        # Convert paths to Path objects
        source_dir = Path(source_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all images
        image_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        image_paths = sorted([
            p for p in source_dir.iterdir() 
            if p.suffix.lower() in image_exts
        ])
        
        # Process each image
        resized_paths = []
        for i, img_path in enumerate(image_paths):
            try:
                with Image.open(img_path) as img:
                    img = img.convert('RGB')
                    resized = img.resize(size, Image.LANCZOS)
                    
                    # Preserve the original extension
                    out_path = output_dir / img_path.name
                    resized.save(out_path)
                    resized_paths.append(out_path)
                    
                print(f"  [{i+1}/{len(image_paths)}] Resized: {img_path.name}")
            except Exception as e:
                print(f"  Error processing {img_path.name}: {e}")
        
        print(f"Resized {len(resized_paths)} images to {size}")
        return resized_paths
    
    def create_studio_zip(
        self, 
        source_dir: Union[str, Path], 
        output_file: Union[str, Path],
        temp_dir: str = 'temp_studio'
    ) -> None:
        """
        Create a ZIP file formatted for the studio from source images.
        
        Args:
            source_dir: Directory containing source images.
            output_file: Path to the output ZIP file.
            temp_dir: Temporary directory for processing.
        """
        # Convert paths to Path objects
        source_dir = Path(source_dir)
        output_file = Path(output_file)
        temp_dir = Path(temp_dir)
        cam0_dir = temp_dir / 'Cam0'
        
        # Clean up temp directory if it exists
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        cam0_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all images
        image_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        image_paths = sorted([
            p for p in source_dir.iterdir() 
            if p.suffix.lower() in image_exts
        ])
        
        if not image_paths:
            print("No images found in source directory.")
            return
        
        # Copy and rename the images to the temp directory
        for i, img_path in enumerate(image_paths):
            try:
                with Image.open(img_path) as img:
                    img = img.convert('RGB')
                    resized = img.resize(self.canvas_size, Image.LANCZOS)
                    
                    # Use sequential numbering for studio
                    out_path = cam0_dir / f"{i+1}.png"
                    resized.save(out_path)
                    
                if (i+1) % 10 == 0 or (i+1) == len(image_paths):
                    print(f"  [{i+1}/{len(image_paths)}] Processed: {img_path.name}")
            except Exception as e:
                print(f"  Error processing {img_path.name}: {e}")
        
        # Create the ZIP file
        print("Creating Studio ZIP file...")
        with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for file_path in sorted(cam0_dir.glob('**/*')):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        # Clean up temporary files
        shutil.rmtree(temp_dir)
        print(f"Created Studio ZIP '{output_file}' with {len(image_paths)} images.") 