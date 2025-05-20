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

# Load environment variables
load_dotenv()

# Object and scene mapping definition
OBJECT_SCENE_MAP = {
    "empty can": [
        "urban street with empty cans on asphalt",
        "park bench with discarded cans",
        "grassy field with scattered aluminum cans",
        "parking lot with empty cans",
        "beach with washed-up cans",
        "sidewalk with empty soda cans",
        "forest floor with discarded cans",
        "public trash bin overflowing with cans",
        "roadside ditch with cans",
        "empty lot with scattered trash and cans"
    ],
    "plastic bottle": [
        "riverbank with plastic bottles",
        "ocean shore with washed-up plastic bottles",
        "hiking trail with discarded plastic bottles",
        "urban street corner with plastic bottles",
        "public park with plastic bottles",
        "roadside with plastic bottles",
        "beach sand with plastic bottles",
        "recycling bin overflowing with plastic bottles",
        "forest clearing with plastic bottles",
        "creek bed with plastic bottles"
    ],
    "glass bottle": [
        "park area with glass bottles",
        "urban alleyway with glass bottles",
        "beach with glass bottles in sand",
        "outdoor tables with empty glass bottles",
        "indoor countertop with glass bottles"
    ],
    "paper cup": [
        "urban street with discarded paper cups",
        "park bench with paper cups",
        "office space with paper cups",
        "cafe tables with empty paper cups",
        "parking lot with scattered paper cups"
    ]
}

# General scenes for fallback
GENERAL_SCENES = [
    "urban street with litter",
    "outdoor park area",
    "indoor surface",
    "parking lot ground",
    "riverside or beach",
    "grassy field"
]

# Sample prompt for LLM examples
SAMPLE_PROMPT = """
A photorealistic handheld snapshot of abandoned street litter—crushed silver aluminum cans with visible dents, a red plastic cup, and scattered cigarette butts—lying on a mixed asphalt, concrete, and stone-paved sidewalk beside an ivy-covered brick wall and the mossy edge of a green-algae-filled canal. Soft ambient natural light under an overcast sky or early morning/evening glow. Tilted camera angle with an off-center composition, shallow to moderate depth of field focusing sharply on the litter in the foreground while gently blurring the background. Ultra-high resolution (4K), emphasizing crisp details: metal textures, leaf veins, grout lines, and algae surface. Muted earth-tone color palette (grays, browns, greens) accented by pops of red, blue, and silver. 4:3 aspect ratio.
"""


