"""
Error handling utilities for the Hotdog Classifier.
"""

from typing import Union, Dict, Any
import logging
from requests.exceptions import RequestException
from PIL import UnidentifiedImageError

logger = logging.getLogger(__name__)

class ImageProcessingError(Exception):
    """Custom exception for image processing errors."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

def handle_image_error(error: Exception) -> tuple[Dict[str, str], int]:
    """
    Handle various image-related errors and return appropriate responses.
    
    Args:
        error: The caught exception
        
    Returns:
        tuple: (error_response_dict, http_status_code)
    """
    if isinstance(error, UnidentifiedImageError):
        return {"error": "Invalid image format or corrupted image file"}, 400
    
    if isinstance(error, OSError):
        return {"error": "Failed to read or process image file"}, 500
        
    if isinstance(error, ValueError):
        return {"error": str(error)}, 400
        
    if isinstance(error, RequestException):
        return {"error": "Failed to download image from URL"}, 503
        
    if isinstance(error, ImageProcessingError):
        return {"error": error.message, "details": error.details}, 400
        
    # Generic error handler
    logger.error(f"Unexpected error: {str(error)}", exc_info=True)
    return {"error": "An unexpected error occurred"}, 500

def validate_image_size(file_size: int, max_size: int) -> None:
    """
    Validate image file size.
    
    Args:
        file_size: Size of the image in bytes
        max_size: Maximum allowed size in bytes
        
    Raises:
        ImageProcessingError: If validation fails
    """
    if file_size > max_size:
        raise ImageProcessingError(
            f"Image file too large. Maximum size allowed is {max_size/1024/1024:.1f}MB",
            {"max_size": max_size, "received_size": file_size}
        )

def validate_image_format(mime_type: str) -> None:
    """
    Validate image MIME type.
    
    Args:
        mime_type: MIME type of the image
        
    Raises:
        ImageProcessingError: If validation fails
    """
    allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
    if mime_type not in allowed_types:
        raise ImageProcessingError(
            f"Unsupported image format. Allowed formats: {', '.join(t.split('/')[-1] for t in allowed_types)}",
            {"allowed_types": list(allowed_types), "received_type": mime_type}
        )