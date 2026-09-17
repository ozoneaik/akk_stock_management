import { Prisma } from "@prisma/client";

import { prisma } from "@/lib/prisma";
import { newId } from "@/lib/id";
import { AppError } from "@/lib/errors";
import { LOW_STOCK_DEFAULT_THRESHOLD } from "@/lib/constants";

const productInclude = { prices: true, category: true } satisfies Prisma.ProductInclude;
type ProductWithRelations = Prisma.ProductGetPayload<{ include: typeof productInclude }>;

export type ProductPriceInput = { price: number; discount?: number };

export type ProductInput = {
  sku: string;
  name: string;
  commonName?: string;
  categoryId: string;
  baseUnit: string;
  packUnit?: string;
  unitsPerPack: number;
  minStockAlert: number;
  imageUrl?: string;
  description?: string;
  prices: Record<string, ProductPriceInput>;
};

/** คืน error ถ้าข้อมูลไม่ถูกต้อง หรือคืน void ถ้าผ่าน (โยน AppError เหมือน validate_product_data ฝั่ง desktop) */
export function validateProductInput(data: Partial<ProductInput> & { quantity?: number }) {
  if (!data.sku?.toString().trim()) throw new AppError("กรุณากรอกรหัสสินค้า");
  if (!data.name?.toString().trim()) throw new AppError("กรุณากรอกชื่อสินค้า");
  if (!data.baseUnit?.toString().trim()) throw new AppError("กรุณากรอกหน่วยนับย่อย (เช่น ขวด, ซอง, ชิ้น)");

  const unitsPerPack = Number(data.unitsPerPack ?? 1);
  if (!Number.isFinite(unitsPerPack) || unitsPerPack <= 0) {
    throw new AppError("จำนวนหน่วยย่อยต่อแพ็คต้องมากกว่า 0");
  }

  if (data.quantity !== undefined) {
    const quantity = Number(data.quantity);
    if (!Number.isFinite(quantity) || quantity < 0) throw new AppError("จำนวนสินค้าต้องไม่ติดลบ");
  }

  const minStockAlert = Number(data.minStockAlert ?? LOW_STOCK_DEFAULT_THRESHOLD);
  if (!Number.isFinite(minStockAlert) || minStockAlert < 0) {
    throw new AppError("ค่าสต็อกขั้นต่ำต้องไม่ติดลบ");
  }
}

function toProductDTO(product: ProductWithRelations) {
  const { prices, category, ...rest } = product;
  return {
    ...rest,
    categoryName: category?.name ?? "ไม่ระบุหมวดหมู่",
    prices: Object.fromEntries(
      prices.map((p) => [p.channel, { price: p.price, discount: p.discountType !== "NONE" ? p.discountValue : 0 }])
    ),
  };
}

export async function getAllProducts(search?: string) {
  const keyword = search?.trim();
  const products = await prisma.product.findMany({
    where: {
      isActive: true,
      ...(keyword ? { OR: [{ sku: { contains: keyword } }, { name: { contains: keyword } }] } : {}),
    },
    include: productInclude,
    orderBy: { name: "asc" },
  });
  return products.map(toProductDTO);
}

export async function getProductById(id: string) {
  const product = await prisma.product.findUnique({
    where: { id },
    include: productInclude,
  });
  return product ? toProductDTO(product) : null;
}

/** สินค้าที่จำนวนคงเหลือน้อยกว่า min_stock_alert ของตัวเอง (เปรียบเทียบ 2 คอลัมน์ ต้องใช้ raw query) */
export async function getLowStockProducts() {
  const rows = await prisma.$queryRaw<{ id: string }[]>`
    SELECT id FROM product WHERE is_active = 1 AND current_stock < min_stock_alert ORDER BY current_stock ASC
  `;
  if (rows.length === 0) return [];

  const products = await prisma.product.findMany({
    where: { id: { in: rows.map((r) => r.id) } },
    include: productInclude,
  });
  const byId = new Map(products.map((p) => [p.id, p]));
  return rows.map((r) => toProductDTO(byId.get(r.id)!));
}

export async function getTotalStockSummary() {
  const result = await prisma.product.aggregate({
    where: { isActive: true },
    _count: { _all: true },
    _sum: { currentStock: true },
  });
  return { totalProducts: result._count._all, totalQuantity: result._sum.currentStock ?? 0 };
}

function priceCreateData(now: Date, channel: string, info: ProductPriceInput) {
  const discountValue = info.discount ?? 0;
  return {
    id: newId(),
    channel,
    price: info.price,
    discountType: discountValue ? "FIXED" : "NONE",
    discountValue,
    updatedAt: now,
  };
}

export async function createProduct(data: ProductInput & { quantity: number }, userId: string) {
  const now = new Date();
  const product = await prisma.product.create({
    data: {
      id: newId(),
      sku: data.sku.trim() || null,
      name: data.name.trim(),
      commonName: data.commonName?.trim() || null,
      categoryId: data.categoryId,
      baseUnit: data.baseUnit.trim(),
      packUnit: data.packUnit?.trim() || null,
      unitsPerPack: Math.trunc(data.unitsPerPack),
      currentStock: Math.trunc(data.quantity),
      minStockAlert: Math.trunc(data.minStockAlert),
      imageUrl: data.imageUrl?.trim() || null,
      description: data.description?.trim() || null,
      isActive: true,
      createdById: userId,
      updatedById: userId,
      updatedAt: now,
      prices: {
        create: Object.entries(data.prices ?? {}).map(([channel, info]) => priceCreateData(now, channel, info)),
      },
    },
  });
  return product.id;
}

/** แก้ไขข้อมูลสินค้าที่มีอยู่ (ไม่รวมจำนวนสต็อก ต้องปรับผ่าน adjustStock เพื่อให้มี log ที่ถูกต้อง) */
export async function updateProduct(id: string, data: ProductInput, userId: string) {
  const now = new Date();
  await prisma.$transaction([
    prisma.product.update({
      where: { id },
      data: {
        sku: data.sku.trim() || null,
        name: data.name.trim(),
        commonName: data.commonName?.trim() || null,
        categoryId: data.categoryId,
        baseUnit: data.baseUnit.trim(),
        packUnit: data.packUnit?.trim() || null,
        unitsPerPack: Math.trunc(data.unitsPerPack),
        minStockAlert: Math.trunc(data.minStockAlert),
        imageUrl: data.imageUrl?.trim() || null,
        description: data.description?.trim() || null,
        updatedById: userId,
        updatedAt: now,
      },
    }),
    prisma.productPrice.deleteMany({ where: { productId: id } }),
    ...Object.entries(data.prices ?? {}).map(([channel, info]) =>
      prisma.productPrice.create({ data: { ...priceCreateData(now, channel, info), productId: id } })
    ),
  ]);
}

/** ลบสินค้าแบบ soft-delete (is_active = false) เก็บประวัติ stock_movement/activity_log ไว้ครบ */
export async function deactivateProduct(id: string) {
  await prisma.product.update({ where: { id }, data: { isActive: false } });
}
