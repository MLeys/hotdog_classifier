"""
Image processing utilities for the Real Hotdog Classifier.
"""

import os
import re
import base64
import requests
from pathlib import Path
from PIL import Image
import io
from urllib.parse import urlparse
from src.config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def process_url(url: str) -> str:
    """
    Process and validate image URL.
    
    Args:
        url: URL to process
        
    Returns:
        str: Processed URL
    """
    # If it's a data URL, download and convert to regular image
    if url.startswith('data:image'):
        try:
            # Extract base64 data
            content = url.split(',')[1]
            image_data = base64.b64decode(content)
            
            # Save temporarily and return path
            temp_path = os.path.join('uploads', f'temp_url_{uuid.uuid4()}.jpg')
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            return temp_path
            
        except Exception as e:
            logger.error(f"Error processing data URL: {str(e)}")
            raise ValueError("Invalid data URL format")
    
    # If it's a regular URL, validate and return
    if not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL format")
        
    return url

def get_image_data(image_path: str | Path) -> str:
    """
    Get base64 encoded image data from file.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        str: Base64 encoded image data
    """
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
            return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image: {str(e)}")
        raise

def validate_image_size(file_size: int, max_size: int) -> bool:
    """
    Validate image file size.
    
    Args:
        file_size: Size of the image in bytes
        max_size: Maximum allowed size in bytes
    
    Returns:
        bool: True if valid size
    """
    if file_size > max_size:
        raise ValueError(f"Image file too large. Maximum size: {max_size/1024/1024:.1f}MB")
    return True

def validate_image_format(mime_type: str) -> bool:
    """
    Validate image MIME type.
    
    Args:
        mime_type: MIME type of the image
    
    Returns:
        bool: True if valid format
    """
    allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
    if mime_type not in allowed_types:
        raise ValueError(f"Unsupported image format. Allowed: {', '.join(t.split('/')[-1] for t in allowed_types)}")
    return True

def is_valid_url(url: str) -> bool:
    """
    Validate if string is a proper URL.
    
    Args:
        url: String to validate
    
    Returns:
        bool: True if valid URL
    """
    try:
        if url.startswith('data:'):
            return False
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc, result.path])
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
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Verify content type
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise ValueError(f"Invalid content type: {content_type}")
            
        return response.content
    except Exception as e:
        logger.error(f"Failed to download image: {str(e)}")
        raise

def is_base64_image(data: str) -> bool:
    """
    Check if string is valid base64 encoded image.
    
    Args:
        data: Base64 string to check
    
    Returns:
        bool: True if valid base64 image
    """
    try:
        if not data.startswith('data:image/'):
            return False
        content = data.split(',')[1]
        image_data = base64.b64decode(content)
        img = Image.open(io.BytesIO(image_data))
        img.verify()
        return True
    except:
        return False

def save_base64_image(data: str, upload_folder: str) -> Path:
    """
    Save base64 image data to file.
    
    Args:
        data: Base64 image data
        upload_folder: Directory to save file
    
    Returns:
        Path: Path to saved file
    """
    try:
        content = data.split(',')[1]
        image_data = base64.b64decode(content)
        
        temp_path = Path(upload_folder) / 'temp_base64.jpg'
        with open(temp_path, 'wb') as f:
            f.write(image_data)
            
        return temp_path
        
    except Exception as e:
        logger.error(f"Error saving base64 image: {str(e)}")
        raise

def cleanup_image(filepath: str | Path) -> None:
    """
    Safely remove temporary image file.
    
    Args:
        filepath: Path to image file to remove
    """
    try:
        path = Path(filepath)
        if path.exists():
            path.unlink()
            logger.debug(f"Removed temporary file: {path}")
    except Exception as e:
        logger.error(f"Error cleaning up image file: {str(e)}")