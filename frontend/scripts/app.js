// Configuration - Automatically detect the correct server URL
const getServerUrl = () => {
    // If using dev tunnels or already on the right port, use current origin
    if (window.location.hostname.includes('devtunnels') || 
        window.location.port === '5000' || 
        window.location.port === '') {
        return window.location.origin;
    }
    // For local development with different ports - use HTTP (not HTTPS)
    const protocol = 'http:';
    const host = window.location.hostname;
    return `${protocol}//${host}:5000`;
};

const API_BASE_URL = `${getServerUrl()}/api`;
const SOCKET_URL = getServerUrl();

console.log('Current location:', window.location.href);
console.log('API Base URL:', API_BASE_URL);
console.log('Socket URL:', SOCKET_URL);

// State management (make it globally accessible)
window.state = {
    user: null,
    token: localStorage.getItem('access_token') || localStorage.getItem('token'),
    refreshToken: localStorage.getItem('refresh_token') || localStorage.getItem('refreshToken'),
    friends: [],
    notifications: [],
    socket: null
};
const state = window.state;

// API Helper Functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers = {
        ...options.headers
    };
    
    // Only add Content-Type for non-FormData requests
    if (!options.skipContentType && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }
    
    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }
    
    try {
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        // Handle token refresh if 401
        if (response.status === 401 && endpoint !== '/auth/refresh') {
            const refreshed = await refreshToken();
            if (refreshed) {
                // Retry the original request
                headers['Authorization'] = `Bearer ${state.token}`;
                return fetch(url, { ...options, headers });
            } else {
                logout();
                throw new Error('Session expired');
            }
        }
        
        return response;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

async function refreshToken() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${state.refreshToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            state.token = data.access_token;
            localStorage.setItem('access_token', state.token);
            localStorage.setItem('token', state.token);
            return true;
        }
    } catch (error) {
        console.error('Token refresh failed:', error);
    }
    return false;
}

// WebSocket Connection
function connectWebSocket() {
    if (state.socket) {
        state.socket.disconnect();
    }
    
    const socket = io(SOCKET_URL, {
        auth: {
            token: state.token
        }
    });
    
    socket.on('connect', () => {
        console.log('Connected to WebSocket');
        const userId = state.user.user_id || state.user.id || state.user._id;
        if (userId) {
            socket.emit('join_room', { user_id: userId });
        }
    });
    
    socket.on('new_content', (data) => {
        showNotification(`New content from ${data.from}`);
        updateNotifications();
    });
    
    socket.on('friend_request', (data) => {
        showNotification(`Friend request from ${data.from_username}`);
        updateFriendRequests();
    });
    
    socket.on('friend_request_accepted', (data) => {
        showNotification('Friend request accepted!');
        updateFriendsList();
    });
    
    state.socket = socket;
}

// Initialize the application
async function initApp() {
    if (state.token) {
        try {
            await fetchUserData();
            showDashboard();
            setupEventListeners(); // Setup after dashboard is shown
            connectWebSocket();
            loadInitialData();
        } catch (error) {
            console.error('Failed to load user data:', error);
            showLogin();
            setupEventListeners(); // Setup for login page too
        }
    } else {
        showLogin();
        setupEventListeners(); // Setup for login page
    }
}

// Load initial data
async function loadInitialData() {
    if (!state.user) return;
    
    try {
        const friendsResponse = await apiRequest('/friends/list');
        if (friendsResponse.ok) {
            const data = await friendsResponse.json();
            state.friends = data.friends;
            updateFriendsList();
            
            // Update receiver dropdowns in QR section
            if (typeof updateReceiverDropdowns !== 'undefined') {
                updateReceiverDropdowns();
            }
        }
        
        // Load friend requests
        if (typeof updateFriendRequests !== 'undefined') {
            updateFriendRequests();
        }
        
        const notifResponse = await apiRequest('/notifications?limit=10&unread_only=true');
        if (notifResponse.ok) {
            const data = await notifResponse.json();
            state.notifications = data.notifications;
            updateNotifications();
        }
        
        // Initialize activity feed
        if (typeof initActivityFeed !== 'undefined') {
            initActivityFeed();
        }
        
        // Initialize notifications
        if (typeof initNotifications !== 'undefined') {
            initNotifications();
        }
        
        updateUserProfile();
        
    } catch (error) {
        console.error('Failed to load initial data:', error);
    }
}

// Page Navigation
function showLogin() {
    document.getElementById('authSection').classList.remove('hidden');
    document.getElementById('appContainer').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('authSection').classList.add('hidden');
    document.getElementById('appContainer').classList.remove('hidden');
}

