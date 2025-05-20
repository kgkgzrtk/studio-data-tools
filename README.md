# Studio Data Tools

A toolkit for generating and processing images for studio datasets, featuring integration with Google's Imagen and Gemini LLM.

## Features

- **Image Generation**: Create realistic images of objects using Google's Gemini & Imagen models
- **Scene Estimation**: Use LLM to dynamically generate realistic scene descriptions
- **Advanced Prompts**: Generate photorealistic prompts for better image quality
- **Dataset Preparation**: Convert and augment images for studio use
- **Unified CLI**: Single command-line interface for all tools

## Installation

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager and resolver

### Quick Setup with uv

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd studio_data_tools
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Gemini API key
   ```

3. Install with uv (automatically creates a virtual environment):
   ```bash
   ./setup_uv.sh
   # Or run these commands manually:
   # uv venv .venv
   # uv pip install -e .
   ```

## Usage

The toolkit provides a unified command-line interface with several subcommands:

### Generate Sample Images (Quick)

```bash
uv run python -m studio_data_tools samples --object "empty can" --count 2
```

### Generate Images

Generate images using Google's image generation models:

```bash
uv run python -m studio_data_tools generate --object "empty can" --count 10
```

Options:
- `--object`: Object type to generate (e.g., "empty can", "plastic bottle")
- `--count`: Number of images to generate (default: 10)
- `--min-objects`: Minimum number of objects per image (default: 1)
- `--max-objects`: Maximum number of objects per image (default: 3)
- `--num-objects`: Exact number of objects per image (overrides min/max)
- `--output-dir`: Output directory for saving images (default: "generated_images")
- `--api-key`: Gemini API key (if not set in .env file)
- `--model`: Model to use (default: "gemini-2.0-flash-preview-image-generation")
- `--use-llm`: Use LLM to dynamically generate scenes (default: True)
- `--no-llm`: Disable LLM scene generation, use predefined scenes only
- `--advanced-prompts`: Use advanced LLM prompt generation for more realistic images

### Generate Sample Images

Generate a small set of high-quality sample images with advanced prompts:

```bash
uv run python -m studio_data_tools samples --object "plastic bottle" --count 5
```

### Prepare Dataset

Prepare a dataset for studio use:

```bash
uv run python -m studio_data_tools prepare path/to/images --output-file Cam0.zip
```

Options:
- `source_dir`: Source directory containing images
- `--output-file`, `-o`: Output ZIP filename (default: "Cam0.zip")
- `--width`: Width of output images (default: 640)
- `--height`: Height of output images (default: 480)
- `--augment`: Apply data augmentation techniques
- `--num-images`, `-n`: Number of augmented images to generate (default: 100, only used with --augment)

## Examples

### Generate 20 images of plastic bottles with advanced prompts

```bash
uv run python -m studio_data_tools generate --object "plastic bottle" --count 20 --advanced-prompts
```

### Create augmented dataset with 200 images

```bash
uv run python -m studio_data_tools prepare test_run/empty_can --output-file Cam0_augmented.zip --augment --num-images 200
```

## Development

If you want to contribute to this project:

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest
```

## API Key

You need a Google Gemini API key to use the image generation features. Get your API key from the [Google AI Studio](https://makersuite.google.com/app/apikey).

Set your API key in the `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

## Dependencies

All dependencies are managed in pyproject.toml:
- google-genai (Google's Generative AI Python SDK)
- Pillow (for image processing)
- numpy (fixed at 1.26.4 for compatibility with imgaug)
- imgaug (for image augmentation)
- python-dotenv (for environment variable management) 