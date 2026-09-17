// ค่าคงที่ที่ต้องตรงกับ config.py ฝั่งโปรแกรม desktop ทุกตัวอักษร เพราะใช้ฐานข้อมูลร่วมกัน

export const ROLE_ADMIN = "ADMIN";
export const ROLE_OWNER = "OWNER";
export const ROLES = [ROLE_ADMIN, ROLE_OWNER] as const;
export type Role = (typeof ROLES)[number];

export const ROLE_LABELS: Record<string, string> = {
  [ROLE_ADMIN]: "แอดมิน",
  [ROLE_OWNER]: "เจ้าของร้าน",
};

export const SALES_CHANNELS = ["STORE", "TIKTOK", "LAZADA", "SHOPEE"] as const;
export type SalesChannel = (typeof SALES_CHANNELS)[number];

export const CHANNEL_LABELS: Record<string, string> = {
  STORE: "หน้าร้าน",
  TIKTOK: "TikTok",
  LAZADA: "Lazada",
  SHOPEE: "Shopee",
};

export const DEFAULT_PACKAGING_UNITS = ["ลัง", "ขวด", "ซอง", "ถุง", "ชิ้น", "กระสอบ"];

export const LOW_STOCK_DEFAULT_THRESHOLD = 10;

// key เป็น "entityType:action" เพราะ action เดียวกัน (เช่น "UPDATE") ใช้ร่วมกันได้หลาย entityType
export const ACTION_TYPE_LABELS: Record<string, string> = {
  "Product:CREATE": "เพิ่มสินค้า",
  "Product:UPDATE": "แก้ไขสินค้า",
  "Product:DELETE": "ลบสินค้า",
  "Stock:UPDATE": "ปรับสต็อก",
  "User:CREATE": "เพิ่มผู้ใช้งาน",
  "User:UPDATE": "แก้ไข/เข้าสู่ระบบ",
  "User:DELETE": "ลบผู้ใช้งาน",
};
