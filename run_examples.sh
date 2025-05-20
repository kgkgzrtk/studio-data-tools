#!/bin/bash
# Example commands for studio_data_tools with uv

# Make sure you're in the right directory and have activated your environment
# uv venv
# source .venv/bin/activate

# Generate 2 sample images of empty cans with advanced prompts
uv run python -m studio_data_tools samples --object "empty can" --count 2

# Generate 5 plastic bottle images with basic prompts
uv run python -m studio_data_tools generate --object "plastic bottle" --count 5

# Generate 10 glass bottle images with advanced prompts
uv run python -m studio_data_tools generate --object "glass bottle" --count 10 --advanced-prompts

# Prepare dataset from existing images without augmentation
# uv run python -m studio_data_tools prepare test_run/empty_can --output-file Cam0.zip

# Prepare dataset with augmentation to create 100 variants
# uv run python -m studio_data_tools prepare test_run/empty_can --output-file Cam0_augmented.zip --augment --num-images 100 