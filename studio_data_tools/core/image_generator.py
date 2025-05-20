"""
Image Generator Module.

This module handles the generation of images using Google's Imagen API,
with support for Imagen 3 model.
"""

import os
import json
import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import base64

from PIL import Image
from dotenv import load_dotenv

# Google Gemini/Imagen API imports
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()


class ImageGenerator:
    """
    Handles the generation of images using Google's Imagen API.
    
    Supports Imagen 3.0 image generation models.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = 'imagen-3.0-generate-002'):
        """
        Initialize the image generator.
        
        Args:
            api_key: Optional API key for Gemini/Imagen. If None, tries to get from environment.
            model: The model to use for image generation.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Please provide it or set GEMINI_API_KEY in .env file.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model
    
    def generate_image(self, prompt: str, aspect_ratio: str = "1:1") -> Optional[Image.Image]:
        """
        Generate a single image using Imagen 3.
        
        Args:
            prompt: The text prompt to generate the image from.
            aspect_ratio: The aspect ratio of the generated image.
            
        Returns:
            PIL Image object or None if generation failed.
        """
        try:
            # Generate the image using the Imagen 3 model
            response = self.client.models.generate_images(
                model=self.model_name,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=aspect_ratio
                )
            )
            
            # Process the generated image
            if response.generated_images and len(response.generated_images) > 0:
                image_bytes = response.generated_images[0].image.image_bytes
                image = Image.open(BytesIO(image_bytes))
                return image
                    
            # No images were generated
            return None
            
        except Exception as e:
            print(f"Error generating image with {self.model_name}: {e}")
            return self._fallback_generate_image(prompt)
    
    def _fallback_generate_image(self, prompt: str) -> Optional[Image.Image]:
        """
        Fallback method for image generation using a different model.
        
        Args:
            prompt: The text prompt to generate the image from.
            
        Returns:
            PIL Image object or None if generation failed.
        """
        try:
            print("Trying fallback image generation...")
            
            # Try a different model for image generation
            fallback_model = "gemini-2.0-flash-preview-image-generation"
            
            response = self.client.models.generate_content(
                model=fallback_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            # Extract the image data
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data is not None:
                    # Get the base64 image data
                    image_data = part.inline_data.data
                    # Decode the base64 data
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                    return image
                    
            return None
            
        except Exception as e:
            print(f"Fallback image generation also failed: {e}")
            return None
    
    def generate_and_save_images(
        self,
        prompts: Union[str, List[Dict[str, Any]]],
        output_dir: str,
        prefix: Optional[str] = None,
        save_prompts: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images from prompts and save them to disk.
        
        Args:
            prompts: Either a single prompt string or a list of prompt data dictionaries
                    with at least a 'prompt' key, and optionally 'scene' and 'object_count' keys.
            output_dir: Directory to save the generated images.
            prefix: Optional prefix for the filenames.
            save_prompts: Whether to save prompt information as JSON.
            
        Returns:
            List of dictionaries with information about the generated images.
        """
        # Convert single prompt to list format
        if isinstance(prompts, str):
            prompts = [{'prompt': prompts}]
        
        # Prepare output directory
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Timestamp for filename prefix
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if prefix:
            timestamp = f"{prefix}_{timestamp}"
        
        # List to store information about generated images
        generated_images_info = []
        
        # Generate and save each image
        for i, prompt_data in enumerate(prompts):
            prompt = prompt_data['prompt']
            scene = prompt_data.get('scene', 'unknown')
            object_count = prompt_data.get('object_count', 0)
            object_name = prompt_data.get('object', 'object')
            
            print(f"[{i+1}/{len(prompts)}] Generating image for: {scene}...")
            
            # Generate the image
            image = self.generate_image(prompt)
            
            if image:
                # Create filename
                file_name = f"{timestamp}_{i+1:03d}_{object_name.replace(' ', '_')}.jpg"
                file_path = output_dir / file_name
                
                # Save the image
                image.save(file_path, format="JPEG")
                
                # Record information
                generated_images_info.append({
                    'file_name': file_name,
                    'file_path': str(file_path),
                    'prompt': prompt,
                    'scene': scene,
                    'object': object_name,
                    'num_objects': object_count
                })
                
                print(f"  Saved as {file_path}")
            else:
                print(f"  Failed to generate image for prompt {i+1}")
        
        # Save prompt information as JSON if requested
        if save_prompts and generated_images_info:
            object_name = generated_images_info[0].get('object', 'object').replace(' ', '_')
            prompts_file = output_dir / f"{object_name}_prompts.json"
            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(generated_images_info, f, indent=2)
            print(f"Prompts saved to: {prompts_file}")
        
        return generated_images_info 