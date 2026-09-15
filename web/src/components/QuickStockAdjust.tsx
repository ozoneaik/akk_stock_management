"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { adjustStock, type StockDirection, type StockUnitMode } from "@/app/actions/stock";

type Product = {
  id: string;
  name: string;
  currentStock: number;
  baseUnit: string;
  packUnit: string | null;
  unitsPerPack: number;
};

export function QuickStockAdjust({ product }: { product: Product }) {
  const [open, setOpen] = useState(false);
  const [direction, setDirection] = useState<StockDirection>("IN");
  const [unitMode, setUnitMode] = useState<StockUnitMode>("BASE");
  const [quantity, setQuantity] = useState("");
  const [note, setNote] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  function submit() {
    const qty = Number(quantity);
    if (!Number.isFinite(qty) || qty <= 0) {
      setError("กรุณากรอกจำนวนเป็นตัวเลขมากกว่า 0");
      return;
    }
    setError(null);
    startTransition(async () => {
      const result = await adjustStock({ productId: product.id, direction, unitMode, quantity: qty, note });
      if (!result.ok) {
        setError(result.error ?? "เกิดข้อผิดพลาด");
        return;
      }
      setOpen(false);
      setQuantity("");
      setNote("");
      router.refresh();
    });
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="w-full rounded-xl bg-brand text-white font-semibold py-3"
      >
        ปรับสต็อกสินค้า
      </button>
    );
  }

  return (
    <div className="rounded-xl border border-border bg-card p-4 space-y-3">
      <p className="font-semibold">ปรับสต็อก: {product.name}</p>
      <p className="text-sm text-muted">คงเหลือปัจจุบัน {product.currentStock} {product.baseUnit}</p>

      <div className="flex gap-2">
        <button
          onClick={() => setDirection("IN")}
          className={`flex-1 rounded-lg py-2 text-sm font-semibold border ${
            direction === "IN" ? "bg-brand text-white border-brand" : "border-border text-muted"
          }`}
        >
          เพิ่มเข้า (รับของ)
        </button>
        <button
          onClick={() => setDirection("OUT")}
          className={`flex-1 rounded-lg py-2 text-sm font-semibold border ${
            direction === "OUT" ? "bg-danger text-white border-danger" : "border-border text-muted"
          }`}
        >
          ลดออก (ขาย/ชำรุด)
        </button>
      </div>

      <div className="flex gap-2 items-center">
        <input
          type="number"
          inputMode="decimal"
          min="0"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          placeholder="จำนวน"
          className="flex-1 rounded-lg border border-border px-3 py-2"
        />
        {product.packUnit && (
          <select
            value={unitMode}
            onChange={(e) => setUnitMode(e.target.value as StockUnitMode)}
            className="rounded-lg border border-border px-2 py-2 text-sm"
          >
            <option value="BASE">{product.baseUnit}</option>
            <option value="PACK">
              {product.packUnit} ({product.unitsPerPack} {product.baseUnit})
            </option>
          </select>
        )}
      </div>

      <input
        type="text"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="เหตุผล/หมายเหตุ (ถ้ามี)"
        className="w-full rounded-lg border border-border px-3 py-2"
      />

      {error && <p className="text-danger text-sm">{error}</p>}

      <div className="flex gap-2">
        <button
          onClick={submit}
          disabled={isPending}
          className="flex-1 rounded-lg bg-brand text-white font-semibold py-2 disabled:opacity-50"
        >
          {isPending ? "กำลังบันทึก..." : "บันทึก"}
        </button>
        <button
          onClick={() => setOpen(false)}
          className="flex-1 rounded-lg border border-border py-2 text-muted"
        >
          ยกเลิก
        </button>
      </div>
    </div>
  );
}
