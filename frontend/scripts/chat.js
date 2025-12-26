// Chat/Messages Management
console.log('Chat.js module loaded');

let conversations = [];
let currentConversation = null;
let currentFriendId = null;
let messages = [];
let messagePollingInterval = null;

// Show toast notification
function showToast(message, type = 'info') {
    // Check if showMessage exists (from app.js)
    if (typeof window.showMessage === 'function') {
        window.showMessage(message, type);
        return;
    }
    
    // Fallback to console
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Simple toast implementation
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Get API base URL
function getApiUrl() {
    return window.API_BASE_URL || 'http://127.0.0.1:5000/api';
}

// Initialize Chat Page
async function initChatPage() {
    console.log('Initializing Chat page...');
    await loadConversations();
    setupChatListeners();
    startMessagePolling();
}

// Make function globally available
window.initChatPage = initChatPage;

// Setup event listeners
function setupChatListeners() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendMessageBtn');
    const shareQRBtn = document.getElementById('shareQRBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const chatSearch = document.getElementById('chatSearch');

    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    if (shareQRBtn) {
        shareQRBtn.addEventListener('click', showShareQRModal);
    }

    if (newChatBtn) {
        newChatBtn.addEventListener('click', showNewChatModal);
    }

    if (chatSearch) {
        chatSearch.addEventListener('input', (e) => {
            filterConversations(e.target.value);
        });
    }
}

// Load all conversations
async function loadConversations() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${getApiUrl()}/messages/conversations`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            conversations = data.conversations || [];
            renderConversations();
        } else {
            console.error('Failed to load conversations');
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

// Render conversations list
function renderConversations() {
    const container = document.getElementById('conversationsList');
    if (!container) return;

    if (conversations.length === 0) {
        container.innerHTML = '<p class="text-muted text-center" style="padding: 2rem;">No conversations yet. Start chatting with your friends!</p>';
        return;
    }

    container.innerHTML = conversations.map(conv => {
        const friend = conv.friend;
        const lastMsg = conv.last_message;
        const unread = conv.unread_count;
        
        // Ensure display_name has a fallback
        const displayName = friend.display_name || friend.username || 'Friend';
        const firstLetter = displayName.charAt(0).toUpperCase();
        
        const avatar = friend.avatar 
            ? `<img src="${friend.avatar}" alt="${displayName}">`
            : `<div class="avatar-placeholder">${firstLetter}</div>`;

        const messagePreview = lastMsg.type === 'qr' 
            ? '<i class="fas fa-qrcode"></i> QR Code'
            : lastMsg.type === 'file'
            ? '<i class="fas fa-file"></i> File'
            : lastMsg.content;

        const timeStr = formatMessageTime(lastMsg.created_at);

        return `
            <div class="conversation-item ${currentFriendId === friend.id ? 'active' : ''}" 
                 data-friend-id="${friend.id}" 
                 onclick="openConversation('${friend.id}', '${displayName.replace(/'/g, "\\'")}')">
                <div class="conversation-avatar">
                    ${avatar}
                </div>
                <div class="conversation-info">
                    <div class="conversation-header">
                        <h4>${displayName}</h4>
                        <span class="conversation-time">${timeStr}</span>
                    </div>
                    <div class="conversation-preview">
                        <p>${lastMsg.is_sender ? 'You: ' : ''}${messagePreview}</p>
                        ${unread > 0 ? `<span class="unread-badge">${unread}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Open a conversation
async function openConversation(friendId, friendName) {
    currentFriendId = friendId;
    
    // Update UI
    document.getElementById('chatEmpty').classList.add('hidden');
    document.getElementById('chatActive').classList.remove('hidden');
    document.getElementById('chatFriendName').textContent = friendName;
    
    // Set avatar
    const friend = conversations.find(c => c.friend.id === friendId)?.friend;
    const avatarEl = document.getElementById('chatFriendAvatar');
    if (friend && friend.avatar) {
        avatarEl.innerHTML = `<img src="${friend.avatar}" alt="${friendName}">`;
    } else {
        avatarEl.textContent = (friendName || 'F').charAt(0).toUpperCase();
    }

    // Load messages
    await loadMessages(friendId);
    
    // Update active state in conversations list
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`.conversation-item[data-friend-id="${friendId}"]`)?.classList.add('active');
}

// Load messages for a conversation
async function loadMessages(friendId) {
    try {
        const token = localStorage.getItem('token');
        const messagesLoading = document.getElementById('messagesLoading');
        messagesLoading?.classList.remove('hidden');

        const response = await fetch(`${getApiUrl()}/messages/conversation/${friendId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        messagesLoading?.classList.add('hidden');

        if (response.ok) {
            const data = await response.json();
            messages = data.messages || [];
            renderMessages();
            scrollToBottom();
            
            // Refresh conversations to update unread count
            await loadConversations();
        } else {
            console.error('Failed to load messages');
        }
    } catch (error) {
        console.error('Error loading messages:', error);
        document.getElementById('messagesLoading')?.classList.add('hidden');
    }
}

