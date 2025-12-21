// Profile Management Functions

// Load user profile
async function loadUserProfile() {
    try {
        console.log('Loading user profile...');
        const response = await apiRequest('/profile');
        console.log('Profile response:', response);
        
        if (response.ok) {
            const profile = await response.json();
            console.log('Profile data:', profile);
            displayUserProfile(profile);
            return profile;
        } else {
            const error = await response.json();
            console.error('Profile load error:', error);
        }
    } catch (error) {
        console.error('Failed to load profile:', error);
    }
}

// Display user profile
function displayUserProfile(profile) {
    console.log('Displaying profile:', profile);
    
    // Update profile name and contact
    const profileName = document.getElementById('profileName');
    const profileEmail = document.getElementById('profileEmail');
    const profilePhone = document.getElementById('profilePhone');
    
    if (profileName) profileName.textContent = profile.username;
    if (profileEmail && profile.email) profileEmail.textContent = profile.email;
    if (profilePhone && profile.phone) profilePhone.textContent = profile.phone;
    
    // Update profile picture
    updateProfilePicture(profile.profile_pic_url, profile.username);
    
    // Update bio and status
    const profileBio = document.getElementById('profileBio');
    const profileStatus = document.getElementById('profileStatus');
    
    if (profileBio) profileBio.value = profile.bio || '';
    if (profileStatus) profileStatus.value = profile.status || '';
    
    // Update stats
    console.log('=== PROFILE STATS DEBUG ===');
    console.log('Full profile object:', JSON.stringify(profile, null, 2));
    console.log('Profile stats object:', profile.stats);
    console.log('Stats keys:', profile.stats ? Object.keys(profile.stats) : 'No stats');
    
    const friendsCount = document.getElementById('profileFriendsCount');
    const sharesCount = document.getElementById('profileSharesCount');
    const scansCount = document.getElementById('profileScansCount');
    
    console.log('DOM Elements found:');
    console.log('- friendsCount:', friendsCount);
    console.log('- sharesCount:', sharesCount);
    console.log('- scansCount:', scansCount);
    
    if (profile.stats) {
        console.log('Stats values:');
        console.log('- friends_count:', profile.stats.friends_count);
        console.log('- total_shares:', profile.stats.total_shares);
        console.log('- content_shared:', profile.stats.content_shared);
        console.log('- total_scans:', profile.stats.total_scans);
        
        if (friendsCount) {
            const count = profile.stats.friends_count || 0;
            friendsCount.textContent = count;
            console.log('✓ Set friends count to:', count);
        }
        if (sharesCount) {
            const count = profile.stats.content_shared || profile.stats.total_shares || 0;
            sharesCount.textContent = count;
            console.log('✓ Set shares count to:', count);
        }
        if (scansCount) {
            const count = profile.stats.total_scans || 0;
            scansCount.textContent = count;
            console.log('✓ Set scans count to:', count);
        }
    } else {
        console.warn('⚠ No stats found in profile object');
        // Set to 0 if no stats
        if (friendsCount) friendsCount.textContent = '0';
        if (sharesCount) sharesCount.textContent = '0';
        if (scansCount) scansCount.textContent = '0';
    }
    console.log('=== END STATS DEBUG ===');
    
    // Update settings
    if (profile.settings) {
        const privacySelect = document.getElementById('profilePrivacy');
        const themeSelect = document.getElementById('profileTheme');
        const allowFriendRequests = document.getElementById('allowFriendRequests');
        const showOnlineStatus = document.getElementById('showOnlineStatus');
        const enableNotifications = document.getElementById('enableNotifications');
        
        if (privacySelect) privacySelect.value = profile.settings.privacy || 'friends_only';
        if (themeSelect) themeSelect.value = profile.settings.theme || 'dark';
        if (allowFriendRequests) allowFriendRequests.checked = profile.settings.allow_friend_requests !== false;
        if (showOnlineStatus) showOnlineStatus.checked = profile.settings.show_online_status !== false;
        if (enableNotifications) enableNotifications.checked = profile.settings.notifications !== false;
    }
}

// Update profile picture display
function updateProfilePicture(url, username) {
    const profilePictureImg = document.getElementById('profilePictureImg');
    const profileAvatarText = document.getElementById('profileAvatarText');
    const userAvatar = document.getElementById('userAvatar');
    
    if (url && profilePictureImg) {
        profilePictureImg.src = url;
        profilePictureImg.classList.remove('hidden');
        if (profileAvatarText) profileAvatarText.classList.add('hidden');
    } else if (profileAvatarText && username) {
        profileAvatarText.textContent = username.charAt(0).toUpperCase();
        profileAvatarText.classList.remove('hidden');
        if (profilePictureImg) profilePictureImg.classList.add('hidden');
    }
    
    // Update header avatar
    if (userAvatar && username) {
        userAvatar.textContent = username.charAt(0).toUpperCase();
    }
}

// Upload profile picture
async function uploadProfilePicture(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        console.log('Uploading profile picture...');
        const response = await apiRequest('/profile/upload-picture', {
            method: 'POST',
            body: formData,
            skipContentType: true
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Profile picture updated successfully!');
            
            // Update the display
            updateProfilePicture(data.profile_pic_url, (window.state && window.state.user) ? window.state.user.username : 'User');
            
            // Reload full profile to get updated data
            await loadUserProfile();
            
            // Refresh activity feed
            if (typeof refreshActivityFeed !== 'undefined') {
                refreshActivityFeed();
            }
            
            return data;
        } else {
            showError(data.error || 'Failed to upload profile picture');
        }
    } catch (error) {
        showError('Failed to upload profile picture');
        console.error(error);
    }
}

