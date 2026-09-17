import { NextResponse } from "next/server";

import { requireUser } from "@/lib/auth";
import { errorResponse, AppError } from "@/lib/errors";
import { getAllCategories, getOrCreateCategory } from "@/models/Category";

export async function GET() {
  try {
    await requireUser();
    const categories = await getAllCategories();
    return NextResponse.json({ categories });
  } catch (err) {
    return errorResponse(err);
  }
}

export async function POST(request: Request) {
  try {
    await requireUser();
    const body = await request.json().catch(() => ({}));
    const name = (body?.name ?? "").toString().trim();
    if (!name) throw new AppError("กรุณากรอกชื่อหมวดหมู่");

    const id = await getOrCreateCategory(name);
    return NextResponse.json({ id }, { status: 201 });
  } catch (err) {
    return errorResponse(err);
  }
}
