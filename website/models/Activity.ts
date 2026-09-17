import { prisma } from "@/lib/prisma";
import { newId } from "@/lib/id";

export type LogInput = {
  userId: string;
  userRole: string;
  action: "CREATE" | "UPDATE" | "DELETE";
  entityType: "Product" | "User" | "Stock";
  entityId: string;
  description: string;
};

export async function addLog(input: LogInput) {
  await prisma.activityLog.create({
    data: { id: newId(), ...input },
  });
}

/** ดึงประวัติทั้งหมด เรียงจากล่าสุดไปเก่าสุด พร้อมชื่อผู้ใช้ที่กระทำ */
export async function getAllLogs(limit = 500) {
  return prisma.activityLog.findMany({
    take: limit,
    orderBy: { createdAt: "desc" },
    include: { user: { select: { name: true, username: true } } },
  });
}
