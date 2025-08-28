'use client';
import { darkModeState } from '@/recoil/blackandwhite';
import { Bot } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useRecoilState } from "recoil";

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [darkMode, setDarkMode] = useRecoilState(darkModeState);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <main className={`min-h-screen ${darkMode ? "bg-gradient-to-br from-slate-900 via-gray-900 to-gray-950 text-white" : "bg-slate-100 text-black"}`}>
      <section className=" py-10 mx-auto">
        <div className=" overflow-hidden whitespace-nowrap py-3">
          <div className="animate-marquee ">
            <div className="flex gap-10 mr-10">
              {[1,2,3,4,5,6].map((i) => (
                <div
                  key={i}
                  className={`transition-transform duration-300 hover:scale-105 hover:shadow-[0_0_20px_rgba(139,92,246,0.6)] ${
                    darkMode ? "bg-gray-800" : "bg-gray-50"
                  } p-6 rounded-2xl shadow-lg max-w-md`}
                >
                  <p className="text-2xl font-semibold">₹1,30,535.80</p>
                  <p className="text-green-500">+₹31,120.76 (23.8%)</p>

                  <div className="mt-6">
                    <p className={`${darkMode ? "text-gray-300" : "text-gray-700"}`}>
                      Prices
                    </p>
                    <div className="mt-2">
                      <div
                        className={`flex justify-between py-2 ${
                          darkMode ? "border-b border-gray-600" : "border-b border-gray-200"
                        }`}
                      >
                        <span>Bitcoin (BTC)</span>
                        <span className="text-green-500">₹70,88,144 ▲10.46%</span>
                      </div>
                      <div className="flex justify-between py-2">
                        <span>Ethereum (ETH)</span>
                        <span className="text-green-500">₹1,34,218 ▲5.8%</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="flex gap-10">
              {[7,8,9,10,11,12].map((i) => (
                <div
                  key={i}
                  className={`transition-transform duration-300 hover:scale-105 hover:shadow-[0_0_20px_rgba(139,92,246,0.6)] ${
                    darkMode ? "bg-gray-800" : "bg-gray-50"
                  } p-6 rounded-2xl shadow-lg max-w-md`}
                >
                  <p className="text-2xl font-semibold">₹1,30,535.80</p>
                  <p className="text-green-500">+₹31,120.76 (23.8%)</p>

                  <div className="mt-6">
                    <p className={`${darkMode ? "text-gray-300" : "text-gray-700"}`}>
                      Prices
                    </p>
                    <div className="mt-2">
                      <div
                        className={`flex justify-between py-2 ${
                          darkMode ? "border-b border-gray-600" : "border-b border-gray-200"
                        }`}
                      >
                        <span>Bitcoin (BTC)</span>
                        <span className="text-green-500">₹70,88,144 ▲10.46%</span>
                      </div>
                      <div className="flex justify-between py-2">
                        <span>Ethereum (ETH)</span>
                        <span className="text-green-500">₹1,34,218 ▲5.8%</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* some dashboard design welcome sugars*/}
        <div className="mx-10 text-center mb-10 mt-10">
          <h1 className="text-4xl font-bold mb-4 animate-pulse bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 bg-clip-text text-transparent">
            Welcome to Your Crypto Dashboard
          </h1>
          <p className={`${darkMode ? "text-gray-300" : "text-gray-700"} text-lg`}>
            Track your portfolio, get insights, and trade securely.
          </p>
        </div>

        {/* Chatbot Promo */}
        <div className='w-full flex justify-center '>
          <div
            className={`max-w-7xl w-full  mx-10 ${
              darkMode ? "bg-gray-800" : "bg-gray-100"
            } p-8 mt-10 rounded-2xl shadow-lg flex flex-col items-center text-center mb-12 transition-all hover:shadow-[0_0_30px_rgba(59,130,246,0.6)]`}
          >
            <div className='flex'>
              <h3 className="text-2xl font-semibold mb-2 bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent animate-text-glow">
                Try Our Smart Chatbot 
              </h3>
              <Bot className="w-8 h-8 ml-2 text-blue-500 animate-pulse" />
            </div>
            <p className={`${darkMode ? "text-gray-300" : "text-gray-700"} mb-4`}>
              Ask questions. Get instant insights. Experience the power of AI for crypto.
            </p>
            <button
              onClick={() => (window.location.href = "/chatbot")}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-3 rounded-xl font-medium shadow-md hover:scale-110 transform transition duration-300 hover:shadow-[0_0_20px_rgba(236,72,153,0.7)]"
            >
              Start Chatting
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
