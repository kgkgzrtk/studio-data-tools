"""
General scenes module.

This module contains general scene descriptions and default scenes for various environments.
"""

# General scenes for fallback
GENERAL_SCENES = [
    "urban street with litter",
    "park area",
    "kitchen counter",
    "office desk",
    "parking lot",
    "riverside or beach",
    "grassy field",
    "restaurant table",
    "store shelf",
    "bedroom floor"
]

# Default scenes with placeholders for object names
DEFAULT_SCENES = [
    "kitchen counter with {object}",
    "bathroom corner with {object}",
    "office desk with {object}",
    "bedroom with {object} on nightstand",
    "storage room with {object}",
    "apartment hallway with {object}",
    "attic with {object}",
    "classroom with {object}",
    "restaurant booth with {object}",
    "hotel room with {object}",
    "urban street with {object}",
    "park bench with {object}",
    "parking lot with {object}",
    "beach with {object}",
    "backyard with {object}",
    "bus stop with {object}",
    "alleyway with {object}",
    "highway underpass with {object}"
]

# Environment types for fallback scene creation
ENVIRONMENT_TYPES = [
    "kitchen", "bathroom", "office", "bedroom", "living room", "hallway", 
    "basement", "attic", "garage", "classroom", "restaurant", "store",
    "urban", "park", "roadside", "beach", "forest", "sidewalk", "backyard", "alley"
]

# Surface types for fallback scene creation
SURFACE_TYPES = [
    "tile", "linoleum", "carpet", "hardwood", "concrete", "counter", "table", "desk", "shelf",
    "asphalt", "grass", "sand", "gravel", "mud", "pavement", "dirt", "stone"
]

# Lighting conditions for fallback scene creation
LIGHTING_CONDITIONS = [
    "dimly lit", "brightly lit", "naturally lit", "artificially lit", "shadowy",
    "sunlit", "fluorescent-lit", "evening", "morning", "noon", "dusk", "dawn"
]