// UI Helper Functions
function parseErrorMessage(message) {
    // Convert technical error messages to user-friendly ones
    const lowerMsg = message.toLowerCase();
    
    if (lowerMsg.includes('not a valid objectid') || lowerMsg.includes('24-character hex')) {
        return 'This QR code has been deactivated or is no longer available';
    }
    if (lowerMsg.includes('content not found')) {
        return 'QR code not found. It may have been deleted or deactivated';
    }
    if (lowerMsg.includes('unauthorized') || lowerMsg.includes('permission')) {
        return 'You don\'t have permission to access this content';
    }
    if (lowerMsg.includes('expired')) {
        return 'This QR code has expired';
    }
    if (lowerMsg.includes('inactive') || lowerMsg.includes('deactivated')) {
        return 'This QR code has been deactivated by the owner';
    }
    if (lowerMsg.includes('decrypt') || lowerMsg.includes('encryption')) {
        return 'Failed to decrypt content. Invalid encryption key';
    }
    if (lowerMsg.includes('network') || lowerMsg.includes('fetch')) {
        return 'Network error. Please check your connection';
    }
    if (lowerMsg.includes('session expired') || lowerMsg.includes('401')) {
        return 'Your session has expired. Please log in again';
    }
    
    // If message is too long or looks technical, show generic message
    if (message.length > 200 || message.includes('{') || message.includes('"')) {
        return 'An error occurred. Please try again';
    }
    
    return message;
}

function showNotification(message, type = 'info') {
    // Parse error messages to be user-friendly
    if (type === 'error') {
        message = parseErrorMessage(message);
    }
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Color scheme based on type
    let backgroundColor, borderColor, icon;
    switch(type) {
        case 'error':
            backgroundColor = '#ff4757';
            borderColor = '#ff6b81';
            icon = '❌';
            break;
        case 'success':
            backgroundColor = '#2ed573';
            borderColor = '#7bed9f';
            icon = '✅';
            break;
        case 'warning':
            backgroundColor = '#ffa502';
            borderColor = '#ffb142';
            icon = '⚠️';
            break;
        default:
            backgroundColor = '#5352ed';
            borderColor = '#7f7fff';
            icon = 'ℹ️';
    }
    
    notification.innerHTML = `
        <div style="padding-right: 30px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                <span style="font-size: 1.3rem;">${icon}</span>
                <strong style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;">${type}</strong>
            </div>
            <p style="margin: 0; font-size: 0.95rem; line-height: 1.5;">${message}</p>
        </div>
        <button onclick="this.parentElement.remove()" style="position: absolute; top: 8px; right: 8px; background: rgba(255,255,255,0.2); border: none; color: white; font-size: 20px; cursor: pointer; padding: 2px 8px; border-radius: 4px; font-weight: bold; line-height: 1;" onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">×</button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 90px;
        left: 50%;
        transform: translateX(-50%);
        background: ${backgroundColor};
        color: white;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid ${borderColor};
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        z-index: 999999;
        width: 450px;
        max-width: calc(100vw - 40px);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        box-sizing: border-box;
        opacity: 1;
    `;
    
    
    document.body.appendChild(notification);
    
    // Longer display time for errors and warnings
    const displayTime = (type === 'error' || type === 'warning') ? 10000 : 5000;
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s ease-out';
            setTimeout(() => notification.remove(), 500);
        }
    }, displayTime);
}

function showLoader(element) {
    element.innerHTML = '<div class="loader"></div>';
}

function showError(message, element = null) {
    if (element) {
        element.innerHTML = `<div class="error-message">${message}</div>`;
    } else {
        showNotification(message, 'error');
    }
}

function showSuccess(message, element = null) {
    if (element) {
        element.innerHTML = `<div class="success-message">${message}</div>`;
    } else {
        showNotification(message, 'success');
    }
}

// Section Navigation
window.showSection = function(sectionName) {
    try {
        console.log('showSection called with:', sectionName);
        
        // Hide all sections
        const sections = document.querySelectorAll('.content-section');
        console.log('Found sections:', sections.length);
        sections.forEach(section => section.classList.remove('active'));
        
        // Show selected section
        const targetSection = document.getElementById(sectionName + 'Section');
        console.log('Target section:', targetSection);
        if (targetSection) {
            targetSection.classList.add('active');
            console.log('Activated section:', sectionName + 'Section');
        } else {
            console.error('Section not found:', sectionName + 'Section');
        }
        
        // Update navigation active states
        const navLinks = document.querySelectorAll('.nav-link, .sidebar-link');
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.section === sectionName || link.getAttribute('data-section') === sectionName) {
                link.classList.add('active');
            }
        });
        
        // Load data for specific sections
        console.log('Checking section type:', sectionName);
        if (sectionName === 'profile') {
            console.log('Profile section');
            if (typeof initProfilePage !== 'undefined') {
                initProfilePage();
            }
        } else if (sectionName === 'friends') {
            console.log('Friends section');
            if (typeof updateFriendRequests !== 'undefined') {
                updateFriendRequests();
            }
            if (typeof updateReceiverDropdowns !== 'undefined') {
                updateReceiverDropdowns();
            }
        } else if (sectionName === 'shared') {
            // Load shared content
            console.log('Shared section - calling loadSharedContent');
            loadSharedContent();
        }
    } catch (error) {
        console.error('Error in showSection:', error);
    }
};

