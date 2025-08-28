// app/api/chats/route.ts
import { NextResponse } from 'next/server';
import prisma from '@/lib/prisma';

export async function GET() {
  const chats = await prisma.chat.findMany({
    orderBy: { createdAt: 'desc' },
    select: { id: true, title: true, userId: true, archived: true, createdAt: true }
  });
  return NextResponse.json(chats);
}

export async function POST(req: Request) {
  const body = await req.json();
  const chat = await prisma.chat.create({
    data: { title: body.title ?? 'New Chat', userId: body.userId ?? null }
  });
  return NextResponse.json(chat);
}
