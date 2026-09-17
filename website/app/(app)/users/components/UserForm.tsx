"use client";

import { useState } from "react";

import { apiFetch, ApiClientError } from "@/lib/api-client";
import { ROLES, ROLE_LABELS } from "@/lib/constants";
import type { UserDTO } from "@/lib/types";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Field, Input, Select, ErrorBanner } from "@/components/ui/Field";

export function UserForm({
  user,
  onClose,
  onSaved,
}: {
  user: UserDTO | null;
  onClose: () => void;
  onSaved: () => void;
}) {
  const isEdit = Boolean(user);
  const [username, setUsername] = useState(user?.username ?? "");
  const [name, setName] = useState(user?.name ?? "");
  const [role, setRole] = useState(user?.role ?? ROLES[0]);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit() {
    setError(null);
    setSaving(true);
    try {
      const payload = { username, name, role, password: password || undefined };
      if (isEdit) {
        await apiFetch(`/api/user/${user!.id}`, { method: "PATCH", body: JSON.stringify(payload) });
      } else {
        await apiFetch("/api/user", { method: "POST", body: JSON.stringify(payload) });
      }
      onSaved();
      onClose();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "บันทึกข้อมูลไม่สำเร็จ");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal title={isEdit ? "แก้ไขผู้ใช้งาน" : "เพิ่มผู้ใช้งานใหม่"} onClose={onClose}>
      <div className="space-y-3">
        {error && <ErrorBanner message={error} />}

        <Field label="ชื่อผู้ใช้ (username)" required>
          <Input value={username} onChange={(e) => setUsername(e.target.value)} disabled={isEdit} />
        </Field>

        <Field label="ชื่อที่แสดง" required>
          <Input value={name} onChange={(e) => setName(e.target.value)} />
        </Field>

        <Field label="บทบาท" required>
          <Select value={role} onChange={(e) => setRole(e.target.value)}>
            {ROLES.map((r) => (
              <option key={r} value={r}>
                {ROLE_LABELS[r]}
              </option>
            ))}
          </Select>
        </Field>

        <Field label={isEdit ? "รหัสผ่านใหม่ (เว้นว่างถ้าไม่เปลี่ยน)" : "รหัสผ่าน"} required={!isEdit}>
          <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </Field>
      </div>

      <div className="mt-5 flex justify-end gap-2 border-t border-slate-200 pt-4">
        <Button variant="secondary" onClick={onClose}>
          ยกเลิก
        </Button>
        <Button onClick={handleSubmit} disabled={saving}>
          {saving ? "กำลังบันทึก..." : "บันทึก"}
        </Button>
      </div>
    </Modal>
  );
}
