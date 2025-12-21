// Shared Content Management
console.log('Shared.js module loaded');

// Get API base URL
function getApiUrl() {
    // For local development on port 5000
    if (window.location.port === '5000') {
        return `${window.location.protocol}//${window.location.hostname}:5000/api`;
    }
    // For tunnels or production
    return `${window.location.origin}/api`;
}

export async function initSharedPage() {
    console.log('Initializing shared page...');
    await loadSharedContent();
}

async function loadSharedContent() {
    try {
        console.log('Loading shared content...');
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        console.log('Token exists:', !!token);
        
        const apiUrl = getApiUrl();
        console.log('API URL:', apiUrl);
        
        const response = await fetch(`${apiUrl}/content/my-shared`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Shared content loaded:', data);
        
        if (data.shared_content) {
            displaySharedContent(data.shared_content);
        } else {
            console.warn('No shared_content in response:', data);
            displaySharedContent([]);
        }
    } catch (error) {
        console.error('Error loading shared content:', error);
        showError('Failed to load shared content: ' + error.message);
    }
}

function displaySharedContent(contentList) {
    const container = document.getElementById('sharedContentList');
    
    if (!container) {
        console.error('Shared content container not found');
        return;
    }
    
    if (contentList.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-share-alt" style="font-size: 4rem; color: var(--text-muted); margin-bottom: 1rem;"></i>
                <p style="color: var(--text-muted);">No shared content yet</p>
                <p style="color: var(--text-muted); font-size: 0.9rem;">Share encrypted content and QR codes to see them here</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="shared-content-grid">';
    
    contentList.forEach(content => {
        const contentType = content.metadata?.type || 'unknown';
        const isFile = contentType === 'file';
        const filename = content.metadata?.filename || 'Untitled';
        const isActive = content.is_active;
        const viewCount = content.view_count || 0;
        const createdDate = new Date(content.created_at).toLocaleDateString();
        const createdTime = new Date(content.created_at).toLocaleTimeString();
        
        let typeIcon = 'fa-file';
        let typeLabel = 'Text';
        
        if (isFile) {
            const contentTypeStr = content.metadata?.content_type || '';
            if (contentTypeStr.startsWith('image/')) {
                typeIcon = 'fa-image';
                typeLabel = 'Image';
            } else if (contentTypeStr.startsWith('video/')) {
                typeIcon = 'fa-video';
                typeLabel = 'Video';
            } else if (contentTypeStr.startsWith('audio/')) {
                typeIcon = 'fa-music';
                typeLabel = 'Audio';
            } else {
                typeIcon = 'fa-file-alt';
                typeLabel = 'File';
            }
        } else {
            typeIcon = 'fa-align-left';
            typeLabel = 'Text';
        }
        
        html += `
            <div class="shared-content-card ${!isActive ? 'inactive' : ''}">
                <div class="card-header">
                    <div class="content-type-badge">
                        <i class="fas ${typeIcon}"></i> ${typeLabel}
                    </div>
                    <div class="status-badge ${isActive ? 'active' : 'inactive'}">
                        <i class="fas ${isActive ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                        ${isActive ? 'Active' : 'Inactive'}
                    </div>
                </div>
                
                <div class="card-body">
                    <h3 class="content-title" title="${filename}">
                        <i class="fas ${typeIcon}"></i> ${truncateText(filename, 30)}
                    </h3>
                    
                    <div class="content-details">
                        <div class="detail-row">
                            <i class="fas fa-user"></i>
                            <span><strong>Shared with:</strong> ${content.receiver_name}</span>
                        </div>
                        <div class="detail-row">
                            <i class="fas fa-eye"></i>
                            <span><strong>Views:</strong> ${viewCount}</span>
                        </div>
                        <div class="detail-row">
                            <i class="fas fa-calendar"></i>
                            <span><strong>Created:</strong> ${createdDate} at ${createdTime}</span>
                        </div>
                        ${content.metadata?.encryption_level ? `
                        <div class="detail-row">
                            <i class="fas fa-shield-alt"></i>
                            <span><strong>Encryption:</strong> ${content.metadata.encryption_name || content.metadata.encryption_level}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="card-footer">
                    ${isActive ? `
                        <button onclick="window.deactivateContent('${content.content_id}')" class="btn btn-danger btn-sm">
                            <i class="fas fa-ban"></i> Deactivate
                        </button>
                    ` : `
                        <button onclick="window.activateContent('${content.content_id}')" class="btn btn-success btn-sm">
                            <i class="fas fa-check"></i> Activate
                        </button>
                    `}
                    <button onclick="window.viewContentQR('${content.content_id}')" class="btn btn-primary btn-sm">
                        <i class="fas fa-qrcode"></i> View QR
                    </button>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

async function deactivateContent(contentId) {
    if (!confirm('Are you sure you want to deactivate this QR code? No one will be able to decode it.')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const apiUrl = getApiUrl();
        const response = await fetch(`${apiUrl}/content/deactivate/${contentId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to deactivate');
        }
        
        showSuccess('Content deactivated successfully');
        await loadSharedContent();
    } catch (error) {
        console.error('Error deactivating content:', error);
        showError(error.message || 'Failed to deactivate content');
    }
}

async function activateContent(contentId) {
    try {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const apiUrl = getApiUrl();
        const response = await fetch(`${apiUrl}/content/activate/${contentId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to activate');
        }
        
        showSuccess('Content activated successfully');
        await loadSharedContent();
    } catch (error) {
        console.error('Error activating content:', error);
        showError(error.message || 'Failed to activate content');
    }
}

async function viewContentQR(contentId) {
    try {
        console.log('Viewing QR for content:', contentId);
        
        // Fetch content details to get QR code
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const apiUrl = getApiUrl();
        
        const response = await fetch(`${apiUrl}/content/qr/${contentId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch QR code');
        }
        
        const data = await response.json();
        
        // Display QR code in modal
        if (data.qr_code && typeof window.generateQRCode === 'function') {
            window.generateQRCode(data.qr_code, {
                encryption_level: data.encryption_level || 'standard',
                encryption_name: data.encryption_name || 'Standard Encryption'
            });
        } else if (data.qr_code) {
            // Fallback: display QR directly
            const modalQrImage = document.getElementById('modalQrCodeImage');
            if (modalQrImage) {
                modalQrImage.innerHTML = '';
                const img = document.createElement('img');
                img.src = `data:image/png;base64,${data.qr_code}`;
                img.alt = 'QR Code';
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
                modalQrImage.appendChild(img);
                
                if (typeof window.showQRModal === 'function') {
                    window.showQRModal();
                }
            }
        }
        
    } catch (error) {
        console.error('Error viewing QR code:', error);
        showError('Failed to load QR code: ' + error.message);
    }
}

function showSuccess(message) {
    // Use window.showNotification if available, otherwise create our own
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, 'success');
        return;
    }
    
    const notification = document.createElement('div');
    notification.className = 'notification success show';
    notification.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showError(message) {
    // Use window.showNotification if available, otherwise create our own
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, 'error');
        return;
    }
    
    const notification = document.createElement('div');
    notification.className = 'notification error show';
    notification.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showInfo(message) {
    // Use window.showNotification if available, otherwise create our own
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, 'info');
        return;
    }
    
    const notification = document.createElement('div');
    notification.className = 'notification info show';
    notification.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Make functions globally available
window.deactivateContent = deactivateContent;
window.activateContent = activateContent;
window.viewContentQR = viewContentQR;
