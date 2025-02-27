# test_connection.py
import requests
from dotenv import load_dotenv
import os
import base64
from pathlib import Path
import logging
import json

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encode image: {str(e)}")
        raise

def test_gpt4_mini():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        logger.error("No API key found in environment variables")
        return

    # API Configuration
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000"
    }

    # Simple text test first
    text_payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "Is this model working? Please respond with a simple yes or no."
            }
        ]
    }

    try:
        logger.info("Testing basic model functionality...")
        response = requests.post(url, headers=headers, json=text_payload)
        logger.info(f"Text Test Status: {response.status_code}")
        logger.info(f"Text Test Response: {response.text}")

        # If text test worked, try with image
        if response.status_code == 200:
            test_image_path = "tests/test_images/hotdog01.jpg"
            
            if Path(test_image_path).exists():
                base64_image = encode_image(test_image_path)
                
                image_payload = {
                    "model": "openai/gpt-4o-mini",
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
                    ]
                }

                logger.info("\nTesting with image...")
                response = requests.post(url, headers=headers, json=image_payload)
                logger.info(f"Image Test Status: {response.status_code}")
                logger.info(f"Image Test Response: {response.text}")
            else:
                logger.error(f"Test image not found: {test_image_path}")

    except Exception as e:
        logger.error(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_gpt4_mini()