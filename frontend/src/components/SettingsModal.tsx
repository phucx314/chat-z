"use client";
import { useState } from "react";
import { useChat } from "@/context/ChatContext";

export default function SettingsModal({ onClose }: { onClose: () => void }) {
  const { config, updateConfig } = useChat();
  const [provider, setProvider] = useState(config?.provider || "");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState(config?.base_url || "");
  const [allowInterrupt, setAllowInterrupt] = useState(config?.allow_interrupt || false);
  const [saving, setSaving] = useState(false);

  const providers = Object.keys(config?.providers || {});

  const handleProviderChange = (p: string) => {
    setProvider(p);
    const preset = config?.providers[p];
    if (preset) setBaseUrl(preset.base_url);
  };

  const handleSave = async () => {
    setSaving(true);
    await updateConfig({ provider, base_url: baseUrl, allow_interrupt: allowInterrupt, ...(apiKey ? { api_key: apiKey } : {}) });
    setSaving(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[2000]" onClick={onClose}>
      <div
        className="bg-[#13151c] border border-[#1e2230] rounded-2xl p-7 w-[440px] flex flex-col gap-4 shadow-2xl"
        onClick={e => e.stopPropagation()}
      >
        <h2 className="text-lg font-extrabold text-[#e4e6f0]">Settings</h2>
        <hr className="border-[#1e2230]" />

        {/* Provider */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] font-bold uppercase tracking-widest text-[#545872]">Provider</label>
          <select
            value={provider}
            onChange={e => handleProviderChange(e.target.value)}
            className="bg-[#1e2330] border border-[#1e2230] rounded-xl px-3 py-2.5 text-[#e4e6f0] text-sm outline-none focus:border-[#4f6ef7] transition-colors"
          >
            {providers.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>

        {/* API Key */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] font-bold uppercase tracking-widest text-[#545872]">API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder="Enter API key (blank = use .env)"
            className="bg-[#1e2330] border border-[#1e2230] rounded-xl px-3 py-2.5 text-[#e4e6f0] text-sm outline-none focus:border-[#4f6ef7] transition-colors placeholder:text-[#545872]"
          />
          {config?.key_from_env && (
            <p className="text-xs text-[#25d366]">✓ Key loaded from .env</p>
          )}
        </div>

        {/* Base URL */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] font-bold uppercase tracking-widest text-[#545872]">Base URL</label>
          <input
            type="text"
            value={baseUrl}
            onChange={e => setBaseUrl(e.target.value)}
            className="bg-[#1e2330] border border-[#1e2230] rounded-xl px-3 py-2.5 text-[#e4e6f0] text-sm outline-none focus:border-[#4f6ef7] transition-colors"
          />
        </div>

        {/* Behavior / Interrupt */}
        <div className="flex items-center justify-between p-3 mt-1 bg-[#1e2330]/50 rounded-xl border border-[#1e2230]">
          <div>
            <div className="text-[13px] font-bold text-[#e4e6f0]">Cho phép Chat Chen Ngang</div>
            <div className="text-[11px] text-[#545872]">Dừng AI đang gõ để trả lời ngay tin nhắn mới (Experimental)</div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              checked={allowInterrupt} 
              onChange={e => setAllowInterrupt(e.target.checked)} 
              className="sr-only peer" 
            />
            <div className="w-9 h-5 bg-[#1e2230] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-[#8b90a7] peer-checked:after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#4f6ef7]"></div>
          </label>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 mt-1">
          <button onClick={onClose} className="px-5 py-2.5 rounded-xl text-sm text-[#8b90a7] bg-[#1e2330] hover:bg-[#1e2230] transition-colors">
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-[#4f6ef7] hover:bg-[#3d5ce5] disabled:opacity-60 transition-colors"
          >
            {saving ? "Saving…" : "Save"}
          </button>
        </div>
      </div>
    </div>
  );
}
