"use client";

import { useEffect, useState } from "react";

import { apiFetch, ApiClientError } from "@/lib/api-client";
import type { UserDTO } from "@/lib/types";
import { Spinner } from "@/components/ui/Spinner";
import { Button } from "@/components/ui/Button";
import { ErrorBanner } from "@/components/ui/Field";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { UserForm } from "./components/UserForm";

export function UsersView() {
  const [users, setUsers] = useState<UserDTO[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formUser, setFormUser] = useState<UserDTO | null | "create">(null);
  const [deleteTarget, setDeleteTarget] = useState<UserDTO | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let ignore = false;
    apiFetch<{ users: UserDTO[] }>("/api/user")
      .then((res) => {
        if (ignore) return;
        setUsers(res.users);
        setError(null);
      })
      .catch((err) => {
        if (ignore) return;
        setError(err instanceof ApiClientError ? err.message : "โหลดข้อมูลไม่สำเร็จ");
      });
    return () => {
      ignore = true;
    };
  }, [reloadKey]);

  function refresh() {
    setReloadKey((k) => k + 1);
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await apiFetch(`/api/user/${deleteTarget.id}`, { method: "DELETE" });
      setDeleteTarget(null);
      refresh();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "ลบผู้ใช้งานไม่สำเร็จ");
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-slate-800">จัดการผู้ใช้งาน</h1>
        <Button onClick={() => setFormUser("create")}>+ เพิ่มผู้ใช้งาน</Button>
      </div>

      {error && <ErrorBanner message={error} />}

      {!users ? (
        <Spinner />
      ) : (
        <div className="overflow-x-auto rounded-lg bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr>
                <th className="px-4 py-2">ชื่อผู้ใช้</th>
                <th className="px-4 py-2">ชื่อที่แสดง</th>
                <th className="px-4 py-2">บทบาท</th>
                <th className="px-4 py-2 text-right">จัดการ</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{u.username}</td>
                  <td className="px-4 py-2">{u.name}</td>
                  <td className="px-4 py-2">{u.roleLabel}</td>
                  <td className="px-4 py-2 text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="ghost" onClick={() => setFormUser(u)}>
                        แก้ไข
                      </Button>
                      <Button variant="ghost" onClick={() => setDeleteTarget(u)}>
                        ลบ
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {formUser !== null && (
        <UserForm user={formUser === "create" ? null : formUser} onClose={() => setFormUser(null)} onSaved={refresh} />
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="ลบผู้ใช้งาน"
          message={`ยืนยันการลบผู้ใช้งาน "${deleteTarget.name}" ใช่หรือไม่?`}
          confirmLabel={deleting ? "กำลังลบ..." : "ลบ"}
          danger
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
}
