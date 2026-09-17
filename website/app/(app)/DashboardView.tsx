"use client";

import { useEffect, useState } from "react";

import { apiFetch, ApiClientError } from "@/lib/api-client";
import type { ProductDTO } from "@/lib/types";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorBanner } from "@/components/ui/Field";
import { ProductDetailModal } from "@/components/ProductDetailModal";

type DashboardData = {
  totalProducts: number;
  totalQuantity: number;
  lowStockItems: ProductDTO[];
  lowStockCount: number;
};

export function DashboardView() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<ProductDTO | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let ignore = false;
    apiFetch<DashboardData>("/api/dashboard")
      .then((result) => {
        if (ignore) return;
        setData(result);
        setError(null);
      })
      .catch((err) => {
        if (ignore) return;
        setError(err instanceof ApiClientError ? err.message : "โหลดข้อมูลไม่สำเร็จ");
      });
    return () => {
      ignore = true;
    };
  }, [reloadKey]);

  if (error) return <ErrorBanner message={error} />;
  if (!data) return <Spinner />;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <SummaryCard label="จำนวนสินค้าทั้งหมด" value={data.totalProducts.toLocaleString()} />
        <SummaryCard label="จำนวนสต็อกรวม" value={data.totalQuantity.toLocaleString()} />
        <SummaryCard label="สินค้าใกล้หมด" value={data.lowStockCount.toLocaleString()} highlight={data.lowStockCount > 0} />
      </div>

      <div className="rounded-lg bg-white shadow-sm">
        <h2 className="border-b border-slate-200 px-4 py-3 font-semibold text-slate-800">สินค้าที่เหลือน้อย</h2>
        {data.lowStockItems.length === 0 ? (
          <p className="px-4 py-6 text-center text-sm text-slate-500">ไม่มีสินค้าที่เหลือน้อย</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-slate-500">
                <tr>
                  <th className="px-4 py-2">รหัส</th>
                  <th className="px-4 py-2">ชื่อสินค้า</th>
                  <th className="px-4 py-2 text-right">คงเหลือ</th>
                  <th className="px-4 py-2 text-right">ขั้นต่ำ</th>
                </tr>
              </thead>
              <tbody>
                {data.lowStockItems.map((item) => (
                  <tr
                    key={item.id}
                    className="cursor-pointer border-t border-slate-100 hover:bg-slate-50"
                    onClick={() => setSelected(item)}
                  >
                    <td className="px-4 py-2">{item.sku ?? "-"}</td>
                    <td className="px-4 py-2">{item.name}</td>
                    <td className="px-4 py-2 text-right font-medium text-amber-700">
                      {item.currentStock} {item.baseUnit}
                    </td>
                    <td className="px-4 py-2 text-right text-slate-500">{item.minStockAlert}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selected && (
        <ProductDetailModal
          product={selected}
          onClose={() => setSelected(null)}
          onChanged={() => setReloadKey((k) => k + 1)}
        />
      )}
    </div>
  );
}

function SummaryCard({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="rounded-lg bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${highlight ? "text-amber-700" : "text-slate-800"}`}>{value}</p>
    </div>
  );
}
