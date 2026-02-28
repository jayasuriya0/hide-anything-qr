// QR Code Functions

// Content Sharing
async function shareText(text, receiverId = null, expiresIn = null, encryptionLevel = 'standard', password = null, maxViews = null) {
    try {
        const payload = {
            text,
            receiver_id: receiverId,
            encryption_level: encryptionLevel
        };
        
        // Add optional parameters only if they have values
        if (expiresIn) payload.expires_in = expiresIn;
        if (password) payload.password = password;
        if (maxViews) payload.max_views = parseInt(maxViews);
        
        const response = await apiRequest('/content/share/text', {
            method: 'POST',
            body: JSON.stringify(payload)
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

async function shareFile(file, receiverId = null, expiresIn = null, encryptionLevel = 'standard', password = null, maxViews = null) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('encryption_level', encryptionLevel);
        
        // Add optional parameters only if they have values
        if (receiverId) formData.append('receiver_id', receiverId);
        if (expiresIn) formData.append('expires_in', expiresIn);
        if (password) formData.append('password', password);
        if (maxViews) formData.append('max_views', maxViews);
        
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

async function decodeContent(qrData, password = null) {
    try {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Add password header if provided
        if (password) {
            headers['X-Content-Password'] = password;
        }
        
        const response = await apiRequest('/content/decode', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ qr_data: qrData })
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            const errorData = await response.json();
            
            // Handle password required error
            if (response.status === 401 && errorData.requires_password) {
                // Show password input card
                return await showPasswordPromptCard(qrData);
            }
            
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

// Show password prompt card
function showPasswordPromptCard(qrData) {
    return new Promise((resolve, reject) => {
        // Create modal overlay
        const modalOverlay = document.createElement('div');
        modalOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            backdrop-filter: blur(4px);
        `;
        
        // Create password card
        const card = document.createElement('div');
        card.style.cssText = `
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8a 100%);
            border-radius: 16px;
            padding: 2rem;
            max-width: 450px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            animation: slideIn 0.3s ease-out;
        `;
        
        card.innerHTML = `
            <style>
                @keyframes slideIn {
                    from {
                        transform: translateY(-20px);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
            </style>
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; background: rgba(255, 255, 255, 0.1); border-radius: 50%; margin-bottom: 1rem;">
                    <i class="fas fa-lock" style="font-size: 28px; color: #4a9eff;"></i>
                </div>
                <h2 style="margin: 0; color: #ffffff; font-size: 1.5rem; font-weight: 600;">Password Protected</h2>
                <p style="margin: 0.5rem 0 0; color: #b8c5d6; font-size: 0.95rem;">This content requires a password to view</p>
            </div>
            
            <div style="margin-bottom: 1.5rem;">
                <label style="display: block; margin-bottom: 0.5rem; color: #e0e6ed; font-size: 0.9rem; font-weight: 500;">
                    <i class="fas fa-key"></i> Enter Password
                </label>
                <input 
                    type="password" 
                    id="passwordInput" 
                    placeholder="Enter password..."
                    style="
                        width: 100%;
                        padding: 0.875rem 1rem;
                        background: rgba(255, 255, 255, 0.08);
                        border: 1px solid rgba(255, 255, 255, 0.15);
                        border-radius: 8px;
                        color: #ffffff;
                        font-size: 1rem;
                        outline: none;
                        transition: all 0.3s ease;
                        box-sizing: border-box;
                    "
                    onkeypress="if(event.key === 'Enter') document.getElementById('submitPasswordBtn').click();"
                />
            </div>
            
            <div style="display: flex; gap: 0.75rem;">
                <button 
                    id="cancelPasswordBtn"
                    style="
                        flex: 1;
                        padding: 0.875rem 1.5rem;
                        background: rgba(255, 255, 255, 0.1);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        border-radius: 8px;
                        color: #ffffff;
                        font-size: 1rem;
                        font-weight: 500;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    "
                    onmouseover="this.style.background='rgba(255, 255, 255, 0.15)'"
                    onmouseout="this.style.background='rgba(255, 255, 255, 0.1)'"
                >
                    <i class="fas fa-times"></i> Cancel
                </button>
                <button 
                    id="submitPasswordBtn"
                    style="
                        flex: 1;
                        padding: 0.875rem 1.5rem;
                        background: linear-gradient(135deg, #4a9eff 0%, #357abd 100%);
                        border: none;
                        border-radius: 8px;
                        color: #ffffff;
                        font-size: 1rem;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        box-shadow: 0 4px 12px rgba(74, 158, 255, 0.3);
                    "
                    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(74, 158, 255, 0.4)'"
                    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(74, 158, 255, 0.3)'"
                >
                    <i class="fas fa-unlock"></i> Unlock
                </button>
            </div>
        `;
        
        modalOverlay.appendChild(card);
        document.body.appendChild(modalOverlay);
        
        // Focus on password input
        setTimeout(() => {
            document.getElementById('passwordInput').focus();
        }, 100);
        
        // Handle submit
        document.getElementById('submitPasswordBtn').onclick = async () => {
            const password = document.getElementById('passwordInput').value;
            if (!password) {
                document.getElementById('passwordInput').style.borderColor = '#ff4444';
                document.getElementById('passwordInput').placeholder = 'Password is required';
                return;
            }
            
            // Show loading
            document.getElementById('submitPasswordBtn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Unlocking...';
            document.getElementById('submitPasswordBtn').disabled = true;
            
            try {
                const result = await decodeContent(qrData, password);
                document.body.removeChild(modalOverlay);
                resolve(result);
            } catch (error) {
                document.getElementById('passwordInput').style.borderColor = '#ff4444';
                document.getElementById('passwordInput').value = '';
                document.getElementById('passwordInput').placeholder = 'Incorrect password. Try again...';
                document.getElementById('submitPasswordBtn').innerHTML = '<i class="fas fa-unlock"></i> Unlock';
                document.getElementById('submitPasswordBtn').disabled = false;
                document.getElementById('passwordInput').focus();
            }
        };
        
        // Handle cancel
        document.getElementById('cancelPasswordBtn').onclick = () => {
            document.body.removeChild(modalOverlay);
            reject(new Error('Password entry cancelled'));
        };
        
        // Close on overlay click
        modalOverlay.onclick = (e) => {
            if (e.target === modalOverlay) {
                document.body.removeChild(modalOverlay);
                reject(new Error('Password entry cancelled'));
            }
        };
    });
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
let scanningInterval = null;
let isScanning = false;
let lastScannedCode = null;
let lastScanTime = 0;
let scanFrameCount = 0;
let scanAnimationFrame = null;

async function startQRScanner() {
    const video = document.getElementById('scannerVideo');
    const overlay = document.getElementById('scannerOverlay');
    const startBtn = document.getElementById('startCameraBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    const indicator = document.getElementById('scanningIndicator');
    const instructions = document.getElementById('scannerInstructions');
    
    if (!video) return;
    
    try {
        // Request camera permission with better constraints
        const constraints = {
            video: {
                facingMode: { ideal: 'environment' },
                width: { ideal: 1920, max: 1920 },
                height: { ideal: 1080, max: 1080 }
            }
        };
        
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        
        currentStream = stream;
        video.srcObject = stream;
        video.classList.remove('hidden');
        await video.play();
        
        if (startBtn) startBtn.classList.add('hidden');
        if (stopBtn) stopBtn.classList.remove('hidden');
        if (indicator) {
            indicator.classList.remove('hidden');
            indicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning for QR codes... Hold steady';
        }
        if (instructions) {
            instructions.classList.remove('hidden');
        }
        
        // Wait for video to be ready
        video.onloadedmetadata = () => {
            console.log('Camera ready, video size:', video.videoWidth, 'x', video.videoHeight);
            console.log('Starting continuous QR scan...');
            
            // Setup overlay canvas
            if (overlay) {
                overlay.width = video.offsetWidth;
                overlay.height = video.offsetHeight;
                overlay.classList.remove('hidden');
            }
            
            isScanning = true;
            scanFrameCount = 0;
            console.log('Starting QR scan loop...');
            scanQRCode();
            showSuccess('Camera started. Point at a QR code to scan.');
        };
        
    } catch (error) {
        console.error('Camera access failed:', error);
        let errorMessage = 'Could not access camera. ';
        
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            errorMessage += 'Please allow camera access in your browser settings.';
        } else if (error.name === 'NotFoundError') {
            errorMessage += 'No camera found on this device.';
        } else if (error.name === 'NotReadableError') {
            errorMessage += 'Camera is already in use by another application.';
        } else {
            errorMessage += 'Please check your camera permissions and try again.';
        }
        
        showError(errorMessage);
    }
}

// Make function globally available
window.startQRScanner = startQRScanner;

function scanQRCode() {
    const video = document.getElementById('scannerVideo');
    const overlay = document.getElementById('scannerOverlay');
    const indicator = document.getElementById('scanningIndicator');
    
    if (!isScanning || !video || video.readyState !== video.HAVE_ENOUGH_DATA) {
        if (isScanning) {
            scanAnimationFrame = requestAnimationFrame(scanQRCode);
        }
        return;
    }
    
    // Increment frame counter and log every 60 frames (~2 seconds at 30fps)
    scanFrameCount++;
    if (scanFrameCount % 60 === 0) {
        console.log(`Scanning... ${scanFrameCount} frames processed, video: ${video.videoWidth}x${video.videoHeight}`);
    }
    
    // Draw scanning indicator on overlay
    if (overlay) {
        const overlayCtx = overlay.getContext('2d');
        overlayCtx.clearRect(0, 0, overlay.width, overlay.height);
        
        // Draw corner brackets
        const centerX = overlay.width / 2;
        const centerY = overlay.height / 2;
        const size = Math.min(overlay.width, overlay.height) * 0.6;
        const cornerLength = 30;
        
        overlayCtx.strokeStyle = '#4CAF50';
        overlayCtx.lineWidth = 4;
        overlayCtx.lineCap = 'round';
        
        // Top-left corner
        overlayCtx.beginPath();
        overlayCtx.moveTo(centerX - size/2, centerY - size/2 + cornerLength);
        overlayCtx.lineTo(centerX - size/2, centerY - size/2);
        overlayCtx.lineTo(centerX - size/2 + cornerLength, centerY - size/2);
        overlayCtx.stroke();
        
        // Top-right corner
        overlayCtx.beginPath();
        overlayCtx.moveTo(centerX + size/2 - cornerLength, centerY - size/2);
        overlayCtx.lineTo(centerX + size/2, centerY - size/2);
        overlayCtx.lineTo(centerX + size/2, centerY - size/2 + cornerLength);
        overlayCtx.stroke();
        
        // Bottom-left corner
        overlayCtx.beginPath();
        overlayCtx.moveTo(centerX - size/2, centerY + size/2 - cornerLength);
        overlayCtx.lineTo(centerX - size/2, centerY + size/2);
        overlayCtx.lineTo(centerX - size/2 + cornerLength, centerY + size/2);
        overlayCtx.stroke();
        
        // Bottom-right corner
        overlayCtx.beginPath();
        overlayCtx.moveTo(centerX + size/2 - cornerLength, centerY + size/2);
        overlayCtx.lineTo(centerX + size/2, centerY + size/2);
        overlayCtx.lineTo(centerX + size/2, centerY + size/2 - cornerLength);
        overlayCtx.stroke();
    }
    
    // Create a canvas to capture video frame
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    if (canvas.width > 0 && canvas.height > 0) {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
        
        // Try to detect QR code using jsQR with better options
        if (typeof jsQR !== 'undefined') {
            const code = jsQR(imageData.data, imageData.width, imageData.height, {
                inversionAttempts: "attemptBoth", // Try both normal and inverted
            });
            
            if (code && code.data) {
                console.log('✓ QR code detected! Length:', code.data.length, 'Preview:', code.data.substring(0, 80));
                
                // Draw detection box on overlay
                if (overlay && code.location) {
                    const overlayCtx = overlay.getContext('2d');
                    overlayCtx.clearRect(0, 0, overlay.width, overlay.height);
                    
                    // Calculate scale
                    const scaleX = overlay.width / canvas.width;
                    const scaleY = overlay.height / canvas.height;
                    
                    overlayCtx.strokeStyle = '#00FF00';
                    overlayCtx.lineWidth = 3;
                    overlayCtx.beginPath();
                    overlayCtx.moveTo(code.location.topLeftCorner.x * scaleX, code.location.topLeftCorner.y * scaleY);
                    overlayCtx.lineTo(code.location.topRightCorner.x * scaleX, code.location.topRightCorner.y * scaleY);
                    overlayCtx.lineTo(code.location.bottomRightCorner.x * scaleX, code.location.bottomRightCorner.y * scaleY);
                    overlayCtx.lineTo(code.location.bottomLeftCorner.x * scaleX, code.location.bottomLeftCorner.y * scaleY);
                    overlayCtx.closePath();
                    overlayCtx.stroke();
                }
                
                const currentTime = Date.now();
                // Avoid scanning the same code multiple times (debounce 1 second)
                if (code.data !== lastScannedCode || currentTime - lastScanTime > 1000) {
                    lastScannedCode = code.data;
                    lastScanTime = currentTime;
                    if (indicator) {
                        indicator.innerHTML = '<i class="fas fa-check-circle"></i> QR Code Found! Decoding...';
                    }
                    handleScannedQR(code.data);
                    return; // Stop scanning after successful scan
                }
            }
        } else {
            console.error('jsQR library not loaded!');
            showError('QR scanner library not loaded. Please refresh the page.');
            stopQRScanner();
            return;
        }
    }
    
    // Continue scanning
    if (isScanning) {
        scanAnimationFrame = requestAnimationFrame(scanQRCode);
    }
}

async function handleScannedQR(qrData) {
    try {
        // Stop scanning temporarily
        isScanning = false;
        
        // Provide haptic feedback if available
        if (navigator.vibrate) {
            navigator.vibrate(200);
        }
        
        console.log('QR Code raw data:', qrData);
        showSuccess('QR Code detected! Decoding...');
        
        // Decode the secure QR data to validate format
        const decodedData = decodeSecureQRData(qrData);
        console.log('Decoded QR data:', decodedData);
        
        if (decodedData && decodedData.content_id) {
            // Pass the RAW qrData string to backend for proper decoding
            console.log('Valid content QR detected, sending to backend...');
            const result = await decodeContent(qrData);
            displayDecryptedContent(result);
            
            // Stop camera after successful scan
            stopQRScanner();
            
            showSuccess('Content decrypted successfully!');
        } else {
            // Not a valid app QR code, keep scanning
            console.log('Not a valid HideAnything.QR code, continuing to scan...');
            // Resume scanning immediately without showing error
            isScanning = true;
            scanQRCode();
        }
    } catch (error) {
        console.error('QR scan error:', error);
        
        // Only show error if it's a permission or critical error
        // Don't show errors for invalid QR codes - just keep scanning
        if (error.message && error.message.includes('permission')) {
            showError(error.message);
            stopQRScanner();
        } else {
            // For other errors, just log and continue scanning
            console.log('Continuing to scan...');
            setTimeout(() => {
                isScanning = true;
                scanQRCode();
            }, 1000);
        }
    }
}

window.stopQRScanner = function() {
    console.log('Stopping camera scanner...');
    const video = document.getElementById('scannerVideo');
    const overlay = document.getElementById('scannerOverlay');
    const startBtn = document.getElementById('startCameraBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    const indicator = document.getElementById('scanningIndicator');
    const instructions = document.getElementById('scannerInstructions');
    
    // Stop scanning loop
    isScanning = false;
    lastScannedCode = null;
    scanFrameCount = 0;
    
    // Cancel any pending animation frame
    if (scanAnimationFrame) {
        cancelAnimationFrame(scanAnimationFrame);
        scanAnimationFrame = null;
    }
    
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
    
    if (video) {
        video.srcObject = null;
        video.classList.add('hidden');
    }
    
    if (overlay) {
        const overlayCtx = overlay.getContext('2d');
        overlayCtx.clearRect(0, 0, overlay.width, overlay.height);
        overlay.classList.add('hidden');
    }
    
    if (startBtn) startBtn.classList.remove('hidden');
    if (stopBtn) stopBtn.classList.add('hidden');
    if (indicator) indicator.classList.add('hidden');
    if (instructions) instructions.classList.add('hidden');
};

// Decode secure QR data
function decodeSecureQRData(rawData) {
    try {
        let encoded = null;
        
        // Check if it's our secure format (new generic scheme)
        if (rawData.startsWith('qrs://v?d=')) {
            encoded = rawData.replace('qrs://v?d=', '');
        } 
        // Backward compatibility with old format
        else if (rawData.startsWith('hideanythingqr://decode?data=')) {
            encoded = rawData.replace('hideanythingqr://decode?data=', '');
        }
        
        // If encoded format found, decode it
        if (encoded) {
            const jsonStr = atob(encoded);
            return JSON.parse(jsonStr);
        } else {
            // Try to parse as JSON (backward compatibility)
            return JSON.parse(rawData);
        }
    } catch (e) {
        // If all parsing fails, return as-is
        return rawData;
    }
}

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
                        console.log('QR detected from image:', code.data);
                        // Decode secure QR data to validate format
                        const qrData = decodeSecureQRData(code.data);
                        console.log('Decoded image QR data:', qrData);
                        
                        if (qrData && qrData.content_id) {
                            // Pass the RAW code.data string to backend
                            const result = await decodeContent(code.data);
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
            // Show encrypted state with error details
            const errorMessage = result.decryption_error || 'Full decryption requires implementing client-side RSA decryption with your private key.';
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
                    <p><i class="fas fa-lock"></i> Failed to decrypt content.</p>
                    <p style="font-size: 0.9rem; margin-top: 0.5rem; color: var(--danger-color);">${errorMessage}</p>
                    <p style="font-size: 0.85rem; margin-top: 0.5rem; color: var(--text-muted);">
                        <strong>Possible reasons:</strong><br>
                        • You are not the intended recipient<br>
                        • Content was shared with a specific person<br>
                        • Your encryption keys are not available
                    </p>
                </div>
                ${result.encrypted_data ? `
                <div style="margin-top: 1rem;">
                    <label class="form-label"><strong>Encrypted Data Preview:</strong></label>
                    <textarea class="form-textarea" readonly style="min-height: 100px; font-family: monospace; font-size: 0.85rem;">${result.encrypted_data}...</textarea>
                </div>
                ` : ''}
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
        
        // If decrypted_content is available, show view/download button
        if (result.decrypted_content) {
            const contentId = `media-${Date.now()}`;
            // decrypted_content is already base64 for files
            const base64Data = result.decrypted_content;
            
            if (isImage || isVideo || isAudio) {
                // For media files, show inline viewer
                contentHtml += `
                    <div class="form-group">
                        <button onclick="viewMediaInCard('${contentId}', '${result.metadata.content_type}', '${base64Data}', '${result.metadata.filename}', '${isImage ? 'image' : isVideo ? 'video' : 'audio'}')" class="btn btn-primary" style="width: 100%;">
                            <i class="fas fa-eye"></i> View ${isImage ? 'Image' : isVideo ? 'Video' : isAudio ? 'Audio' : 'Content'}
                        </button>
                        <div id="${contentId}" class="media-card-view" style="display: none; margin-top: 1rem; padding: 1rem; background: var(--card-bg); border-radius: 8px; text-align: center;"></div>
                    </div>
                `;
            } else {
                // For other files (PDFs, documents, etc.), show download button
                contentHtml += `
                    <div class="form-group">
                        <button onclick="downloadDecryptedFileData('${base64Data}', '${result.metadata.filename}', '${result.metadata.content_type}')" class="btn btn-primary" style="width: 100%;">
                            <i class="fas fa-download"></i> Download File
                        </button>
                    </div>
                `;
            }
            
            contentHtml += `
                <div class="success-message">
                    <i class="fas fa-shield-check"></i> Content decrypted successfully!
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

window.downloadDecryptedFileData = function(base64Data, filename, contentType) {
    try {
        // Convert base64 to blob
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: contentType });
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showSuccess(`Downloading ${filename}...`);
    } catch (error) {
        console.error('Download error:', error);
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
            
            // Get security options
            const password = document.getElementById('textPassword').value || null;
            const expiresIn = document.getElementById('textExpiry').value || null;
            const maxViews = document.getElementById('textMaxViews').value || null;
            
            if (!text.trim()) {
                showError('Please enter text to share');
                return;
            }
            
            try {
                const result = await shareText(text, receiverId, expiresIn, encryptionLevel, password, maxViews);
                generateQRCode(result.qr_code);
                
                // Build success message with security info
                let successMsg = `Text shared with ${result.encryption_name} encryption!`;
                if (password) successMsg += ' 🔒 Password protected';
                if (expiresIn) successMsg += ' ⏱️ With expiry';
                if (maxViews) successMsg += ` 👁️ Max ${maxViews} views`;
                
                showSuccess(successMsg);
                
                // Clear the inputs
                document.getElementById('shareTextInput').value = '';
                document.getElementById('textPassword').value = '';
                document.getElementById('textExpiry').value = '';
                document.getElementById('textMaxViews').value = '';
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
            
            // Get security options
            const password = document.getElementById('filePassword').value || null;
            const expiresIn = document.getElementById('fileExpiry').value || null;
            const maxViews = document.getElementById('fileMaxViews').value || null;
            
            if (!fileInput.files[0]) {
                showError('Please select a file');
                return;
            }
            
            try {
                const result = await shareFile(fileInput.files[0], receiverId, expiresIn, encryptionLevel, password, maxViews);
                generateQRCode(result.qr_code);
                
                // Build success message with security info
                let successMsg = `File shared with ${result.encryption_name} encryption!`;
                if (password) successMsg += ' 🔒 Password protected';
                if (expiresIn) successMsg += ' ⏱️ With expiry';
                if (maxViews) successMsg += ` 👁️ Max ${maxViews} views`;
                
                showSuccess(successMsg);
                
                // Clear the inputs
                fileInput.value = '';
                document.getElementById('filePassword').value = '';
                document.getElementById('fileExpiry').value = '';
                document.getElementById('fileMaxViews').value = '';
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
