"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { prisma } from "@/lib/prisma";
import { requireAdmin } from "@/lib/auth";
import { addActivityLog } from "@/lib/activity-log";

export type UserFormState = { error?: string } | null;

function readUserForm(formData: FormData) {
  return {
    username: String(formData.get("username") ?? "").trim(),
    name: String(formData.get("name") ?? "").trim(),
    role: String(formData.get("role") ?? "").trim(),
    pin: String(formData.get("pin") ?? "").trim(),
    avatarUrl: String(formData.get("avatarUrl") ?? "").trim() || null,
  };
}

function validateUserForm(data: ReturnType<typeof readUserForm>, isEdit: boolean): string | null {
  if (!data.username) return "กรุณากรอกชื่อผู้ใช้ (username)";
  if (!data.name) return "กรุณากรอกชื่อที่แสดง";
  if (data.role !== "ADMIN" && data.role !== "OWNER") return "กรุณาเลือกบทบาทผู้ใช้";
  if (!isEdit && !data.pin) return "กรุณากำหนดรหัส PIN";
  if (data.pin && !/^\d{4}$/.test(data.pin)) return "PIN ต้องเป็นตัวเลข 4 หลัก";
  return null;
}

async function countActiveAdmins() {
  return prisma.user.count({ where: { role: "ADMIN", isActive: true } });
}

export async function createUser(_prev: UserFormState, formData: FormData): Promise<UserFormState> {
  const admin = await requireAdmin();
  const data = readUserForm(formData);

  const error = validateUserForm(data, false);
  if (error) return { error };

  const existing = await prisma.user.findUnique({ where: { username: data.username } });
  if (existing) return { error: "ชื่อผู้ใช้นี้ถูกใช้ไปแล้ว" };

  const user = await prisma.user.create({
    data: {
      id: crypto.randomUUID(),
      username: data.username,
      name: data.name,
      role: data.role,
      pin: data.pin,
      avatarUrl: data.avatarUrl,
      updatedAt: new Date(),
    },
  });

  await addActivityLog({
    userId: admin.id,
    userRole: admin.role,
    action: "CREATE",
    entityType: "User",
    entityId: user.id,
    description: `${admin.name} เพิ่มผู้ใช้งานใหม่ "${user.name}" (${user.username})`,
  });

  revalidatePath("/users");
  redirect("/users");
}

export async function updateUser(
  userId: string,
  _prev: UserFormState,
  formData: FormData,
): Promise<UserFormState> {
  const admin = await requireAdmin();
  const data = readUserForm(formData);

  const error = validateUserForm(data, true);
  if (error) return { error };

  const target = await prisma.user.findUnique({ where: { id: userId } });
  if (!target) return { error: "ไม่พบผู้ใช้งานนี้ในระบบ" };

  if (target.role === "ADMIN" && data.role !== "ADMIN" && (await countActiveAdmins()) <= 1) {
    return { error: "ต้องมีผู้ใช้บทบาทแอดมินอย่างน้อย 1 คนในระบบเสมอ" };
  }

  await prisma.user.update({
    where: { id: userId },
    data: {
      name: data.name,
      role: data.role,
      avatarUrl: data.avatarUrl,
      ...(data.pin ? { pin: data.pin } : {}),
    },
  });

  await addActivityLog({
    userId: admin.id,
    userRole: admin.role,
    action: "UPDATE",
    entityType: "User",
    entityId: userId,
    description: `${admin.name} แก้ไขข้อมูลผู้ใช้งาน "${data.name}" (${target.username})`,
  });

  revalidatePath("/users");
  redirect("/users");
}

export async function deactivateUser(userId: string) {
  const admin = await requireAdmin();

  if (userId === admin.id) {
    throw new Error("ไม่สามารถลบบัญชีผู้ใช้ที่กำลังใช้งานอยู่ได้");
  }

  const target = await prisma.user.findUnique({ where: { id: userId } });
  if (!target) throw new Error("ไม่พบผู้ใช้งานนี้ในระบบ");

  if (target.role === "ADMIN" && (await countActiveAdmins()) <= 1) {
    throw new Error("ต้องมีผู้ใช้บทบาทแอดมินอย่างน้อย 1 คนในระบบเสมอ");
  }

  await prisma.user.update({ where: { id: userId }, data: { isActive: false } });

  await addActivityLog({
    userId: admin.id,
    userRole: admin.role,
    action: "DELETE",
    entityType: "User",
    entityId: userId,
    description: `${admin.name} ลบผู้ใช้งาน "${target.name}" (${target.username})`,
  });

  revalidatePath("/users");
}
