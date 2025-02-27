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
        # Validate request
        if 'file' not in request.files:
            logger.warning("No file part in request")
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("No selected file")
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not file.filename.lower().endswith(tuple(config.ALLOWED_EXTENSIONS)):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save and process file
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        
        logger.debug(f"Saving uploaded file to: {filepath}")
        file.save(filepath)
        
        try:
            # Classify image
            result = classifier.classify_image(str(filepath))
            
            response_data = {
                'result': 'Not Hotdog! ❌'
            }
            
            if result:
                response_data['result'] = 'Hotdog! 🌭'
            
            logger.info(f"Classification complete for {filename}: {result}")
            return jsonify(response_data)
            
        except ConnectionError as e:
            logger.error(f"Connection error during classification: {str(e)}")
            return jsonify({'error': str(e)}), 503
            
        except TimeoutError as e:
            logger.error(f"Timeout error during classification: {str(e)}")
            return jsonify({'error': str(e)}), 504
            
        except Exception as e:
            logger.error(f"Error during classification: {str(e)}")
            return jsonify({'error': f'Classification error: {str(e)}'}), 500
            
        finally:
            # Clean up uploaded file
            cleanup_image(filepath)
            
    except Exception as e:
        logger.error(f"Unexpected server error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

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