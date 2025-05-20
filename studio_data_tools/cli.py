#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Studio Data Tools CLI.

This module provides a unified command-line interface for all functionality,
allowing users to generate images, prepare datasets, and more.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Load local modules
try:
    from studio_data_tools.core.prompt_generator import PromptGenerator
    from studio_data_tools.core.image_generator import ImageGenerator
    from studio_data_tools.core.dataset_processor import DatasetProcessor
except ImportError:
    # Handle case where module is run directly
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from studio_data_tools.core.prompt_generator import PromptGenerator
    from studio_data_tools.core.image_generator import ImageGenerator
    from studio_data_tools.core.dataset_processor import DatasetProcessor

# Load environment variables
load_dotenv()


def generate_images(args) -> None:
    """
    Generate images with Imagen 3 using either simple or LLM-enhanced prompts.
    
    Args:
        args: Command line arguments
    """
    # Initialize generators
    prompt_gen = PromptGenerator(api_key=args.api_key)
    image_gen = ImageGenerator(api_key=args.api_key, model=args.model)
    
    # Create output directory path
    output_dir = Path(args.output_dir) / args.object.replace(" ", "_")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {args.count} images of '{args.object}'...")
    
    # List to store prompt data
    prompt_data_list = []
    
    # 常に動的シーン生成を使用する
    use_dynamic_scenes = True
    
    # Generate prompts
    for i in range(args.count):
        # Generate a random number of objects per image unless specified
        num_objects = args.num_objects
        if num_objects is None:
            num_objects = args.min_objects if args.min_objects == args.max_objects else None
        
        # Generate scene using LLM if enabled, otherwise use predefined scenes
        scene_type = None  # Will be inferred or randomly selected
        
        if args.advanced_prompts:
            # Use LLM to generate realistic scene and prompt
            scene_type = prompt_gen.infer_scene(args.object, num_objects or 1) if args.use_llm else None
            prompt_data = prompt_gen.generate_realistic_prompt(
                args.object, 
                scene_type,
                num_objects,
                args.min_objects,
                args.max_objects
            )
            
            # Add object info to prompt data
            prompt_data['object'] = args.object
            prompt_data_list.append(prompt_data)
            
            # 屋内/屋外の分類を判定して表示
            scene_location = "INDOOR" if any(indoor_term in prompt_data['scene'].lower() for indoor_term in 
                                           ["kitchen", "bathroom", "office", "bedroom", "living room", 
                                            "restaurant", "hotel", "shop", "store", "room", "indoor", 
                                            "shelf", "counter", "desk", "cabinet", "hallway", "lobby"]) else "OUTDOOR"
            
            print(f"[{i+1}/{args.count}] Generated realistic prompt for scene [{scene_location}]: {prompt_data['scene']}")
            
        else:
            # Use simple prompt generation with dynamic scenes
            prompt, scene, actual_num_objects = prompt_gen.generate_simple_prompt(
                args.object,
                scene_type,
                num_objects,
                args.use_llm,
                use_dynamic_scenes
            )
            
            prompt_data = {
                'prompt': prompt,
                'scene': scene,
                'object_count': actual_num_objects,
                'object': args.object
            }
            prompt_data_list.append(prompt_data)
            
            # 屋内/屋外の分類を判定して表示
            scene_location = "INDOOR" if any(indoor_term in scene.lower() for indoor_term in 
                                           ["kitchen", "bathroom", "office", "bedroom", "living room", 
                                            "restaurant", "hotel", "shop", "store", "room", "indoor", 
                                            "shelf", "counter", "desk", "cabinet", "hallway", "lobby"]) else "OUTDOOR"
            
            print(f"[{i+1}/{args.count}] Generated simple prompt for scene [{scene_location}]: {scene}")
    
    # Generate and save images
    generated_info = image_gen.generate_and_save_images(
        prompts=prompt_data_list,
        output_dir=output_dir,
        save_prompts=True
    )
    
    print(f"\nGenerated {len(generated_info)} images.")
    print(f"Images saved to: {output_dir}")


