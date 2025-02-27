/**
 * Main JavaScript file for the Hotdog Classifier application.
 * Handles file uploads, URL inputs, API interactions, and history management.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Upload and URL
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('file-input');
    const urlForm = document.getElementById('url-form');
    const urlInput = document.getElementById('url-input');
    const urlDisplay = document.getElementById('url-display');

    // DOM Elements - Display Sections
    const previewSection = document.getElementById('preview-section');
    const previewImage = document.getElementById('preview-image');
    const resultSection = document.getElementById('result-section');
    const resultText = document.getElementById('result-text');
    const loadingSection = document.getElementById('loading-section');
    const errorSection = document.getElementById('error-section');
    const errorText = document.getElementById('error-text');

    // DOM Elements - Stats and History
    const totalCount = document.getElementById('total-count');
    const hotdogCount = document.getElementById('hotdog-count');
    const hotdogRate = document.getElementById('hotdog-rate');
    const historyList = document.getElementById('history-list');

    // State Management
    let stats = JSON.parse(localStorage.getItem('hotdogStats')) || {
        total: 0,
        hotdogs: 0
    };
    let history = JSON.parse(localStorage.getItem('hotdogHistory')) || [];

    /**
     * Update statistics display and save to localStorage
     */
    function updateStats() {
        totalCount.textContent = stats.total;
        hotdogCount.textContent = stats.hotdogs;
        const rate = stats.total ? ((stats.hotdogs / stats.total) * 100).toFixed(1) : 0;
        hotdogRate.textContent = `${rate}%`;
        localStorage.setItem('hotdogStats', JSON.stringify(stats));
    }

    /**
     * Add new item to history and update display
     * @param {string} imageUrl URL or data URL of the image
     * @param {string} result Classification result
     */
    function addToHistory(imageUrl, result) {
        const item = {
            imageUrl,
            result,
            timestamp: new Date().toLocaleString()
        };
        
        history.unshift(item);
        if (history.length > 50) history.pop(); // Keep last 50 items
        localStorage.setItem('hotdogHistory', JSON.stringify(history));
        updateHistoryDisplay();
    }

    /**
     * Update history display in sidebar
     */
    function updateHistoryDisplay() {
        historyList.innerHTML = history.map(item => `
            <div class="history-item">
                <div class="thumbnail">
                    <img src="${item.imageUrl}" alt="Analyzed image">
                </div>
                <div class="content">
                    <div class="result" style="color: ${
                        item.result.includes('Hotdog') ? 
                        'var(--success-color)' : 'var(--error-color)'
                    }">
                        ${item.result}
                    </div>
                    <div class="timestamp">${item.timestamp}</div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Show error message with details if available
     * @param {string|Object} error - Error message or object
     */
    function showError(error) {
        let message = '';
        let details = '';

        if (typeof error === 'string') {
            message = error;
        } else if (error.error) {
            message = error.error;
            if (error.details) {
                details = `\nDetails: ${JSON.stringify(error.details, null, 2)}`;
            }
        } else {
            message = 'An unexpected error occurred';
        }

        errorText.textContent = message + details;
        errorSection.classList.remove('hidden');
        
        // Scroll error into view
        errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Auto-hide after 8 seconds
        setTimeout(() => {
            errorSection.classList.add('hidden');
        }, 8000);
    }

    /**
     * Reset all display sections
     */
    function resetDisplay() {
        resultSection.classList.add('hidden');
        loadingSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        urlDisplay.classList.add('hidden');
    }

    /**
     * Update image preview
     * @param {string} src Image source (URL or Data URL)
     */
    function updatePreview(src) {
        previewImage.src = src;
        previewImage.onload = () => {
            previewSection.classList.remove('hidden');
            previewSection.scrollIntoView({ behavior: 'smooth' });
        };
        previewImage.onerror = () => {
            showError('Failed to load image preview');
            previewSection.classList.add('hidden');
        };
    }

    /**
     * Format and validate image URL, handling various URL formats
     * @param {string} url URL to format
     * @returns {string|null} Formatted URL or null if invalid
     */
    function formatImageUrl(url) {
        try {
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                return null;
            }

            // Display the URL being tried
            urlDisplay.textContent = `Processing: ${url}`;
            urlDisplay.classList.remove('hidden');

            // For Bing image URLs, use as is
            if (url.includes('bing.com/th/id/')) {
                return url;
            }

            // For other URLs, check and handle image extensions
            let cleanUrl = url.split('?')[0].split('#')[0];
            const hasImageExt = /\.(jpg|jpeg|png|gif|webp)$/i.test(cleanUrl);

            if (!hasImageExt) {
                cleanUrl = cleanUrl.replace(/\/$/, '') + '.jpg';
                urlDisplay.textContent = `Trying modified URL: ${cleanUrl}`;
            }

            return cleanUrl;
        } catch (error) {
            console.error('Error formatting URL:', error);
            return null;
        }
    }

    /**
     * Handle API response
     * @param {Response} response - Fetch API response
     * @returns {Promise} - Parsed response
     */
    async function handleResponse(response) {
        const data = await response.json();
        
        if (!response.ok) {
            console.error('API Error:', {
                status: response.status,
                statusText: response.statusText,
                data: data
            });
            
            throw new Error(data.error || 'Classification failed');
        }
        
        return data;
    }

    /**
     * Classify image and handle response
     * @param {FormData} formData Form data containing file or URL
     */
    async function classifyImage(formData) {
        try {
            loadingSection.classList.remove('hidden');
            resultSection.classList.add('hidden');

            const response = await fetch('/classify', {
                method: 'POST',
                body: formData
            });

            const data = await handleResponse(response);
            
            loadingSection.classList.add('hidden');
            resultSection.classList.remove('hidden');
            resultText.textContent = data.result;
            resultText.style.color = data.result.includes('Hotdog') ? 
                'var(--success-color)' : 'var(--error-color)';

            // Update statistics
            stats.total++;
            if (data.result.includes('Hotdog')) {
                stats.hotdogs++;
            }
            updateStats();

            // Add to history
            addToHistory(previewImage.src, data.result);

        } catch (error) {
            loadingSection.classList.add('hidden');
            showError(error);
            console.error('Classification error:', error);
        }
    }

    /**
     * Handle file selection
     * @param {File} file Selected file
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
     * @param {string} url Image URL
     */
    async function handleUrl(url) {
        resetDisplay();

        const formattedUrl = formatImageUrl(url);
        if (!formattedUrl) {
            showError('Please enter a valid URL');
            return;
        }

        try {
            // Try to load the image first
            const imgPromise = new Promise((resolve, reject) => {
                const testImg = new Image();
                testImg.onload = () => resolve(formattedUrl);
                testImg.onerror = () => reject('Failed to load image');
                
                // Add crossOrigin attribute to handle CORS
                testImg.crossOrigin = "anonymous";
                testImg.src = formattedUrl;
            });

            loadingSection.classList.remove('hidden');
            await imgPromise;
            
            // Convert image to base64 if it's a direct URL
            const formData = new FormData();
            
            try {
                // Try to convert to base64 first
                const response = await fetch(formattedUrl);
                const blob = await response.blob();
                const reader = new FileReader();
                
                const base64Promise = new Promise((resolve, reject) => {
                    reader.onload = () => resolve(reader.result);
                    reader.onerror = () => reject('Failed to convert image');
                });
                
                reader.readAsDataURL(blob);
                const base64Data = await base64Promise;
                
                formData.append('base64', base64Data);
            } catch (error) {
                // Fallback to direct URL if base64 conversion fails
                formData.append('url', formattedUrl);
            }

            updatePreview(formattedUrl);
            await classifyImage(formData);

        } catch (error) {
            showError('Unable to load image from URL');
            console.error('Error:', error);
            loadingSection.classList.add('hidden');
        }
    }

    // Event Listeners - File Upload
    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length) {
            handleFile(fileInput.files[0]);
        }
    });

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderStyle = 'solid';
    });

    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, () => {
            dropZone.style.borderStyle = 'dashed';
        });
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderStyle = 'dashed';
        
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // Event Listener - URL Form
    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        
        if (!url) return;

        await handleUrl(url);
        urlInput.value = ''; // Clear input after submission
    });

    // Initialize
    updateStats();
    updateHistoryDisplay();
});