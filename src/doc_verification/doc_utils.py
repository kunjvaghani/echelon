import cv2
import numpy as np
from typing import Dict, Optional

# Import models from the models package
from .models import (
    DocumentQualityChecker,
    ForgeryDetector,
    OCRExtractor,
    RuleEngine
)
from .config import SCORING_WEIGHTS, DECISION_CONFIG


class DocumentVerifier:
    """
    Complete document verification pipeline
    Combines all models for comprehensive verification
    """
    
    def __init__(self):
        """Initialize all verification models"""
        self.quality_checker = DocumentQualityChecker()
        self.forgery_detector = ForgeryDetector()
        self.ocr_extractor = OCRExtractor()
        self.rule_engine = RuleEngine()
        self.weights = SCORING_WEIGHTS
        self.decision_config = DECISION_CONFIG
    
    def check_quality(self, image):
        """
        Checks document image quality (blur, glare, brightness, resolution, contrast).
        """
        result = self.quality_checker.get_quality_score(image)
        return {
            "quality_score": result['quality_score'],
            "is_valid": result['passed'],
            "details": result['details']
        }

    def detect_forgery(self, image):
        """
        Detects AI-generated or edited documents using multiple techniques.
        """
        result = self.forgery_detector.get_forgery_score(image)
        return {
            "forgery_score": result['forgery_score'],
            "is_suspicious": result['is_suspicious'],
            "risk_level": result['risk_level'],
            "details": result['details']
        }

    def extract_text(self, image):
        """
        Extracts text using OCR with preprocessing.
        """
        result = self.ocr_extractor.extract_all(image)
        return {
            "name": result['extracted_data'].get('name', ''),
            "dob": result['extracted_data'].get('dob', ''),
            "id_number": result['extracted_data'].get('id_number', ''),
            "id_type": result['extracted_data'].get('id_type', ''),
            "confidence": result['confidence'],
            "raw_text": result['raw_text']
        }
    
    def verify_document(self, image: np.ndarray, user_data: Optional[Dict] = None) -> Dict:
        """
        Complete document verification pipeline
        
        Args:
            image: BGR image array of the document
            user_data: Optional user-provided data for validation {name, dob, id_number}
            
        Returns:
            Complete verification result with all scores and decision
        """
        result = {
            'phase': 'DOC_VERIFICATION',
            'status': None,
            'decision': None,
            'scores': {},
            'details': {},
            'flags': [],
            'doc_risk_score': 0.0
        }
        
        # STEP 1: QUALITY CHECK
        try:
            quality_result = self.quality_checker.get_quality_score(image)
            result['scores']['quality_score'] = quality_result['quality_score']
            result['details']['quality'] = quality_result
            
            if not quality_result['passed']:
                result['flags'].append('⚠️ Document quality issues detected')
        except Exception as e:
            result['scores']['quality_score'] = 0.5
            result['flags'].append(f'❌ Quality check failed: {str(e)}')
        
        # STEP 2: FORGERY DETECTION
        try:
            forgery_result = self.forgery_detector.get_forgery_score(image)
            result['scores']['forgery_score'] = forgery_result['forgery_score']
            result['details']['forgery'] = forgery_result
            
            if forgery_result['is_suspicious']:
                result['flags'].append(f"⚠️ Potential forgery detected ({forgery_result['risk_level']} risk)")
        except Exception as e:
            result['scores']['forgery_score'] = 0.5
            result['flags'].append(f'❌ Forgery detection failed: {str(e)}')
        
        # STEP 3: OCR EXTRACTION
        try:
            ocr_result = self.ocr_extractor.extract_all(image)
            result['details']['ocr'] = ocr_result
            
            extracted = ocr_result['extracted_data']
            if ocr_result['confidence'] < 0.5:
                result['flags'].append('⚠️ Low OCR confidence - text extraction incomplete')
        except Exception as e:
            ocr_result = {'extracted_data': {}, 'confidence': 0}
            extracted = {}
            result['flags'].append(f'❌ OCR extraction failed: {str(e)}')
        
        # STEP 4: RULE ENGINE (Content Validation)
        if user_data:
            try:
                mismatch_result = self.rule_engine.get_mismatch_score(extracted, user_data)
                result['scores']['mismatch_score'] = mismatch_result['mismatch_score']
                result['details']['rule_engine'] = mismatch_result
                result['flags'].extend(mismatch_result['flags'])
            except Exception as e:
                result['scores']['mismatch_score'] = 0.5
                result['flags'].append(f'❌ Content validation failed: {str(e)}')
        else:
            result['scores']['mismatch_score'] = 0.0
            result['details']['rule_engine'] = {'message': 'No user data provided for comparison'}
        
        # STEP 5: CALCULATE FINAL RISK SCORE
        doc_risk_score = self._calculate_risk_score(result['scores'])
        result['doc_risk_score'] = doc_risk_score
        
        # STEP 6: MAKE DECISION
        decision = self._make_decision(doc_risk_score, result)
        result['decision'] = decision['decision']
        result['status'] = decision['status']
        result['decision_details'] = decision
        
        return result
    
    def _calculate_risk_score(self, scores: Dict) -> float:
        """Calculate final document risk score"""
        quality = scores.get('quality_score', 0.5)
        forgery = scores.get('forgery_score', 0.5)
        mismatch = scores.get('mismatch_score', 0.0)
        
        quality_risk = 1.0 - quality
        
        risk_score = (
            quality_risk * self.weights['quality'] +
            forgery * self.weights['forgery'] +
            mismatch * self.weights['mismatch']
        )
        
        return round(risk_score, 3)
    
    def _make_decision(self, risk_score: float, result: Dict) -> Dict:
        """Make verification decision"""
        quality_score = result['scores'].get('quality_score', 0.5)
        forgery_score = result['scores'].get('forgery_score', 0.5)
        
        component_decisions = []
        
        if quality_score < 0.30:
            component_decisions.append('REJECT')
        elif quality_score < 0.50:
            component_decisions.append('MANUAL_REVIEW')
        else:
            component_decisions.append('APPROVE')
        
        if forgery_score > 0.70:
            component_decisions.append('REJECT')
        elif forgery_score > 0.40:
            component_decisions.append('MANUAL_REVIEW')
        else:
            component_decisions.append('APPROVE')
        
        if 'rule_engine' in result['details'] and 'component_decisions' in result['details']['rule_engine']:
            data_match_decision = result['details']['rule_engine']['component_decisions'].get('data_match', 'APPROVE')
            component_decisions.append(data_match_decision)
            
            age_decision = result['details']['rule_engine']['component_decisions'].get('age_valid', 'APPROVE')
            component_decisions.append(age_decision)
        
        if 'REJECT' in component_decisions:
            return {
                'decision': 'REJECT',
                'status': 'FAILED',
                'confidence': 'HIGH',
                'message': 'Document rejected due to failed component check(s)',
                'risk_score': risk_score,
                'component_decisions': component_decisions
            }
        elif 'MANUAL_REVIEW' in component_decisions:
            return {
                'decision': 'MANUAL_REVIEW',
                'status': 'PENDING',
                'confidence': 'MEDIUM',
                'message': 'Document requires manual review',
                'risk_score': risk_score,
                'component_decisions': component_decisions
            }
        else:
            return {
                'decision': 'APPROVE',
                'status': 'PASSED',
                'confidence': 'HIGH',
                'message': 'Document passed all automated verification checks',
                'risk_score': risk_score,
                'component_decisions': component_decisions
            }
