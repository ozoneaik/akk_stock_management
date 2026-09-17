"use client";

import { useState } from "react";

import { CHANNEL_LABELS } from "@/lib/constants";
import { apiFetch, ApiClientError } from "@/lib/api-client";
import type { ProductDTO } from "@/lib/types";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Field, Input, Select, ErrorBanner } from "@/components/ui/Field";

export function ProductDetailModal({
  product,
  onClose,
  onChanged,
}: {
  product: ProductDTO;
  onClose: () => void;
  onChanged: (newStock: number) => void;
}) {
  const [currentStock, setCurrentStock] = useState(product.currentStock);
  const [showAdjust, setShowAdjust] = useState(false);
  const [mode, setMode] = useState<"IN" | "OUT">("IN");
  const [unit, setUnit] = useState(product.baseUnit);
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const unitOptions = product.packUnit ? [product.baseUnit, product.packUnit] : [product.baseUnit];

  async function handleAdjust() {
    setError(null);
    const qty = Number(quantity);
    if (!qty || qty <= 0) {
      setError("กรุณากรอกจำนวนที่มากกว่า 0");
      return;
    }
    const factor = unit === product.packUnit ? product.unitsPerPack : 1;
    const changeAmount = (mode === "IN" ? 1 : -1) * qty * factor;

    setSaving(true);
    try {
      const res = await apiFetch<{ results: { ok: boolean; error?: string; newQuantity?: number }[] }>(
        "/api/stock",
        {
          method: "POST",
          body: JSON.stringify({
            adjustments: [
              { productId: product.id, changeAmount, reason, unitLabel: unit, inputQuantity: qty },
            ],
          }),
        }
      );
      const result = res.results[0];
      if (!result.ok) {
        setError(result.error ?? "ปรับสต็อกไม่สำเร็จ");
        return;
      }
      setCurrentStock(result.newQuantity!);
      onChanged(result.newQuantity!);
      setShowAdjust(false);
      setQuantity("");
      setReason("");
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "ปรับสต็อกไม่สำเร็จ");
    } finally {
      setSaving(false);
    }
  }

  const priceEntries = Object.entries(product.prices).filter(([, v]) => v.price > 0);

  return (
    <Modal title={product.name} onClose={onClose} wide>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span className="text-slate-500">รหัสสินค้า</span>
            <p className="font-medium">{product.sku ?? "-"}</p>
          </div>
          <div>
            <span className="text-slate-500">หมวดหมู่</span>
            <p className="font-medium">{product.categoryName}</p>
          </div>
          <div>
            <span className="text-slate-500">ชื่อสามัญ</span>
            <p className="font-medium">{product.commonName ?? "-"}</p>
          </div>
          <div>
            <span className="text-slate-500">สต็อกคงเหลือ</span>
            <p className="font-medium">
              {currentStock} {product.baseUnit}
              {currentStock < product.minStockAlert && (
                <span className="ml-2 rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-700">ใกล้หมด</span>
              )}
            </p>
          </div>
        </div>

        {product.description && (
          <div className="text-sm">
            <span className="text-slate-500">หมายเหตุ</span>
            <p>{product.description}</p>
          </div>
        )}

        {priceEntries.length > 0 && (
          <div>
            <span className="text-sm text-slate-500">ราคาขาย</span>
            <table className="mt-1 w-full text-sm">
              <tbody>
                {priceEntries.map(([channel, info]) => (
                  <tr key={channel} className="border-t border-slate-100">
                    <td className="py-1 text-slate-600">{CHANNEL_LABELS[channel] ?? channel}</td>
                    <td className="py-1 text-right font-medium">{info.price.toLocaleString()} บาท</td>
                    <td className="py-1 text-right text-slate-500">
                      {info.discount > 0 ? `ลด ${info.discount.toLocaleString()}` : ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="border-t border-slate-200 pt-4">
          {!showAdjust ? (
            <Button variant="secondary" onClick={() => setShowAdjust(true)}>
              ปรับสต็อกสินค้า
            </Button>
          ) : (
            <div className="space-y-3 rounded-md bg-slate-50 p-3">
              {error && <ErrorBanner message={error} />}
              <div className="grid grid-cols-2 gap-3">
                <Field label="รูปแบบ">
                  <Select value={mode} onChange={(e) => setMode(e.target.value as "IN" | "OUT")}>
                    <option value="IN">เพิ่มสต็อก</option>
                    <option value="OUT">ลดสต็อก</option>
                  </Select>
                </Field>
                <Field label="หน่วย">
                  <Select value={unit} onChange={(e) => setUnit(e.target.value)}>
                    {unitOptions.map((u) => (
                      <option key={u} value={u}>
                        {u}
                      </option>
                    ))}
                  </Select>
                </Field>
                <Field label="จำนวน" required>
                  <Input
                    type="number"
                    min={0}
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                  />
                </Field>
                <Field label="เหตุผล">
                  <Input value={reason} onChange={(e) => setReason(e.target.value)} />
                </Field>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="ghost" onClick={() => setShowAdjust(false)}>
                  ยกเลิก
                </Button>
                <Button onClick={handleAdjust} disabled={saving}>
                  {saving ? "กำลังบันทึก..." : "บันทึก"}
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
}