def prepare_dataset(args) -> None:
    """
    Prepare dataset for studio use, with optional augmentation.
    
    Args:
        args: Command line arguments
    """
    processor = DatasetProcessor(canvas_size=(args.width, args.height))
    
    # Determine source directory
    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return
    
    if args.augment:
        # Create augmented dataset
        print(f"Creating augmented dataset with {args.num_images} images...")
        try:
            processor.create_augmented_dataset(
                source_dir=source_dir,
                output_file=args.output_file,
                num_images=args.num_images
            )
        except RuntimeError as e:
            print(f"Error: {e}")
    else:
        # Create studio-formatted dataset without augmentation
        print("Creating studio dataset without augmentation...")
        processor.create_studio_zip(
            source_dir=source_dir,
            output_file=args.output_file
        )


def main(argv: List[str] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        argv: Command line arguments (if None, uses sys.argv)
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description='Studio Data Tools - Image generation and dataset preparation'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Command to execute'
    )
    subparsers.required = True
    
    # Generate images command
    gen_parser = subparsers.add_parser(
        'generate', 
        help='Generate images using Imagen 3'
    )
    gen_parser.add_argument(
        '--object', type=str, default='empty can',
        help='Object type to generate (e.g., "empty can", "plastic bottle")'
    )
    gen_parser.add_argument(
        '--count', type=int, default=10,
        help='Number of images to generate'
    )
    gen_parser.add_argument(
        '--min-objects', type=int, default=1,
        help='Minimum number of objects per image'
    )
    gen_parser.add_argument(
        '--max-objects', type=int, default=3,
        help='Maximum number of objects per image'
    )
    gen_parser.add_argument(
        '--num-objects', type=int, default=None,
        help='Exact number of objects per image (overrides min/max)'
    )
    gen_parser.add_argument(
        '--output-dir', type=str, default='generated_images',
        help='Output directory for saving images'
    )
    gen_parser.add_argument(
        '--api-key', type=str, default=None,
        help='Gemini/Imagen API key (if not set in .env file)'
    )
    gen_parser.add_argument(
        '--model', type=str, default='imagen-3.0-generate-002',
        help='Imagen model to use'
    )
    gen_parser.add_argument(
        '--use-llm', action='store_true', default=True,
        help='Use LLM to dynamically generate scenes (default: True)'
    )
    gen_parser.add_argument(
        '--no-llm', action='store_false', dest='use_llm',
        help='Disable LLM scene generation, use predefined scenes only'
    )
    gen_parser.add_argument(
        '--advanced-prompts', action='store_true', default=False,
        help='Use advanced LLM prompt generation for more realistic images'
    )
    gen_parser.set_defaults(func=generate_images)
    
    # Prepare dataset command
    prep_parser = subparsers.add_parser(
        'prepare', 
        help='Prepare dataset for studio use'
    )
    prep_parser.add_argument(
        'source_dir', type=str,
        help='Source directory containing images'
    )
    prep_parser.add_argument(
        '--output-file', '-o', type=str, default='Cam0.zip',
        help='Output ZIP filename'
    )
    prep_parser.add_argument(
        '--width', type=int, default=640,
        help='Width of output images'
    )
    prep_parser.add_argument(
        '--height', type=int, default=480,
        help='Height of output images'
    )
    prep_parser.add_argument(
        '--augment', action='store_true', default=False,
        help='Apply data augmentation techniques'
    )
    prep_parser.add_argument(
        '--num-images', '-n', type=int, default=100,
        help='Number of augmented images to generate (only used with --augment)'
    )
    prep_parser.set_defaults(func=prepare_dataset)
    
    # Sample images command (alias for generate with specific settings)
    sample_parser = subparsers.add_parser(
        'samples', 
        help='Generate sample images with advanced prompts'
    )
    sample_parser.add_argument(
        '--object', type=str, default='empty can',
        help='Object type to generate (e.g., "empty can", "plastic bottle")'
    )
    sample_parser.add_argument(
        '--count', type=int, default=5,
        help='Number of sample images to generate'
    )
    sample_parser.add_argument(
        '--output-dir', type=str, default='sample_images',
        help='Output directory for saving images'
    )
    sample_parser.add_argument(
        '--api-key', type=str, default=None,
        help='Gemini/Imagen API key (if not set in .env file)'
    )
    # Pre-set advanced prompts and use LLM
    sample_parser.set_defaults(
        func=generate_images,
        min_objects=1,
        max_objects=3,
        num_objects=None,
        use_llm=True,
        advanced_prompts=True,
        model='imagen-3.0-generate-002'
    )
    
    # Parse arguments
    args = parser.parse_args(argv)
    
    # Execute the appropriate function
    args.func(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 