import { Suspense } from "react";

import { prisma } from "@/lib/prisma";
import { LoginScreen } from "./LoginScreen";

export default async function LoginPage() {
  const users = await prisma.user.findMany({
    where: { isActive: true },
    orderBy: { role: "asc" },
    select: { username: true, name: true, role: true, avatarUrl: true },
  });

  return (
    <main className="flex-1 flex flex-col items-center justify-center px-5 py-10 bg-linear-to-b from-brand-light/40 to-background">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-brand-dark">ออฟกิจเกษตร</h1>
          <p className="text-muted text-sm mt-1">ระบบจัดการสต็อกสินค้า</p>
        </div>
        <Suspense fallback={null}>
          <LoginScreen users={users} />
        </Suspense>
      </div>
    </main>
  );
}