// Shared Content Functions
async function loadSharedContent() {
    console.log('=== loadSharedContent STARTED ===');
    try {
        console.log('Fetching shared content from API...');
        console.log('API_BASE_URL:', API_BASE_URL);
        console.log('Token:', state.token ? 'Present' : 'Missing');
        
        const response = await apiRequest('/content/my-shared', {
            method: 'GET'
        });
        
        console.log('Response received:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Shared content data:', data);
        console.log('Number of items:', data.shared_content ? data.shared_content.length : 0);
        
        if (data.shared_content) {
            originalSharedContent = data.shared_content; // Store for filtering
            displaySharedContent(data.shared_content);
        } else {
            console.warn('No shared_content in response');
            originalSharedContent = [];
            displaySharedContent([]);
        }
    } catch (error) {
        console.error('Error loading shared content:', error);
        const container = document.getElementById('sharedContentList');
        if (container) {
            container.innerHTML = `
                <div class="error-message" style="text-align: center; padding: 3rem;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #ef476f; margin-bottom: 1rem;"></i>
                    <p style="color: var(--text-color); margin-bottom: 0.5rem;">Failed to load shared content</p>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">${error.message}</p>
                </div>
            `;
        }
    }
}

// Make loadSharedContent globally accessible
window.loadSharedContent = loadSharedContent;

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
                            <span><strong>Shared with:</strong> ${content.receiver_name || 'Unknown'}</span>
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
                        <button onclick="deactivateSharedContent('${content.content_id}')" class="btn btn-danger btn-sm">
                            <i class="fas fa-ban"></i> Deactivate
                        </button>
                    ` : `
                        <button onclick="activateSharedContent('${content.content_id}')" class="btn btn-success btn-sm">
                            <i class="fas fa-check"></i> Activate
                        </button>
                    `}
                    <button onclick="viewContentQR('${content.content_id}')" class="btn btn-primary btn-sm">
                        <i class="fas fa-qrcode"></i> View QR
                    </button>
                    <button onclick="deleteSharedContent('${content.content_id}')" class="btn btn-danger btn-sm" style="margin-left: 0.5rem;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

window.deactivateSharedContent = async function(contentId) {
    if (!confirm('Are you sure you want to deactivate this QR code? No one will be able to decode it.')) {
        return;
    }
    
    try {
        const response = await apiRequest(`/content/deactivate/${contentId}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to deactivate');
        }
        
        showNotification('Content deactivated successfully', 'success');
        await loadSharedContent();
    } catch (error) {
        console.error('Error deactivating content:', error);
        showNotification(error.message || 'Failed to deactivate content', 'error');
    }
};

