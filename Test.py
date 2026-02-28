import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from pyzbar.pyzbar import decode
import textwrap 
import time  # <--- อย่าลืม import time ตรงนี้นะครับ

from vision.camera import Camera
from vision.face_analyzer import FaceAnalyzer
from core.state_machine import StateMachine

def draw_thai_text(img, text, position, font_size, color_bgr, max_chars=40):
    font_path = "C:/Windows/Fonts/tahoma.ttf" 
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    color_rgb = (color_bgr[2], color_bgr[1], color_bgr[0])
    
    x, y = position
    line_spacing = font_size + 10 
    
    raw_lines = text.split('\n')
    wrapped_lines = []
    
    for line in raw_lines:
        wrapped = textwrap.wrap(line, width=max_chars)
        if not wrapped:
            wrapped_lines.append("") 
        else:
            wrapped_lines.extend(wrapped)
            
    for i, line in enumerate(wrapped_lines):
        current_y = y + (i * line_spacing)
        draw.text((x, current_y), line, font=font, fill=color_rgb)
        
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def main():
    cam = Camera(camera_index=0)
    analyzer = FaceAnalyzer()
    sm = StateMachine()
    
    cam.start()
    print("🚀 เริ่มระบบ: สมอง + ตา + สแกน + ประเมินสุขภาพจิต")
    print("💡 กด ESC เพื่อปิดโปรแกรม\n")

    # --- เพิ่มตัวแปรสำหรับจำค่าคะแนนและเวลาที่อัปเดตล่าสุด ---
    last_score_update_time = time.time()
    display_hap = 0.0
    display_eng = 0.0

    while True:
        success, frame = cam.get_frame()
        if not success:
            break
            
        # 1. วิเคราะห์ใบหน้า (ดึงคะแนน Happiness / Energy แบบ Realtime)
        data = analyzer.analyze(frame)
        is_face_detected = data["detected"]
        raw_hap_score = data.get("happiness_score", 0.0)
        raw_eng_score = data.get("energy_score", 0.0)
        
        # --- ระบบหน่วงเวลาตัวเลขบนจอ (อัปเดตทุก 2 วินาที) ---
        current_time = time.time()
        if current_time - last_score_update_time >= 2.0:
            display_hap = raw_hap_score
            display_eng = raw_eng_score
            last_score_update_time = current_time
        
        # 2. ตรวจจับบาร์โค้ด / คิวอาร์โค้ด
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray_frame)
        is_barcode_scanned = len(barcodes) > 0 
        
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        # 3. ส่งข้อมูลให้ State Machine (ส่งค่า raw แบบปกติ เพื่อให้ระบบเก็บข้อมูลได้แม่นยำ)
        current_state, display_text = sm.update(
            face_detected=is_face_detected, 
            barcode_scanned=is_barcode_scanned,
            happiness=raw_hap_score, 
            energy=raw_eng_score
        )
        
        # --- ส่วนแสดงสถานะบนหน้าต่าง (Debug) ---
        color = (0, 255, 0)
        if current_state == "IDLE": color = (150, 150, 150)
        elif current_state == "DETECTING": color = (0, 255, 255)
        elif current_state == "GREETING": color = (0, 200, 255)
        elif current_state == "FORTUNE": color = (255, 0, 255)
        elif current_state == "ADVICE": color = (0, 255, 100) 

        face_status = "Face: YES" if is_face_detected else "Face: NO"
        cv2.putText(frame, face_status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"State: {current_state}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # โชว์ค่าคะแนนบนจอ (โดยใช้ตัวแปร display ที่อัปเดตทุก 2 วิ)
        if is_face_detected:
            cv2.putText(frame, f"Hap: {display_hap:.0f} | Eng: {display_eng:.0f}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

        # --- ส่วนแสดงข้อความภาษาไทย ---
        if display_text:
            frame = draw_thai_text(frame, display_text, (20, 150), font_size=26, color_bgr=(0, 255, 255), max_chars=45)

        cv2.imshow("Smart Mirror - Health & Fortune", frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cam.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()