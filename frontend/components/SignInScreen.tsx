"use client";

import { AuthButton } from "@coinbase/cdp-react/components/AuthButton";

export default function SignInScreen() {
  return (
    <main className="w-full h-full rounded-2xl flex items-center justify-center bg-gradient-to-br from-slate-900 via-gray-900 to-black ">
      <div className="w-full max-w-md bg-white/10 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 p-8 flex flex-col items-center text-center">
        <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">
          Welcome to DeFi AI Assistant
        </h1>
        <p className="text-gray-300 mb-6 text-sm sm:text-base">
          Connect your wallet to get started
        </p>

        <div className="w-full flex justify-center">
          <AuthButton
            className="w-full flex items-center justify-center gap-2 rounded-xl 
                       bg-gradient-to-r from-blue-500 to-purple-600 
                       text-white font-semibold text-sm sm:text-base
                       shadow-md hover:scale-[1.02] active:scale-[0.98] 
                       transition-all duration-200"
          />
        </div>

        <p className="mt-6 text-xs text-gray-400">
          By signing in, you agree to our{" "}
          <a href="/terms" className="underline hover:text-gray-200">
            Terms
          </a>{" "}
          and{" "}
          <a href="/privacy" className="underline hover:text-gray-200">
            Privacy Policy
          </a>
          .
        </p>
      </div>
    </main>
  );
}
