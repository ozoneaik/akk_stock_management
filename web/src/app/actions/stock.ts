"use server";

import { revalidatePath } from "next/cache";

import { prisma } from "@/lib/prisma";
import { requireUser } from "@/lib/auth";
import { addActivityLog } from "@/lib/activity-log";
import type { User } from "@/generated/prisma/client";

export type StockDirection = "IN" | "OUT";
export type StockUnitMode = "BASE" | "PACK";

export type StockAdjustInput = {
  productId: string;
  direction: StockDirection;
  unitMode: StockUnitMode;
  quantity: number;
  note: string;
};

export type StockAdjustResult = { productId: string; ok: boolean; error?: string; newStock?: number };

async function performStockAdjustment(input: StockAdjustInput, user: User): Promise<StockAdjustResult> {
  if (!Number.isFinite(input.quantity) || input.quantity <= 0) {
    return { productId: input.productId, ok: false, error: "กรุณาระบุจำนวนเป็นตัวเลขมากกว่า 0" };
  }

  const product = await prisma.product.findUnique({ where: { id: input.productId } });
  if (!product) {
    return { productId: input.productId, ok: false, error: "ไม่พบสินค้านี้ในระบบ" };
  }

  const baseQuantity =
    input.unitMode === "PACK" ? Math.round(input.quantity * product.unitsPerPack) : Math.round(input.quantity);
  const signedChange = input.direction === "IN" ? baseQuantity : -baseQuantity;
  const newStock = product.currentStock + signedChange;

  if (newStock < 0) {
    return {
      productId: input.productId,
      ok: false,
      error: `จำนวนสต็อกคงเหลือจะติดลบ (ปัจจุบัน ${product.currentStock} ${product.baseUnit})`,
    };
  }

  const inputUnitLabel = input.unitMode === "PACK" ? product.packUnit ?? product.baseUnit : product.baseUnit;

  await prisma.$transaction([
    prisma.product.update({
      where: { id: input.productId },
      data: { currentStock: newStock, updatedById: user.id },
    }),
    prisma.stockMovement.create({
      data: {
        id: crypto.randomUUID(),
        productId: input.productId,
        type: input.direction,
        quantity: baseQuantity,
        inputUnit: inputUnitLabel,
        inputQuantity: input.quantity,
        balanceBefore: product.currentStock,
        balanceAfter: newStock,
        note: input.note || null,
        createdById: user.id,
      },
    }),
  ]);

  const directionText = input.direction === "IN" ? "เพิ่ม" : "ลด";
  await addActivityLog({
    userId: user.id,
    userRole: user.role,
    action: "UPDATE",
    entityType: "Stock",
    entityId: input.productId,
    description: `${user.name} ${directionText}สต็อกสินค้า "${product.name}" จำนวน ${input.quantity} ${inputUnitLabel} (คงเหลือใหม่: ${newStock} ${product.baseUnit})${
      input.note ? ` เหตุผล: ${input.note}` : ""
    }`,
  });

  return { productId: input.productId, ok: true, newStock };
}

export async function adjustStock(input: StockAdjustInput): Promise<StockAdjustResult> {
  const user = await requireUser();
  const result = await performStockAdjustment(input, user);
  if (result.ok) {
    revalidatePath("/");
    revalidatePath("/products");
    revalidatePath(`/products/${input.productId}`);
    revalidatePath("/stock");
  }
  return result;
}

export async function bulkAdjustStock(items: StockAdjustInput[]): Promise<StockAdjustResult[]> {
  const user = await requireUser();
  const results: StockAdjustResult[] = [];

  // ทำทีละรายการต่อเนื่องกัน (ไม่รวมเป็น transaction เดียวทั้งหมด) เพื่อให้รายการที่ผ่านสำเร็จแล้ว
  // ไม่ถูกยกเลิกตามรายการอื่นที่ error ทีหลัง (เช่น ทำให้สต็อกติดลบ)
  for (const item of items) {
    results.push(await performStockAdjustment(item, user));
  }

  revalidatePath("/");
  revalidatePath("/products");
  revalidatePath("/stock");
  return results;
}
