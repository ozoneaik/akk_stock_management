# -*- coding: utf-8 -*-
"""
controllers/storage_controller.py
เป็นตัวกลางระหว่างหน้าจอ (views) กับ database/r2_storage.py
ตั้งชื่อไฟล์รูปสินค้าใหม่เป็น <รหัสสินค้า>_<timestamp>.<นามสกุลไฟล์> ก่อนอัปโหลดขึ้น Cloudflare R2 ทุกครั้ง
"""

import os
from datetime import datetime

from database import r2_storage


def upload_product_image(local_file_path: str, product_code: str) -> str:
    """อัปโหลดรูปสินค้าขึ้น R2 คืนค่า URL เต็มสำหรับเก็บลงคอลัมน์ image_url ในฐานข้อมูล"""
    ext = os.path.splitext(local_file_path)[1].lower()
    safe_code = (product_code or "product").strip().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{safe_code}_{timestamp}{ext}"
    object_key = f"images/{filename}"
    return r2_storage.upload_file(local_file_path, object_key)


def delete_product_image(image_url: str):
    """ลบรูปสินค้าเก่าออกจาก R2 เฉพาะกรณีที่ URL นั้นเป็นไฟล์ที่อัปโหลดขึ้น bucket นี้เองเท่านั้น"""
    object_key = r2_storage.object_key_from_url(image_url)
    if object_key:
        r2_storage.delete_file(object_key)
