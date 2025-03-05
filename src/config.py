"""
Configuration settings for the Real Hotdog Classifier.
"""

import os
from dotenv import load_dotenv
import logging
from pathlib import Path

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv('OPENROUTER_API_KEY')
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

# Updated API URLs with correct endpoint
API_BASE_URL = "https://api.openrouter.ai"  # Changed from openrouter.ai to api.openrouter.ai
API_URL = f"{API_BASE_URL}/api/v1/chat/completions"

API_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5000",
    "X-Title": "Real Hotdog Classifier",
    'C-Model': 'gpt-4-vision-preview',  # Added model specification in header
    'C-Version': '2024-02-28'  # Added version
}

# Model Configuration
MODEL_NAME = "gpt-4-vision-preview"
MAX_TOKENS = 50

# File Upload Configuration
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')

# Default to 10MB if MAX_IMAGE_SIZE is not set
DEFAULT_MAX_SIZE = 10 * 1024 * 1024  # 10MB in bytes
try:
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_IMAGE_SIZE', DEFAULT_MAX_SIZE))
except (TypeError, ValueError):
    MAX_CONTENT_LENGTH = DEFAULT_MAX_SIZE

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Request Configuration
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))

# Flask Configuration
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', '5000'))

# Create required directories
for directory in [UPLOAD_FOLDER, 'logs']:
    Path(directory).mkdir(exist_ok=True)

# Test API connectivity on startup
def test_api_connection():
    """Test API connectivity and return detailed error if fails."""
    import requests
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/models",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=5
        )
        response.raise_for_status()
        return True, "API connection successful"
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if isinstance(e, requests.exceptions.ConnectionError):
            return False, "Cannot connect to OpenRouter API. Please check your internet connection."
        elif isinstance(e, requests.exceptions.Timeout):
            return False, "API connection timed out. Please try again."
        elif isinstance(e, requests.exceptions.HTTPError):
            if e.response.status_code == 401:
                return False, "Invalid API key. Please check your OPENROUTER_API_KEY."
            return False, f"HTTP Error: {e.response.status_code}"
        return False, f"API Error: {error_msg}"

# Test API connection on startup
api_status, api_message = test_api_connection()
if not api_status:
    logging.error(f"API Connection Error: {api_message}")