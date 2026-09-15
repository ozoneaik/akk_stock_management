import "dotenv/config";
import { PrismaMariaDb } from "@prisma/adapter-mariadb";
import { PrismaClient } from "../src/generated/prisma/client";

const dbUrl = new URL(process.env.DATABASE_URL ?? "");
const adapter = new PrismaMariaDb({
  host: dbUrl.hostname,
  port: Number(dbUrl.port) || 3306,
  user: decodeURIComponent(dbUrl.username),
  password: decodeURIComponent(dbUrl.password),
  database: dbUrl.pathname.replace(/^\//, ""),
  ssl: {},
});

const prisma = new PrismaClient({ adapter });

async function main() {
  const existingUsers = await prisma.user.count();
  if (existingUsers > 0) {
    console.log("มีข้อมูลผู้ใช้อยู่แล้ว ข้ามการ seed (เคลียร์ตารางก่อนถ้าต้องการ seed ใหม่)");
    return;
  }

  const now = new Date();

  const admin = await prisma.user.create({
    data: {
      id: crypto.randomUUID(),
      username: "admin",
      name: "แอดมิน",
      role: "ADMIN",
      pin: "9999",
      updatedAt: now,
    },
  });

  const owner = await prisma.user.create({
    data: {
      id: crypto.randomUUID(),
      username: "owner",
      name: "เจ้าของร้าน",
      role: "OWNER",
      pin: "1234",
      updatedAt: now,
    },
  });

  const categoryDefs = [
    { name: "ยาดูดซึม (กำจัดวัชพืช)", color: "#15803d", sortOrder: 1 },
    { name: "ยาเผาไหม้ (กำจัดวัชพืช)", color: "#b91c1c", sortOrder: 2 },
    { name: "ยาฆ่าแมลงและหนอน", color: "#d97706", sortOrder: 3 },
    { name: "ปุ๋ยและธาตุอาหาร", color: "#0284c7", sortOrder: 4 },
    { name: "อุปกรณ์การเกษตร", color: "#7c3aed", sortOrder: 5 },
  ];

  const categories = new Map<string, string>();
  for (const c of categoryDefs) {
    const category = await prisma.category.create({
      data: { id: crypto.randomUUID(), name: c.name, color: c.color, sortOrder: c.sortOrder, updatedAt: now },
    });
    categories.set(c.name, category.id);
  }

  const productDefs = [
    {
      name: "ไกลโฟเสต 48% (ตรามังกรคู่)",
      category: "ยาดูดซึม (กำจัดวัชพืช)",
      baseUnit: "ขวด",
      packUnit: "ลัง",
      unitsPerPack: 12,
      currentStock: 96,
      minStockAlert: 24,
      price: 230,
    },
    {
      name: "กลูโฟซิเนต-แอมโมเนียม 15%",
      category: "ยาเผาไหม้ (กำจัดวัชพืช)",
      baseUnit: "ขวด",
      packUnit: "ลัง",
      unitsPerPack: 12,
      currentStock: 18,
      minStockAlert: 24,
      price: 280,
    },
    {
      name: "อะบาเมกติน 1.8% EC",
      category: "ยาฆ่าแมลงและหนอน",
      baseUnit: "ขวด",
      packUnit: "ลัง",
      unitsPerPack: 12,
      currentStock: 6,
      minStockAlert: 24,
      price: 210,
    },
    {
      name: "ปุ๋ยเกล็ด 16-16-16",
      category: "ปุ๋ยและธาตุอาหาร",
      baseUnit: "ถุง",
      packUnit: "กระสอบ",
      unitsPerPack: 10,
      currentStock: 40,
      minStockAlert: 10,
      price: 65,
    },
    {
      name: "ถังพ่นยาสะพายหลัง 16 ลิตร",
      category: "อุปกรณ์การเกษตร",
      baseUnit: "ชิ้น",
      packUnit: null,
      unitsPerPack: 1,
      currentStock: 9,
      minStockAlert: 5,
      price: 890,
    },
  ];

  for (const p of productDefs) {
    const product = await prisma.product.create({
      data: {
        id: crypto.randomUUID(),
        name: p.name,
        categoryId: categories.get(p.category)!,
        baseUnit: p.baseUnit,
        packUnit: p.packUnit,
        unitsPerPack: p.unitsPerPack,
        currentStock: p.currentStock,
        minStockAlert: p.minStockAlert,
        createdById: admin.id,
        updatedById: admin.id,
        updatedAt: now,
      },
    });

    await prisma.productPrice.create({
      data: { id: crypto.randomUUID(), productId: product.id, channel: "STORE", price: p.price, updatedAt: now },
    });

    await prisma.stockMovement.create({
      data: {
        id: crypto.randomUUID(),
        productId: product.id,
        type: "IN",
        quantity: p.currentStock,
        inputUnit: p.baseUnit,
        inputQuantity: p.currentStock,
        balanceBefore: 0,
        balanceAfter: p.currentStock,
        note: "ยอดยกมารับเข้าสต็อกรอบเปิดร้าน",
        createdById: admin.id,
      },
    });
  }

  await prisma.activityLog.create({
    data: {
      id: crypto.randomUUID(),
      action: "CREATE",
      entityType: "Product",
      entityId: "SYSTEM-INIT",
      description: `${admin.name} นำเข้ารายการสินค้าเริ่มต้นระบบ ${productDefs.length} รายการ`,
      userId: admin.id,
      userRole: admin.role,
    },
  });

  console.log("Seed ข้อมูลตัวอย่างเรียบร้อยแล้ว");
  console.log(`  - ผู้ใช้: admin/9999 (แอดมิน), owner/1234 (เจ้าของร้าน) — ${owner.username} ก็สร้างแล้วเช่นกัน`);
  console.log(`  - หมวดหมู่: ${categoryDefs.length} รายการ`);
  console.log(`  - สินค้า: ${productDefs.length} รายการ`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
