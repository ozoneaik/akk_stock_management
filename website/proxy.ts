import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { jwtVerify } from "jose";

// กันการเข้าหน้า/API โดยไม่ login เป็นชั้นความสะดวกแรก
// ทุก API route ที่แก้ข้อมูลจริงต้องเช็คสิทธิ์ของตัวเองซ้ำอีกชั้นเสมอ (ดู lib/auth.ts requireUser/requireAdmin)
const PUBLIC_PATHS = ["/login", "/api/auth/login"];
const ADMIN_ONLY_PATHS = ["/users", "/activity", "/api/user", "/api/activity"];

async function readSessionRole(request: NextRequest) {
  const token = request.cookies.get("session")?.value;
  const secret = process.env.JWT_SECRET;
  if (!token || !secret) return null;

  try {
    const { payload } = await jwtVerify(token, new TextEncoder().encode(secret));
    return payload as { role?: string };
  } catch {
    return null;
  }
}

function matchesPath(pathname: string, paths: string[]) {
  return paths.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isPublic = matchesPath(pathname, PUBLIC_PATHS);
  const session = await readSessionRole(request);
  const isApi = pathname.startsWith("/api/");

  if (!isPublic && !session) {
    if (isApi) {
      return NextResponse.json({ error: "กรุณาเข้าสู่ระบบก่อนใช้งาน" }, { status: 401 });
    }
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (pathname === "/login" && session) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  if (session && matchesPath(pathname, ADMIN_ONLY_PATHS) && session.role !== "ADMIN") {
    if (isApi) {
      return NextResponse.json({ error: "เฉพาะแอดมินเท่านั้นที่ใช้งานส่วนนี้ได้" }, { status: 403 });
    }
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.svg$).*)"],
};
