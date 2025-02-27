"""
Main Flask application for the Hotdog Classifier web interface.
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
from src.utils.error_handlers import (
    ImageProcessingError,
    handle_image_error
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

@app.route('/')
def index():
    """Render the main page."""
    logger.info("Rendering index page")
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify_image():
    """
    Handle image classification requests.
    Accepts file uploads, URLs, and base64 encoded images.
    """
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
                    raise ImageProcessingError("Invalid base64 image data")
                
                temp_path = save_base64_image(image_data, app.config['UPLOAD_FOLDER'])
                logger.debug(f"Base64 image saved to temporary file (Request ID: {request_id})")
                
                try:
                    result = classifier.classify_image(temp_path)
                    logger.info(f"Classification result: {result} (Request ID: {request_id})")
                    return jsonify({
                        'result': 'Hotdog! 🌭' if result else 'Not Hotdog! ❌',
                        'source': 'base64',
                        'request_id': request_id
                    })
                finally:
                    cleanup_image(temp_path)
                    
            except Exception as e:
                logger.error(f"Error processing base64 image: {str(e)} (Request ID: {request_id})")
                error_response, status_code = handle_image_error(e)
                error_response['request_id'] = request_id
                return jsonify(error_response), status_code

        # Handle URL input
        elif 'url' in request.form:
            image_url = request.form['url'].strip()
            logger.info(f"Processing image URL: {image_url} (Request ID: {request_id})")
            
            try:
                if not is_valid_url(image_url):
                    raise ImageProcessingError("Invalid URL provided")
                
                image_data = download_image(image_url)
                logger.debug(f"Image downloaded from URL (Request ID: {request_id})")
                
                temp_path = Path(app.config['UPLOAD_FOLDER']) / f'temp_url_{request_id}.jpg'
                
                with open(temp_path, 'wb') as f:
                    f.write(image_data)
                
                try:
                    result = classifier.classify_image(temp_path)
                    logger.info(f"Classification result: {result} (Request ID: {request_id})")
                    return jsonify({
                        'result': 'Hotdog! 🌭' if result else 'Not Hotdog! ❌',
                        'source': 'url',
                        'processed_url': image_url,
                        'request_id': request_id
                    })
                finally:
                    cleanup_image(temp_path)
                    
            except Exception as e:
                logger.error(f"Error processing URL: {str(e)} (Request ID: {request_id})")
                error_response, status_code = handle_image_error(e)
                error_response['request_id'] = request_id
                return jsonify(error_response), status_code

        # Handle file upload
        elif 'file' in request.files:
            file = request.files['file']
            logger.debug(f"Processing file upload: {file.filename} (Request ID: {request_id})")
            
            try:
                if file.filename == '':
                    raise ImageProcessingError("No file selected")
                
                if not file.filename.lower().endswith(tuple(config.ALLOWED_EXTENSIONS)):
                    raise ImageProcessingError(
                        f"Invalid file type. Allowed types: {', '.join(config.ALLOWED_EXTENSIONS)}"
                    )
                
                # Validate file
                validate_image_format(file.content_type)
                validate_image_size(file.content_length or 0, config.MAX_CONTENT_LENGTH)
                
                filename = secure_filename(file.filename)
                filepath = Path(app.config['UPLOAD_FOLDER']) / f"{request_id}_{filename}"
                
                logger.debug(f"Saving uploaded file to: {filepath} (Request ID: {request_id})")
                file.save(filepath)
                
                try:
                    result = classifier.classify_image(filepath)
                    logger.info(f"Classification result: {result} (Request ID: {request_id})")
                    return jsonify({
                        'result': 'Hotdog! 🌭' if result else 'Not Hotdog! ❌',
                        'source': 'file',
                        'request_id': request_id
                    })
                finally:
                    cleanup_image(filepath)
                    
            except Exception as e:
                logger.error(f"Error processing file: {str(e)} (Request ID: {request_id})")
                error_response, status_code = handle_image_error(e)
                error_response['request_id'] = request_id
                return jsonify(error_response), status_code
                
        else:
            logger.warning(f"No image provided (Request ID: {request_id})")
            return jsonify({
                'error': 'No image provided',
                'details': {
                    'accepted_inputs': ['file', 'url', 'base64']
                },
                'request_id': request_id
            }), 400
            
    except Exception as e:
        logger.error(f"Unexpected server error: {str(e)} (Request ID: {request_id})", exc_info=True)
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
    logger.info("Starting Hotdog Classifier application")
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