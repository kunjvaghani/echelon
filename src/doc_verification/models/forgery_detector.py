"""
MODEL 4: AI-Generated / Edited Document Detection
==================================================
Uses pretrained EfficientNetB0 and statistical analysis
NO TRAINING REQUIRED - uses pretrained weights + heuristics
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional

try:
    from ..config import FORGERY_CONFIG
except ImportError:
    from doc_verification.config import FORGERY_CONFIG

try:
    import tensorflow as tf
    from tensorflow.keras.applications import EfficientNetB0
    from tensorflow.keras.applications.efficientnet import preprocess_input
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class ForgeryDetector:
    """Detects AI-generated or digitally manipulated documents"""
    
    def __init__(self):
        self.config = FORGERY_CONFIG
        self.model = None
        
        if TF_AVAILABLE:
            try:
                self.model = EfficientNetB0(
                    weights='imagenet',
                    include_top=False,
                    pooling='avg',
                    input_shape=(224, 224, 3)
                )
            except:
                pass
    
    def _preprocess_for_efficientnet(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for EfficientNet"""
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, self.config['input_size'])
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img) if TF_AVAILABLE else img / 255.0
        return img
    
    def analyze_ela(self, image: np.ndarray, quality: int = 90) -> Tuple[float, np.ndarray]:
        """Error Level Analysis (ELA) - detects compression inconsistencies"""
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encoded = cv2.imencode('.jpg', image, encode_param)
        recompressed = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        ela = cv2.absdiff(image, recompressed)
        ela_amplified = cv2.convertScaleAbs(ela, alpha=10)
        ela_gray = cv2.cvtColor(ela_amplified, cv2.COLOR_BGR2GRAY)
        
        mean_ela = np.mean(ela_gray)
        std_ela = np.std(ela_gray)
        max_ela = np.max(ela_gray)
        ela_score = min((std_ela / 30) + (max_ela / 255) * 0.3, 1.0)
        
        return ela_score, ela_amplified
    
    def analyze_noise(self, image: np.ndarray) -> float:
        """Analyze noise patterns"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float64)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = gray - blur
        
        block_size = 64
        h, w = noise.shape
        blocks_h = h // block_size
        blocks_w = w // block_size
        
        if blocks_h < 2 or blocks_w < 2:
            return 0.3
        
        block_stds = []
        for i in range(blocks_h):
            for j in range(blocks_w):
                block = noise[i*block_size:(i+1)*block_size, j*block_size:(j+1)*block_size]
                block_stds.append(np.std(block))
        
        noise_variance = np.std(block_stds)
        noise_score = max(1.0 - (noise_variance / 5), 0.0)
        return noise_score
    
    def analyze_edges(self, image: np.ndarray) -> float:
        """Analyze edge consistency"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(canny > 0) / canny.size
        ideal_density = 0.1
        edge_deviation = abs(edge_density - ideal_density)
        edge_score = min(edge_deviation * 3, 1.0)
        return edge_score
    
    def analyze_frequency(self, image: np.ndarray) -> float:
        """Frequency domain analysis"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude = np.log(np.abs(fshift) + 1)
        
        h, w = magnitude.shape
        center_h, center_w = h // 2, w // 2
        low_freq = magnitude[center_h-20:center_h+20, center_w-20:center_w+20]
        high_freq = np.concatenate([
            magnitude[:20, :].flatten(),
            magnitude[-20:, :].flatten(),
            magnitude[:, :20].flatten(),
            magnitude[:, -20:].flatten()
        ])
        
        ratio = np.mean(low_freq) / (np.mean(high_freq) + 1e-10)
        ideal_ratio = 2.0
        freq_score = abs(ratio - ideal_ratio) / 5
        freq_score = min(freq_score, 1.0)
        return freq_score
    
    def analyze_deep_features(self, image: np.ndarray) -> float:
        """Use EfficientNet features for anomaly detection"""
        if not TF_AVAILABLE or self.model is None:
            return 0.3
        
        try:
            preprocessed = self._preprocess_for_efficientnet(image)
            features = self.model.predict(preprocessed, verbose=0)
            mean_feat = np.mean(features)
            std_feat = np.std(features)
            expected_mean = 0.5
            expected_std = 0.3
            mean_deviation = abs(mean_feat - expected_mean)
            std_deviation = abs(std_feat - expected_std)
            deep_score = min((mean_deviation + std_deviation) / 2, 1.0)
            return deep_score
        except:
            return 0.3
    
    def get_forgery_score(self, image: np.ndarray) -> Dict:
        """Calculate overall forgery/manipulation score"""
        ela_score, ela_image = self.analyze_ela(image)
        noise_score = self.analyze_noise(image)
        edge_score = self.analyze_edges(image)
        freq_score = self.analyze_frequency(image)
        deep_score = self.analyze_deep_features(image)
        
        weights = {
            'ela': 0.25,
            'noise': 0.20,
            'edges': 0.15,
            'frequency': 0.15,
            'deep_features': 0.25
        }
        
        forgery_score = (
            ela_score * weights['ela'] +
            noise_score * weights['noise'] +
            edge_score * weights['edges'] +
            freq_score * weights['frequency'] +
            deep_score * weights['deep_features']
        )
        
        if forgery_score > 0.70:
            risk_level = 'HIGH'
            is_suspicious = True
        elif forgery_score > 0.40:
            risk_level = 'MEDIUM'
            is_suspicious = True
        else:
            risk_level = 'LOW'
            is_suspicious = False
        
        return {
            'forgery_score': round(forgery_score, 3),
            'is_suspicious': is_suspicious,
            'risk_level': risk_level,
            'details': {
                'ela_analysis': {
                    'score': round(ela_score, 3),
                    'description': 'Error Level Analysis'
                },
                'noise_analysis': {
                    'score': round(noise_score, 3),
                    'description': 'Noise pattern analysis'
                },
                'edge_analysis': {
                    'score': round(edge_score, 3),
                    'description': 'Edge consistency'
                },
                'frequency_analysis': {
                    'score': round(freq_score, 3),
                    'description': 'Frequency domain'
                },
                'deep_features': {
                    'score': round(deep_score, 3),
                    'description': 'Deep learning features'
                }
            }
        }


def analyze_document_forgery(image_path: str) -> Dict:
    """Convenience function to analyze document for forgery"""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    detector = ForgeryDetector()
    return detector.get_forgery_score(image)
