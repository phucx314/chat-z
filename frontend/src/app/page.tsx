"use client";
import { useChat } from "@/context/ChatContext";
import { useAuth } from "@/context/AuthContext";
import Sidebar from "@/components/Sidebar";
import ChatHeader from "@/components/ChatHeader";
import ChatArea from "@/components/ChatArea";
import InputArea from "@/components/InputArea";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const { loading: chatLoading, serverError } = useChat();
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [authLoading, user, router]);

  if (authLoading || (!user && !authLoading)) {
    return (
      <main className="flex h-[100dvh] items-center justify-center bg-[#0e1117]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-full border-2 border-[#4f6ef7] border-t-transparent animate-spin" />
          <p className="text-[#8b90a7] text-sm">Authenticating…</p>
        </div>
      </main>
    );
  }

  if (serverError) {
    return (
      <main className="flex h-[100dvh] items-center justify-center bg-[#0e1117]">
        <div className="flex flex-col items-center gap-4 max-w-md text-center px-6">
          <div className="w-16 h-16 rounded-full bg-[#2a1a1a] border border-red-500/40 flex items-center justify-center text-3xl">⚠</div>
          <h2 className="text-xl font-bold text-red-400">Cannot Connect to Server</h2>
          <p className="text-[#8b90a7] text-sm leading-relaxed">
            Không thể kết nối tới FastAPI server tại{" "}
            <code className="bg-[#1e2330] px-1.5 py-0.5 rounded text-[#4f6ef7]">localhost:8000</code>
          </p>
          <div className="bg-[#13151c] border border-[#1e2230] rounded-xl p-4 text-left w-full">
            <p className="text-[11px] font-bold uppercase tracking-wider text-[#545872] mb-2">Start server with:</p>
            <code className="text-xs text-[#25d366] font-mono">
              uvicorn server.main:app --reload --port 8000
            </code>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="bg-[#4f6ef7] hover:bg-[#3d5ce5] text-white px-6 py-2.5 rounded-xl font-semibold transition-colors text-sm"
          >
            Retry
          </button>
        </div>
      </main>
    );
  }

  if (chatLoading) {
    return (
      <main className="flex h-[100dvh] items-center justify-center bg-[#0e1117]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-full border-2 border-[#4f6ef7] border-t-transparent animate-spin" />
          <p className="text-[#8b90a7] text-sm">Connecting to server…</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex h-[100dvh] overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden bg-[#0e1117]">
        <ChatHeader />
        <ChatArea />
        <InputArea />
      </div>
    </main>
  );
}
