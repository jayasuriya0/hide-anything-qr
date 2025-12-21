// Notification Management Module
let notificationCheckInterval = null;
let unreadCount = 0;

// Initialize notification system
function initNotifications() {
    loadNotifications();
    setupNotificationWebSocket();
    startNotificationPolling();
    setupNotificationHandlers();
}

// Load notifications from server
async function loadNotifications() {
    try {
        const response = await fetch('/api/notifications', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (!response.ok) throw new Error('Failed to load notifications');

        const data = await response.json();
        displayNotifications(data.notifications);
        await updateUnreadCount();
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

// Display notifications in dropdown
function displayNotifications(notifications) {
    const container = document.getElementById('notificationList');
    if (!container) return;

    if (!notifications || notifications.length === 0) {
        container.innerHTML = '<div class="notification-item empty">No notifications</div>';
        return;
    }

    container.innerHTML = notifications.map(notification => {
        const readClass = notification.is_read ? 'read' : 'unread';
        const icon = getNotificationIcon(notification.type);
        const message = formatNotificationMessage(notification);
        const time = formatTimeAgo(new Date(notification.created_at));

        return `
            <div class="notification-item ${readClass}" data-id="${notification._id}">
                <div class="notification-icon">${icon}</div>
                <div class="notification-content">
                    <div class="notification-message">${message}</div>
                    <div class="notification-time">${time}</div>
                </div>
                ${!notification.is_read ? `
                    <button class="mark-read-btn" onclick="markNotificationAsRead('${notification._id}')">
                        ✓
                    </button>
                ` : ''}
                <button class="delete-notification-btn" onclick="deleteNotification('${notification._id}')">
                    ×
                </button>
            </div>
        `;
    }).join('');

    // Add click handlers for notifications
    document.querySelectorAll('.notification-item').forEach(item => {
        item.addEventListener('click', async (e) => {
            // Skip if clicking buttons
            if (e.target.classList.contains('mark-read-btn') || 
                e.target.classList.contains('delete-notification-btn')) {
                return;
            }

            const notificationId = item.dataset.id;
            const notification = notifications.find(n => n._id === notificationId);
            
            if (notification && !notification.is_read) {
                await markNotificationAsRead(notificationId);
            }

            // Handle notification click action
            handleNotificationClick(notification);
        });
    });
}

// Get icon for notification type
function getNotificationIcon(type) {
    const icons = {
        'friend_request': '👤',
        'friend_accepted': '✓',
        'content_received': '📦',
        'content_viewed': '👁️',
        'activity': '🔔'
    };
    return icons[type] || '🔔';
}

// Format notification message
function formatNotificationMessage(notification) {
    const user = notification.related_user;
    const username = user ? `<strong>${user.username}</strong>` : 'Someone';
    
    switch (notification.type) {
        case 'friend_request':
            return `${username} sent you a friend request`;
        case 'friend_accepted':
            return `${username} accepted your friend request`;
        case 'content_received':
            const contentType = notification.metadata?.content_type || 'content';
            return `${username} sent you ${contentType}`;
        case 'content_viewed':
            return `${username} viewed your content`;
        case 'activity':
            return notification.message || 'New activity';
        default:
            return notification.message || 'New notification';
    }
}

// Handle notification click
function handleNotificationClick(notification) {
    if (!notification) return;

    switch (notification.type) {
        case 'friend_request':
            // Navigate to friends tab
            if (window.location.pathname.includes('dashboard')) {
                showFriendsTab();
            }
            break;
        case 'content_received':
            // Could navigate to content or show QR scanner
            if (window.location.pathname.includes('dashboard')) {
                showQRScannerTab();
            }
            break;
        case 'friend_accepted':
            // Navigate to friends tab
            if (window.location.pathname.includes('dashboard')) {
                showFriendsTab();
            }
            break;
    }

    // Close notification dropdown
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) {
        dropdown.style.display = 'none';
    }
}

// Helper functions for navigation (to be defined in main app)
function showFriendsTab() {
    if (window.showSection) {
        window.showSection('friends');
    }
}

function showQRScannerTab() {
    if (window.showSection) {
        window.showSection('scan');
    }
}

// Update unread count badge
async function updateUnreadCount() {
    try {
        const response = await fetch('/api/notifications/unread-count', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (!response.ok) throw new Error('Failed to get unread count');

        const data = await response.json();
        unreadCount = data.total_unread || 0;
        
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error updating unread count:', error);
    }
}

// Mark notification as read
async function markNotificationAsRead(notificationId) {
    try {
        const response = await fetch(`/api/notifications/${notificationId}/read`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (!response.ok) throw new Error('Failed to mark as read');

        await loadNotifications();
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

// Mark all notifications as read
async function markAllAsRead() {
    try {
        const response = await fetch('/api/notifications/read-all', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (!response.ok) throw new Error('Failed to mark all as read');

        await loadNotifications();
    } catch (error) {
        console.error('Error marking all as read:', error);
    }
}

// Delete single notification
async function deleteNotification(notificationId) {
    try {
        const response = await fetch(`/api/notifications/${notificationId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (!response.ok) throw new Error('Failed to delete notification');

        await loadNotifications();
    } catch (error) {
        console.error('Error deleting notification:', error);
    }
}

// Clear all notifications
async function clearAllNotifications() {
    if (!confirm('Are you sure you want to clear all notifications?')) {
        return;
    }

    try {
        const response = await fetch('/api/notifications/clear-all', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (!response.ok) throw new Error('Failed to clear notifications');

        await loadNotifications();
    } catch (error) {
        console.error('Error clearing notifications:', error);
    }
}

// Setup WebSocket listeners for real-time notifications
function setupNotificationWebSocket() {
    if (!window.socket) return;

    // Listen for new notifications
    window.socket.on('new_notification', async (data) => {
        console.log('New notification received:', data);
        await loadNotifications();
        
        // Show toast notification
        showNotificationToast(data);
    });

    // Listen for friend requests
    window.socket.on('friend_request', async (data) => {
        await loadNotifications();
        showNotificationToast({
            type: 'friend_request',
            message: `${data.from_username} sent you a friend request`
        });
    });

    // Listen for friend request accepted
    window.socket.on('friend_request_accepted', async (data) => {
        await loadNotifications();
        showNotificationToast({
            type: 'friend_accepted',
            message: `${data.from_username} accepted your friend request`
        });
    });

    // Listen for new content
    window.socket.on('new_content', async (data) => {
        await loadNotifications();
        showNotificationToast({
            type: 'content_received',
            message: 'You received new content'
        });
    });
}

// Show toast notification
function showNotificationToast(notification) {
    const toast = document.createElement('div');
    toast.className = 'notification-toast';
    toast.innerHTML = `
        <div class="toast-icon">${getNotificationIcon(notification.type)}</div>
        <div class="toast-message">${notification.message}</div>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Start polling for notifications
function startNotificationPolling() {
    // Poll every 30 seconds
    notificationCheckInterval = setInterval(updateUnreadCount, 30000);
}

// Stop polling
function stopNotificationPolling() {
    if (notificationCheckInterval) {
        clearInterval(notificationCheckInterval);
        notificationCheckInterval = null;
    }
}

// Setup notification UI handlers
function setupNotificationHandlers() {
    // Toggle notification dropdown
    const notificationBtn = document.getElementById('notificationBtn');
    const dropdown = document.getElementById('notificationDropdown');
    
    if (notificationBtn && dropdown) {
        notificationBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isVisible = dropdown.style.display === 'block';
            dropdown.style.display = isVisible ? 'none' : 'block';
            
            if (!isVisible) {
                loadNotifications();
            }
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (dropdown && !dropdown.contains(e.target) && e.target !== notificationBtn) {
            dropdown.style.display = 'none';
        }
    });

    // Mark all as read button
    const markAllBtn = document.getElementById('markAllReadBtn');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', markAllAsRead);
    }

    // Clear all button
    const clearAllBtn = document.getElementById('clearAllBtn');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', clearAllNotifications);
    }
}

// Format time ago helper
function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
        }
    }
    
    return 'Just now';
}

// Cleanup on logout
function cleanupNotifications() {
    stopNotificationPolling();
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initNotifications,
        loadNotifications,
        markNotificationAsRead,
        markAllAsRead,
        deleteNotification,
        clearAllNotifications,
        cleanupNotifications
    };
}
