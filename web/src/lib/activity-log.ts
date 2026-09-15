import "server-only";

import { prisma } from "@/lib/prisma";

type LogParams = {
  userId: string;
  userRole: string;
  action: "CREATE" | "UPDATE" | "DELETE";
  entityType: string;
  entityId: string;
  description: string;
};

export async function addActivityLog(params: LogParams) {
  await prisma.activityLog.create({
    data: {
      id: crypto.randomUUID(),
      userId: params.userId,
      userRole: params.userRole,
      action: params.action,
      entityType: params.entityType,
      entityId: params.entityId,
      description: params.description,
    },
  });
}
