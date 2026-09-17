"use client";

import { useEffect, useState } from "react";

import { apiFetch, ApiClientError } from "@/lib/api-client";
import type { ProductDTO } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Input, Select, ErrorBanner } from "@/components/ui/Field";

type PendingItem = {
  productId: string;
  name: string;
  baseUnit: string;
  packUnit: string | null;
  unitsPerPack: number;
  mode: "IN" | "OUT";
  unit: string;
  quantity: string;
  reason: string;
  error?: string;
};

export function StockView() {
  const [search, setSearch] = useState("");
  const [results, setResults] = useState<ProductDTO[]>([]);
  const [items, setItems] = useState<PendingItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (!search.trim()) {
        setResults([]);
        return;
      }
      apiFetch<{ products: ProductDTO[] }>(`/api/product?search=${encodeURIComponent(search)}`)
        .then((res) => setResults(res.products))
        .catch(() => setResults([]));
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  function addItem(product: ProductDTO) {
    if (items.some((i) => i.productId === product.id)) return;
    setItems((prev) => [
      ...prev,
      {
        productId: product.id,
        name: product.name,
        baseUnit: product.baseUnit,
        packUnit: product.packUnit,
        unitsPerPack: product.unitsPerPack,
        mode: "IN",
        unit: product.baseUnit,
        quantity: "",
        reason: "",
      },
    ]);
  }

  function updateItem(productId: string, patch: Partial<PendingItem>) {
    setItems((prev) => prev.map((i) => (i.productId === productId ? { ...i, ...patch, error: undefined } : i)));
  }

  function removeItem(productId: string) {
    setItems((prev) => prev.filter((i) => i.productId !== productId));
  }

  async function handleSaveAll() {
    setError(null);
    setSavedMessage(null);

    const invalid = items.find((i) => !i.quantity || Number(i.quantity) <= 0);
    if (invalid) {
      setError(`กรุณากรอกจำนวนที่มากกว่า 0 สำหรับ "${invalid.name}"`);
      return;
    }

    setSaving(true);
    try {
      const adjustments = items.map((i) => {
        const factor = i.unit === i.packUnit ? i.unitsPerPack : 1;
        const qty = Number(i.quantity);
        return {
          productId: i.productId,
          changeAmount: (i.mode === "IN" ? 1 : -1) * qty * factor,
          reason: i.reason,
          unitLabel: i.unit,
          inputQuantity: qty,
        };
      });

      const res = await apiFetch<{ results: { ok: boolean; error?: string }[] }>("/api/stock", {
        method: "POST",
        body: JSON.stringify({ adjustments }),
      });

      let successCount = 0;
      setItems((prev) =>
        prev.reduce<PendingItem[]>((acc, item, idx) => {
          const result = res.results[idx];
          if (result.ok) {
            successCount += 1;
            return acc;
          }
          acc.push({ ...item, error: result.error });
          return acc;
        }, [])
      );

      if (successCount > 0) setSavedMessage(`บันทึกสำเร็จ ${successCount} รายการ`);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "บันทึกไม่สำเร็จ");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="ค้นหาสินค้าเพื่อเพิ่มเข้ารายการปรับสต็อก" />
        {results.length > 0 && (
          <div className="mt-2 max-h-64 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-sm">
            {results.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => addItem(p)}
                className="flex w-full items-center justify-between px-4 py-2 text-left text-sm hover:bg-slate-50"
              >
                <span>
                  {p.name} <span className="text-slate-400">({p.sku ?? "-"})</span>
                </span>
                <span className="text-slate-500">
                  {p.currentStock} {p.baseUnit}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {error && <ErrorBanner message={error} />}
      {savedMessage && <p className="rounded-md bg-green-50 px-3 py-2 text-sm text-green-700">{savedMessage}</p>}

      {items.length > 0 && (
        <div className="overflow-x-auto rounded-lg bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr>
                <th className="px-3 py-2">สินค้า</th>
                <th className="px-3 py-2">รูปแบบ</th>
                <th className="px-3 py-2">หน่วย</th>
                <th className="px-3 py-2">จำนวน</th>
                <th className="px-3 py-2">เหตุผล</th>
                <th className="px-3 py-2" />
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const unitOptions = item.packUnit ? [item.baseUnit, item.packUnit] : [item.baseUnit];
                return (
                  <tr key={item.productId} className="border-t border-slate-100 align-top">
                    <td className="px-3 py-2">
                      <p className="font-medium">{item.name}</p>
                      {item.error && <p className="text-xs text-red-600">{item.error}</p>}
                    </td>
                    <td className="px-3 py-2">
                      <Select
                        value={item.mode}
                        onChange={(e) => updateItem(item.productId, { mode: e.target.value as "IN" | "OUT" })}
                      >
                        <option value="IN">เพิ่ม</option>
                        <option value="OUT">ลด</option>
                      </Select>
                    </td>
                    <td className="px-3 py-2">
                      <Select value={item.unit} onChange={(e) => updateItem(item.productId, { unit: e.target.value })}>
                        {unitOptions.map((u) => (
                          <option key={u} value={u}>
                            {u}
                          </option>
                        ))}
                      </Select>
                    </td>
                    <td className="px-3 py-2">
                      <Input
                        type="number"
                        min={0}
                        value={item.quantity}
                        onChange={(e) => updateItem(item.productId, { quantity: e.target.value })}
                        className="w-24"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <Input value={item.reason} onChange={(e) => updateItem(item.productId, { reason: e.target.value })} />
                    </td>
                    <td className="px-3 py-2">
                      <Button variant="ghost" onClick={() => removeItem(item.productId)}>
                        ลบ
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <div className="flex justify-end border-t border-slate-200 px-3 py-3">
            <Button onClick={handleSaveAll} disabled={saving}>
              {saving ? "กำลังบันทึก..." : "บันทึกทั้งหมด"}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
