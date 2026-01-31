"""
MODEL 3: Document Quality Check using OpenCV
============================================
Input: Document image
Output: quality_score (0-1, where 1 = perfect quality)

Checks:
- Blur detection (Laplacian variance)
- Resolution check
- Brightness/contrast
- Border/cropping detection
"""

import cv2
import numpy as np
from typing import Dict, Tuple

try:
    from ..config import QUALITY_CONFIG
except ImportError:
    from doc_verification.config import QUALITY_CONFIG


class DocumentQualityChecker:
    """OpenCV-based document quality assessment"""
    
    def __init__(self):
        self.config = QUALITY_CONFIG
    
    def check_blur(self, image: np.ndarray) -> Tuple[float, bool]:
        """Detect blur using Laplacian variance"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        threshold = self.config['blur_threshold']
        blur_score = min(laplacian_var / threshold, 1.0)
        is_sharp = laplacian_var >= threshold
        return blur_score, is_sharp
    
    def check_resolution(self, image: np.ndarray) -> Tuple[float, bool]:
        """Check if image meets minimum resolution"""
        height, width = image.shape[:2]
        min_width, min_height = self.config['min_resolution']
        width_ratio = width / min_width
        height_ratio = height / min_height
        resolution_score = min((width_ratio + height_ratio) / 2, 1.0)
        meets_minimum = width >= min_width and height >= min_height
        return resolution_score, meets_minimum
    
    def check_brightness(self, image: np.ndarray) -> Tuple[float, bool]:
        """Check if image has good brightness"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        min_bright = self.config['min_brightness']
        max_bright = self.config['max_brightness']
        is_good = min_bright <= avg_brightness <= max_bright
        ideal_brightness = (min_bright + max_bright) / 2
        deviation = abs(avg_brightness - ideal_brightness) / ideal_brightness
        brightness_score = max(1.0 - deviation, 0.0)
        return brightness_score, is_good
    
    def check_borders(self, image: np.ndarray) -> Tuple[float, bool]:
        """Check if document has proper margins"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        edges = cv2.Canny(gray, 50, 150)
        margin = int(min(width, height) * self.config['border_threshold'])
        
        if margin == 0:
            return 1.0, True
        
        top_edges = np.sum(edges[:margin, :]) / (margin * width * 255) if margin > 0 and width > 0 else 0
        bottom_edges = np.sum(edges[-margin:, :]) / (margin * width * 255) if margin > 0 and width > 0 else 0
        left_edges = np.sum(edges[:, :margin]) / (margin * height * 255) if margin > 0 and height > 0 else 0
        right_edges = np.sum(edges[:, -margin:]) / (margin * height * 255) if margin > 0 and height > 0 else 0
        
        edge_threshold = 0.3
        has_margins = all([
            top_edges < edge_threshold,
            bottom_edges < edge_threshold,
            left_edges < edge_threshold,
            right_edges < edge_threshold
        ])
        
        avg_edge_density = (top_edges + bottom_edges + left_edges + right_edges) / 4
        border_score = max(1.0 - avg_edge_density * 2, 0.0)
        return border_score, has_margins
    
    def check_contrast(self, image: np.ndarray) -> Tuple[float, bool]:
        """Check image contrast"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrast = gray.std()
        min_contrast = 40
        is_good = contrast >= min_contrast
        contrast_score = min(contrast / 80, 1.0)
        return contrast_score, is_good
    
    def get_quality_score(self, image: np.ndarray) -> Dict:
        """Calculate overall document quality score"""
        blur_score, is_sharp = self.check_blur(image)
        resolution_score, meets_resolution = self.check_resolution(image)
        brightness_score, good_brightness = self.check_brightness(image)
        border_score, has_margins = self.check_borders(image)
        contrast_score, good_contrast = self.check_contrast(image)
        
        weights = {
            'blur': 0.30,
            'resolution': 0.25,
            'brightness': 0.15,
            'border': 0.15,
            'contrast': 0.15
        }
        
        quality_score = (
            blur_score * weights['blur'] +
            resolution_score * weights['resolution'] +
            brightness_score * weights['brightness'] +
            border_score * weights['border'] +
            contrast_score * weights['contrast']
        )
        
        quality_threshold = 0.50
        passed = quality_score >= quality_threshold
        
        return {
            'quality_score': round(quality_score, 3),
            'passed': passed,
            'details': {
                'blur': {
                    'score': round(blur_score, 3),
                    'passed': is_sharp,
                    'message': 'Image is sharp' if is_sharp else 'Image is too blurry'
                },
                'resolution': {
                    'score': round(resolution_score, 3),
                    'passed': meets_resolution,
                    'message': 'Resolution OK' if meets_resolution else 'Resolution too low'
                },
                'brightness': {
                    'score': round(brightness_score, 3),
                    'passed': good_brightness,
                    'message': 'Brightness OK' if good_brightness else 'Poor lighting'
                },
                'borders': {
                    'score': round(border_score, 3),
                    'passed': has_margins,
                    'message': 'Margins OK' if has_margins else 'Document may be cropped'
                },
                'contrast': {
                    'score': round(contrast_score, 3),
                    'passed': good_contrast,
                    'message': 'Contrast OK' if good_contrast else 'Low contrast'
                }
            }
        }


def analyze_document_quality(image_path: str) -> Dict:
    """Convenience function to analyze document quality from file path"""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    checker = DocumentQualityChecker()
    return checker.get_quality_score(image)
