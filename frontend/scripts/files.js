// My Files Management
console.log('Files.js module loaded');

// Store uploaded files
let myFiles = [];
let viewMode = 'list'; // 'list' or 'grid'

// Get API base URL
function getApiUrl() {
    // Fallback to current origin if API_BASE_URL not set
    return window.API_BASE_URL || `${window.location.origin}/api`;
}

// Initialize Files Page
async function initFilesPage() {
    console.log('Initializing Files page...');
    setupFileUpload();
    setupViewToggle();
    setupSorting();
    await loadMyFiles();
}

// Make initFilesPage available globally
window.initFilesPage = initFilesPage;

// Setup file upload functionality
function setupFileUpload() {
    const uploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('myFileInput');
    const browseBtn = document.getElementById('browseFilesBtn');

    // Browse button click
    if (browseBtn) {
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    // Upload area click
    if (uploadArea) {
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
    }

    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });
    }

    // Drag and drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            handleFiles(e.dataTransfer.files);
        });
    }
}

// Handle selected files
async function handleFiles(files) {
    if (files.length === 0) return;

    const progressDiv = document.getElementById('uploadProgress');
    const fileNameSpan = document.getElementById('uploadFileName');
    const percentSpan = document.getElementById('uploadPercent');
    const progressBar = document.getElementById('uploadProgressBar');

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            showError(`${file.name} is too large (max 10MB)`);
            continue;
        }

        try {
            // Show progress
            progressDiv.classList.remove('hidden');
            fileNameSpan.textContent = `Uploading ${file.name}...`;
            percentSpan.textContent = '0%';
            progressBar.style.width = '0%';

            // Create file object
            const fileData = {
                name: file.name,
                size: file.size,
                type: file.type,
                uploadedAt: new Date().toISOString(),
                file: file // Store actual file for QR generation
            };

            // Simulate upload progress (since we're storing locally)
            await simulateUpload(progressBar, percentSpan);

            // Add to files list
            myFiles.push(fileData);
            console.log('File added to myFiles array:', fileData);
            console.log('Total files now:', myFiles.length);
            
            showSuccess(`${file.name} uploaded successfully!`);
        } catch (error) {
            showError(`Failed to upload ${file.name}: ${error.message}`);
        }
    }

    // Hide progress and refresh list
    setTimeout(() => {
        progressDiv.classList.add('hidden');
        displayFiles();
    }, 500);

    // Clear input
    document.getElementById('myFileInput').value = '';
}

// Simulate upload progress
function simulateUpload(progressBar, percentSpan) {
    return new Promise((resolve) => {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                resolve();
            }
            progressBar.style.width = `${progress}%`;
            percentSpan.textContent = `${Math.floor(progress)}%`;
        }, 100);
    });
}

// Load my files
async function loadMyFiles() {
    // For now, display stored files from local array
    displayFiles();
}

// Display files
function displayFiles() {
    console.log('displayFiles called, myFiles length:', myFiles.length);
    const container = document.getElementById('filesListContainer');
    
    if (!container) {
        console.error('filesListContainer not found!');
        return;
    }
    
    if (!myFiles || myFiles.length === 0) {
        console.log('No files to display');
        container.innerHTML = '<p class="text-muted text-center">No files uploaded yet</p>';
        return;
    }

    console.log('Displaying', myFiles.length, 'files');
    
    // Sort files
    const sortBy = document.getElementById('filesSortBy')?.value || 'date';
    const sortedFiles = sortFiles(myFiles, sortBy);

    if (viewMode === 'grid') {
        displayFilesGrid(sortedFiles, container);
    } else {
        displayFilesList(sortedFiles, container);
    }
}

// Display files in list view
function displayFilesList(files, container) {
    const html = files.map(file => {
        const icon = getFileIcon(file.type || file.name);
        const iconClass = getFileIconClass(file.type || file.name);
        const size = formatFileSize(file.size);
        const date = formatDate(file.uploadedAt);

        return `
            <div class="file-item">
                <div class="file-icon ${iconClass}">
                    <i class="${icon}"></i>
                </div>
                <div class="file-info">
                    <div class="file-name">${escapeHtml(file.name)}</div>
                    <div class="file-meta">
                        <span><i class="fas fa-hdd"></i> ${size}</span>
                        <span><i class="fas fa-clock"></i> ${date}</span>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-primary" onclick="window.shareFileViaQR('${escapeHtml(file.name)}')" title="Share via QR">
                        <i class="fas fa-qrcode"></i> Share
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="window.downloadMyFile('${escapeHtml(file.name)}')" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="window.deleteMyFile('${escapeHtml(file.name)}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
}

// Display files in grid view
function displayFilesGrid(files, container) {
    container.className = 'card-body files-grid-view';
    
    const html = files.map(file => {
        const icon = getFileIcon(file.type || file.name);
        const iconClass = getFileIconClass(file.type || file.name);
        const size = formatFileSize(file.size);

        return `
            <div class="file-grid-item">
                <div class="file-icon ${iconClass}">
                    <i class="${icon}"></i>
                </div>
                <div class="file-name">${escapeHtml(file.name)}</div>
                <div class="file-meta">
                    <span>${size}</span>
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-primary" onclick="window.shareFileViaQR('${escapeHtml(file.name)}')" title="Share via QR">
                        <i class="fas fa-qrcode"></i>
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="window.downloadMyFile('${escapeHtml(file.name)}')" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="window.deleteMyFile('${escapeHtml(file.name)}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
}

// Sort files
function sortFiles(files, sortBy) {
    const sorted = [...files];
    
    switch (sortBy) {
        case 'name':
            sorted.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'size':
            sorted.sort((a, b) => b.size - a.size);
            break;
        case 'type':
            sorted.sort((a, b) => (a.type || '').localeCompare(b.type || ''));
            break;
        case 'date':
        default:
            sorted.sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt));
            break;
    }
    
    return sorted;
}

