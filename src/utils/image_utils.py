"""
Image processing utilities for the Hotdog Classifier.
Handles image validation, processing, and encoding.
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

def is_valid_url(url: str) -> bool:
    """
    Validate if a string is a proper URL.
    
    Args:
        url: String to validate
    
    Returns:
        bool: True if valid URL
    """
    try:
        # Check if it's a data URL
        if url.startswith('data:'):
            return False
            
        result = urlparse(url)
        return all([
            result.scheme in ('http', 'https'),
            result.netloc,
            result.path
        ])
    except Exception as e:
        logger.error(f"URL validation error: {str(e)}")
        return False

def is_base64_image(data: str) -> bool:
    """
    Check if string is a valid base64 encoded image.
    
    Args:
        data: Base64 string to check
    
    Returns:
        bool: True if valid base64 image
    """
    try:
        if not data.startswith('data:image/'):
            return False
        
        # Extract the base64 content
        content = data.split(',')[1]
        
        # Try to decode
        image_data = base64.b64decode(content)
        img = Image.open(io.BytesIO(image_data))
        img.verify()
        return True
    except:
        return False

def download_image(url: str) -> bytes:
    """
    Download image from URL, trying different extensions if needed.
    
    Args:
        url: Image URL
    
    Returns:
        bytes: Image data
    """
    extensions = ['', '.jpg', '.jpeg', '.png', '.gif', '.webp']
    base_url = url.split('?')[0].split('#')[0]  # Remove query params and hash
    
    if any(base_url.lower().endswith(ext) for ext in extensions[1:]):
        extensions = ['']  # If URL already has extension, don't try others
    
    last_error = None
    for ext in extensions:
        try:
            if ext:
                test_url = re.sub(r'\.[^.]+$', '', base_url) + ext
            else:
                test_url = base_url
                
            logger.debug(f"Trying URL: {test_url}")
            response = requests.get(test_url, timeout=10)
            response.raise_for_status()
            
            # Verify it's an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                continue
                
            # Verify image data
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img.verify()
            
            return img_data
            
        except Exception as e:
            last_error = e
            logger.debug(f"Failed to download from {test_url}: {str(e)}")
            continue
    
    raise ValueError(f"Failed to download image: {str(last_error)}")

def save_base64_image(data: str, upload_folder: str) -> Path:
    """
    Save base64 image data to a temporary file.
    
    Args:
        data: Base64 image data
        upload_folder: Directory to save the file
    
    Returns:
        Path: Path to saved file
    """
    try:
        # Extract the base64 content and image type
        content_type = data.split(';')[0].split('/')[1]
        content = data.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(content)
        
        # Save to temporary file
        temp_path = Path(upload_folder) / f'temp_base64.{content_type}'
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
        filepath: Path to the image file to remove
    """
    try:
        path = Path(filepath)
        if path.exists():
            path.unlink()
            logger.debug(f"Removed temporary file: {path}")
    except Exception as e:
        logger.error(f"Error cleaning up image file: {str(e)}")