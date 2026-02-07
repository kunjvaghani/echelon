"""
MODEL 5: OCR Text Extraction using Tesseract
=============================================
Uses Tesseract OCR with preprocessing for better accuracy
"""

import cv2
import numpy as np
import re
from typing import Dict, List, Optional
from datetime import datetime

try:
    from ..config import OCR_CONFIG, ID_PATTERNS, DATE_PATTERNS, TESSERACT_PATH
except ImportError:
    from doc_verification.config import OCR_CONFIG, ID_PATTERNS, DATE_PATTERNS, TESSERACT_PATH

try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class OCRExtractor:
    """Tesseract-based OCR for ID document text extraction"""
    
    def __init__(self):
        self.config = OCR_CONFIG
        self.id_patterns = ID_PATTERNS
        self.date_patterns = DATE_PATTERNS
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Resize if too small
        height, width = gray.shape
        if width < 600 or height < 400:
            scale_factor = max(600 / width, 400 / height)
            gray = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, 
                            interpolation=cv2.INTER_CUBIC)
        
        # Denoise the image
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # Apply bilateral filter to smooth while preserving edges
        filtered = cv2.bilateralFilter(denoised, 9, 75, 75)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(filtered)
        
        # Apply adaptive thresholding for better text detection
        thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        
        # Morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=1)
        thresh = cv2.erode(thresh, kernel, iterations=1)
        
        return thresh
    
    def extract_raw_text(self, image: np.ndarray) -> str:
        """Extract raw text from image using Tesseract"""
        if not TESSERACT_AVAILABLE:
            return ""
        
        processed = self.preprocess_image(image)
        configs = [
            f'--psm 6 --oem 3',
            f'--psm 1 --oem 3',
            f'--psm 3 --oem 3',
        ]
        
        best_text = ""
        best_confidence = 0
        
        for config in configs:
            try:
                text = pytesseract.image_to_string(
                    processed,
                    lang=self.config['lang'],
                    config=config
                )
                lines = [l for l in text.split('\n') if l.strip()]
                confidence = len(lines) / max(len(text.split('\n')), 1)
                
                if confidence > best_confidence:
                    best_text = text
                    best_confidence = confidence
            except:
                continue
        
        return best_text.strip() if best_text else ""
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract name from OCR text"""
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        
        for i, line in enumerate(cleaned_lines):
            if re.search(r'(?:Name|नाम)', line, re.IGNORECASE):
                if ':' in line:
                    name = line.split(':', 1)[1].strip()
                    if name and len(name) > 2:
                        name = self._clean_name(name)
                        if name:
                            return name
                if i + 1 < len(cleaned_lines):
                    name = cleaned_lines[i + 1]
                    name = self._clean_name(name)
                    if name:
                        return name
        
        best_name = None
        best_score = 0
        
        for line in cleaned_lines:
            if len(line) < 5 or len(line) > 50:
                continue
            if re.search(r'\d{4,}', line):
                continue
            
            alpha_space_count = sum(1 for c in line if c.isalpha() or c.isspace())
            ratio = alpha_space_count / len(line) if line else 0
            
            is_name = (ratio > 0.75 and 
                      not any(word in line.lower() for word in 
                      ['government', 'india', 'aadhaar', 'income', 'tax', 'ministry', 
                       'department', 'state', 'male', 'female', 'address', 'email', 'phone']))
            
            if is_name and ratio > best_score:
                best_name = line
                best_score = ratio
        
        if best_name:
            return self._clean_name(best_name)
        
        return None
    
    def _clean_name(self, name: str) -> Optional[str]:
        """Clean and validate extracted name"""
        if not name:
            return None
        
        name = re.sub(r'\s+', ' ', name).strip()
        name = re.sub(r'[^A-Za-z\s\-\']', '', name)
        
        filter_words = ['government', 'india', 'aadhaar', 'income', 'tax', 'department', 
                       'ministry', 'state', 'male', 'female', 'mr', 'mrs', 'miss', 'ms']
        for word in filter_words:
            name = re.sub(r'\b' + word + r'\b', '', name, flags=re.IGNORECASE)
        
        name = name.strip()
        
        if 3 <= len(name) <= 40 and any(c.isalpha() for c in name):
            return name
        
        return None
    
    def extract_dob(self, text: str) -> Optional[str]:
        """Extract Date of Birth from OCR text"""
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            if re.search(r'(?:DOB|D\.?O\.?B|Date of Birth|Birth)', line, re.IGNORECASE):
                search_text = line + ' ' + (lines[i+1] if i+1 < len(lines) else '')
                
                for pattern in self.date_patterns:
                    match = re.search(pattern, search_text)
                    if match:
                        parsed = self._parse_date(match.group())
                        if parsed:
                            return parsed
        
        for pattern in self.date_patterns:
            match = re.search(pattern, text)
            if match:
                parsed = self._parse_date(match.group())
                if parsed:
                    return parsed
        
        date_8digit = re.search(r'\b(\d{2})(\d{2})(\d{4})\b', text)
        if date_8digit:
            try:
                day, month, year = date_8digit.groups()
                date_obj = datetime.strptime(f'{day}/{month}/{year}', '%d/%m/%Y')
                return date_obj.strftime('%Y-%m-%d')
            except:
                pass
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats to YYYY-MM-DD"""
        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y',
            '%Y/%m/%d', '%Y-%m-%d',
            '%d %B %Y', '%d %b %Y',
        ]
        
        date_str = date_str.strip()
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def extract_id_number(self, text: str) -> Dict[str, Optional[str]]:
        """Extract ID number(s) from OCR text"""
        found_ids = {}
        text_upper = text.upper()
        
        for id_type, pattern in self.id_patterns.items():
            matches = re.finditer(pattern, text_upper)
            for match in matches:
                found_id = match.group().strip()
                if found_id and len(found_id) > 5:
                    found_ids[id_type] = found_id
                    break
        
        if not found_ids:
            aadhaar = re.search(r'\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4})\b', text)
            if aadhaar:
                found_ids['aadhaar'] = aadhaar.group(1).replace(' ', '').replace('-', '')
            
            pan = re.search(r'\b([A-Z]{5}\d{4}[A-Z])\b', text_upper)
            if pan:
                found_ids['pan'] = pan.group(1)
        
        return found_ids
    
    def extract_all(self, image: np.ndarray) -> Dict:
        """Extract all structured data from document image"""
        raw_text = self.extract_raw_text(image)
        name = self.extract_name(raw_text)
        dob = self.extract_dob(raw_text)
        id_numbers = self.extract_id_number(raw_text)
        
        primary_id = None
        id_type = None
        for id_t, id_num in id_numbers.items():
            if id_num:
                primary_id = id_num
                id_type = id_t
                break
        
        return {
            'raw_text': raw_text,
            'extracted_data': {
                'name': name,
                'dob': dob,
                'id_number': primary_id,
                'id_type': id_type,
                'all_ids': id_numbers
            },
            'extraction_success': {
                'name': name is not None,
                'dob': dob is not None,
                'id_number': primary_id is not None
            },
            'confidence': self._calculate_confidence(name, dob, primary_id)
        }
    
    def _calculate_confidence(self, name: Optional[str], dob: Optional[str], 
                             id_number: Optional[str]) -> float:
        """Calculate overall extraction confidence"""
        score = 0.0
        
        if name and len(name) > 2:
            score += 0.33
        if dob:
            score += 0.33
        if id_number:
            score += 0.34
        
        return round(score, 2)


def extract_document_text(image_path: str) -> Dict:
    """Convenience function to extract text from document image"""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    extractor = OCRExtractor()
    return extractor.extract_all(image)
