"use client";
import { createContext, useContext, useEffect, useState, useCallback, useRef } from "react";
import { api, Conversation, Message, Config } from "@/lib/api";

export const AVATAR_COLORS = [
  "#4f6ef7","#e05678","#25a56a","#f07d3e",
  "#9b59b6","#1abc9c","#e74c3c","#3498db",
  "#f39c12","#d35400","#8e44ad","#16a085",
];

interface ChatState {
  convs: Conversation[];
  activeId: string | null;
  messages: Message[];
  config: Config | null;
  sending: boolean;
  loading: boolean;
  serverError: string | null;
}

interface ChatActions {
  newChat: () => Promise<void>;
  loadConv: (id: string) => Promise<void>;
  deleteConv: (id: string) => Promise<void>;
  renameConv: (id: string, title: string) => Promise<void>;
  updateAvatar: (id: string, color: string) => Promise<void>;
  sendMessage: (text: string) => Promise<void>;
  deleteMessage: (idx: number) => Promise<void>;
  updateConfig: (data: Record<string, string>) => Promise<void>;
  refreshConvs: () => Promise<void>;
}

const ChatCtx = createContext<(ChatState & ChatActions) | null>(null);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [convs, setConvs] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [config, setConfig] = useState<Config | null>(null);
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [serverError, setServerError] = useState<string | null>(null);

  const fetchConvs = useCallback(async () => {
    const cs = await api.getConversations();
    setConvs(cs);
    return cs;
  }, []);

  const loadConvById = useCallback(async (id: string) => {
    const conv = await api.getConversation(id);
    setActiveId(conv.id);
    setMessages(conv.messages ?? []);
    setConvs(prev => prev.map(c => c.id === id ? conv : c));
  }, []);

  // ── Boot ──────────────────────────────────────────────────────────────────
  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const [cfg, cs] = await Promise.all([api.getConfig(), api.getConversations()]);
        setConfig(cfg);

        // Clean stale empty "New Chat" entries
        const stale = cs.filter(c => !c.messages?.length && c.title === "New Chat");
        const live   = cs.filter(c => c.messages?.length  || c.title !== "New Chat");
        stale.forEach(c => api.deleteConversation(c.id).catch(() => {}));
        setConvs(live);

        if (live.length) {
          await loadConvById(live[0].id);
        } else {
          const conv = await api.createConversation();
          const fresh = await api.getConversations();
          setConvs(fresh);
          setActiveId(conv.id);
          setMessages([]);
        }
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        setServerError(msg);
      } finally {
        setLoading(false);
      }
    })();
  }, [loadConvById]);

  // ── Actions ───────────────────────────────────────────────────────────────
  const refreshConvs = useCallback(async () => {
    const cs = await fetchConvs();
    setConvs(cs);
  }, [fetchConvs]);

  const newChat = useCallback(async () => {
    // Remove other empty new chats
    const cs = await api.getConversations();
    const stale = cs.filter(c => !c.messages?.length && c.title === "New Chat");
    stale.forEach(c => api.deleteConversation(c.id).catch(() => {}));

    const conv = await api.createConversation();
    const fresh = await api.getConversations();
    setConvs(fresh);
    setActiveId(conv.id);
    setMessages([]);
  }, []);

  const loadConv = useCallback(async (id: string) => {
    await loadConvById(id);
  }, [loadConvById]);

  const deleteConv = useCallback(async (id: string) => {
    await api.deleteConversation(id);
    const cs = await api.getConversations();
    setConvs(cs);
    if (id === activeId) {
      if (cs.length) await loadConvById(cs[0].id);
      else {
        const conv = await api.createConversation();
        const fresh = await api.getConversations();
        setConvs(fresh);
        setActiveId(conv.id);
        setMessages([]);
      }
    }
  }, [activeId, loadConvById]);

  const renameConv = useCallback(async (id: string, title: string) => {
    await api.renameConversation(id, title);
    setConvs(prev => prev.map(c => c.id === id ? { ...c, title } : c));
  }, []);

  const updateAvatar = useCallback(async (id: string, color: string) => {
    await api.updateAvatar(id, color);
    setConvs(prev => prev.map(c => c.id === id ? { ...c, avatar_color: color } : c));
  }, []);

  const typingRunRef = useRef(0);

  const sendMessage = useCallback(async (text: string) => {
    if (!activeId) return;
    
    // If we're already sending and interrupts are disabled, ignore.
    if (sending && !config?.allow_interrupt) return;

    const currentRunId = ++typingRunRef.current;
    const currentActiveId = activeId;
    
    // If interrupting, capture exactly what is on the screen right now
    const override_messages = sending ? messages : undefined;

    setSending(true);

    // Optimistic user bubble
    let currentMessages = [...messages, { role: "user" as const, content: text }];
    setMessages(currentMessages);

    // Auto-title on first message
    const conv = convs.find(c => c.id === activeId);
    if (conv && !conv.messages?.length) {
      const title = text.slice(0, 40) + (text.length > 40 ? "…" : "");
      api.renameConversation(activeId, title).catch(() => {});
      setConvs(prev => prev.map(c => c.id === activeId ? { ...c, title } : c));
    }

    try {
      const res = await api.sendMessage(activeId, text, config?.model, override_messages);
      
      // Simulate typing delays for multiple replies
      for (let i = 0; i < res.replies.length; i++) {
        const reply = res.replies[i];
        
        const msPerChar = 80;
        const baseDelay = 500;
        const delay = Math.min(baseDelay + (reply.length * msPerChar), 5000);
        
        await new Promise(resolve => setTimeout(resolve, delay));

        // Abort if a new message was sent (interrupted) or switched chat
        if (typingRunRef.current !== currentRunId || activeId !== currentActiveId) {
          return;
        }

        // Update messages optimistic queue
        currentMessages = [...currentMessages, { role: "assistant" as const, content: reply }];
        setMessages(currentMessages);
      }

      // Sync the full state to be exactly what the server has
      if (typingRunRef.current === currentRunId && activeId === currentActiveId) {
        setMessages(res.messages);
      }
      
      const cs = await api.getConversations();
      setConvs(cs);
    } catch (e: unknown) {
      if (typingRunRef.current === currentRunId && activeId === currentActiveId) {
        const msg = e instanceof Error ? e.message : String(e);
        setMessages(prev => [...prev, { role: "assistant", content: `❌ Lỗi: ${msg}` }]);
      }
    } finally {
      if (typingRunRef.current === currentRunId) {
        setSending(false);
      }
    }
  }, [activeId, sending, messages, convs, config?.model, config?.allow_interrupt]);

  const deleteMessage = useCallback(async (idx: number) => {
    if (!activeId) return;
    const res = await api.deleteMessage(activeId, idx);
    setMessages(res.messages);
  }, [activeId]);

  const updateConfig = useCallback(async (data: Record<string, string>) => {
    await api.updateConfig(data);
    const cfg = await api.getConfig();
    setConfig(cfg);
  }, []);

  return (
    <ChatCtx.Provider value={{
      convs, activeId, messages, config, sending, loading, serverError,
      newChat, loadConv, deleteConv, renameConv, updateAvatar,
      sendMessage, deleteMessage, updateConfig, refreshConvs,
    }}>
      {children}
    </ChatCtx.Provider>
  );
}

export const useChat = () => {
  const ctx = useContext(ChatCtx);
  if (!ctx) throw new Error("useChat must be inside ChatProvider");
  return ctx;
};
