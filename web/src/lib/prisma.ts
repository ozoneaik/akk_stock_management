import { PrismaMariaDb } from "@prisma/adapter-mariadb";

import { PrismaClient } from "@/generated/prisma/client";

// Prisma 7 ต้องต่อฐานข้อมูลผ่าน driver adapter เอง ไม่อ่าน connection string อัตโนมัติเหมือนเวอร์ชันก่อนหน้า
// แยก parse ค่าจาก DATABASE_URL เองแทนการส่ง connection string ตรงๆ เพราะ query param
// "sslaccept=strict" เป็นรูปแบบเฉพาะของ Prisma engine เดิม ไม่ใช่รูปแบบที่ driver "mariadb" เข้าใจ
function buildAdapter() {
  const url = new URL(process.env.DATABASE_URL ?? "");
  return new PrismaMariaDb({
    host: url.hostname,
    port: Number(url.port) || 3306,
    user: decodeURIComponent(url.username),
    password: decodeURIComponent(url.password),
    database: url.pathname.replace(/^\//, ""),
    ssl: {},
  });
}

// เก็บ instance เดียวไว้ใน global ตอน dev เพื่อกัน hot-reload สร้าง connection ใหม่ซ้ำๆ จนฐานข้อมูลโดนถล่ม
const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma = globalForPrisma.prisma ?? new PrismaClient({ adapter: buildAdapter() });

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
