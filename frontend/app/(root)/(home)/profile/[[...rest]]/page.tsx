"use client";

import { darkModeState } from "@/recoil/blackandwhite";
import { UserProfile } from "@clerk/nextjs";
import { useRecoilValue } from "recoil";

export default function ProfilePage() {
  const darkMode = useRecoilValue(darkModeState);

  return (
    <div
      className={`p-5 flex w-full justify-center min-h-screen ${
        darkMode ? "bg-gray-900" : "bg-slate-100"
      }`}
    >
      <UserProfile
      appearance={{
        variables: {
          colorPrimary: darkMode ? "#8b5cf6" : "#6d28d9",
          colorBackground: darkMode ? "#111827" : "#ffffff",
          colorInputBackground: darkMode ? "#1f2937" : "#f9fafb",
          colorText: darkMode ? "#f9fafb" : "#111827",
          colorTextSecondary: darkMode ? "#9ca3af" : "#6b7280",
          colorBorder: darkMode ? "" : "#374151",
          colorShadow: darkMode ? "#000000" : "#d1d5db",
          borderRadius: "0.75rem",
        },
        elements: {
          card: "w-full max-w-4xl shadow-lg rounded-2xl",
          headerTitle: darkMode
            ? "text-3xl font-bold text-purple-400"
            : "text-3xl font-bold text-purple-700",
          formButtonPrimary: darkMode
            ? "bg-purple-500 hover:bg-purple-600 text-white rounded-lg px-4 py-2"
            : "bg-purple-600 hover:bg-purple-700 text-white rounded-lg px-4 py-2",
        },
      }}
    />

    </div>
  );
}

