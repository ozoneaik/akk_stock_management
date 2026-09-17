import type { Metadata } from "next";
import { Noto_Sans_Thai } from "next/font/google";
import type { ReactNode } from "react";
import "./globals.css";

const notoSansThai = Noto_Sans_Thai({
  variable: "--font-sans",
  subsets: ["thai", "latin"],
});

export const metadata: Metadata = {
  title: "ระบบจัดการสต็อกสินค้า - ออฟกิจเกษตร",
  description: "ระบบจัดการสต็อกสินค้าสำหรับร้านขายปุ๋ย ยากำจัดวัชพืช/ศัตรูพืช และอุปกรณ์การเกษตร",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="th" className={`${notoSansThai.variable} h-full`}>
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900 antialiased">{children}</body>
    </html>
  );
}
