'use client';
import { darkModeState } from '@/recoil/blackandwhite';
import { Bot, MessageSquare, Moon, Sun } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useRecoilState } from "recoil";
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';
import WalletButton from './ui/connect-wallet';
import Providers from './Providers';
import Slider from './slider';

// Navbar Component (beautified)
export const Navbar = () => {
  const [mounted, setMounted] = useState(false);
  const [darkMode, setDarkMode] = useRecoilState(darkModeState);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className={`w-full fixed top-0 z-50 ${darkMode ? "bg-gray-900 text-white" : "bg-slate-100 text-gray-700"} shadow-lg backdrop-blur-md transition-all`}>
      <header className={`w-full border-b ${darkMode ? "border-gray-700" : "border-gray-200"} px-2 sm:px-6 py-2 sm:py-3`}>
        <div className="mx-auto flex flex-col sm:flex-row items-center sm:justify-between gap-2 sm:gap-0">
          {/* Left Section */}
          <div className="flex items-center gap-2 sm:gap-4 w-full sm:w-auto justify-center sm:justify-start">
            <div className={`rounded-lg p-1 sm:p-2 shadow-md transition-transform hover:scale-110 ${darkMode ? "bg-gray-800" : "bg-white"}`}>
              <MessageSquare className="w-5 h-5 sm:w-6 sm:h-6 text-blue-400" />
            </div>
            <div>
              <h1 className={`${darkMode ? "text-slate-100" : "text-gray-700"} text-base sm:text-lg font-bold tracking-tight`}>DeFi AI Assistant</h1>
              <div className="text-[10px] sm:text-xs text-slate-400">
                Powered by <span className="text-blue-400 font-medium">Coinbase</span>
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
              className={`cursor-pointer p-2 rounded-full border transition-all hover:scale-110 hover:shadow-[0_0_10px_rgba(250,204,21,0.7)] ${darkMode ? "border-gray-600" : "border-gray-400"}`}
              aria-label="Toggle dark mode"
            >
              {darkMode ? (
                <Sun className="w-5 h-5 text-yellow-400 animate-pulse" />
              ) : (
                <Moon className="w-5 h-5 text-gray-700" />
              )}
            </button>

            {/* Connect Wallet */}
            <Providers>
              <WalletButton />
            </Providers>

            {/* Auth */}
            <div className='max-w-full'>
              <SignedOut>
                <SignInButton>
                  <button
                    className="w-full cursor-pointer text-white bg-gradient-to-r from-blue-500 to-purple-600 shadow-md hover:shadow-[0_0_20px_rgba(96,165,250,0.7)] hover:scale-110 px-4 py-2 rounded-lg text-sm sm:text-base font-medium transition-all duration-200 whitespace-nowrap"
                  >
                    Sign In
                  </button>
                </SignInButton>
              </SignedOut>
              <SignedIn>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </div>
          </div>
        </div>
      </header>
    </div>
  );
};
