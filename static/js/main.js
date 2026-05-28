document.addEventListener('DOMContentLoaded', () => {
    setupToolCards();
    setupAllTools();
});

function setupToolCards() {
    const toolCards = document.querySelectorAll('.tool-card');
    toolCards.forEach(card => {
        card.addEventListener('click', () => {
            const toolId = card.dataset.tool;
            openPanel(toolId);
        });
    });
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

function openPanel(toolId) {
    const toolCards = document.querySelectorAll('.tool-card');
    const toolPanels = document.querySelectorAll('.tool-panel');

    toolCards.forEach(c => c.classList.remove('active'));
    toolPanels.forEach(p => p.classList.remove('active'));

    const card = document.querySelector(`.tool-card[data-tool="${toolId}"]`);
    const panel = document.getElementById(`${toolId}-panel`);

    if (card) card.classList.add('active');
    if (panel) {
        panel.classList.add('active');
        window.scrollTo({ top: panel.offsetTop - 100, behavior: 'smooth' });
    }
}

function closePanel(toolId) {
    const card = document.querySelector(`.tool-card[data-tool="${toolId}"]`);
    const panel = document.getElementById(`${toolId}-panel`);

    if (card) card.classList.remove('active');
    if (panel) panel.classList.remove('active');
}

function setupAllTools() {
    const tools = ['merge', 'split', 'extract-pages', 'remove-pages', 'rotate', 'resize', 'compress', 'info', 'protect', 'unlock', 'image', 'extract'];

    tools.forEach(toolId => {
        setupTool(toolId);
    });
}

function setupTool(toolId) {
    const panel = document.getElementById(`${toolId}-panel`);
    if (!panel) return;

    const uploadArea = panel.querySelector('.upload-area');
    const fileInput = panel.querySelector('input[type="file"]');
    const fileList = panel.querySelector('.file-list');
    const submitBtn = panel.querySelector('.submit-btn');

    if (!fileInput || !submitBtn) return;

    let files = [];
    const maxFiles = (toolId === 'merge' || toolId === 'image') ? 50 : 1;

    if (uploadArea) {
        uploadArea.addEventListener('click', () => fileInput.click());

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFiles(Array.from(e.dataTransfer.files));
        });
    }

    fileInput.addEventListener('change', (e) => {
        handleFiles(Array.from(e.target.files));
    });

    function handleFiles(filesList) {
        const validFiles = filesList.filter(f => {
            if (toolId === 'image') {
                return f.type.startsWith('image/');
            }
            return f.type === 'application/pdf';
        });

        files = [...files, ...validFiles].slice(0, maxFiles);
        renderFileList();
    }

    function renderFileList() {
        if (!fileList) return;

        if (files.length === 0) {
            fileList.innerHTML = '';
            submitBtn.disabled = true;
            return;
        }

        fileList.innerHTML = files.map((file, index) => `
            <div class="file-item">
                <div class="file-icon">${getFileIcon(file.type)}</div>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${formatBytes(file.size)}</div>
                </div>
                <button class="remove-btn" onclick="removeFile('${toolId}', ${index})">Remove</button>
            </div>
        `).join('');

        const minRequired = (toolId === 'merge') ? 2 : 1;
        submitBtn.disabled = files.length < minRequired;
    }

    window.removeFile = (toolId, index) => {
        files.splice(index, 1);
        renderFileList();
    };

    submitBtn.addEventListener('click', () => processTool(toolId, files));
}

function processTool(toolId, files) {
    if (!files || files.length === 0) return;

    const panel = document.getElementById(`${toolId}-panel`);
    const progressContainer = panel.querySelector('.progress-container');
    const progressFill = panel.querySelector('.progress-fill');
    const progressText = panel.querySelector('.progress-text');
    const resultContainer = panel.querySelector('.result-container');

    progressContainer.style.display = 'block';
    resultContainer.style.display = 'none';
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading files...';

    const formData = new FormData();

    if (toolId === 'merge' || toolId === 'image') {
        files.forEach(file => formData.append('files', file));
    } else {
        formData.append('file', files[0]);

        if (toolId === 'split') {
            formData.append('start_page', document.getElementById('split-start')?.value || 1);
            formData.append('end_page', document.getElementById('split-end')?.value || 1);
        } else if (toolId === 'rotate') {
            formData.append('angle', document.getElementById('rotate-angle')?.value || 90);
        } else if (toolId === 'resize') {
            formData.append('page_size', document.getElementById('resize-size')?.value || 'A4');
            formData.append('orientation', document.getElementById('resize-orientation')?.value || 'portrait');
        } else if (toolId === 'extract-pages') {
            formData.append('pages', document.getElementById('extract-pages-list')?.value || '');
        } else if (toolId === 'remove-pages') {
            formData.append('pages', document.getElementById('remove-pages-list')?.value || '');
        } else if (toolId === 'protect') {
            const password = document.getElementById('protect-password')?.value;
            const confirm = document.getElementById('protect-confirm')?.value;
            if (password !== confirm) {
                showResult(resultContainer, 'error', 'Passwords do not match!');
                progressContainer.style.display = 'none';
                return;
            }
            formData.append('password', password);
        } else if (toolId === 'unlock') {
            const password = document.getElementById('unlock-password')?.value;
            if (!password) {
                showResult(resultContainer, 'error', 'Please enter the PDF password!');
                progressContainer.style.display = 'none';
                return;
            }
            formData.append('password', password);
        }
    }

    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 12;
        if (progress <= 85) {
            progressFill.style.width = `${progress}%`;
            progressText.textContent = `Processing... ${Math.round(progress)}%`;
        }
    }, 200);

    const endpoints = {
        'merge': '/api/merge',
        'split': '/api/split',
        'extract-pages': '/api/extract-pages',
        'remove-pages': '/api/remove-pages',
        'rotate': '/api/rotate',
        'resize': '/api/resize',
        'compress': '/api/compress',
        'info': '/api/pdf-info',
        'protect': '/api/protect',
        'unlock': '/api/unlock',
        'image': '/api/image-to-pdf',
        'extract': '/api/extract-text'
    };

    fetch(endpoints[toolId], {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        progressText.textContent = 'Complete!';

        setTimeout(() => {
            progressContainer.style.display = 'none';

            if (data.error) {
                showResult(resultContainer, 'error', data.error);
            } else if (data.success) {
                showResult(resultContainer, 'success', data, toolId);
            } else {
                showResult(resultContainer, 'error', 'Something went wrong!');
            }
            resultContainer.style.display = 'block';
        }, 500);
    })
    .catch(error => {
        clearInterval(progressInterval);
        progressContainer.style.display = 'none';
        showResult(resultContainer, 'error', error.message || 'An error occurred');
        resultContainer.style.display = 'block';
    });
}

