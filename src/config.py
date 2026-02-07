import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), "doc_verification", "static")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "doc_verification", "uploads")

# Database
DB_PATH = os.path.join(DATA_DIR, "kyc_database.db")

# Thresholds
FACE_MATCH_THRESHOLD = 0.80  # Cosine similarity
FRAUD_PROBABILITY_THRESHOLD = 0.75

# Flask Configuration
FLASK_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True,
    'max_content_length': 16 * 1024 * 1024  # 16MB max file size
}

# Create dirs if not exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
