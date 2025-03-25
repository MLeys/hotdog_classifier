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
    let stats = { total: 0, hotdogs: 0 };
  
    function calculateStats() {
      stats.total = history.length;
      stats.hotdogs = history.filter(item => item.isRealHotdog).length;
      totalCount.textContent = stats.total;
      hotdogCount.textContent = stats.hotdogs;
      const rate = stats.total ? ((stats.hotdogs / stats.total) * 100).toFixed(1) : '0.0';
      hotdogRate.textContent = `${rate}%`;
    }
  
    function addToHistory(imageUrl, result) {
      const item = {
        imageUrl,
        result: result.result,
        isRealHotdog: result.isRealHotdog,
        description: result.description || '',
        timestamp: new Date().toLocaleString()
      };
      history.unshift(item);
      if (history.length > 50) history.pop();
      localStorage.setItem('hotdogHistory', JSON.stringify(history));
      updateHistoryDisplay();
      calculateStats();
    }
  
    function resetStats() {
      history = [];
      localStorage.setItem('hotdogHistory', JSON.stringify(history));
      updateHistoryDisplay();
      calculateStats();
    }
  
    function updateHistoryDisplay() {
      historyList.innerHTML = history.map(item => `
        <div class="history-item">
          <div class="thumbnail">
            <img src="${item.imageUrl}" alt="Analyzed image" onerror="this.src='static/img/error.png'">
          </div>
          <div class="content">
            <div class="result" data-result="${item.isRealHotdog ? 'hotdog' : 'not-hotdog'}">
              ${item.result}
            </div>
            ${item.description ? `<div class="description">${item.description}</div>` : ''}
            <div class="timestamp">${item.timestamp}</div>
          </div>
        </div>
      `).join('');
    }
  
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
      setTimeout(() => { errorSection.classList.add('hidden'); }, 8000);
    }
  
    function resetDisplay() {
      resultSection.classList.add('hidden');
      loadingSection.classList.add('hidden');
      errorSection.classList.add('hidden');
      urlDisplay.classList.add('hidden');
    }
  
    function updatePreview(src) {
      previewImage.src = src;
      previewSection.classList.remove('hidden');
      previewImage.onload = () => { previewSection.scrollIntoView({ behavior: 'smooth' }); };
      previewImage.onerror = () => {
        showError('Failed to load image preview');
        previewSection.classList.add('hidden');
      };
    }
  
    function formatImageUrl(url) {
      try {
        if (!url.startsWith('http://') && !url.startsWith('https://')) return null;
        urlDisplay.textContent = `Processing: ${url}`;
        urlDisplay.classList.remove('hidden');
        return url;
      } catch (error) {
        console.error('Error formatting URL:', error);
        return null;
      }
    }
  
    async function classifyImage(formData, imageUrl = null) {
      try {
        loadingSection.classList.remove('hidden');
        resultSection.classList.add('hidden');
        const response = await fetch('/classify', { method: 'POST', body: formData });
        if (!response.ok) {
          const data = await response.json();
          throw data;
        }
        const data = await response.json();
        loadingSection.classList.add('hidden');
        resultSection.classList.remove('hidden');
        resultText.textContent = data.result;
        resultText.setAttribute('data-result', data.isRealHotdog ? 'hotdog' : 'not-hotdog');
        const explanationEl = document.querySelector('.result-explanation');
        if (explanationEl && data.description) {
          explanationEl.textContent = data.description;
          explanationEl.classList.remove('hidden');
        }
        const historyImageUrl = imageUrl || previewImage.src;
        addToHistory(historyImageUrl, { ...data, description: data.description });
      } catch (error) {
        loadingSection.classList.add('hidden');
        showError(error);
        console.error('Classification error:', error);
      }
    }
  
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
      reader.onerror = () => { showError('Error reading file'); };
      reader.readAsDataURL(file);
    }
  
    async function handleUrl(url) {
      resetDisplay();
      if (!url.startsWith('http://') && !url.startsWith('https://') && !url.startsWith('data:image')) {
        showError('Please enter a valid URL or base64 image data');
        return;
      }
      try {
        loadingSection.classList.remove('hidden');
        updatePreview(url);
        const formData = new FormData();
        if (url.startsWith('data:image')) {
          formData.append('base64', url);
        } else {
          formData.append('url', url);
        }
        await classifyImage(formData, url);
      } catch (error) {
        showError('Unable to load image from URL or base64 data');
        console.error('Error:', error);
        loadingSection.classList.add('hidden');
      }
    }
  
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
  
    updateHistoryDisplay();
    calculateStats();
  });