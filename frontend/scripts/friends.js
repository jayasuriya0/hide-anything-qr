// Friend Management Functions

async function searchUsers(query) {
    try {
        const response = await apiRequest(`/friends/search?q=${encodeURIComponent(query)}`);
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

window.sendFriendRequestTo = async function(userId) {
    try {
        const result = await sendFriendRequest(userId, 'Hello!');
        showSuccess('Friend request sent!');
        if (result.qr_code) {
            generateQRCode(result.qr_code);
        }
    } catch (error) {
        showError(error.message);
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
                    <strong>${friend.username}</strong>
                    <p class="text-muted" style="margin: 0; font-size: 0.9rem;">${friend.email}</p>
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
                        <p class="text-muted" style="margin: 0; font-size: 0.9rem;">${req.sender_email || ''}</p>
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
        userDiv.innerHTML = `
            <div>
                <strong>${user.username}</strong>
                <p class="text-muted" style="margin: 0; font-size: 0.9rem;">${user.email}</p>
            </div>
            <button onclick="sendFriendRequestTo('${user._id}')" class="btn btn-primary">
                <i class="fas fa-user-plus"></i> Add Friend
            </button>
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
            const receiverSelect = document.getElementById('shareReceiver') || document.getElementById('fileReceiver');
            if (receiverSelect) {
                receiverSelect.value = friendId;
            }
            localStorage.removeItem('selectedFriendId');
        }, 100);
    }
};

