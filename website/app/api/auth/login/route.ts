import { NextResponse } from "next/server";

import { createSession } from "@/lib/auth";
import { errorResponse } from "@/lib/errors";
import { authenticate } from "@/models/User";
import { addLog } from "@/models/Activity";

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const username = (body?.username ?? "").toString().trim();
    const password = (body?.password ?? "").toString();

    if (!username || !password) {
      return NextResponse.json({ error: "กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ครบถ้วน" }, { status: 400 });
    }

    const user = await authenticate(username, password);
    if (!user) {
      return NextResponse.json({ error: "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง" }, { status: 401 });
    }

    await createSession({ userId: user.id, username: user.username, name: user.name, role: user.role });

    await addLog({
      userId: user.id,
      userRole: user.role,
      action: "UPDATE",
      entityType: "User",
      entityId: user.id,
      description: `${user.name} เข้าสู่ระบบสำเร็จ`,
    });

    return NextResponse.json({
      user: { id: user.id, username: user.username, name: user.name, role: user.role },
    });
  } catch (err) {
    return errorResponse(err);
  }
}
