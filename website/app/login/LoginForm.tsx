"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { apiFetch, ApiClientError } from "@/lib/api-client";
import { Button } from "@/components/ui/Button";
import { Input, Field, ErrorBanner } from "@/components/ui/Field";

export function LoginForm() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      router.push("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : "เข้าสู่ระบบไม่สำเร็จ");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 rounded-lg bg-white p-6 shadow-md">
      <div className="text-center">
        <h1 className="text-xl font-bold text-brand-dark">ออฟกิจเกษตร</h1>
        <p className="mt-1 text-sm text-slate-500">ระบบจัดการสต็อกสินค้า</p>
      </div>

      {error && <ErrorBanner message={error} />}

      <Field label="ชื่อผู้ใช้" required>
        <Input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          autoFocus
          required
        />
      </Field>

      <Field label="รหัสผ่าน" required>
        <Input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
      </Field>

      <Button type="submit" disabled={loading} className="w-full">
        {loading ? "กำลังเข้าสู่ระบบ..." : "เข้าสู่ระบบ"}
      </Button>
    </form>
  );
}
