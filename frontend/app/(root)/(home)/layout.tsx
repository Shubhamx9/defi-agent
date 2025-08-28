// app/(root)/(home)/layout.tsx
import { Navbar } from "@/components/navbar";

export default function HomeLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative">
      <Navbar />
      <main className="pt-20 min-h-screen max-w-screen overflow-x-hidden">
        {children}
      </main>
    </div>
  );
}