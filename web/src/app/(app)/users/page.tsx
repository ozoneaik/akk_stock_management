import Link from "next/link";
import { redirect } from "next/navigation";

import { prisma } from "@/lib/prisma";
import { getCurrentUser } from "@/lib/auth";
import { DeactivateUserButton } from "./DeactivateUserButton";

const ROLE_LABELS: Record<string, string> = { ADMIN: "แอดมิน", OWNER: "เจ้าของร้าน" };

export default async function UsersPage() {
  const currentUser = await getCurrentUser();
  if (currentUser?.role !== "ADMIN") {
    redirect("/");
  }

  const users = await prisma.user.findMany({
    where: { isActive: true },
    orderBy: { username: "asc" },
  });

  return (
    <div className="px-4 py-5 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">จัดการผู้ใช้งาน</h1>
        <Link href="/users/new" className="bg-brand text-white text-sm font-semibold rounded-full px-4 py-2">
          + เพิ่มผู้ใช้งาน
        </Link>
      </div>

      <div className="space-y-2">
        {users.map((user) => (
          <div key={user.id} className="rounded-xl border border-border bg-card p-3 flex items-center justify-between">
            <div>
              <p className="font-medium">{user.name}</p>
              <p className="text-xs text-muted">
                {user.username} · {ROLE_LABELS[user.role] ?? user.role}
              </p>
            </div>
            <div className="flex gap-2">
              <Link href={`/users/${user.id}/edit`} className="text-sm text-brand-dark font-semibold">
                แก้ไข
              </Link>
              {user.id !== currentUser.id && <DeactivateUserButton userId={user.id} userName={user.name} />}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
