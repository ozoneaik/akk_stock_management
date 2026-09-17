import { prisma } from "@/lib/prisma";
import { newId } from "@/lib/id";

export async function getAllCategories() {
  return prisma.category.findMany({
    orderBy: [{ sortOrder: "asc" }, { name: "asc" }],
  });
}

/**
 * ถ้ามีหมวดหมู่นี้อยู่แล้วคืน id เดิม ถ้ายังไม่มีให้สร้างใหม่แล้วคืน id ที่สร้าง
 * ใช้ตอนเพิ่ม/แก้ไขสินค้าเพื่อให้ผู้ใช้พิมพ์ชื่อหมวดหมู่ใหม่ได้เลยโดยไม่ต้องมีหน้าจัดการหมวดหมู่แยก
 */
export async function getOrCreateCategory(name: string) {
  const trimmed = name.trim();

  const existing = await prisma.category.findUnique({ where: { name: trimmed } });
  if (existing) return existing.id;

  const maxSort = await prisma.category.aggregate({ _max: { sortOrder: true } });
  const category = await prisma.category.create({
    data: {
      id: newId(),
      name: trimmed,
      sortOrder: (maxSort._max.sortOrder ?? 0) + 1,
      updatedAt: new Date(),
    },
  });
  return category.id;
}

export async function getCategoryById(id: string) {
  return prisma.category.findUnique({ where: { id } });
}
