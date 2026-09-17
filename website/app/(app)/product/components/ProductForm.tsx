"use client";

import { useEffect, useState } from "react";

import { apiFetch, ApiClientError } from "@/lib/api-client";
import { SALES_CHANNELS, CHANNEL_LABELS, DEFAULT_PACKAGING_UNITS, LOW_STOCK_DEFAULT_THRESHOLD } from "@/lib/constants";
import type { ProductDTO, CategoryDTO } from "@/lib/types";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Field, Input, Select, TextArea, ErrorBanner } from "@/components/ui/Field";

const NEW_CATEGORY = "__new__";

type PriceForm = { price: string; discount: string };

export function ProductForm({
  product,
  onClose,
  onSaved,
}: {
  product: ProductDTO | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const isEdit = Boolean(product);
  const [categories, setCategories] = useState<CategoryDTO[]>([]);
  const [categoryId, setCategoryId] = useState(product?.categoryId ?? "");
  const [newCategoryName, setNewCategoryName] = useState("");

  const [sku, setSku] = useState(product?.sku ?? "");
  const [name, setName] = useState(product?.name ?? "");
  const [commonName, setCommonName] = useState(product?.commonName ?? "");
  const [baseUnit, setBaseUnit] = useState(product?.baseUnit ?? "ขวด");
  const [packUnit, setPackUnit] = useState(product?.packUnit ?? "");
  const [unitsPerPack, setUnitsPerPack] = useState(String(product?.unitsPerPack ?? 12));
  const [quantity, setQuantity] = useState(String(product?.currentStock ?? 0));
  const [minStockAlert, setMinStockAlert] = useState(String(product?.minStockAlert ?? LOW_STOCK_DEFAULT_THRESHOLD));
  const [imageUrl, setImageUrl] = useState(product?.imageUrl ?? "");
  const [description, setDescription] = useState(product?.description ?? "");
  const [prices, setPrices] = useState<Record<string, PriceForm>>(() => {
    const initial: Record<string, PriceForm> = {};
    for (const channel of SALES_CHANNELS) {
      const existing = product?.prices?.[channel];
      initial[channel] = { price: existing ? String(existing.price) : "", discount: existing?.discount ? String(existing.discount) : "" };
    }
    return initial;
  });

  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    apiFetch<{ categories: CategoryDTO[] }>("/api/category")
      .then((res) => setCategories(res.categories))
      .catch(() => {});
  }, []);

  async function handleSubmit() {
    setError(null);
    setSaving(true);
    try {
      let resolvedCategoryId = categoryId;
      if (categoryId === NEW_CATEGORY) {
        if (!newCategoryName.trim()) throw new ApiClientError("กรุณากรอกชื่อหมวดหมู่ใหม่");
        const res = await apiFetch<{ id: string }>("/api/category", {
          method: "POST",
          body: JSON.stringify({ name: newCategoryName }),
        });
        resolvedCategoryId = res.id;
      }

      const priceEntries = Object.entries(prices).filter(([, v]) => v.price.trim() !== "");
      const payload = {
        sku,
        name,
        commonName,
        categoryId: resolvedCategoryId,
        baseUnit,
        packUnit: packUnit || undefined,
        unitsPerPack: Number(unitsPerPack),
        quantity: Number(quantity),
        minStockAlert: Number(minStockAlert),
        imageUrl,
        description,
        prices: Object.fromEntries(
          priceEntries.map(([channel, v]) => [channel, { price: Number(v.price), discount: Number(v.discount || 0) }])
        ),
      };

      if (isEdit) {
        await apiFetch(`/api/product/${product!.id}`, { method: "PATCH", body: JSON.stringify(payload) });
      } else {
        await apiFetch("/api/product", { method: "POST", body: JSON.stringify(payload) });
      }

      onSaved();
      onClose();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "บันทึกข้อมูลไม่สำเร็จ");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal title={isEdit ? "แก้ไขสินค้า" : "เพิ่มสินค้าใหม่"} onClose={onClose} wide>
      <div className="max-h-[70vh] space-y-4 overflow-y-auto pr-1">
        {error && <ErrorBanner message={error} />}

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Field label="รหัสสินค้า (SKU)" required>
            <Input value={sku} onChange={(e) => setSku(e.target.value)} />
          </Field>
          <Field label="ชื่อสินค้า" required>
            <Input value={name} onChange={(e) => setName(e.target.value)} />
          </Field>
          <Field label="ชื่อสามัญ">
            <Input value={commonName} onChange={(e) => setCommonName(e.target.value)} />
          </Field>
          <Field label="หมวดหมู่">
            <Select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
              <option value="">ไม่ระบุหมวดหมู่</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
              <option value={NEW_CATEGORY}>➕ เพิ่มหมวดหมู่ใหม่</option>
            </Select>
          </Field>
          {categoryId === NEW_CATEGORY && (
            <Field label="ชื่อหมวดหมู่ใหม่" required>
              <Input value={newCategoryName} onChange={(e) => setNewCategoryName(e.target.value)} />
            </Field>
          )}

          <Field label="หน่วยนับย่อย (เช่น ขวด, ซอง)" required>
            <Input value={baseUnit} onChange={(e) => setBaseUnit(e.target.value)} list="packaging-units" />
          </Field>
          <Field label="หน่วยบรรจุ (เช่น ลัง)">
            <Input value={packUnit} onChange={(e) => setPackUnit(e.target.value)} list="packaging-units" />
          </Field>
          <Field label="จำนวนหน่วยย่อยต่อแพ็ค" required>
            <Input type="number" min={1} value={unitsPerPack} onChange={(e) => setUnitsPerPack(e.target.value)} />
          </Field>
          {!isEdit && (
            <Field label="จำนวนสต็อกเริ่มต้น">
              <Input type="number" min={0} value={quantity} onChange={(e) => setQuantity(e.target.value)} />
            </Field>
          )}
          <Field label="แจ้งเตือนเมื่อเหลือน้อยกว่า">
            <Input type="number" min={0} value={minStockAlert} onChange={(e) => setMinStockAlert(e.target.value)} />
          </Field>
          <Field label="ลิงก์รูปภาพ">
            <Input value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} placeholder="https://..." />
          </Field>
        </div>

        <Field label="หมายเหตุ">
          <TextArea rows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
        </Field>

        <div>
          <p className="mb-2 text-sm font-medium text-slate-700">ราคาขายแต่ละช่องทาง</p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {SALES_CHANNELS.map((channel) => (
              <div key={channel} className="rounded-md border border-slate-200 p-3">
                <p className="mb-2 text-sm font-medium text-slate-600">{CHANNEL_LABELS[channel]}</p>
                <div className="grid grid-cols-2 gap-2">
                  <Field label="ราคา">
                    <Input
                      type="number"
                      min={0}
                      value={prices[channel].price}
                      onChange={(e) => setPrices((p) => ({ ...p, [channel]: { ...p[channel], price: e.target.value } }))}
                    />
                  </Field>
                  <Field label="ส่วนลด">
                    <Input
                      type="number"
                      min={0}
                      value={prices[channel].discount}
                      onChange={(e) => setPrices((p) => ({ ...p, [channel]: { ...p[channel], discount: e.target.value } }))}
                    />
                  </Field>
                </div>
              </div>
            ))}
          </div>
        </div>

        <datalist id="packaging-units">
          {DEFAULT_PACKAGING_UNITS.map((u) => (
            <option key={u} value={u} />
          ))}
        </datalist>
      </div>

      <div className="mt-4 flex justify-end gap-2 border-t border-slate-200 pt-4">
        <Button variant="secondary" onClick={onClose}>
          ยกเลิก
        </Button>
        <Button onClick={handleSubmit} disabled={saving}>
          {saving ? "กำลังบันทึก..." : "บันทึก"}
        </Button>
      </div>
    </Modal>
  );
}
