// สคริปต์ one-off: ตั้ง password เริ่มต้น = PIN เดิม (hash ด้วย bcrypt) ให้ user ที่มีอยู่แล้วแต่ยังไม่มี
// password (เช่น admin/owner ที่ seed มาจากฝั่ง desktop) จะได้ login เว็บได้ทันที แล้วค่อยเปลี่ยนทีหลัง
// ผ่านหน้า "จัดการผู้ใช้งาน" — รันครั้งเดียว: npx tsx scripts/backfill-passwords.ts
import bcrypt from "bcryptjs";

import { prisma } from "../lib/prisma";

async function main() {
  const users = await prisma.user.findMany({
    where: { password: null, pin: { not: null } },
  });

  for (const user of users) {
    const hashed = await bcrypt.hash(user.pin as string, 10);
    await prisma.user.update({
      where: { id: user.id },
      data: { password: hashed },
    });
    console.log(`ตั้ง password เริ่มต้นให้ ${user.username} แล้ว (= PIN เดิม)`);
  }

  console.log(`เสร็จสิ้น: ตั้ง password ให้ ${users.length} บัญชี`);
}

main()
  .catch((err) => {
    console.error(err);
    process.exitCode = 1;
  })
  .finally(() => prisma.$disconnect());
