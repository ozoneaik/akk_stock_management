# -*- coding: utf-8 -*-
"""
controllers/user_controller.py
เป็นตัวกลางระหว่างหน้าจอ "จัดการผู้ใช้งาน" กับ model ผู้ใช้
หน้าที่หลัก: ตรวจสอบข้อมูลก่อนบันทึก, กันไม่ให้ระบบเหลือ admin 0 คน,
และบันทึก activity log ทุกครั้งที่มีการเพิ่ม/แก้ไข/ลบผู้ใช้งาน
"""

import config
from models import user as user_model
from models import log as log_model

ROLE_LABELS = {
    config.ROLE_ADMIN: "แอดมิน",
    config.ROLE_OWNER: "เจ้าของร้าน",
}


def list_users():
    users = user_model.get_all_users()
    for u in users:
        u["role_label"] = ROLE_LABELS.get(u["role"], u["role"])
    return users


def validate_user_data(data: dict, is_edit: bool) -> str:
    """คืนข้อความ error ถ้าข้อมูลไม่ถูกต้อง หรือคืน None ถ้าข้อมูลผ่าน"""
    if not data.get("username", "").strip():
        return "กรุณากรอกชื่อผู้ใช้ (username)"
    if not data.get("display_name", "").strip():
        return "กรุณากรอกชื่อที่แสดง"
    if data.get("role") not in (config.ROLE_ADMIN, config.ROLE_OWNER):
        return "กรุณาเลือกบทบาทผู้ใช้"
    pin = data.get("pin", "")
    if not is_edit and not pin.strip():
        return "กรุณากำหนดรหัส PIN"
    if pin and not (pin.isdigit() and len(pin) == 4):
        return "PIN ต้องเป็นตัวเลข 4 หลัก"
    return None


def create_user(data: dict, current_user: dict) -> str:
    error = validate_user_data(data, is_edit=False)
    if error:
        raise ValueError(error)

    user_id = user_model.create_user(
        data["username"].strip(), data["pin"].strip(), data["display_name"].strip(), data["role"]
    )
    log_model.add_log(
        user_id=current_user["id"],
        user_role=current_user["role"],
        action="CREATE",
        entity_type="User",
        entity_id=user_id,
        description=f'{current_user["name"]} เพิ่มผู้ใช้งานใหม่ "{data["display_name"]}" ({data["username"]})',
    )
    return user_id


def update_user(user_id, data: dict, current_user: dict):
    error = validate_user_data(data, is_edit=True)
    if error:
        raise ValueError(error)

    target = user_model.get_user_by_id(user_id)
    if target is None:
        raise ValueError("ไม่พบผู้ใช้งานนี้ในระบบ")

    if target["role"] == config.ROLE_ADMIN and data["role"] != config.ROLE_ADMIN:
        if user_model.count_active_admins() <= 1:
            raise ValueError("ต้องมีผู้ใช้บทบาทแอดมินอย่างน้อย 1 คนในระบบเสมอ")

    user_model.update_user(user_id, data["display_name"].strip(), data["role"])
    if data.get("pin", "").strip():
        user_model.update_pin(user_id, data["pin"].strip())

    log_model.add_log(
        user_id=current_user["id"],
        user_role=current_user["role"],
        action="UPDATE",
        entity_type="User",
        entity_id=user_id,
        description=f'{current_user["name"]} แก้ไขข้อมูลผู้ใช้งาน "{data["display_name"]}" ({target["username"]})',
    )


def delete_user(user_id, current_user: dict):
    if user_id == current_user["id"]:
        raise ValueError("ไม่สามารถลบบัญชีผู้ใช้ที่กำลังใช้งานอยู่ได้")

    target = user_model.get_user_by_id(user_id)
    if target is None:
        raise ValueError("ไม่พบผู้ใช้งานนี้ในระบบ")

    if target["role"] == config.ROLE_ADMIN and user_model.count_active_admins() <= 1:
        raise ValueError("ต้องมีผู้ใช้บทบาทแอดมินอย่างน้อย 1 คนในระบบเสมอ")

    user_model.deactivate_user(user_id)
    log_model.add_log(
        user_id=current_user["id"],
        user_role=current_user["role"],
        action="DELETE",
        entity_type="User",
        entity_id=user_id,
        description=f'{current_user["name"]} ลบผู้ใช้งาน "{target["name"]}" ({target["username"]})',
    )
