import { createProduct } from "@/app/actions/products";
import { prisma } from "@/lib/prisma";
import { ProductForm } from "@/components/ProductForm";

export default async function NewProductPage() {
  const categories = await prisma.category.findMany({ orderBy: { name: "asc" } });

  return (
    <div className="px-4 py-5">
      <h1 className="text-xl font-bold mb-4">เพิ่มสินค้าใหม่</h1>
      <ProductForm
        action={createProduct}
        categoryNames={categories.map((c) => c.name)}
        submitLabel="บันทึกสินค้าใหม่"
      />
    </div>
  );
}
