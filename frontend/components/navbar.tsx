'use client';

import { MessageSquare, Moon, Sun } from 'lucide-react'
import React, { useEffect, useState } from 'react'
import Slider from './slider';
import { useRecoilState } from 'recoil';
import { darkModeState } from '@/recoil/blackandwhite';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';
import { buttonVariants } from './ui/button';

export const Navbar = () => {
  const [mounted, setMounted] = useState(false);
  const [darkMode, setDarkMode] = useRecoilState(darkModeState);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Avoid rendering until after hydration
    return null;
  }  
  return (
    <div className={`w-full fixed top-0 z-50 text-slate-100 ${darkMode ? "bg-gray-900 text-white" : "bg-slate-100 text-gray-700"}`}>
      {/* Header */}
      <header className={`w-full  border-b ${darkMode ? "border-gray-700" : "border-gray-200"} px-2 sm:px-6 py-2 sm:py-3`}>
        <div className="mx-auto flex flex-col sm:flex-row items-center sm:justify-between gap-2 sm:gap-0">
          {/* Left Section */}
          <div className="flex items-center gap-2 sm:gap-4 w-full sm:w-auto justify-center sm:justify-start">
            <div className={`rounded-lg ${darkMode ? "bg-gray-900 text-white shadow-gray-500" : "bg-white text-gray-700"} p-1 sm:p-2 shadow-sm`}>
              <MessageSquare className="w-5 h-5 sm:w-6 sm:h-6 text-[#60a5fa]" />
            </div>
            <div>
              <h1 className={`${darkMode? "text-slate-100":"text-gray-700"} text-base sm:text-lg font-semibold tracking-tight`}>
                DeFi AI Assistant
              </h1>
              <div className="text-[10px] sm:text-xs text-slate-400">
                Powered by <span className="text-[#60a5fa] font-medium">Coinbase</span>
              </div>
            </div>
          </div>
          {/* Right Section */}
          <div className="flex items-center gap-2 sm:gap-6 w-full sm:w-auto justify-center sm:justify-end">
            <nav className="flex gap-2 sm:gap-6 relative">
              <Slider darkMode={darkMode} />
            </nav>
            {/* Dark/Light Mode Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`cursor-pointer p-1 sm:p-2 rounded-full border ${darkMode ? "border-gray-600" : "border-gray-400"}`}
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-400" /> : <Moon className="w-4 h-4 sm:w-5 sm:h-5 text-gray-700" />}
            </button>
            
            {/* Connect Wallet Button */}
            <button className={`cursor-pointer text-slate-100 bg-gradient-to-r from-blue-500 to-purple-600 shadow hover:scale-105 px-2 sm:px-4 py-1 sm:py-2 rounded-lg hover:bg-blue-700 text-xs sm:text-base font-medium transition-all duration-200`}>
              Connect Wallet 
            </button>
            <div>
              <SignedOut>
                <SignInButton>
                  <button className={`cursor-pointer text-slate-100 bg-gradient-to-r from-blue-500 to-purple-600 shadow hover:scale-105 px-2 sm:px-4 py-1 sm:py-2 rounded-lg hover:bg-blue-700 text-xs sm:text-base font-medium transition-all duration-200`}>
                    Sign In 
                  </button>
                </SignInButton>
              </SignedOut>
              <SignedIn>
                <UserButton />
              </SignedIn>
            </div>
          </div>
        </div>
      </header>
    </div>
  )
}