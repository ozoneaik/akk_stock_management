import { NextResponse } from "next/server";

import { requireUser } from "@/lib/auth";
import { errorResponse, AppError } from "@/lib/errors";
import { LOW_STOCK_DEFAULT_THRESHOLD } from "@/lib/constants";
import * as ProductModel from "@/models/Product";
import { addLog } from "@/models/Activity";

type Params = { params: Promise<{ id: string }> };

export async function GET(_request: Request, { params }: Params) {
  try {
    await requireUser();
    const { id } = await params;
    const product = await ProductModel.getProductById(id);
    if (!product) throw new AppError("ไม่พบสินค้านี้ในระบบ", 404);
    return NextResponse.json({ product });
  } catch (err) {
    return errorResponse(err);
  }
}

export async function PATCH(request: Request, { params }: Params) {
  try {
    const user = await requireUser();
    const { id } = await params;
    const data = await request.json();
    ProductModel.validateProductInput(data);

    await ProductModel.updateProduct(
      id,
      {
        sku: data.sku,
        name: data.name,
        commonName: data.commonName,
        categoryId: data.categoryId,
        baseUnit: data.baseUnit,
        packUnit: data.packUnit,
        unitsPerPack: Number(data.unitsPerPack ?? 1),
        minStockAlert: Number(data.minStockAlert ?? LOW_STOCK_DEFAULT_THRESHOLD),
        imageUrl: data.imageUrl,
        description: data.description,
        prices: data.prices ?? {},
      },
      user.id
    );

    await addLog({
      userId: user.id,
      userRole: user.role,
      action: "UPDATE",
      entityType: "Product",
      entityId: id,
      description: `${user.name} แก้ไขข้อมูลสินค้า "${data.name}" (รหัส ${data.sku})`,
    });

    return NextResponse.json({ ok: true });
  } catch (err) {
    return errorResponse(err);
  }
}

export async function DELETE(_request: Request, { params }: Params) {
  try {
    const user = await requireUser();
    const { id } = await params;
    const product = await ProductModel.getProductById(id);
    if (!product) throw new AppError("ไม่พบสินค้านี้ในระบบ", 404);

    await ProductModel.deactivateProduct(id);

    await addLog({
      userId: user.id,
      userRole: user.role,
      action: "DELETE",
      entityType: "Product",
      entityId: id,
      description: `${user.name} ลบสินค้า "${product.name}" (รหัส ${product.sku ?? "-"})`,
    });

    return NextResponse.json({ ok: true });
  } catch (err) {
    return errorResponse(err);
  }
}
