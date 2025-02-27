"""
Image processing utilities for the Hotdog Classifier.
Handles image validation, processing, and encoding.
"""

import os
from pathlib import Path
from PIL import Image
import base64
import io
from src.config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def validate_image(image_path: str | Path) -> bool:
    """
    Validate image file before processing.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        bool: True if image is valid
    
    Raises:
        ValueError: If image validation fails
    """
    image_path = Path(image_path)
    logger.debug(f"Validating image: {image_path}")

    # Check if file exists
    if not image_path.exists():
        logger.error(f"Image file not found: {image_path}")
        raise ValueError("Image file not found")

    # Check file extension
    if image_path.suffix[1:].lower() not in ALLOWED_EXTENSIONS:
        logger.error(f"Unsupported image format: {image_path.suffix}")
        raise ValueError(f"Unsupported image format. Allowed formats: {ALLOWED_EXTENSIONS}")

    # Check file size
    file_size = image_path.stat().st_size
    if file_size > MAX_CONTENT_LENGTH:
        logger.error(f"Image file too large: {file_size} bytes")
        raise ValueError(f"Image file too large. Maximum size: {MAX_CONTENT_LENGTH} bytes")

    logger.debug("Image validation successful")
    return True

def encode_image(image_path: str | Path) -> str:
    """
    Convert image to base64 encoding for API transmission.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        str: Base64 encoded image string
    
    Raises:
        Exception: If image processing fails
    """
    logger.debug(f"Starting image encoding process for: {image_path}")
    
    try:
        # Validate image before processing
        validate_image(image_path)

        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                logger.debug(f"Converting image from {img.mode} to RGB")
                img = img.convert('RGB')
            
            # Convert to base64
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            logger.debug("Image successfully encoded to base64")
            return img_str

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise Exception(f"Error processing image: {str(e)}")

def cleanup_image(image_path: str | Path) -> None:
    """
    Safely remove temporary image file.
    
    Args:
        image_path: Path to the image file to remove
    """
    try:
        image_path = Path(image_path)
        if image_path.exists():
            image_path.unlink()
            logger.debug(f"Removed temporary file: {image_path}")
    except Exception as e:
        logger.error(f"Error cleaning up image file: {str(e)}")