// Update bio and status
async function updateBioStatus() {
    try {
        const bio = document.getElementById('profileBio').value.trim();
        const status = document.getElementById('profileStatus').value.trim();
        
        const response = await apiRequest('/profile/update', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ bio, status })
        });
        
        if (response.ok) {
            showSuccess('Profile updated successfully!');
            
            // Refresh activity feed
            if (typeof refreshActivityFeed !== 'undefined') {
                refreshActivityFeed();
            }
        } else {
            const data = await response.json();
            showError(data.error || 'Failed to update profile');
        }
    } catch (error) {
        showError('Failed to update profile');
        console.error(error);
    }
}

// Update privacy settings
async function updatePrivacySettings() {
    try {
        const privacy = document.getElementById('profilePrivacy').value;
        const allowFriendRequests = document.getElementById('allowFriendRequests').checked;
        const showOnlineStatus = document.getElementById('showOnlineStatus').checked;
        const notifications = document.getElementById('enableNotifications').checked;
        
        const response = await apiRequest('/profile/update', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                settings: {
                    privacy,
                    allow_friend_requests: allowFriendRequests,
                    show_online_status: showOnlineStatus,
                    notifications
                }
            })
        });
        
        if (response.ok) {
            showSuccess('Privacy settings updated successfully!');
        } else {
            const data = await response.json();
            showError(data.error || 'Failed to update privacy settings');
        }
    } catch (error) {
        showError('Failed to update privacy settings');
        console.error(error);
    }
}

// Update theme
async function updateTheme() {
    try {
        const theme = document.getElementById('profileTheme').value;
        
        const response = await apiRequest('/profile/update', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                settings: { theme }
            })
        });
        
        if (response.ok) {
            showSuccess('Theme updated successfully!');
            // TODO: Apply theme to UI
            applyTheme(theme);
        } else {
            const data = await response.json();
            showError(data.error || 'Failed to update theme');
        }
    } catch (error) {
        showError('Failed to update theme');
        console.error(error);
    }
}

// Apply theme to UI
function applyTheme(theme) {
    const body = document.body;
    const root = document.documentElement;
    
    // Remove existing theme classes
    body.classList.remove('theme-light', 'theme-dark');
    
    // Apply theme
    if (theme === 'light') {
        body.classList.add('theme-light');
        root.style.setProperty('--primary-color', '#4361ee');
        root.style.setProperty('--dark-bg', '#f5f5f5');
        root.style.setProperty('--card-bg', '#ffffff');
        root.style.setProperty('--text-color', '#1a1a1a');
        root.style.setProperty('--text-muted', '#666666');
        root.style.setProperty('--border-color', '#e0e0e0');
        root.style.setProperty('--hover-bg', '#f0f0f0');
    } else if (theme === 'dark') {
        body.classList.add('theme-dark');
        root.style.setProperty('--primary-color', '#4361ee');
        root.style.setProperty('--dark-bg', '#0d1117');
        root.style.setProperty('--card-bg', '#161b22');
        root.style.setProperty('--text-color', '#e6edf3');
        root.style.setProperty('--text-muted', '#8b949e');
        root.style.setProperty('--border-color', '#30363d');
        root.style.setProperty('--hover-bg', '#21262d');
    } else if (theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyTheme(prefersDark ? 'dark' : 'light');
        return;
    }
    
    // Store in localStorage
    localStorage.setItem('theme', theme);
    
    // Update body attribute for CSS targeting
    body.setAttribute('data-theme', theme);
    
    console.log('Theme applied:', theme);
}

// Setup profile event listeners
function setupProfileEventListeners() {
    // Profile picture upload
    const profilePictureInput = document.getElementById('profilePictureInput');
    if (profilePictureInput) {
        profilePictureInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                // Validate file size (5MB max)
                if (file.size > 5 * 1024 * 1024) {
                    showError('File too large. Maximum size is 5MB');
                    return;
                }
                
                // Validate file type
                const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    showError('Invalid file type. Please upload PNG, JPG, GIF, or WEBP');
                    return;
                }
                
                await uploadProfilePicture(file);
            }
        });
    }
    
    // Update bio button
    const updateBioBtn = document.getElementById('updateBioBtn');
    if (updateBioBtn) {
        updateBioBtn.addEventListener('click', updateBioStatus);
    }
    
    // Update privacy button
    const updatePrivacyBtn = document.getElementById('updatePrivacyBtn');
    if (updatePrivacyBtn) {
        updatePrivacyBtn.addEventListener('click', updatePrivacySettings);
    }
    
    // Update theme button
    const updateThemeBtn = document.getElementById('updateThemeBtn');
    if (updateThemeBtn) {
        updateThemeBtn.addEventListener('click', updateTheme);
    }
}

// Initialize profile page
function initProfilePage() {
    loadUserProfile();
    setupProfileEventListeners();
}

// Export functions
window.loadUserProfile = loadUserProfile;
window.initProfilePage = initProfilePage;
window.updateProfilePicture = updateProfilePicture;
