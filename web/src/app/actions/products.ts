"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { prisma } from "@/lib/prisma";
import { requireUser } from "@/lib/auth";
import { addActivityLog } from "@/lib/activity-log";

export type ProductFormState = { error?: string } | null;

async function resolveCategoryId(categoryName: string): Promise<string> {
  const name = categoryName.trim();
  const existing = await prisma.category.findUnique({ where: { name } });
  if (existing) return existing.id;

  const maxSort = await prisma.category.aggregate({ _max: { sortOrder: true } });
  const created = await prisma.category.create({
    data: {
      id: crypto.randomUUID(),
      name,
      sortOrder: (maxSort._max.sortOrder ?? 0) + 1,
      updatedAt: new Date(),
    },
  });
  return created.id;
}

function readProductForm(formData: FormData) {
  return {
    name: String(formData.get("name") ?? "").trim(),
    commonName: String(formData.get("commonName") ?? "").trim() || null,
    sku: String(formData.get("sku") ?? "").trim() || null,
    barcode: String(formData.get("barcode") ?? "").trim() || null,
    categoryName: String(formData.get("categoryName") ?? "").trim(),
    baseUnit: String(formData.get("baseUnit") ?? "").trim() || "ขวด",
    packUnit: String(formData.get("packUnit") ?? "").trim() || null,
    unitsPerPack: Number(formData.get("unitsPerPack") ?? 1),
    minStockAlert: Number(formData.get("minStockAlert") ?? 10),
    currentStock: Number(formData.get("currentStock") ?? 0),
    imageUrl: String(formData.get("imageUrl") ?? "").trim() || null,
    description: String(formData.get("description") ?? "").trim() || null,
    price: formData.get("price") ? Number(formData.get("price")) : null,
  };
}

function validateProductForm(data: ReturnType<typeof readProductForm>, isEdit: boolean): string | null {
  if (!data.name) return "กรุณากรอกชื่อสินค้า";
  if (!data.categoryName) return "กรุณาเลือกหรือพิมพ์หมวดหมู่สินค้า";
  if (!data.baseUnit) return "กรุณากรอกหน่วยนับ";
  if (!Number.isFinite(data.unitsPerPack) || data.unitsPerPack <= 0) {
    return "จำนวนต่อแพ็คต้องเป็นตัวเลขมากกว่า 0";
  }
  if (!Number.isFinite(data.minStockAlert) || data.minStockAlert < 0) {
    return "ค่าสต็อกขั้นต่ำต้องเป็นตัวเลขไม่ติดลบ";
  }
  if (!isEdit && (!Number.isFinite(data.currentStock) || data.currentStock < 0)) {
    return "จำนวนสต็อกเริ่มต้นต้องเป็นตัวเลขไม่ติดลบ";
  }
  if (data.price !== null && (!Number.isFinite(data.price) || data.price < 0)) {
    return "ราคาต้องเป็นตัวเลขไม่ติดลบ";
  }
  return null;
}

export async function createProduct(_prev: ProductFormState, formData: FormData): Promise<ProductFormState> {
  const user = await requireUser();
  const data = readProductForm(formData);

  const error = validateProductForm(data, false);
  if (error) return { error };

  const categoryId = await resolveCategoryId(data.categoryName);
  const now = new Date();

  const product = await prisma.product.create({
    data: {
      id: crypto.randomUUID(),
      name: data.name,
      commonName: data.commonName,
      sku: data.sku,
      barcode: data.barcode,
      categoryId,
      baseUnit: data.baseUnit,
      packUnit: data.packUnit,
      unitsPerPack: data.unitsPerPack,
      currentStock: data.currentStock,
      minStockAlert: data.minStockAlert,
      imageUrl: data.imageUrl,
      description: data.description,
      createdById: user.id,
      updatedById: user.id,
      updatedAt: now,
      ...(data.price !== null
        ? {
            prices: {
              create: {
                id: crypto.randomUUID(),
                channel: "STORE",
                price: data.price,
                updatedAt: now,
              },
            },
          }
        : {}),
    },
  });

  await addActivityLog({
    userId: user.id,
    userRole: user.role,
    action: "CREATE",
    entityType: "Product",
    entityId: product.id,
    description: `${user.name} เพิ่มสินค้าใหม่ "${product.name}"`,
  });

  revalidatePath("/products");
  redirect(`/products/${product.id}`);
}

export async function updateProduct(
  productId: string,
  _prev: ProductFormState,
  formData: FormData,
): Promise<ProductFormState> {
  const user = await requireUser();
  const data = readProductForm(formData);

  const error = validateProductForm(data, true);
  if (error) return { error };

  const existing = await prisma.product.findUnique({ where: { id: productId }, include: { prices: true } });
  if (!existing) return { error: "ไม่พบสินค้านี้ในระบบ" };

  const categoryId = await resolveCategoryId(data.categoryName);
  const now = new Date();

  await prisma.product.update({
    where: { id: productId },
    data: {
      name: data.name,
      commonName: data.commonName,
      sku: data.sku,
      barcode: data.barcode,
      categoryId,
      baseUnit: data.baseUnit,
      packUnit: data.packUnit,
      unitsPerPack: data.unitsPerPack,
      minStockAlert: data.minStockAlert,
      imageUrl: data.imageUrl,
      description: data.description,
      updatedById: user.id,
      updatedAt: now,
    },
  });

  if (data.price !== null) {
    const storePrice = existing.prices.find((p) => p.channel === "STORE");
    if (storePrice) {
      await prisma.productPrice.update({
        where: { id: storePrice.id },
        data: { price: data.price, updatedAt: now },
      });
    } else {
      await prisma.productPrice.create({
        data: { id: crypto.randomUUID(), productId, channel: "STORE", price: data.price, updatedAt: now },
      });
    }
  }

  await addActivityLog({
    userId: user.id,
    userRole: user.role,
    action: "UPDATE",
    entityType: "Product",
    entityId: productId,
    description: `${user.name} แก้ไขข้อมูลสินค้า "${data.name}"`,
  });

  revalidatePath("/products");
  revalidatePath(`/products/${productId}`);
  redirect(`/products/${productId}`);
}

export async function deactivateProduct(productId: string) {
  const user = await requireUser();

  const product = await prisma.product.findUnique({ where: { id: productId } });
  if (!product) throw new Error("ไม่พบสินค้านี้ในระบบ");

  await prisma.product.update({ where: { id: productId }, data: { isActive: false, updatedById: user.id } });

  await addActivityLog({
    userId: user.id,
    userRole: user.role,
    action: "DELETE",
    entityType: "Product",
    entityId: productId,
    description: `${user.name} ลบสินค้า "${product.name}"`,
  });

  revalidatePath("/products");
}
