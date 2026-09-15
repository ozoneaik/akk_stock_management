# -*- coding: utf-8 -*-
"""
models/product.py
จัดการข้อมูลสินค้า: CRUD, ราคาหลายช่องทางขาย, และการปรับเพิ่ม/ลดสต็อก
"""

import uuid
from datetime import datetime

import config
from database.db import get_connection


def _now():
    return datetime.now()


def _new_id():
    return str(uuid.uuid4())


def _row_to_dict_with_prices(conn, row):
    product = dict(row)
    cur = conn.cursor()
    cur.execute(
        "SELECT channel, price, discountType, discountValue FROM ProductPrice WHERE productId = %s",
        (product["id"],),
    )
    product["prices"] = {
        r["channel"]: {
            "price": r["price"],
            "discount": r["discountValue"] if r["discountType"] != "NONE" else 0,
        }
        for r in cur.fetchall()
    }

    cur.execute("SELECT name FROM Category WHERE id = %s", (product["categoryId"],))
    cat_row = cur.fetchone()
    product["category_name"] = cat_row["name"] if cat_row else "ไม่ระบุหมวดหมู่"
    return product


def get_all_products(search_text: str = None):
    """ดึงสินค้าที่ยัง active อยู่ทั้งหมด พร้อมรองรับค้นหาจาก SKU หรือชื่อสินค้า"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        if search_text:
            like = f"%{search_text.strip()}%"
            cur.execute(
                "SELECT * FROM Product WHERE isActive = TRUE AND (sku LIKE %s OR name LIKE %s) ORDER BY name",
                (like, like),
            )
        else:
            cur.execute("SELECT * FROM Product WHERE isActive = TRUE ORDER BY name")
        rows = cur.fetchall()
        return [_row_to_dict_with_prices(conn, row) for row in rows]
    finally:
        conn.close()


def get_product_by_id(product_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Product WHERE id = %s", (product_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return _row_to_dict_with_prices(conn, row)
    finally:
        conn.close()


def get_low_stock_products():
    """สินค้าที่จำนวนคงเหลือน้อยกว่า minStockAlert ของตัวเอง"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM Product WHERE isActive = TRUE AND currentStock < minStockAlert ORDER BY currentStock ASC"
        )
        rows = cur.fetchall()
        return [_row_to_dict_with_prices(conn, row) for row in rows]
    finally:
        conn.close()


def get_total_stock_summary():
    """สรุปยอดรวมสำหรับหน้า Dashboard: จำนวนสินค้าทั้งหมด และจำนวนรวมของสต็อกทุกชิ้น"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) as total_products, COALESCE(SUM(currentStock), 0) as total_quantity "
            "FROM Product WHERE isActive = TRUE"
        )
        row = cur.fetchone()
        return {"total_products": row["total_products"], "total_quantity": row["total_quantity"]}
    finally:
        conn.close()


def create_product(data: dict, user_id: str) -> str:
    """
    สร้างสินค้าใหม่ คืนค่า id ที่สร้าง (string)
    data ต้องมี: code(sku), name, category_id, base_unit, pack_unit, units_per_pack,
                quantity, low_stock_threshold, image_url, note, prices (dict: {channel: {price, discount}})
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        now = _now()
        product_id = _new_id()
        cur.execute(
            """
            INSERT INTO Product
                (id, sku, name, categoryId, baseUnit, packUnit, unitsPerPack, currentStock,
                 minStockAlert, imageUrl, description, isActive, createdById, updatedById, createdAt, updatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                product_id,
                data["code"].strip() or None,
                data["name"].strip(),
                data.get("category_id"),
                data["packaging_unit"].strip(),
                data.get("pack_unit") or None,
                int(data.get("units_per_pack", 1)),
                int(data.get("quantity", 0)),
                int(data.get("low_stock_threshold", config.LOW_STOCK_DEFAULT_THRESHOLD)),
                data.get("image_path") or None,
                data.get("note") or None,
                True,
                user_id,
                user_id,
                now,
                now,
            ),
        )

        for channel, price_info in (data.get("prices") or {}).items():
            discount_value = float(price_info.get("discount", 0) or 0)
            cur.execute(
                """
                INSERT INTO ProductPrice (id, productId, channel, price, discountType, discountValue, updatedAt)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    _new_id(),
                    product_id,
                    channel,
                    float(price_info.get("price", 0)),
                    "FIXED" if discount_value else "NONE",
                    discount_value,
                    now,
                ),
            )

        conn.commit()
        return product_id
    finally:
        conn.close()