function showResult(container, type, data, toolId) {
    container.className = `result-container ${type}`;

    if (type === 'error') {
        container.innerHTML = `
            <div class="result-icon">&#10060;</div>
            <h3>Error</h3>
            <p>${escapeHtml(data)}</p>
        `;
        return;
    }

    let html = `
        <div class="result-icon">&#10004;</div>
        <h3>Success!</h3>
    `;

    if (toolId === 'compress' && data.original_size) {
        const savings = ((data.original_size - data.compressed_size) / data.original_size * 100).toFixed(1);
        html += `
            <div class="result-stats">
                <div class="stat-item">
                    <div class="stat-value">${formatBytes(data.original_size)}</div>
                    <div class="stat-label">Original Size</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${formatBytes(data.compressed_size)}</div>
                    <div class="stat-label">New Size</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${savings}%</div>
                    <div class="stat-label">Saved</div>
                </div>
            </div>
            <p>Your PDF has been compressed successfully!</p>
        `;
    } else if (toolId === 'info') {
        html = `
            <div class="result-icon">&#128209;</div>
            <h3>PDF Information</h3>
            <div class="result-stats">
                <div class="stat-item">
                    <div class="stat-value">${data.pages || 0}</div>
                    <div class="stat-label">Pages</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${formatBytes(data.size)}</div>
                    <div class="stat-label">File Size</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.encrypted ? 'Yes' : 'No'}</div>
                    <div class="stat-label">Encrypted</div>
                </div>
            </div>
            ${data.metadata ? `<p style="margin-top:15px;"><strong>Title:</strong> ${data.metadata.title || 'N/A'}<br><strong>Author:</strong> ${data.metadata.author || 'N/A'}</p>` : ''}
        `;
    } else if (toolId === 'extract' && data.text) {
        const preview = data.text.substring(0, 800);
        const truncated = data.text.length > 800;
        html += `
            <div class="result-stats">
                <div class="stat-item">
                    <div class="stat-value">${data.total_pages || 0}</div>
                    <div class="stat-label">Pages</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.word_count || 0}</div>
                    <div class="stat-label">Words</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.char_count || 0}</div>
                    <div class="stat-label">Characters</div>
                </div>
            </div>
            <div class="text-preview">${escapeHtml(preview)}${truncated ? '\n\n... (text truncated)' : ''}</div>
            <button class="btn btn-primary" onclick="copyText('${escapeHtml(data.text.replace(/'/g, "\\'").replace(/\n/g, "\\n"))}')">
                &#128203; Copy Text
            </button>
        `;
    } else if (toolId === 'image' && data.total_images) {
        html += `<p>${data.total_images} images converted to PDF (${formatBytes(data.file_size)})</p>`;
    } else if (toolId === 'extract-pages' && data.pages_extracted) {
        html += `
            <div class="result-stats">
                <div class="stat-item">
                    <div class="stat-value">${data.pages_extracted}</div>
                    <div class="stat-label">Pages Extracted</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${formatBytes(data.file_size)}</div>
                    <div class="stat-label">File Size</div>
                </div>
            </div>
            <p>Your pages have been extracted successfully!</p>
        `;
    } else if (toolId === 'remove-pages' && data.pages_removed) {
        html += `
            <div class="result-stats">
                <div class="stat-item">
                    <div class="stat-value">${data.pages_removed}</div>
                    <div class="stat-label">Pages Removed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${data.pages_remaining}</div>
                    <div class="stat-label">Pages Remaining</div>
                </div>
            </div>
            <p>Your pages have been removed successfully!</p>
        `;
    } else {
        html += `<p>Your file is ready for download (${formatBytes(data.file_size || 0)})</p>`;
    }

    if (data.download_url) {
        html += `
            <a href="${data.download_url}" class="btn btn-primary" download style="margin-top: 15px;">
                &#128229; Download File
            </a>
        `;
    }

    container.innerHTML = html;
}

function copyText(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Text copied to clipboard!');
    }).catch(() => {
        alert('Failed to copy text');
    });
}

function formatBytes(bytes) {
    if (bytes === 0 || !bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getFileIcon(type) {
    if (type === 'application/pdf') return '&#128196;';
    if (type.startsWith('image/')) return '&#128444;';
    return '&#128196;';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}