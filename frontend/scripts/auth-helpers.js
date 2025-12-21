// Helper functions for auth form switching
window.showRegister = function() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('registerForm').classList.remove('hidden');
};

window.showLoginForm = function() {
    document.getElementById('registerForm').classList.add('hidden');
    document.getElementById('loginForm').classList.remove('hidden');
};

// Initialize toggle buttons for email/phone authentication
document.addEventListener('DOMContentLoaded', () => {
    // Login form toggles
    const loginToggles = document.querySelectorAll('#loginForm .toggle-btn');
    loginToggles.forEach(btn => {
        btn.addEventListener('click', function() {
            const mode = this.dataset.mode;
            
            // Update active state
            loginToggles.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide fields
            const emailGroup = document.getElementById('loginEmailGroup');
            const phoneGroup = document.getElementById('loginPhoneGroup');
            const emailInput = document.getElementById('loginEmail');
            const phoneInput = document.getElementById('loginPhone');
            
            if (mode === 'email') {
                emailGroup.classList.remove('hidden');
                phoneGroup.classList.add('hidden');
                emailInput.setAttribute('required', 'required');
                phoneInput.removeAttribute('required');
                phoneInput.value = '';
            } else {
                emailGroup.classList.add('hidden');
                phoneGroup.classList.remove('hidden');
                phoneInput.setAttribute('required', 'required');
                emailInput.removeAttribute('required');
                emailInput.value = '';
            }
        });
    });
    
    // Register form toggles
    const registerToggles = document.querySelectorAll('#registerForm .toggle-btn');
    registerToggles.forEach(btn => {
        btn.addEventListener('click', function() {
            const mode = this.dataset.mode;
            
            // Update active state
            registerToggles.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Show/hide fields
            const emailGroup = document.getElementById('registerEmailGroup');
            const phoneGroup = document.getElementById('registerPhoneGroup');
            const emailInput = document.getElementById('registerEmail');
            const phoneInput = document.getElementById('registerPhone');
            
            if (mode === 'email') {
                emailGroup.classList.remove('hidden');
                phoneGroup.classList.add('hidden');
                emailInput.setAttribute('required', 'required');
                phoneInput.removeAttribute('required');
                phoneInput.value = '';
            } else {
                emailGroup.classList.add('hidden');
                phoneGroup.classList.remove('hidden');
                phoneInput.setAttribute('required', 'required');
                emailInput.removeAttribute('required');
                emailInput.value = '';
            }
        });
    });
});
