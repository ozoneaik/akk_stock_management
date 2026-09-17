import { NextResponse } from "next/server";

import { getCurrentUser, destroySession } from "@/lib/auth";
import { addLog } from "@/models/Activity";

export async function POST() {
  const user = await getCurrentUser();
  if (user) {
    await addLog({
      userId: user.id,
      userRole: user.role,
      action: "UPDATE",
      entityType: "User",
      entityId: user.id,
      description: `${user.name} ออกจากระบบ`,
    });
  }
  await destroySession();
  return NextResponse.json({ ok: true });
}
