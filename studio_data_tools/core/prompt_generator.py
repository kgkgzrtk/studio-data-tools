"""
Prompt Generator Module.

This module handles the generation of prompts for image generation using LLMs,
providing dynamic scene estimation and realistic prompt creation.
"""

import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dotenv import load_dotenv

# Google Gemini API imports
from google import genai
from google.genai import types

# Import prompt data from separate modules
from studio_data_tools.core.prompts.object_scenes import OBJECT_SCENE_MAP
from studio_data_tools.core.prompts.general_scenes import (
    GENERAL_SCENES, DEFAULT_SCENES,
    ENVIRONMENT_TYPES, LIGHTING_CONDITIONS, SURFACE_TYPES
)
from studio_data_tools.core.prompts.templates import (
    DYNAMIC_SCENE_SYSTEM_INSTRUCTION, DYNAMIC_SCENE_USER_MESSAGE,
    DIVERSE_SCENE_SYSTEM_INSTRUCTION, DIVERSE_SCENE_USER_MESSAGE,
    SCENE_INFERENCE_SYSTEM_INSTRUCTION, SCENE_INFERENCE_USER_MESSAGE,
    REALISTIC_PROMPT_SYSTEM_INSTRUCTION, REALISTIC_PROMPT_USER_MESSAGE,
    FALLBACK_PROMPT_TEMPLATE, ENHANCED_FALLBACK_PROMPT_TEMPLATE
)

# Load environment variables
load_dotenv()


