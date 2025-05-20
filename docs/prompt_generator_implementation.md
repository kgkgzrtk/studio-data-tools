# Prompt Generator Implementation Details

This document provides technical details about the implementation of the prompt generation system, focusing on the scene generation and prompt creation processes.

## Code Structure

```mermaid
classDiagram
    class PromptGenerator {
        -api_key: str
        -client: genai.Client
        -model_name: str
        +__init__(api_key, model)
        +get_appropriate_scenes(object_name)
        +generate_diverse_scenes(object_name, num_scenes)
        +infer_scene(object_name, num_objects)
        +generate_realistic_prompt(object_name, scene_type, num_objects, min_objects, max_objects)
        +generate_simple_prompt(object_name, scene_type, num_objects, use_llm)
        +generate_simple_prompts(object_type, count)
        +generate_llm_prompts(object_type, count, min_objects, max_objects, exact_objects, advanced)
    }
```

## Dynamic Scene Generation

### Scene Diversity with `generate_diverse_scenes`

The `generate_diverse_scenes` method is a key component for creating varied scene descriptions:

```mermaid
flowchart TD
    A[Start: generate_diverse_scenes] --> B{API Available?}
    B -->|No| C[Use predefined scenes]
    B -->|Yes| D[Get example scenes from OBJECT_SCENE_MAP]
    D --> E[Create system instruction]
    E --> F[Create user message]
    F --> G[Call Gemini API]
    G --> H{Successful?}
    H -->|Yes| I[Process response]
    H -->|No| J[Use fallback scenes]
    I --> K[Clean up scene texts]
    K --> L[Return generated scenes]
    C --> L
    J --> L
```

Implementation details:
1. Uses Gemini 1.5 Pro model for higher creativity
2. Creates a system instruction that positions the AI as a "location scout"
3. Provides examples from the predefined scene map to guide generation
4. Sets temperature to 0.8 for creative variety
5. Processes response by:
   - Splitting into lines
   - Removing numbering and formatting
   - Cleaning up the text
6. Includes robust error handling with fallback to predefined scenes

### Context-Aware Scene Inference with `infer_scene`

The `infer_scene` method dynamically creates appropriate scenes for a specific object:

```mermaid
flowchart TD
    A[Start: infer_scene] --> B{API Available?}
    B -->|No| C[Use random predefined scene]
    B -->|Yes| D[Create system instruction]
    D --> E[Create user message]
    E --> F[Call Gemini API with 1.5-flash model]
    F --> G{Successful?}
    G -->|Yes| H[Clean up response]
    G -->|No| I[Use random predefined scene]
    H --> J{Valid length?}
    J -->|Yes| K[Return scene]
    J -->|No| L[Use random predefined scene]
    C --> K
    I --> K
    L --> K
```

Implementation details:
1. Uses faster Gemini 1.5 Flash model for quicker inference
2. System instruction positions AI as expert in environmental photography
3. User message requests brief 5-10 word descriptions
4. Sets temperature to 0.7 (slightly lower than for diverse generation)
5. Validates response quality (length check)
6. Falls back to predefined scenes if generation fails

## Prompt Generation Techniques

### 1. Realistic Prompt Generation

The `generate_realistic_prompt` method creates detailed, technically-rich prompts:

```mermaid
flowchart TD
    A[Start: generate_realistic_prompt] --> B{API Available?}
    B -->|No| C[Use fallback template]
    B -->|Yes| D[Determine number of objects]
    D --> E[Create detailed system instruction]
    E --> F[Create specific user message]
    F --> G[Call Gemini 1.5 Pro]
    G --> H{Successful?}
    H -->|Yes| I[Return prompt data]
    H -->|No| J[Use fallback template]
    C --> K[Return prompt data]
    J --> K
    I --> K
```

Key implementation features:
1. Uses extensive system instructions (700+ tokens) that guide the model to:
   - Create amateur photography descriptions
   - Include technical flaws like bad white balance, noise
   - Create off-center compositions
   - Include lighting problems and camera shake
2. Uses structured prompting approach with specific requirements
3. Returns complete data object with prompt, scene, object count, and object

### 2. LLM Prompt Generation

The `generate_llm_prompts` method offers the most flexible approach:

```mermaid
flowchart TD
    A[Start: generate_llm_prompts] --> B[Determine object count]
    B --> C[Choose system instruction]
    C --> D{Advanced mode?}
    D -->|Yes| E[Create advanced instruction]
    D -->|No| F[Create basic instruction]
    E --> G[Call Gemini API]
    F --> G
    G --> H{Success?}
    H -->|Yes| I[Create final prompt]
    H -->|No| J[Use fallback simple prompt]
    I --> K[Add to prompts list]
    J --> K
    K --> L{More prompts needed?}
    L -->|Yes| B
    L -->|No| M[Return prompts]
```

