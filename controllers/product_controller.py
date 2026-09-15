# -*- coding: utf-8 -*-
"""
controllers/product_controller.py
เป็นตัวกลางระหว่างหน้าจอ (views) กับ model สินค้า
หน้าที่หลัก: ตรวจสอบข้อมูลก่อนบันทึก และบันทึก activity log ทุกครั้งที่มีการ
เพิ่ม/แก้ไข/ลบสินค้า ตามข้อกำหนดของระบบ (ทุก action ต้องรู้ว่าใครเป็นคนทำ)
"""

from models import product as product_model
from models import category as category_model
from models import log as log_model


def get_categories():
    return category_model.get_all_categories()


def get_or_create_category(name: str):
    return category_model.get_or_create_category(name)


def list_products(search_text: str = None):
    return product_model.get_all_products(search_text)


def get_product(product_id):
    return product_model.get_product_by_id(product_id)


def get_dashboard_data():
    summary = product_model.get_total_stock_summary()
    low_stock = product_model.get_low_stock_products()
    return {
        "total_products": summary["total_products"],
        "total_quantity": summary["total_quantity"],
        "low_stock_items": low_stock,
        "low_stock_count": len(low_stock),
    }


def validate_product_data(data: dict) -> str:
    """คืนข้อความ error ถ้าข้อมูลไม่ถูกต้อง หรือคืน None ถ้าข้อมูลผ่าน"""
    if not data.get("code", "").strip():
        return "กรุณากรอกรหัสสินค้า"
    if not data.get("name", "").strip():
        return "กรุณากรอกชื่อสินค้า"
    if not data.get("packaging_unit", "").strip():
        return "กรุณากรอกหน่วยนับย่อย (เช่น ขวด, ซอง, ชิ้น)"
    try:
        if int(data.get("units_per_pack", 1)) <= 0:
            return "จำนวนหน่วยย่อยต่อแพ็คต้องมากกว่า 0"
    except (TypeError, ValueError):
        return "จำนวนหน่วยย่อยต่อแพ็คต้องเป็นตัวเลข"
    try:
        if int(data.get("quantity", 0)) < 0:
            return "จำนวนสินค้าต้องไม่ติดลบ"
    except (TypeError, ValueError):
        return "จำนวนสินค้าต้องเป็นตัวเลข"
    try:
        if int(data.get("low_stock_threshold", 10)) < 0:
            return "ค่าสต็อกขั้นต่ำต้องไม่ติดลบ"
    except (TypeError, ValueError):
        return "ค่าสต็อกขั้นต่ำต้องเป็นตัวเลข"
    return None


def create_product(data: dict, current_user: dict):
    error = validate_product_data(data)
    if error:
        raise ValueError(error)

    product_id = product_model.create_product(data, current_user["id"])
    log_model.add_log(
        user_id=current_user["id"],
        user_role=current_user["role"],
        action="CREATE",
        entity_type="Product",
        entity_id=product_id,
        description=f'{current_user["name"]} เพิ่มสินค้าใหม่ "{data["name"]}" (รหัส {data["code"]})',
    )
    return product_id


def update_product(product_id, data: dict, current_user: dict):
    error = validate_product_data(data)
    if error:
        raise ValueError(error)

    product_model.update_product(product_id, data, current_user["id"])
    log_model.add_log(
        user_id=current_user["id"],
        user_role=current_user["role"],
        action="UPDATE",
        entity_type="Product",
        entity_id=product_id,
        description=f'{current_user["name"]} แก้ไขข้อมูลสินค้า "{data["name"]}" (รหัส {data["code"]})',
    )


def delete_product(product_id, current_user: dict):
    product = product_model.get_product_by_id(product_id)
    if product is None:
        raise ValueError("ไม่พบสินค้านี้ในระบบ")

    product_model.deactivate_product(product_id)
    log_model.add_log(
        user_id=current_user["id"],
        user_role=current_user["role"],
        action="DELETE",
        entity_type="Product",
        entity_id=product_id,
        description=f'{current_user["name"]} ลบสินค้า "{product["name"]}" (รหัส {product["sku"]})',
    )
