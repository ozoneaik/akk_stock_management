# -*- coding: utf-8 -*-
"""
models/log.py
บันทึกและดึงประวัติการทำงาน พร้อมชื่อผู้ใช้ที่กระทำ
หน้า Activity Log (admin เท่านั้น) จะดึงข้อมูลจากที่นี่
"""

import uuid
from datetime import datetime

from database.db import get_connection


def add_log(user_id: str, user_role: str, action: str, entity_type: str, entity_id: str, description: str):
    """
    บันทึก log หนึ่งรายการ
    action: 'CREATE' | 'UPDATE' | 'DELETE'
    entity_type: 'Product' | 'User' | 'Stock'
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO ActivityLog (id, action, entityType, entityId, description, userId, userRole, createdAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (str(uuid.uuid4()), action, entity_type, str(entity_id), description, user_id, user_role, datetime.now()),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_logs(limit: int = 500):
    """ดึงประวัติทั้งหมด เรียงจากล่าสุดไปเก่าสุด พร้อม join ชื่อผู้ใช้มาด้วยเลย"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                ActivityLog.*,
                User.name AS user_display_name,
                User.username AS username
            FROM ActivityLog
            LEFT JOIN User ON User.id = ActivityLog.userId
            ORDER BY ActivityLog.createdAt DESC
            LIMIT %s
            """,
            (limit,),
        )
        return cur.fetchall()
    finally:
        conn.close()
