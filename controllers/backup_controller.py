# -*- coding: utf-8 -*-
"""
controllers/backup_controller.py
สำรองข้อมูลจากฐานข้อมูลร่วม (TiDB) ออกเป็นไฟล์ JSON ไว้บนเครื่อง

หมายเหตุสำคัญ: ตั้งแต่ย้ายไปใช้ TiDB ที่ใช้ร่วมกับเว็บแอป (มีหลายคน/หลายอุปกรณ์เข้าถึงพร้อมกันได้)
ฟีเจอร์ "กู้คืนข้อมูล" แบบเขียนทับทั้งฐานข้อมูล (เหมือนตอนใช้ SQLite ไฟล์เดียว) ถูกตัดออกไปแล้ว
เพราะเสี่ยงเขียนทับข้อมูลที่คนอื่นกำลังใช้งานอยู่จริงบนเว็บ/เครื่องอื่นพร้อมกัน โดยไม่มีทางแจ้งเตือนได้
การกู้คืนข้อมูลของ TiDB Cloud ควรทำผ่านฟีเจอร์ Backup/PITR ในหน้าคอนโซลของ TiDB Cloud โดยตรงแทน
ไฟล์ JSON ที่ export ออกมาจากที่นี่ใช้เป็นสำเนาสำรองไว้ดูย้อนหลัง/ตรวจสอบข้อมูลเท่านั้น
"""

import json
from datetime import datetime

from database.db import get_connection

EXPORTED_TABLES = ["User", "Category", "Product", "ProductPrice", "StockMovement", "ActivityLog"]


def default_export_filename() -> str:
    return f"wtp2021_stock_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


def _serialize(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def export_snapshot(destination_path: str, current_user: dict):
    conn = get_connection()
    try:
        cur = conn.cursor()
        snapshot = {}
        for table in EXPORTED_TABLES:
            cur.execute(f"SELECT * FROM `{table}`")
            rows = cur.fetchall()
            for row in rows:
                # ไม่เอา PIN ติดไปกับไฟล์ export เพราะเป็นข้อมูลสำหรับ login โดยตรง
                row.pop("pin", None)
            snapshot[table] = [{k: _serialize(v) for k, v in row.items()} for row in rows]
    finally:
        conn.close()

    snapshot["_exportedAt"] = datetime.now().isoformat()
    snapshot["_exportedBy"] = current_user.get("name")

    with open(destination_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
