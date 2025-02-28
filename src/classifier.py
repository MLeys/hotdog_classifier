"""
Hotdog Classifier implementation using OpenRouter API.
"""

import requests
from pathlib import Path
import logging
from src.utils.logger import setup_logger
from src.utils.image_utils import encode_image
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

def classify_image(self, image_source: str | Path | bytes) -> bool:
    """
    Classify if an image contains a real, edible hotdog.
    
    Args:
        image_source: Image source (URL, file path, or bytes)
    
    Returns:
        bool: True if real hotdog food item, False if not
    """
    logger.info(f"Starting classification for image source: {image_source}")
    
    try:
        # Test API connection first
        if not self.test_api_connection():
            raise ConnectionError("Cannot connect to OpenRouter API")

        # Get image data
        logger.debug("Processing image")
        base64_image = get_image_data(image_source)
        
        # Prepare payload with detailed prompt
        payload = {
            "model": config.MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a precise food image classifier focusing only on real, edible hotdogs. Drawings, toys, costumes, or other representations do not count as real hotdogs."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this image and determine if it shows a real, edible hotdog (sausage/frankfurter in a bun).

Rules for classification:
- Must be a real food item that could be eaten
- Must have both a sausage/frankfurter AND a bun
- Must be clearly visible and identifiable

NOT considered a hotdog:
- Drawings or artwork
- Costumes or clothing
- Toys or plastic replicas
- Logos or graphics
- Just a sausage without bun
- Just a bun without sausage
- Other similar foods (hamburgers, sandwiches)
- Heavily processed/edited images

Respond ONLY with:
'Hotdog' - for real, edible hotdogs
'Not Hotdog' - for everything else"""
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
        
        # Check for real hotdog classification
        is_hotdog = "hotdog" in answer and "not" not in answer
        logger.info(f"Final classification: {'Real Hotdog' if is_hotdog else 'Not a Real Hotdog'}")
        
        return is_hotdog

    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise
        """
        Classify if an image contains a hotdog.
        
        Args:
            image_source: Image source (URL, file path, or bytes)
        
        Returns:
            bool: True if hotdog, False if not
        """
        logger.info(f"Starting classification for image source: {image_source}")
        
        try:
            # Test API connection first
            if not self.test_api_connection():
                raise ConnectionError("Cannot connect to OpenRouter API")

            # Get image data
            logger.debug("Processing image")
            base64_image = get_image_data(image_source)
            
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

        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            raise