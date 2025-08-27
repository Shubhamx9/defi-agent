"use client";
import { useEvmAddress } from "@coinbase/cdp-hooks";
import { AuthButton } from "@coinbase/cdp-react/components/AuthButton";
import { useEffect, useState } from "react";

import { IconCheck, IconCopy, IconUser } from "@/components/Icons";

export default function Header() {
  const { evmAddress } = useEvmAddress();
  const [isCopied, setIsCopied] = useState(false);

  const copyAddress = async () => {
    if (!evmAddress) return;
    try {
      await navigator.clipboard.writeText(evmAddress);
      setIsCopied(true);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    if (!isCopied) return;
    const timeout = setTimeout(() => setIsCopied(false), 2000);
    return () => clearTimeout(timeout);
  }, [isCopied]);

  const isSmartAccountsEnabled =
    process.env.NEXT_PUBLIC_CDP_CREATE_ACCOUNT_TYPE === "evm-smart";

  return (
    <header className="sticky top-0 z-50 min-w-3xl bg-gray-900 backdrop-blur-md border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
        {/* Left: Title */}
        <div className="flex items-center gap-2">
          <h1 className="text-lg sm:text-xl font-bold text-white">
            CDP Next.js StarterKit
          </h1>
          {isSmartAccountsEnabled && (
            <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-blue-500/20 text-blue-400 font-medium">
              SMART
            </span>
          )}
        </div>

        {/* Right: Wallet Info + Auth */}
        <div className="flex items-center gap-3">
          {evmAddress && (
            <button
              aria-label="Copy wallet address"
              onClick={copyAddress}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20 text-sm font-medium text-gray-200 transition-colors"
            >
              {!isCopied ? (
                <>
                  <IconUser className="w-4 h-4 text-gray-300" />
                  <IconCopy className="w-4 h-4 text-gray-400" />
                </>
              ) : (
                <IconCheck className="w-4 h-4 text-green-400" />
              )}
              <span className="truncate max-w-[100px] sm:max-w-[140px]">
                {evmAddress.slice(0, 6)}...{evmAddress.slice(-4)}
              </span>
            </button>
          )}

          {/* Coinbase Auth Button */}
          <div className="ml-2">
            <AuthButton />
          </div>
        </div>
      </div>
    </header>
  );
}
