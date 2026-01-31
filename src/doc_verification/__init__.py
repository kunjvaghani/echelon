"""
Document Verification Module
=============================
Comprehensive document verification using multiple models:
- Quality Check (OpenCV)
- Forgery Detection (EfficientNet + statistical analysis)
- OCR Extraction (Tesseract)
- Rule Engine (Content validation)
"""

from .doc_utils import DocumentVerifier

__all__ = ['DocumentVerifier']
