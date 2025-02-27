"""
Main Flask application for the Hotdog Classifier web interface.
Handles routes, image uploads, and URL classification requests.
"""

import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from src.classifier import HotdogClassifier
from src.utils.logger import setup_logger
from src.utils.image_utils import (
    is_valid_url, 
    download_image, 
    cleanup_image,
    save_base64_image,
    is_base64_image
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
    
    try:
        # Handle base64 image data
        if 'base64' in request.form:
            image_data = request.form['base64']
            if not is_base64_image(image_data):
                logger.warning("Invalid base64 image data")
                return jsonify({'error': 'Invalid base64 image data'}), 400
            
            try:
                temp_path = save_base64_image(image_data, app.config['UPLOAD_FOLDER'])
                result = classifier.classify_image(temp_path)
                cleanup_image(temp_path)
                
                return jsonify({
                    'result': 'Hotdog! 🌭' if result else 'Not Hotdog! ❌',
                    'source': 'base64'
                })
            except Exception as e:
                logger.error(f"Error processing base64 image: {str(e)}")
                return jsonify({'error': str(e)}), 400

        # Handle URL input
        elif 'url' in request.form:
            image_url = request.form['url'].strip()
            logger.info(f"Processing image URL: {image_url}")
            
            if not is_valid_url(image_url):
                logger.warning(f"Invalid URL provided: {image_url}")
                return jsonify({'error': 'Invalid URL provided'}), 400
            
            try:
                # Download and process URL
                image_data = download_image(image_url)
                temp_path = Path(app.config['UPLOAD_FOLDER']) / 'temp_url_image.jpg'
                
                with open(temp_path, 'wb') as f:
                    f.write(image_data)
                
                try:
                    result = classifier.classify_image(temp_path)
                    return jsonify({
                        'result': 'Hotdog! 🌭' if result else 'Not Hotdog! ❌',
                        'source': 'url',
                        'processed_url': image_url
                    })
                finally:
                    cleanup_image(temp_path)
                    
            except Exception as e:
                logger.error(f"Error processing URL: {str(e)}")
                return jsonify({'error': f'Error processing URL: {str(e)}'}), 400

        # Handle file upload
        elif 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                logger.warning("No selected file")
                return jsonify({'error': 'No file selected'}), 400
            
            if not file.filename.lower().endswith(tuple(config.ALLOWED_EXTENSIONS)):
                logger.warning(f"Invalid file type: {file.filename}")
                return jsonify({'error': 'Invalid file type'}), 400
            
            try:
                filename = secure_filename(file.filename)
                filepath = Path(app.config['UPLOAD_FOLDER']) / filename
                
                logger.debug(f"Saving uploaded file to: {filepath}")
                file.save(filepath)
                
                try:
                    result = classifier.classify_image(filepath)
                    return jsonify({
                        'result': 'Hotdog! 🌭' if result else 'Not Hotdog! ❌',
                        'source': 'file'
                    })
                finally:
                    cleanup_image(filepath)
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
                
        else:
            logger.warning("No image data provided")
            return jsonify({'error': 'No image provided'}), 400
            
    except Exception as e:
        logger.error(f"Unexpected server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint to verify API connectivity."""
    try:
        api_status = classifier.test_api_connection()
        return jsonify({
            'status': 'healthy' if api_status else 'unhealthy',
            'api_connection': api_status
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Log application startup
    logger.info("Starting Hotdog Classifier application")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Max content length: {app.config['MAX_CONTENT_LENGTH']} bytes")
    
    # Start Flask application
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )