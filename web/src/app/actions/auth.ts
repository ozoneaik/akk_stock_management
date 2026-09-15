"use server";

import { redirect } from "next/navigation";

import { prisma } from "@/lib/prisma";
import { createSession, destroySession, getCurrentUser } from "@/lib/auth";
import { addActivityLog } from "@/lib/activity-log";

export async function loginWithPin(username: string, pin: string) {
  const user = await prisma.user.findUnique({ where: { username } });

  if (!user || !user.isActive || !user.pin || user.pin !== pin) {
    return { ok: false as const, error: "PIN ไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง" };
  }

  await createSession({
    userId: user.id,
    username: user.username,
    name: user.name,
    role: user.role,
  });

  await addActivityLog({
    userId: user.id,
    userRole: user.role,
    action: "UPDATE",
    entityType: "User",
    entityId: user.id,
    description: `${user.name} เข้าสู่ระบบสำเร็จ`,
  });

  return { ok: true as const };
}

export async function logout() {
  const user = await getCurrentUser();
  if (user) {
    await addActivityLog({
      userId: user.id,
      userRole: user.role,
      action: "UPDATE",
      entityType: "User",
      entityId: user.id,
      description: `${user.name} ออกจากระบบ`,
    });
  }
  await destroySession();
  redirect("/login");
}
