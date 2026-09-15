# -*- coding: utf-8 -*-
"""
controllers/auth_controller.py
ควบคุมกระบวนการเข้าสู่ระบบ (ตัวกลางระหว่าง view กับ model ผู้ใช้)
เข้าสู่ระบบด้วย username + PIN 4 หลัก (ตรงกับ schema ที่ใช้ร่วมกับเว็บแอป)
"""

from models import user as user_model
from models import log as log_model
import config


def login(username: str, pin: str):
    """
    คืนค่า (user_dict, error_message)
    ถ้า login สำเร็จ error_message จะเป็น None
    ถ้าล้มเหลว user_dict จะเป็น None และ error_message จะบอกสาเหตุ
    """
    username = (username or "").strip()
    pin = (pin or "").strip()

    if not username or not pin:
        return None, "กรุณากรอกชื่อผู้ใช้และรหัส PIN ให้ครบถ้วน"

    user = user_model.authenticate(username, pin)
    if user is None:
        return None, "ชื่อผู้ใช้หรือรหัส PIN ไม่ถูกต้อง"

    log_model.add_log(
        user_id=user["id"],
        user_role=user["role"],
        action="UPDATE",
        entity_type="User",
        entity_id=user["id"],
        description=f'{user["name"]} เข้าสู่ระบบสำเร็จ',
    )

    return user, None


def is_admin(user: dict) -> bool:
    return bool(user) and user.get("role") == config.ROLE_ADMIN
