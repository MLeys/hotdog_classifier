"""
Utility modules for the Hotdog Classifier.
"""

from .image_utils import (
    is_valid_url,
    download_image,
    cleanup_image,
    is_base64_image,
    save_base64_image
)
from .logger import setup_logger

__all__ = [
    'is_valid_url',
    'download_image',
    'cleanup_image',
    'is_base64_image',
    'save_base64_image',
    'setup_logger'
]