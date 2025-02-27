"""
Hotdog Classifier implementation using OpenRouter API.
"""

import requests
from pathlib import Path
import logging
from src.utils.logger import setup_logger
from src.utils.image_utils import (
    is_valid_url,
    download_image,
    cleanup_image,
    is_base64_image,
    save_base64_image
)
import src.config as config

# Initialize logger
logger = setup_logger(__name__)

class HotdogClassifier:
    """Class to handle hotdog image classification using OpenRouter API."""
    
    def __init__(self):
        """Initialize the classifier with API configuration."""
        self.api_url = config.API_URL
        self.headers = config.API_HEADERS
        self.timeout = config.REQUEST_TIMEOUT
        logger.info("HotdogClassifier initialized")
        logger.debug(f"API URL: {self.api_url}")
        logger.debug(f"Timeout: {self.timeout} seconds")

    def test_api_connection(self) -> bool:
        """Test the connection to the OpenRouter API."""
        try:
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": self.headers["Authorization"]},
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.debug("API connection test successful")
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return False

    def classify_image(self, image_path: str | Path) -> bool:
        """
        Classify if an image contains a hotdog.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            bool: True if hotdog, False if not
        """
        logger.info(f"Starting classification for image: {image_path}")
        
        try:
            # Test API connection first
            if not self.test_api_connection():
                raise ConnectionError("Cannot connect to OpenRouter API")

            # Encode image to base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
                import base64
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare payload
            payload = {
                "model": config.MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Does this image contain a hotdog? Please respond with only 'Hotdog' or 'Not Hotdog'."
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        ]
                    }
                ],
                "max_tokens": config.MAX_TOKENS
            }

            # Make API request
            logger.debug("Sending request to OpenRouter API")
            logger.debug(f"Using model: {config.MODEL_NAME}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            # Log response details
            logger.debug(f"API Response Status: {response.status_code}")
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            answer = result['choices'][0]['message']['content'].strip().lower()
            
            # Log results
            logger.debug(f"Raw API response: {result}")
            logger.info(f"Classification answer: {answer}")
            
            is_hotdog = "hotdog" in answer and "not" not in answer
            logger.info(f"Final classification: {'Hotdog' if is_hotdog else 'Not Hotdog'}")
            
            return is_hotdog

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise ConnectionError("Cannot connect to OpenRouter API")
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error: {str(e)}")
            raise TimeoutError("API request timed out")
            
        except Exception as e:
            logger.error(f"Unexpected error during classification: {str(e)}")
            raise