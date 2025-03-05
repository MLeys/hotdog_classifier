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
                f"{config.API_BASE_URL}/api/v1/models",
                headers={"Authorization": self.headers["Authorization"]},
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.debug("API connection test successful")
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return False

    def classify_image(self, image_path: str | Path) -> tuple[bool, str]:
        """
        Classify if an image contains a real, edible hotdog.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            tuple[bool, str]: (is_hotdog, description) where:
                - is_hotdog: True if real hotdog, False if not
                - description: Brief description of what's in the image
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
                                "text": "First, tell me if this is a hotdog (answer EXACTLY 'Hotdog' or 'Not Hotdog'). Then on a new line, briefly describe what you see in 15 words or less."
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        ]
                    }
                ],
                "max_tokens": 100
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
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            answer_text = result['choices'][0]['message']['content'].strip()
            
            # Split into classification and description
            lines = answer_text.split('\n', 1)
            is_hotdog = lines[0].lower().strip() == "hotdog"
            description = lines[1].strip() if len(lines) > 1 else "No description provided"
            
            # Log results
            logger.info(f"Classification result: {is_hotdog}")
            logger.info(f"Description: {description}")
            
            return is_hotdog, description

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            raise ConnectionError("Cannot connect to OpenRouter API")
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error: {str(e)}")
            raise TimeoutError("API request timed out")
            
        except Exception as e:
            logger.error(f"Unexpected error during classification: {str(e)}")
            raise