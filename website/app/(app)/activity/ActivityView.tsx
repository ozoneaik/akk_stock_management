"use client";

import { useEffect, useState } from "react";

import { apiFetch, ApiClientError } from "@/lib/api-client";
import type { ActivityLogDTO } from "@/lib/types";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorBanner } from "@/components/ui/Field";

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString("th-TH", { dateStyle: "medium", timeStyle: "short" });
}

export function ActivityView() {
  const [logs, setLogs] = useState<ActivityLogDTO[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<{ logs: ActivityLogDTO[] }>("/api/activity")
      .then((res) => setLogs(res.logs))
      .catch((err) => setError(err instanceof ApiClientError ? err.message : "โหลดข้อมูลไม่สำเร็จ"));
  }, []);

  if (error) return <ErrorBanner message={error} />;
  if (!logs) return <Spinner />;

  return (
    <div className="overflow-x-auto rounded-lg bg-white shadow-sm">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-left text-slate-500">
          <tr>
            <th className="px-4 py-2">เวลา</th>
            <th className="px-4 py-2">ผู้ใช้</th>
            <th className="px-4 py-2">การกระทำ</th>
            <th className="px-4 py-2">รายละเอียด</th>
          </tr>
        </thead>
        <tbody>
          {logs.length === 0 ? (
            <tr>
              <td colSpan={4} className="px-4 py-6 text-center text-slate-500">
                ยังไม่มีประวัติการทำงาน
              </td>
            </tr>
          ) : (
            logs.map((log) => (
              <tr key={log.id} className="border-t border-slate-100">
                <td className="whitespace-nowrap px-4 py-2 text-slate-500">{formatDateTime(log.createdAt)}</td>
                <td className="whitespace-nowrap px-4 py-2">{log.userDisplayName}</td>
                <td className="whitespace-nowrap px-4 py-2">{log.actionLabel}</td>
                <td className="px-4 py-2">{log.description}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
