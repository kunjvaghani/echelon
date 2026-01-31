import cv2
import os
import pathlib
from dotenv import load_dotenv
import numpy as np
from deepface import DeepFace

# Load environment variables from ../../.env (relative to this file)
current_dir = pathlib.Path(__file__).parent.resolve()
env_path = current_dir.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class FaceVerifier:
    def __init__(self):
        """
        Initialize FaceVerifier with FaceNet model and Haar Cascade.
        Models are loaded once to avoid reloading overhead.
        """
        # 1. Architecture: Use FaceNet (via DeepFace)
        self.model_name = os.getenv("FACE_MODEL_NAME", "Facenet")
        
        # 2. Architecture: Load Haar Cascade for face detection
        # Try loading from cv2.data first, then fallback
        try:
             self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except AttributeError:
             self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            
        if self.face_cascade.empty():
            print("CRITICAL WARNING: Haar Cascade not loaded correctly. Check opencv installation or path.")

        # 3. Architecture: Pre-load/Warm-up DeepFace model
        print(f"[INFO] Loading {self.model_name} model for Face Verification... This may take a few seconds.")
        try:
            # Dummy run to load weights into memory
            dummy_img = np.zeros((160, 160, 3), dtype=np.uint8)
            DeepFace.represent(
                img_path=dummy_img, 
                model_name=self.model_name, 
                enforce_detection=False,
                detector_backend="skip"
            )
            print(f"[INFO] {self.model_name} loaded and warmed up successfully.")
        except Exception as e:
            print(f"[WARNING] Model warmup failed: {e}")

    def detect_face(self, image):
        """
        Detects the largest face in the image using Haar Cascade.
        
        Args:
            image: BGR numpy array (OpenCV format)
            
        Returns:
            cropped_face: BGR numpy array of the face (or None if no face)
        """
        # 7. Edge Case Handling: Invalid input
        if image is None or image.size == 0:
            return None

        # 3. Face Detection: Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 3. Face Detection: Detect faces
        # scaleFactor=1.1, minNeighbors=5 are standard robust params
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            return None
            
        # 3. Face Detection: Select the largest face
        # faces returns list of (x, y, w, h)
        # We assume the largest face is the primary user
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face
        
        # 3. Face Detection: Crop safely
        height, width, _ = image.shape
        # Add a small margin if desired, but sticking to strict box for now to avoid noise
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(width, x + w), min(height, y + h)
        
        cropped_face = image[y1:y2, x1:x2]
        
        return cropped_face

    def check_liveness(self, image):
        """
        Performs Liveness Detection using Laplacian Variance.
        Checks for blur/loss of texture which is common in spoofs (screens/paper).
        
        Args:
            image: BGR numpy array (full image or face crop)
            
        Returns:
            is_live (bool): True if passes liveness check
            confidence (float): A heuristic score 0.0-1.0
        """
        # 2. Liveness Detection: Mandatory
        if image is None or image.size == 0:
            return False, 0.0
            
        # Convert to grayscale for Laplacian
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate variance of Laplacian: High variance = sharp edges (Live), Low = blur (Spoof)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Threshold: 
        # Real cameras usually produce sharp images > 100-300 variance.
        # Blurred screens/printed photos often drop below 50-60.
        # Setting a conservative threshold to satisfy "effective method".
        LIVENESS_THRESHOLD = float(os.getenv("LIVENESS_THRESHOLD", 50.0)) 
        
        is_live = laplacian_var > LIVENESS_THRESHOLD
        
        # Normalize for display/logging (cap at 500 for 1.0)
        confidence = min(1.0, laplacian_var / 500.0)
        
        return is_live, confidence

    def get_embedding(self, face_image):
        """
        Generates a 128-D embedding for a verified live face.
        
        Args:
            face_image: BGR numpy array (cropped face)
            
        Returns:
            embedding: 128-D numpy array, or None if failed
        """
        # 7. Edge Case Handling: Zero embeddings or invalid input
        if face_image is None or face_image.size == 0:
            return None

        try:
            # 4. Live Embedding Generation: DeepFace.represent
            results = DeepFace.represent(
                img_path=face_image,
                model_name=self.model_name,
                enforce_detection=False, # We already detected/cropped
                detector_backend="skip"
            )
            
            if results and len(results) > 0:
                embedding = results[0]['embedding']
                return np.array(embedding, dtype=np.float32)
                
        except Exception as e:
            print(f"[ERROR] Embedding generation failed: {e}")
            return None
            
        return None

    def verify_with_stored_embedding(self, live_embedding, stored_embedding):
        """
        Verifies a live embedding against a trusted stored embedding.
        
        Args:
            live_embedding (np.array): 128-D array from live camera
            stored_embedding (np.array): 128-D array from database
            
        Returns:
            similarity_score (float): 0.0 to 1.0 (Cosine Similarity)
            decision (str): "VERIFIED", "MANUAL_REVIEW", or "REJECTED"
        """
        # 7. Edge Case Handling: Invalid inputs
        if live_embedding is None or stored_embedding is None:
            return 0.0, "REJECTED"

        # Ensure numpy arrays
        emb1 = np.array(live_embedding)
        emb2 = np.array(stored_embedding)

        # 5. Face Verification Logic: Cosine Similarity
        # similarity = dot(a, b) / (||a|| * ||b||)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
             return 0.0, "REJECTED"
             
        # Compute cosine similarity
        cos_sim = np.dot(emb1, emb2) / (norm1 * norm2)
        
        # Clamp value to [-1, 1] to avoid floating point errors
        cos_sim = max(-1.0, min(1.0, cos_sim))
        
        # 6. Decision Thresholds
        verified_thresh = float(os.getenv("VERIFICATION_THRESHOLD_VERIFIED", 0.75))
        review_thresh = float(os.getenv("VERIFICATION_THRESHOLD_REVIEW", 0.60))

        if cos_sim >= verified_thresh:
            decision = "VERIFIED"
        elif cos_sim >= review_thresh:
            decision = "MANUAL_REVIEW"
        else:
            decision = "REJECTED"
            
        return float(cos_sim), decision

