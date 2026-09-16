# -*- coding: utf-8 -*-
"""
controllers/stock_controller.py
ควบคุมการค้นหาสินค้าและปรับเพิ่ม/ลดจำนวนสต็อก สำหรับหน้า "เพิ่ม/ลดสต็อกสินค้า"
"""

from models import product as product_model
from models import log as log_model


def search_products(keyword: str):
    """ค้นหาสินค้าจากรหัสหรือชื่อ ใช้ในหน้าปรับสต็อก"""
    return product_model.get_all_products(keyword)


def adjust_stock(
    product_id, change_amount: int, reason: str, current_user: dict,
    unit_label: str = None, input_quantity: float = None,
):
    """
    เพิ่ม/ลดสต็อกสินค้า 1 รายการ
    change_amount: จำนวนที่เปลี่ยนแปลง เป็นหน่วยย่อยเสมอ (บวก = เพิ่มเข้าสต็อก, ลบ = ตัดออกจากสต็อก)
    unit_label/input_quantity: หน่วย/จำนวนตามที่ผู้ใช้กรอกจริงก่อนแปลงหน่วย (ถ้าไม่ระบุ จะใช้หน่วยย่อยของสินค้าเอง)
    """
    if change_amount == 0:
        raise ValueError("กรุณาระบุจำนวนที่ต้องการเพิ่มหรือลด (ต้องไม่เป็น 0)")

    product = product_model.get_product_by_id(product_id)
    if product is None:
        raise ValueError("ไม่พบสินค้านี้ในระบบ")

    if unit_label is None:
        unit_label = product["base_unit"]
    if input_quantity is None:
        input_quantity = abs(change_amount)

    new_quantity = product_model.adjust_stock(
        product_id, change_amount, reason, unit_label, input_quantity, current_user["id"]
    )

    direction_text = "เพิ่ม" if change_amount > 0 else "ลด"
    log_model.add_log(
        user_id=current_user["id"],
        user_role=current_user["role"],
        action="UPDATE",
        entity_type="Stock",
        entity_id=product_id,
        description=(
            f'{current_user["name"]} {direction_text}สต็อกสินค้า "{product["name"]}" '
            f'จำนวน {input_quantity:g} {unit_label} '
            f'(คงเหลือใหม่: {new_quantity} {product["base_unit"]}) เหตุผล: {reason or "-"}'
        ),
    )
    return new_quantity
