import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";

import { prisma } from "@/lib/prisma";
import { QuickStockAdjust } from "@/components/QuickStockAdjust";
import { DeactivateProductButton } from "./DeactivateProductButton";

const CHANNEL_LABELS: Record<string, string> = {
  STORE: "หน้าร้าน",
  TIKTOK: "TikTok",
  LAZADA: "Lazada",
  SHOPEE: "Shopee",
};

export default async function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  const product = await prisma.product.findUnique({
    where: { id },
    include: { category: true, prices: true },
  });

  if (!product || !product.isActive) {
    notFound();
  }

  return (
    <div className="px-4 py-5 space-y-4">
      <Link href="/products" className="text-sm text-muted">
        ← กลับไปรายการสินค้า
      </Link>

      {product.imageUrl && (
        <div className="w-full aspect-video rounded-xl overflow-hidden relative bg-brand-light">
          <Image src={product.imageUrl} alt={product.name} fill sizes="100vw" className="object-cover" />
        </div>
      )}

      <div>
        <h1 className="text-xl font-bold">{product.name}</h1>
        {product.commonName && <p className="text-sm text-muted">{product.commonName}</p>}
      </div>

      <div className="rounded-xl border border-border bg-card divide-y divide-border">
        <InfoRow label="หมวดหมู่" value={product.category.name} />
        {product.sku && <InfoRow label="รหัสสินค้า (SKU)" value={product.sku} />}
        {product.barcode && <InfoRow label="บาร์โค้ด" value={product.barcode} />}
        <InfoRow
          label="คงเหลือ"
          value={`${product.currentStock} ${product.baseUnit}`}
          valueClassName={product.currentStock < product.minStockAlert ? "text-danger font-bold" : "font-bold"}
        />
        <InfoRow label="แจ้งเตือนเมื่อเหลือน้อยกว่า" value={`${product.minStockAlert} ${product.baseUnit}`} />
        {product.packUnit && (
          <InfoRow label="หน่วยบรรจุ" value={`1 ${product.packUnit} = ${product.unitsPerPack} ${product.baseUnit}`} />
        )}
      </div>

      {product.prices.length > 0 && (
        <div className="rounded-xl border border-border bg-card divide-y divide-border">
          {product.prices.map((price) => (
            <InfoRow
              key={price.id}
              label={CHANNEL_LABELS[price.channel] ?? price.channel}
              value={`${price.price.toLocaleString()} บาท`}
            />
          ))}
        </div>
      )}

      {product.description && (
        <div className="rounded-xl border border-border bg-card p-3">
          <p className="text-sm font-medium mb-1">รายละเอียด</p>
          <p className="text-sm text-muted whitespace-pre-line">{product.description}</p>
        </div>
      )}

      <QuickStockAdjust
        product={{
          id: product.id,
          name: product.name,
          currentStock: product.currentStock,
          baseUnit: product.baseUnit,
          packUnit: product.packUnit,
          unitsPerPack: product.unitsPerPack,
        }}
      />

      <div className="flex gap-2">
        <Link
          href={`/products/${product.id}/edit`}
          className="flex-1 text-center rounded-xl border border-border py-3 font-semibold"
        >
          แก้ไขสินค้า
        </Link>
        <DeactivateProductButton productId={product.id} productName={product.name} />
      </div>
    </div>
  );
}

function InfoRow({
  label,
  value,
  valueClassName,
}: {
  label: string;
  value: string;
  valueClassName?: string;
}) {
  return (
    <div className="flex justify-between items-center px-3 py-2.5 text-sm">
      <span className="text-muted">{label}</span>
      <span className={valueClassName ?? ""}>{value}</span>
    </div>
  );
}
