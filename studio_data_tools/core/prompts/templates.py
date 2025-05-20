"""
Prompt templates module.

This module contains templates for various prompts used in the prompt generator.
"""

# System instruction templates for LLM

# Template for dynamic scene generation
DYNAMIC_SCENE_SYSTEM_INSTRUCTION = """
You are an expert environmental scene designer specialized in creating realistic contexts 
where objects might be found. Generate {num_scenes} diverse and realistic locations or settings 
where '{object_name}' might naturally be found in everyday environments.
Include a variety of different settings (both indoor and outdoor).
Each description should be 10-15 words and focus on physical setting only.
"""

# Template for dynamic scene generation user message
DYNAMIC_SCENE_USER_MESSAGE = """
Create {num_scenes} diverse and realistic scene descriptions where one might find '{object_name}'.

Include a variety of settings such as:
- Residential spaces (kitchens, bathrooms, living rooms, bedrooms)
- Workplaces (offices, break rooms, conference rooms)
- Public buildings (stores, restaurants, schools, libraries)
- Urban environments (streets, alleys, parking lots, sidewalks)
- Natural areas (parks, forests, beaches, rivers)
- Suburban settings (yards, driveways, neighborhood streets)

Number each scene in a simple list format.
Example format:
1. Kitchen counter with fruit bowl
2. Park bench under maple trees
3. Office desk with computer monitor

Return ONLY a numbered list of scene descriptions.
"""

# Template for diverse scene generation
DIVERSE_SCENE_SYSTEM_INSTRUCTION = """
You are an expert location scout for realistic documentary photography.
Generate {num_scenes} diverse and realistic locations where {object_name}(s) might be found in everyday environments.
The locations should vary in terms of settings, surfaces, and contexts.
Be specific about the environment, surface material, and nearby elements.
Each location description should be 10-15 words and focus on physical setting only.
"""

# Template for diverse scene generation user message
DIVERSE_SCENE_USER_MESSAGE = """
Generate {num_scenes} diverse locations where {object_name}(s) might be found.
Include a mix of:
- Urban environments (streets, sidewalks, parking lots)
- Natural settings (parks, beaches, wooded areas)
- Indoor locations (floors, tables, shelves)
- Various surface materials (concrete, asphalt, grass, sand, wood, carpet)

Some examples of location descriptions:
{examples_text}

Return ONLY a numbered list of location descriptions, each 10-15 words long.
"""

# Template for scene inference
SCENE_INFERENCE_SYSTEM_INSTRUCTION = """
You are an expert in environmental photography.
Create a single realistic scene where {object_name}(s) might naturally be found.
Consider various settings like homes, offices, stores, streets, parks, etc.
"""

# Template for scene inference user message
SCENE_INFERENCE_USER_MESSAGE = """
Generate ONE realistic scene description (5-10 words only) where {num_objects} {object_name}(s) might be found.

- Focus on location and context only
- Be specific about surfaces and environment
- Keep it brief (5-10 words total)

Reply with ONLY the scene description, no explanation.
"""

# Template for realistic prompt generation
REALISTIC_PROMPT_SYSTEM_INSTRUCTION = """
You are an expert in generating prompts for AI image generators to create AUTHENTIC AMATEUR photographs.
Create a prompt for a scene containing {num_objects} {object_name}(s) in this location: '{scene_type}'.
The prompt must result in an image that looks like a genuine, unprocessed file straight from a basic smartphone camera.

Include specific details about:
1. NATURAL INTEGRATION - objects should blend naturally with the environment as if they belong there
2. VARIED SIZES - objects should vary in size (small, medium) randomly throughout the scene
3. RANDOM POSITIONING - objects should be scattered throughout the frame at different depths and positions
4. PARTIAL VISIBILITY - some objects may be partially hidden behind other elements or cut off by frame edges
5. DEPTH VARIATION - objects should appear at different distances from the camera (foreground, mid-ground, background)
6. HEIGHT VARIATION - objects should be positioned at different heights within the scene
7. AMATEUR PHOTOGRAPHY - technical flaws common in casual phone photos
8. OFF-CENTER COMPOSITION - objects placed randomly as if accidentally captured
9. VISIBLE TECHNICAL FLAWS - digital noise, lens flare, compression artifacts
10. CAMERA SHAKE - some blur from unstable handheld shooting
11. FLAT COLORS AND CONTRAST - lacks post-processing enhancement

The image should look amateurish - as if quickly taken by someone using a basic smartphone camera
with little understanding of composition or technical settings, yet the objects must still be identifiable.
"""

