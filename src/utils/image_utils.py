"""
Image processing utilities for the Hotdog Classifier.
Handles both local files and URLs.
"""

import os
import requests
from pathlib import Path
from PIL import Image
import base64
import io
from urllib.parse import urlparse
from src.config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def is_valid_url(url: str) -> bool:
    """
    Validate if a string is a proper URL.
    
    Args:
        url: String to validate
    
    Returns:
        bool: True if valid URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception as e:
        logger.error(f"URL validation error: {str(e)}")
        return False

def download_image(url: str) -> bytes:
    """
    Download image from URL.
    
    Args:
        url: Image URL
    
    Returns:
        bytes: Image data
        
    Raises:
        Exception: If download fails
    """
    try:
        logger.debug(f"Downloading image from URL: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise ValueError(f"Invalid content type: {content_type}")
            
        return response.content
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image: {str(e)}")
        raise ValueError(f"Failed to download image: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error downloading image: {str(e)}")
        raise

def validate_image_data(image_data: bytes) -> bool:
    """
    Validate image data.
    
    Args:
        image_data: Image bytes to validate
    
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If validation fails
    """
    try:
        # Check file size
        if len(image_data) > MAX_CONTENT_LENGTH:
            raise ValueError(f"Image too large. Maximum size: {MAX_CONTENT_LENGTH} bytes")

        # Verify it's a valid image
        with Image.open(io.BytesIO(image_data)) as img:
            img.verify()
            
            # Convert to RGB if needed
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
        return True
        
    except Exception as e:
        logger.error(f"Image validation failed: {str(e)}")
        raise ValueError(f"Invalid image: {str(e)}")

def encode_image_data(image_data: bytes) -> str:
    """
    Encode image data to base64.
    
    Args:
        image_data: Image bytes to encode
    
    Returns:
        str: Base64 encoded image
    """
    try:
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encode image: {str(e)}")
        raise

def get_image_data(source: str | Path | bytes) -> str:
    """
    Get base64 encoded image data from various sources.
    
    Args:
        source: Image source (URL, file path, or bytes)
    
    Returns:
        str: Base64 encoded image
        
    Raises:
        ValueError: If source is invalid or processing fails
    """
    logger.debug(f"Processing image from source type: {type(source)}")
    
    try:
        # Handle URLs
        if isinstance(source, str) and is_valid_url(source):
            logger.debug(f"Downloading image from URL: {source}")
            image_data = download_image(source)
            validate_image_data(image_data)
            return encode_image_data(image_data)

        # Handle file paths
        elif isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists():
                raise ValueError(f"File not found: {path}")
                
            if path.suffix[1:].lower() not in ALLOWED_EXTENSIONS:
                raise ValueError(f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}")
                
            logger.debug(f"Reading image from file: {path}")
            with open(path, 'rb') as f:
                image_data = f.read()
                validate_image_data(image_data)
                return encode_image_data(image_data)

        # Handle raw bytes
        elif isinstance(source, bytes):
            logger.debug("Processing raw image data")
            validate_image_data(source)
            return encode_image_data(source)

        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    except Exception as e:
        logger.error(f"Failed to process image: {str(e)}")
        raise

def cleanup_image(filepath: str | Path) -> None:
    """
    Safely remove temporary image file.
    
    Args:
        filepath: Path to the image file to remove
    """
    try:
        path = Path(filepath)
        if path.exists():
            path.unlink()
            logger.debug(f"Removed temporary file: {path}")
    except Exception as e:
        logger.error(f"Error cleaning up image file: {str(e)}")