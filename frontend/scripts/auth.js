// Authentication Functions

async function login(email, phone, password) {
    try {
        const body = { password };
        if (email) {
            body.email = email;
        } else if (phone) {
            body.phone = phone;
        }
        
        console.log('Attempting login to:', `${API_BASE_URL}/auth/login`);
        console.log('Login body:', { ...body, password: '***' });
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        
        console.log('Login response status:', response.status);
        const data = await response.json();
        console.log('Login response data:', data);
        
        if (response.ok) {
            state.token = data.access_token;
            state.refreshToken = data.refresh_token;
            state.user = {
                id: data.user_id,
                username: data.username,
                email: data.email,
                phone: data.phone,
                publicKey: data.public_key
            };
            
            localStorage.setItem('access_token', state.token);
            localStorage.setItem('token', state.token);
            localStorage.setItem('refresh_token', state.refreshToken);
            localStorage.setItem('refreshToken', state.refreshToken);
            
            connectWebSocket();
            loadInitialData();
            showDashboard();
            
            return { success: true, data };
        } else {
            return { success: false, error: data.error };
        }
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: `Network error: ${error.message}` };
    }
}

async function register(email, phone, username, password) {
    try {
        const body = { username, password };
        if (email) {
            body.email = email;
        }
        if (phone) {
            body.phone = phone;
        }
        
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return { success: true, data };
        } else {
            return { success: false, error: data.error };
        }
    } catch (error) {
        return { success: false, error: 'Network error' };
    }
}

async function fetchUserData() {
    try {
        const response = await apiRequest('/auth/me');
        if (response.ok) {
            const data = await response.json();
            state.user = data;
            return data;
        } else {
            throw new Error('Failed to fetch user data');
        }
    } catch (error) {
        throw error;
    }
}
