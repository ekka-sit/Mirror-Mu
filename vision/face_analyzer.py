import cv2
import mediapipe as mp
import numpy as np

class FaceAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # จุด Landmark มาตรฐานอ้างอิง
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.MOUTH_CORNER_L = 61
        self.MOUTH_CORNER_R = 291

    def _calculate_ear(self, landmarks, eye_indices):
        """คำนวณ Eye Aspect Ratio ทางคณิตศาสตร์"""
        v1 = np.linalg.norm(landmarks[eye_indices[1]] - landmarks[eye_indices[5]])
        v2 = np.linalg.norm(landmarks[eye_indices[2]] - landmarks[eye_indices[4]])
        h = np.linalg.norm(landmarks[eye_indices[0]] - landmarks[eye_indices[3]])
        return (v1 + v2) / (2.0 * h) if h != 0 else 0

    def analyze(self, frame):
        """รับภาพเข้ามา แล้วคืนค่า Dict ที่มีคะแนนต่างๆ กลับไป"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        data = {
            "detected": False,
            "energy_score": 0.0,
            "happiness_score": 0.0
        }

        if results.multi_face_landmarks:
            data["detected"] = True
            face_landmarks = results.multi_face_landmarks[0]
            
            h, w, _ = frame.shape
            coords = np.array([(lm.x * w, lm.y * h) for lm in face_landmarks.landmark])

            # 1. วิเคราะห์พลังงาน (ความเบิกกว้างของดวงตา)
            ear_left = self._calculate_ear(coords, self.LEFT_EYE)
            ear_right = self._calculate_ear(coords, self.RIGHT_EYE)
            avg_ear = (ear_left + ear_right) / 2.0
            data["energy_score"] = np.clip((avg_ear / 0.35) * 100, 0, 100)

            # 2. วิเคราะห์ความสุข (ระยะฉีกยิ้มเทียบกับระยะห่างของตา)
            mouth_width = np.linalg.norm(coords[self.MOUTH_CORNER_L] - coords[self.MOUTH_CORNER_R])
            eye_dist = np.linalg.norm(coords[self.LEFT_EYE[0]] - coords[self.RIGHT_EYE[3]])
            
            smile_ratio = mouth_width / eye_dist if eye_dist != 0 else 0
            data["happiness_score"] = np.clip(((smile_ratio - 0.7) / 0.3) * 100, 0, 100)

        return data