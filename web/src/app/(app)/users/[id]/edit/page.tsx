import { notFound, redirect } from "next/navigation";

import { prisma } from "@/lib/prisma";
import { getCurrentUser } from "@/lib/auth";
import { updateUser } from "@/app/actions/users";
import { UserForm } from "@/components/UserForm";

export default async function EditUserPage({ params }: { params: Promise<{ id: string }> }) {
  const currentUser = await getCurrentUser();
  if (currentUser?.role !== "ADMIN") redirect("/");

  const { id } = await params;
  const user = await prisma.user.findUnique({ where: { id } });
  if (!user) notFound();

  const boundAction = updateUser.bind(null, user.id);

  return (
    <div className="px-4 py-5">
      <h1 className="text-xl font-bold mb-4">แก้ไขผู้ใช้งาน</h1>
      <UserForm
        action={boundAction}
        isEdit
        disableRole={user.id === currentUser.id}
        submitLabel="บันทึกการแก้ไข"
        initial={{
          username: user.username,
          name: user.name,
          role: user.role,
          avatarUrl: user.avatarUrl ?? "",
        }}
      />
    </div>
  );
}