// Render messages
function renderMessages() {
    const container = document.getElementById('messagesList');
    if (!container) return;

    if (messages.length === 0) {
        container.innerHTML = '<p class="text-muted text-center" style="padding: 2rem;">No messages yet. Say hi!</p>';
        return;
    }

    container.innerHTML = messages.map(msg => {
        const isSender = msg.is_sender;
        const timeStr = formatMessageTime(msg.created_at);
        
        let messageContent = '';
        
        if (msg.type === 'text') {
            messageContent = `<p class="message-text">${escapeHtml(msg.content)}</p>`;
        } else if (msg.type === 'qr') {
            messageContent = `
                <div class="message-qr">
                    <i class="fas fa-qrcode"></i>
                    <p>Shared a QR Code</p>
                    ${msg.qr_data ? `<img src="${msg.qr_data}" alt="QR Code" style="max-width: 200px; border-radius: 8px; margin-top: 8px;">` : ''}
                </div>
            `;
        } else if (msg.type === 'file') {
            messageContent = `
                <div class="message-file">
                    <i class="fas fa-file"></i>
                    <p>Shared a file</p>
                </div>
            `;
        }

        return `
            <div class="message ${isSender ? 'message-sent' : 'message-received'}">
                <div class="message-bubble">
                    ${messageContent}
                    <span class="message-time">${timeStr}</span>
                </div>
            </div>
        `;
    }).join('');
}

// Send a message
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const content = input?.value.trim();

    if (!content || !currentFriendId) return;

    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${getApiUrl()}/messages/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                receiver_id: currentFriendId,
                content: content,
                type: 'text'
            })
        });

        if (response.ok) {
            const data = await response.json();
            messages.push(data.message);
            renderMessages();
            scrollToBottom();
            input.value = '';
            
            // Refresh conversations
            await loadConversations();
        } else {
            const error = await response.json();
            showToast(error.error || 'Failed to send message', 'error');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showToast('Failed to send message', 'error');
    }
}

