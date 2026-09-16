# -*- coding: utf-8 -*-
"""
database/r2_storage.py
เชื่อมต่อ Cloudflare R2 (S3-compatible object storage) สำหรับอัปโหลด/ลบไฟล์รูปภาพสินค้า
"""

import mimetypes
import os
import sys

import boto3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def get_client():
    return boto3.client(
        "s3",
        endpoint_url=config.R2_ENDPOINT,
        aws_access_key_id=config.R2_ACCESS_KEY_ID,
        aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def upload_file(local_path: str, object_key: str) -> str:
    """อัปโหลดไฟล์ขึ้น R2 ด้วย object_key ที่กำหนด คืนค่า URL เต็มสำหรับเก็บลงฐานข้อมูล"""
    client = get_client()
    content_type = mimetypes.guess_type(local_path)[0] or "application/octet-stream"
    client.upload_file(
        local_path, config.R2_BUCKET_NAME, object_key,
        ExtraArgs={"ContentType": content_type},
    )
    return f"{config.R2_PUBLIC_URL.rstrip('/')}/{os.path.basename(object_key)}"


def delete_file(object_key: str):
    """ลบไฟล์ออกจาก R2 เงียบๆ ถ้าลบไม่สำเร็จ (เช่น ไฟล์ถูกลบไปแล้ว/เน็ตหลุด) ไม่ต้อง throw ให้กระทบ flow หลัก"""
    try:
        get_client().delete_object(Bucket=config.R2_BUCKET_NAME, Key=object_key)
    except Exception:
        pass


def object_key_from_url(url: str):
    """แปลง URL เต็มที่เก็บในฐานข้อมูลกลับเป็น object key ไว้ลบไฟล์ คืนค่า None ถ้า URL ไม่ได้มาจาก R2 bucket นี้
    (กันลบไฟล์ผิดตัวกรณีมี URL ภายนอกที่เคยกรอกด้วยมือค้างอยู่)
    """
    if not url or not config.R2_PUBLIC_URL or not url.startswith(config.R2_PUBLIC_URL.rstrip("/") + "/"):
        return None
    filename = url[len(config.R2_PUBLIC_URL.rstrip("/")) + 1:]
    return f"images/{filename}"
