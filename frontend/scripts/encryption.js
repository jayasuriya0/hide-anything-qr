// Client-side Encryption Utilities

// Generate a shared key (simplified - in real app, use proper key exchange)
async function generateSharedKey() {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

// Generate AES key for content encryption
async function generateAESKey() {
    const key = await crypto.subtle.generateKey(
        {
            name: "AES-GCM",
            length: 256
        },
        true,
        ["encrypt", "decrypt"]
    );
    return key;
}

// Encrypt data with AES-GCM
async function encryptData(data, key) {
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encoder = new TextEncoder();
    const encodedData = encoder.encode(data);
    
    const encrypted = await crypto.subtle.encrypt(
        {
            name: "AES-GCM",
            iv: iv
        },
        key,
        encodedData
    );
    
    return {
        iv: Array.from(iv),
        data: Array.from(new Uint8Array(encrypted))
    };
}

// Decrypt data with AES-GCM
async function decryptData(encryptedData, key, iv) {
    const decrypted = await crypto.subtle.decrypt(
        {
            name: "AES-GCM",
            iv: new Uint8Array(iv)
        },
        key,
        new Uint8Array(encryptedData)
    );
    
    const decoder = new TextDecoder();
    return decoder.decode(decrypted);
}

// Convert key to exportable format
async function exportKey(key) {
    const exported = await crypto.subtle.exportKey("raw", key);
    return Array.from(new Uint8Array(exported));
}

// Import key from array
async function importKey(keyData) {
    return await crypto.subtle.importKey(
        "raw",
        new Uint8Array(keyData),
        {
            name: "AES-GCM",
            length: 256
        },
        true,
        ["encrypt", "decrypt"]
    );
}

// Hash data with SHA-256
async function hashData(data) {
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Generate RSA key pair (for demonstration)
async function generateRSAKeyPair() {
    const keyPair = await crypto.subtle.generateKey(
        {
            name: "RSA-OAEP",
            modulusLength: 2048,
            publicExponent: new Uint8Array([1, 0, 1]),
            hash: "SHA-256"
        },
        true,
        ["encrypt", "decrypt"]
    );
    return keyPair;
}

// Export RSA public key
async function exportPublicKey(key) {
    const exported = await crypto.subtle.exportKey("spki", key);
    const exportedAsString = String.fromCharCode.apply(null, new Uint8Array(exported));
    return btoa(exportedAsString);
}

// Import RSA public key
async function importPublicKey(pemKey) {
    const binaryDerString = atob(pemKey);
    const binaryDer = str2ab(binaryDerString);
    
    return await crypto.subtle.importKey(
        "spki",
        binaryDer,
        {
            name: "RSA-OAEP",
            hash: "SHA-256"
        },
        true,
        ["encrypt"]
    );
}

// Encrypt with RSA public key
async function encryptWithPublicKey(data, publicKey) {
    const encoder = new TextEncoder();
    const encodedData = encoder.encode(data);
    
    const encrypted = await crypto.subtle.encrypt(
        {
            name: "RSA-OAEP"
        },
        publicKey,
        encodedData
    );
    
    return Array.from(new Uint8Array(encrypted));
}

// Helper: String to ArrayBuffer
function str2ab(str) {
    const buf = new ArrayBuffer(str.length);
    const bufView = new Uint8Array(buf);
    for (let i = 0; i < str.length; i++) {
        bufView[i] = str.charCodeAt(i);
    }
    return buf;
}

// Helper: ArrayBuffer to Base64
function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

// Helper: Base64 to ArrayBuffer
function base64ToArrayBuffer(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}
