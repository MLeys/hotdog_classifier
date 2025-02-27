"""
Test suite for the Flask application.
"""

import unittest
from pathlib import Path
import io
from app import app
import src.config as config

class TestFlaskApp(unittest.TestCase):
    """Test cases for the Flask application."""

    def setUp(self):
        """Set up test client and other test variables."""
        app.config['TESTING'] = True
        app.config['UPLOAD_FOLDER'] = 'tests/test_uploads'
        self.client = app.test_client()
        
        # Ensure test upload directory exists
        Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    def test_index_page(self):
        """Test index page load."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hotdog Classifier', response.data)

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'status', response.data)

    def test_classify_no_file(self):
        """Test classification endpoint with no file."""
        response = self.client.post('/classify')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'error', response.data)

    def test_classify_invalid_file(self):
        """Test classification endpoint with invalid file type."""
        data = {
            'file': (io.BytesIO(b"not an image"), 'test.txt')
        }
        response = self.client.post('/classify', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid file type', response.data)

    def test_classify_valid_image(self):
        """Test classification endpoint with valid image."""
        # Create a test image
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        
        data = {
            'file': (img_io, 'test.jpg')
        }
        
        response = self.client.post('/classify', data=data)
        # Note: This might fail if API is not accessible
        self.assertIn(response.status_code, [200, 503])