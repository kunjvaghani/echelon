"""
Production-ready Flask REST API for KYC Verification
Provides endpoints for document, face, and behavioral verification.
Runs on port 8501 - Do not use Streamlit with this.
"""

import os
import sys
import uuid
import tempfile
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import cv2

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.face_verification.face_utils import FaceVerifier
from src.doc_verification.doc_utils import DocumentVerifier
from src.behavior_analysis.behavior_utils import BehaviorAnalyzer, SessionAccumulator, BEHAVIOR_SESSIONS

# =============================================================================
# Flask App Configuration
# =============================================================================

app = Flask(__name__)

# Enable CORS for React frontend on port 5173
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# =============================================================================
# Load ML Models Once at Startup
# =============================================================================

print("[INFO] Loading ML models at startup...")
face_verifier = FaceVerifier()
doc_verifier = DocumentVerifier()
behavior_analyzer = BehaviorAnalyzer()

# Initialize Auth Service
from src.auth_service import AuthService
auth_service = AuthService()

print("[INFO] All models and services loaded successfully!")

# =============================================================================
# Helper Functions
# =============================================================================

def allowed_file(filename):
    """Check if file has allowed image extension"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_image_from_file(file):
    """Load image from uploaded file and convert to OpenCV BGR format"""
    try:
        # Read image using PIL
        image = Image.open(file)
        # Convert to RGB (in case of RGBA or other modes)
        image = image.convert('RGB')
        # Convert to numpy array
        image_array = np.array(image)
        # Convert RGB to BGR for OpenCV
        bgr_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        return bgr_image
    except Exception as e:
        print(f"[ERROR] Failed to load image: {e}")
        return None


def save_temp_file(file):
    """Save uploaded file to temp directory and return path"""
    try:
        temp_dir = tempfile.gettempdir()
        filename = f"kyc_{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)
        return filepath
    except Exception as e:
        print(f"[ERROR] Failed to save temp file: {e}")
        return None


def cleanup_temp_file(filepath):
    """Remove temporary file"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"[WARNING] Failed to cleanup temp file: {e}")


# =============================================================================
# API Endpoints
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "status": "healthy",
        "message": "KYC API is running"
    }), 200


