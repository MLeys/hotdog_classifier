/**
 * Main JavaScript file for the Hotdog Classifier application.
 * Handles file uploads, drag and drop, and API interactions.
 */

// Add URL form handling
document.getElementById('url-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const url = this.querySelector('input[name="url"]').value;
    if (!url) return;

    // Show loading spinner
    loadingSpinner.classList.remove('hidden');
    resultContainer.classList.add('hidden');

    // Send URL for classification
    fetch('/classify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `url=${encodeURIComponent(url)}`
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Classification failed');
            });
        }
        return response.json();
    })
    .then(data => {
        loadingSpinner.classList.add('hidden');
        resultContainer.classList.remove('hidden');
        resultText.textContent = data.result;
        resultText.style.color = data.result.includes('Hotdog') ? 
            'var(--success-color)' : 'var(--error-color)';
    })
    .catch(error => {
        loadingSpinner.classList.add('hidden');
        showError(error.message || 'Error classifying image');
    });
});


document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = dropZone.querySelector('.drop-zone__input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const resultContainer = document.getElementById('result-container');
    const resultText = document.getElementById('result-text');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorContainer = document.getElementById('error-container');
    const errorText = document.getElementById('error-text');

    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    function showError(message) {
        errorText.textContent = message;
        errorContainer.classList.remove('hidden');
        setTimeout(() => {
            errorContainer.classList.add('hidden');
        }, 5000);
    }

    /**
     * Reset display state
     */
    function resetDisplay() {
        resultContainer.classList.add('hidden');
        loadingSpinner.classList.add('hidden');
        errorContainer.classList.add('hidden');
    }

    /**
     * Handle file input change event
     */
    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length) {
            updateThumbnail(fileInput.files[0]);
        }
    });

    /**
     * Handle click on drop zone
     */
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    /**
     * Handle drag over event
     */
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drop-zone--over');
    });

    /**
     * Handle drag leave and drag end events
     */
    ['dragleave', 'dragend'].forEach((type) => {
        dropZone.addEventListener(type, () => {
            dropZone.classList.remove('drop-zone--over');
        });
    });

    /**
     * Handle drop event
     */
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drop-zone--over');

        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateThumbnail(e.dataTransfer.files[0]);
        }
    });

    /**
     * Update thumbnail preview and initiate classification
     * @param {File} file - The uploaded file
     */
    function updateThumbnail(file) {
        resetDisplay();

        // Validate file type
        if (!file.type.startsWith('image/')) {
            showError('Please upload an image file!');
            return;
        }

        // Show preview
        previewContainer.classList.remove('hidden');

        // Create preview
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            imagePreview.src = reader.result;
            uploadAndClassify(file);
        };
    }

    /**
     * Upload and classify the image
     * @param {File} file - The file to classify
     */
    function uploadAndClassify(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Show loading spinner
        loadingSpinner.classList.remove('hidden');

        // Send classification request
        fetch('/classify', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Classification failed');
                });
            }
            return response.json();
        })
        .then(data => {
            loadingSpinner.classList.add('hidden');
            resultContainer.classList.remove('hidden');
            
            resultText.textContent = data.result;
            resultText.style.color = data.result.includes('Hotdog') ? 
                'var(--success-color)' : 'var(--error-color)';
        })
        .catch(error => {
            loadingSpinner.classList.add('hidden');
            showError(error.message || 'Error classifying image');
            console.error('Error:', error);
        });
    }
});