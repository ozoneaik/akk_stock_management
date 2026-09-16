# -*- coding: utf-8 -*-
"""
database/migrate.py
สร้างตารางทั้งหมดที่โปรแกรมต้องใช้ใน TiDB (MySQL-compatible) ถ้ายังไม่มี

เดิม schema ถูกจัดการโดยฝั่งเว็บแอป (web/) ผ่าน Prisma แต่ตอนนี้ web/ ถูกลบไปแล้ว
ฝั่ง Desktop นี้จึงต้องรับหน้าที่สร้างตารางเอง โครงสร้างตารางด้านล่างตรงกับที่ models/*.py ใช้งานอยู่ทุกตัวอักษร

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
    CREATE TABLE IF NOT EXISTS User (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        username VARCHAR(191) NOT NULL,
        name VARCHAR(191) NOT NULL,
        role VARCHAR(191) NOT NULL DEFAULT 'OWNER',
        pin VARCHAR(191) NULL,
        avatarUrl VARCHAR(191) NULL,
        isActive BOOLEAN NOT NULL DEFAULT TRUE,
        createdAt DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
        updatedAt DATETIME(3) NOT NULL,
        UNIQUE KEY User_username_key (username),
        KEY User_role_idx (role)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS Category (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        name VARCHAR(191) NOT NULL,
        description VARCHAR(191) NULL,
        color VARCHAR(191) NOT NULL DEFAULT '#2e7d32',
        iconName VARCHAR(191) NULL DEFAULT 'Sprout',
        sortOrder INT NOT NULL DEFAULT 0,
        createdAt DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
        updatedAt DATETIME(3) NOT NULL,
        UNIQUE KEY Category_name_key (name),
        KEY Category_sortOrder_idx (sortOrder)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS Product (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        sku VARCHAR(191) NULL,
        barcode VARCHAR(191) NULL,
        name VARCHAR(191) NOT NULL,
        commonName VARCHAR(191) NULL,
        description VARCHAR(191) NULL,
        imageUrl VARCHAR(191) NULL,
        categoryId VARCHAR(191) NOT NULL,
        baseUnit VARCHAR(191) NOT NULL DEFAULT 'ขวด',
        packUnit VARCHAR(191) NULL DEFAULT 'ลัง',
        unitsPerPack INT NOT NULL DEFAULT 12,
        currentStock INT NOT NULL DEFAULT 0,
        minStockAlert INT NOT NULL DEFAULT 10,
        isActive BOOLEAN NOT NULL DEFAULT TRUE,
        createdById VARCHAR(191) NULL,
        updatedById VARCHAR(191) NULL,
        createdAt DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
        updatedAt DATETIME(3) NOT NULL,
        UNIQUE KEY Product_sku_key (sku),
        UNIQUE KEY Product_barcode_key (barcode),
        KEY Product_categoryId_idx (categoryId),
        KEY Product_commonName_idx (commonName),
        KEY Product_createdById_idx (createdById),
        KEY Product_currentStock_idx (currentStock),
        KEY Product_name_idx (name),
        KEY Product_updatedById_idx (updatedById),
        CONSTRAINT Product_categoryId_fkey FOREIGN KEY (categoryId) REFERENCES Category(id),
        CONSTRAINT Product_createdById_fkey FOREIGN KEY (createdById) REFERENCES User(id),
        CONSTRAINT Product_updatedById_fkey FOREIGN KEY (updatedById) REFERENCES User(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS ProductPrice (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        productId VARCHAR(191) NOT NULL,
        channel VARCHAR(191) NOT NULL DEFAULT 'STORE',
        price DOUBLE NOT NULL,
        packPrice DOUBLE NULL,
        discountType VARCHAR(191) NOT NULL DEFAULT 'NONE',
        discountValue DOUBLE NOT NULL DEFAULT 0,
        discountStartDate DATETIME(3) NULL,
        discountEndDate DATETIME(3) NULL,
        note VARCHAR(191) NULL,
        updatedAt DATETIME(3) NOT NULL,
        UNIQUE KEY ProductPrice_productId_channel_key (productId, channel),
        KEY ProductPrice_channel_idx (channel),
        KEY ProductPrice_productId_idx (productId),
        CONSTRAINT ProductPrice_productId_fkey FOREIGN KEY (productId) REFERENCES Product(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS StockMovement (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        productId VARCHAR(191) NOT NULL,
        type VARCHAR(191) NOT NULL,
        quantity INT NOT NULL,
        inputUnit VARCHAR(191) NOT NULL,
        inputQuantity DOUBLE NOT NULL,
        balanceBefore INT NOT NULL,
        balanceAfter INT NOT NULL,
        referenceDoc VARCHAR(191) NULL,
        imageUrl VARCHAR(191) NULL,
        note VARCHAR(191) NULL,
        createdById VARCHAR(191) NOT NULL,
        createdAt DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
        KEY StockMovement_createdAt_idx (createdAt),
        KEY StockMovement_createdById_idx (createdById),
        KEY StockMovement_productId_idx (productId),
        KEY StockMovement_type_idx (type),
        CONSTRAINT StockMovement_productId_fkey FOREIGN KEY (productId) REFERENCES Product(id) ON DELETE CASCADE,
        CONSTRAINT StockMovement_createdById_fkey FOREIGN KEY (createdById) REFERENCES User(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """,
    """
    CREATE TABLE IF NOT EXISTS ActivityLog (
        id VARCHAR(191) NOT NULL PRIMARY KEY,
        action VARCHAR(191) NOT NULL,
        entityType VARCHAR(191) NOT NULL,
        entityId VARCHAR(191) NOT NULL,
        description VARCHAR(191) NOT NULL,
        preValue TEXT NULL,
        postValue TEXT NULL,
        userId VARCHAR(191) NOT NULL,
        userRole VARCHAR(191) NOT NULL DEFAULT 'OWNER',
        createdAt DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
        KEY ActivityLog_action_idx (action),
        KEY ActivityLog_createdAt_idx (createdAt),
        KEY ActivityLog_entityType_entityId_idx (entityType, entityId),
        KEY ActivityLog_userId_idx (userId),
        CONSTRAINT ActivityLog_userId_fkey FOREIGN KEY (userId) REFERENCES User(id)
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
