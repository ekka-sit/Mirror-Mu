import json
import os
from datetime import datetime

class ShirtColor:
    def __init__(self, filepath="data/fortunesColor.json"):
        self.filepath = filepath
        self.color_data = self._load_json()

    def _load_json(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # ดึงก้อนข้อมูลหลักออกมา
                return data.get("lucky_colors_march_2026", [])
        return []

    def get_today_color(self):
        """ดึงข้อมูลสีเสื้อมงคลของวันนี้"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # ค้นหาข้อมูลที่ตรงกับวันที่ปัจจุบัน
        day_info = next((item for item in self.color_data if item["date"] == today_str), None)
        
        if day_info:
            text = (f"สีเสื้อมงคล{day_info['day_of_week']}นี้:\n"
                    f"งาน: {', '.join(day_info['work'])}\n"
                    f"เงิน: {', '.join(day_info['money'])}\n"
                    f"โชค: {', '.join(day_info['luck'])}")
            return text
        return "วันนี้ขอให้แต่งตัวด้วยความมั่นใจนะคะ"