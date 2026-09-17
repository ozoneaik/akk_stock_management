import { prisma } from "@/lib/prisma";
import { newId } from "@/lib/id";
import { AppError } from "@/lib/errors";

/**
 * เพิ่ม/ลดจำนวนสต็อกสินค้า 1 รายการ (changeAmount เป็นบวก = เพิ่ม (IN), ลบ = ลด (OUT), หน่วยเป็นหน่วยย่อยเสมอ)
 * unitLabel/inputQuantity: หน่วยและจำนวนตามที่ผู้ใช้กรอกจริง (ก่อนแปลงเป็นหน่วยย่อย) เก็บไว้เป็นประวัติ
 * บันทึกลง stock_movement ด้วยทุกครั้งเพื่อดูประวัติย้อนหลังได้ ทำใน transaction เดียวกับการอัปเดตสต็อก
 */
export async function adjustStock(
  productId: string,
  changeAmount: number,
  reason: string | null,
  unitLabel: string,
  inputQuantity: number,
  userId: string
) {
  if (changeAmount === 0) {
    throw new AppError("กรุณาระบุจำนวนที่ต้องการเพิ่มหรือลด (ต้องไม่เป็น 0)");
  }

  return prisma.$transaction(async (tx) => {
    const product = await tx.product.findUnique({ where: { id: productId } });
    if (!product) throw new AppError("ไม่พบสินค้านี้ในระบบ", 404);

    const newQuantity = product.currentStock + changeAmount;
    if (newQuantity < 0) {
      throw new AppError("จำนวนสต็อกคงเหลือจะติดลบ กรุณาตรวจสอบจำนวนที่ต้องการลด");
    }

    await tx.product.update({
      where: { id: productId },
      data: { currentStock: newQuantity, updatedById: userId },
    });

    await tx.stockMovement.create({
      data: {
        id: newId(),
        productId,
        type: changeAmount > 0 ? "IN" : "OUT",
        quantity: Math.abs(changeAmount),
        inputUnit: unitLabel,
        inputQuantity,
        balanceBefore: product.currentStock,
        balanceAfter: newQuantity,
        note: reason || null,
        createdById: userId,
      },
    });

    return { newQuantity, productName: product.name, baseUnit: product.baseUnit };
  });
}
