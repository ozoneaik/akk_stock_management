"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

import { ROLE_ADMIN } from "@/lib/constants";
import { apiFetch } from "@/lib/api-client";

type NavItem = { href: string; label: string; adminOnly?: boolean };

const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "แดชบอร์ด" },
  { href: "/product", label: "สินค้า" },
  { href: "/stock", label: "ปรับสต็อก" },
  { href: "/activity", label: "บันทึกกิจกรรม", adminOnly: true },
  { href: "/users", label: "จัดการผู้ใช้งาน", adminOnly: true },
];

export function Navbar({ name, role }: { name: string; role: string }) {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const items = NAV_ITEMS.filter((item) => !item.adminOnly || role === ROLE_ADMIN);

  async function handleLogout() {
    setLoggingOut(true);
    try {
      await apiFetch("/api/auth/logout", { method: "POST" });
    } finally {
      router.push("/login");
      router.refresh();
    }
  }

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <span className="text-lg font-bold text-brand-dark">ออฟกิจเกษตร</span>
          <nav className="hidden items-center gap-1 md:flex">
            {items.map((item) => {
              const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-md px-3 py-2 text-sm font-medium ${
                    active ? "bg-brand/10 text-brand-dark" : "text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <span className="text-sm text-slate-600">{name}</span>
          <button
            type="button"
            onClick={handleLogout}
            disabled={loggingOut}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100"
          >
            ออกจากระบบ
          </button>
        </div>

        <button
          type="button"
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="เมนู"
        >
          ☰
        </button>
      </div>

      {open && (
        <nav className="border-t border-slate-200 px-4 py-2 md:hidden">
          {items.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className={`block rounded-md px-3 py-2 text-sm font-medium ${
                  active ? "bg-brand/10 text-brand-dark" : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
          <div className="mt-2 flex items-center justify-between border-t border-slate-200 pt-2">
            <span className="text-sm text-slate-600">{name}</span>
            <button
              type="button"
              onClick={handleLogout}
              disabled={loggingOut}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-600"
            >
              ออกจากระบบ
            </button>
          </div>
        </nav>
      )}
    </header>
  );
}
