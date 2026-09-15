"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useTransition } from "react";
import Image from "next/image";

import { loginWithPin } from "@/app/actions/auth";

type LoginUser = {
  username: string;
  name: string;
  role: string;
  avatarUrl: string | null;
};

const ROLE_LABELS: Record<string, string> = { ADMIN: "แอดมิน", OWNER: "เจ้าของร้าน" };

export function LoginScreen({ users }: { users: LoginUser[] }) {
  const [selected, setSelected] = useState<LoginUser | null>(null);
  const [pin, setPin] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const searchParams = useSearchParams();

  function selectUser(user: LoginUser) {
    setSelected(user);
    setPin("");
    setError(null);
  }

  function pressDigit(digit: string) {
    if (isPending || pin.length >= 4) return;
    const next = pin + digit;
    setPin(next);
    setError(null);
    if (next.length === 4 && selected) {
      submit(selected.username, next);
    }
  }

  function submit(username: string, pinValue: string) {
    startTransition(async () => {
      const result = await loginWithPin(username, pinValue);
      if (!result.ok) {
        setError(result.error);
        setPin("");
        return;
      }
      const next = searchParams.get("next") || "/";
      router.push(next);
      router.refresh();
    });
  }

  if (!selected) {
    return (
      <div className="grid grid-cols-2 gap-4">
        {users.map((user) => (
          <button
            key={user.username}
            onClick={() => selectUser(user)}
            className="flex flex-col items-center gap-2 rounded-2xl bg-card border border-border p-4 active:scale-95 transition"
          >
            <div className="w-16 h-16 rounded-full overflow-hidden bg-brand-light relative">
              {user.avatarUrl ? (
                <Image src={user.avatarUrl} alt={user.name} fill sizes="64px" className="object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-brand-dark font-bold text-xl">
                  {user.name.charAt(0)}
                </div>
              )}
            </div>
            <span className="font-semibold text-sm text-center">{user.name}</span>
            <span className="text-xs text-muted">{ROLE_LABELS[user.role] ?? user.role}</span>
          </button>
        ))}
        {users.length === 0 && (
          <p className="col-span-2 text-center text-muted text-sm py-6">
            ยังไม่มีผู้ใช้งานในระบบ
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center">
      <button onClick={() => selectUser(null as unknown as LoginUser)} className="self-start text-sm text-muted mb-4">
        ← เปลี่ยนผู้ใช้งาน
      </button>

      <div className="w-16 h-16 rounded-full overflow-hidden bg-brand-light relative mb-2">
        {selected.avatarUrl ? (
          <Image src={selected.avatarUrl} alt={selected.name} fill sizes="64px" className="object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-brand-dark font-bold text-xl">
            {selected.name.charAt(0)}
          </div>
        )}
      </div>
      <p className="font-semibold mb-1">{selected.name}</p>
      <p className="text-sm text-muted mb-4">กรอกรหัส PIN 4 หลัก</p>

      <div className="flex gap-3 mb-2" aria-live="polite">
        {[0, 1, 2, 3].map((i) => (
          <span
            key={i}
            className={`w-4 h-4 rounded-full border-2 border-brand ${
              i < pin.length ? "bg-brand" : "bg-transparent"
            }`}
          />
        ))}
      </div>

      <p className="text-danger text-sm h-5 mb-2">{error ?? (isPending ? "กำลังตรวจสอบ..." : "")}</p>

      <div className="grid grid-cols-3 gap-3 w-full max-w-[280px]">
        {["1", "2", "3", "4", "5", "6", "7", "8", "9"].map((digit) => (
          <button
            key={digit}
            type="button"
            disabled={isPending}
            onClick={() => pressDigit(digit)}
            className="aspect-square rounded-full bg-card border border-border text-xl font-semibold active:bg-brand-light disabled:opacity-50"
          >
            {digit}
          </button>
        ))}
        <button
          type="button"
          onClick={() => {
            setPin("");
            setError(null);
          }}
          className="aspect-square rounded-full text-sm text-muted"
        >
          ล้าง
        </button>
        <button
          type="button"
          disabled={isPending}
          onClick={() => pressDigit("0")}
          className="aspect-square rounded-full bg-card border border-border text-xl font-semibold active:bg-brand-light disabled:opacity-50"
        >
          0
        </button>
        <button
          type="button"
          onClick={() => setPin((p) => p.slice(0, -1))}
          className="aspect-square rounded-full text-sm text-muted"
        >
          ลบ
        </button>
      </div>
    </div>
  );
}
