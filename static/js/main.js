/**
 * Main JavaScript file for the Hotdog Classifier application.
 * Handles file uploads, URL inputs, and API interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = dropZone.querySelector('.drop-zone__input');
    const urlForm = document.getElementById('url-form');
    const urlInput = document.getElementById('url-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const resultContainer = document.getElementById('result-container');
    const resultText = document.getElementById('result-text');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorContainer = document.getElementById('error-container');
    const errorText = document.getElementById('error-text');

    /**
     * Show error message with auto-hide
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
     * Update preview image
     * @param {string} src - Image source (URL or Data URL)
     */
    function updatePreview(src) {
        previewContainer.classList.remove('hidden');
        imagePreview.src = src;
        imagePreview.onload = () => {
            previewContainer.scrollIntoView({ behavior: 'smooth' });
        };
        imagePreview.onerror = () => {
            showError('Failed to load image preview');
            previewContainer.classList.add('hidden');
        };
    }

    /**
     * Validate image URL format
     * @param {string} url - URL to validate
     * @returns {boolean} - True if valid image URL
     */
    function isValidImageUrl(url) {
        return /^https?:\/\/.+\.(jpg|jpeg|png|gif|webp)$/i.test(url);
    }

    /**
     * Classify image and handle response
     * @param {FormData} formData - Form data containing file or URL
     */
    async function classifyImage(formData) {
        try {
            loadingSpinner.classList.remove('hidden');
            resultContainer.classList.add('hidden');

            const response = await fetch('/classify', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Classification failed');
            }

            loadingSpinner.classList.add('hidden');
            resultContainer.classList.remove('hidden');
            resultText.textContent = data.result;
            resultText.style.color = data.result.includes('Hotdog') ? 
                'var(--success-color)' : 'var(--error-color)';

        } catch (error) {
            loadingSpinner.classList.add('hidden');
            showError(error.message || 'Error classifying image');
            console.error('Error:', error);
        }
    }

    /**
     * Handle file selection
     * @param {File} file - Selected file
     */
    function handleFile(file) {
        resetDisplay();

        if (!file.type.startsWith('image/')) {
            showError('Please upload an image file!');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            updatePreview(e.target.result);
            
            const formData = new FormData();
            formData.append('file', file);
            classifyImage(formData);
        };
        reader.onerror = () => {
            showError('Error reading file');
        };
        reader.readAsDataURL(file);
    }

    /**
     * Handle URL submission
     * @param {string} url - Image URL
     */
    async function handleUrl(url) {
        resetDisplay();

        if (!isValidImageUrl(url)) {
            showError('Please enter a valid direct image URL');
            return;
        }

        try {
            updatePreview(url);

            const formData = new FormData();
            formData.append('url', url);
            await classifyImage(formData);

        } catch (error) {
            showError('Error processing image URL');
            console.error('Error:', error);
        }
    }

    // File Input Event Listeners
    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length) {
            handleFile(fileInput.files[0]);
        }
    });

    // Drop Zone Event Listeners
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drop-zone--over');
    });

    ['dragleave', 'dragend'].forEach((type) => {
        dropZone.addEventListener(type, () => {
            dropZone.classList.remove('drop-zone--over');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drop-zone--over');

        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // URL Form Event Listener
    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        
        if (!url) return;

        await handleUrl(url);
        urlInput.value = ''; // Clear input after submission
    });
});