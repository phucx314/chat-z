"use client";
import { useRef, useState, KeyboardEvent } from "react";
import { useChat } from "@/context/ChatContext";

export default function InputArea() {
  const { sendMessage, sending, config } = useChat();
  const [text, setText] = useState("");
  const [showModelMenu, setShowModelMenu] = useState(false);
  const textRef = useRef<HTMLTextAreaElement>(null);

  const currentModel = config?.model || "Loading…";
  const providerModels = config ? (config.providers[config.provider]?.models || []) : [];

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = async () => {
    const t = text.trim();
    if (!t || sending) return;
    setText("");
    if (textRef.current) textRef.current.style.height = "auto";
    await sendMessage(t);
    textRef.current?.focus();
  };

  const handleInput = () => {
    const el = textRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 150) + "px";
  };

  const { updateConfig } = useChat();
  const selectModel = async (model: string) => {
    await updateConfig({ model });
    setShowModelMenu(false);
  };

  return (
    <div className="bg-[#13151c] border-t border-[#1e2230] px-4 py-3">
      {/* Pill */}
      <div className="flex items-center bg-[#1a1d27] rounded-3xl border border-[#1e2230] focus-within:border-[#4f6ef7] transition-colors px-4 py-1 gap-3">
        {/* Model selector */}
        <div className="relative flex-shrink-0">
          <button
            onClick={() => setShowModelMenu(v => !v)}
            className="text-[#4f6ef7] font-bold text-xs hover:bg-[#1e2330] px-2 py-1 rounded-xl transition-colors whitespace-nowrap"
          >
            ⚡ {currentModel} ▾
          </button>
          {showModelMenu && providerModels.length > 0 && (
            <div className="absolute bottom-full left-0 mb-2 bg-[#1e2330] border border-[#2a2d3e] rounded-xl shadow-2xl overflow-hidden z-50 min-w-[180px]">
              {providerModels.map(m => (
                <button
                  key={m}
                  onClick={() => selectModel(m)}
                  className={`w-full text-left px-4 py-2.5 text-sm hover:bg-[#4f6ef7] hover:text-white transition-colors
                    ${m === currentModel ? "text-[#4f6ef7] font-semibold" : "text-[#e4e6f0]"}`}
                >
                  {m}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Divider */}
        <div className="w-px h-5 bg-[#2a2d3e] flex-shrink-0" />

        {/* Textarea */}
        <textarea
          ref={textRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onInput={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          rows={1}
          disabled={sending && !config?.allow_interrupt}
          className="flex-1 bg-transparent text-[#e4e6f0] placeholder:text-[#545872] text-sm resize-none outline-none py-2 max-h-[150px] leading-relaxed disabled:opacity-60"
        />

        {/* Send */}
        <button
          onClick={handleSend}
          disabled={(sending && !config?.allow_interrupt) || !text.trim()}
          className="w-11 h-11 rounded-full bg-[#4f6ef7] hover:bg-[#3d5ce5] disabled:bg-[#1e2330] disabled:text-[#545872] text-white text-lg flex items-center justify-center flex-shrink-0 transition-colors"
        >➤</button>
      </div>

      {/* Hint */}
      <p className="text-center text-[11px] text-[#545872] mt-1.5">
        Enter to send · Shift+Enter for new line
      </p>

      {/* Close model menu on outside click */}
      {showModelMenu && (
        <div className="fixed inset-0 z-40" onClick={() => setShowModelMenu(false)} />
      )}
    </div>
  );
}
