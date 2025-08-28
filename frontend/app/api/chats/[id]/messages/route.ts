// app/api/chats/[id]/messages/route.ts
import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";

export async function GET(req: Request, { params }: { params: { id: string } }) {
  const messages = await prisma.message.findMany({
    where: { chatId: params.id },
    orderBy: { createdAt: "asc" },
  });
  return NextResponse.json(messages);
}

export async function POST(req: Request, { params }: { params: { id: string } }) {
  const { content, role } = await req.json();
  const message = await prisma.message.create({
    data: { chatId: params.id, content, role },
  });
  return NextResponse.json(message);
}
