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
    const loadingSection = document.getElementById('loading-spinner');
    const errorSection = document.getElementById('error-section');
    const errorText = document.getElementById('error-text');

    // DOM Elements - Stats and History
    const totalCount = document.getElementById('total-count');
    const hotdogCount = document.getElementById('hotdog-count');
    const hotdogRate = document.getElementById('hotdog-rate');
    const historyList = document.getElementById('history-list');
    const resetStatsButton = document.getElementById('reset-stats');

    // State Management
    let history = JSON.parse(localStorage.getItem('hotdogHistory')) || [];
    let stats = {
        total: 0,
        hotdogs: 0
    };

    /**
     * Calculate and update statistics based on history
     */
    function calculateStats() {
        stats.total = history.length;
        stats.hotdogs = history.filter(item => item.isRealHotdog).length;
        
        // Update display
        totalCount.textContent = stats.total;
        hotdogCount.textContent = stats.hotdogs;
        const rate = stats.total ? ((stats.hotdogs / stats.total) * 100).toFixed(1) : '0.0';
        hotdogRate.textContent = `${rate}%`;
    }

    /**
     * Add new item to history and update stats
     * @param {string} imageUrl URL or data URL of the image
     * @param {Object} result Classification result
     */
    function addToHistory(imageUrl, result) {
        const item = {
            imageUrl,
            result: result.result,
            isRealHotdog: result.isRealHotdog,
            timestamp: new Date().toLocaleString()
        };
        
        history.unshift(item);
        if (history.length > 50) history.pop(); // Keep last 50 items
        
        localStorage.setItem('hotdogHistory', JSON.stringify(history));
        updateHistoryDisplay();
        calculateStats();
    }

    /**
     * Reset history and stats
     */
    function resetStats() {
        history = [];
        localStorage.setItem('hotdogHistory', JSON.stringify(history));
        updateHistoryDisplay();
        calculateStats();
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
                    <div class="result" data-result="${item.isRealHotdog ? 'hotdog' : 'not-hotdog'}">
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
        
        errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

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
     * Update preview image
     * @param {string} src Image source (URL or Data URL)
     */
    function updatePreview(src) {
        previewImage.src = src;
        previewSection.classList.remove('hidden');
        previewImage.onload = () => {
            previewSection.scrollIntoView({ behavior: 'smooth' });
        };
        previewImage.onerror = () => {
            showError('Failed to load image preview');
            previewSection.classList.add('hidden');
        };
    }

    /**
     * Format and validate image URL
     * @param {string} url URL to format
     * @returns {string|null} Formatted URL or null if invalid
     */
    function formatImageUrl(url) {
        try {
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                return null;
            }

            urlDisplay.textContent = `Processing: ${url}`;
            urlDisplay.classList.remove('hidden');

            return url;
        } catch (error) {
            console.error('Error formatting URL:', error);
            return null;
        }
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

            if (!response.ok) {
                const data = await response.json();
                throw data;
            }

            const data = await response.json();
            
            loadingSection.classList.add('hidden');
            resultSection.classList.remove('hidden');
            
            resultText.textContent = data.result;
            resultText.setAttribute('data-result', data.isRealHotdog ? 'hotdog' : 'not-hotdog');

            // Add explanation if provided
            const explanationEl = document.querySelector('.result-explanation');
            if (explanationEl && data.explanation) {
                explanationEl.textContent = data.explanation;
                explanationEl.classList.remove('hidden');
            }

            addToHistory(previewImage.src, data);

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
            // Update preview immediately with the URL
            updatePreview(formattedUrl);

            const formData = new FormData();
            formData.append('url', formattedUrl);
            await classifyImage(formData);

        } catch (error) {
            showError('Unable to load image from URL');
            console.error('Error:', error);
            loadingSection.classList.add('hidden');
        }
    }

    // Event Listeners
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

    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        
        if (!url) return;

        await handleUrl(url);
        urlInput.value = '';
    });

    resetStatsButton?.addEventListener('click', () => {
        if (confirm('Are you sure you want to reset history and statistics?')) {
            resetStats();
        }
    });

    // Initialize
    updateHistoryDisplay();
    calculateStats();
});