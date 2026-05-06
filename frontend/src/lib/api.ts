import API_URL from "./api-url";

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface Conversation {
  id: string;
  title: string;
  avatar_color?: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

export interface Config {
  provider: string;
  model: string;
  base_url: string;
  has_key: boolean;
  key_from_env: boolean;
  allow_interrupt?: boolean;
  providers: Record<string, { base_url: string; models: string[] }>;
}

async function req<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
    cache: "no-store",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

export const api = {
  getConversations: () => req<Conversation[]>("GET", "/conversations"),
  getConversation:  (id: string) => req<Conversation>("GET", `/conversations/${id}`),
  createConversation: (title = "New Chat") => req<Conversation>("POST", "/conversations", { title }),
  renameConversation: (id: string, title: string) => req("PATCH", `/conversations/${id}/rename`, { title }),
  updateAvatar:      (id: string, color: string) => req("PATCH", `/conversations/${id}/avatar`, { color }),
  deleteConversation: (id: string) => req("DELETE", `/conversations/${id}`),
  deleteMessage:     (convId: string, idx: number) => req<{ ok: boolean; messages: Message[] }>("DELETE", `/conversations/${convId}/messages/${idx}`),
  sendMessage:       (convId: string, message: string, model?: string, override_messages?: Message[]) =>
    req<{ replies: string[]; messages: Message[] }>("POST", "/chat/send", { conv_id: convId, message, model, override_messages }),
  getConfig:     () => req<Config>("GET", "/config"),
  updateConfig:  (data: Partial<{ provider: string; model: string; base_url: string; api_key: string; allow_interrupt: boolean }>) =>
    req("PATCH", "/config", data),
};