class PromptGenerator:
    """
    Generates prompts for image generation using LLMs.
    
    This class provides both predefined scene templates and LLM-generated
    dynamic scene descriptions for image generation.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = 'gemini-2.0-flash-001'):
        """
        Initialize the prompt generator.
        
        Args:
            api_key: Optional API key for Gemini. If None, tries to get from environment.
            model: The model to use for prompt generation.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Please provide it or set GEMINI_API_KEY in .env file.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model
        
    def get_appropriate_scenes(self, object_name: str, use_llm: bool = False) -> List[str]:
        """
        Get appropriate scenes for a given object.
        
        Args:
            object_name: The name of the object to find scenes for.
            use_llm: Whether to use LLM for scene generation instead of predefined scenes.
            
        Returns:
            List of scene descriptions appropriate for the object.
        """
        if use_llm and self.client is not None:
            # Use LLM to generate scenes dynamically
            try:
                return self.generate_dynamic_scenes(object_name)
            except Exception as e:
                print(f"Error generating scenes with LLM: {e}")
                print("Falling back to predefined scenes")
                # Fall back to predefined scenes
        
        # Find the closest object key in the mapping using more flexible matching
        matched_scenes = self._find_matching_scenes(object_name)
        if matched_scenes:
            return matched_scenes
        
        # Fall back to general scenes if no match
        return GENERAL_SCENES
    
    def _find_matching_scenes(self, object_name: str) -> List[str]:
        """
        Find scenes that match the given object name using flexible matching.
        
        Args:
            object_name: The name of the object to find scenes for.
            
        Returns:
            List of matching scene descriptions, or empty list if no match found.
        """
        # Convert to lowercase for case-insensitive matching
        object_name_lower = object_name.lower()
        
        # 1. Try exact match first
        if object_name_lower in OBJECT_SCENE_MAP:
            return OBJECT_SCENE_MAP[object_name_lower]
        
        # 2. Try partial match (object name contains key or key contains object name)
        for key in OBJECT_SCENE_MAP:
            key_lower = key.lower()
            if key_lower in object_name_lower or object_name_lower in key_lower:
                return OBJECT_SCENE_MAP[key]
        
        # 3. Try word-level matching (any word in object name matches any word in key)
        object_words = set(object_name_lower.split())
        for key in OBJECT_SCENE_MAP:
            key_words = set(key.lower().split())
            if object_words.intersection(key_words):
                return OBJECT_SCENE_MAP[key]
        
        # No match found
        return []
    
    def generate_dynamic_scenes(self, object_name: str, num_scenes: int = 10) -> List[str]:
        """
        Generate scenes for an object completely from scratch using LLM without relying on predefined templates.
        
        Args:
            object_name: The object to generate scenes for.
            num_scenes: Number of scenes to generate.
            
        Returns:
            List of generated scene descriptions.
        """
        if self.client is None:
            raise ValueError("API client is required for dynamic scene generation")
        
        # Format the system instruction and user message with the appropriate values
        system_instruction = DYNAMIC_SCENE_SYSTEM_INSTRUCTION.format(
            num_scenes=num_scenes,
            object_name=object_name
        )
        
        user_message = DYNAMIC_SCENE_USER_MESSAGE.format(
            num_scenes=num_scenes,
            object_name=object_name
        )
        
        try:
            # Generate content
            response = self.client.models.generate_content(
                model="gemini-1.5-pro",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.9,  # Higher temperature for more creativity
                    max_output_tokens=800,
                    top_p=0.95
                )
            )
            
            # Process response
            scene_texts = [line.strip() for line in response.text.split('\n')
                         if line.strip() and not line.strip().startswith('#')]
            
            # Clean up scenes
            scenes = []
            
            for scene in scene_texts:
                if not scene or scene.isdigit() or scene.startswith('#'):
                    continue
                    
                clean_scene = scene
                
                # Remove numbering (e.g., "1. ", "1) ", etc.)
                if len(clean_scene) > 2 and clean_scene[0].isdigit():
                    for separator in ['. ', ') ', '- ', ': ']:
                        if separator in clean_scene[:5]:
                            clean_scene = clean_scene.split(separator, 1)[1].strip()
                            break
                
                # Add to scenes list if not empty
                if clean_scene:
                    scenes.append(clean_scene)
            
            # If we don't have enough scenes total, add fallbacks
            while len(scenes) < num_scenes:
                scenes.append(self._create_fallback_scene(object_name, len(scenes) + 1))
            
            return scenes[:num_scenes]
            
        except Exception as e:
            print(f"Error in dynamic scene generation: {e}")
            return self._create_default_dynamic_scenes(object_name, num_scenes)
    
    def _create_default_dynamic_scenes(self, object_name: str, num_scenes: int) -> List[str]:
        """Create default scenes when dynamic generation fails."""
        # Use the default scenes from the imported modules
        default_scenes = [scene.format(object=object_name) for scene in DEFAULT_SCENES]
        
        # シーンの選択
        result_scenes = default_scenes[:min(num_scenes, len(default_scenes))]
        
        # 必要であれば、残りのシーンをバリエーションで埋める
        while len(result_scenes) < num_scenes:
            idx = len(result_scenes) % len(default_scenes)
            base_scene = default_scenes[idx]
            
            # 照明バリエーションを追加
            lighting_vars = ["underexposed", "overexposed", "shadow-filled", "harshly lit",
                            "unevenly lit", "poorly lit", "backlit", "side-lit"]
            light_var = lighting_vars[len(result_scenes) % len(lighting_vars)]
            
            new_scene = f"{light_var} " + base_scene
            result_scenes.append(new_scene)
        
        return result_scenes[:num_scenes]
    
    def _create_fallback_scene(self, object_name: str, index: int) -> str:
        """Create a single fallback scene when needed to fill out the requested number."""
        # Use the environment types, lighting conditions, and surface types from the imported modules
        env_idx = (index * 3) % len(ENVIRONMENT_TYPES)
        cond_idx = (index * 7) % len(LIGHTING_CONDITIONS)
        surf_idx = (index * 5) % len(SURFACE_TYPES)
        
        return f"{LIGHTING_CONDITIONS[cond_idx]} {ENVIRONMENT_TYPES[env_idx]} with {SURFACE_TYPES[surf_idx]} and {object_name}"
    
    def generate_diverse_scenes(self, object_name: str, num_scenes: int = 10) -> List[str]:
        """
        Generate diverse scene descriptions using LLM.
        
        Args:
            object_name: The object to generate scenes for.
            num_scenes: Number of scenes to generate.
            
        Returns:
            List of generated scene descriptions.
        """
        if self.client is None:
            print("Warning: No API key available, using predefined scenes.")
            return self.get_appropriate_scenes(object_name)
        
        # Get example scenes for the prompt
        examples = []
        matched_scenes = self._find_matching_scenes(object_name)
        if matched_scenes:
            examples = matched_scenes[:3]  # Use up to 3 examples
        
        examples_text = "\n".join([f"- {ex}" for ex in examples]) if examples else ""
        
        # Format the system instruction and user message with the appropriate values
        system_instruction = DIVERSE_SCENE_SYSTEM_INSTRUCTION.format(
            num_scenes=num_scenes,
            object_name=object_name
        )
        
        user_message = DIVERSE_SCENE_USER_MESSAGE.format(
            num_scenes=num_scenes,
            object_name=object_name,
            examples_text=examples_text
        )
        
        try:
            # Generate content
            response = self.client.models.generate_content(
                model="gemini-1.5-pro",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.8,
                    max_output_tokens=500
                )
            )
            
            # Split response into lines and extract non-empty lines
            scene_texts = [line.strip() for line in response.text.split('\n') 
                           if line.strip() and not line.strip().startswith('#') and not line.strip().isdigit()]
            
            # Clean up the scenes (remove numbering, etc.)
            scenes = []
            for scene in scene_texts:
                clean_scene = scene
                if scene[0].isdigit() and len(scene) > 2:
                    parts = scene.split('.', 1)
                    if len(parts) > 1:
                        clean_scene = parts[1].strip()
                        
                # Remove leading dashes or bullets
                if clean_scene.startswith('-') or clean_scene.startswith('*'):
                    clean_scene = clean_scene[1:].strip()
                    
                scenes.append(clean_scene)
                
            # Fall back to default scenes if generation failed
            if not scenes:
                print("Warning: Failed to generate scenes with LLM, using default scenes instead.")
                # Use a mix of general scenes with the object name
                return [f"{scene} with {object_name}" for scene in GENERAL_SCENES]
            
            return scenes
            
        except Exception as e:
            print(f"Error generating scenes with LLM: {e}")
            # Fall back to default scenes on error
            # Use a mix of general scenes with the object name
            return [f"{scene} with {object_name}" for scene in GENERAL_SCENES]
    
    def infer_scene(self, object_name: str, num_objects: int = 1) -> str:
        """
        Use LLM to infer an appropriate scene for the given object.
        
        Args:
            object_name: The target object.
            num_objects: Number of objects in the scene.
            
        Returns:
            An inferred scene description.
        """
        if self.client is None:
            # Fall back to predefined scenes if no API access
            appropriate_scenes = self.get_appropriate_scenes(object_name)
            return random.choice(appropriate_scenes)
        
        # 動的シーン生成を使用して複数のシーンを生成し、そこからランダムに選択する方式に変更
        try:
            # 多様なシーンを生成
            scenes = self.generate_dynamic_scenes(object_name, num_scenes=10)
            # ランダムに1つ選択
            return random.choice(scenes)
        except Exception as e:
            print(f"Error generating dynamic scenes: {e}")
            # フォールバック: より直接的なプロンプト
            
            # Format the system instruction and user message with the appropriate values
            system_instruction = SCENE_INFERENCE_SYSTEM_INSTRUCTION
            
            user_message = SCENE_INFERENCE_USER_MESSAGE.format(
                num_objects=num_objects,
                object_name=object_name
            )
            
            try:
                # Generate the scene with LLM
                response = self.client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.9,  # Higher temperature for more variety
                        max_output_tokens=50
                    )
                )
                
                # Clean up the response
                scene = response.text.strip().strip('"\'').replace('\n', ' ')
                
                # Fall back to predefined scenes if response is too short or long
                if len(scene.split()) < 2 or len(scene.split()) > 15:
                    # Use the default dynamic scenes
                    default_scenes = self._create_default_dynamic_scenes(object_name, 10)
                    scene = random.choice(default_scenes)
                    
                return scene
                
            except Exception as e:
                print(f"Error inferring scene: {e}")
                # Fall back to predefined scenes on error
                default_scenes = [scene.format(object=object_name) for scene in DEFAULT_SCENES[:10]]
                return random.choice(default_scenes)
    
    def generate_realistic_prompt(self, object_name: str, scene_type: str, 
                                 num_objects: Optional[int] = None, 
                                 min_objects: int = 1, 
                                 max_objects: int = 3) -> Dict[str, Union[str, int]]:
        """
        Generate a highly realistic prompt for image generation using LLM.
        
        Args:
            object_name: The target object.
            scene_type: The scene description.
            num_objects: Number of objects (if None, will be random between min and max).
            min_objects: Minimum number of objects if num_objects is None.
            max_objects: Maximum number of objects if num_objects is None.
            
        Returns:
            Dictionary with prompt, scene, and object_count.
        """
        if self.client is None:
            # Fall back to simple prompt if no API access
            num_objects = num_objects or random.randint(min_objects, max_objects)
            prompt = FALLBACK_PROMPT_TEMPLATE.format(
                num_objects=num_objects,
                object_name=object_name,
                scene_type=scene_type
            )
            return {
                "prompt": prompt,
                "scene": scene_type,
                "object_count": num_objects,
                "object": object_name
            }
        
        # Determine number of objects if not provided
        if num_objects is None:
            num_objects = random.randint(min_objects, max_objects)
        
        # Format the system instruction and user message with the appropriate values
        system_instruction = REALISTIC_PROMPT_SYSTEM_INSTRUCTION.format(
            num_objects=num_objects,
            object_name=object_name,
            scene_type=scene_type
        )
        
        user_message = REALISTIC_PROMPT_USER_MESSAGE.format(
            num_objects=num_objects,
            object_name=object_name,
            scene_type=scene_type
        )
        
        try:
            # Generate the prompt
            response = self.client.models.generate_content(
                model="gemini-1.5-pro",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.8,
                    max_output_tokens=500
                )
            )
            
            return {
                "prompt": response.text,
                "scene": scene_type,
                "object_count": num_objects,
                "object": object_name
            }
        except Exception as e:
            print(f"Error generating realistic prompt: {e}")
            # Fall back to simple prompt on error
            prompt = FALLBACK_PROMPT_TEMPLATE.format(
                num_objects=num_objects,
                object_name=object_name,
                scene_type=scene_type
            )
            return {
                "prompt": prompt,
                "scene": scene_type,
                "object_count": num_objects,
                "object": object_name
            }
    
    def generate_simple_prompt(self, object_name: str, scene_type: Optional[str] = None, 
                              num_objects: Optional[int] = None, use_llm: bool = True,
                              use_dynamic_scenes: bool = True) -> Tuple[str, str, int]:
        """
        Generate a simple image prompt without using extensive LLM for the prompt itself.
        
        Args:
            object_name: The target object.
            scene_type: The scene description (if None, will be inferred).
            num_objects: Number of objects (if None, will be random between 1-3).
            use_llm: Whether to use LLM for scene inference if scene_type is None.
            use_dynamic_scenes: Whether to use fully dynamic scene generation instead of predefined mappings.
            
        Returns:
            Tuple of (prompt_text, scene, object_count)
        """
        # Set defaults
        if object_name is None:
            object_name = random.choice(list(OBJECT_SCENE_MAP.keys()))
        
        if num_objects is None:
            num_objects = random.randint(1, 3)
        
        # Determine scene
        if scene_type is None:
            if use_llm:
                # デフォルトでは動的シーン生成を使用する
                try:
                    # 多様なシーンを生成
                    dynamic_scenes = self.generate_dynamic_scenes(object_name, num_scenes=10)
                    
                    # 生成されたシーンが同じものばかりでないか確認
                    if len(set(dynamic_scenes)) < 3:  # 少なくとも3種類以上のシーンが必要
                        print("Warning: Not enough scene variety, regenerating...")
                        # 予備のシーンセットを生成して結合
                        extra_scenes = self._create_default_dynamic_scenes(object_name, 5)
                        dynamic_scenes.extend(extra_scenes)
                        # 重複を削除
                        dynamic_scenes = list(set(dynamic_scenes))
                    
                    scene_type = random.choice(dynamic_scenes)
                except Exception as e:
                    print(f"Error using dynamic scene generation: {e}")
                    # デフォルトシーンにフォールバック
                    default_scenes = [scene.format(object=object_name) for scene in DEFAULT_SCENES[:10]]
                    scene_type = random.choice(default_scenes)
            else:
                # LLMを使わない場合は、デフォルトシーンを使用
                default_scenes = [scene.format(object=object_name) for scene in DEFAULT_SCENES[:10]]
                scene_type = random.choice(default_scenes)
        
        # Generate a standard prompt with worse lighting conditions
        prompt = ENHANCED_FALLBACK_PROMPT_TEMPLATE.format(
            num_objects=num_objects,
            object_name=object_name,
            scene_type=scene_type
        )
        
        return prompt, scene_type, num_objects
    
    def generate_simple_prompts(self, object_type: str, count: int = 1, use_dynamic_scenes: bool = False) -> List[Dict[str, str]]:
        """
        Generate simple prompts using predefined templates or dynamic generation.
        
        Args:
            object_type: Type of object to generate prompts for (e.g., "empty can")
            count: Number of prompts to generate
            use_dynamic_scenes: Whether to use dynamic scene generation instead of predefined mappings
            
        Returns:
            List of prompt dictionaries with scene, prompt, and object
        """
        if not use_dynamic_scenes and object_type not in OBJECT_SCENE_MAP:
            if use_dynamic_scenes:
                # When using dynamic scenes, we don't need to validate against OBJECT_SCENE_MAP
                pass
            else:
                raise ValueError(f"Unsupported object type: {object_type}. Supported types: {list(OBJECT_SCENE_MAP.keys())}")
        
        # Get scenes - either from predefined mappings or dynamically generated
        if use_dynamic_scenes:
            try:
                scenes = self.generate_dynamic_scenes(object_type, num_scenes=count)
            except Exception as e:
                print(f"Error in dynamic scene generation: {e}, falling back to predefined scenes")
                scenes = self.get_appropriate_scenes(object_type, use_llm=False)
        else:
            scenes = self.get_appropriate_scenes(object_type, use_llm=False)
            
        # If we need more scenes than available and not using dynamic generation, cycle through them
        if not use_dynamic_scenes and count > len(scenes):
            additional_needed = count - len(scenes)
            additional_scenes = [scenes[i % len(scenes)] for i in range(additional_needed)]
            scenes = scenes + additional_scenes
            
        # Ensure we have enough scenes
        selected_scenes = scenes[:count]
        
        prompts = []
        for scene in selected_scenes:
            # Create a prompt that will produce a photorealistic image
            prompt_text = f"Photorealistic image of {scene}. High resolution, detailed, professional photography."
            
            prompts.append({
                "scene": scene,
                "prompt": prompt_text,
                "object": object_type
            })
        
        return prompts
    
    def generate_fully_dynamic_prompts(self, object_type: str, count: int = 1) -> List[Dict]:
        """
        Generate prompts completely dynamically for any object type without relying on predefined mappings.
        
        This method is useful for objects that are not in the predefined OBJECT_SCENE_MAP.
        
        Args:
            object_type: Any object type to generate prompts for (no restrictions)
            count: Number of prompts to generate
            
        Returns:
            List of prompt dictionaries with scene, prompt, object, and object_count
        """
        if self.client is None:
            raise ValueError("API client is required for fully dynamic prompt generation")
            
        prompts = []
        
        try:
            # 1. Generate diverse scenes dynamically
            scenes = self.generate_dynamic_scenes(object_type, num_scenes=count)
            
            # 2. For each scene, create a prompt
            for scene in scenes:
                # Randomly determine object count
                obj_count = random.randint(1, 3)
                
                # Generate a standard prompt template with poor lighting emphasis
                prompt_text = ENHANCED_FALLBACK_PROMPT_TEMPLATE.format(
                    num_objects=obj_count,
                    object_name=object_type,
                    scene_type=scene
                )
                
                prompts.append({
                    "scene": scene,
                    "prompt": prompt_text,
                    "object": object_type,
                    "object_count": obj_count
                })
                
        except Exception as e:
            print(f"Error in fully dynamic prompt generation: {e}")
            # Create some basic fallback prompts
            for i in range(count):
                obj_count = random.randint(1, 3)
                scene = self._create_fallback_scene(object_type, i)
                
                prompt_text = FALLBACK_PROMPT_TEMPLATE.format(
                    num_objects=obj_count,
                    object_name=object_type,
                    scene_type=scene
                )
                
                prompts.append({
                    "scene": scene,
                    "prompt": prompt_text,
                    "object": object_type,
                    "object_count": obj_count
                })
                
        return prompts
    
    def generate_llm_prompts(
        self, 
        object_type: str, 
        count: int = 1,
        min_objects: int = 1,
        max_objects: int = 5,
        exact_objects: Optional[int] = None,
        advanced: bool = False,
        use_dynamic_scenes: bool = False
    ) -> List[Dict]:
        """
        Generate prompts using the LLM for creative scene descriptions.
        
        Args:
            object_type: Type of object to generate prompts for (e.g., "empty can")
            count: Number of prompts to generate
            min_objects: Minimum number of objects per scene
            max_objects: Maximum number of objects per scene
            exact_objects: Exact number of objects (overrides min/max)
            advanced: Use advanced prompt techniques
            use_dynamic_scenes: Whether to use fully dynamic scene generation without relying on predefined mappings
            
        Returns:
            List of prompt dictionaries with scene, prompt, object, and object_count
        """
        prompts = []
        
        # Check if object type is supported or if using dynamic generation
        if not use_dynamic_scenes and object_type not in OBJECT_SCENE_MAP:
            if self.client is None:
                raise ValueError(f"Unsupported object type: {object_type}. Supported types: {list(OBJECT_SCENE_MAP.keys())}")
            else:
                print(f"Warning: {object_type} not in predefined mappings, using full dynamic generation")
                use_dynamic_scenes = True
        
        # If using dynamic scenes, use the fully dynamic generation approach
        if use_dynamic_scenes:
            try:
                # Generate scenes dynamically
                scenes = self.generate_dynamic_scenes(object_type, num_scenes=count)
                
                # For each scene, customize the object count and generate a prompt
                for i in range(count):
                    scene_idx = i % len(scenes)  # Cycle through scenes if needed
                    scene = scenes[scene_idx]
                    
                    # Determine object count
                    if exact_objects is not None:
                        obj_count = exact_objects
                    else:
                        obj_count = random.randint(min_objects, max_objects)
                    
                    # Choose a system instruction based on advanced mode
                    if advanced:
                        system_instruction = (
                            f"You are an expert photographer describing scenes with {obj_count} {object_type}(s) in various environments. "
                            f"Create a brief, vivid description of a scene containing {obj_count} {object_type}(s) in this setting: '{scene}'. "
                            f"Make it specific and visually interesting. "
                            f"Focus on lighting, environment, and composition. "
                            f"Your descriptions should be suitable for generating photorealistic images. "
                            f"Keep your response to 1-2 sentences only describing the scene. "
                            f"DO NOT write 'a photo of' or 'a picture of' - just describe the scene itself."
                        )
                    else:
                        system_instruction = (
                            f"Describe a realistic scene containing {obj_count} {object_type}(s) in this setting: '{scene}'. "
                            f"Keep your response to 1-2 sentences only describing the scene. "
                            f"DO NOT write 'a photo of' or 'a picture of' - just describe the scene itself."
                        )
                    
                    # Call the LLM to generate the prompt or use a fallback
                    try:
                        response = self.client.models.generate_content(
                            model=self.model_name,
                            contents="Generate a scene description.",
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.7,
                                max_output_tokens=100,
                                top_p=0.95,
                                top_k=40
                            )
                        )
                        
                        # Get the generated scene
                        scene_desc = response.text.strip()
                        
                        # Construct the final prompt with instructions for the image model
                        if advanced:
                            prompt_text = (
                                f"{scene_desc}. "
                                f"Amateur smartphone photo, unprocessed RAW quality, unstable handheld shot, "
                                f"random composition with poor framing, visible digital noise, flat colors, "
                                f"mild motion blur, and uneven lighting with bad white balance."
                            )
                        else:
                            prompt_text = f"Casual amateur snapshot of {scene_desc}. Unprocessed, smartphone quality with technical imperfections."
                        
                        prompts.append({
                            "scene": scene,
                            "scene_description": scene_desc,
                            "prompt": prompt_text,
                            "object": object_type,
                            "object_count": obj_count
                        })
                        
                    except Exception as e:
                        print(f"Error generating LLM prompt: {e}")
                        # Use fallback template
                        prompt_text = FALLBACK_PROMPT_TEMPLATE.format(
                            num_objects=obj_count,
                            object_name=object_type,
                            scene_type=scene
                        )
                        
                        prompts.append({
                            "scene": scene,
                            "prompt": prompt_text,
                            "object": object_type,
                            "object_count": obj_count
                        })
                        
                return prompts
                
            except Exception as e:
                print(f"Error in dynamic scene generation: {e}, falling back to original method")
                # Fall through to the original method if dynamic generation fails
        
        # Original method (non-dynamic) using predefined object mappings
        # Determine the object count description
        if exact_objects is not None:
            objects_desc = f"exactly {exact_objects}"
            obj_count = exact_objects
        else:
            # If no exact count specified, vary the amounts within range
            for _ in range(count):
                obj_count = random.randint(min_objects, max_objects)
                objects_desc = f"{obj_count}"
                
                # Choose a system instruction based on advanced mode
                if advanced:
                    system_instruction = (
                        f"You are an expert photographer describing scenes with {objects_desc} {object_type}(s) in various environments. "
                        f"Create a brief, vivid description of a scene containing {objects_desc} {object_type}(s). "
                        f"Make it specific and visually interesting. "
                        f"Focus on lighting, environment, and composition. "
                        f"Your descriptions should be suitable for generating photorealistic images. "
                        f"Keep your response to 1-2 sentences only describing the scene. "
                        f"DO NOT write 'a photo of' or 'a picture of' - just describe the scene itself."
                    )
                else:
                    system_instruction = (
                        f"Describe a realistic scene containing {objects_desc} {object_type}(s). "
                        f"Keep your response to 1-2 sentences only describing the scene. "
                        f"DO NOT write 'a photo of' or 'a picture of' - just describe the scene itself."
                    )
                
                # Call the LLM to generate the prompt
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents="Generate a scene description.",
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.7,
                            max_output_tokens=100,
                            top_p=0.95,
                            top_k=40
                        )
                    )
                    
                    # Get the generated scene
                    scene = response.text.strip()
                    
                    # Construct the final prompt with instructions for the image model
                    if advanced:
                        prompt_text = (
                            f"{scene}. "
                            f"Amateur smartphone photo, unprocessed RAW quality, unstable handheld shot, "
                            f"random composition with poor framing, visible digital noise, flat colors, "
                            f"mild motion blur, and uneven lighting with bad white balance."
                        )
                    else:
                        prompt_text = f"Casual amateur snapshot of {scene}. Unprocessed, smartphone quality with technical imperfections."
                    
                    prompts.append({
                        "scene": scene,
                        "prompt": prompt_text,
                        "object": object_type,
                        "object_count": obj_count
                    })
                
                except Exception as e:
                    print(f"Error generating LLM prompt: {e}")
                    # Fallback to simple prompts if LLM fails
                    simple_prompt = self.generate_simple_prompts(object_type, 1)[0]
                    simple_prompt["object_count"] = obj_count
                    prompts.append(simple_prompt)
        
        return prompts 