# -*- coding: utf-8 -*-
"""
config.py
ค่าคงที่และการตั้งค่าต่างๆ ของระบบ อยู่รวมกันที่นี่ที่เดียว

หมายเหตุ: ตั้งแต่ย้ายฐานข้อมูลไปใช้ TiDB (MySQL) ร่วมกับเว็บแอป (โฟลเดอร์ web/)
ค่าคงที่ที่เกี่ยวกับ schema (ชื่อ role, ชื่อช่องทางขาย) ต้องตรงกับที่เว็บแอปใช้ทุกตัวอักษร
เพราะเป็นฐานข้อมูลเดียวกัน แก้ฝั่งเดียวไม่ได้
"""

import os

from dotenv import load_dotenv

# --- Path หลักของโปรเจกต์ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DATABASE_URL = os.environ["DATABASE_URL"]

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
DEFAULT_PRODUCT_IMAGE = os.path.join(IMAGES_DIR, "default.png")

# --- Cloudflare R2 (เก็บรูปภาพสินค้า) ---
R2_ACCOUNT_ID = os.environ.get("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME")
R2_ENDPOINT = os.environ.get("R2_ENDPOINT")
R2_PUBLIC_URL = os.environ.get("R2_PUBLIC_URL")

# --- ข้อมูลทั่วไปของแอป ---
APP_TITLE = "ระบบจัดการสต็อกสินค้า - ออฟกิจเกษตร"
APP_MIN_WIDTH = 1100
APP_MIN_HEIGHT = 680

# --- ค่าตั้งต้นของสต็อกขั้นต่ำ (แจ้งเตือนเมื่อสินค้าเหลือน้อยกว่านี้) ---
LOW_STOCK_DEFAULT_THRESHOLD = 10

# --- ฟอนต์ที่ใช้ในระบบ ---
# Tahoma มากับ Windows ทุกเครื่องเป็นค่าเริ่มต้นและรองรับภาษาไทยได้ดี
# จึงไม่ต้องติดตั้งฟอนต์เพิ่มเติมใดๆ
UI_FONT_FAMILY = "Tahoma"
UI_FONT_SIZE_NORMAL = 10
UI_FONT_SIZE_HEADER = 14
UI_FONT_SIZE_TITLE = 18

# --- ช่องทางการขาย (ค่าที่เก็บจริงในฐานข้อมูล ต้องตรงกับเว็บแอปทุกตัวอักษร) ---
SALES_CHANNELS = ["STORE", "TIKTOK", "LAZADA", "SHOPEE"]
CHANNEL_LABELS = {
    "STORE": "หน้าร้าน",
    "TIKTOK": "TikTok",
    "LAZADA": "Lazada",
    "SHOPEE": "Shopee",
}

# --- หน่วยบรรจุตัวอย่าง (ผู้ใช้พิมพ์เพิ่มเองได้ ไม่ได้บังคับเป็น list ตายตัว) ---
DEFAULT_PACKAGING_UNITS = ["ลัง", "ขวด", "ซอง", "ถุง", "ชิ้น", "กระสอบ"]

# --- บทบาทผู้ใช้งาน (ตัวพิมพ์ใหญ่ ต้องตรงกับ enum ที่เว็บแอปใช้) ---
ROLE_ADMIN = "ADMIN"
ROLE_OWNER = "OWNER"
