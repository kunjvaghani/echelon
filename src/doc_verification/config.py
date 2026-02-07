"""
Configuration for Document Verification Module
All thresholds and settings in one place
"""

import os

# =============================================================================
# PATHS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Tesseract path for Windows (update if installed elsewhere)
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# =============================================================================
# QUALITY CHECK THRESHOLDS (OpenCV)
# =============================================================================
QUALITY_CONFIG = {
    'min_resolution': (480, 320),
    'blur_threshold': 50.0,
    'min_brightness': 20,
    'max_brightness': 240,
    'border_threshold': 0.02,
}

# =============================================================================
# FORGERY DETECTION THRESHOLDS
# =============================================================================
FORGERY_CONFIG = {
    'model_name': 'EfficientNetB0',
    'input_size': (224, 224),
    'confidence_threshold': 0.5,
}

# =============================================================================
# OCR CONFIGURATION
# =============================================================================
OCR_CONFIG = {
    'lang': 'eng+hin',  # English + Hindi for Indian documents
    'psm': 6,
    'oem': 3,
}

# =============================================================================
# ID DOCUMENT PATTERNS (Regex)
# =============================================================================
ID_PATTERNS = {
    'aadhaar': r'\b\d{4}\s?\d{4}\s?\d{4}\b',
    'pan': r'\b[A-Z]{5}\d{4}[A-Z]\b',
    'passport': r'\b[A-Z]\d{7}\b',
    'driving_license': r'\b[A-Z]{2}\d{2}\s?\d{11}\b',
    'voter_id': r'\b[A-Z]{3}\d{7}\b',
}

DATE_PATTERNS = [
    r'\d{2}/\d{2}/\d{4}',
    r'\d{2}-\d{2}-\d{4}',
    r'\d{4}/\d{2}/\d{2}',
    r'\d{4}-\d{2}-\d{2}',
    r'\d{2}\s+\w+\s+\d{4}',
]

# =============================================================================
# RULE ENGINE THRESHOLDS
# =============================================================================
RULE_CONFIG = {
    'name_match_threshold': 0.70,
    'min_age': 18,
    'max_age': 120,
    'mismatch_tolerance': 0.30,
}

# =============================================================================
# SCORING WEIGHTS (for final doc_risk_score)
# =============================================================================
SCORING_WEIGHTS = {
    'quality': 0.25,
    'forgery': 0.40,
    'mismatch': 0.35,
}

# =============================================================================
# DECISION THRESHOLDS
# =============================================================================
DECISION_CONFIG = {
    'reject_threshold': 0.70,
    'review_threshold': 0.35,
}
