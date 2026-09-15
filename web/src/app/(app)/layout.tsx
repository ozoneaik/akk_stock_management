import { redirect } from "next/navigation";

import { getCurrentUser } from "@/lib/auth";
import { BottomNav } from "@/components/BottomNav";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser();
  if (!user) {
    redirect("/login");
  }

  return (
    <div className="flex-1 flex flex-col min-h-screen">
      <main className="flex-1 pb-20 w-full max-w-2xl mx-auto">{children}</main>
      <BottomNav isAdmin={user.role === "ADMIN"} />
    </div>
  );
}
