import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Database
DB_PATH = os.path.join(DATA_DIR, "kyc_database.db")

# Thresholds
FACE_MATCH_THRESHOLD = 0.40  # Cosine similarity
FRAUD_PROBABILITY_THRESHOLD = 0.75

# Create dirs if not exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
