// app/(root)/(chatbot)/layout.tsx
'use client';
import { cn } from "@/lib/utils";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { useRecoilState, useRecoilValue } from "recoil";
import { darkModeState } from "@/recoil/blackandwhite";
import { useState } from "react";
import { openState } from "@/recoil/open";

export default function Sidebarprovider ({ children }: { children: React.ReactNode }) {
    const darkMode = useRecoilValue(darkModeState);
    const [open, setOpen] = useRecoilState(openState);
  return (
    <div className={cn(
    "bg-black dark:bg-white/5" , darkMode ? "bg-gray-900 text-white" : "bg-white text-black"
  )}>
        <SidebarProvider open={open} onOpenChange={setOpen} className="flex h-screen w-screen">
            <AppSidebar />
            <main className="h-screen flex flex-col w-screen">
            <div className="h-full">
                {children}
            </div>
            </main>
        </SidebarProvider>
    </div>

      
  )
}
