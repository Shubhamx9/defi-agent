"use client";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { useIsInitialized, useIsSignedIn } from "@coinbase/cdp-hooks";
import { Loader2 } from "lucide-react"; // spinner icon if you want loading state
import Providers from "../Providers";
import ClientApp from "../ClientApp";

export default function WalletButton() {
  const { isInitialized } = useIsInitialized();
  const { isSignedIn } = useIsSignedIn();

  // Loading state (SDK not ready yet)
  if (!isInitialized) {
    return (
      <button
        disabled
        className="cursor-not-allowed opacity-60 text-slate-100 bg-gradient-to-r from-blue-500 to-purple-600 shadow px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2"
      >
        <Loader2 className="h-4 w-4 animate-spin" />
        Connecting...
      </button>
    );
  }

  // Not signed in → Show "Connect Wallet"
  if (!isSignedIn) {
    return (
        <Popover>
        <PopoverTrigger><button
                className="w-full cursor-pointer text-slate-100 bg-gradient-to-r from-blue-500 to-purple-600 shadow hover:scale-105 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
            >
                Connect Wallet
            </button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0 rounded-2xl">
            <Providers>
                <ClientApp />
            </Providers>
        </PopoverContent>
    </Popover>
      
    );
  }

  // Signed in → Show rounded button (you’ll add popover later)
  return (
    <Popover >
        <PopoverTrigger><button
            className="w-full rounded-full bg-gradient-to-r from-green-500 to-emerald-600 px-4 py-2 text-white font-medium shadow hover:scale-105 transition-all duration-200"
            >
            Wallet
            </button>
        </PopoverTrigger>
        <PopoverContent className="w-auto overflow-auto p-0 max-h-[700px] rounded-2xl">
            <Providers>
                <ClientApp />
            </Providers>
        </PopoverContent>
    </Popover>
    
  );
}
