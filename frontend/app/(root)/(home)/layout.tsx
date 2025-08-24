// app/(root)/(home)/layout.tsx
import { Navbar } from "@/components/navbar";

export default function HomeLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className=" relative">
      <Navbar />
      <main className="pt-20">
        {children}
      </main>
    </div>
  );
}