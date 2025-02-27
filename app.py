"""
Main Flask application for the Hotdog Classifier.
"""

import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from src.classifier import HotdogClassifier
from src.utils.logger import setup_logger
from src.utils.image_utils import cleanup_image
import src.config as config

# Initialize Flask application
app = Flask(__name__)
logger = setup_logger(__name__)

# Configure upload folder
if not os.path.exists(config.UPLOAD_FOLDER):
    os.makedirs(config.UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
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
    """Handle image classification requests."""
    logger.info("Received classification request")
    
    try:
        # Check for URL in request
        if 'url' in request.form:
            image_url = request.form['url']
            logger.info(f"Processing image URL: {image_url}")
            
            try:
                result = classifier.classify_image(image_url)
                return jsonify({
                    'result': 'Hotdog! 🌭' if result else 'Not Hotdog! ❌'
                })
            except Exception as e:
                logger.error(f"Error processing URL: {str(e)}")
                return jsonify({'error': str(e)}), 400

        # Handle file upload
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                logger.warning("No selected file")
                return jsonify({'error': 'No file selected'}), 400
            
            if not file.filename.lower().endswith(tuple(config.ALLOWED_EXTENSIONS)):
                logger.warning(f"Invalid file type: {file.filename}")
                return jsonify({'error': 'Invalid file type'}), 400
            
            # Save and process file
            filename = secure_filename(file.filename)
            filepath = Path(app.config['UPLOAD_FOLDER']) / filename
            
            logger.debug(f"Saving uploaded file to: {filepath}")
            file.save(filepath)
            
            try:
                result = classifier.classify_image(filepath)
                return jsonify({
                    'result': 'Hotdog! 🌭' if result else 'Not Hotdog! ❌'
                })
            finally:
                # Clean up uploaded file
                if filepath.exists():
                    filepath.unlink()
                    logger.debug(f"Removed temporary file: {filepath}")
        
        else:
            logger.warning("No file or URL provided")
            return jsonify({'error': 'No image provided'}), 400
            
    except Exception as e:
        logger.error(f"Unexpected server error: {str(e)}")
        return jsonify({'error': str(e)}), 500

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