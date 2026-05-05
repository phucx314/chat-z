import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ChatProvider } from "@/context/ChatContext";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  title: "AI Chat",
  description: "GenZ AI Chatbot — powered by FastAPI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body className={`${inter.className} bg-[#0e1117] text-[#e4e6f0] overflow-hidden h-screen`} suppressHydrationWarning>
        <ChatProvider>
          {children}
        </ChatProvider>
      </body>
    </html>
  );
}
