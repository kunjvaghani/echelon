import cv2
import numpy as np
# from deepface import DeepFace

class FaceVerifier:
    def __init__(self):
        # TEAM NOTE: Initialize your models here.
        # Suggestion: Load DeepFace models once at startup to save time.
        # self.model_name = "FaceNet"
        pass

    def detect_face(self, image):
        """
        Detects face in an image.
        Returns: cropped_face, confidence
        """
        # TODO: Implement Face Detection
        # 1. Convert image to RGB.
        # 2. Use MTCNN or cv2.CascadeClassifier to find faces.
        # 3. If multiple faces found, select the largest one.
        # 4. Return the cropped numpy array of the face.
        return None, 0.0

    def get_embedding(self, face_image):
        """
        Generates face embedding vector.
        """
        # TODO: Implement Embedding Generation
        # 1. Use DeepFace.represent(img_path=face_image, model_name="FaceNet")
        # 2. Extract the 'embedding' list from the result.
        # 3. specificy `enforce_detection=False` if you already cropped the face.
        return np.zeros(128)

    def verify_faces(self, img1, img2):
        """
        Compares two faces and returns similarity score.
        """
        # TODO: Implement Comparison Logic
        # 1. Get embedding for img1.
        # 2. Get embedding for img2.
        # 3. Calculate Cosine Similarity:
        #    similarity = dot(a, b) / (norm(a) * norm(b))
        # 4. Return score (0.0 to 1.0).
        return 0.0

    def check_liveness(self, image):
        """
        Checks if the face is real (live) or a spoof.
        """
        # TODO: Implement Liveness Detection (Anti-Spoofing)
        # Option A (Simple): Eye Blink Detection using dlib/mediapipe.
        # Option B (Advanced): Texture analysis (LBP) to detect screen pixels.
        # Return True if real, False if fake.
        return True, 0.99
