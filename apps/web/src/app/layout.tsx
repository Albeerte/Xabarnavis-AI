import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { GlobalAudioPlayer } from "@/components/GlobalAudioPlayer";
import { AnimatedCursor } from "@/components/AnimatedCursor";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Xabarnavis AI | AI Forensics Platformasi",
  description:
    "Rasm, video, audio va matn fayllarini tekshiradigan professional AI forensics platforma. QR kod orqali tasdiqlanadigan rasmiy hisobotlar.",
  icons: {
    icon: "/xabarnavis-logo.png",
    shortcut: "/xabarnavis-logo.png",
    apple: "/xabarnavis-logo.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="uz"
      data-scroll-behavior="smooth"
      className={`${geistSans.variable} ${geistMono.variable} h-full scroll-smooth antialiased`}
    >
      <body className="min-h-full theme-bg theme-text-primary pt-12">
        <GlobalAudioPlayer />
        <AnimatedCursor />
        {children}
      </body>
    </html>
  );
}



