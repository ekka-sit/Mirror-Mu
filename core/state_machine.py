import time
import json
import random
from datetime import datetime
import os
from core.advisor import Advisor 
from core.shirt_color import ShirtColor # <-- เพิ่มการ import

class StateMachine:
    def __init__(self):
        self.STATE_IDLE = "IDLE"           
        self.STATE_DETECTING = "DETECTING" 
        self.STATE_GREETING = "GREETING"   
        self.STATE_SHIRT_COLOR = "SHIRT_COLOR" # <-- สถานะใหม่
        self.STATE_FORTUNE = "FORTUNE"     
        self.STATE_ADVICE = "ADVICE"       

        self.current_state = self.STATE_IDLE
        self.state_start_time = 0.0
        self.display_text = ""
        
        self.last_seen_time = 0.0
        self.face_timeout = 2.0  
        self.has_greeted = False
        self.reset_greeting_timeout = 30.0 
        
        self.medicine_reminded = False 
        self.score_samples = []      
        self.last_sample_time = 0.0  
        self.fortune_start_time = 0.0 

        self.chosen_fortune_id = ""
        self.chosen_fortune_text = ""

        self.greetings = self._load_json("data/greetings.json", {})
        self.fortunes = self._load_json("data/fortunes.json", {})
        self.advisor = Advisor()
        self.shirt_color = ShirtColor() # <-- เรียกใช้ตัวจัดการสีเสื้อ

    def _load_json(self, filepath, default_data):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_data

    def _get_time_of_day(self):
        hour = datetime.now().hour
        if 5 <= hour < 12: return "morning"
        elif 12 <= hour < 18: return "afternoon"
        else: return "evening"

    def update(self, face_detected, barcode_scanned=False, happiness=0.0, energy=0.0):
        current_time = time.time()

        if face_detected:
            self.last_seen_time = current_time

        if not face_detected:
            time_away = current_time - self.last_seen_time
            if time_away > self.reset_greeting_timeout:
                self.has_greeted = False

            if self.current_state in [self.STATE_SHIRT_COLOR, self.STATE_FORTUNE, self.STATE_ADVICE]:
                if time_away > 15.0: 
                    self.current_state = self.STATE_IDLE
                    self.display_text = ""
            else:
                if time_away > self.face_timeout:
                    self.current_state = self.STATE_IDLE
                    self.display_text = ""
            return self.current_state, self.display_text

        # เก็บตัวอย่างคะแนน
        if face_detected and self.current_state in [self.STATE_DETECTING, self.STATE_GREETING, self.STATE_SHIRT_COLOR]:
            if current_time - self.last_sample_time >= 2.0:
                self.score_samples.append((happiness, energy))
                self.last_sample_time = current_time

        # --- LOGIC สถานะต่างๆ ---
        if self.current_state == self.STATE_IDLE:
            if face_detected:
                self.current_state = self.STATE_DETECTING
                self.state_start_time = current_time
                self.score_samples = [] 
                self.medicine_reminded = False 

        elif self.current_state == self.STATE_DETECTING:
            if current_time - self.state_start_time >= 1.0:
                self.current_state = self.STATE_GREETING
                self.state_start_time = current_time 
                if not self.has_greeted:
                    time_period = self._get_time_of_day()
                    greeting_list = self.greetings.get("daily_greetings", {}).get(time_period, [{"text": "สวัสดีค่ะ"}])
                    self.display_text = random.choice(greeting_list).get("text", "สวัสดีค่ะ")
                    self.has_greeted = True 
                else:
                    self.display_text = "พร้อมดูแลคุณแล้วค่ะ"

        elif self.current_state == self.STATE_GREETING:
            elapsed = current_time - self.state_start_time
            # รอ 3 วิหลังจากทักทาย แล้วเปลี่ยนไปบอกสีเสื้อ
            if elapsed >= 3.0:
                self.current_state = self.STATE_SHIRT_COLOR
                self.state_start_time = current_time
                self.display_text = self.shirt_color.get_today_color()

        elif self.current_state == self.STATE_SHIRT_COLOR:
            elapsed = current_time - self.state_start_time
            # แสดงสีเสื้อไป 5 วินาที หรือจนกว่าจะมีการสแกนยา
            if elapsed >= 5.0 and not self.medicine_reminded:
                self.display_text = "อย่าลืมทานยาตามที่คุณหมอสั่งนะคะ \n(สแกนคิวอาร์โค้ดเพื่อรับคำทำนาย)"
                self.medicine_reminded = True

            if barcode_scanned:
                self.current_state = self.STATE_FORTUNE
                self.fortune_start_time = current_time 
                siamese_list = self.fortunes.get("siamese_predictions", [])
                if siamese_list:
                    chosen = random.choice(siamese_list)
                    self.chosen_fortune_id = str(chosen.get("id", "?"))
                    self.chosen_fortune_text = chosen.get("prediction", "ขอให้โชคดี!")
                else:
                    self.chosen_fortune_id = "1"; self.chosen_fortune_text = "ขอให้เป็นวันที่ดี!"

        elif self.current_state == self.STATE_FORTUNE:
            elapsed = current_time - self.fortune_start_time
            if elapsed < 3.0:
                self.display_text = "สแกนสำเร็จ!\nกำลังเขย่าเซียมซี..."
            elif elapsed < 6.0:
                self.display_text = f"คุณได้เซียมซีใบที่ {self.chosen_fortune_id}"
            elif elapsed < 13.0:
                self.display_text = self.chosen_fortune_text
            else:
                self.current_state = self.STATE_ADVICE
                self.display_text = self.advisor.get_advice(self.score_samples, happiness, energy)

        return self.current_state, self.display_text