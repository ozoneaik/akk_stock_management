import { prisma } from "@/lib/prisma";
import { BulkStockAdjust } from "./BulkStockAdjust";

export default async function StockAdjustPage() {
  const products = await prisma.product.findMany({
    where: { isActive: true },
    select: {
      id: true,
      name: true,
      sku: true,
      currentStock: true,
      baseUnit: true,
      packUnit: true,
      unitsPerPack: true,
    },
    orderBy: { name: "asc" },
  });

  return (
    <div className="px-4 py-5">
      <h1 className="text-xl font-bold mb-1">เพิ่ม/ลดสต็อกสินค้า</h1>
      <p className="text-sm text-muted mb-4">เลือกสินค้าได้ทีละหลายรายการ แล้วบันทึกพร้อมกันในครั้งเดียว</p>
      <BulkStockAdjust products={products} />
    </div>
  );
}
