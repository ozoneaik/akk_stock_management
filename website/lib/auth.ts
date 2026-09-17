import "server-only";

import { cookies } from "next/headers";
import { SignJWT, jwtVerify } from "jose";

import { prisma } from "@/lib/prisma";
import { AppError } from "@/lib/errors";

const COOKIE_NAME = "session";
const SESSION_DURATION_SECONDS = 60 * 60 * 24 * 7; // 7 วัน

function getSecretKey() {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    throw new Error("ไม่ได้ตั้งค่า JWT_SECRET ใน .env");
  }
  return new TextEncoder().encode(secret);
}

export type SessionPayload = {
  userId: string;
  username: string;
  name: string;
  role: string;
};

export async function createSession(payload: SessionPayload) {
  const token = await new SignJWT({ ...payload })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime(`${SESSION_DURATION_SECONDS}s`)
    .sign(getSecretKey());

  const cookieStore = await cookies();
  cookieStore.set(COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_DURATION_SECONDS,
  });
}

export async function destroySession() {
  const cookieStore = await cookies();
  cookieStore.delete(COOKIE_NAME);
}

/** อ่าน session จาก cookie เฉยๆ ไม่เช็คฐานข้อมูล (เร็ว ใช้ใน proxy) */
export async function readSessionCookie(): Promise<SessionPayload | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get(COOKIE_NAME)?.value;
  if (!token) return null;

  try {
    const { payload } = await jwtVerify(token, getSecretKey());
    return payload as unknown as SessionPayload;
  } catch {
    return null;
  }
}

/** ดึงข้อมูลผู้ใช้ปัจจุบันสดจากฐานข้อมูล (เผื่อถูกลบ/ปิดใช้งาน/เปลี่ยน role ระหว่าง session) */
export async function getCurrentUser() {
  const session = await readSessionCookie();
  if (!session) return null;

  const user = await prisma.user.findUnique({ where: { id: session.userId } });
  if (!user || !user.isActive) return null;

  return user;
}

export async function requireUser() {
  const user = await getCurrentUser();
  if (!user) {
    throw new AppError("กรุณาเข้าสู่ระบบก่อนใช้งาน", 401);
  }
  return user;
}

export async function requireAdmin() {
  const user = await requireUser();
  if (user.role !== "ADMIN") {
    throw new AppError("เฉพาะแอดมินเท่านั้นที่ใช้งานส่วนนี้ได้", 403);
  }
  return user;
}
