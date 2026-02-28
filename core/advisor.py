import json
import random
import os

class Advisor:
    def __init__(self, filepath="data/advisor.json"):
        self.filepath = filepath
        self.emotion_feedback = self._load_json()

    def _load_json(self):
        """โหลดข้อมูลจากไฟล์ advisor.json"""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("emotion_feedback", {})
        
        print(f"⚠️ ไม่พบไฟล์ {self.filepath} จะใช้ข้อความเริ่มต้นแทน")
        return {}

    def get_advice(self, score_samples, current_hap, current_eng):
        """รับค่าคะแนนมาคำนวณเกรด และสุ่มคืนค่าคำแนะนำจาก JSON พร้อมบอกเกณฑ์"""
        # 1. หาค่าเฉลี่ย
        if len(score_samples) == 0:
            avg_hap = current_hap
            avg_eng = current_eng
        else:
            avg_hap = sum(s[0] for s in score_samples) / len(score_samples)
            avg_eng = sum(s[1] for s in score_samples) / len(score_samples)
            
        total_avg = (avg_hap + avg_eng) / 2.0
        
        # 2. ตัดเกรด และกำหนดชื่อเกณฑ์ภาษาไทย
        if total_avg >= 80:
            category = "very_good"
            status_text = "ดีมาก"
        elif total_avg >= 60:
            category = "good"
            status_text = "ดี"
        elif total_avg >= 40:
            category = "neutral"
            status_text = "ปานกลาง"
        else:
            category = "low"
            status_text = "ควรพักผ่อน"
            
        # 3. สุ่มข้อความตามหมวดหมู่จากไฟล์ JSON
        feedback_list = self.emotion_feedback.get(category, [{"text": "ขอให้สุขภาพกายและใจแข็งแรงนะคะ"}])
        
        if feedback_list:
            chosen_item = random.choice(feedback_list)
            advice_text = chosen_item.get("text", "รักษาสุขภาพด้วยนะคะ")
        else:
            advice_text = "รักษาสุขภาพด้วยนะคะ"

        # 4. ประกอบข้อความเข้าด้วยกัน (ใช้ \n เพื่อขึ้นบรรทัดใหม่)
        final_display_text = f"เกณฑ์ประเมินอารมณ์: {status_text}\nคำแนะนำ: {advice_text}"
        
        return final_display_text