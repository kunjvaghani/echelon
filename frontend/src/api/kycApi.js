/**
 * KYC API Service
 * Centralized API calls to the Flask backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8501';

/**
 * Helper to handle API responses consistently
 */
async function handleResponse(response) {
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || 'API request failed');
    }
    return data;
}

/**
 * Convert base64 data URL to Blob for FormData upload
 */
function dataURLtoBlob(dataURL) {
    if (!dataURL || typeof dataURL !== 'string') {
        throw new Error('Invalid data URL: must be a non-empty string');
    }

    const arr = dataURL.split(',');
    if (arr.length < 2) {
        throw new Error('Invalid data URL format: missing data part');
    }

    const mimeMatch = arr[0].match(/:(.*?);/);
    if (!mimeMatch || !mimeMatch[1]) {
        // Fallback to image/jpeg if mime type cannot be extracted
        console.warn('[KYC API] Could not extract MIME type, defaulting to image/jpeg');
    }
    const mime = mimeMatch ? mimeMatch[1] : 'image/jpeg';

    try {
        const bstr = atob(arr[1]);
        let n = bstr.length;
        const u8arr = new Uint8Array(n);
        while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new Blob([u8arr], { type: mime });
    } catch (e) {
        throw new Error(`Failed to decode image data: ${e.message}`);
    }
}

/**
 * Health check - verify API is running
 */
export async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/api/health`);
        return await handleResponse(response);
    } catch (error) {
        console.error('[KYC API] Health check failed:', error);
        throw error;
    }
}

/**
 * Submit behavioral data for analysis
 * @param {string} sessionId - Unique session identifier
 * @param {Array} events - Array of behavioral events
 * @returns {Promise<{success, risk_score, decision, reasons}>}
 */
export async function submitBehavior(sessionId, events = []) {
    try {
        const response = await fetch(`${API_URL}/api/behavior`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                events: events
            })
        });
        return await handleResponse(response);
    } catch (error) {
        console.error('[KYC API] Behavior submission failed:', error);
        throw error;
    }
}

/**
 * Verify document image (ID card, passport, etc.)
 * @param {File} file - Image file to verify
 * @param {Object} userData - Optional user data for content validation
 * @returns {Promise<{success, quality_score, forgery_score, ocr_data, decision}>}
 */
export async function verifyDocument(file, userData = null) {
    try {
        const formData = new FormData();
        formData.append('image', file);

        if (userData) {
            formData.append('user_data', JSON.stringify(userData));
        }

        const response = await fetch(`${API_URL}/api/document-verify`, {
            method: 'POST',
            body: formData
        });

        return await handleResponse(response);
    } catch (error) {
        console.error('[KYC API] Document verification failed:', error);
        throw error;
    }
}

/**
 * Verify face image (liveness + embedding)
 * @param {string|File} image - Image file or base64 data URL
 * @param {string} email - Optional user email for face matching with stored embedding
 * @param {Array} storedEmbedding - Optional stored embedding for comparison
 * @returns {Promise<{success, face_detected, is_live, embedding, face_match_score, decision}>}
 */
export async function verifyFace(image, email = null, storedEmbedding = null) {
    try {
        const formData = new FormData();

        // Handle both File objects and base64 data URLs
        if (image instanceof File) {
            formData.append('image', image);
        } else if (typeof image === 'string' && image.startsWith('data:')) {
            const blob = dataURLtoBlob(image);
            formData.append('image', blob, 'selfie.jpg');
        } else {
            throw new Error('Invalid image format. Provide File or data URL.');
        }

        // Add email for database lookup of stored embedding
        if (email) {
            formData.append('email', email);
        }

        if (storedEmbedding) {
            formData.append('stored_embedding', JSON.stringify(storedEmbedding));
        }

        const response = await fetch(`${API_URL}/api/face-verify`, {
            method: 'POST',
            body: formData
        });

        return await handleResponse(response);
    } catch (error) {
        console.error('[KYC API] Face verification failed:', error);
        throw error;
    }
}

/**
 * Calculate final KYC score based on all verification results
 * @param {Object} scores - Object with doc_score, face_score, behavior_score
 * @returns {Promise<{success, final_risk_score, decision, status, message}>}
 */
export async function calculateKYCScore(scores) {
    try {
        const response = await fetch(`${API_URL}/api/kyc-score`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(scores)
        });

        return await handleResponse(response);
    } catch (error) {
        console.error('[KYC API] KYC score calculation failed:', error);
        throw error;
    }
}

/**
 * Send OTP to email for login
 * @param {string} email - Registered email address
 * @returns {Promise<{success, message}>}
 */
export async function sendLoginOtp(email) {
    try {
        const response = await fetch(`${API_URL}/api/login/send-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });

        return await handleResponse(response);
    } catch (error) {
        console.error('[KYC API] Send OTP failed:', error);
        throw error;
    }
}

/**
 * Verify OTP and login
 * @param {string} email - Email address
 * @param {string} otp - OTP code
 * @returns {Promise<{success, message, user}>}
 */
export async function verifyLoginOtp(email, otp) {
    try {
        const response = await fetch(`${API_URL}/api/login/verify-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, otp })
        });

        return await handleResponse(response);
    } catch (error) {
        console.error('[KYC API] Verify OTP failed:', error);
        throw error;
    }
}

/**
 * Register a new user
 * @param {Object} userData - User registration data
 * @returns {Promise<{success, message}>}
 */
export async function registerUser(userData) {
    try {
        const response = await fetch(`${API_URL}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        return await handleResponse(response);
    } catch (error) {
        console.error('[KYC API] Registration failed:', error);
        throw error;
    }
}

/**
 * Update user KYC data (face embedding, scores)
 * @param {string} email - User email
 * @param {Array} faceEmbedding - Face embedding array
 * @param {Object} kycData - KYC scores and decision
 * @returns {Promise<{success, message}>}
 */
export async function updateUserKyc(email, faceEmbedding, kycData) {
    try {
        const response = await fetch(`${API_URL}/api/update-user-kyc`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                face_embedding: faceEmbedding,
                kyc_data: kycData
            })
        });

        return await handleResponse(response);
    } catch (error) {
        console.error('[KYC API] Update user KYC failed:', error);
        throw error;
    }
}

// Export API URL for debugging
export { API_URL };


