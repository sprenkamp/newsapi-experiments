#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration utilities for the application.
"""

import os
import sys
from typing import Dict, Any

from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables.
    
    Returns:
        Dictionary with configuration values.
    """
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        print("Error: NEWS_API_KEY not found in environment variables.")
        print("Please create a .env file with your API key.")
        sys.exit(1)
    
    # Create configuration dictionary
    config = {
        'api_key': api_key,
        'days_back': int(os.getenv('DAYS_BACK', '7')),
        'output_dir': os.getenv('OUTPUT_DIR', 'data'),
    }
    
    # Ensure output directory exists
    os.makedirs(config['output_dir'], exist_ok=True)
    
    return config