@app.route('/api/behavior', methods=['POST'])
def analyze_behavior():
    """
    Behavioral analysis endpoint.
    Accepts JSON: { session_id: string, events: array }
    Returns risk score and decision.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        session_id = data.get('session_id')
        events = data.get('events', [])
        
        if not session_id:
            return jsonify({
                "success": False,
                "error": "session_id is required"
            }), 400
        
        # Add events to session accumulator
        if session_id not in BEHAVIOR_SESSIONS:
            BEHAVIOR_SESSIONS[session_id] = SessionAccumulator()
        
        BEHAVIOR_SESSIONS[session_id].add_events(events)
        
        # Calculate risk score
        risk_score, decision, reasons = behavior_analyzer.calculate_risk_score(session_id)
        
        return jsonify({
            "success": True,
            "risk_score": round(risk_score, 3),
            "decision": decision,
            "reasons": reasons,
            "events_processed": len(events)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Behavior analysis failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/document-verify', methods=['POST'])
def verify_document():
    """
    Document verification endpoint.
    Accepts FormData with 'image' file.
    Optionally accepts 'user_data' JSON for content validation.
    Returns quality, forgery, OCR results and decision.
    """
    try:
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "error": "No image file provided. Use 'image' field in FormData."
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "Invalid file type. Allowed: png, jpg, jpeg, gif, bmp, webp"
            }), 400
        
        # Load image
        image = load_image_from_file(file)
        
        if image is None:
            return jsonify({
                "success": False,
                "error": "Failed to process image"
            }), 400
        
        # Get optional user data for validation
        user_data = None
        if 'user_data' in request.form:
            import json
            try:
                user_data = json.loads(request.form['user_data'])
            except json.JSONDecodeError:
                pass
        
        # Run document verification
        result = doc_verifier.verify_document(image, user_data)
        
        return jsonify({
            "success": True,
            "quality_score": result['scores'].get('quality_score', 0),
            "forgery_score": result['scores'].get('forgery_score', 0),
            "ocr_data": result['details'].get('ocr', {}).get('extracted_data', {}),
            "decision": result['decision'],
            "status": result['status'],
            "risk_score": result['doc_risk_score'],
            "flags": result['flags']
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Document verification failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/face-verify', methods=['POST'])
def verify_face():
    """
    Face verification endpoint.
    Accepts FormData with 'image' file.
    Optionally accepts 'email' to compare with stored embedding from database.
    Returns liveness, embedding, face match score, and verification decision.
    """
    try:
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({
                "success": False,
                "error": "No image file provided. Use 'image' field in FormData."
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "No file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "Invalid file type. Allowed: png, jpg, jpeg, gif, bmp, webp"
            }), 400
        
        # Load image
        image = load_image_from_file(file)
        
        if image is None:
            return jsonify({
                "success": False,
                "error": "Failed to process image"
            }), 400
        
        # Detect face
        face_crop = face_verifier.detect_face(image)
        
        if face_crop is None:
            return jsonify({
                "success": False,
                "error": "No face detected in image",
                "face_detected": False
            }), 200
        
        # Liveness check
        is_live, liveness_confidence = face_verifier.check_liveness(face_crop)
        
        # Generate embedding
        embedding = face_verifier.get_embedding(face_crop)
        
        response = {
            "success": True,
            "face_detected": True,
            "is_live": bool(is_live),
            "liveness_confidence": float(round(liveness_confidence, 3)),
            "embedding": embedding.tolist() if embedding is not None else None,
            "face_match_score": None,
            "face_match_decision": None
        }
        
        # Get user email for DB lookup
        user_email = request.form.get('email')
        
        # Try to get stored embedding from database if email provided
        if user_email and embedding is not None:
            try:
                user = auth_service.db.users.find_one({"email": user_email})
                if user and user.get('face_embedding'):
                    stored_embedding = np.array(user['face_embedding'], dtype=np.float32)
                    similarity, match_decision = face_verifier.verify_with_stored_embedding(embedding, stored_embedding)
                    response['face_match_score'] = float(round(similarity, 3))
                    response['face_match_decision'] = match_decision
                    response['has_stored_embedding'] = True
                    print(f"[INFO] Face match for {user_email}: similarity={similarity:.3f}, decision={match_decision}")
                else:
                    response['has_stored_embedding'] = False
                    response['face_match_note'] = 'No stored embedding found - this is first KYC'
            except Exception as db_error:
                print(f"[WARNING] Could not retrieve stored embedding: {db_error}")
                response['face_match_error'] = str(db_error)
        
        # Also support manual stored_embedding for backward compatibility
        stored_embedding_json = request.form.get('stored_embedding')
        if stored_embedding_json and embedding is not None and not response.get('face_match_score'):
            import json
            try:
                stored_embedding = np.array(json.loads(stored_embedding_json), dtype=np.float32)
                similarity, decision = face_verifier.verify_with_stored_embedding(embedding, stored_embedding)
                response['face_match_score'] = float(round(similarity, 3))
                response['face_match_decision'] = decision
            except (json.JSONDecodeError, ValueError) as e:
                response['face_match_error'] = f"Invalid stored_embedding format: {e}"
        
        # Overall decision based on liveness and face match
        if not is_live:
            response['decision'] = 'REJECTED'
            response['reason'] = 'Liveness check failed - possible spoof detected'
        elif embedding is None:
            response['decision'] = 'MANUAL_REVIEW'
            response['reason'] = 'Could not generate face embedding'
        elif response.get('face_match_decision') == 'REJECTED':
            response['decision'] = 'REJECTED'
            response['reason'] = 'Face does not match stored identity'
        elif response.get('face_match_decision') == 'MANUAL_REVIEW':
            response['decision'] = 'MANUAL_REVIEW'
            response['reason'] = 'Face match inconclusive - requires manual verification'
        else:
            response['decision'] = 'PASSED'
            response['reason'] = 'Face verified successfully'
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"[ERROR] Face verification failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/kyc-score', methods=['POST'])
def calculate_kyc_score():
    """
    Final KYC decision endpoint.
    Accepts JSON with scores from all verification phases.
    Returns final aggregated decision.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Extract scores (all should be 0.0 to 1.0, where lower is better for risk)
        doc_score = data.get('doc_score', 0.5)  # Document risk score
        face_score = data.get('face_score', 0.5)  # Face risk score (1 - liveness_confidence)
        behavior_score = data.get('behavior_score', 0.5)  # Behavioral risk score
        
        # Weights for final score
        WEIGHTS = {
            'document': 0.35,
            'face': 0.40,
            'behavior': 0.25
        }
        
        # Calculate weighted final risk score
        final_risk_score = (
            doc_score * WEIGHTS['document'] +
            face_score * WEIGHTS['face'] +
            behavior_score * WEIGHTS['behavior']
        )
        
        # Decision thresholds
        if final_risk_score < 0.30:
            decision = 'APPROVED'
            status = 'success'
            message = 'Identity verified successfully. All checks passed.'
        elif final_risk_score < 0.55:
            decision = 'MANUAL_REVIEW'
            status = 'pending'
            message = 'Some verification checks require human review.'
        else:
            decision = 'REJECTED'
            status = 'failed'
            message = 'Identity verification failed due to high risk indicators.'
        
        return jsonify({
            "success": True,
            "final_risk_score": round(final_risk_score, 3),
            "decision": decision,
            "status": status,
            "message": message,
            "breakdown": {
                "document": round(doc_score, 3),
                "face": round(face_score, 3),
                "behavior": round(behavior_score, 3)
            },
            "weights": WEIGHTS
        }), 200
        
    except Exception as e:
        print(f"[ERROR] KYC score calculation failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/update-user-kyc', methods=['POST'])
def update_user_kyc():
    """
    Update user KYC data after successful verification.
    Stores face embedding and KYC scores in database.
    Accepts JSON: { email, face_embedding, kyc_data }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        email = data.get('email')
        face_embedding = data.get('face_embedding')
        kyc_data = data.get('kyc_data', {})
        
        if not email:
            return jsonify({
                "success": False,
                "error": "Email is required"
            }), 400
        
        # Update user with face embedding and KYC data
        update_data = {}
        
        if face_embedding:
            # Store embedding as list (MongoDB compatible)
            update_data['face_embedding'] = face_embedding
        
        if kyc_data:
            update_data['kyc_scores'] = kyc_data.get('scores', {})
            update_data['kyc_decision'] = kyc_data.get('decision', 'PENDING')
            update_data['kyc_completed'] = True
        
        if update_data:
            from datetime import datetime
            update_data['kyc_completed_at'] = datetime.now()
            
            # Use the database from auth_service
            result = auth_service.db.users.update_one(
                {"email": email},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return jsonify({
                    "success": True,
                    "message": "KYC data updated successfully"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "User not found or no changes made"
                }), 400
        
        return jsonify({
            "success": False,
            "error": "No data to update"
        }), 400
        
    except Exception as e:
        print(f"[ERROR] Update user KYC failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =============================================================================
# Authentication Endpoints
# =============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """
    Register a new user.
    Accepts JSON: { email, password, full_name, ... }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        success, msg = auth_service.register_user(data)
        return jsonify({
            "success": success,
            "message": msg
        }), 200 if success else 400
        
    except Exception as e:
        print(f"[ERROR] Registration failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/login/send-otp', methods=['POST'])
def login_send_otp():
    """
    Send OTP to registered email for login.
    Accepts JSON: { email: string }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                "success": False,
                "error": "Email is required"
            }), 400
        
        success, msg = auth_service.send_login_otp(email)
        
        return jsonify({
            "success": success,
            "message": msg
        }), 200 if success else 400
        
    except Exception as e:
        print(f"[ERROR] Send OTP failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/login/verify-otp', methods=['POST'])
def login_verify_otp():
    """
    Verify OTP and login user.
    Accepts JSON: { email: string, otp: string }
    Returns user data on success.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({
                "success": False,
                "error": "Email and OTP are required"
            }), 400
        
        success, msg, user = auth_service.verify_login_otp(email, otp)
        
        if success and user:
            return jsonify({
                "success": True,
                "message": msg,
                "user": {
                    "email": user.get('email'),
                    "full_name": user.get('full_name'),
                    "is_verified": user.get('is_verified', False)
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": msg
            }), 400
        
    except Exception as e:
        print(f"[ERROR] Verify OTP failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("KYC Verification API Server")
    print("=" * 60)
    print(f"Server running at: http://localhost:8501")
    print(f"CORS enabled for: http://localhost:5173")
    print("=" * 60)
    print("Available endpoints:")
    print("  GET  /api/health           - Health check")
    print("  POST /api/behavior         - Behavioral analysis")
    print("  POST /api/document-verify  - Document verification")
    print("  POST /api/face-verify      - Face verification")
    print("  POST /api/kyc-score        - Final KYC decision")
    print("  POST /api/update-user-kyc  - Store KYC data + face embedding")
    print("  POST /api/register         - User registration")
    print("  POST /api/login/send-otp   - Send login OTP")
    print("  POST /api/login/verify-otp - Verify OTP and login")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8501, debug=False, use_reloader=False)

