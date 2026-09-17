import { NextResponse } from "next/server";

import { requireUser } from "@/lib/auth";
import { errorResponse } from "@/lib/errors";
import { LOW_STOCK_DEFAULT_THRESHOLD } from "@/lib/constants";
import * as ProductModel from "@/models/Product";
import { addLog } from "@/models/Activity";

export async function GET(request: Request) {
  try {
    await requireUser();
    const { searchParams } = new URL(request.url);
    const search = searchParams.get("search") ?? undefined;
    const products = await ProductModel.getAllProducts(search);
    return NextResponse.json({ products });
  } catch (err) {
    return errorResponse(err);
  }
}

export async function POST(request: Request) {
  try {
    const user = await requireUser();
    const data = await request.json();
    ProductModel.validateProductInput(data);

    const id = await ProductModel.createProduct(
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
        quantity: Number(data.quantity ?? 0),
      },
      user.id
    );

    await addLog({
      userId: user.id,
      userRole: user.role,
      action: "CREATE",
      entityType: "Product",
      entityId: id,
      description: `${user.name} เพิ่มสินค้าใหม่ "${data.name}" (รหัส ${data.sku})`,
    });

    return NextResponse.json({ id }, { status: 201 });
  } catch (err) {
    return errorResponse(err);
  }
}
