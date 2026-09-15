# -*- coding: utf-8 -*-
"""
database/db.py
เชื่อมต่อฐานข้อมูล TiDB (MySQL-compatible) — ฐานข้อมูลเดียวกับที่เว็บแอป (web/) ใช้
schema ถูกจัดการโดยฝั่งเว็บ (Prisma) อยู่แล้ว ฝั่ง desktop นี้แค่เชื่อมต่อและอ่าน/เขียนข้อมูล
ไม่มีหน้าที่สร้างตาราง (ต่างจากตอนที่ยังใช้ SQLite ของตัวเอง)
"""

import os
import sys
from urllib.parse import urlparse

import pymysql
import pymysql.cursors

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def get_connection():
    """เปิด connection ไปยัง TiDB คืนค่าแถวเป็น dict (เข้าถึงด้วย row["column"] ได้เหมือนเดิม)"""
    url = urlparse(config.DATABASE_URL)
    return pymysql.connect(
        host=url.hostname,
        port=url.port or 3306,
        user=url.username,
        password=url.password,
        database=url.path.lstrip("/").split("?")[0],
        ssl={"ssl": {}},
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def init_db():
    """ไม่ต้องทำอะไร — schema ของ TiDB ถูกสร้าง/จัดการโดยฝั่งเว็บแอป (Prisma) อยู่แล้ว"""
    pass


def is_database_empty():
    """เช็คว่ายังไม่มีข้อมูลผู้ใช้เลยหรือไม่ (ใช้ตัดสินใจว่าต้อง seed ข้อมูลตัวอย่างหรือไม่)"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM User")
        row = cur.fetchone()
        return row["cnt"] == 0
    finally:
        conn.close()
