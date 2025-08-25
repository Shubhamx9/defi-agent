'use client';

import { motion } from "framer-motion";
import { useRouter, usePathname } from "next/navigation";

const Slider = ({ darkMode }: { darkMode: boolean }) => {
  const router = useRouter();
  const pathname = usePathname();
  const routes = [
    { name: "Dashboard", path: "/" },
    { name: "Chatbot", path: "/chatbot" },
    { name: "Profile", path: "/profile" },
  ];

  return (
    <nav>
      <ul className=" flex justify-center gap-8 py-4 relative">
        {routes.map((route) => {
          const isActive = pathname === route.path;
          return (
            <li key={route.path} className=" relative">
              <button
                onClick={() => router.push(route.path)}
                className={`pb-2 cursor-pointer relative transition-colors duration-200 ${isActive ? "text-blue-600" : darkMode ? "text-gray-300" : "text-gray-700"}`}
              >
                {route.name}
              </button>
              {isActive && (
                <motion.div
                  layoutId="nav-indicator"
                  className="absolute -bottom-[2px] left-0 right-0 h-[5px] bg-blue-600 rounded-full"
                  transition={{ type: "spring", stiffness: 500, damping: 40 }}
                />
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export default Slider;