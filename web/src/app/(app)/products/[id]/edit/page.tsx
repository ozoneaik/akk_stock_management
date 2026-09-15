import { notFound } from "next/navigation";

import { prisma } from "@/lib/prisma";
import { updateProduct } from "@/app/actions/products";
import { ProductForm } from "@/components/ProductForm";

export default async function EditProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  const [product, categories] = await Promise.all([
    prisma.product.findUnique({ where: { id }, include: { category: true, prices: true } }),
    prisma.category.findMany({ orderBy: { name: "asc" } }),
  ]);

  if (!product) notFound();

  const storePrice = product.prices.find((p) => p.channel === "STORE");
  const boundAction = updateProduct.bind(null, product.id);

  return (
    <div className="px-4 py-5">
      <h1 className="text-xl font-bold mb-4">แก้ไขสินค้า</h1>
      <ProductForm
        action={boundAction}
        categoryNames={categories.map((c) => c.name)}
        isEdit
        submitLabel="บันทึกการแก้ไข"
        initial={{
          name: product.name,
          commonName: product.commonName ?? "",
          sku: product.sku ?? "",
          barcode: product.barcode ?? "",
          categoryName: product.category.name,
          baseUnit: product.baseUnit,
          packUnit: product.packUnit ?? "",
          unitsPerPack: product.unitsPerPack,
          minStockAlert: product.minStockAlert,
          currentStock: product.currentStock,
          imageUrl: product.imageUrl ?? "",
          description: product.description ?? "",
          price: storePrice?.price ?? null,
        }}
      />
    </div>
  );
}
