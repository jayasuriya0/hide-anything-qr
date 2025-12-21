// Settings Management
console.log('Settings.js module loaded');

// Get API base URL
function getApiUrl() {
    return window.API_BASE_URL || 'http://127.0.0.1:5000/api';
}

// Initialize Settings Page
async function initSettingsPage() {
    console.log('Initializing Settings page...');
    await loadUserSettings();
    setupSettingsListeners();
}

// Load user settings
async function loadUserSettings() {
    try {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const apiUrl = getApiUrl();
        
        const response = await fetch(`${apiUrl}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            
            // Populate account settings
            document.getElementById('settingsUsername').value = user.username || '';
            document.getElementById('settingsEmail').value = user.email || '';
            document.getElementById('settingsPhone').value = user.phone || '';
            
            // Populate other settings from user.settings
            const settings = user.settings || {};
            
            // QR Defaults
            document.getElementById('defaultEncryption').value = settings.default_encryption || 'standard';
            document.getElementById('defaultExpiration').value = settings.default_expiration || '0';
            document.getElementById('autoDeleteExpired').checked = settings.auto_delete_expired || false;
            
            // Notifications
            document.getElementById('notifyNewContent').checked = settings.notify_new_content !== false;
            document.getElementById('notifyQRScanned').checked = settings.notify_qr_scanned !== false;
            document.getElementById('notifyFriendRequest').checked = settings.notify_friend_request !== false;
            document.getElementById('emailNotifications').checked = settings.email_notifications || false;
            
            // Calculate storage (mock for now)
            calculateStorage();
        }
    } catch (error) {
        console.error('Error loading settings:', error);
        showError('Failed to load settings');
    }
}

// Setup event listeners
function setupSettingsListeners() {
    // Update Account
    const updateAccountBtn = document.getElementById('updateAccountBtn');
    if (updateAccountBtn) {
        updateAccountBtn.addEventListener('click', updateAccount);
    }
    
    // Change Password
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', changePassword);
    }
    
    // Update QR Defaults
    const updateQRDefaultsBtn = document.getElementById('updateQRDefaultsBtn');
    if (updateQRDefaultsBtn) {
        updateQRDefaultsBtn.addEventListener('click', updateQRDefaults);
    }
    
    // Update Notifications
    const updateNotificationsBtn = document.getElementById('updateNotificationsBtn');
    if (updateNotificationsBtn) {
        updateNotificationsBtn.addEventListener('click', updateNotifications);
    }
    
    // Clear Expired
    const clearExpiredBtn = document.getElementById('clearExpiredBtn');
    if (clearExpiredBtn) {
        clearExpiredBtn.addEventListener('click', clearExpiredContent);
    }
    
    // Clear Inactive
    const clearInactiveBtn = document.getElementById('clearInactiveBtn');
    if (clearInactiveBtn) {
        clearInactiveBtn.addEventListener('click', clearInactiveContent);
    }
    
    // Delete All QR
    const deleteAllQRBtn = document.getElementById('deleteAllQRBtn');
    if (deleteAllQRBtn) {
        deleteAllQRBtn.addEventListener('click', deleteAllQR);
    }
    
    // Delete Account
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', deleteAccount);
    }
}

// Update Account
async function updateAccount() {
    try {
        const email = document.getElementById('settingsEmail').value;
        const phone = document.getElementById('settingsPhone').value;
        
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const apiUrl = getApiUrl();
        
        const response = await fetch(`${apiUrl}/auth/update-profile`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, phone })
        });
        
        if (response.ok) {
            showSuccess('Account updated successfully');
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update account');
        }
    } catch (error) {
        showError(error.message);
    }
}

// Change Password
async function changePassword() {
    try {
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        if (!currentPassword || !newPassword || !confirmPassword) {
            showError('Please fill all password fields');
            return;
        }
        
        if (newPassword !== confirmPassword) {
            showError('New passwords do not match');
            return;
        }
        
        if (newPassword.length < 8) {
            showError('Password must be at least 8 characters');
            return;
        }
        
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const apiUrl = getApiUrl();
        
        const response = await fetch(`${apiUrl}/auth/change-password`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        
        if (response.ok) {
            showSuccess('Password changed successfully');
            // Clear password fields
            document.getElementById('currentPassword').value = '';
            document.getElementById('newPassword').value = '';
            document.getElementById('confirmPassword').value = '';
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to change password');
        }
    } catch (error) {
        showError(error.message);
    }
}

// Update QR Defaults
async function updateQRDefaults() {
    try {
        const settings = {
            default_encryption: document.getElementById('defaultEncryption').value,
            default_expiration: parseInt(document.getElementById('defaultExpiration').value),
            auto_delete_expired: document.getElementById('autoDeleteExpired').checked
        };
        
        await updateSettings(settings);
        showSuccess('QR defaults updated successfully');
    } catch (error) {
        showError(error.message);
    }
}

// Update Notifications
async function updateNotifications() {
    try {
        const settings = {
            notify_new_content: document.getElementById('notifyNewContent').checked,
            notify_qr_scanned: document.getElementById('notifyQRScanned').checked,
            notify_friend_request: document.getElementById('notifyFriendRequest').checked,
            email_notifications: document.getElementById('emailNotifications').checked
        };
        
        await updateSettings(settings);
        showSuccess('Notification settings updated successfully');
    } catch (error) {
        showError(error.message);
    }
}

// Update Settings (generic)
async function updateSettings(settings) {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const apiUrl = getApiUrl();
    
    const response = await fetch(`${apiUrl}/auth/update-settings`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ settings })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to update settings');
    }
}

// Clear Expired Content
async function clearExpiredContent() {
    if (!confirm('Delete all expired QR codes?')) return;
    
    try {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const apiUrl = getApiUrl();
        
        const response = await fetch(`${apiUrl}/content/clear-expired`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            showSuccess(`Deleted ${data.deleted_count} expired QR codes`);
            calculateStorage();
        } else {
            throw new Error('Failed to clear expired content');
        }
    } catch (error) {
        showError(error.message);
    }
}

// Clear Inactive Content
async function clearInactiveContent() {
    if (!confirm('Delete all inactive QR codes? This cannot be undone.')) return;
    
    try {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const apiUrl = getApiUrl();
        
        const response = await fetch(`${apiUrl}/content/clear-inactive`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            showSuccess(`Deleted ${data.deleted_count} inactive QR codes`);
            calculateStorage();
        } else {
            throw new Error('Failed to clear inactive content');
        }
    } catch (error) {
        showError(error.message);
    }
}

// Delete All QR
async function deleteAllQR() {
    const confirmation = prompt('Type "DELETE ALL" to confirm deletion of all your QR codes:');
    if (confirmation !== 'DELETE ALL') {
        showInfo('Deletion cancelled');
        return;
    }
    
    try {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const apiUrl = getApiUrl();
        
        const response = await fetch(`${apiUrl}/content/delete-all`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            showSuccess(`Deleted ${data.deleted_count} QR codes`);
            calculateStorage();
        } else {
            throw new Error('Failed to delete all QR codes');
        }
    } catch (error) {
        showError(error.message);
    }
}

// Delete Account
async function deleteAccount() {
    const confirmation = prompt('Type "DELETE MY ACCOUNT" to permanently delete your account:');
    if (confirmation !== 'DELETE MY ACCOUNT') {
        showInfo('Account deletion cancelled');
        return;
    }
    
    try {
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const apiUrl = getApiUrl();
        
        const response = await fetch(`${apiUrl}/auth/delete-account`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            showSuccess('Account deleted successfully. Logging out...');
            setTimeout(() => {
                localStorage.clear();
                window.location.reload();
            }, 2000);
        } else {
            throw new Error('Failed to delete account');
        }
    } catch (error) {
        showError(error.message);
    }
}

// Calculate Storage (mock implementation)
function calculateStorage() {
    // This would normally fetch from API
    const storageUsed = Math.floor(Math.random() * 50); // Mock: 0-50 MB
    const storageTotal = 100; // MB
    const percentage = (storageUsed / storageTotal) * 100;
    
    document.getElementById('storageUsed').textContent = `${storageUsed} MB / ${storageTotal} MB`;
    document.getElementById('storageBar').style.width = `${percentage}%`;
}

// Notification helpers
function showSuccess(message) {
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, 'success');
    } else {
        console.log('✓', message);
    }
}

function showError(message) {
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, 'error');
    } else {
        console.error('✗', message);
    }
}

function showInfo(message) {
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, 'info');
    } else {
        console.info('ℹ', message);
    }
}

// Make initSettingsPage available globally
window.initSettingsPage = initSettingsPage;