// Setup view toggle
function setupViewToggle() {
    const toggleBtn = document.getElementById('filesViewToggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            viewMode = viewMode === 'list' ? 'grid' : 'list';
            toggleBtn.innerHTML = viewMode === 'list' 
                ? '<i class="fas fa-th"></i>' 
                : '<i class="fas fa-list"></i>';
            displayFiles();
        });
    }
}

// Setup sorting
function setupSorting() {
    const sortSelect = document.getElementById('filesSortBy');
    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            displayFiles();
        });
    }
}

// Share file via QR
window.shareFileViaQR = async function(fileName) {
    const file = myFiles.find(f => f.name === fileName);
    if (!file) {
        showError('File not found');
        return;
    }

    try {
        // Show loading
        showInfo('Generating QR code...');

        // Get receiver selection from Generate QR page or default to public
        const receiverId = null; // Public by default
        const encryptionLevel = 'standard';

        // Use existing shareFile function from qr.js
        const result = await shareFile(file.file, receiverId, null, encryptionLevel);
        
        // Generate and display QR code
        generateQRCode(result.qr_code, {
            encryption_level: result.encryption_level,
            encryption_name: result.encryption_name
        });
        
        showSuccess(`QR code generated for ${file.name}!`);
        
        // Switch to generate section to show QR
        if (typeof showSection === 'function') {
            showSection('generate');
        }
    } catch (error) {
        console.error('Error sharing file:', error);
        showError('Failed to generate QR code: ' + error.message);
    }
};

// Download file
window.downloadMyFile = function(fileName) {
    const file = myFiles.find(f => f.name === fileName);
    if (!file || !file.file) {
        showError('File not found');
        return;
    }

    // Create download link
    const url = URL.createObjectURL(file.file);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showSuccess(`${file.name} downloaded!`);
};

// Delete file
window.deleteMyFile = function(fileName) {
    if (!confirm(`Are you sure you want to delete ${fileName}?`)) {
        return;
    }

    const index = myFiles.findIndex(f => f.name === fileName);
    if (index !== -1) {
        myFiles.splice(index, 1);
        displayFiles();
        showSuccess(`${fileName} deleted successfully`);
    }
};

// Helper: Get file icon
function getFileIcon(typeOrName) {
    const type = (typeOrName || '').toLowerCase();
    const name = (typeOrName || '').toLowerCase();
    
    if (type.startsWith('image/') || /\.(jpg|jpeg|png|gif|svg|webp)$/.test(name)) {
        return 'fas fa-image';
    } else if (type.startsWith('video/') || /\.(mp4|avi|mov|mkv|webm)$/.test(name)) {
        return 'fas fa-video';
    } else if (type.startsWith('audio/') || /\.(mp3|wav|ogg|m4a)$/.test(name)) {
        return 'fas fa-music';
    } else if (type.includes('pdf') || name.endsWith('.pdf')) {
        return 'fas fa-file-pdf';
    } else if (type.includes('word') || /\.(doc|docx)$/.test(name)) {
        return 'fas fa-file-word';
    } else if (type.includes('excel') || /\.(xls|xlsx)$/.test(name)) {
        return 'fas fa-file-excel';
    } else if (type.includes('zip') || type.includes('rar') || /\.(zip|rar|7z|tar|gz)$/.test(name)) {
        return 'fas fa-file-archive';
    } else if (name.endsWith('.txt')) {
        return 'fas fa-file-alt';
    }
    return 'fas fa-file';
}

// Helper: Get file icon class
function getFileIconClass(typeOrName) {
    const type = (typeOrName || '').toLowerCase();
    const name = (typeOrName || '').toLowerCase();
    
    if (type.startsWith('image/') || /\.(jpg|jpeg|png|gif|svg|webp)$/.test(name)) {
        return 'image';
    } else if (type.startsWith('video/') || /\.(mp4|avi|mov|mkv|webm)$/.test(name)) {
        return 'video';
    } else if (type.startsWith('audio/') || /\.(mp3|wav|ogg|m4a)$/.test(name)) {
        return 'audio';
    } else if (type.includes('zip') || type.includes('rar') || /\.(zip|rar|7z|tar|gz)$/.test(name)) {
        return 'archive';
    }
    return 'document';
}

// Helper: Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Helper: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    // Less than 1 minute
    if (diff < 60000) return 'Just now';
    
    // Less than 1 hour
    if (diff < 3600000) {
        const mins = Math.floor(diff / 60000);
        return `${mins} min${mins > 1 ? 's' : ''} ago`;
    }
    
    // Less than 24 hours
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
    
    // Less than 7 days
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
    
    // Format as date
    return date.toLocaleDateString();
}

// Helper: Escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Helper functions for notifications
function showSuccess(message) {
    if (typeof window.showSuccess === 'function') {
        window.showSuccess(message);
    } else {
        console.log('✓', message);
    }
}

function showError(message) {
    if (typeof window.showError === 'function') {
        window.showError(message);
    } else {
        console.error('✗', message);
    }
}

function showInfo(message) {
    if (typeof window.showInfo === 'function') {
        window.showInfo(message);
    } else {
        console.info('ℹ', message);
    }
}