def update_product(product_id, data: dict, user_id: str):
    """แก้ไขข้อมูลสินค้าที่มีอยู่ (ไม่รวมจำนวนสต็อก ซึ่งต้องปรับผ่าน adjust_stock เพื่อให้มี log ที่ถูกต้อง)"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        now = _now()
        cur.execute(
            """
            UPDATE Product
            SET sku = %s, name = %s, categoryId = %s, baseUnit = %s, packUnit = %s, unitsPerPack = %s,
                minStockAlert = %s, imageUrl = %s, description = %s, updatedById = %s, updatedAt = %s
            WHERE id = %s
            """,
            (
                data["code"].strip() or None,
                data["name"].strip(),
                data.get("category_id"),
                data["packaging_unit"].strip(),
                data.get("pack_unit") or None,
                int(data.get("units_per_pack", 1)),
                int(data.get("low_stock_threshold", config.LOW_STOCK_DEFAULT_THRESHOLD)),
                data.get("image_path") or None,
                data.get("note") or None,
                user_id,
                now,
                product_id,
            ),
        )

        # อัปเดตราคา: ลบของเก่าแล้วใส่ใหม่ทั้งหมด ง่ายและชัดเจนกว่าการไล่ diff ทีละช่องทาง
        cur.execute("DELETE FROM ProductPrice WHERE productId = %s", (product_id,))
        for channel, price_info in (data.get("prices") or {}).items():
            discount_value = float(price_info.get("discount", 0) or 0)
            cur.execute(
                """
                INSERT INTO ProductPrice (id, productId, channel, price, discountType, discountValue, updatedAt)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    _new_id(),
                    product_id,
                    channel,
                    float(price_info.get("price", 0)),
                    "FIXED" if discount_value else "NONE",
                    discount_value,
                    now,
                ),
            )

        conn.commit()
    finally:
        conn.close()


def deactivate_product(product_id):
    """ลบสินค้าแบบ soft-delete (isActive = False) เก็บประวัติ StockMovement/ActivityLog ไว้ครบ"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE Product SET isActive = FALSE WHERE id = %s", (product_id,))
        conn.commit()
    finally:
        conn.close()


def adjust_stock(product_id, change_amount: int, reason: str, unit_label: str, input_quantity: float, user_id: str):
    """
    เพิ่ม/ลดจำนวนสต็อกสินค้า (change_amount เป็นบวก = เพิ่ม (IN), ลบ = ลด (OUT), หน่วยเป็นหน่วยย่อยเสมอ)
    unit_label/input_quantity: หน่วยและจำนวนตามที่ผู้ใช้กรอกจริง (ก่อนแปลงเป็นหน่วยย่อย) เก็บไว้เป็นประวัติ
    บันทึกลง StockMovement ด้วยทุกครั้งเพื่อดูประวัติย้อนหลังได้ (โครงสร้างตรงกับที่เว็บแอปใช้)
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT currentStock FROM Product WHERE id = %s", (product_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError("ไม่พบสินค้านี้ในระบบ")

        new_quantity = row["currentStock"] + change_amount
        if new_quantity < 0:
            raise ValueError("จำนวนสต็อกคงเหลือจะติดลบ กรุณาตรวจสอบจำนวนที่ต้องการลด")

        cur.execute("UPDATE Product SET currentStock = %s, updatedById = %s WHERE id = %s", (new_quantity, user_id, product_id))
        cur.execute(
            """
            INSERT INTO StockMovement
                (id, productId, type, quantity, inputUnit, inputQuantity, balanceBefore, balanceAfter,
                 note, createdById, createdAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                _new_id(),
                product_id,
                "IN" if change_amount > 0 else "OUT",
                abs(change_amount),
                unit_label,
                input_quantity,
                row["currentStock"],
                new_quantity,
                reason or None,
                user_id,
                _now(),
            ),
        )
        conn.commit()
        return new_quantity
    finally:
        conn.close()
