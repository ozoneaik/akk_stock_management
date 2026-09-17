import { NextResponse } from "next/server";

import { requireAdmin } from "@/lib/auth";
import { AppError, errorResponse } from "@/lib/errors";
import { ROLE_ADMIN } from "@/lib/constants";
import * as UserModel from "@/models/User";
import { addLog } from "@/models/Activity";

type Params = { params: Promise<{ id: string }> };

export async function PATCH(request: Request, { params }: Params) {
  try {
    const currentUser = await requireAdmin();
    const { id } = await params;
    const data = await request.json();
    UserModel.validateUserInput(data, true);

    const target = await UserModel.getUserById(id);
    if (!target) throw new AppError("ไม่พบผู้ใช้งานนี้ในระบบ", 404);

    if (target.role === ROLE_ADMIN && data.role !== ROLE_ADMIN) {
      if ((await UserModel.countActiveAdmins()) <= 1) {
        throw new AppError("ต้องมีผู้ใช้บทบาทแอดมินอย่างน้อย 1 คนในระบบเสมอ");
      }
    }

    await UserModel.updateUser(id, { name: data.name, role: data.role });
    if (data.password?.trim()) {
      await UserModel.updatePassword(id, data.password);
    }

    await addLog({
      userId: currentUser.id,
      userRole: currentUser.role,
      action: "UPDATE",
      entityType: "User",
      entityId: id,
      description: `${currentUser.name} แก้ไขข้อมูลผู้ใช้งาน "${data.name}" (${target.username})`,
    });

    return NextResponse.json({ ok: true });
  } catch (err) {
    return errorResponse(err);
  }
}

export async function DELETE(_request: Request, { params }: Params) {
  try {
    const currentUser = await requireAdmin();
    const { id } = await params;

    if (id === currentUser.id) {
      throw new AppError("ไม่สามารถลบบัญชีผู้ใช้ที่กำลังใช้งานอยู่ได้");
    }

    const target = await UserModel.getUserById(id);
    if (!target) throw new AppError("ไม่พบผู้ใช้งานนี้ในระบบ", 404);

    if (target.role === ROLE_ADMIN && (await UserModel.countActiveAdmins()) <= 1) {
      throw new AppError("ต้องมีผู้ใช้บทบาทแอดมินอย่างน้อย 1 คนในระบบเสมอ");
    }

    await UserModel.deactivateUser(id);

    await addLog({
      userId: currentUser.id,
      userRole: currentUser.role,
      action: "DELETE",
      entityType: "User",
      entityId: id,
      description: `${currentUser.name} ลบผู้ใช้งาน "${target.name}" (${target.username})`,
    });

    return NextResponse.json({ ok: true });
  } catch (err) {
    return errorResponse(err);
  }
}
