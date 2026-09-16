# -*- coding: utf-8 -*-
"""
models/category.py
จัดการหมวดหมู่สินค้า เช่น ยาฮอร์โมน, ยาบำรุงราก, ยาเผาไหม้ ฯลฯ
"""

import uuid
from datetime import datetime

from database.db import get_connection


def get_all_categories():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM category ORDER BY sort_order, name")
        return cur.fetchall()
    finally:
        conn.close()


def get_or_create_category(name: str) -> str:
    """
    ถ้ามีหมวดหมู่นี้อยู่แล้วคืน id เดิม
    ถ้ายังไม่มีให้สร้างใหม่แล้วคืน id ที่สร้าง
    ใช้เวลาเพิ่ม/แก้ไขสินค้าเพื่อให้ผู้ใช้พิมพ์ชื่อหมวดหมู่ใหม่ได้เลยโดยไม่ต้องมีหน้าจัดการหมวดหมู่แยก
    """
    name = name.strip()
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM category WHERE name = %s", (name,))
        row = cur.fetchone()
        if row:
            return row["id"]

        cur.execute("SELECT COALESCE(MAX(sort_order), 0) as max_sort FROM category")
        next_sort = cur.fetchone()["max_sort"] + 1

        category_id = str(uuid.uuid4())
        now = datetime.now()
        cur.execute(
            "INSERT INTO category (id, name, sort_order, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
            (category_id, name, next_sort, now, now),
        )
        conn.commit()
        return category_id
    finally:
        conn.close()


def get_category_by_id(category_id):
    if category_id is None:
        return None
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM category WHERE id = %s", (category_id,))
        return cur.fetchone()
    finally:
        conn.close()
