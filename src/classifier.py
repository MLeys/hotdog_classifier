"""
Hotdog Classifier implementation using OpenRouter API.
"""

import requests
from pathlib import Path
import logging
from src.utils.logger import setup_logger
from src.utils.image_utils import get_image_data
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
                f"{config.API_BASE_URL}/api/v1/auth/key",
                headers={"Authorization": self.headers["Authorization"]},
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.debug("API connection test successful")
            return True
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if isinstance(e, requests.exceptions.ConnectionError):
                logger.error("Cannot connect to OpenRouter API. Please check your internet connection.")
            elif isinstance(e, requests.exceptions.Timeout):
                logger.error("API connection timed out. Please try again.")
            elif isinstance(e, requests.exceptions.HTTPError):
                if e.response.status_code == 401:
                    logger.error("Invalid API key. Please check your OPENROUTER_API_KEY.")
                else:
                    logger.error(f"HTTP Error: {e.response.status_code}")
            else:
                logger.error(f"API Error: {error_msg}")
            return False

    def classify_image(self, image_path: str | Path) -> bool:
        """
        Classify if an image contains a real, edible hotdog.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            bool: True if real hotdog, False if not
        """
        logger.info(f"Starting classification for image: {image_path}")
        
        try:
            # Test API connection first
            if not self.test_api_connection():
                raise ConnectionError("Cannot connect to OpenRouter API")

            # Get base64 encoded image
            base64_image = get_image_data(image_path)
            
            # Prepare payload
            payload = {
                "model": config.MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image and determine if it shows a real, edible hotdog (frankfurter/sausage in a bun). Answer with EXACTLY 'Hotdog' ONLY if it's a real, edible hotdog. Answer with EXACTLY 'Not Hotdog' for anything else including drawings, toys, costumes, or non-edible representations of hotdogs. The item must be an actual edible food item to qualify as a hotdog."
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
            
            is_hotdog = answer == "hotdog"
            logger.info(f"Final classification: {'Real Hotdog' if is_hotdog else 'Not a Real Hotdog'}")
            
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