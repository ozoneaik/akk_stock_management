import Link from "next/link";

import { getCurrentUser } from "@/lib/auth";
import { LogoutButton } from "./LogoutButton";

const ROLE_LABELS: Record<string, string> = { ADMIN: "แอดมิน", OWNER: "เจ้าของร้าน" };

export default async function MorePage() {
  const user = await getCurrentUser();
  const isAdmin = user?.role === "ADMIN";

  return (
    <div className="px-4 py-5 space-y-5">
      <div className="rounded-xl border border-border bg-card p-4">
        <p className="font-semibold">{user?.name}</p>
        <p className="text-sm text-muted">{ROLE_LABELS[user?.role ?? ""] ?? user?.role}</p>
      </div>

      {isAdmin && (
        <div className="rounded-xl border border-border bg-card divide-y divide-border overflow-hidden">
          <MenuLink href="/users" label="จัดการผู้ใช้งาน" />
          <MenuLink href="/activity" label="บันทึกกิจกรรม" />
        </div>
      )}

      <LogoutButton />
    </div>
  );
}

function MenuLink({ href, label }: { href: string; label: string }) {
  return (
    <Link href={href} className="flex justify-between items-center px-4 py-3">
      <span>{label}</span>
      <span className="text-muted">›</span>
    </Link>
  );
}
