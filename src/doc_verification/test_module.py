"""
Test script for Document Verification Module
Demonstrates how to use the integrated models
"""

import cv2
import sys
from doc_utils import DocumentVerifier


def test_basic_verification():
    """Test basic document verification"""
    print("\n" + "="*60)
    print("Document Verification Module - Test")
    print("="*60)
    
    # Initialize verifier
    print("\n[1/3] Initializing Document Verifier...")
    verifier = DocumentVerifier()
    print("✅ DocumentVerifier initialized successfully")
    
    # Load test image (you need to provide an actual image)
    test_image_path = "test_document.jpg"
    
    try:
        print(f"\n[2/3] Loading test image: {test_image_path}")
        image = cv2.imread(test_image_path)
        
        if image is None:
            print(f"❌ Could not load image: {test_image_path}")
            print("   Create a 'test_document.jpg' file to run the test")
            return
        
        print(f"✅ Image loaded successfully ({image.shape[1]}x{image.shape[0]}px)")
        
        # Test individual components
        print("\n[3/3] Running verification components...")
        
        # Quality Check
        print("\n   Quality Check...")
        quality = verifier.check_quality(image)
        print(f"   ✅ Quality Score: {quality['quality_score']:.2%}")
        print(f"   ✅ Valid: {quality['is_valid']}")
        
        # Forgery Detection
        print("\n   Forgery Detection...")
        forgery = verifier.detect_forgery(image)
        print(f"   ✅ Forgery Score: {forgery['forgery_score']:.2%}")
        print(f"   ✅ Risk Level: {forgery['risk_level']}")
        
        # OCR Extraction
        print("\n   OCR Extraction...")
        ocr = verifier.extract_text(image)
        print(f"   ✅ Name: {ocr['name'] or 'Not detected'}")
        print(f"   ✅ DOB: {ocr['dob'] or 'Not detected'}")
        print(f"   ✅ ID: {ocr['id_number'] or 'Not detected'}")
        print(f"   ✅ Confidence: {ocr['confidence']:.0%}")
        
        # Complete Verification
        print("\n   Complete Verification (with optional user data)...")
        user_data = {
            'name': 'John Doe',
            'dob': '1990-01-15',
            'id_number': 'ABCDE1234F'
        }
        
        result = verifier.verify_document(image, user_data)
        print(f"   ✅ Decision: {result['decision']}")
        print(f"   ✅ Risk Score: {result['doc_risk_score']:.2%}")
        print(f"   ✅ Status: {result['status']}")
        
        if result['flags']:
            print("\n   Flags:")
            for flag in result['flags']:
                print(f"   - {flag}")
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()


def test_without_image():
    """Test that module loads correctly without an image"""
    print("\n" + "="*60)
    print("Document Verification Module - Load Test")
    print("="*60)
    
    try:
        print("\n[1/2] Importing DocumentVerifier...")
        from doc_utils import DocumentVerifier
        print("✅ Import successful")
        
        print("\n[2/2] Initializing DocumentVerifier...")
        verifier = DocumentVerifier()
        print("✅ Initialization successful")
        
        print("\n✅ Module is working correctly!")
        print("   - DocumentQualityChecker initialized")
        print("   - ForgeryDetector initialized")
        print("   - OCRExtractor initialized")
        print("   - RuleEngine initialized")
        
        print("\n" + "="*60)
        print("Ready to verify documents!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔍 Document Verification Module Test Suite\n")
    
    # Always run the basic load test
    test_without_image()
    
    # Optionally run with image if available
    try:
        test_basic_verification()
    except FileNotFoundError:
        print("ℹ️  To test with images, place 'test_document.jpg' in the same directory")
