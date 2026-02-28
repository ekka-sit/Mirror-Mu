import time
import json
import random
from datetime import datetime
import os

# --- นำเข้า Advisor ที่เราเพิ่งสร้าง ---
from core.advisor import Advisor 

class StateMachine:
    def __init__(self):
        self.STATE_IDLE = "IDLE"           
        self.STATE_DETECTING = "DETECTING" 
        self.STATE_GREETING = "GREETING"   
        self.STATE_FORTUNE = "FORTUNE"     
        self.STATE_ADVICE = "ADVICE"       

        self.current_state = self.STATE_IDLE
        self.state_start_time = 0.0
        self.display_text = ""
        
        self.last_seen_time = 0.0
        self.face_timeout = 2.0  
        self.has_greeted = False
        self.reset_greeting_timeout = 30.0 

        self.score_samples = []      
        self.last_sample_time = 0.0  
        self.fortune_start_time = 0.0 

        self.greetings = self._load_json("data/greetings.json", {})
        self.fortunes = self._load_json("data/fortunes.json", {})
        
        # --- เรียกใช้งานคลาส Advisor ---
        self.advisor = Advisor()

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

            if self.current_state in [self.STATE_FORTUNE, self.STATE_ADVICE]:
                if time_away > 15.0: 
                    self.current_state = self.STATE_IDLE
                    self.display_text = ""
                    self.score_samples = [] 
            else:
                if time_away > self.face_timeout:
                    if self.current_state != self.STATE_IDLE:
                        self.current_state = self.STATE_IDLE
                        self.display_text = ""
                        self.score_samples = [] 
                    return self.current_state, self.display_text

        if face_detected and self.current_state in [self.STATE_DETECTING, self.STATE_GREETING]:
            if current_time - self.last_sample_time >= 2.0:
                self.score_samples.append((happiness, energy))
                self.last_sample_time = current_time

        if self.current_state == self.STATE_IDLE:
            if face_detected:
                self.current_state = self.STATE_DETECTING
                self.state_start_time = current_time
                self.score_samples = [] 

        elif self.current_state == self.STATE_DETECTING:
            if current_time - self.state_start_time >= 3.0:
                self.current_state = self.STATE_GREETING
                
                if not self.has_greeted:
                    time_period = self._get_time_of_day()
                    daily_greetings = self.greetings.get("daily_greetings", {})
                    greeting_list = daily_greetings.get(time_period, [{"text": "สวัสดีค่ะ"}])
                    
                    chosen_item = random.choice(greeting_list)
                    self.display_text = chosen_item.get("text", "สวัสดีค่ะ")
                    self.has_greeted = True 
                else:
                    self.display_text = "พร้อมสแกนบาร์โค้ดหรือคิวอาร์โค้ดค่ะ" 

        elif self.current_state == self.STATE_GREETING:
            if barcode_scanned:
                self.current_state = self.STATE_FORTUNE
                self.fortune_start_time = current_time 
                
                siamese_list = self.fortunes.get("siamese_predictions", [])
                if siamese_list:
                    chosen_fortune = random.choice(siamese_list)
                    self.display_text = chosen_fortune.get("prediction", "ขอให้โชคดี!")
                else:
                    self.display_text = "ขอให้เป็นวันที่ดีนะคะ!"

        elif self.current_state == self.STATE_FORTUNE:
            if current_time - self.fortune_start_time >= 7.0:
                self.current_state = self.STATE_ADVICE
                
                # --- ย้ายไปเรียกใช้ฟังก์ชันจาก Advisor ---
                self.display_text = self.advisor.get_advice(
                    self.score_samples, 
                    happiness, 
                    energy
                )

        elif self.current_state == self.STATE_ADVICE:
            pass 

        return self.current_state, self.display_text

    # ลบฟังก์ชัน _calculate_and_show_advice เดิมทิ้งไปได้เลยครับ