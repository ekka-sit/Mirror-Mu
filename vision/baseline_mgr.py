import json
import os

class BaselineManager:
    def __init__(self, filepath="data/baselines.json"):
        """กำหนดพาธของไฟล์ฐานข้อมูล JSON"""
        self.filepath = filepath
        self.baselines = self._load_data()

    def _load_data(self):
        """อ่านไฟล์ JSON หากไม่มีไฟล์ให้สร้างค่าเริ่มต้น (Default)"""
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # ค่า Default กรณีเปิดใช้งานครั้งแรก
        return {
            "normal": {"energy": 75.0, "happiness": 50.0},
            "wakeup": {"energy": 40.0, "happiness": 20.0}
        }

    def save_baseline(self, mode, energy, happiness):
        """
        บันทึกค่าทับลงไป
        mode: ควรใส่ค่า 'normal' (หน้าปกติ) หรือ 'wakeup' (หน้าตอนตื่นนอน)
        """
        self.baselines[mode] = {
            "energy": round(energy, 2),
            "happiness": round(happiness, 2)
        }
        
        # ตรวจสอบว่ามีโฟลเดอร์ data/ หรือยัง ถ้าไม่มีให้สร้าง
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.baselines, f, indent=4)
        print(f"บันทึกค่าโหมด '{mode}' สำเร็จ!")

    def get_baseline(self, mode):
        """ดึงค่า Baseline ออกมาใช้งาน"""
        return self.baselines.get(mode, {"energy": 50.0, "happiness": 50.0})
    
    def compare_with_baseline(self, current_energy, current_happiness):
        """
        หาค่าส่วนต่าง (%) ว่าปัจจุบันต่างจากโหมด 'normal' แค่ไหน
        (เอาไว้ส่งให้ระบบ Advisor วิเคราะห์คำพูด)
        """
        normal = self.get_baseline("normal")
        energy_diff = current_energy - normal["energy"]
        happiness_diff = current_happiness - normal["happiness"]
        
        return {
            "energy_diff": round(energy_diff, 2),
            "happiness_diff": round(happiness_diff, 2)
        }