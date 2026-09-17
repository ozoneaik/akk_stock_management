import { NextResponse } from "next/server";

import { requireAdmin } from "@/lib/auth";
import { errorResponse } from "@/lib/errors";
import { ACTION_TYPE_LABELS } from "@/lib/constants";
import { getAllLogs } from "@/models/Activity";

export async function GET() {
  try {
    await requireAdmin();
    const logs = await getAllLogs();

    const items = logs.map((entry) => ({
      id: entry.id,
      action: entry.action,
      entityType: entry.entityType,
      entityId: entry.entityId,
      description: entry.description,
      userRole: entry.userRole,
      createdAt: entry.createdAt,
      actionLabel: ACTION_TYPE_LABELS[`${entry.entityType}:${entry.action}`] ?? `${entry.entityType} ${entry.action}`,
      userDisplayName: entry.user?.name ?? "(ผู้ใช้ถูกลบไปแล้ว)",
      username: entry.user?.username ?? null,
    }));

    return NextResponse.json({ logs: items });
  } catch (err) {
    return errorResponse(err);
  }
}
