"""
Test suite for the Hotdog Classifier application.
"""

import unittest
import os
from pathlib import Path
import shutil
from src.classifier import HotdogClassifier
from src.utils.image_utils import encode_image, validate_image
import src.config as config

class TestHotdogClassifier(unittest.TestCase):
    """Test cases for the Hotdog Classifier."""

    @classmethod
    def setUpClass(cls):
        """Set up test class - runs once before all tests."""
        # Create test directories if they don't exist
        cls.test_dir = Path('tests/test_images')
        cls.test_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test upload directory
        cls.test_upload_dir = Path('tests/test_uploads')
        cls.test_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize classifier
        cls.classifier = HotdogClassifier()
        
        # Create a small test image
        cls.create_test_image()

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        # Remove test upload directory
        if cls.test_upload_dir.exists():
            shutil.rmtree(cls.test_upload_dir)

    @classmethod
    def create_test_image(cls):
        """Create a test image file."""
        from PIL import Image
        
        # Create a small red image
        img = Image.new('RGB', (100, 100), color='red')
        cls.test_image_path = cls.test_dir / 'test_image.jpg'
        img.save(cls.test_image_path)

    def test_image_validation(self):
        """Test image validation functionality."""
        # Test valid image
        self.assertTrue(validate_image(self.test_image_path))
        
        # Test non-existent file
        with self.assertRaises(ValueError):
            validate_image('nonexistent.jpg')
        
        # Test invalid extension
        invalid_path = self.test_dir / 'test.txt'
        invalid_path.touch()
        with self.assertRaises(ValueError):
            validate_image(invalid_path)
        invalid_path.unlink()

    def test_image_encoding(self):
        """Test image encoding functionality."""
        # Test valid image encoding
        encoded = encode_image(self.test_image_path)
        self.assertIsInstance(encoded, str)
        self.assertTrue(len(encoded) > 0)

    def test_classifier_initialization(self):
        """Test classifier initialization."""
        self.assertIsNotNone(self.classifier)
        self.assertEqual(self.classifier.api_url, config.API_URL)
        self.assertEqual(self.classifier.timeout, config.REQUEST_TIMEOUT)

    def test_api_connection(self):
        """Test API connection."""
        # This test requires internet connection
        connection_status = self.classifier.test_api_connection()
        self.assertIsInstance(connection_status, bool)

class TestClassifierIntegration(unittest.TestCase):
    """Integration tests for the Hotdog Classifier."""

    def setUp(self):
        """Set up each test."""
        self.classifier = HotdogClassifier()
        self.test_dir = Path('tests/test_images')
        
        # Ensure test images directory exists
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def test_classification_workflow(self):
        """Test the complete classification workflow."""
        # This test requires a real image and API access
        test_image_path = self.test_dir / 'hotdog.jpg'
        
        # Skip test if test image doesn't exist
        if not test_image_path.exists():
            self.skipTest("Test image not available")
        
        try:
            result = self.classifier.classify_image(test_image_path)
            self.assertIsInstance(result, bool)
        except ConnectionError:
            self.skipTest("API connection not available")