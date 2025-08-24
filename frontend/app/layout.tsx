
import { Providers } from "./(root)/(home)/providers";
import localFont from "next/font/local";
import { type Metadata } from 'next'
import {
  ClerkProvider,
} from '@clerk/nextjs'
import './globals.css'


import { Inter, Roboto_Mono } from "next/font/google";

const geistSans = Inter({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Roboto_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});



export const metadata: Metadata = {
  title: "DeFi AI Assistant",
  description: "AI-powered DeFi assistant",
  icons: {
    icon: "/favicon.ico",
  },
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <ClerkProvider
      appearance={{
          layout: {
            socialButtonsVariant: "iconButton",
          },
          variables: {
            colorText: "#fff",
            colorPrimary: "#0E78F9",
            colorBackground: "#1C1F2E",
            colorInputBackground: "#252A41",
            colorInputText: "#fff",
            colorNeutral :"#FFFFFF",
            colorDanger :"#FFFFFF",
            colorShimmer:"#FFFFFF",
            colorSuccess:"#FFFFFF",
            colorTextOnPrimaryBackground:"#FFFFFF",
            colorWarning:"#FFFFFF",

          },
        }}
        >
        <Providers>
          <body
            className={`${geistSans.variable} ${geistMono.variable} antialiased bg-dark-2`}
          >
            {children}
          </body>
        </Providers>

      </ClerkProvider>
      
    </html>
  );
}