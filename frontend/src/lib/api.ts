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

let accessToken = "";
export const setAccessToken = (token: string) => { accessToken = token; };
export const getAccessToken = () => accessToken;

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

const onRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

async function req<T>(method: string, path: string, body?: unknown, isRetry = false): Promise<T> {
  const headers: Record<string, string> = {};
  if (body) headers["Content-Type"] = "application/json";
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
    cache: "no-store",
    credentials: "omit", // We don't send cookies to non-auth routes
  });

  if (res.status === 401 && !isRetry && path !== "/auth/login" && path !== "/auth/refresh") {
    if (!isRefreshing) {
      isRefreshing = true;
      try {
        const refreshRes = await fetch(`${API_URL}/auth/refresh`, {
          method: "POST",
          credentials: "include", // Send HttpOnly cookie for refresh token
        });
        
        if (!refreshRes.ok) throw new Error("Session expired");
        
        const data = await refreshRes.json();
        setAccessToken(data.access_token);
        isRefreshing = false;
        onRefreshed(data.access_token);
      } catch (err) {
        isRefreshing = false;
        refreshSubscribers = [];
        // Optional: clear local state and force redirect to /login
        if (typeof window !== "undefined") {
            window.location.href = "/login";
        }
        throw err;
      }
    }

    // Wait for refresh to finish, then retry
    return new Promise((resolve, reject) => {
      subscribeTokenRefresh((token: string) => {
        req<T>(method, path, body, true).then(resolve).catch(reject);
      });
    });
  }

  if (res.status === 401 && isRetry) {
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Session expired");
  }

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
