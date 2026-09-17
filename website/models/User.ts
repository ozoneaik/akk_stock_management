import bcrypt from "bcryptjs";

import { prisma } from "@/lib/prisma";
import { newId } from "@/lib/id";
import { AppError } from "@/lib/errors";
import { ROLES } from "@/lib/constants";

export type UserInput = {
  username: string;
  name: string;
  role: string;
  password?: string;
};

/** คืนข้อความ error ถ้าข้อมูลไม่ถูกต้อง หรือคืน null ถ้าข้อมูลผ่าน (isEdit = true จะไม่บังคับกรอก password) */
export function validateUserInput(data: UserInput, isEdit: boolean) {
  if (!data.username?.trim()) throw new AppError("กรุณากรอกชื่อผู้ใช้ (username)");
  if (!data.name?.trim()) throw new AppError("กรุณากรอกชื่อที่แสดง");
  if (!ROLES.includes(data.role as (typeof ROLES)[number])) throw new AppError("กรุณาเลือกบทบาทผู้ใช้");
  if (!isEdit && !data.password?.trim()) throw new AppError("กรุณากำหนดรหัสผ่าน");
  if (data.password && data.password.trim().length < 4) throw new AppError("รหัสผ่านต้องมีอย่างน้อย 4 ตัวอักษร");
}

export async function authenticate(username: string, password: string) {
  const user = await prisma.user.findUnique({ where: { username } });
  if (!user || !user.isActive || !user.password) return null;

  const ok = await bcrypt.compare(password, user.password);
  if (!ok) return null;

  return user;
}

export async function getAllUsers(activeOnly = true) {
  return prisma.user.findMany({
    where: activeOnly ? { isActive: true } : undefined,
    orderBy: { username: "asc" },
  });
}

export async function getUserById(id: string) {
  return prisma.user.findUnique({ where: { id } });
}

export async function countActiveAdmins() {
  return prisma.user.count({ where: { role: "ADMIN", isActive: true } });
}

export async function createUser(data: UserInput) {
  const hashed = await bcrypt.hash(data.password!.trim(), 10);
  const user = await prisma.user.create({
    data: {
      id: newId(),
      username: data.username.trim(),
      name: data.name.trim(),
      role: data.role,
      password: hashed,
      updatedAt: new Date(),
    },
  });
  return user.id;
}

/** แก้ไขชื่อที่แสดงและบทบาทของผู้ใช้ ไม่รวม password ใช้ updatePassword แยกต่างหาก */
export async function updateUser(id: string, data: { name: string; role: string }) {
  await prisma.user.update({
    where: { id },
    data: { name: data.name.trim(), role: data.role, updatedAt: new Date() },
  });
}

export async function updatePassword(id: string, newPassword: string) {
  const hashed = await bcrypt.hash(newPassword.trim(), 10);
  await prisma.user.update({ where: { id }, data: { password: hashed, updatedAt: new Date() } });
}

/** ลบผู้ใช้แบบ soft-delete เพราะมี FK จากตารางอื่นอ้างถึงผู้ใช้อยู่ (stock_movement, activity_log) */
export async function deactivateUser(id: string) {
  await prisma.user.update({ where: { id }, data: { isActive: false, updatedAt: new Date() } });
}
