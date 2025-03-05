/**
 * Main JavaScript file for the Hotdog Classifier application.
 * Handles file uploads, drag and drop, and API interactions.
 */

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

    // Debug flag
    const DEBUG = true;

    // Console logging wrapper
    const log = {
        info: (...args) => DEBUG && console.log('[INFO]', ...args),
        error: (...args) => DEBUG && console.error('[ERROR]', ...args),
        warn: (...args) => DEBUG && console.warn('[WARN]', ...args),
        debug: (...args) => DEBUG && console.debug('[DEBUG]', ...args)
    };

// Then replace all console.log/error calls with log.info/error


async function handleUrl(url) {
    resetDisplay();
    log.info('Processing URL:', url);

    const formattedUrl = formatImageUrl(url);
    if (!formattedUrl) {
        log.error('Invalid URL format');
        showError('Please enter a valid URL');
        return;
    }
    // ... rest of the function
}
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

/**
 * Classify image and handle response
 * @param {FormData} formData Form data containing file or URL
 * @param {string} [imageUrl] Optional URL for history (for URL submissions)
 */
async function classifyImage(formData, imageUrl = null) {
    try {
        log.info('Starting classification...');
        loadingSection.classList.remove('hidden');
        resultSection.classList.add('hidden');

        const response = await fetch('/classify', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const data = await response.json();
            log.error('Classification failed:', data);
            throw data;
        }

        const data = await response.json();
        log.info('Classification result:', data);
        
        loadingSection.classList.add('hidden');
        resultSection.classList.remove('hidden');
        
        // Update result text and styling
        resultText.textContent = data.result;
        resultText.setAttribute('data-result', data.isRealHotdog ? 'hotdog' : 'not-hotdog');

        // Add description if provided
        const explanationEl = document.querySelector('.result-explanation');
        if (explanationEl && data.description) {
            explanationEl.textContent = data.description;
            explanationEl.classList.remove('hidden');
            log.debug('Added description:', data.description);
        }

        // Use provided imageUrl for history if available, otherwise use preview image
        const historyImageUrl = imageUrl || previewImage.src;
        log.debug('Using image URL for history:', historyImageUrl);
        
        // Add to history
        addToHistory(historyImageUrl, {
            result: data.result,
            isRealHotdog: data.isRealHotdog,
            description: data.description,
            explanation: data.explanation
        });

        log.info('Classification completed successfully');

    } catch (error) {
        log.error('Classification error:', error);
        loadingSection.classList.add('hidden');
        showError(error);
    }
}
