import { redirect } from "next/navigation";

import { prisma } from "@/lib/prisma";
import { getCurrentUser } from "@/lib/auth";

const ACTION_LABELS: Record<string, Record<string, string>> = {
  Product: { CREATE: "เพิ่มสินค้า", UPDATE: "แก้ไขสินค้า", DELETE: "ลบสินค้า" },
  Stock: { UPDATE: "ปรับสต็อก" },
  User: { CREATE: "เพิ่มผู้ใช้งาน", UPDATE: "แก้ไข/เข้าสู่ระบบ", DELETE: "ลบผู้ใช้งาน" },
};

function labelFor(entityType: string, action: string) {
  return ACTION_LABELS[entityType]?.[action] ?? `${entityType} ${action}`;
}

export default async function ActivityLogPage() {
  const user = await getCurrentUser();
  if (user?.role !== "ADMIN") {
    redirect("/");
  }

  const logs = await prisma.activityLog.findMany({
    orderBy: { createdAt: "desc" },
    take: 200,
  });

  return (
    <div className="px-4 py-5 space-y-3">
      <h1 className="text-xl font-bold">บันทึกกิจกรรม</h1>
      <div className="space-y-2">
        {logs.map((log) => (
          <div key={log.id} className="rounded-xl border border-border bg-card p-3">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs font-semibold text-brand-dark">
                {labelFor(log.entityType, log.action)}
              </span>
              <span className="text-xs text-muted">
                {log.createdAt.toLocaleString("th-TH", { dateStyle: "short", timeStyle: "short" })}
              </span>
            </div>
            <p className="text-sm">{log.description}</p>
          </div>
        ))}
        {logs.length === 0 && <p className="text-center text-muted text-sm py-8">ยังไม่มีบันทึกกิจกรรม</p>}
      </div>
    </div>
  );
}
