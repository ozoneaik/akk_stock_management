# -*- coding: utf-8 -*-
"""
database/migrate.py
สร้างตารางทั้งหมดที่โปรแกรมต้องใช้ใน TiDB (MySQL-compatible) ถ้ายังไม่มี

ชื่อตาราง/คอลัมน์ทั้งหมดเป็น snake_case ตัวพิมพ์เล็ก โครงสร้างตารางด้านล่างตรงกับที่
models/*.py ใช้งานอยู่ทุกตัวอักษร

รันแยกได้ด้วยคำสั่ง: python -m database.migrate
หรือถูกเรียกอัตโนมัติจาก database.db.init_db() ทุกครั้งที่โปรแกรมเริ่มทำงาน (ใช้ CREATE TABLE IF NOT EXISTS
จึงปลอดภัย รันซ้ำได้เรื่อยๆ ไม่ลบ/ทับข้อมูลเดิม)
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_connection


def safe_print(message: str):
    """print() ธรรมดา แต่กันเหนียวไม่ให้โปรแกรมพังตอน bootstrap ถ้า console ของ Windows
    ไม่รองรับภาษาไทย (เช่น cp1252) — เคยเจอ UnicodeEncodeError ตอนรันจาก cmd.exe เริ่มต้น"""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8", errors="replace"))


# เรียงตามลำดับ dependency (FK) ต้องสร้างตารางที่ถูกอ้างอิงก่อน
STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS user (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        username VARCHAR(191) NOT NULL,
        name VARCHAR(191) NOT NULL,
        role VARCHAR(191) NOT NULL DEFAULT 'OWNER',
        pin VARCHAR(191) NULL,
        avatar_url VARCHAR(191) NULL,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
        updated_at DATETIME(3) NOT NULL,
        UNIQUE KEY user_username_key (username),
        KEY user_role_idx (role)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS category (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        name VARCHAR(191) NOT NULL,
        description VARCHAR(191) NULL,
        color VARCHAR(191) NOT NULL DEFAULT '#2e7d32',
        icon_name VARCHAR(191) NULL DEFAULT 'Sprout',
        sort_order INT NOT NULL DEFAULT 0,
        created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
        updated_at DATETIME(3) NOT NULL,
        UNIQUE KEY category_name_key (name),
        KEY category_sort_order_idx (sort_order)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS product (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        sku VARCHAR(191) NULL,
        barcode VARCHAR(191) NULL,
        name VARCHAR(191) NOT NULL,
        common_name VARCHAR(191) NULL,
        description VARCHAR(191) NULL,
        image_url VARCHAR(191) NULL,
        category_id VARCHAR(191) NOT NULL,
        base_unit VARCHAR(191) NOT NULL DEFAULT 'ขวด',
        pack_unit VARCHAR(191) NULL DEFAULT 'ลัง',
        units_per_pack INT NOT NULL DEFAULT 12,
        current_stock INT NOT NULL DEFAULT 0,
        min_stock_alert INT NOT NULL DEFAULT 10,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_by_id VARCHAR(191) NULL,
        updated_by_id VARCHAR(191) NULL,
        created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
        updated_at DATETIME(3) NOT NULL,
        UNIQUE KEY product_sku_key (sku),
        UNIQUE KEY product_barcode_key (barcode),
        KEY product_category_id_idx (category_id),
        KEY product_common_name_idx (common_name),
        KEY product_created_by_id_idx (created_by_id),
        KEY product_current_stock_idx (current_stock),
        KEY product_name_idx (name),
        KEY product_updated_by_id_idx (updated_by_id),
        CONSTRAINT product_category_id_fkey FOREIGN KEY (category_id) REFERENCES category(id),
        CONSTRAINT product_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES user(id),
        CONSTRAINT product_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES user(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS product_price (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        product_id VARCHAR(191) NOT NULL,
        channel VARCHAR(191) NOT NULL DEFAULT 'STORE',
        price DOUBLE NOT NULL,
        pack_price DOUBLE NULL,
        discount_type VARCHAR(191) NOT NULL DEFAULT 'NONE',
        discount_value DOUBLE NOT NULL DEFAULT 0,
        discount_start_date DATETIME(3) NULL,
        discount_end_date DATETIME(3) NULL,
        note VARCHAR(191) NULL,
        updated_at DATETIME(3) NOT NULL,
        UNIQUE KEY product_price_product_id_channel_key (product_id, channel),
        KEY product_price_channel_idx (channel),
        KEY product_price_product_id_idx (product_id),
        CONSTRAINT product_price_product_id_fkey FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS stock_movement (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        product_id VARCHAR(191) NOT NULL,
        type VARCHAR(191) NOT NULL,
        quantity INT NOT NULL,
        input_unit VARCHAR(191) NOT NULL,
        input_quantity DOUBLE NOT NULL,
        balance_before INT NOT NULL,
        balance_after INT NOT NULL,
        reference_doc VARCHAR(191) NULL,
        image_url VARCHAR(191) NULL,
        note VARCHAR(191) NULL,
        created_by_id VARCHAR(191) NOT NULL,
        created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
        KEY stock_movement_created_at_idx (created_at),
        KEY stock_movement_created_by_id_idx (created_by_id),
        KEY stock_movement_product_id_idx (product_id),
        KEY stock_movement_type_idx (type),
        CONSTRAINT stock_movement_product_id_fkey FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
        CONSTRAINT stock_movement_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES user(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS activity_log (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        action VARCHAR(191) NOT NULL,
        entity_type VARCHAR(191) NOT NULL,
        entity_id VARCHAR(191) NOT NULL,
        description VARCHAR(191) NOT NULL,
        pre_value TEXT NULL,
        post_value TEXT NULL,
        user_id VARCHAR(191) NOT NULL,
        user_role VARCHAR(191) NOT NULL DEFAULT 'OWNER',
        created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
        KEY activity_log_action_idx (action),
        KEY activity_log_created_at_idx (created_at),
        KEY activity_log_entity_type_entity_id_idx (entity_type, entity_id),
        KEY activity_log_user_id_idx (user_id),
        CONSTRAINT activity_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES user(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
]


def migrate():
    """สร้างตารางทั้งหมดถ้ายังไม่มี (ปลอดภัย รันซ้ำได้)"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        for statement in STATEMENTS:
            cur.execute(statement)
        conn.commit()
        safe_print("Migrate: สร้าง/ตรวจสอบตารางครบทุกตารางเรียบร้อยแล้ว")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
