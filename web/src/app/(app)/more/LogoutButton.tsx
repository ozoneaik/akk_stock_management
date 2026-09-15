"use client";

import { useTransition } from "react";

import { logout } from "@/app/actions/auth";

export function LogoutButton() {
  const [isPending, startTransition] = useTransition();

  return (
    <button
      onClick={() => startTransition(() => logout())}
      disabled={isPending}
      className="w-full rounded-xl border border-danger text-danger font-semibold py-3 disabled:opacity-50"
    >
      {isPending ? "กำลังออกจากระบบ..." : "ออกจากระบบ"}
    </button>
  );
}
