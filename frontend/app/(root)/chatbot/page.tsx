// app/chatbot/page.tsx
import { redirect } from "next/navigation";
import { v4 as uuidv4 } from "uuid";

export default function ChatbotRootPage() {
  const newId = uuidv4();
  redirect(`/chatbot/${newId}`);
}
