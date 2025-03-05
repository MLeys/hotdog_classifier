"""
Error handling utilities for the Real Hotdog Classifier.
Provides consistent error handling and messaging across the application.
"""

from typing import Union, Dict, Any, Tuple
import logging
from requests.exceptions import RequestException
from PIL import UnidentifiedImageError

logger = logging.getLogger(__name__)

class ImageProcessingError(Exception):
    """
    Custom exception for image processing errors.
    
    Attributes:
        message: Error message
        details: Additional error details dictionary
    """
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

def handle_image_error(error: Exception) -> Tuple[Dict[str, Any], int]:
    """
    Handle various image-related errors and return appropriate responses.
    
    Args:
        error: The caught exception
        
    Returns:
        tuple: (error_response_dict, http_status_code)
        
    Note:
        Error responses include help text specific to real hotdog classification
    """
    if isinstance(error, UnidentifiedImageError):
        return {
            "error": "Invalid image format or corrupted image file",
            "help": "Please ensure you're uploading a clear, valid image of food",
            "details": {
                "accepted_formats": ["JPEG", "PNG", "GIF", "WebP"]
            }
        }, 400
    
    if isinstance(error, OSError):
        return {
            "error": "Failed to read or process image file",
            "help": "The image file might be corrupted or inaccessible",
            "details": {
                "error_type": "file_access",
                "message": str(error)
            }
        }, 500
        
    if isinstance(error, ValueError):
        return {
            "error": str(error),
            "help": "Please provide a clear, well-lit image of the food item",
            "details": {
                "error_type": "validation",
                "message": str(error)
            }
        }, 400
        
    if isinstance(error, RequestException):
        return {
            "error": "Failed to download or process image from URL",
            "help": "Please ensure the URL points to a valid, accessible image",
            "details": {
                "error_type": "network",
                "message": str(error)
            }
        }, 503
        
    if isinstance(error, ImageProcessingError):
        return {
            "error": error.message,
            "help": "Try uploading a different, clear image of the food item",
            "details": error.details
        }, 400
        
    # Generic error handler
    logger.error(f"Unexpected error: {str(error)}", exc_info=True)
    return {
        "error": "An unexpected error occurred while processing the image",
        "help": "Please try again with a different image or contact support if the issue persists",
        "details": {
            "error_type": "unknown",
            "message": str(error)
        }
    }, 500

def create_validation_error(message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a consistent validation error response.
    
    Args:
        message: Main error message
        details: Additional error details
        
    Returns:
        dict: Formatted error response
    """
    return {
        "error": message,
        "help": "Please ensure your input meets the requirements",
        "details": details or {},
        "error_type": "validation"
    }

def create_processing_error(message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a consistent processing error response.
    
    Args:
        message: Main error message
        details: Additional error details
        
    Returns:
        dict: Formatted error response
    """
    return {
        "error": message,
        "help": "Try uploading a different image or try again later",
        "details": details or {},
        "error_type": "processing"
    }

class ValidationError(Exception):
    """Custom exception for input validation errors."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ProcessingError(Exception):
    """Custom exception for processing errors."""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

def log_error(error: Exception, request_id: str = None) -> None:
    """
    Log error with consistent format.
    
    Args:
        error: Exception to log
        request_id: Optional request identifier
    """
    error_context = {
        'error_type': error.__class__.__name__,
        'error_message': str(error),
        'request_id': request_id
    }
    
    if hasattr(error, 'details'):
        error_context['details'] = error.details
        
    logger.error(
        f"Error occurred: {error_context['error_type']} - {error_context['error_message']}",
        extra=error_context,
        exc_info=True
    )

def format_error_response(error: Exception, status_code: int = 500) -> Tuple[Dict[str, Any], int]:
    """
    Format error for API response.
    
    Args:
        error: Exception to format
        status_code: HTTP status code
        
    Returns:
        tuple: (error_response_dict, http_status_code)
    """
    response = {
        "error": str(error),
        "error_type": error.__class__.__name__
    }
    
    if hasattr(error, 'details'):
        response['details'] = error.details
    
    if hasattr(error, 'help'):
        response['help'] = error.help
        
    return response, status_code