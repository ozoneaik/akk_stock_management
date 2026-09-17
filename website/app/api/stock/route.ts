import { NextResponse } from "next/server";

import { requireUser } from "@/lib/auth";
import { AppError, errorResponse } from "@/lib/errors";
import { adjustStock } from "@/models/Stock";
import { addLog } from "@/models/Activity";

type AdjustmentInput = {
  productId: string;
  changeAmount: number;
  reason?: string;
  unitLabel?: string;
  inputQuantity?: number;
};

type AdjustmentResult =
  | { productId: string; ok: true; newQuantity: number }
  | { productId: string; ok: false; error: string };

// รับปรับสต็อกได้หลายรายการพร้อมกัน (เหมือนหน้า "เพิ่ม/ลดสต็อกสินค้า" ฝั่ง desktop)
// รายการที่ล้มเหลว (เช่น ทำให้สต็อกติดลบ) จะไม่กระทบรายการอื่นที่สำเร็จแล้ว
export async function POST(request: Request) {
  try {
    const user = await requireUser();
    const body = await request.json();
    const adjustments: AdjustmentInput[] = Array.isArray(body?.adjustments) ? body.adjustments : [body];

    const results: AdjustmentResult[] = [];

    for (const item of adjustments) {
      try {
        if (!item.productId) throw new AppError("ไม่พบสินค้านี้ในระบบ");
        const changeAmount = Number(item.changeAmount);
        if (!Number.isFinite(changeAmount)) {
          throw new AppError("กรุณาระบุจำนวนที่ต้องการเพิ่มหรือลด (ต้องไม่เป็น 0)");
        }
        const unitLabel = item.unitLabel?.trim() || "หน่วย";
        const inputQuantity = Number.isFinite(Number(item.inputQuantity))
          ? Number(item.inputQuantity)
          : Math.abs(changeAmount);

        const { newQuantity, productName, baseUnit } = await adjustStock(
          item.productId,
          changeAmount,
          item.reason?.trim() || null,
          unitLabel,
          inputQuantity,
          user.id
        );

        const direction = changeAmount > 0 ? "เพิ่ม" : "ลด";
        await addLog({
          userId: user.id,
          userRole: user.role,
          action: "UPDATE",
          entityType: "Stock",
          entityId: item.productId,
          description:
            `${user.name} ${direction}สต็อกสินค้า "${productName}" จำนวน ${inputQuantity} ${unitLabel} ` +
            `(คงเหลือใหม่: ${newQuantity} ${baseUnit}) เหตุผล: ${item.reason?.trim() || "-"}`,
        });

        results.push({ productId: item.productId, ok: true, newQuantity });
      } catch (err) {
        const message = err instanceof AppError ? err.message : "เกิดข้อผิดพลาดที่ไม่คาดคิดในระบบ";
        results.push({ productId: item.productId, ok: false, error: message });
      }
    }

    return NextResponse.json({ results });
  } catch (err) {
    return errorResponse(err);
  }
}
