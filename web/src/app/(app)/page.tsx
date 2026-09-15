import Link from "next/link";

import { prisma } from "@/lib/prisma";
import { getCurrentUser } from "@/lib/auth";

export default async function DashboardPage() {
  const user = await getCurrentUser();

  const [totalProducts, totalStockAgg, activeProducts] = await Promise.all([
    prisma.product.count({ where: { isActive: true } }),
    prisma.product.aggregate({ where: { isActive: true }, _sum: { currentStock: true } }),
    prisma.product.findMany({
      where: { isActive: true },
      include: { category: true },
    }),
  ]);

  const totalStock = totalStockAgg._sum.currentStock ?? 0;
  // เทียบ currentStock < minStockAlert (คอลัมน์กับคอลัมน์) ทำใน query ตรงๆ ไม่ได้ผ่าน Prisma Client
  // จำนวนสินค้าต่อร้านมีไม่มาก จึงกรอง/เรียงฝั่ง JS แทนแทนที่จะใช้ raw SQL
  const lowStockProducts = activeProducts
    .filter((p) => p.currentStock < p.minStockAlert)
    .sort((a, b) => a.currentStock - b.currentStock);

  return (
    <div className="px-4 py-5 space-y-5">
      <div>
        <p className="text-muted text-sm">สวัสดี</p>
        <h1 className="text-xl font-bold">{user?.name}</h1>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <StatCard label="สินค้าทั้งหมด" value={`${totalProducts.toLocaleString()} รายการ`} />
        <StatCard label="สต็อกรวม" value={`${totalStock.toLocaleString()} ชิ้น`} />
        <StatCard
          label="สต็อกใกล้หมด"
          value={`${lowStockProducts.length.toLocaleString()} รายการ`}
          highlight={lowStockProducts.length > 0}
          className="col-span-2"
        />
      </div>

      <div>
        <h2 className="font-semibold mb-2">สินค้าที่สต็อกใกล้หมด</h2>
        {lowStockProducts.length === 0 ? (
          <p className="text-muted text-sm bg-card border border-border rounded-xl p-4 text-center">
            ยังไม่มีสินค้าที่สต็อกต่ำกว่าเกณฑ์
          </p>
        ) : (
          <div className="space-y-2">
            {lowStockProducts.map((product) => {
              const critical = product.currentStock <= product.minStockAlert / 2;
              return (
                <Link
                  key={product.id}
                  href={`/products/${product.id}`}
                  className={`block rounded-xl border p-3 ${
                    critical ? "bg-red-50 border-red-200" : "bg-card border-border"
                  }`}
                >
                  <div className="flex justify-between items-start gap-2">
                    <div>
                      <p className="font-medium">{product.name}</p>
                      <p className="text-xs text-muted">{product.category.name}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <p className={`font-bold ${critical ? "text-danger" : "text-brand-dark"}`}>
                        {product.currentStock}
                      </p>
                      <p className="text-xs text-muted">ขั้นต่ำ {product.minStockAlert}</p>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  highlight,
  className,
}: {
  label: string;
  value: string;
  highlight?: boolean;
  className?: string;
}) {
  return (
    <div className={`rounded-xl border border-border bg-card p-4 ${className ?? ""}`}>
      <p className="text-xs text-muted mb-1">{label}</p>
      <p className={`text-2xl font-bold ${highlight ? "text-danger" : "text-foreground"}`}>{value}</p>
    </div>
  );
}
