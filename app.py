"""
Main Flask application for the Real Hotdog Classifier web interface.
Handles routes, image uploads, URL classification requests, and error handling.
"""

import os
import uuid
import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from src.classifier import HotdogClassifier
from src.utils.logger import setup_logger
from src.utils.image_utils import (
    is_valid_url, 
    download_image, 
    cleanup_image,
    save_base64_image,
    is_base64_image,
    validate_image_size,
    validate_image_format
)
import src.config as config

# Initialize Flask application
app = Flask(__name__)
logger = setup_logger(__name__)

# Configure upload folder
upload_dir = Path(config.UPLOAD_FOLDER)
upload_dir.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(upload_dir)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Initialize classifier
classifier = HotdogClassifier()

def create_response(result: bool, source: str, request_id: str, **extra_data) -> dict:
    """Create a consistent response format for all classification results."""
    response = {
        'result': 'Hotdog! 🌭 (Real, edible hotdog detected)' if result else 'Not Hotdog! ❌ (Not a real hotdog)',
        'isRealHotdog': result,
        'explanation': (
            'This appears to be a real, edible hotdog in a bun.' if result 
            else 'This is not a real, edible hotdog (could be a drawing, toy, costume, or other item).'
        ),
        'source': source,
        'request_id': request_id,
        'timestamp': datetime.datetime.now().isoformat()
    }
    response.update(extra_data)
    return response

@app.route('/')
def index():
    """Render the main page."""
    logger.info("Rendering index page")
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify_image():
    """Handle image classification requests."""
    logger.info("Received classification request")
    request_id = str(uuid.uuid4())
    logger.debug(f"Request ID: {request_id}")
    
    try:
        # Handle base64 image data
        if 'base64' in request.form:
            image_data = request.form['base64']
            logger.debug(f"Processing base64 image data (Request ID: {request_id})")
            
            try:
                if not is_base64_image(image_data):
                    raise ValueError("Invalid base64 image data")
                
                temp_path = save_base64_image(image_data, app.config['UPLOAD_FOLDER'])
                
                try:
                    result = classifier.classify_image(temp_path)
                    return jsonify(create_response(result, 'base64', request_id))
                finally:
                    cleanup_image(temp_path)
                    
            except Exception as e:
                logger.error(f"Error processing base64 image: {str(e)}")
                return jsonify({'error': str(e), 'request_id': request_id}), 400

        # Handle URL input
        elif 'url' in request.form:
            image_url = request.form['url'].strip()
            logger.info(f"Processing image URL: {image_url}")
            
            if not is_valid_url(image_url):
                return jsonify({'error': 'Invalid URL provided'}), 400
            
            try:
                image_data = download_image(image_url)
                temp_path = Path(app.config['UPLOAD_FOLDER']) / f'temp_url_{request_id}.jpg'
                
                with open(temp_path, 'wb') as f:
                    f.write(image_data)
                
                try:
                    result = classifier.classify_image(temp_path)
                    return jsonify(create_response(
                        result, 
                        'url', 
                        request_id,
                        processed_url=image_url
                    ))
                finally:
                    cleanup_image(temp_path)
                    
            except Exception as e:
                logger.error(f"Error processing URL: {str(e)}")
                return jsonify({'error': str(e), 'request_id': request_id}), 400

        # Handle file upload
        elif 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not file.filename.lower().endswith(tuple(config.ALLOWED_EXTENSIONS)):
                return jsonify({'error': 'Invalid file type'}), 400
            
            try:
                validate_image_format(file.content_type)
                
                filename = secure_filename(file.filename)
                filepath = Path(app.config['UPLOAD_FOLDER']) / f"{request_id}_{filename}"
                
                file.save(filepath)
                
                try:
                    result = classifier.classify_image(filepath)
                    return jsonify(create_response(
                        result, 
                        'file', 
                        request_id,
                        filename=file.filename
                    ))
                finally:
                    cleanup_image(filepath)
                    
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return jsonify({'error': str(e), 'request_id': request_id}), 500
                
        else:
            logger.warning("No image provided")
            return jsonify({
                'error': 'No image provided',
                'request_id': request_id
            }), 400
            
    except Exception as e:
        logger.error(f"Unexpected server error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'request_id': request_id
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint to verify API connectivity."""
    try:
        api_status = classifier.test_api_connection()
        memory_usage = os.popen('ps -o rss= -p %d' % os.getpid()).read()
        
        return jsonify({
            'status': 'healthy' if api_status else 'unhealthy',
            'api_connection': api_status,
            'timestamp': datetime.datetime.now().isoformat(),
            'memory_usage_kb': int(memory_usage.strip()) if memory_usage else None,
            'upload_dir_size_mb': sum(f.stat().st_size for f in upload_dir.glob('**/*') if f.is_file()) / (1024 * 1024)
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.datetime.now().isoformat()
        }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'error': 'File too large',
        'details': {
            'max_size_mb': config.MAX_CONTENT_LENGTH / (1024 * 1024)
        }
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Resource not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed errors."""
    return jsonify({
        'error': 'Method not allowed'
    }), 405

if __name__ == '__main__':
    # Log application startup
    logger.info("Starting Real Hotdog Classifier application")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Max content length: {app.config['MAX_CONTENT_LENGTH']} bytes")
    
    # Clean up any leftover temporary files
    for temp_file in upload_dir.glob('temp_*'):
        cleanup_image(temp_file)
    
    # Start Flask application
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )