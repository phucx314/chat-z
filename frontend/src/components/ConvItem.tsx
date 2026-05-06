"use client";
import { useState, useRef } from "react";
import { useChat, AVATAR_COLORS } from "@/context/ChatContext";
import { Conversation } from "@/lib/api";

interface Props { conv: Conversation; index: number; }

export default function ConvItem({ conv, index }: Props) {
  const { activeId, loadConv, deleteConv, renameConv, updateAvatar } = useChat();
  const [hovering, setHovering] = useState(false);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [renaming, setRenaming] = useState(false);
  const [renameVal, setRenameVal] = useState(conv.title);
  const inputRef = useRef<HTMLInputElement>(null);

  const isActive = conv.id === activeId;
  const color = conv.avatar_color || AVATAR_COLORS[index % AVATAR_COLORS.length];
  const letter = conv.title[0]?.toUpperCase() || "N";
  const msgs = conv.messages || [];
  const last = msgs[msgs.length - 1];
  const preview = last
    ? (last.role === "user" ? "You: " : "AI: ") + last.content.slice(0, 35)
    : "New conversation";
  const ts = conv.updated_at
    ? new Date(conv.updated_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "";

  const handleRenameSubmit = async () => {
    if (renameVal.trim()) await renameConv(conv.id, renameVal.trim());
    setRenaming(false);
  };

  return (
    <div
      className={`relative flex items-center gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer border-l-[3px] transition-all duration-150
        ${isActive ? "bg-[#1e2330] border-l-[#4f6ef7]" : "bg-transparent border-l-transparent hover:bg-[#1e2230]"}`}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => { setHovering(false); setShowColorPicker(false); }}
      onClick={() => !renaming && loadConv(conv.id)}
    >
      {/* Avatar */}
      <div
        className="w-11 h-11 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
        style={{ background: color }}
        onClick={e => { e.stopPropagation(); setShowColorPicker(v => !v); }}
        title="Change color"
      >
        {letter}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        {renaming ? (
          <input
            ref={inputRef}
            autoFocus
            value={renameVal}
            onChange={e => setRenameVal(e.target.value)}
            onBlur={handleRenameSubmit}
            onKeyDown={e => {
              if (e.key === "Enter") handleRenameSubmit();
              if (e.key === "Escape") setRenaming(false);
            }}
            onClick={e => e.stopPropagation()}
            className="w-full bg-[#2a2d3e] text-[#e4e6f0] rounded px-2 py-0.5 text-sm outline-none border border-[#4f6ef7]"
          />
        ) : (
          <p className="text-sm font-semibold text-[#e4e6f0] truncate">{conv.title}</p>
        )}
        <p className="text-xs text-[#8b90a7] truncate">{preview}</p>
      </div>

      {/* Right: time + actions */}
      <div className="flex flex-col items-end gap-1 flex-shrink-0">
        <span className="text-[11px] text-[#545872]">{ts}</span>
        {hovering && !renaming && (
          <div className="flex gap-1" onClick={e => e.stopPropagation()}>
            <button
              title="Rename"
              onClick={() => { setRenaming(true); setRenameVal(conv.title); }}
              className="text-[#8b90a7] hover:text-[#e4e6f0] text-xs px-1.5 py-0.5 rounded hover:bg-[#3a3b3c] transition-colors"
            >✏</button>
            <button
              title="Delete"
              onClick={() => { if (confirm("Xóa cuộc trò chuyện này?")) deleteConv(conv.id); }}
              className="text-[#8b90a7] hover:text-red-400 text-xs px-1.5 py-0.5 rounded hover:bg-[#3a1a1a] transition-colors"
            >🗑</button>
          </div>
        )}
      </div>

      {/* Color picker */}
      {showColorPicker && (
        <div
          className="absolute left-14 top-0 z-50 bg-[#1e2330] border border-[#1e2230] rounded-xl p-3 shadow-2xl"
          onClick={e => e.stopPropagation()}
        >
          <div className="grid grid-cols-4 gap-2">
            {AVATAR_COLORS.map(c => (
              <button
                key={c}
                onClick={() => { updateAvatar(conv.id, c); setShowColorPicker(false); }}
                className="w-8 h-8 rounded-full border-2 border-transparent hover:border-white hover:scale-110 transition-all"
                style={{ background: c }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
