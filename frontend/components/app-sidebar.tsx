'use client';
import { Calendar, Home, Inbox, PanelLeftClose, PanelRightClose, Search, Settings, User, User2 } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { cn } from "@/lib/utils"
import { useRecoilValue } from "recoil";
import { darkModeState } from "@/recoil/blackandwhite";
import React from "react";
import { openState } from "@/recoil/open";
import { UserButton, useUser } from "@clerk/nextjs";

// Menu items.
const items = [
  {
    title: "Home",
    url: "/",
    icon: Home,
  },
  {
    title: "Profile",
    url: "/profile",
    icon: User2,
  },
]

export function AppSidebar() {
    const user = useUser();
    const darkMode = useRecoilValue(darkModeState);
    const open = useRecoilValue(openState);
  return (
  <div>
    <Sidebar collapsible="icon">
      {/* Sidebar top / trigger */}
      <div
        className={`px-[11px] pt-5 ${
          darkMode ? "bg-gray-900 text-white" : "bg-slate-50 text-black"
        }`}
      >
        <SidebarTrigger
          className={`transition-transform duration-300 ease-in-out 
            ${open ? "translate-x-[200px]" : "translate-x-0"}`}
        />
      </div>

      {/* Sidebar content */}
      <SidebarContent
        className={cn(
          "flex flex-col h-full justify-between", // make content a column with full height
          darkMode
            ? "bg-gray-900 text-white border-gray-700"
            : "bg-slate-50 text-gray-700 border-gray-200"
        )}
      >
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    className="gap-3 [&>svg]:h-5 [&>svg]:w-5"
                  >
                    <a href={item.url}>
                      <item.icon />
                      <span className="text-lg">{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Push UserButton to the bottom */}
        <div className="mt-auto flex p-4 ">
          <UserButton />
          <div className={`pl-4 text-xl text-center ${darkMode ? "text-white" : "text-black"} ${!open && "hidden"}`}>
            {user.user?.firstName} {user.user?.lastName}
          </div>
        </div>
      </SidebarContent>
    </Sidebar>
  </div>
);

}