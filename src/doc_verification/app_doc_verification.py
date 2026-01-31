"""
Flask API for Phase 3: Document Verification
=============================================
Endpoints:
- POST /verify-document: Complete document verification
- GET /health: Health check
"""

import os
import sys
import uuid
import json
from flask import Flask, request, jsonify, send_from_directory
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from werkzeug.utils import secure_filename
import cv2
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import FLASK_CONFIG, UPLOAD_FOLDER, STATIC_FOLDER
from doc_verification import DocumentVerifier


class NumpyJSONProvider(DefaultJSONProvider):
    """Custom JSON provider to handle numpy types"""
    def default(self, o):
        if isinstance(o, (np.bool_, np.integer, np.floating)):
            return o.item()
        elif isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)

# Initialize Flask app
app = Flask(__name__, 
            static_folder=STATIC_FOLDER,
            template_folder=STATIC_FOLDER)

# Set custom JSON provider
app.json = NumpyJSONProvider(app)
CORS(app)

# Configure upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = FLASK_CONFIG['max_content_length']

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Create upload folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Initialize verifier
verifier = DocumentVerifier()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory(STATIC_FOLDER, 'index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Phase 3 Document Verification',
        'version': '1.0.0'
    })


@app.route('/verify-document', methods=['POST'])
def verify_document():
    """
    Main document verification endpoint
    
    Request:
    - document: Image file (required)
    - user_name: User's name (optional)
    - user_dob: User's DOB in YYYY-MM-DD (optional)
    - user_id_number: User's ID number (optional)
    
    Response:
    - JSON with verification results
    """
    # Check if file was uploaded
    if 'document' not in request.files:
        return jsonify({
            'error': 'No document file provided',
            'message': 'Please upload a document image'
        }), 400
    
    file = request.files['document']
    
    if file.filename == '':
        return jsonify({
            'error': 'No file selected',
            'message': 'Please select a document image'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Invalid file type',
            'message': f'Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read image
        image = cv2.imread(filepath)
        if image is None:
            return jsonify({
                'error': 'Could not read image',
                'message': 'The uploaded file could not be read as an image'
            }), 400
        
        # Get user data from form
        user_data = None
        if any(key in request.form for key in ['user_name', 'user_dob', 'user_id_number']):
            user_data = {
                'name': request.form.get('user_name', ''),
                'dob': request.form.get('user_dob', ''),
                'id_number': request.form.get('user_id_number', '')
            }
        
        # Run verification
        result = verifier.verify_document(image, user_data)
        
        # Clean up - delete uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)
    
    except Exception as e:
        # Clean up on error
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'error': 'Verification failed',
            'message': str(e)
        }), 500


@app.route('/verify-base64', methods=['POST'])
def verify_base64():
    """
    Alternative endpoint accepting base64 encoded image
    
    Request JSON:
    {
        "image": "base64_encoded_image_data",
        "user_name": "John Doe",
        "user_dob": "1990-01-15",
        "user_id_number": "ABCDE1234F"
    }
    """
    import base64
    
    data = request.get_json()
    
    if not data or 'image' not in data:
        return jsonify({
            'error': 'No image data provided',
            'message': 'Please provide base64 encoded image'
        }), 400
    
    try:
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:  # Handle data URL format
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({
                'error': 'Could not decode image',
                'message': 'Invalid base64 image data'
            }), 400
        
        # Get user data
        user_data = None
        if any(key in data for key in ['user_name', 'user_dob', 'user_id_number']):
            user_data = {
                'name': data.get('user_name', ''),
                'dob': data.get('user_dob', ''),
                'id_number': data.get('user_id_number', '')
            }
        
        # Run verification
        result = verifier.verify_document(image, user_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': 'Verification failed',
            'message': str(e)
        }), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large',
        'message': 'Maximum file size is 16MB'
    }), 413


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🔒 PHASE 3: DOCUMENT VERIFICATION API")
    print("="*50)
    print(f"📍 Running on: http://localhost:{FLASK_CONFIG['port']}")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print("="*50 + "\n")
    
    app.run(
        host=FLASK_CONFIG['host'],
        port=FLASK_CONFIG['port'],
        debug=FLASK_CONFIG['debug']
    )