// Show share QR modal
async function showShareQRModal() {
    if (!currentFriendId) return;

    const currentFriendName = document.getElementById('chatFriendName').textContent;
    
    // Create share QR modal with card-like design
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="share-qr-card">
            <div class="share-qr-header">
                <div class="share-qr-icon">
                    <i class="fas fa-qrcode"></i>
                </div>
                <h2 class="share-qr-title">Share QR Code</h2>
                <p class="share-qr-subtitle">Send encrypted content to ${currentFriendName}</p>
                <button class="share-qr-close" onclick="this.closest('.modal-overlay').remove()" title="Close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="share-qr-body">
                <!-- Content Type Selection -->
                <div class="qr-option-group">
                    <label class="qr-label">
                        <i class="fas fa-cube"></i> Content Type
                    </label>
                    <div class="qr-type-selector">
                        <button class="qr-type-btn active" data-type="text" onclick="selectQRType('text')">
                            <i class="fas fa-comment-alt"></i>
                            <span>Text</span>
                        </button>
                        <button class="qr-type-btn" data-type="file" onclick="selectQRType('file')">
                            <i class="fas fa-file-upload"></i>
                            <span>File</span>
                        </button>
                    </div>
                </div>
                
                <!-- Text Input -->
                <div class="qr-content-group" id="qrTextGroup">
                    <label class="qr-label" for="qrTextContent">
                        <i class="fas fa-pen"></i> Your Message
                    </label>
                    <textarea id="qrTextContent" class="qr-textarea" rows="4" placeholder="Type your secret message here..."></textarea>
                </div>
                
                <!-- File Input -->
                <div class="qr-content-group hidden" id="qrFileGroup">
                    <label class="qr-label" for="qrFileInput">
                        <i class="fas fa-paperclip"></i> Choose File
                    </label>
                    <div class="qr-file-upload">
                        <input type="file" id="qrFileInput" class="qr-file-input" accept="*/*" onchange="updateFileName(this)">
                        <label for="qrFileInput" class="qr-file-label">
                            <i class="fas fa-cloud-upload-alt"></i>
                            <span id="qrFileName">Click to choose file</span>
                        </label>
                    </div>
                </div>
                
                <!-- Security Options -->
                <div class="qr-security-grid">
                    <div class="qr-option-group">
                        <label class="qr-label" for="qrEncryption">
                            <i class="fas fa-shield-alt"></i> Encryption
                        </label>
                        <select id="qrEncryption" class="qr-select" title="Choose encryption level">
                            <option value="standard">🔒 Standard</option>
                            <option value="high">🔐 High Security</option>
                            <option value="extreme">🛡️ Extreme</option>
                        </select>
                    </div>
                    
                    <div class="qr-option-group">
                        <label class="qr-label" for="qrExpiration">
                            <i class="fas fa-clock"></i> Expires In
                        </label>
                        <select id="qrExpiration" class="qr-select" title="Choose expiration time">
                            <option value="">♾️ Never</option>
                            <option value="3600">⏱️ 1 Hour</option>
                            <option value="86400">📅 24 Hours</option>
                            <option value="604800">🗓️ 7 Days</option>
                            <option value="2592000">📆 30 Days</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="share-qr-footer">
                <button class="qr-btn qr-btn-cancel" onclick="this.closest('.modal-overlay').remove()">
                    <i class="fas fa-times"></i> Cancel
                </button>
                <button class="qr-btn qr-btn-primary" onclick="shareQRCodeToFriend()">
                    <i class="fas fa-paper-plane"></i> Generate & Share
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Focus on text input
    setTimeout(() => document.getElementById('qrTextContent').focus(), 100);
}