class PromptGenerator:
    """
    Generates prompts for image generation using LLMs.
    
    This class provides both hardcoded scene templates and LLM-generated
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
        
    def get_appropriate_scenes(self, object_name: str) -> List[str]:
        """
        Get appropriate scenes for a given object.
        
        Args:
            object_name: The name of the object to find scenes for.
            
        Returns:
            List of scene descriptions appropriate for the object.
        """
        # Find the closest object key in the mapping
        for key in OBJECT_SCENE_MAP:
            if key.lower() in object_name.lower() or object_name.lower() in key.lower():
                return OBJECT_SCENE_MAP[key]
        
        # Fall back to general scenes if no match
        return GENERAL_SCENES
    
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
        for key, scenes in OBJECT_SCENE_MAP.items():
            if key.lower() in object_name.lower() or object_name.lower() in key.lower():
                examples = scenes[:3]  # Use up to 3 examples
                break
        
        examples_text = "\n".join([f"- {ex}" for ex in examples]) if examples else ""
        
        system_instruction = (
            "You are an expert location scout for realistic documentary photography. "
            f"Generate {num_scenes} diverse and realistic locations where discarded {object_name}(s) might be found in everyday environments. "
            "The locations should vary in terms of urban/rural settings, indoor/outdoor, lighting conditions, and surface types. "
            "Be specific about the environment, surface material, nearby elements, and lighting. "
            "Each location description should be 10-15 words and focus on physical setting, not camera settings."
        )
        
        user_message = (
            f"Generate {num_scenes} diverse locations where {object_name}(s) might be found as litter or discarded items. "
            "Include a mix of:\n"
            "- Urban environments (streets, sidewalks, parking lots)\n"
            "- Natural settings (parks, beaches, wooded areas)\n"
            "- Indoor locations (floors, tables, shelves)\n"
            "- Different lighting conditions (bright sunlight, overcast, dawn/dusk, indoor lighting)\n"
            "- Various surface materials (concrete, asphalt, grass, sand, wood, carpet)\n\n"
            "Some examples of location descriptions:\n"
            f"{examples_text}\n\n"
            "Return ONLY a numbered list of location descriptions, each 10-15 words long."
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
                return [
                    f"urban street with {object_name}",
                    f"park area with {object_name}",
                    f"indoor surface with {object_name}",
                    f"parking lot with {object_name}",
                    f"riverside with {object_name}"
                ]
            
            return scenes
            
        except Exception as e:
            print(f"Error generating scenes with LLM: {e}")
            # Fall back to default scenes on error
            return [
                f"urban street with {object_name}",
                f"park area with {object_name}",
                f"indoor surface with {object_name}",
                f"parking lot with {object_name}",
                f"riverside with {object_name}"
            ]
    
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
        
        # System and user prompts for scene inference
        system_instruction = (
            "You are an expert in environmental photography and waste management. "
            "Create realistic scenarios where litter or recyclable items might naturally be found."
        )
        
        user_message = (
            f"Suggest a realistic scene description where {num_objects} {object_name}(s) might naturally be found. "
            "The scene should be described in 5-10 words only, focusing on the location and context. "
            "Be specific and realistic. Don't use bullet points or numbering. "
            "Don't include explanations. Reply with only the scene description."
        )
        
        try:
            # Generate the scene with LLM
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    max_output_tokens=50
                )
            )
            
            # Clean up the response
            scene = response.text.strip().strip('"\'').replace('\n', ' ')
            
            # Fall back to predefined scenes if response is too short or long
            if len(scene.split()) < 2 or len(scene.split()) > 15:
                appropriate_scenes = self.get_appropriate_scenes(object_name)
                scene = random.choice(appropriate_scenes)
                
            return scene
            
        except Exception as e:
            print(f"Error inferring scene: {e}")
            # Fall back to predefined scenes on error
            appropriate_scenes = self.get_appropriate_scenes(object_name)
            return random.choice(appropriate_scenes)
    
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
            prompt = (
                f"An amateurish smartphone photo of {num_objects} {object_name}(s) in a {scene_type}. "
                f"The {object_name}(s) should look accidentally captured, randomly positioned and strongly off-center. "
                "Some objects should be partially cut off or awkwardly positioned in the frame. "
                "Typical flawed raw smartphone shot with bad white balance, noticeable digital noise, inconsistent exposure. "
                "Visible camera shake, unstable handheld shot with visible tilt, poor composition. "
                "Unprocessed, with flat colors, weak contrast, and signs of poor lighting conditions. "
                "Looks like someone quickly took the photo without caring about composition or quality. "
                "The horizon is noticeably tilted (10-25 degrees), with accidental finger intrusion at the edge of frame possible."
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
        
        # System instruction for prompt generation
        system_instruction = (
            "You are an expert in generating prompts for AI image generators to create AUTHENTIC AMATEUR photographs. "
            f"Create a prompt for a scene containing {num_objects} {object_name}(s) in this location: '{scene_type}'. "
            "The prompt must result in an image that looks like a genuine, unprocessed RAW file straight from a basic smartphone camera. "
            "Include specific details about:\n"
            "1. BAD AMATEUR PHOTOGRAPHY - technical flaws common in casual phone photos (bad white balance, poor exposure)\n"
            "2. STRONGLY OFF-CENTER COMPOSITION - objects placed randomly as if accidentally captured, NOT artistically off-center\n"
            "3. AWKWARD FRAMING - objects may be partially cut off, too small in frame, or poorly spaced\n"
            "4. INCONSISTENT LIGHTING - unflattering lighting, harsh shadows, mixed light sources, or blown-out areas\n"
            "5. VISIBLE TECHNICAL FLAWS - digital noise, chromatic aberration, lens flare, over-compression artifacts\n"
            "6. CAMERA SHAKE - noticeable blur from unstable handheld shooting or subject movement\n"
            "7. FLAT COLORS AND CONTRAST - lacks post-processing enhancement, looks like untouched RAW file\n\n"
            "The image must look genuinely amateurish - as if quickly taken by a non-photographer using a basic smartphone camera "
            "with no understanding of composition or technical settings, yet the objects must still be identifiable."
        )
        
        # User message for prompt generation
        user_message = (
            f"Create a photo generation prompt for a genuinely amateurish smartphone snapshot showing {num_objects} {object_name}(s) "
            f"in this location: '{scene_type}'.\n\n"
            "CRITICAL REQUIREMENTS:\n"
            f"- The {num_objects} {object_name}(s) must be visible enough for identification, but NOT perfectly captured\n"
            "- DELIBERATELY BAD PHOTOGRAPHY - simulate the flaws of untouched RAW files from basic smartphone cameras\n"
            "- AWKWARD FRAMING - objects positioned randomly as if accidentally captured, not artistically composed\n"
            "- TECHNICAL ISSUES - include multiple realistic technical flaws (noise, bad white balance, focus hunting)\n"
            "- LIGHTING PROBLEMS - unflattering lighting conditions, inconsistent exposure, blown highlights\n"
            "- CAMERA SHAKE - visible blur from unstable handheld shooting\n"
            "- COLOR ISSUES - flat colors, weak contrast, poor white balance typical of unprocessed RAW files\n"
            "- TILTED HORIZON - between 5-25 degrees off-level as if hastily shot without care\n"
            "- NO ARTISTIC QUALITIES - absolutely avoid any hint of professional or artistic photography\n\n"
            "DO NOT use terms like 'photorealistic', 'high quality', 'detailed', 'professional', 'beautiful', or 'stunning'.\n"
            "Instead, emphasize terms like 'unprocessed', 'amateur', 'casual', 'raw file', 'smartphone camera', 'unstable', 'flawed'.\n\n"
            "Create a unique prompt that will generate a truly authentic-looking amateur photo that appears to be straight from a smartphone's camera sensor."
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
            prompt = (
                f"An amateurish smartphone photo of {num_objects} {object_name}(s) in a {scene_type}. "
                f"The {object_name}(s) should look accidentally captured, randomly positioned and strongly off-center. "
                "Some objects should be partially cut off or awkwardly positioned in the frame. "
                "Typical flawed raw smartphone shot with bad white balance, noticeable digital noise, inconsistent exposure. "
                "Visible camera shake, unstable handheld shot with visible tilt, poor composition. "
                "Unprocessed, with flat colors, weak contrast, and signs of poor lighting conditions. "
                "Looks like someone quickly took the photo without caring about composition or quality. "
                "The horizon is noticeably tilted (10-25 degrees), with accidental finger intrusion at the edge of frame possible."
            )
            return {
                "prompt": prompt,
                "scene": scene_type,
                "object_count": num_objects,
                "object": object_name
            }
    
    def generate_simple_prompt(self, object_name: str, scene_type: Optional[str] = None, 
                              num_objects: Optional[int] = None, use_llm: bool = True) -> Tuple[str, str, int]:
        """
        Generate a simple image prompt without using extensive LLM for the prompt itself.
        
        Args:
            object_name: The target object.
            scene_type: The scene description (if None, will be inferred).
            num_objects: Number of objects (if None, will be random between 1-3).
            use_llm: Whether to use LLM for scene inference if scene_type is None.
            
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
                # Use LLM to infer an appropriate scene
                scene_type = self.infer_scene(object_name, num_objects)
            else:
                # Use predefined scenes
                appropriate_scenes = self.get_appropriate_scenes(object_name)
                scene_type = random.choice(appropriate_scenes)
        
        # Generate a standard prompt
        prompt = (
            f"An amateurish smartphone photo of {num_objects} {object_name}(s) in a {scene_type}. "
            f"The {object_name}(s) should look accidentally captured, randomly positioned and strongly off-center. "
            "Some objects should be partially cut off or awkwardly positioned in the frame. "
            "Typical flawed raw smartphone shot with bad white balance, noticeable digital noise, inconsistent exposure. "
            "Visible camera shake, unstable handheld shot with visible tilt, poor composition. "
            "Unprocessed, with flat colors, weak contrast, and signs of poor lighting conditions. "
            "Looks like someone quickly took the photo without caring about composition or quality. "
            "The horizon is noticeably tilted (10-25 degrees), with accidental finger intrusion at the edge of frame possible."
        )
        
        return prompt, scene_type, num_objects
    
    def generate_simple_prompts(self, object_type: str, count: int = 1) -> List[Dict[str, str]]:
        """
        Generate simple prompts using predefined templates.
        
        Args:
            object_type: Type of object to generate prompts for (e.g., "empty can")
            count: Number of prompts to generate
            
        Returns:
            List of prompt dictionaries with scene, prompt, and object
        """
        if object_type not in OBJECT_SCENE_MAP:
            raise ValueError(f"Unsupported object type: {object_type}. Supported types: {list(OBJECT_SCENE_MAP.keys())}")
        
        scenes = OBJECT_SCENE_MAP[object_type]
        selected_scenes = random.sample(scenes, min(count, len(scenes)))
        
        # If we need more scenes than available, cycle through them
        if count > len(scenes):
            additional_needed = count - len(scenes)
            additional_scenes = [scenes[i % len(scenes)] for i in range(additional_needed)]
            selected_scenes.extend(additional_scenes)
        
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
    
    def generate_llm_prompts(
        self, 
        object_type: str, 
        count: int = 1,
        min_objects: int = 1,
        max_objects: int = 5,
        exact_objects: Optional[int] = None,
        advanced: bool = False
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
            
        Returns:
            List of prompt dictionaries with scene, prompt, object, and object_count
        """
        prompts = []
        
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