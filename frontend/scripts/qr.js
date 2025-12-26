// QR Code Functions

// Content Sharing
async function shareText(text, receiverId = null, expiresIn = null, encryptionLevel = 'standard') {
    try {
        const response = await apiRequest('/content/share/text', {
            method: 'POST',
            body: JSON.stringify({
                text,
                receiver_id: receiverId,
                expires_in: expiresIn,
                encryption_level: encryptionLevel
            })
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Sharing failed');
        }
    } catch (error) {
        throw error;
    }
}

async function shareFile(file, receiverId = null, expiresIn = null, encryptionLevel = 'standard') {
    try {
        const formData = new FormData();
        formData.append('file', file);
        if (receiverId) formData.append('receiver_id', receiverId);
        if (expiresIn) formData.append('expires_in', expiresIn);
        formData.append('encryption_level', encryptionLevel);
        
        const response = await fetch(`${API_BASE_URL}/content/share/file`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${state.token}`
            },
            body: formData
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'File upload failed');
        }
    } catch (error) {
        throw error;
    }
}

async function decodeContent(qrData) {
    try {
        const response = await apiRequest('/content/decode', {
            method: 'POST',
            body: JSON.stringify({ qr_data: qrData })
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            const errorData = await response.json();
            const errorMsg = errorData.error || 'Failed to decode QR code';
            throw new Error(errorMsg);
        }
    } catch (error) {
        if (error.message) {
            throw error;
        }
        throw new Error('Network error. Please try again');
    }
}

// QR Code Generation
function generateQRCode(qrData, encryptionInfo = null) {
    console.log('generateQRCode called with data length:', qrData ? qrData.length : 0);
    
    const modalQrImage = document.getElementById('modalQrCodeImage');
    const modal = document.getElementById('qrModal');
    
    console.log('modalQrCodeImage element:', modalQrImage);
    console.log('qrModal element:', modal);
    
    if (!modalQrImage) {
        console.error('modalQrCodeImage not found!');
        return;
    }
    
    modalQrImage.innerHTML = '';
    
    // If qrData is base64 image data
    if (typeof qrData === 'string' && qrData.length > 0) {
        const img = document.createElement('img');
        img.src = `data:image/png;base64,${qrData}`;
        img.alt = 'QR Code';
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        modalQrImage.appendChild(img);
        
        console.log('QR image added to modal');
        
        // Store qrData for download
        window.currentQRData = qrData;
        window.currentEncryptionInfo = encryptionInfo;
        
        // Show the modal
        if (typeof showQRModal === 'function') {
            console.log('Calling showQRModal...');
            showQRModal();
            console.log('Modal hidden class:', modal.classList.contains('hidden'));
        } else {
            console.error('showQRModal function not found!');
        }
    } else {
        console.error('Invalid QR data:', qrData);
    }
}

function downloadQRCode() {
    if (window.currentQRData) {
        const link = document.createElement('a');
        link.href = `data:image/png;base64,${window.currentQRData}`;
        link.download = `secure-qr-${Date.now()}.png`;
        link.click();
    }
}

// Make downloadQRCode available globally
window.downloadQRCode = downloadQRCode;

function downloadQR(qrData) {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${qrData}`;
    link.download = `secure-qr-${Date.now()}.png`;
    link.click();
}

// QR Scanner using WebRTC
let currentStream = null;

async function startQRScanner() {
    const video = document.getElementById('scannerVideo');
    const startBtn = document.getElementById('startCameraBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    
    if (!video) return;
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        
        currentStream = stream;
        video.srcObject = stream;
        video.style.display = 'block';
        video.play();
        
        if (startBtn) startBtn.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'inline-flex';
        
        showSuccess('Camera started. Point at a QR code to scan.');
        
    } catch (error) {
        console.error('Camera access failed:', error);
        showError('Could not access camera. Please check permissions.');
    }
}

window.stopQRScanner = function() {
    const video = document.getElementById('scannerVideo');
    const startBtn = document.getElementById('startCameraBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
    
    if (video) {
        video.srcObject = null;
        video.style.display = 'none';
    }
    
    if (startBtn) startBtn.style.display = 'inline-flex';
    if (stopBtn) stopBtn.style.display = 'none';
};

// Decode QR Code from uploaded image
async function decodeQRImage(file) {
    if (!file || !file.type.startsWith('image/')) {
        showError('Please select a valid image file');
        return;
    }
    
    try {
        const reader = new FileReader();
        
        reader.onload = async function(e) {
            const img = new Image();
            img.onload = async function() {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                // Use jsQR to decode the QR code
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const code = jsQR(imageData.data, imageData.width, imageData.height);
                
                if (code && code.data) {
                    try {
                        // Parse the QR code data
                        const qrData = JSON.parse(code.data);
                        
                        if (qrData.content_id) {
                            const result = await decodeContent(qrData.content_id);
                            displayDecryptedContent(result);
                            showNotification('Content decrypted successfully!', 'success');
                        } else {
                            showNotification('Invalid QR code format', 'error');
                        }
                    } catch (parseError) {
                        // If it's not JSON, treat it as plain content_id
                        try {
                            const result = await decodeContent(code.data);
                            displayDecryptedContent(result);
                            showNotification('Content decrypted successfully!', 'success');
                        } catch (error) {
                            showNotification(error.message, 'error');
                        }
                    }
                } else {
                    showNotification('No QR code found in the image. Please ensure the image contains a clear QR code.', 'error');
                }
            };
            img.onerror = function() {
                showNotification('Failed to load image', 'error');
            };
            img.src = e.target.result;
        };
        
        reader.onerror = function() {
            showNotification('Failed to read file', 'error');
        };
        
        reader.readAsDataURL(file);
        
    } catch (error) {
        console.error('QR decode error:', error);
        showError('Failed to process QR code image');
    }
}

function displayDecryptedContent(result) {
    const resultCard = document.getElementById('scanResultCard');
    const resultDiv = document.getElementById('scanResult');
    
    if (!resultCard || !resultDiv) return;
    
    let contentHtml = '';
    
    // Get content type from metadata
    const contentType = result.metadata?.type || result.content_type;
    const senderName = result.sender_name || result.sender_id || 'Unknown';
    const encryptionLevel = result.metadata?.encryption_name || result.encryption_name || 'Unknown';
    
    if (contentType === 'text') {
        const content = result.decrypted_content || result.content || result.text;
        
        if (content) {
            // Show decrypted text content
            contentHtml = `
                <div class="encryption-info-display">
                    <div class="encryption-badge">
                        <i class="fas fa-shield-alt"></i> ${encryptionLevel}
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label"><strong>From:</strong> ${senderName}</label>
                    <label class="form-label"><strong>Content Type:</strong> Text Message</label>
                    <label class="form-label"><strong>Created:</strong> ${result.created_at ? new Date(result.created_at).toLocaleString() : 'N/A'}</label>
                </div>
                <div class="form-group">
                    <label class="form-label"><strong>Message:</strong></label>
                    <textarea class="form-textarea" readonly style="min-height: 150px; background: var(--card-bg); color: var(--text-primary);">${content}</textarea>
                </div>
                <div class="success-message">
                    <i class="fas fa-check-circle"></i> Content decrypted successfully!
                </div>
            `;
        } else {
            // Show encrypted state
            contentHtml = `
                <div class="encryption-info-display">
                    <div class="encryption-badge">
                        <i class="fas fa-shield-alt"></i> ${encryptionLevel}
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label"><strong>From:</strong> ${senderName}</label>
                    <label class="form-label"><strong>Content Type:</strong> Text Message</label>
                    <label class="form-label"><strong>Status:</strong> Encrypted</label>
                </div>
                <div class="error-message">
                    <p><i class="fas fa-lock"></i> Content is encrypted.</p>
                    <p style="font-size: 0.9rem; margin-top: 0.5rem;">Full decryption requires implementing client-side RSA decryption with your private key.</p>
                </div>
                <div style="margin-top: 1rem;">
                    <label class="form-label"><strong>Encrypted Data Preview:</strong></label>
                    <textarea class="form-textarea" readonly style="min-height: 100px; font-family: monospace; font-size: 0.85rem;">${result.encrypted_data?.substring(0, 200)}...</textarea>
                </div>
            `;
        }
    } else if (contentType === 'file') {
        const isImage = result.metadata?.content_type?.startsWith('image/');
        const isVideo = result.metadata?.content_type?.startsWith('video/');
        const isAudio = result.metadata?.content_type?.startsWith('audio/');
        
        contentHtml = `
            <div class="encryption-info-display">
                <div class="encryption-badge">
                    <i class="fas fa-shield-alt"></i> ${encryptionLevel}
                </div>
            </div>
            <div class="form-group">
                <label class="form-label"><strong>From:</strong> ${senderName}</label>
                <label class="form-label"><strong>Content Type:</strong> ${isImage ? 'Image' : isVideo ? 'Video' : isAudio ? 'Audio' : 'File'}</label>
                <label class="form-label"><strong>Filename:</strong> ${result.metadata?.filename || 'file'}</label>
                <label class="form-label"><strong>Size:</strong> ${formatFileSize(result.metadata?.size || 0)}</label>
                <label class="form-label"><strong>Created:</strong> ${result.created_at ? new Date(result.created_at).toLocaleString() : 'N/A'}</label>
            </div>
        `;
        
        // If decrypted_content is available and it's media, show view button
        if (result.decrypted_content && (isImage || isVideo || isAudio)) {
            const contentId = `media-${Date.now()}`;
            // decrypted_content is already base64 for files
            const base64Data = result.decrypted_content;
            contentHtml += `
                <div class="form-group">
                    <button onclick="viewMediaInCard('${contentId}', '${result.metadata.content_type}', '${base64Data}', '${result.metadata.filename}', '${isImage ? 'image' : isVideo ? 'video' : 'audio'}')" class="btn btn-primary" style="width: 100%;">
                        <i class="fas fa-eye"></i> View ${isImage ? 'Image' : isVideo ? 'Video' : isAudio ? 'Audio' : 'Content'}
                    </button>
                    <div id="${contentId}" class="media-card-view" style="display: none; margin-top: 1rem; padding: 1rem; background: var(--card-bg); border-radius: 8px; text-align: center;"></div>
                </div>
                <div class="success-message">
                    <i class="fas fa-shield-check"></i> Content decrypted successfully! Click "View" to see it.
                </div>
                <p style="color: var(--text-muted); margin-top: 1rem; text-align: center;">
                    <i class="fas fa-info-circle"></i> To share this content, download the QR code above instead.
                </p>
            `;
        } else {
            contentHtml += `
                <div class="success-message">
                    <p><i class="fas fa-file"></i> File information retrieved successfully!</p>
                </div>
            `;
        }
    } else {
        contentHtml = `
            <div class="form-group">
                <label class="form-label"><strong>From:</strong> ${senderName}</label>
                <label class="form-label"><strong>Content Type:</strong> ${contentType || 'Unknown'}</label>
            </div>
            <div class="success-message">
                <p><strong>Status:</strong> Retrieved Successfully</p>
            </div>
        `;
    }
    
    resultDiv.innerHTML = contentHtml;
    resultCard.classList.remove('hidden');
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

window.downloadDecryptedFile = async function(contentId) {
    try {
        window.open(`${API_BASE_URL}/content/download/${contentId}`, '_blank');
    } catch (error) {
        showError('Failed to download file');
    }
};

function simulateQRScan(resultDiv) {
    const mockResult = {
        type: 'text',
        content: 'This is a simulated QR scan result',
        sender: 'Demo User'
    };
    
    if (resultDiv) {
        resultDiv.innerHTML = `
            <h3>Scan Result:</h3>
            <p><strong>From:</strong> ${mockResult.sender}</p>
            <p><strong>Content:</strong> ${mockResult.content}</p>
            <button onclick="saveScanResult('${mockResult.content}')" class="btn btn-success">
                Save Content
            </button>
        `;
        resultDiv.style.display = 'block';
    }
}

window.saveScanResult = function(content) {
    showSuccess('Content saved successfully!');
};

// Setup content sharing listeners
document.addEventListener('DOMContentLoaded', () => {
    const shareTextBtn = document.getElementById('shareTextBtn');
    if (shareTextBtn) {
        shareTextBtn.addEventListener('click', async () => {
            const text = document.getElementById('shareTextInput').value;
            const receiverId = document.getElementById('shareReceiver').value || null;
            const encryptionLevel = document.getElementById('textEncryptionLevel').value || 'standard';
            
            if (!text.trim()) {
                showError('Please enter text to share');
                return;
            }
            
            try {
                const result = await shareText(text, receiverId, null, encryptionLevel);
                generateQRCode(result.qr_code);
                showSuccess(`Text shared with ${result.encryption_name} encryption!`);
                // Clear the input
                document.getElementById('shareTextInput').value = '';
            } catch (error) {
                showError(error.message);
            }
        });
    }
    
    const uploadFileBtn = document.getElementById('uploadFileBtn');
    if (uploadFileBtn) {
        uploadFileBtn.addEventListener('click', async () => {
            const fileInput = document.getElementById('fileInput');
            const receiverId = document.getElementById('fileReceiver').value || null;
            const encryptionLevel = document.getElementById('fileEncryptionLevel').value || 'standard';
            
            if (!fileInput.files[0]) {
                showError('Please select a file');
                return;
            }
            
            try {
                const result = await shareFile(fileInput.files[0], receiverId, null, encryptionLevel);
                generateQRCode(result.qr_code);
                showSuccess(`File shared with ${result.encryption_name} encryption!`);
                // Clear the input
                fileInput.value = '';
            } catch (error) {
                showError(error.message);
            }
        });
    }
    
    const decodeQrImageBtn = document.getElementById('decodeQrImageBtn');
    if (decodeQrImageBtn) {
        decodeQrImageBtn.addEventListener('click', async () => {
            const qrImageInput = document.getElementById('qrImageInput');
            
            if (!qrImageInput.files[0]) {
                showError('Please select a QR code image');
                return;
            }
            
            try {
                await decodeQRImage(qrImageInput.files[0]);
            } catch (error) {
                showError(error.message);
            }
        });
    }
    
    // Populate receiver dropdowns with friends
    updateReceiverDropdowns();
});

// Update receiver dropdown options
function updateReceiverDropdowns() {
    const textReceiver = document.getElementById('shareReceiver');
    const fileReceiver = document.getElementById('fileReceiver');
    
    const dropdowns = [textReceiver, fileReceiver].filter(el => el);
    
    if (state.friends && state.friends.length > 0) {
        dropdowns.forEach(select => {
            // Clear existing options except the first (Public)
            while (select.options.length > 1) {
                select.remove(1);
            }
            
            // Add friend options
            state.friends.forEach(friend => {
                const option = document.createElement('option');
                option.value = friend.friend_id;
                option.textContent = friend.username;
                select.appendChild(option);
            });
            
            // Check if there's a pre-selected friend
            const selectedFriendId = localStorage.getItem('selectedFriendId');
            if (selectedFriendId) {
                select.value = selectedFriendId;
            }
        });
    }
}

// Make function globally available
window.updateReceiverDropdowns = updateReceiverDropdowns;

// View media in card
function viewMediaInCard(containerId, contentType, base64Data, filename, mediaType) {
    const container = document.getElementById(containerId);
    
    if (container.style.display === 'none' || container.style.display === '') {
        let mediaHtml = '';
        
        if (mediaType === 'image') {
            mediaHtml = `
                <img src="data:${contentType};base64,${base64Data}" 
                     alt="${filename}" 
                     style="max-width: 100%; max-height: 600px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); cursor: zoom-in;"
                     onclick="this.style.maxHeight = this.style.maxHeight === '600px' ? 'none' : '600px';">
                <p style="margin-top: 0.5rem; color: var(--text-muted); font-size: 0.9rem;">
                    <i class="fas fa-info-circle"></i> Click image to toggle full size
                </p>
            `;
        } else if (mediaType === 'video') {
            mediaHtml = `
                <video controls style="max-width: 100%; max-height: 600px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                    <source src="data:${contentType};base64,${base64Data}" type="${contentType}">
                    Your browser does not support the video tag.
                </video>
            `;
        } else if (mediaType === 'audio') {
            mediaHtml = `
                <div style="padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px;">
                    <i class="fas fa-music" style="font-size: 3rem; color: white; margin-bottom: 1rem;"></i>
                    <audio controls style="width: 100%;">
                        <source src="data:${contentType};base64,${base64Data}" type="${contentType}">
                        Your browser does not support the audio tag.
                    </audio>
                    <p style="margin-top: 1rem; color: white; font-size: 0.9rem;">${filename}</p>
                </div>
            `;
        }
        
        container.innerHTML = mediaHtml;
        container.style.display = 'block';
        
        // Change button text
        const button = container.previousElementSibling;
        if (button && button.tagName === 'BUTTON') {
            button.innerHTML = `<i class="fas fa-eye-slash"></i> Hide ${mediaType.charAt(0).toUpperCase() + mediaType.slice(1)}`;
        }
    } else {
        container.style.display = 'none';
        container.innerHTML = '';
        
        // Change button text back
        const button = container.previousElementSibling;
        if (button && button.tagName === 'BUTTON') {
            button.innerHTML = `<i class="fas fa-eye"></i> View ${mediaType.charAt(0).toUpperCase() + mediaType.slice(1)}`;
        }
    }
}

window.viewMediaInCard = viewMediaInCard;