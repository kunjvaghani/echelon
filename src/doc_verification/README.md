# Document Verification Module

Self-contained document verification system with multiple AI models for comprehensive ID document analysis.

## Structure

```
doc_verification/
├── __init__.py              # Package initialization
├── config.py                # All configuration and thresholds
├── doc_utils.py             # Main DocumentVerifier class
├── models/
│   ├── __init__.py
│   ├── document_quality.py  # OpenCV-based quality check
│   ├── forgery_detector.py  # EfficientNet forgery detection
│   ├── ocr_extractor.py     # Tesseract OCR extraction
│   └── rule_engine.py       # Content validation
└── README.md                # This file
```

## Features

### 1. Quality Check (OpenCV)
- Blur detection using Laplacian variance
- Resolution validation
- Brightness/contrast assessment
- Border/cropping detection

**Output:** `quality_score` (0-1, where 1 = perfect quality)

### 2. Forgery Detection (EfficientNet + ELA)
- Error Level Analysis (ELA) for compression artifacts
- Noise pattern analysis
- Edge consistency checking
- Frequency domain analysis
- Deep learning features (if TensorFlow available)

**Output:** `forgery_score` (0-1, where 1 = definitely forged)

### 3. OCR Extraction (Tesseract)
- Image preprocessing for better accuracy
- Text extraction with multiple configs
- Name extraction with filtering
- DOB parsing (multiple formats)
- ID number detection (Aadhaar, PAN, Passport, etc.)

**Output:** Extracted Name, DOB, ID Number with confidence score

### 4. Rule Engine (Content Validation)
- Fuzzy name matching
- DOB validation with age checks
- ID format validation
- Mismatch scoring

**Output:** `mismatch_score` (0-1, how much OCR data differs from user data)

## Usage

### Basic Usage

```python
from doc_verification import DocumentVerifier
import cv2

# Initialize verifier
verifier = DocumentVerifier()

# Load document image
image = cv2.imread('document.jpg')

# Verify document (with optional user data for comparison)
user_data = {
    'name': 'John Doe',
    'dob': '1990-01-15',
    'id_number': 'ABCDE1234F'
}

result = verifier.verify_document(image, user_data)

# Result contains:
# - decision: 'APPROVE', 'MANUAL_REVIEW', or 'REJECT'
# - doc_risk_score: 0-1 (higher = riskier)
# - scores: quality, forgery, mismatch scores
# - details: detailed analysis from each model
# - flags: human-readable findings
```

### Individual Model Usage

```python
# Quality Check
quality_result = verifier.check_quality(image)
# Returns: quality_score, is_valid, details

# Forgery Detection
forgery_result = verifier.detect_forgery(image)
# Returns: forgery_score, is_suspicious, risk_level

# OCR Extraction
ocr_result = verifier.extract_text(image)
# Returns: name, dob, id_number, confidence
```

## Configuration

Edit `config.py` to customize:

- **QUALITY_CONFIG**: Blur threshold, resolution, brightness, contrast
- **FORGERY_CONFIG**: Model input size, confidence threshold
- **OCR_CONFIG**: Tesseract language, page segmentation mode
- **ID_PATTERNS**: Regex patterns for different ID types
- **RULE_CONFIG**: Matching thresholds, age limits
- **SCORING_WEIGHTS**: How much each score affects final decision
- **DECISION_CONFIG**: Risk thresholds for APPROVE/REVIEW/REJECT

## Decision Logic

Final `doc_risk_score` = (1 - quality_score) × 0.25 + forgery_score × 0.40 + mismatch_score × 0.35

### Decision Thresholds

| Risk Score | Decision |
|------------|----------|
| < 0.35 | ✅ APPROVE |
| 0.35 - 0.70 | ⚠️ MANUAL_REVIEW |
| > 0.70 | ❌ REJECT |

## Dependencies

### Required
- `cv2` (OpenCV)
- `numpy`
- `pytesseract` (Tesseract OCR wrapper)

### Optional
- `tensorflow` (for deep learning features in forgery detection)
- `fuzzywuzzy` (for improved name matching)
- `dateutil` (for advanced date parsing)

### System Requirements
- **Tesseract-OCR**: Required for OCR functionality
  - Install from: https://github.com/UB-Mannheim/tesseract/wiki
  - Update `TESSERACT_PATH` in config.py after installation

## Features

✅ **No Training Required** - Uses pretrained models and heuristics
✅ **Self-Contained** - Doesn't affect other code
✅ **Independent** - All models integrated into one module
✅ **Comprehensive** - Multiple verification techniques
✅ **Configurable** - Thresholds adjustable via config.py
✅ **Error Handling** - Graceful fallbacks if optional dependencies missing

## Error Handling

The module handles missing dependencies gracefully:
- If TensorFlow not available: Uses OpenCV-only forgery detection
- If Tesseract not found: Returns empty OCR results
- If fuzzywuzzy not available: Falls back to basic string matching
- If dateutil not available: Uses simple age calculation

## Performance Notes

- Typical document verification: 2-5 seconds
- Quality check: ~0.1s
- Forgery detection: ~0.5-1s
- OCR extraction: ~1-3s
- Rule engine: ~0.1s

## Troubleshooting

### "Could not read image" error
- Verify image path is correct
- Ensure image format is supported (JPG, PNG, BMP, etc.)

### "Tesseract not found" error
- Install Tesseract-OCR from: https://github.com/UB-Mannheim/tesseract/wiki
- Update `TESSERACT_PATH` in config.py

### Low OCR confidence
- Improve image quality (resolution, brightness, contrast)
- Ensure document is clearly visible
- Check that document is not rotated

### High false positives in forgery detection
- Adjust `FORGERY_CONFIG['confidence_threshold']` in config.py
- Check document image quality
- Review `SCORING_WEIGHTS` in config.py

## Version

Version 1.0 - Integrated from Echeleon project
