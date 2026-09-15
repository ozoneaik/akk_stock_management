"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/", label: "ภาพรวม", icon: "🏠" },
  { href: "/products", label: "สินค้า", icon: "📦" },
  { href: "/stock", label: "ปรับสต็อก", icon: "🔄" },
  { href: "/more", label: "เมนู", icon: "☰" },
];

export function BottomNav({ isAdmin }: { isAdmin: boolean }) {
  const pathname = usePathname();

  return (
    <nav
      className="fixed bottom-0 inset-x-0 bg-card border-t border-border"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <div className="flex justify-around max-w-2xl mx-auto">
        {TABS.map((tab) => {
          const active = tab.href === "/" ? pathname === "/" : pathname.startsWith(tab.href);
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={`flex flex-col items-center gap-0.5 py-2 px-3 flex-1 text-xs ${
                active ? "text-brand font-semibold" : "text-muted"
              }`}
            >
              <span className="text-xl leading-none">{tab.icon}</span>
              {tab.label}
              {tab.href === "/more" && isAdmin && (
                <span className="sr-only">(มีเมนูแอดมิน)</span>
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
