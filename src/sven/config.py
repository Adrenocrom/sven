"""
Configuration management for the Sven project.
Supports environment variables and different profiles (dev, prod).
"""

import os
import json
from typing import Any, Dict

def load_config(profile: str = "dev") -> Dict[str, Any]:
    """
    Load configuration from a JSON file and override with environment variables.
    
    Args:
        profile (str): The profile to use (e.g., 'dev', 'prod').
        
    Returns:
        Dict[str, Any]: The loaded configuration.
    """
    # Default config path
    config_path = "config.json"
    
    # Load base configuration from file
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    # If a profile is specified and exists in the config, we could potentially 
    # load specific settings for that profile. For now, let's just ensure 
    # it's handled if added to config.json later.
    if "profiles" in config and profile in config["profiles"]:
        config.update(config["profiles"][profile])

    # Override with environment variables
    # Example: SVEN_MODEL overrides 'model' key
    if "model" in config and os.getenv("SVEN_MODEL"):
        config["model"] = os.getenv("SVEN_MODEL")
    
    if "system_prompt" in config and os.getenv("SVEN_SYSTEM_PROMPT"):
        config["system_prompt"] = os.getenv("SVEN_SYSTEM_PROMPT")

    # Handle options if they exist
    if "options" in config:
        opt_dict = config["options"]
        # Example: SVEN_TEMPERATURE overrides 'temperature' inside options
        if "temperature" in opt_dict and os.getenv("SVEN_TEMPERATURE"):
            opt_dict["temperature"] = float(os.getenv("SVEN_TEMPERATURE"))

    return config
