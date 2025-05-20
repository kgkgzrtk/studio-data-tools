#!/bin/bash
# Setup script for studio_data_tools using uv

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it first."
    echo "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Create the environment and install dependencies
echo "Installing studio_data_tools and dependencies..."
uv sync

# Setup environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from example..."
    cp .env.example .env
    echo "Please edit .env and add your Gemini API key"
fi

echo ""
echo "Setup complete! You can now run the tools using:"
echo "  uv run python -m studio_data_tools samples --object \"empty can\" --count 2"
echo "  uv run python -m studio_data_tools generate --help"
echo "  uv run python -m studio_data_tools prepare --help"
echo "" 