Advanced features:
1. Support for exact object counts or random ranges
2. Two instruction modes:
   - Basic mode: Simple scene descriptions
   - Advanced mode: Detailed photographer-style descriptions
3. Processing loop to generate multiple prompts at once
4. Fallback to simple prompts on API failure

## Prompt Engineering Techniques

The module employs several advanced prompt engineering techniques:

### 1. Role-Based Prompting

Each method assigns a specific expertise role to the LLM:
- "Expert location scout" for diverse scenes
- "Expert in environmental photography" for scene inference
- "Expert in generating prompts for AI image generators" for realistic prompts

```mermaid
flowchart LR
    A[Role Assignment] --> B[Expert Location Scout]
    A --> C[Environmental Photography Expert]
    A --> D[AI Prompt Engineering Expert]
    B --> E[Scene Generation]
    C --> F[Scene Inference]
    D --> G[Prompt Creation]
```

### 2. Detailed Parameter Control

Temperature settings are carefully tuned for each use case:
- 0.8 for creative diversity in scene generation
- 0.7 for more controlled scene inference
- 0.8 for realistic prompt generation with balanced creativity

### 3. Multi-Step Processing

```mermaid
flowchart TD
    A[Raw Response] --> B[Line Splitting]
    B --> C[Numbering Removal]
    C --> D[Formatting Cleanup]
    D --> E[Validation Checks]
    E --> F[Processed Result]
```

### 4. Contextual Examples

For `generate_diverse_scenes`, examples from the same object category are included in the prompt to guide the model toward appropriate scene types.

## Integration with Static Data

Static predefined data (`OBJECT_SCENE_MAP` and `GENERAL_SCENES`) serves multiple purposes:

1. **Fallback mechanism** when API is unavailable or fails
2. **Inspiration source** for the LLM (examples provided in prompts)
3. **Validation reference** to ensure outputs are appropriate

```mermaid
flowchart TD
    A[Static Data] --> B[Fallback Mechanism]
    A --> C[Inspiration Source for LLM]
    A --> D[Validation Reference]
    B --> E[Ensures System Reliability]
    C --> F[Guides Model Output]
    D --> G[Quality Control]
```

## Error Handling and Robustness

All LLM-based methods include comprehensive error handling:

1. API availability checks
2. Try-except blocks around API calls
3. Response validation (length checks, content checks)
4. Fallback to static generation methods
5. Warning messages for tracking issues

## Performance Considerations

The module balances quality and performance:

1. Uses different Gemini models based on needs:
   - Gemini 1.5 Pro for detailed prompt generation
   - Gemini 1.5 Flash for quicker scene inference
   - Default model (`gemini-2.0-flash-001`) configurable at initialization
2. Caches environment variables (API keys)
3. Reuses existing client connection
4. Optional parameters to control generation complexity

## Usage Examples

### Example 1: Generating Diverse Scenes

```python
from studio_data_tools.core.prompt_generator import PromptGenerator

# Initialize with API key
generator = PromptGenerator(api_key="YOUR_API_KEY")

# Generate 5 diverse scenes for empty cans
scenes = generator.generate_diverse_scenes("empty can", num_scenes=5)
print(scenes)
```

Output:
```
[
  "Urban alleyway with empty cans beside graffiti wall",
  "Park bench with discarded cans under afternoon shadows",
  "Convenience store parking lot with scattered cans",
  "Riverside rocks with empty cans caught in driftwood",
  "Festival grounds morning after with empty cans on trampled grass"
]
```

### Example 2: Creating Multiple Advanced Prompts

```python
from studio_data_tools.core.prompt_generator import PromptGenerator

# Initialize generator
generator = PromptGenerator()

# Generate 3 advanced prompts for plastic bottles with 2-4 objects
prompts = generator.generate_llm_prompts(
    object_type="plastic bottle",
    count=3,
    min_objects=2,
    max_objects=4,
    advanced=True
)

for prompt in prompts:
    print(f"Scene: {prompt['scene']}")
    print(f"Count: {prompt['object_count']}")
    print(f"Prompt: {prompt['prompt'][:100]}...\n")
```

## Implementation Considerations

When modifying or extending the prompt generator:

1. **API Changes**: If Google's Genai API changes, update the client initialization and model calls
2. **New Object Types**: Add new object types to `OBJECT_SCENE_MAP` with appropriate scenes
3. **Performance Tuning**: Adjust model selection and temperature parameters based on needs
4. **Error Handling**: Maintain the fallback mechanisms to ensure robustness 