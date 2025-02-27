"""
Configuration module for the Hotdog Classifier application.
Handles all configuration settings and environment variables.
"""

import os
from dotenv import load_dotenv
import logging
from pathlib import Path

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API Configuration
API_KEY = os.getenv('OPENROUTER_API_KEY')
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

# Updated API URLs - note the capital AI
API_BASE_URL = "https://openrouter.AI"
API_URL = "https://openrouter.AI/api/v1/chat/completions"

# Updated API Headers
API_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5000"
}

# Model Configuration
MODEL_NAME = "openai/gpt-4o-mini"
MAX_TOKENS = 50

# File Upload Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))

# Set maximum content length (10MB default)
DEFAULT_MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB in bytes

try:
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_IMAGE_SIZE', DEFAULT_MAX_CONTENT_LENGTH))
except (TypeError, ValueError):
    MAX_CONTENT_LENGTH = DEFAULT_MAX_CONTENT_LENGTH

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Request Configuration
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))  # seconds

# Flask Configuration
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', '5000'))

# Logging Configuration
LOG_DIR = BASE_DIR / 'logs'
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Create required directories
LOG_DIR.mkdir(exist_ok=True)
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)