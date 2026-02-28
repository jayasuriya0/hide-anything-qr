// Friend Management Functions

async function searchUsers(query) {
    try {
        const response = await apiRequest(`/profile/search?q=${encodeURIComponent(query)}`);
        if (response.ok) {
            return await response.json();
        }
        return { users: [] };
    } catch (error) {
        console.error('Search failed:', error);
        return { users: [] };
    }
}

async function sendFriendRequest(receiverId, message = '') {
    try {
        const response = await apiRequest('/friends/request', {
            method: 'POST',
            body: JSON.stringify({ receiver_id: receiverId, message })
        });
        
        if (response.ok) {
            return await response.json();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Request failed');
        }
    } catch (error) {
        throw error;
    }
}

async function getFriendRequests() {
    try {
        const response = await apiRequest('/friends/requests');
        if (response.ok) {
            return await response.json();
        }
        return { requests: [] };
    } catch (error) {
        console.error('Failed to get friend requests:', error);
        return { requests: [] };
    }
}

window.acceptFriendRequest = async function(requestId) {
    try {
        const sharedKey = await generateSharedKey();
        
        const response = await apiRequest('/friends/accept', {
            method: 'POST',
            body: JSON.stringify({
                request_id: requestId,
                shared_key: sharedKey
            })
        });
        
        if (response.ok) {
            showSuccess('Friend request accepted!');
            updateFriendRequests();
            updateFriendsList();
        } else {
            showError('Failed to accept friend request');
        }
    } catch (error) {
        showError(error.message);
    }
};

window.rejectFriendRequest = async function(requestId) {
    try {
        const response = await apiRequest('/friends/reject', {
            method: 'POST',
            body: JSON.stringify({ request_id: requestId })
        });
        
        if (response.ok) {
            showSuccess('Friend request rejected');
            updateFriendRequests();
        } else {
            showError('Failed to reject friend request');
        }
    } catch (error) {
        showError(error.message);
    }
};

window.sendFriendRequestTo = async function(userId, buttonElement) {
    try {
        // Get the button element if not passed
        if (!buttonElement) {
            buttonElement = event.target.closest('button');
        }
        
        // Disable button and show loading
        if (buttonElement) {
            buttonElement.disabled = true;
            buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        }
        
        const result = await sendFriendRequest(userId, 'Hello!');
        showSuccess('Friend request sent!');
        
        // Update button to show request sent
        if (buttonElement) {
            buttonElement.className = 'btn btn-secondary';
            buttonElement.innerHTML = '<i class="fas fa-check"></i> Request Sent';
            buttonElement.disabled = true;
            buttonElement.style.cursor = 'not-allowed';
        }
        
        if (result.qr_code) {
            generateQRCode(result.qr_code);
        }
    } catch (error) {
        showError(error.message);
        // Reset button on error
        if (buttonElement) {
            buttonElement.disabled = false;
            buttonElement.className = 'btn btn-primary';
            buttonElement.innerHTML = '<i class="fas fa-user-plus"></i> Add Friend';
        }
    }
};

