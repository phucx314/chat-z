"use client";
import { useChat } from "@/context/ChatContext";

export default function ChatHeader() {
  const { convs, activeId, config, setSidebarOpen } = useChat();
  const conv = convs.find(c => c.id === activeId);
  const title = conv?.title || "AI Assistant";
  const provider = config?.provider?.split(" (")[0] || "";
  const model = config?.model || "";

  return (
    <header className="flex items-center gap-3 px-4 md:px-5 h-[60px] bg-[#13151c] border-b border-[#1e2230] flex-shrink-0">
      {/* Mobile Hamburger */}
      <button 
        onClick={() => setSidebarOpen(true)}
        className="md:hidden text-[#e4e6f0] p-1 -ml-1 text-2xl"
      >☰</button>

      {/* Avatar */}
      <div className="w-[38px] h-[38px] md:w-[42px] md:h-[42px] rounded-full bg-[#1e2533] border-[1.5px] border-[#4f6ef7] flex items-center justify-center text-[#4f6ef7] text-lg md:text-xl font-bold flex-shrink-0">
        ✦
      </div>

      {/* Info */}
      <div className="flex-1">
        <p className="text-[15px] font-bold text-[#e4e6f0] leading-tight">{title}</p>
        <p className="text-xs font-semibold text-[#25d366]">● Active Now</p>
      </div>

      {/* Provider · Model badge */}
      {model && (
        <span className="text-[11px] text-[#545872] bg-[#1e2330] px-3 py-1.5 rounded-xl">
          {provider} · {model}
        </span>
      )}
    </header>
  );
}
