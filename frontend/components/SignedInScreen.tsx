"use client";

import { useEvmAddress, useIsSignedIn } from "@coinbase/cdp-hooks";
import { useCallback, useEffect, useMemo, useState } from "react";
import { createPublicClient, http, formatEther } from "viem";
import { baseSepolia } from "viem/chains";

import Header from "@/components/Header";
import Transaction from "@/components/Transaction";
import UserBalance from "@/components/UserBalance";

/**
 * Create a viem client to access user's balance on the Base Sepolia network
 */
const client = createPublicClient({
  chain: baseSepolia,
  transport: http(),
});

export default function SignedInScreen() {
  const { isSignedIn } = useIsSignedIn();
  const { evmAddress } = useEvmAddress();
  const [balance, setBalance] = useState<bigint | undefined>(undefined);

  const formattedBalance = useMemo(() => {
    if (balance === undefined) return undefined;
    return formatEther(balance);
  }, [balance]);

  const getBalance = useCallback(async () => {
    if (!evmAddress) return;
    const balance = await client.getBalance({
      address: evmAddress,
    });
    setBalance(balance);
  }, [evmAddress]);

  useEffect(() => {
    getBalance();
    const interval = setInterval(getBalance, 5000); // update every 5s
    return () => clearInterval(interval);
  }, [getBalance]);

  return (
    <div className=" flex flex-col bg-gradient-to-br from-slate-900 via-gray-900 to-black text-white">
      {/* Sticky Header */}
      <Header />

      <main className="flex-1 flex flex-col items-center justify-center px-5 py-6">
        <div className="w-full max-w-3xl space-y-8">
          {/* Balance Card */}
            <div className="group relative overflow-hidden bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-lg transition-all duration-300 hover:scale-[1.02] hover:border-blue-500/40 hover:shadow-blue-500/20">
              {/* Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-tr from-blue-500/10 via-purple-500/10 to-transparent opacity-0 group-hover:opacity-100 blur-2xl transition-opacity duration-500"></div>

              <div className="flex flex-col space-y-5 relative z-10">
                {/* Title */}
                <h2 className="text-sm font-medium text-gray-300 uppercase tracking-wide">
                  Balance Overview
                </h2>

                {/* Balance Value */}
                <div>
                  <p className="text-xl font-bold text-white">
                    <UserBalance balance={formattedBalance} />
                  </p>
                  <p className="text-xs text-gray-400 mt-1">Available on Base Sepolia</p>
                </div>

                {/* Wallet Address */}
                <div className="pt-4 border-t border-white/10">
                  <p className="text-xs text-gray-500 truncate font-mono">
                    {evmAddress}
                  </p>
                </div>
              </div>
            </div>

            {/* Transaction Card */}
            <div className="group relative overflow-hidden bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-lg transition-all duration-300 hover:scale-[1.02] hover:border-purple-500/40 hover:shadow-purple-500/20">
              {/* Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/10 via-pink-500/10 to-transparent opacity-0 group-hover:opacity-100 blur-2xl transition-opacity duration-500"></div>

              <div className="flex flex-col space-y-6 relative z-10">
                {/* Title */}
                <h2 className="text-sm font-medium text-gray-300 uppercase tracking-wide">
                  Make a Transaction
                </h2>

                {/* Subtitle */}
                <p className="text-sm text-gray-400 leading-relaxed">
                  Send tokens securely and quickly using your connected wallet.
                </p>

                {/* Transaction Form */}
                {isSignedIn && evmAddress && (
                  <div>
                    <Transaction balance={formattedBalance} onSuccess={getBalance} />
                  </div>
                )}
              </div>
            </div>



        </div>
      </main>
    </div>
  );
}
