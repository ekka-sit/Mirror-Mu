import cv2

class Camera:
    def __init__(self, camera_index=0):
        """
        camera_index: 0 คือกล้องเว็บแคมตัวแรกของเครื่อง
        """
        self.camera_index = camera_index
        self.cap = None

    def start(self):
        """เปิดการทำงานของกล้อง"""
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index)
            # ตั้งค่าความละเอียดให้เหมาะสม ไม่ให้กินสเปคเกินไป
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def get_frame(self):
        """ดึงภาพ 1 เฟรม (พร้อมกลับซ้ายขวาให้เป็นกระจก)"""
        if self.cap is None or not self.cap.isOpened():
            return False, None
            
        success, frame = self.cap.read()
        if success:
            # กลับด้านภาพแนวนอน (Mirror Effect) 
            frame = cv2.flip(frame, 1)
        return success, frame

    def stop(self):
        """คืนทรัพยากรกล้องให้ระบบ"""
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            self.cap = None