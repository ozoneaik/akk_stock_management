"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

import { deactivateProduct } from "@/app/actions/products";

export function DeactivateProductButton({
  productId,
  productName,
}: {
  productId: string;
  productName: string;
}) {
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  function handleClick() {
    if (!confirm(`ต้องการลบสินค้า "${productName}" ใช่หรือไม่?\nการลบไม่สามารถกู้คืนได้`)) return;
    startTransition(async () => {
      try {
        await deactivateProduct(productId);
        router.push("/products");
      } catch (e) {
        alert(e instanceof Error ? e.message : "เกิดข้อผิดพลาด");
      }
    });
  }

  return (
    <button
      onClick={handleClick}
      disabled={isPending}
      className="flex-1 rounded-xl bg-danger text-white font-semibold py-3 disabled:opacity-50"
    >
      {isPending ? "กำลังลบ..." : "ลบสินค้า"}
    </button>
  );
}
