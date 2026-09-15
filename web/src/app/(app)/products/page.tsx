import Link from "next/link";

import { prisma } from "@/lib/prisma";

export default async function ProductListPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  const keyword = (q ?? "").trim();

  const products = await prisma.product.findMany({
    where: {
      isActive: true,
      ...(keyword
        ? {
            OR: [
              { name: { contains: keyword } },
              { commonName: { contains: keyword } },
              { sku: { contains: keyword } },
              { barcode: { contains: keyword } },
            ],
          }
        : {}),
    },
    include: { category: true },
    orderBy: { name: "asc" },
  });

  return (
    <div className="px-4 py-5 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">รายการสินค้า</h1>
        <Link
          href="/products/new"
          className="bg-brand text-white text-sm font-semibold rounded-full px-4 py-2"
        >
          + เพิ่มสินค้า
        </Link>
      </div>

      <form className="flex gap-2">
        <input
          type="text"
          name="q"
          defaultValue={keyword}
          placeholder="ค้นหาชื่อ, รหัส, บาร์โค้ด..."
          className="flex-1 rounded-xl border border-border bg-card px-3 py-2 text-sm"
        />
        <button className="rounded-xl bg-brand text-white px-4 py-2 text-sm font-semibold">ค้นหา</button>
      </form>

      <div className="space-y-2">
        {products.map((product) => {
          const low = product.currentStock < product.minStockAlert;
          return (
            <Link
              key={product.id}
              href={`/products/${product.id}`}
              className={`flex items-center justify-between gap-3 rounded-xl border p-3 ${
                low ? "bg-amber-50 border-amber-200" : "bg-card border-border"
              }`}
            >
              <div className="min-w-0">
                <p className="font-medium truncate">{product.name}</p>
                <p className="text-xs text-muted truncate">
                  {product.category.name}
                  {product.sku ? ` · ${product.sku}` : ""}
                </p>
              </div>
              <div className="text-right shrink-0">
                <p className={`font-bold ${low ? "text-amber-700" : "text-foreground"}`}>
                  {product.currentStock}
                </p>
                <p className="text-xs text-muted">{product.baseUnit}</p>
              </div>
            </Link>
          );
        })}
        {products.length === 0 && (
          <p className="text-center text-muted text-sm py-8">
            {keyword ? "ไม่พบสินค้าที่ค้นหา" : "ยังไม่มีสินค้าในระบบ"}
          </p>
        )}
      </div>
    </div>
  );
}
