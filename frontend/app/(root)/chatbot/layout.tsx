// app/(root)/(chatbot)/layout.tsx
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import Sidebarprovider from "./sidebar-provide"
import { cn } from "@/lib/utils"

export default function ChatbotLayout({ children }: { children: React.ReactNode }) {
  return (
    <Sidebarprovider >
      {children}
    </Sidebarprovider>
  )
}
