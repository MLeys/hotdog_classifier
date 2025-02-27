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

    // DOM Elements - Stats
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
     * Show error message
     * @param {string} message Error message to display
     */
    function showError(message) {
        errorText.textContent = message;
        errorSection.classList.remove('hidden');
        setTimeout(() => {
            errorSection.classList.add('hidden');
        }, 5000);
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
     * Format and validate image URL
     * @param {string} url URL to format
     * @returns {string|null} Formatted URL or null if invalid
     */
    function formatImageUrl(url) {
        try {
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                return null;
            }

            let cleanUrl = url.split('?')[0].split('#')[0];
            const hasImageExt = /\.(jpg|jpeg|png|gif|webp)$/i.test(cleanUrl);

            if (!hasImageExt) {
                cleanUrl = cleanUrl.replace(/\/$/, '') + '.jpg';
                urlDisplay.textContent = `Trying: ${cleanUrl}`;
                urlDisplay.classList.remove('hidden');
            }

            return cleanUrl;
        } catch (error) {
            console.error('Error formatting URL:', error);
            return null;
        }
    }

    /**
     * Send classification request to server
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

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'Classification failed');
            }

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
            showError(error.message || 'Error classifying image');
            console.error('Error:', error);
        }
    }

    /**
     * Handle file upload
     * @param {File} file Uploaded file
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
                testImg.src = formattedUrl;
            });

            loadingSection.classList.remove('hidden');
            await imgPromise;
            
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