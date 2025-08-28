"use client";
import { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type Msg = {
  id: string;
  content: string;
  role: "user" | "assistant";
  createdAt?: string;
};

export default function ChatWindow({ chatId }: { chatId: string }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // 🔹 Load history from DB on first render
  useEffect(() => {
    if (!chatId) return;

    // save chatId in localStorage
    localStorage.setItem("activeChatId", chatId);

    (async () => {
      try {
        const res = await fetch(`/api/chats/${chatId}/messages`);
        if (!res.ok) throw new Error("Failed to load messages");
        const data = await res.json();
        setMessages(data);
      } catch (err) {
        console.error("ChatWindow load error:", err);
      }
    })();
  }, [chatId]);

  // 🔹 Restore chat after refresh
  useEffect(() => {
    const savedId = localStorage.getItem("activeChatId");
    if (savedId && !chatId) {
      window.location.href = `/chatbot/${savedId}`;
    }
  }, [chatId]);

  async function handleSend() {
    if (!input.trim() || !chatId) return;
    setLoading(true);

    const userMsg: Msg = {
      id: crypto.randomUUID(),
      content: input,
      role: "user",
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      // Save user message in DB
      await fetch(`/api/chats/${chatId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userMsg),
      });

      // Call assistant API
      const res = await fetch(`/api/assistant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chatId, message: input }),
      });

      if (!res.ok) throw new Error("Assistant request failed");
      const data = await res.json();

      const assistantMsg: Msg = {
        id: crypto.randomUUID(),
        content: data.reply,
        role: "assistant",
      };

      // update UI
      setMessages((prev) => [...prev, assistantMsg]);

      // save assistant msg in DB
      await fetch(`/api/chats/${chatId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(assistantMsg),
      });
    } catch (err) {
      console.error("Send error:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m) => (
          <div key={m.id} className={m.role === "user" ? "text-right" : "text-left"}>
            <span
              className={`inline-block px-3 py-2 rounded-lg whitespace-pre-wrap ${
                m.role === "user" ? "bg-blue-500 text-white" : "bg-gray-200"
              }`}
            >
              {m.content}
            </span>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="p-3 border-t flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <Button onClick={handleSend} disabled={loading || !input.trim()}>
          {loading ? "..." : "Send"}
        </Button>
      </div>
    </div>
  );
}
