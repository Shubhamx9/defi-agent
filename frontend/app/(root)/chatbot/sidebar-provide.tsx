// app/sidebar-provider.tsx (replace your file)
'use client';

import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { useRecoilState, useRecoilValue } from "recoil";
import { darkModeState } from "@/recoil/blackandwhite";
import { openState } from "@/recoil/open";
import { useState, useEffect } from "react";
import ChatWindow from "@/components/ChatWindow";
import { useParams } from "next/navigation";

export default function Sidebarprovider({ children }: { children: React.ReactNode }) {
  const darkMode = useRecoilValue(darkModeState);
  const [open, setOpen] = useRecoilState(openState);

  // use string ids (UUIDs) — matches DB
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const params = useParams();
  const urlId = params?.id ? String(params.id) : null;

  // if route contains chat id, prefer showing the main chat page (children)
  useEffect(() => {
    if (urlId) {
      // ensure any selected chat in sidebar is cleared so children can render
      setSelectedChatId(null);
      return;
    }
  }, [urlId]);

  return (
    <SidebarProvider open={open} onOpenChange={setOpen} className="flex h-screen w-screen">
      {/* Sidebar */}
      <AppSidebar onSelectChat={setSelectedChatId} />

      {/* Main content */}
      <main className="h-screen flex flex-col w-screen">
        <div className="h-full overflow-auto">
          {selectedChatId && !urlId ? (
            // read-only chat window inside sidebar area
            <ChatWindow chatId={selectedChatId} />
          ) : (
            children ?? (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                Select a chat to view history
              </div>
            )
          )}
        </div>
      </main>
    </SidebarProvider>
  );
}
