# -*- coding: utf-8 -*-
"""
main.py
จุดเริ่มต้นของโปรแกรม (Entry point)

การทำงาน:
1. สร้างฐานข้อมูลและตารางถ้ายังไม่มี (init_db)
2. ถ้าฐานข้อมูลยังว่างอยู่ (เปิดใช้งานครั้งแรก) จะ seed ข้อมูลตัวอย่างให้อัตโนมัติ
3. เปิดหน้าจอเข้าสู่ระบบ (Login)

วิธีรัน:
    python main.py
"""

from database.db import init_db, is_database_empty
from database.seed import seed_all
from views.login_view import run as run_login


def bootstrap():
    init_db()
    if is_database_empty():
        seed_all()


def main():
    bootstrap()
    run_login()


if __name__ == "__main__":
    main()
