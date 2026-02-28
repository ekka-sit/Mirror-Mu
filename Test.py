import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from pyzbar.pyzbar import decode  # <--- เพิ่มการนำเข้า pyzbar
from vision.camera import Camera
from vision.face_analyzer import FaceAnalyzer
from core.state_machine import StateMachine

def draw_thai_text(img, text, position, font_size, color_bgr):
    font_path = "C:/Windows/Fonts/tahoma.ttf" 
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    
    color_rgb = (color_bgr[2], color_bgr[1], color_bgr[0])
    draw.text(position, text, font=font, fill=color_rgb)
    
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def main():
    cam = Camera(camera_index=0)
    analyzer = FaceAnalyzer()
    sm = StateMachine()
    
    cam.start()
    print("🚀 เริ่มระบบ: สมอง (Core) + ตา (Vision) + บาร์โค้ด (Barcode)")
    print("💡 กด ESC เพื่อปิดโปรแกรม\n")

    while True:
        success, frame = cam.get_frame()
        if not success:
            break
            
        # 1. วิเคราะห์ใบหน้า
        data = analyzer.analyze(frame)
        is_face_detected = data["detected"]
        
        # 2. ตรวจจับบาร์โค้ดในภาพ
        barcodes = decode(frame)
        is_barcode_scanned = len(barcodes) > 0 # ถ้าเจอมากกว่า 0 แปลว่าสแกนติด
        
        # วาดกรอบสี่เหลี่ยมสีแดงรอบบาร์โค้ดบนกล้อง (เพื่อให้รู้ว่ากล้องอ่านเจอแล้ว)
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        # 3. ส่งข้อมูล (หน้า, บาร์โค้ด) ไปให้ State Machine ตัดสินใจ
        current_state, display_text = sm.update(is_face_detected, is_barcode_scanned)
        
        # --- ส่วนแสดงสถานะบนหน้าต่าง ---
        color = (0, 255, 0)
        if current_state == "IDLE": color = (150, 150, 150)
        elif current_state == "DETECTING": color = (0, 255, 255)
        elif current_state == "GREETING": color = (0, 200, 255)
        elif current_state == "FORTUNE": color = (255, 0, 255)

        face_status = "Face: YES" if is_face_detected else "Face: NO"
        barcode_status = "Barcode: SCANNED" if is_barcode_scanned else "Barcode: WAITING"
        
        cv2.putText(frame, face_status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, barcode_status, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"State: {current_state}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # --- ส่วนแสดงข้อความภาษาไทย ---
        if display_text:
            frame = draw_thai_text(frame, display_text, (20, 160), font_size=24, color_bgr=(0, 255, 255))

        cv2.imshow("Smart Mirror - Barcode & Face", frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cam.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()