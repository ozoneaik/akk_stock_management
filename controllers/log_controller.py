# -*- coding: utf-8 -*-
"""
controllers/log_controller.py
ดึงข้อมูลประวัติการทำงานสำหรับหน้า Activity Log (เห็นเฉพาะ admin เท่านั้น)
"""

from models import log as log_model

# key เป็น (entity_type, action) เพราะ action เดียวกัน (เช่น "UPDATE") ใช้ร่วมกันได้หลาย entity_type
# ความหมายจึงต่างกันไปตาม entity_type
ACTION_TYPE_LABELS = {
    ("Product", "CREATE"): "เพิ่มสินค้า",
    ("Product", "UPDATE"): "แก้ไขสินค้า",
    ("Product", "DELETE"): "ลบสินค้า",
    ("Stock", "UPDATE"): "ปรับสต็อก",
    ("User", "CREATE"): "เพิ่มผู้ใช้งาน",
    ("User", "UPDATE"): "แก้ไข/เข้าสู่ระบบ",
    ("User", "DELETE"): "ลบผู้ใช้งาน",
}


def get_logs():
    logs = log_model.get_all_logs()
    for entry in logs:
        key = (entry["entity_type"], entry["action"])
        entry["action_label"] = ACTION_TYPE_LABELS.get(key, f'{entry["entity_type"]} {entry["action"]}')
        entry["user_display_name"] = entry["user_display_name"] or "(ผู้ใช้ถูกลบไปแล้ว)"
    return logs
