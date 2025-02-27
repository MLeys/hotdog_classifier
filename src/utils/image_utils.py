"""
Image processing utilities for the Hotdog Classifier.
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

def validate_image_size(file_size: int, max_size: int) -> bool:
    """
    Validate image file size.
    
    Args:
        file_size: Size of the image in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        bool: True if valid size
        
    Raises:
        ValueError: If file is too large
    """
    if file_size > max_size:
        raise ValueError(f"Image file too large. Maximum size allowed is {max_size/1024/1024:.1f}MB")
    return True

def validate_image_format(mime_type: str) -> bool:
    """
    Validate image MIME type.
    
    Args:
        mime_type: MIME type of the image
        
    Returns:
        bool: True if valid format
        
    Raises:
        ValueError: If format is not supported
    """
    allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
    if mime_type not in allowed_types:
        raise ValueError(f"Unsupported image format. Allowed formats: {', '.join(t.split('/')[-1] for t in allowed_types)}")
    return True

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

def download_image(url: str) -> bytes:
    """
    Download image from URL, trying different extensions if needed.
    
    Args:
        url: Image URL
    
    Returns:
        bytes: Image data
    """
    extensions = ['', '.jpg', '.jpeg', '.png', '.gif', '.webp']
    base_url = url.split('?')[0].split('#')[0]
    
    if any(base_url.lower().endswith(ext) for ext in extensions[1:]):
        extensions = ['']
    
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
                
            return response.content
            
        except Exception as e:
            last_error = e
            logger.debug(f"Failed to download from {test_url}: {str(e)}")
            continue
    
    raise ValueError(f"Failed to download image: {str(last_error)}")

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
        
        content = data.split(',')[1]
        image_data = base64.b64decode(content)
        img = Image.open(io.BytesIO(image_data))
        img.verify()
        return True
    except:
        return False

def save_base64_image(data: str, upload_folder: str) -> Path:
    """
    Save base64 image data to a file.
    
    Args:
        data: Base64 image data
        upload_folder: Directory to save the file
    
    Returns:
        Path: Path to saved file
    """
    try:
        content_type = data.split(';')[0].split('/')[1]
        content = data.split(',')[1]
        
        image_data = base64.b64decode(content)
        
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