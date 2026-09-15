"use client";

import { useMemo, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { bulkAdjustStock, type StockDirection, type StockUnitMode } from "@/app/actions/stock";

type Product = {
  id: string;
  name: string;
  sku: string | null;
  currentStock: number;
  baseUnit: string;
  packUnit: string | null;
  unitsPerPack: number;
};

type CartItem = {
  product: Product;
  direction: StockDirection;
  unitMode: StockUnitMode;
  quantity: string;
  note: string;
  error?: string;
};

export function BulkStockAdjust({ products }: { products: Product[] }) {
  const [keyword, setKeyword] = useState("");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [summary, setSummary] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  const searchResults = useMemo(() => {
    const kw = keyword.trim().toLowerCase();
    if (!kw) return [];
    return products
      .filter(
        (p) =>
          !cart.some((c) => c.product.id === p.id) &&
          (p.name.toLowerCase().includes(kw) || (p.sku ?? "").toLowerCase().includes(kw)),
      )
      .slice(0, 8);
  }, [keyword, products, cart]);

  function addToCart(product: Product) {
    setCart((prev) => [
      ...prev,
      { product, direction: "IN", unitMode: "BASE", quantity: "", note: "" },
    ]);
    setKeyword("");
  }

  function updateItem(productId: string, patch: Partial<CartItem>) {
    setCart((prev) => prev.map((item) => (item.product.id === productId ? { ...item, ...patch } : item)));
  }

  function removeItem(productId: string) {
    setCart((prev) => prev.filter((item) => item.product.id !== productId));
  }

  function submitAll() {
    setSummary(null);
    const ready = cart.filter((item) => Number(item.quantity) > 0);
    if (ready.length === 0) {
      setSummary("กรุณากำหนดจำนวนของอย่างน้อย 1 รายการก่อนบันทึก");
      return;
    }

    startTransition(async () => {
      const results = await bulkAdjustStock(
        ready.map((item) => ({
          productId: item.product.id,
          direction: item.direction,
          unitMode: item.unitMode,
          quantity: Number(item.quantity),
          note: item.note,
        })),
      );

      // คำนวณจำนวนสำเร็จ/ล้มเหลวจาก results ตรงๆ ก่อน (ไม่พึ่งตัวแปรที่แก้ไขใน callback ของ setCart
      // เพราะ callback นั้นอาจยังไม่ถูกเรียกทันทีตอนอ่านค่าต่อจากนี้)
      const successCount = results.filter((r) => r.ok).length;
      const failures = results
        .filter((r) => !r.ok)
        .map((r) => {
          const item = cart.find((c) => c.product.id === r.productId);
          return `${item?.product.name ?? r.productId}: ${r.error}`;
        });

      setCart((prev) =>
        prev
          .map((item) => {
            const result = results.find((r) => r.productId === item.product.id);
            if (!result) return item;
            if (result.ok) return null;
            return { ...item, error: result.error };
          })
          .filter((item): item is CartItem => item !== null),
      );

      let text = `ปรับสต็อกสำเร็จ ${successCount} รายการ`;
      if (failures.length > 0) {
        text += `\n\nรายการที่ไม่สำเร็จ (ยังค้างอยู่ให้แก้ไข):\n${failures.join("\n")}`;
      }
      setSummary(text);
      router.refresh();
    });
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="ค้นหาสินค้าเพื่อเพิ่มเข้ารายการ..."
          className="w-full rounded-xl border border-border bg-card px-3 py-2"
        />
        {searchResults.length > 0 && (
          <div className="absolute z-10 mt-1 w-full rounded-xl border border-border bg-card shadow-lg overflow-hidden">
            {searchResults.map((p) => (
              <button
                key={p.id}
                onClick={() => addToCart(p)}
                className="w-full text-left px-3 py-2 border-b border-border last:border-0 hover:bg-brand-light"
              >
                <p className="text-sm font-medium">{p.name}</p>
                <p className="text-xs text-muted">
                  คงเหลือ {p.currentStock} {p.baseUnit}
                </p>
              </button>
            ))}
          </div>
        )}
      </div>

      {cart.length === 0 ? (
        <p className="text-center text-muted text-sm py-8">ยังไม่มีสินค้าในรายการ ค้นหาแล้วแตะเพื่อเพิ่ม</p>
      ) : (
        <div className="space-y-3">
          {cart.map((item) => (
            <div key={item.product.id} className="rounded-xl border border-border bg-card p-3 space-y-2">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium text-sm">{item.product.name}</p>
                  <p className="text-xs text-muted">
                    คงเหลือ {item.product.currentStock} {item.product.baseUnit}
                  </p>
                </div>
                <button onClick={() => removeItem(item.product.id)} className="text-xs text-danger">
                  ลบออก
                </button>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => updateItem(item.product.id, { direction: "IN" })}
                  className={`flex-1 rounded-lg py-1.5 text-xs font-semibold border ${
                    item.direction === "IN" ? "bg-brand text-white border-brand" : "border-border text-muted"
                  }`}
                >
                  เพิ่มเข้า
                </button>
                <button
                  onClick={() => updateItem(item.product.id, { direction: "OUT" })}
                  className={`flex-1 rounded-lg py-1.5 text-xs font-semibold border ${
                    item.direction === "OUT" ? "bg-danger text-white border-danger" : "border-border text-muted"
                  }`}
                >
                  ลดออก
                </button>
              </div>

              <div className="flex gap-2">
                <input
                  type="number"
                  inputMode="decimal"
                  min="0"
                  value={item.quantity}
                  onChange={(e) => updateItem(item.product.id, { quantity: e.target.value })}
                  placeholder="จำนวน"
                  className="flex-1 rounded-lg border border-border px-2 py-1.5 text-sm"
                />
                {item.product.packUnit && (
                  <select
                    value={item.unitMode}
                    onChange={(e) => updateItem(item.product.id, { unitMode: e.target.value as StockUnitMode })}
                    className="rounded-lg border border-border px-2 py-1.5 text-xs"
                  >
                    <option value="BASE">{item.product.baseUnit}</option>
                    <option value="PACK">{item.product.packUnit}</option>
                  </select>
                )}
              </div>

              <input
                type="text"
                value={item.note}
                onChange={(e) => updateItem(item.product.id, { note: e.target.value })}
                placeholder="เหตุผล/หมายเหตุ"
                className="w-full rounded-lg border border-border px-2 py-1.5 text-sm"
              />

              {item.error && <p className="text-danger text-xs">{item.error}</p>}
            </div>
          ))}
        </div>
      )}

      {summary && (
        <p className="whitespace-pre-line text-sm rounded-lg bg-brand-light/60 border border-brand-light p-3">
          {summary}
        </p>
      )}

      <button
        onClick={submitAll}
        disabled={isPending || cart.length === 0}
        className="w-full rounded-xl bg-brand text-white font-semibold py-3 disabled:opacity-50"
      >
        {isPending ? "กำลังบันทึก..." : "บันทึกการปรับสต็อกทั้งหมด"}
      </button>
    </div>
  );
}
