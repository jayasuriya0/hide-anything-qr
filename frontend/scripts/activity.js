// Activity Feed Functions

// Load activity feed
async function loadActivityFeed() {
    try {
        const response = await apiRequest('/activity/feed?limit=30');
        if (response.ok) {
            const data = await response.json();
            displayActivityFeed(data.activities);
        }
    } catch (error) {
        console.error('Failed to load activity feed:', error);
    }
}

// Load user statistics
async function loadActivityStats() {
    try {
        console.log('[loadActivityStats] Fetching stats from /profile endpoint...');
        const response = await apiRequest('/profile');
        if (response.ok) {
            const profile = await response.json();
            console.log('[loadActivityStats] Profile response:', profile);
            console.log('[loadActivityStats] Stats from profile:', profile.stats);
            if (profile.stats) {
                updateDashboardStats(profile.stats);
            } else {
                console.warn('[loadActivityStats] No stats found in profile response');
            }
        } else {
            console.error('[loadActivityStats] Failed to fetch profile, status:', response.status);
        }
    } catch (error) {
        console.error('[loadActivityStats] Error loading activity stats:', error);
    }
}

// Display activity feed in sidebar
function displayActivityFeed(activities) {
    const feedContainer = document.querySelector('.activity-feed');
    if (!feedContainer) return;
    
    if (!activities || activities.length === 0) {
        feedContainer.innerHTML = '<p class="text-muted text-center">No recent activity</p>';
        return;
    }
    
    feedContainer.innerHTML = activities.slice(0, 5).map(activity => {
        const icon = getActivityIcon(activity.type);
        const timeAgo = formatTimeAgo(new Date(activity.created_at));
        const username = activity.user ? activity.user.username : 'Someone';
        
        return `
            <div class="activity-item" data-activity-id="${activity.id}">
                <i class="${icon}"></i>
                <div>
                    <p>${formatActivityDescription(activity, username)}</p>
                    <span class="time">${timeAgo}</span>
                </div>
            </div>
        `;
    }).join('');
}

// Get icon for activity type
function getActivityIcon(type) {
    const icons = {
        'share_qr': 'fas fa-qrcode',
        'scan_qr': 'fas fa-camera',
        'add_friend': 'fas fa-user-plus',
        'accept_friend': 'fas fa-handshake',
        'upload_file': 'fas fa-upload',
        'download_file': 'fas fa-download'
    };
    return icons[type] || 'fas fa-info-circle';
}

// Format activity description
function formatActivityDescription(activity, username) {
    // If it's the current user's activity
    if (activity.user_id === state.user.id) {
        return activity.description;
    }
    // If it's a friend's activity
    return `<strong>${username}</strong> ${activity.description.toLowerCase()}`;
}

// Format time ago
function formatTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
}

// Update dashboard stats from activity stats
function updateDashboardStats(stats) {
    console.log('Updating dashboard stats:', stats);
    
    const totalQrCountEl = document.getElementById('totalQrCount');
    const activeQrCountEl = document.getElementById('activeQrCount');
    const deletedQrCountEl = document.getElementById('deletedQrCount');
    const friendCountEl = document.getElementById('friendCount');
    const lastActivityEl = document.querySelector('.stat-card:last-child .stat-number');
    
    // Update Total QR Generated count
    if (totalQrCountEl) {
        const count = stats.total_qr_generated || stats.content_shared || 0;
        console.log('Setting totalQrCount to:', count);
        totalQrCountEl.textContent = count;
    }
    
    // Update Active QR codes count
    if (activeQrCountEl) {
        const count = stats.active_qr_count || 0;
        console.log('Setting activeQrCount to:', count);
        activeQrCountEl.textContent = count;
    }
    
    // Update Deleted QR codes count
    if (deletedQrCountEl) {
        const count = stats.deleted_qr_count || 0;
        console.log('Setting deletedQrCount to:', count);
        deletedQrCountEl.textContent = count;
    }
    
    // Update friends count from backend stats
    if (friendCountEl) {
        const count = stats.friends_count || 0;
        console.log('Setting friendCount to:', count);
        friendCountEl.textContent = count;
    }
    
    // Update friends count
    if (friendCountEl) {
        // Get friends count from state or fetch it
        if (state.friends && state.friends.length > 0) {
            friendCountEl.textContent = state.friends.length;
        } else {
            // Fetch friends count
            apiRequest('/friends/list').then(async res => {
                if (res.ok) {
                    const data = await res.json();
                    friendCountEl.textContent = data.friends?.length || 0;
                    state.friends = data.friends || [];
                }
            });
        }
    }
    
    // Update last activity time
    const lastActivityTimeEl = document.getElementById('lastActivityTime');
    if (lastActivityTimeEl && stats.last_activity) {
        const lastActivityTime = new Date(stats.last_activity);
        lastActivityTimeEl.textContent = formatTimeAgo(lastActivityTime);
    } else if (lastActivityTimeEl) {
        lastActivityTimeEl.textContent = 'No activity yet';
    }
}

// Load recent shares for display
async function loadRecentShares() {
    try {
        const response = await apiRequest('/activity/recent-shares?limit=10');
        if (response.ok) {
            const data = await response.json();
            return data.shares;
        }
    } catch (error) {
        console.error('Failed to load recent shares:', error);
    }
    return [];
}

// Load recent scans for display
async function loadRecentScans() {
    try {
        const response = await apiRequest('/activity/recent-scans?limit=10');
        if (response.ok) {
            const data = await response.json();
            return data.scans;
        }
    } catch (error) {
        console.error('Failed to load recent scans:', error);
    }
    return [];
}

// Load friend activities
async function loadFriendActivities() {
    try {
        const response = await apiRequest('/activity/friend-activities?limit=20');
        if (response.ok) {
            const data = await response.json();
            return data.activities;
        }
    } catch (error) {
        console.error('Failed to load friend activities:', error);
    }
    return [];
}

// Refresh activity feed
async function refreshActivityFeed() {
    await loadActivityFeed();
    await loadActivityStats();
}

// Set up automatic refresh for activity feed
function setupActivityRefresh() {
    // Refresh every 30 seconds
    setInterval(refreshActivityFeed, 30000);
}

// Listen for real-time activity updates via WebSocket
function setupActivityWebSocket() {
    if (state.socket) {
        state.socket.on('new_activity', (data) => {
            refreshActivityFeed();
        });
        
        state.socket.on('friend_activity', (data) => {
            refreshActivityFeed();
        });
    }
}

// Initialize activity feed system
function initActivityFeed() {
    loadActivityFeed();
    loadActivityStats();
    setupActivityRefresh();
    setupActivityWebSocket();
}

// Export for use in app.js
window.initActivityFeed = initActivityFeed;
window.refreshActivityFeed = refreshActivityFeed;
window.loadActivityFeed = loadActivityFeed;
window.loadActivityStats = loadActivityStats;
