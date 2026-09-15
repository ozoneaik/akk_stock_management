"use client";

import { useTransition } from "react";

import { deactivateUser } from "@/app/actions/users";

export function DeactivateUserButton({ userId, userName }: { userId: string; userName: string }) {
  const [isPending, startTransition] = useTransition();

  function handleClick() {
    if (!confirm(`ต้องการลบผู้ใช้งาน "${userName}" ใช่หรือไม่?`)) return;
    startTransition(async () => {
      try {
        await deactivateUser(userId);
      } catch (e) {
        alert(e instanceof Error ? e.message : "เกิดข้อผิดพลาด");
      }
    });
  }

  return (
    <button onClick={handleClick} disabled={isPending} className="text-sm text-danger font-semibold">
      {isPending ? "กำลังลบ..." : "ลบ"}
    </button>
  );
}