function updateFriendsList() {
    const friendsList = document.getElementById('friendsList');
    if (!friendsList) return;
    
    if (!state.friends || state.friends.length === 0) {
        friendsList.innerHTML = '<p class="text-muted text-center">No friends yet</p>';
        return;
    }
    
    friendsList.innerHTML = '';
    
    state.friends.forEach(friend => {
        const friendDiv = document.createElement('div');
        friendDiv.className = 'friend-item';
        friendDiv.innerHTML = `
            <div class="friend-info">
                <div class="friend-avatar">${friend.username.charAt(0).toUpperCase()}</div>
                <div>
                    <strong style="cursor: pointer; color: #667eea;" onclick="viewUserProfile('${friend.friend_id}')" title="View profile">${friend.username}</strong>
                </div>
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <button onclick="shareWithFriend('${friend.friend_id}')" class="btn btn-primary">
                    <i class="fas fa-share"></i> Share
                </button>
                <button onclick="removeFriend('${friend.friend_id}')" class="btn btn-secondary">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        friendsList.appendChild(friendDiv);
    });
}

async function updateFriendRequests() {
    const requestsList = document.getElementById('friendRequestsList');
    if (!requestsList) return;
    
    try {
        const data = await getFriendRequests();
        const requests = data.requests || [];
        
        if (requests.length === 0) {
            requestsList.innerHTML = '<p class="text-muted text-center">No pending requests</p>';
            return;
        }
        
        requestsList.innerHTML = '';
        
        requests.forEach(req => {
            const reqDiv = document.createElement('div');
            reqDiv.className = 'friend-request-item';
            reqDiv.innerHTML = `
                <div class="friend-info">
                    <div class="friend-avatar">${req.sender_username.charAt(0).toUpperCase()}</div>
                    <div>
                        <strong>${req.sender_username}</strong>
                        ${req.message ? `<p class="text-muted" style="margin: 0.25rem 0 0 0; font-size: 0.85rem; font-style: italic;">"${req.message}"</p>` : ''}
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <button onclick="acceptFriendRequest('${req.request_id}')" class="btn btn-success">
                        <i class="fas fa-check"></i> Accept
                    </button>
                    <button onclick="rejectFriendRequest('${req.request_id}')" class="btn btn-danger">
                        <i class="fas fa-times"></i> Reject
                    </button>
                </div>
            `;
            requestsList.appendChild(reqDiv);
        });
    } catch (error) {
        console.error('Failed to update friend requests:', error);
        requestsList.innerHTML = '<p class="text-muted text-center">Failed to load requests</p>';
    }
}

function displaySearchResults(users) {
    const resultsContainer = document.getElementById('searchResults');
    if (!resultsContainer) return;
    
    if (users.length === 0) {
        resultsContainer.innerHTML = '<p class="text-muted text-center">No users found</p>';
        return;
    }
    
    resultsContainer.innerHTML = '';
    
    users.forEach(user => {
        const userDiv = document.createElement('div');
        userDiv.className = 'user-search-item';
        
        const visibilityIcon = user.profile_visibility === 'private' 
            ? '<i class="fas fa-lock" title="Private Profile" style="color: rgba(255,255,255,0.5); margin-left: 0.5rem;"></i>' 
            : '';
        
        userDiv.innerHTML = `
            <div>
                <strong>${user.username}</strong>${visibilityIcon}
                ${user.bio ? `<p class="text-muted" style="font-size: 0.875rem; margin: 0.25rem 0 0 0;">${user.bio}</p>` : ''}
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <button onclick="viewUserProfile('${user.user_id}')" class="btn btn-outline" style="padding: 0.5rem 1rem;">
                    <i class="fas fa-eye"></i> View Profile
                </button>
                <button onclick="sendFriendRequestTo('${user.user_id}', this)" class="btn btn-primary" data-user-id="${user.user_id}" style="padding: 0.5rem 1rem;">
                    <i class="fas fa-user-plus"></i> Add Friend
                </button>
            </div>
        `;
        resultsContainer.appendChild(userDiv);
    });
}

// Setup search listener
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchUsersInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', async (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(async () => {
                const query = e.target.value;
                if (query.length >= 2) {
                    const result = await searchUsers(query);
                    displaySearchResults(result.users);
                }
            }, 300);
        });
    }
});

// Remove friend
window.removeFriend = async function(friendId) {
    if (!confirm('Are you sure you want to remove this friend?')) {
        return;
    }
    
    try {
        const response = await apiRequest(`/friends/remove/${friendId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showSuccess('Friend removed');
            // Reload friends list
            const friendsResponse = await apiRequest('/friends/list');
            if (friendsResponse.ok) {
                const data = await friendsResponse.json();
                state.friends = data.friends;
                updateFriendsList();
            }
        } else {
            showError('Failed to remove friend');
        }
    } catch (error) {
        showError(error.message);
    }
};

// Share with friend - navigate to generate section with friend pre-selected
window.shareWithFriend = function(friendId) {
    // Store the selected friend ID
    localStorage.setItem('selectedFriendId', friendId);
    
    // Navigate to generate QR section
    const generateTab = document.querySelector('[data-section="generate"]');
    if (generateTab) {
        generateTab.click();
        
        // Wait a bit for the section to load, then select the friend
        setTimeout(() => {
            const friendSelect = document.getElementById('receiverSelect');
            if (friendSelect) {
                friendSelect.value = friendId;
            }
        }, 100);
    }
};

// View User Profile
window.viewUserProfile = async function(userId) {
    try {
        // Show modal with loading state
        const modal = document.getElementById('profileViewModal');
        const content = document.getElementById('profileViewContent');
        
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        content.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <i class="fas fa-spinner fa-spin" style="font-size: 2rem;"></i>
                <p class="text-muted">Loading profile...</p>
            </div>
        `;
        
        // Fetch profile data
        const response = await apiRequest(`/profile/view/${userId}`);
        
        if (response.status === 403) {
            // Private profile
            const data = await response.json();
            content.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <i class="fas fa-lock" style="font-size: 3rem; color: rgba(255,255,255,0.3); margin-bottom: 1rem;"></i>
                    <h3>${data.username}'s Profile</h3>
                    <p class="text-muted" style="margin-top: 1rem;">This profile is private. Only friends can view it.</p>
                    <p class="text-muted">Send a friend request to connect!</p>
                </div>
            `;
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to load profile');
        }
        
        const profile = await response.json();
        
        // Render profile
        content.innerHTML = `
            <div class="profile-view">
                <div style="text-align: center; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div style="width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 2.5rem; color: white;">
                        ${profile.username.charAt(0).toUpperCase()}
                    </div>
                    <h2 style="margin: 0 0 0.5rem 0;">${profile.username}</h2>
                    ${profile.is_friend ? '<span class="badge" style="background: rgba(102, 126, 234, 0.2); color: #667eea; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.875rem;"><i class="fas fa-user-friends"></i> Friend</span>' : ''}
                    ${profile.bio ? `<p class="text-muted" style="margin-top: 1rem;">${profile.bio}</p>` : ''}
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                    <div class="stat-card" style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${profile.stats.friends_count || 0}</div>
                        <div class="text-muted" style="font-size: 0.875rem;">Friends</div>
                    </div>
                    <div class="stat-card" style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${profile.stats.public_qr_count || 0}</div>
                        <div class="text-muted" style="font-size: 0.875rem;">Public QR Codes</div>
                    </div>
                    <div class="stat-card" style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${profile.stats.total_qr_shared || 0}</div>
                        <div class="text-muted" style="font-size: 0.875rem;">Total QR Shared</div>
                    </div>
                </div>
                
                <div>
                    <h3 style="margin-bottom: 1rem;"><i class="fas fa-qrcode"></i> Shared QR Codes</h3>
                    ${profile.qr_codes && profile.qr_codes.length > 0 ? `
                        <div id="profileQRList" style="display: grid; gap: 1rem; max-height: 400px; overflow-y: auto;">
                            ${profile.qr_codes.map(qr => `
                                <div class="qr-item" style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                                            <i class="fas fa-${qr.type === 'text' ? 'font' : qr.type === 'file' ? 'file' : 'link'}" style="color: #667eea;"></i>
                                            <strong>${qr.type.charAt(0).toUpperCase() + qr.type.slice(1)}</strong>
                                            ${qr.shared_with_me ? '<span class="badge" style="background: rgba(102, 126, 234, 0.2); color: #667eea; padding: 0.15rem 0.5rem; border-radius: 1rem; font-size: 0.75rem;"><i class="fas fa-share"></i> Shared with you</span>' : ''}
                                            ${qr.is_public ? '<span class="badge" style="background: rgba(76, 175, 80, 0.2); color: #4caf50; padding: 0.15rem 0.5rem; border-radius: 1rem; font-size: 0.75rem;"><i class="fas fa-globe"></i> Public</span>' : ''}
                                        </div>
                                        <div class="text-muted" style="font-size: 0.875rem;">
                                            Created: ${new Date(qr.created_at).toLocaleDateString()}
                                            ${qr.viewed ? ' • <i class="fas fa-eye"></i> Viewed' : ''}
                                            ${qr.view_count > 0 ? ` • ${qr.view_count} views` : ''}
                                        </div>
                                    </div>
                                    ${qr.shared_with_me ? `
                                        <button onclick="viewQRContent('${qr.content_id}')" class="btn btn-sm btn-primary">
                                            <i class="fas fa-eye"></i> View
                                        </button>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : '<p class="text-muted text-center" style="padding: 2rem;">No QR codes to display</p>'}
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error viewing profile:', error);
        const content = document.getElementById('profileViewContent');
        content.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <i class="fas fa-exclamation-circle" style="font-size: 3rem; color: #f44336; margin-bottom: 1rem;"></i>
                <h3>Error Loading Profile</h3>
                <p class="text-muted">${error.message}</p>
            </div>
        `;
    }
};

// Close Profile Modal
window.closeProfileModal = function() {
    const modal = document.getElementById('profileViewModal');
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
};

// View QR Content from profile
window.viewQRContent = function(contentId) {
    // Close profile modal and navigate to received QR section
    closeProfileModal();
    
    // Navigate to received section
    const receivedTab = document.querySelector('[data-section="received"]');
    if (receivedTab) {
        receivedTab.click();
    }
    
    // Highlight the QR code
    setTimeout(() => {
        const qrElement = document.querySelector(`[data-content-id="${contentId}"]`);
        if (qrElement) {
            qrElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            qrElement.style.boxShadow = '0 0 0 3px #667eea';
            setTimeout(() => {
                qrElement.style.boxShadow = '';
            }, 2000);
        }
    }, 300);
};
