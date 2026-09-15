import { redirect } from "next/navigation";

import { getCurrentUser } from "@/lib/auth";
import { createUser } from "@/app/actions/users";
import { UserForm } from "@/components/UserForm";

export default async function NewUserPage() {
  const currentUser = await getCurrentUser();
  if (currentUser?.role !== "ADMIN") redirect("/");

  return (
    <div className="px-4 py-5">
      <h1 className="text-xl font-bold mb-4">เพิ่มผู้ใช้งานใหม่</h1>
      <UserForm action={createUser} submitLabel="บันทึกผู้ใช้งานใหม่" />
    </div>
  );
}
