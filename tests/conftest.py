"""
PyTest configuration file.
Contains fixtures and configuration for tests.
"""

import pytest
from pathlib import Path
import shutil

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment before all tests."""
    # Create necessary test directories
    test_dirs = [
        Path('tests/test_images'),
        Path('tests/test_uploads'),
        Path('logs')
    ]
    
    for directory in test_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Cleanup after all tests
    shutil.rmtree('tests/test_uploads', ignore_errors=True)

@pytest.fixture
def test_client():
    """Create a test client for the Flask application."""
    from app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client