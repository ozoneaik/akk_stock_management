"use client";

import { useCallback, useEffect, useState } from "react";

import { apiFetch, ApiClientError } from "@/lib/api-client";
import type { ProductDTO } from "@/lib/types";
import { Spinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";
import { Input, ErrorBanner } from "@/components/ui/Field";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { ProductDetailModal } from "@/components/ProductDetailModal";
import { ProductForm } from "./components/ProductForm";

export function ProductView() {
  const [products, setProducts] = useState<ProductDTO[] | null>(null);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<ProductDTO | null>(null);
  const [formProduct, setFormProduct] = useState<ProductDTO | null | "create">(null);
  const [deleteTarget, setDeleteTarget] = useState<ProductDTO | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(async (keyword: string) => {
    try {
      const qs = keyword ? `?search=${encodeURIComponent(keyword)}` : "";
      const res = await apiFetch<{ products: ProductDTO[] }>(`/api/product${qs}`);
      setProducts(res.products);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "โหลดข้อมูลไม่สำเร็จ");
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => load(search), 300);
    return () => clearTimeout(timer);
  }, [search, load]);

  async function handleDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await apiFetch(`/api/product/${deleteTarget.id}`, { method: "DELETE" });
      setDeleteTarget(null);
      load(search);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "ลบสินค้าไม่สำเร็จ");
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="ค้นหาด้วยรหัสหรือชื่อสินค้า"
          className="sm:max-w-xs"
        />
        <Button onClick={() => setFormProduct("create")}>+ เพิ่มสินค้าใหม่</Button>
      </div>

      {error && <ErrorBanner message={error} />}

      {!products ? (
        <Spinner />
      ) : products.length === 0 ? (
        <p className="rounded-lg bg-white p-6 text-center text-sm text-slate-500 shadow-sm">ไม่พบสินค้า</p>
      ) : (
        <div className="overflow-x-auto rounded-lg bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr>
                <th className="px-4 py-2">รหัส</th>
                <th className="px-4 py-2">ชื่อสินค้า</th>
                <th className="px-4 py-2">หมวดหมู่</th>
                <th className="px-4 py-2 text-right">คงเหลือ</th>
                <th className="px-4 py-2 text-right">จัดการ</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id} className="border-t border-slate-100 hover:bg-slate-50">
                  <td className="cursor-pointer px-4 py-2" onClick={() => setDetail(p)}>
                    {p.sku ?? "-"}
                  </td>
                  <td className="cursor-pointer px-4 py-2" onClick={() => setDetail(p)}>
                    {p.name}
                  </td>
                  <td className="px-4 py-2 text-slate-500">{p.categoryName}</td>
                  <td
                    className={`px-4 py-2 text-right font-medium ${
                      p.currentStock < p.minStockAlert ? "text-amber-700" : ""
                    }`}
                  >
                    {p.currentStock} {p.baseUnit}
                  </td>
                  <td className="px-4 py-2 text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="ghost" onClick={() => setFormProduct(p)}>
                        แก้ไข
                      </Button>
                      <Button variant="ghost" onClick={() => setDeleteTarget(p)}>
                        ลบ
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {detail && (
        <ProductDetailModal product={detail} onClose={() => setDetail(null)} onChanged={() => load(search)} />
      )}

      {formProduct !== null && (
        <ProductForm
          product={formProduct === "create" ? null : formProduct}
          onClose={() => setFormProduct(null)}
          onSaved={() => load(search)}
        />
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="ลบสินค้า"
          message={`ยืนยันการลบสินค้า "${deleteTarget.name}" ใช่หรือไม่?`}
          confirmLabel={deleting ? "กำลังลบ..." : "ลบ"}
          danger
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
}
