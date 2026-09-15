"use client";

import { useActionState } from "react";

import type { ProductFormState } from "@/app/actions/products";

type ProductFormAction = (state: ProductFormState, formData: FormData) => Promise<ProductFormState>;

type InitialProduct = {
  name: string;
  commonName: string;
  sku: string;
  barcode: string;
  categoryName: string;
  baseUnit: string;
  packUnit: string;
  unitsPerPack: number;
  minStockAlert: number;
  currentStock: number;
  imageUrl: string;
  description: string;
  price: number | null;
};

const EMPTY: InitialProduct = {
  name: "",
  commonName: "",
  sku: "",
  barcode: "",
  categoryName: "",
  baseUnit: "ขวด",
  packUnit: "ลัง",
  unitsPerPack: 12,
  minStockAlert: 10,
  currentStock: 0,
  imageUrl: "",
  description: "",
  price: null,
};

export function ProductForm({
  action,
  categoryNames,
  initial,
  isEdit,
  submitLabel,
}: {
  action: ProductFormAction;
  categoryNames: string[];
  initial?: InitialProduct;
  isEdit?: boolean;
  submitLabel: string;
}) {
  const [state, formAction, isPending] = useActionState(action, null);
  const data = initial ?? EMPTY;

  return (
    <form action={formAction} className="space-y-4 pb-8">
      {state?.error && (
        <p className="rounded-lg bg-red-50 border border-red-200 text-danger text-sm p-3">{state.error}</p>
      )}

      <Field label="ชื่อสินค้า *">
        <input name="name" required defaultValue={data.name} className="input" />
      </Field>

      <Field label="ชื่อสามัญ / ชื่อสารสำคัญ">
        <input name="commonName" defaultValue={data.commonName} className="input" />
      </Field>

      <Field label="หมวดหมู่ *">
        <input
          name="categoryName"
          required
          list="category-suggestions"
          defaultValue={data.categoryName}
          placeholder="เลือกหรือพิมพ์หมวดหมู่ใหม่"
          className="input"
        />
        <datalist id="category-suggestions">
          {categoryNames.map((name) => (
            <option key={name} value={name} />
          ))}
        </datalist>
      </Field>

      <div className="grid grid-cols-2 gap-3">
        <Field label="รหัสสินค้า (SKU)">
          <input name="sku" defaultValue={data.sku} className="input" />
        </Field>
        <Field label="บาร์โค้ด">
          <input name="barcode" defaultValue={data.barcode} className="input" />
        </Field>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Field label="หน่วยนับย่อย *">
          <input name="baseUnit" required defaultValue={data.baseUnit} className="input" />
        </Field>
        <Field label="หน่วยบรรจุ (แพ็ค)">
          <input name="packUnit" defaultValue={data.packUnit} className="input" />
        </Field>
      </div>

      <Field label="จำนวนหน่วยย่อยต่อแพ็ค *">
        <input
          type="number"
          name="unitsPerPack"
          min="1"
          required
          defaultValue={data.unitsPerPack}
          className="input"
        />
      </Field>

      {!isEdit && (
        <Field label="จำนวนคงเหลือเริ่มต้น *">
          <input
            type="number"
            name="currentStock"
            min="0"
            required
            defaultValue={data.currentStock}
            className="input"
          />
        </Field>
      )}
      {isEdit && (
        <p className="text-xs text-muted -mt-2">
          * แก้ไขจำนวนสต็อกได้ที่ปุ่ม &quot;ปรับสต็อกสินค้า&quot; ในหน้ารายละเอียดสินค้าเท่านั้น
        </p>
      )}

      <Field label="แจ้งเตือนเมื่อเหลือน้อยกว่า *">
        <input
          type="number"
          name="minStockAlert"
          min="0"
          required
          defaultValue={data.minStockAlert}
          className="input"
        />
      </Field>

      <Field label="ราคาขายหน้าร้าน (บาท)">
        <input
          type="number"
          name="price"
          min="0"
          step="0.01"
          defaultValue={data.price ?? ""}
          className="input"
        />
      </Field>

      <Field label="ลิงก์รูปภาพสินค้า (URL)">
        <input name="imageUrl" type="url" defaultValue={data.imageUrl} placeholder="https://..." className="input" />
      </Field>

      <Field label="รายละเอียด/หมายเหตุ">
        <textarea name="description" defaultValue={data.description} rows={3} className="input" />
      </Field>

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-xl bg-brand text-white font-semibold py-3 disabled:opacity-50"
      >
        {isPending ? "กำลังบันทึก..." : submitLabel}
      </button>

      <style jsx global>{`
        .input {
          width: 100%;
          border-radius: 0.75rem;
          border: 1px solid var(--border);
          background: var(--card);
          padding: 0.6rem 0.75rem;
        }
      `}</style>
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-sm font-medium mb-1">{label}</span>
      {children}
    </label>
  );
}
