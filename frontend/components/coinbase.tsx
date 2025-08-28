"use client";
import ClientApp from "@/components/ClientApp";
import Providers from "@/components/Providers";

/**
 * Home page for the Next.js app
 *
 * @returns The home page
 */
export default function Coinbase() {
  return (
    <Providers>
      <ClientApp />
    </Providers>
  );
}