// Select QR content type
window.selectQRType = function(type) {
    const textGroup = document.getElementById('qrTextGroup');
    const fileGroup = document.getElementById('qrFileGroup');
    const buttons = document.querySelectorAll('.qr-type-btn');
    
    buttons.forEach(btn => {
        if (btn.dataset.type === type) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    if (type === 'text') {
        textGroup.classList.remove('hidden');
        fileGroup.classList.add('hidden');
        setTimeout(() => document.getElementById('qrTextContent').focus(), 100);
    } else {
        textGroup.classList.add('hidden');
        fileGroup.classList.remove('hidden');
    }
}

// Update file name display
window.updateFileName = function(input) {
    const fileNameDisplay = document.getElementById('qrFileName');
    if (input.files && input.files[0]) {
        const fileName = input.files[0].name;
        const fileSize = (input.files[0].size / 1024).toFixed(2);
        fileNameDisplay.innerHTML = `<i class="fas fa-file"></i> ${fileName} <span style="opacity: 0.7; font-size: 0.85em;">(${fileSize} KB)</span>`;
    } else {
        fileNameDisplay.innerHTML = '<i class="fas fa-cloud-upload-alt"></i> Click to choose file';
    }
}

// Toggle QR content input (legacy support)
window.toggleQRContentInput = function() {
    const contentType = document.getElementById('qrContentType').value;
    const textGroup = document.getElementById('qrTextGroup');
    const fileGroup = document.getElementById('qrFileGroup');
    
    if (contentType === 'text') {
        textGroup.classList.remove('hidden');
        fileGroup.classList.add('hidden');
    } else {
        textGroup.classList.add('hidden');
        fileGroup.classList.remove('hidden');
    }
}

// Share QR code to friend
window.shareQRCodeToFriend = async function() {
    try {
        // Get content type from active button instead of select
        const activeTypeBtn = document.querySelector('.qr-type-btn.active');
        const contentType = activeTypeBtn ? activeTypeBtn.dataset.type : 'text';
        
        const encryption = document.getElementById('qrEncryption').value;
        const expirationStr = document.getElementById('qrExpiration').value;
        const expiration = expirationStr ? parseInt(expirationStr, 10) : null;
        const token = localStorage.getItem('token');
        
        let shareData;
        let formData = null;
        
        if (contentType === 'text') {
            const text = document.getElementById('qrTextContent').value.trim();
            if (!text) {
                showToast('Please enter text to share', 'error');
                return;
            }
            
            shareData = {
                text: text,
                receiver_id: currentFriendId,
                encryption_level: encryption,
                expires_in: expiration
            };
        } else {
            const fileInput = document.getElementById('qrFileInput');
            if (!fileInput.files || !fileInput.files[0]) {
                showToast('Please select a file to share', 'error');
                return;
            }
            
            formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('receiver_id', currentFriendId);
            formData.append('encryption_level', encryption);
            if (expiration) formData.append('expires_in', expiration.toString());
        }
        
        // Share content
        const endpoint = contentType === 'text' ? '/content/share/text' : '/content/share/file';
        const response = await fetch(`${getApiUrl()}${endpoint}`, {
            method: 'POST',
            headers: formData ? {
                'Authorization': `Bearer ${token}`
            } : {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: formData || JSON.stringify(shareData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to share content');
        }
        
        const result = await response.json();
        
        // Close modal
        document.querySelector('.modal-overlay').remove();
        
        // Send message in chat with QR info
        const friendName = document.getElementById('chatFriendName').textContent;
        await sendMessage(`🎁 Shared a QR Code: ${contentType === 'text' ? 'Text Message' : fileInput.files[0].name}\n\n🔒 Encryption: ${encryption}\n⏰ Expires: ${expiration ? formatExpiration(expiration) : 'Never'}\n\nScan the QR code I generated for you!`, 'qr_share', result.content_id);
        
        showToast('QR Code generated and shared successfully!', 'success');
        
        // Refresh shared page in background
        if (typeof loadSharedContent === 'function') {
            setTimeout(() => loadSharedContent(), 1000);
        }
        
    } catch (error) {
        console.error('Error sharing QR:', error);
        showToast(error.message || 'Failed to share QR code', 'error');
    }
}

// Format expiration time
function formatExpiration(seconds) {
    if (seconds == 3600) return '1 Hour';
    if (seconds == 86400) return '24 Hours';
    if (seconds == 604800) return '7 Days';
    if (seconds == 2592000) return '30 Days';
    return `${seconds} seconds`;
}

// Show new chat modal
async function showNewChatModal() {
    // Load friends and show a modal to start a new chat
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${getApiUrl()}/friends/list`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            const friends = data.friends || [];
            
            if (friends.length === 0) {
                showToast('Add friends first to start chatting!', 'info');
                showSection('friends');
                return;
            }

            // Show modal with friends list
            showFriendsModal(friends);
        }
    } catch (error) {
        console.error('Error loading friends:', error);
    }
}

// Show friends modal to start new chat
function showFriendsModal(friends) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h3>Start New Chat</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <input type="text" id="friendSearchModal" class="form-input" placeholder="Search friends..." style="margin-bottom: 1rem;">
                <div class="friends-list-modal" id="friendsListModal">
                    ${friends.map(friend => {
                        const displayName = friend.username || 'Friend';
                        const avatar = friend.profile_pic_url;
                        return `
                        <div class="friend-item-modal" onclick="startChatWith('${friend.friend_id}', '${displayName.replace(/'/g, "\\'")}')">\n                            <div class="friend-avatar-modal">
                                ${avatar ? `<img src="${avatar}" alt="${displayName}">` : displayName.charAt(0).toUpperCase()}
                            </div>
                            <div class="friend-info-modal">
                                <h4>${displayName}</h4>
                                <p class="text-muted">@${friend.username}</p>
                            </div>
                        </div>
                    `}).join('')}
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// Start chat with a specific friend
async function startChatWith(friendId, friendName) {
    // Close modal
    document.querySelector('.modal-overlay')?.remove();
    
    // Open conversation
    await openConversation(friendId, friendName);
}

// Make function global
window.startChatWith = startChatWith;

// Filter conversations
function filterConversations(query) {
    const filtered = conversations.filter(conv => {
        const friend = conv.friend;
        const displayName = friend.display_name || friend.username || '';
        return displayName.toLowerCase().includes(query.toLowerCase()) ||
               (friend.username || '').toLowerCase().includes(query.toLowerCase());
    });
    
    const container = document.getElementById('conversationsList');
    if (!container) return;

    if (filtered.length === 0) {
        container.innerHTML = '<p class="text-muted text-center" style="padding: 2rem;">No conversations found</p>';
        return;
    }

    // Render filtered conversations (similar to renderConversations but with filtered data)
    container.innerHTML = filtered.map(conv => {
        const friend = conv.friend;
        const lastMsg = conv.last_message;
        const unread = conv.unread_count;
        
        const displayName = friend.display_name || friend.username || 'Friend';
        const firstLetter = displayName.charAt(0).toUpperCase();
        
        const avatar = friend.avatar 
            ? `<img src="${friend.avatar}" alt="${displayName}">`
            : `<div class="avatar-placeholder">${firstLetter}</div>`;

        const messagePreview = lastMsg.type === 'qr' 
            ? '<i class="fas fa-qrcode"></i> QR Code'
            : lastMsg.type === 'file'
            ? '<i class="fas fa-file"></i> File'
            : lastMsg.content;

        const timeStr = formatMessageTime(lastMsg.created_at);

        return `
            <div class="conversation-item ${currentFriendId === friend.id ? 'active' : ''}" 
                 data-friend-id="${friend.id}" 
                 onclick="openConversation('${friend.id}', '${displayName.replace(/'/g, "\\'")}')">
                <div class="conversation-avatar">
                    ${avatar}
                </div>
                <div class="conversation-info">
                    <div class="conversation-header">
                        <h4>${displayName}</h4>
                        <span class="conversation-time">${timeStr}</span>
                    </div>
                    <div class="conversation-preview">
                        <p>${lastMsg.is_sender ? 'You: ' : ''}${messagePreview}</p>
                        ${unread > 0 ? `<span class="unread-badge">${unread}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Scroll to bottom of messages
function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    if (container) {
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 100);
    }
}

// Format message time
function formatMessageTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    // Less than 1 minute
    if (diff < 60000) {
        return 'Just now';
    }
    
    // Less than 1 hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes}m ago`;
    }
    
    // Today
    if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    }
    
    // Yesterday
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
    }
    
    // Within a week
    if (diff < 604800000) {
        return date.toLocaleDateString('en-US', { weekday: 'short' });
    }
    
    // Older
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Start polling for new messages
function startMessagePolling() {
    // Poll every 10 seconds for new messages (reduced to avoid rate limits)
    messagePollingInterval = setInterval(async () => {
        if (currentFriendId) {
            await loadMessages(currentFriendId);
        }
        // Always refresh conversations to update unread counts
        await loadConversations();
    }, 10000);
}

// Stop polling
function stopMessagePolling() {
    if (messagePollingInterval) {
        clearInterval(messagePollingInterval);
        messagePollingInterval = null;
    }
}

// Cleanup when leaving page
window.addEventListener('beforeunload', () => {
    stopMessagePolling();
});