# Template for realistic prompt generation user message
REALISTIC_PROMPT_USER_MESSAGE = """
Create a photo generation prompt for an amateur smartphone snapshot showing {num_objects} {object_name}(s)
in this location: '{scene_type}'.

REQUIREMENTS:
- NATURAL INTEGRATION - the {object_name}(s) should blend naturally with the environment as if they belong there
- VARIED SIZES - include {object_name}(s) of different sizes (small, medium) randomly distributed
- RANDOM POSITIONING - scatter the {object_name}(s) throughout the frame in a natural, unplanned way
- PARTIAL VISIBILITY - some {object_name}(s) may be partially hidden or obscured by other elements
- DEPTH VARIATION - place {object_name}(s) at different distances (foreground, mid-ground, background)
- HEIGHT VARIATION - position {object_name}(s) at different heights within the scene
- The {num_objects} {object_name}(s) must be visible enough for identification, but NOT perfectly captured
- AMATEUR PHOTOGRAPHY - simulate the flaws of untouched files from basic smartphone cameras
- AWKWARD FRAMING - objects positioned randomly as if accidentally captured
- TECHNICAL ISSUES - include realistic technical flaws (noise, focus issues)
- CAMERA SHAKE - some blur from handheld shooting
- COLOR ISSUES - flat colors, average contrast typical of unprocessed files
- TILTED HORIZON - slightly off-level as if hastily shot
- NO ARTISTIC QUALITIES - avoid any hint of professional photography

DO NOT use terms like 'photorealistic', 'high quality', 'detailed', 'professional', 'beautiful', or 'stunning'.
Instead, use terms like 'unprocessed', 'amateur', 'casual', 'smartphone camera', 'unstable', 'flawed'.

Create a unique prompt that will generate an authentic-looking amateur photo with naturally integrated objects.
"""

# Fallback prompt template
FALLBACK_PROMPT_TEMPLATE = """
An amateur smartphone photo of {num_objects} {object_name}(s) in a {scene_type}.
The {object_name}(s) blend naturally with the environment, varying in size from small to medium.
Objects are randomly scattered throughout the scene, some partially visible or obscured by other elements.
Some {object_name}(s) appear in the foreground, others in the mid-ground or background at different depths.
The {object_name}(s) are positioned at various heights and angles, creating a natural, unplanned arrangement.
Typical smartphone shot with average white balance, some digital noise, uneven exposure.
Slight camera shake, handheld shot with minor tilt, casual composition.
Unprocessed, with standard colors and contrast.
Looks like someone quickly took the photo without much attention to composition.
"""

# Enhanced fallback prompt template with more emphasis on natural placement and technical issues
ENHANCED_FALLBACK_PROMPT_TEMPLATE = """
An amateur smartphone photo of {num_objects} {object_name}(s) in a {scene_type}.
The {object_name}(s) blend naturally with the surroundings, appearing as if they've been there for some time.
Objects vary in size (some small, some medium) and are distributed randomly throughout the frame.
Some {object_name}(s) are partially hidden behind other elements or cut off by the frame edges.
The {object_name}(s) are positioned at various distances from the camera - some close, some far away.
Objects appear at different heights and positions within the scene, creating a natural, unplanned distribution.
Typical smartphone shot with poor white balance, visible digital noise, uneven exposure.
Noticeable camera shake, handheld shot with tilted horizon, casual composition.
Unprocessed, with flat colors and low contrast.
Harsh shadows or blown highlights, poor lighting conditions.
Looks like someone quickly took the photo without much attention to composition or lighting.
"""