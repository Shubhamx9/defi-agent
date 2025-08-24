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
    // Avoid rendering until after hydration
    return null;
  }

  return (
    <main className={`${darkMode ? "bg-gray-900 text-white" : "bg-slate-100 text-black"}`}>
      <section className="p-10 max-w-7xl mx-auto">
        <div className=" overflow-hidden whitespace-nowrap py-3">
          <div className="animate-marquee ">
            <div className="flex gap-10 mr-10">
              <div
                className={`${
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
              <div
                className={`${
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
              <div
                className={`${
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
              <div
                className={`${
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
              <div
                className={`${
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
              <div
                className={`${
                  darkMode ? "bg-gray-800" : "bg-gray-50"
                } p-6 rounded-2xl shadow-lg max-w-md`}
              >
                <p className="text-2xl font-semibold">₹69,696,999.80</p>
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
            </div>
            <div className="flex gap-10">
              <div
                className={`${
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
              <div
                className={`${
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
              <div
                className={`${
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
              <div
                className={`${
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
              <div
                className={`${
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
              <div
                className={`${
                  darkMode ? "bg-gray-800" : "bg-gray-50"
                } p-6 rounded-2xl shadow-lg max-w-md`}
              >
                <p className="text-2xl font-semibold">₹69,696,999.80</p>
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
            </div>
          </div>
        </div>
        
        {/* some dashboard design welcome sugars*/}
        <div className="text-center mb-10 mt-10">
          <h1 className="text-4xl font-bold mb-4">Welcome to Your Crypto Dashboard</h1>
          <p className={`${darkMode ? "text-gray-300" : "text-gray-700"} text-lg`}>
            Track your portfolio, get insights, and trade securely.
          </p>
        </div>

        {/* Chatbot Promo */}
        <div
          className={`${
            darkMode ? "bg-gray-800" : "bg-gray-100"
          } p-8 mt-10 rounded-2xl shadow-lg flex flex-col items-center text-center mb-12`}
        >
          <div className='flex'>
            <h3 className="text-2xl font-semibold mb-2 bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
              Try Our Smart Chatbot 
            </h3>
            <Bot className="w-8 h-8 ml-2 text-blue-500" />
          </div>
          <p className={`${darkMode ? "text-gray-300" : "text-gray-700"} mb-4`}>
            Ask questions. Get instant insights. Experience the power of AI for crypto.
          </p>
          <button
            onClick={() => (window.location.href = "/chatbot")}
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-3 rounded-xl font-medium shadow-md hover:scale-105 transform transition"
          >
            Start Chatting
          </button>
        </div>
      </section>
    </main>
  );
}
