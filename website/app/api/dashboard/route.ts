import { NextResponse } from "next/server";

import { requireUser } from "@/lib/auth";
import { errorResponse } from "@/lib/errors";
import { getTotalStockSummary, getLowStockProducts } from "@/models/Product";

export async function GET() {
  try {
    await requireUser();
    const [summary, lowStock] = await Promise.all([getTotalStockSummary(), getLowStockProducts()]);
    return NextResponse.json({
      totalProducts: summary.totalProducts,
      totalQuantity: summary.totalQuantity,
      lowStockItems: lowStock,
      lowStockCount: lowStock.length,
    });
  } catch (err) {
    return errorResponse(err);
  }
}
