import { NextResponse } from "next/server";

import { requireAdmin } from "@/lib/auth";
import { errorResponse } from "@/lib/errors";
import { ROLE_LABELS } from "@/lib/constants";
import * as UserModel from "@/models/User";
import { addLog } from "@/models/Activity";

export async function GET() {
  try {
    await requireAdmin();
    const users = await UserModel.getAllUsers();
    const items = users.map((u) => ({
      id: u.id,
      username: u.username,
      name: u.name,
      role: u.role,
      roleLabel: ROLE_LABELS[u.role] ?? u.role,
      isActive: u.isActive,
      createdAt: u.createdAt,
    }));
    return NextResponse.json({ users: items });
  } catch (err) {
    return errorResponse(err);
  }
}

export async function POST(request: Request) {
  try {
    const currentUser = await requireAdmin();
    const data = await request.json();
    UserModel.validateUserInput(data, false);

    const id = await UserModel.createUser({
      username: data.username,
      name: data.name,
      role: data.role,
      password: data.password,
    });

    await addLog({
      userId: currentUser.id,
      userRole: currentUser.role,
      action: "CREATE",
      entityType: "User",
      entityId: id,
      description: `${currentUser.name} เพิ่มผู้ใช้งานใหม่ "${data.name}" (${data.username})`,
    });

    return NextResponse.json({ id }, { status: 201 });
  } catch (err) {
    return errorResponse(err);
  }
}
