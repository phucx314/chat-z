"use client";
import { useState } from "react";
import { useChat } from "@/context/ChatContext";
import { useAuth } from "@/context/AuthContext";
import ConvItem from "./ConvItem";
import SettingsModal from "./SettingsModal";

export default function Sidebar() {
  const { convs, newChat } = useChat();
  const { user, logout } = useAuth();
  const [search, setSearch] = useState("");
  const [showSettings, setShowSettings] = useState(false);

  const filtered = convs.filter(c => c.title.toLowerCase().includes(search.toLowerCase()));

  return (
    <>
      <aside className="w-[280px] min-w-[260px] bg-[#13151c] border-r border-[#1e2230] flex flex-col overflow-hidden">
        {/* Title row */}
        <div className="flex items-center justify-between px-4 pt-5 pb-2">
          <h1 className="text-[22px] font-extrabold text-[#e4e6f0]">Chats</h1>
          <button
            onClick={newChat}
            title="New Chat"
            className="w-9 h-9 rounded-full bg-[#1e2330] text-[#4f6ef7] hover:bg-[#252a3e] transition-colors flex items-center justify-center text-lg font-bold"
          >✎</button>
        </div>

        {/* Search */}
        <div className="px-3 pb-2">
          <input
            type="text"
            placeholder="🔍  Search Messenger"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-[#1e2330] rounded-2xl px-4 py-2 text-sm text-[#e4e6f0] placeholder:text-[#545872] outline-none"
          />
        </div>

        {/* Conv list */}
        <div className="flex-1 overflow-y-auto px-2 space-y-0.5 scrollbar-thin scrollbar-thumb-[#1e2230]">
          {filtered.length === 0 && (
            <p className="text-center text-[#545872] text-sm py-8">No conversations yet</p>
          )}
          {filtered.map((conv, i) => (
            <ConvItem key={conv.id} conv={conv} index={i} />
          ))}
        </div>

        {/* Bottom settings */}
        <div className="border-t border-[#1e2230] p-2 flex flex-col gap-1">
          {user && (
            <div className="px-4 py-2 flex items-center justify-between">
              <span className="text-sm font-bold text-[#e4e6f0] truncate">@{user.username}</span>
              <button 
                onClick={logout}
                title="Sign Out"
                className="text-xs text-[#e05678] hover:underline"
              >
                Logout
              </button>
            </div>
          )}
          <button
            onClick={() => setShowSettings(true)}
            className="w-full text-left px-4 py-2.5 rounded-xl text-sm text-[#8b90a7] hover:bg-[#1e2230] hover:text-[#e4e6f0] transition-colors flex items-center gap-2"
          >
            ⚙  Settings
          </button>
        </div>
      </aside>

      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </>
  );
}
