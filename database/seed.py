# -*- coding: utf-8 -*-
"""
database/seed.py
ใส่ข้อมูลตัวอย่างเริ่มต้น: ผู้ใช้ 2 คน, หมวดหมู่สินค้า, และสินค้าตัวอย่างประมาณ 15 รายการ
(มีทั้งรายการที่สต็อกต่ำกว่า 10 เพื่อทดสอบการแจ้งเตือนใน Dashboard)

รันแยกได้ด้วยคำสั่ง: python -m database.seed
หรือถูกเรียกอัตโนมัติจาก main.py ถ้าฐานข้อมูลยังว่างอยู่ (ฟังก์ชันนี้จะข้ามการ seed
โดยอัตโนมัติถ้ามีผู้ใช้อยู่แล้ว)
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from database.db import init_db, is_database_empty
from database.migrate import safe_print
from models import user as user_model
from models import category as category_model
from models import product as product_model


SAMPLE_USERS = [
    {
        "username": "admin",
        "pin": "9999",
        "display_name": "แอดมินระบบ",
        "role": config.ROLE_ADMIN,
    },
    {
        "username": "owner",
        "pin": "1234",
        "display_name": "เจ้าของร้าน (คุณพ่อ)",
        "role": config.ROLE_OWNER,
    },
]

# (รหัสสินค้า, ชื่อสินค้า, หมวดหมู่, หน่วยนับย่อย, จำนวนคงเหลือ, สต็อกขั้นต่ำ, ราคาแต่ละช่องทาง{channel: (ราคา, ส่วนลด)})
SAMPLE_PRODUCTS = [
    (
        "FT-001", "ปุ๋ยเคมีสูตร 16-16-16 ตราหัววัว", "ปุ๋ยเคมี", "กระสอบ", 45, 10,
        {"STORE": (650, 0), "SHOPEE": (680, 30), "LAZADA": (680, 20)},
    ),
    (
        "FT-002", "ปุ๋ยยูเรีย 46-0-0", "ปุ๋ยเคมี", "กระสอบ", 8, 10,
        {"STORE": (580, 0), "TIKTOK": (600, 20)},
    ),
    (
        "HM-001", "ฮอร์โมนเร่งดอก ตราใบไม้ทอง", "ยาฮอร์โมน", "ขวด", 32, 10,
        {"STORE": (120, 0), "SHOPEE": (135, 5), "LAZADA": (135, 5), "TIKTOK": (130, 0)},
    ),
    (
        "HM-002", "ฮอร์โมนเร่งราก NAA", "ยาฮอร์โมน", "ขวด", 6, 10,
        {"STORE": (150, 0)},
    ),
    (
        "RT-001", "ปุ๋ยบำรุงราก สาหร่ายสกัด", "ยาบำรุงราก", "ขวด", 18, 10,
        {"STORE": (95, 0), "SHOPEE": (110, 10)},
    ),
    (
        "BN-001", "ยาเผาไหม้พาราควอต", "ยาเผาไหม้", "ขวด", 25, 10,
        {"STORE": (180, 0), "LAZADA": (195, 0)},
    ),
    (
        "BN-002", "ยาคุมหญ้าอะลาคลอร์", "ยาเผาไหม้", "แกลลอน", 4, 10,
        {"STORE": (420, 0)},
    ),
    (
        "SB-001", "ยาดูดซึมไกลโฟเซต", "ยาดูดซึม", "แกลลอน", 60, 10,
        {"STORE": (350, 0), "SHOPEE": (370, 20), "TIKTOK": (360, 0)},
    ),
    (
        "SB-002", "ยาดูดซึมกำจัดเพลี้ย อิมิดาคลอพริด", "ยาดูดซึม", "ขวด", 3, 10,
        {"STORE": (140, 0)},
    ),
    (
        "SD-001", "เมล็ดพันธุ์ข้าวโพดหวาน", "สินค้าการเกษตรทั่วไป", "ซอง", 120, 10,
        {"STORE": (35, 0), "SHOPEE": (40, 0)},
    ),
    (
        "SD-002", "เมล็ดพันธุ์ผักบุ้งจีน", "สินค้าการเกษตรทั่วไป", "ซอง", 95, 10,
        {"STORE": (20, 0)},
    ),
    (
        "EQ-001", "บัวรดน้ำพลาสติก 10 ลิตร", "อุปกรณ์การเกษตร", "ชิ้น", 22, 10,
        {"STORE": (150, 0), "LAZADA": (165, 0)},
    ),
    (
        "EQ-002", "ถังพ่นยาสะพายหลัง 16 ลิตร", "อุปกรณ์การเกษตร", "ชิ้น", 9, 10,
        {"STORE": (890, 0), "SHOPEE": (950, 50), "TIKTOK": (920, 0)},
    ),
    (
        "EQ-003", "จอบขุดดินด้ามไม้", "อุปกรณ์การเกษตร", "ชิ้น", 40, 10,
        {"STORE": (180, 0)},
    ),
    (
        "FT-003", "ปุ๋ยคอกอัดเม็ด ตราใบไผ่", "ปุ๋ยเคมี", "กระสอบ", 2, 10,
        {"STORE": (95, 0), "LAZADA": (105, 5)},
    ),
]


def seed_all():
    init_db()

    if not is_database_empty():
        safe_print("ฐานข้อมูลมีข้อมูลอยู่แล้ว ข้ามการ seed")
        return

    admin_user_id = None
    for u in SAMPLE_USERS:
        uid = user_model.create_user(u["username"], u["pin"], u["display_name"], u["role"])
        if u["role"] == config.ROLE_ADMIN:
            admin_user_id = uid

    for code, name, cat_name, unit, qty, threshold, prices in SAMPLE_PRODUCTS:
        category_id = category_model.get_or_create_category(cat_name)
        prices_dict = {ch: {"price": p, "discount": d} for ch, (p, d) in prices.items()}
        product_model.create_product(
            {
                "code": code,
                "name": name,
                "category_id": category_id,
                "packaging_unit": unit,
                "pack_unit": None,
                "units_per_pack": 1,
                "quantity": qty,
                "low_stock_threshold": threshold,
                "image_path": None,
                "note": "",
                "prices": prices_dict,
            },
            admin_user_id,
        )

    safe_print("Seed ข้อมูลตัวอย่างเรียบร้อยแล้ว")
    safe_print(f"  - ผู้ใช้: {len(SAMPLE_USERS)} คน (admin/PIN 9999, owner/PIN 1234)")
    safe_print(f"  - สินค้า: {len(SAMPLE_PRODUCTS)} รายการ")


if __name__ == "__main__":
    seed_all()