window.activateSharedContent = async function(contentId) {
    try {
        const response = await apiRequest(`/content/activate/${contentId}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to activate');
        }
        
        showNotification('Content activated successfully', 'success');
        await loadSharedContent();
    } catch (error) {
        console.error('Error activating content:', error);
        showNotification(error.message || 'Failed to activate content', 'error');
    }
};

window.viewContentQR = async function(contentId) {
    try {
        console.log('Viewing QR for content:', contentId);
        
        // Fetch content details to get QR code
        const response = await apiRequest(`/content/qr/${contentId}`, {
            method: 'GET'
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Display QR code in modal
            const modalQrImage = document.getElementById('modalQrCodeImage');
            if (modalQrImage && data.qr_code) {
                modalQrImage.innerHTML = '';
                const img = document.createElement('img');
                img.src = `data:image/png;base64,${data.qr_code}`;
                img.alt = 'QR Code';
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
                modalQrImage.appendChild(img);
                
                // Update modal title with encryption info
                const modalTitle = document.getElementById('modalQrCodeTitle');
                if (modalTitle) {
                    const statusText = data.is_active ? '🟢 Active' : '🔴 Inactive';
                    modalTitle.textContent = `${statusText} - ${data.encryption_name}`;
                }
                
                // Store for download
                window.currentQRData = data.qr_code;
                
                // Show the modal
                if (typeof showQRModal === 'function') {
                    showQRModal();
                }
            }
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to fetch QR code');
        }
        
    } catch (error) {
        console.error('Error viewing QR code:', error);
        showNotification('Failed to load QR code: ' + error.message, 'error');
    }
};

window.deleteSharedContent = async function(contentId) {
    if (!confirm('Are you sure you want to permanently delete this QR code? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await apiRequest(`/content/delete/${contentId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('QR code deleted successfully', 'success');
            await loadSharedContent();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete');
        }
    } catch (error) {
        console.error('Error deleting content:', error);
        showNotification(error.message || 'Failed to delete content', 'error');
    }
};

// Store original content list for filtering
let originalSharedContent = [];

// Filter functions
window.applySharedFilters = function() {
    if (originalSharedContent.length === 0) {
        showNotification('No content to filter', 'warning');
        return;
    }
    
    const status = document.getElementById('filterStatus').value;
    const type = document.getElementById('filterType').value;
    const views = document.getElementById('filterViews').value;
    const dateFrom = document.getElementById('filterDateFrom').value;
    const dateTo = document.getElementById('filterDateTo').value;
    const search = document.getElementById('filterSearch').value.toLowerCase();
    
    let filtered = originalSharedContent.filter(content => {
        // Status filter
        if (status !== 'all') {
            if (status === 'active' && !content.is_active) return false;
            if (status === 'inactive' && content.is_active) return false;
        }
        
        // Type filter
        if (type !== 'all') {
            const contentType = content.metadata?.type || 'unknown';
            const isFile = contentType === 'file';
            
            if (type === 'text' && (isFile || contentType !== 'text')) return false;
            if (type === 'image' && (!isFile || !content.metadata?.content_type?.startsWith('image/'))) return false;
            if (type === 'video' && (!isFile || !content.metadata?.content_type?.startsWith('video/'))) return false;
            if (type === 'audio' && (!isFile || !content.metadata?.content_type?.startsWith('audio/'))) return false;
            if (type === 'file' && !isFile) return false;
        }
        
        // Views filter
        if (views !== 'all') {
            const viewCount = content.view_count || 0;
            if (views === '0' && viewCount !== 0) return false;
            if (views === '1-5' && (viewCount < 1 || viewCount > 5)) return false;
            if (views === '6-20' && (viewCount < 6 || viewCount > 20)) return false;
            if (views === '20+' && viewCount <= 20) return false;
        }
        
        // Date range filter
        const contentDate = new Date(content.created_at);
        if (dateFrom) {
            const fromDate = new Date(dateFrom);
            if (contentDate < fromDate) return false;
        }
        if (dateTo) {
            const toDate = new Date(dateTo);
            toDate.setHours(23, 59, 59); // End of day
            if (contentDate > toDate) return false;
        }
        
        // Search filter
        if (search) {
            const filename = (content.metadata?.filename || '').toLowerCase();
            const receiver = (content.receiver_name || '').toLowerCase();
            if (!filename.includes(search) && !receiver.includes(search)) return false;
        }
        
        return true;
    });
    
    displaySharedContent(filtered);
    showNotification(`Showing ${filtered.length} of ${originalSharedContent.length} items`, 'info');
};

window.resetSharedFilters = function() {
    document.getElementById('filterStatus').value = 'all';
    document.getElementById('filterType').value = 'all';
    document.getElementById('filterViews').value = 'all';
    document.getElementById('filterDateFrom').value = '';
    document.getElementById('filterDateTo').value = '';
    document.getElementById('filterSearch').value = '';
    
    displaySharedContent(originalSharedContent);
    showNotification('Filters reset', 'info');
};

function updateUserProfile() {
    if (!state.user) return;
    
    const profileName = document.getElementById('profileName');
    const profileEmail = document.getElementById('profileEmail');
    const userAvatar = document.getElementById('userAvatar');
    const profileAvatarLarge = document.getElementById('profileAvatarLarge');
    
    if (profileName) profileName.textContent = state.user.username;
    if (profileEmail) profileEmail.textContent = state.user.email;
    if (userAvatar) userAvatar.textContent = state.user.username.charAt(0).toUpperCase();
    if (profileAvatarLarge) profileAvatarLarge.textContent = state.user.username.charAt(0).toUpperCase();
}

function updateNotifications() {
    const notifCount = document.getElementById('notificationCount');
    if (notifCount) {
        const unreadCount = state.notifications.filter(n => !n.read).length;
        notifCount.textContent = unreadCount;
        notifCount.style.display = unreadCount > 0 ? 'flex' : 'none';
    }
}

function updateFriendRequests() {
    // Implementation depends on UI structure
}

// Event Listeners Setup
function setupEventListeners() {
    // Navigation links
    console.log('Setting up event listeners...');
    const navLinks = document.querySelectorAll('.nav-link, .sidebar-link');
    console.log('Found navigation links:', navLinks.length);
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section || link.getAttribute('data-section');
            console.log('Link clicked, section:', section);
            
            if (section === 'logout') {
                return;
            }
            
            if (section) {
                console.log('About to call showSection with:', section);
                console.log('showSection exists?', typeof window.showSection);
                
                // DIRECT HANDLING FOR SPECIAL SECTIONS
                if (section === 'shared') {
                    console.log('DIRECT SHARED SECTION HANDLER');
                    // Hide all sections
                    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
                    // Show shared section
                    const sharedSection = document.getElementById('sharedSection');
                    if (sharedSection) {
                        sharedSection.classList.add('active');
                        console.log('Shared section activated directly');
                    }
                    // Update nav
                    document.querySelectorAll('.nav-link, .sidebar-link').forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                    // Load content
                    console.log('Calling loadSharedContent directly');
                    loadSharedContent();
                } else if (section === 'profile') {
                    console.log('DIRECT PROFILE SECTION HANDLER');
                    // Hide all sections
                    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
                    // Show profile section
                    const profileSection = document.getElementById('profileSection');
                    if (profileSection) {
                        profileSection.classList.add('active');
                        console.log('Profile section activated directly');
                    }
                    // Update nav
                    document.querySelectorAll('.nav-link, .sidebar-link').forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                    // Load profile data
                    console.log('Calling initProfilePage directly');
                    if (typeof initProfilePage !== 'undefined') {
                        initProfilePage();
                    } else {
                        console.error('initProfilePage is not defined!');
                    }
                } else if (section === 'files') {
                    console.log('DIRECT FILES SECTION HANDLER');
                    // Hide all sections
                    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
                    // Show files section
                    const filesSection = document.getElementById('filesSection');
                    if (filesSection) {
                        filesSection.classList.add('active');
                        console.log('Files section activated directly');
                    }
                    // Update nav
                    document.querySelectorAll('.nav-link, .sidebar-link').forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                    // Load chat page
                    console.log('Calling initChatPage directly');
                    if (typeof initChatPage !== 'undefined') {
                        initChatPage();
                    } else {
                        console.error('initChatPage is not defined!');
                    }
                } else if (section === 'settings') {
                    console.log('DIRECT SETTINGS SECTION HANDLER');
                    // Hide all sections
                    document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
                    // Show settings section
                    const settingsSection = document.getElementById('settingsSection');
                    if (settingsSection) {
                        settingsSection.classList.add('active');
                        console.log('Settings section activated directly');
                    }
                    // Update nav
                    document.querySelectorAll('.nav-link, .sidebar-link').forEach(l => l.classList.remove('active'));
                    link.classList.add('active');
                    // Load settings page
                    console.log('Calling initSettingsPage directly');
                    if (typeof initSettingsPage !== 'undefined') {
                        initSettingsPage();
                    } else {
                        console.error('initSettingsPage is not defined!');
                    }
                } else {
                    window.showSection(section);
                }
            }
        });
    });
    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail').value.trim();
            const phone = document.getElementById('loginPhone').value.trim();
            const password = document.getElementById('loginPassword').value;
            
            const result = await login(email, phone, password);
            if (result.success) {
                showSuccess('Login successful!');
            } else {
                showError(result.error);
            }
        });
    }
    
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('registerEmail').value.trim();
            const phone = document.getElementById('registerPhone').value.trim();
            const username = document.getElementById('registerUsername').value.trim();
            const password = document.getElementById('registerPassword').value;
            
            const result = await register(email, phone, username, password);
            if (result.success) {
                showSuccess('Registration successful! Please login.');
                document.getElementById('registerForm').classList.add('hidden');
                document.getElementById('loginForm').classList.remove('hidden');
            } else {
                showError(result.error);
            }
        });
    }
}

// Global logout function
window.logout = function() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('refreshToken');
    state.token = null;
    state.user = null;
    if (state.socket) {
        state.socket.disconnect();
        state.socket = null;
    }
    
    // Cleanup notification polling
    if (typeof cleanupNotifications !== 'undefined') {
        cleanupNotifications();
    }
    
    window.location.reload();
};

// Initialize theme on load
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (typeof applyTheme !== 'undefined') {
        applyTheme(savedTheme);
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    initApp();
});

