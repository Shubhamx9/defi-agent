// app/api/chats/history/route.ts
import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const chatIdParam = url.searchParams.get("chatId");
    if (!chatIdParam) return NextResponse.json({ messages: [] });

    const chatId = Number(chatIdParam);
    if (Number.isNaN(chatId)) return NextResponse.json({ messages: [] });

    const msgs = await prisma.message.findMany({
      where: { chatId },
      orderBy: { createdAt: "asc" },
    });

    // Convert messages to shape used in ChatbotPage: { role, text }
    const messages = msgs.map((m) => ({ role: m.role as "user" | "bot", text: m.content }));

    return NextResponse.json({ messages });
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: "Failed to load history" }, { status: 500 });
  }
}
