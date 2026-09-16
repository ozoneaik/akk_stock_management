# -*- coding: utf-8 -*-
"""
models/user.py
จัดการข้อมูลผู้ใช้งานและการเข้าสู่ระบบ

หมายเหตุ: schema ของฐานข้อมูลร่วม (TiDB) ออกแบบให้ login ด้วย PIN 4 หลัก (ไม่ใช่ password)
เพื่อให้เหมาะกับฝั่งเว็บที่ใช้งานบนมือถือ/iPad เป็นหลัก desktop นี้จึงต้อง login ด้วย PIN เช่นกัน
"""

import uuid
from datetime import datetime

from database.db import get_connection


def _now():
    return datetime.now()


def create_user(username: str, pin: str, name: str, role: str) -> str:
    """สร้างผู้ใช้ใหม่ คืนค่า id ที่สร้าง (string)"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        user_id = str(uuid.uuid4())
        now = _now()
        cur.execute(
            """
            INSERT INTO user (id, username, name, role, pin, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, username, name, role, pin, True, now, now),
        )
        conn.commit()
        return user_id
    finally:
        conn.close()


def authenticate(username: str, pin: str):
    """ตรวจสอบ username/PIN คืนค่า dict ข้อมูลผู้ใช้ถ้าถูกต้อง หรือ None ถ้าผิด"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE username = %s", (username,))
        row = cur.fetchone()
        if row is None or not row["is_active"]:
            return None
        if row["pin"] != pin:
            return None
        return row
    finally:
        conn.close()


def get_user_by_id(user_id):
    if user_id is None:
        return None
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        return cur.fetchone()
    finally:
        conn.close()


def get_all_users(active_only: bool = True):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if active_only:
            cur.execute("SELECT * FROM user WHERE is_active = TRUE ORDER BY username")
        else:
            cur.execute("SELECT * FROM user ORDER BY username")
        return cur.fetchall()
    finally:
        conn.close()


def count_active_admins() -> int:
    """นับจำนวนผู้ใช้ role ADMIN ที่ยังใช้งานอยู่ ใช้ป้องกันไม่ให้ระบบเหลือ admin 0 คน"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM user WHERE role = 'ADMIN' AND is_active = TRUE")
        return cur.fetchone()["cnt"]
    finally:
        conn.close()


def update_user(user_id: str, name: str, role: str):
    """แก้ไขชื่อที่แสดงและบทบาทของผู้ใช้ (ไม่รวม PIN ใช้ update_pin แยกต่างหาก)"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE user SET name = %s, role = %s, updated_at = %s WHERE id = %s",
            (name, role, _now(), user_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_pin(user_id: str, new_pin: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE user SET pin = %s, updated_at = %s WHERE id = %s", (new_pin, _now(), user_id))
        conn.commit()
    finally:
        conn.close()


def deactivate_user(user_id: str):
    """ลบผู้ใช้แบบ soft-delete (ตั้ง is_active = False) เพราะมี FK จากตารางอื่นอ้างถึงผู้ใช้อยู่
    (stock_movement, activity_log) การลบจริงจะชนกับ constraint ถ้าผู้ใช้เคยทำรายการใดๆ ไว้"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE user SET is_active = FALSE, updated_at = %s WHERE id = %s", (_now(), user_id))
        conn.commit()
    finally:
        conn.close()
