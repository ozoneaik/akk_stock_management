import { PrismaClient } from "@prisma/client";

// เก็บ instance เดียวไว้ใน global ตอน dev เพื่อกัน hot-reload สร้าง connection ใหม่ซ้ำๆ จนฐานข้อมูลโดนถล่ม
const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
