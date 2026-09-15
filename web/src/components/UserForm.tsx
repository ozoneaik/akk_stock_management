"use client";

import { useActionState } from "react";

import type { UserFormState } from "@/app/actions/users";

type UserFormAction = (state: UserFormState, formData: FormData) => Promise<UserFormState>;

export function UserForm({
  action,
  isEdit,
  initial,
  submitLabel,
  disableRole,
}: {
  action: UserFormAction;
  isEdit?: boolean;
  initial?: { username: string; name: string; role: string; avatarUrl: string };
  submitLabel: string;
  disableRole?: boolean;
}) {
  const [state, formAction, isPending] = useActionState(action, null);

  return (
    <form action={formAction} className="space-y-4">
      {state?.error && (
        <p className="rounded-lg bg-red-50 border border-red-200 text-danger text-sm p-3">{state.error}</p>
      )}

      <label className="block">
        <span className="block text-sm font-medium mb-1">ชื่อผู้ใช้ (username) *</span>
        <input
          name="username"
          required
          disabled={isEdit}
          defaultValue={initial?.username}
          className="w-full rounded-xl border border-border bg-card px-3 py-2 disabled:opacity-60"
        />
      </label>

      <label className="block">
        <span className="block text-sm font-medium mb-1">ชื่อที่แสดง *</span>
        <input
          name="name"
          required
          defaultValue={initial?.name}
          className="w-full rounded-xl border border-border bg-card px-3 py-2"
        />
      </label>

      <fieldset className="block">
        <legend className="text-sm font-medium mb-1">บทบาท *</legend>
        <div className="flex gap-4">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="role"
              value="ADMIN"
              defaultChecked={initial?.role === "ADMIN" || !initial}
              disabled={disableRole}
            />
            แอดมิน
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="role"
              value="OWNER"
              defaultChecked={initial?.role === "OWNER"}
              disabled={disableRole}
            />
            เจ้าของร้าน
          </label>
        </div>
        {disableRole && <p className="text-xs text-muted mt-1">ไม่สามารถเปลี่ยนบทบาทของบัญชีตัวเองได้</p>}
      </fieldset>

      <label className="block">
        <span className="block text-sm font-medium mb-1">
          {isEdit ? "PIN ใหม่ (เว้นว่างไว้ถ้าไม่เปลี่ยน)" : "PIN 4 หลัก *"}
        </span>
        <input
          name="pin"
          inputMode="numeric"
          pattern="\d{4}"
          maxLength={4}
          required={!isEdit}
          className="w-full rounded-xl border border-border bg-card px-3 py-2"
        />
      </label>

      <label className="block">
        <span className="block text-sm font-medium mb-1">ลิงก์รูปโปรไฟล์ (URL, ไม่บังคับ)</span>
        <input
          name="avatarUrl"
          type="url"
          defaultValue={initial?.avatarUrl}
          placeholder="https://..."
          className="w-full rounded-xl border border-border bg-card px-3 py-2"
        />
      </label>

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-xl bg-brand text-white font-semibold py-3 disabled:opacity-50"
      >
        {isPending ? "กำลังบันทึก..." : submitLabel}
      </button>
    </form>
  );
}
