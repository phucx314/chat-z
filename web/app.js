const API = "http://localhost:8000";

const AVATAR_COLORS = [
  "#4f6ef7","#e05678","#25a56a","#f07d3e",
  "#9b59b6","#1abc9c","#e74c3c","#3498db",
  "#f39c12","#d35400","#8e44ad","#16a085",
];

// ── State ──────────────────────────────────────────────────────────────────
let state = {
  convs:      [],
  activeId:   null,
  config:     {},
  sending:    false,
  renameTarget: null,
  colorTarget:  null,
};

// ── API helpers ────────────────────────────────────────────────────────────
async function api(method, path, body) {
  const res = await fetch(API + path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// ── Boot ───────────────────────────────────────────────────────────────────
async function boot() {
  try {
    [state.config, state.convs] = await Promise.all([
      api("GET", "/config"),
      api("GET", "/conversations"),
    ]);
  } catch (e) {
    showError("Cannot connect to server at " + API + ". Start it with:\n\nuvicorn server.main:app --reload --port 8000");
    return;
  }

  renderConvList();
  updateModelBtn();
  updateHeaderBadge();
  populateProviders();

  // Resume most recent non-empty conv or create one
  const withMsgs = state.convs.filter(c => c.messages && c.messages.length);
  if (withMsgs.length) {
    await loadConv(withMsgs[0].id);
  } else if (state.convs.length) {
    await loadConv(state.convs[0].id);
  } else {
    await newChat();
  }
}

function showError(msg) {
  const msgs = document.getElementById("chat-messages");
  msgs.innerHTML = `<div id="welcome">
    <div id="welcome-icon">⚠</div>
    <h2 style="color:#ff4d4f">Connection Error</h2>
    <pre style="color:#8b90a7;white-space:pre-wrap;text-align:center;font-family:monospace;font-size:13px">${msg}</pre>
  </div>`;
}

// ── Conversations ──────────────────────────────────────────────────────────
function renderConvList() {
  const list = document.getElementById("conv-list");
  const q    = document.getElementById("search-input").value.toLowerCase();

  list.innerHTML = "";
  const filtered = state.convs.filter(c => c.title.toLowerCase().includes(q));

  filtered.forEach((conv, i) => {
    const el   = document.createElement("div");
    el.className = "conv-item" + (conv.id === state.activeId ? " active" : "");
    el.dataset.id = conv.id;

    const color  = conv.avatar_color || AVATAR_COLORS[i % AVATAR_COLORS.length];
    const letter = conv.title[0]?.toUpperCase() || "N";

    const msgs    = conv.messages || [];
    const last    = msgs[msgs.length - 1];
    const preview = last ? (last.role === "user" ? "You: " : "AI: ") + last.content.slice(0, 35) : "New conversation";

    const ts = conv.updated_at
      ? new Date(conv.updated_at).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})
      : "";

    el.innerHTML = `
      <div class="conv-avatar" style="background:${color}">${letter}</div>
      <div class="conv-info">
        <div class="conv-name">${escHtml(conv.title)}</div>
        <div class="conv-preview">${escHtml(preview)}</div>
      </div>
      <div class="conv-right">
        <span class="conv-time">${ts}</span>
        <div class="conv-actions">
          <button class="conv-action-btn" data-action="rename" title="Rename">✏</button>
          <button class="conv-action-btn" data-action="color" title="Change color">🎨</button>
          <button class="conv-action-btn del" data-action="delete" title="Delete">🗑</button>
        </div>
      </div>
    `;

    el.addEventListener("click", e => {
      const btn = e.target.closest("[data-action]");
      if (btn) {
        e.stopPropagation();
        handleConvAction(btn.dataset.action, conv.id, conv.title);
        return;
      }
      loadConv(conv.id);
    });

    list.appendChild(el);
  });
}

async function loadConv(id) {
  state.activeId = id;
  renderConvList();
  try {
    const conv = await api("GET", `/conversations/${id}`);
    state.activeId = id;
    // Update in state
    const idx = state.convs.findIndex(c => c.id === id);
    if (idx >= 0) state.convs[idx] = conv;

    document.getElementById("header-title").textContent = conv.title;
    renderMessages(conv.messages || []);
  } catch (e) {
    console.error(e);
  }
}

async function newChat() {
  // Clean up empty new chats first
  const empties = state.convs.filter(c => (!c.messages || !c.messages.length) && c.title === "New Chat");
  for (const e of empties) {
    await api("DELETE", `/conversations/${e.id}`).catch(() => {});
  }

  const conv = await api("POST", "/conversations", { title: "New Chat" });
  state.convs = await api("GET", "/conversations");
  state.activeId = conv.id;
  renderConvList();
  document.getElementById("header-title").textContent = "AI Assistant";
  renderMessages([]);
  document.getElementById("msg-input").focus();
}

async function handleConvAction(action, id, title) {
  if (action === "delete") {
    if (!confirm("Xóa cuộc trò chuyện này?")) return;
    await api("DELETE", `/conversations/${id}`);
    state.convs = state.convs.filter(c => c.id !== id);
    if (state.activeId === id) {
      state.activeId = null;
      if (state.convs.length) await loadConv(state.convs[0].id);
      else await newChat();
    }
    renderConvList();
  } else if (action === "rename") {
    state.renameTarget = id;
    document.getElementById("rename-input").value = title;
    document.getElementById("rename-modal").classList.remove("hidden");
    document.getElementById("rename-input").focus();
    document.getElementById("rename-input").select();
  } else if (action === "color") {
    state.colorTarget = id;
    document.getElementById("color-modal").classList.remove("hidden");
  }
}

// ── Messages ───────────────────────────────────────────────────────────────
function renderMessages(messages) {
  const el = document.getElementById("chat-messages");

  if (!messages.length) {
    el.innerHTML = `<div id="welcome">
      <div id="welcome-icon">✦</div>
      <h2>AI Assistant</h2>
      <div class="online">● Active Now</div>
      <p>Send a message to start chatting</p>
    </div>`;
    return;
  }

  el.innerHTML = `<div class="date-pill"><span>Today</span></div>`;
  messages.forEach((msg, idx) => appendMessage(msg.role, msg.content, idx, false));
  scrollBottom();
}

function appendMessage(role, content, idx, scroll=true) {
  const isUser = role === "user";
  const el = document.getElementById("chat-messages");

  // Remove welcome if present
  const welcome = el.querySelector("#welcome");
  if (welcome) {
    el.innerHTML = `<div class="date-pill"><span>Today</span></div>`;
  }

  const row = document.createElement("div");
  row.className = `msg-row ${isUser ? "user" : "bot"}`;
  row.dataset.idx = idx ?? "";

  const avatarHtml = isUser ? "" : `<div class="msg-avatar">✦</div>`;

  row.innerHTML = `
    ${avatarHtml}
    <div class="msg-bubble">${escHtml(content)}</div>
    <button class="msg-del-btn" title="Xóa tin nhắn">✕</button>
  `;

  row.querySelector(".msg-del-btn").addEventListener("click", () => deleteMsg(row));
  el.appendChild(row);

  if (scroll) scrollBottom();
}

async function deleteMsg(row) {
  if (!state.activeId) return;
  const allRows = [...document.querySelectorAll(".msg-row")];
  const idx = allRows.indexOf(row);
  if (idx < 0) return;

  try {
    const result = await api("DELETE", `/conversations/${state.activeId}/messages/${idx}`);
    // Update state
    const ci = state.convs.findIndex(c => c.id === state.activeId);
    if (ci >= 0) state.convs[ci].messages = result.messages;
    row.remove();
  } catch (e) {
    alert("Lỗi khi xóa: " + e.message);
  }
}

// ── Send ───────────────────────────────────────────────────────────────────
async function sendMessage() {
  if (state.sending || !state.activeId) return;
  const input = document.getElementById("msg-input");
  const text  = input.value.trim();
  if (!text) return;

  input.value   = "";
  input.style.height = "";
  state.sending = true;
  document.getElementById("send-btn").disabled = true;

  const conv = state.convs.find(c => c.id === state.activeId);
  const msgIdx = (conv?.messages?.length || 0);

  // Update title on first message
  if (!conv?.messages?.length) {
    const title = text.slice(0, 40) + (text.length > 40 ? "…" : "");
    document.getElementById("header-title").textContent = title;
    api("PATCH", `/conversations/${state.activeId}/rename`, { title }).catch(() => {});
  }

  appendMessage("user", text, msgIdx);
  showTyping();

  try {
    const res = await api("POST", "/chat/send", {
      conv_id: state.activeId,
      message: text,
      model:   state.config.model,
    });

    hideTyping();
    appendMessage("assistant", res.reply, msgIdx + 1);

    // Sync messages in state
    const ci = state.convs.findIndex(c => c.id === state.activeId);
    if (ci >= 0) state.convs[ci].messages = res.messages;

    // Update title in list (auto-titled by server)
    state.convs = await api("GET", "/conversations");
    renderConvList();
  } catch (e) {
    hideTyping();
    appendMessage("assistant", "❌ Lỗi: " + e.message, msgIdx + 1);
  }

  state.sending = false;
  document.getElementById("send-btn").disabled = false;
  document.getElementById("msg-input").focus();
}

function showTyping() {
  let row = document.getElementById("typing-row");
  if (!row) {
    row = document.createElement("div");
    row.id = "typing-row";
    row.className = "msg-row bot";
    row.innerHTML = `<div class="msg-avatar">✦</div><div class="typing-bubble">●●●</div>`;
    document.getElementById("chat-messages").appendChild(row);
  }
  row.style.display = "flex";
  scrollBottom();
}

function hideTyping() {
  const row = document.getElementById("typing-row");
  if (row) row.remove();
}

// ── Config / Settings ──────────────────────────────────────────────────────
function updateModelBtn() {
  const m = state.config.model || "";
  document.getElementById("model-btn").textContent = `⚡ ${m} ▾`;
}

function updateHeaderBadge() {
  const p = (state.config.provider || "").split(" (")[0];
  const m = state.config.model || "";
  document.getElementById("header-model-badge").textContent = `${p} · ${m}`;
}

function populateProviders() {
  const sel = document.getElementById("cfg-provider");
  sel.innerHTML = "";
  Object.keys(state.config.providers || {}).forEach(name => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    if (name === state.config.provider) opt.selected = true;
    sel.appendChild(opt);
  });
  sel.addEventListener("change", () => {
    const preset = state.config.providers[sel.value];
    if (preset) document.getElementById("cfg-baseurl").value = preset.base_url;
  });
}

async function saveSettings() {
  const provider = document.getElementById("cfg-provider").value;
  const apiKey   = document.getElementById("cfg-apikey").value.trim();
  const baseUrl  = document.getElementById("cfg-baseurl").value.trim();
  await api("PATCH", "/config", { provider, api_key: apiKey, base_url: baseUrl });
  state.config = await api("GET", "/config");
  updateModelBtn();
  updateHeaderBadge();
  document.getElementById("settings-modal").classList.add("hidden");
}

// ── Model picker ───────────────────────────────────────────────────────────
function showModelMenu(anchor) {
  const menu    = document.getElementById("model-menu");
  const models  = state.config.providers?.[state.config.provider]?.models || [];
  menu.innerHTML = "";
  models.forEach(m => {
    const item = document.createElement("div");
    item.className = "dropdown-item";
    item.textContent = m;
    item.addEventListener("click", async () => {
      state.config.model = m;
      await api("PATCH", "/config", { model: m });
      updateModelBtn();
      updateHeaderBadge();
      menu.classList.add("hidden");
    });
    menu.appendChild(item);
  });

  const rect = anchor.getBoundingClientRect();
  menu.style.left   = rect.left + "px";
  menu.style.bottom = (window.innerHeight - rect.top + 4) + "px";
  menu.classList.remove("hidden");
}

// ── Color picker ───────────────────────────────────────────────────────────
function renderColorGrid() {
  const grid = document.getElementById("color-grid");
  grid.innerHTML = "";
  AVATAR_COLORS.forEach(c => {
    const sw = document.createElement("div");
    sw.className = "color-swatch";
    sw.style.background = c;
    sw.addEventListener("click", async () => {
      if (!state.colorTarget) return;
      await api("PATCH", `/conversations/${state.colorTarget}/avatar`, { color: c });
      state.convs = await api("GET", "/conversations");
      renderConvList();
      document.getElementById("color-modal").classList.add("hidden");
    });
    grid.appendChild(sw);
  });
}

// ── Utilities ──────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function scrollBottom() {
  const el = document.getElementById("chat-messages");
  requestAnimationFrame(() => { el.scrollTop = el.scrollHeight; });
}

// ── Event Listeners ────────────────────────────────────────────────────────
document.getElementById("new-chat-btn").addEventListener("click", newChat);

document.getElementById("search-input").addEventListener("input", renderConvList);

document.getElementById("msg-input").addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
document.getElementById("msg-input").addEventListener("input", function() {
  this.style.height = "auto";
  this.style.height = Math.min(this.scrollHeight, 150) + "px";
});

document.getElementById("send-btn").addEventListener("click", sendMessage);

document.getElementById("model-btn").addEventListener("click", function(e) {
  e.stopPropagation();
  showModelMenu(this);
});

document.addEventListener("click", () => {
  document.getElementById("model-menu").classList.add("hidden");
});

document.getElementById("settings-btn").addEventListener("click", () => {
  document.getElementById("cfg-apikey").value = "";
  const ind = document.getElementById("cfg-env-indicator");
  ind.textContent = state.config.key_from_env ? "✓ Key loaded from .env" : "";
  ind.style.color = "#25d366";
  document.getElementById("cfg-baseurl").value = state.config.base_url || "";
  document.getElementById("settings-modal").classList.remove("hidden");
});

document.getElementById("settings-save").addEventListener("click", saveSettings);
document.getElementById("settings-cancel").addEventListener("click", () => {
  document.getElementById("settings-modal").classList.add("hidden");
});

document.getElementById("rename-save").addEventListener("click", async () => {
  const title = document.getElementById("rename-input").value.trim();
  if (!title || !state.renameTarget) return;
  await api("PATCH", `/conversations/${state.renameTarget}/rename`, { title });
  state.convs = await api("GET", "/conversations");
  if (state.renameTarget === state.activeId) {
    document.getElementById("header-title").textContent = title;
  }
  renderConvList();
  document.getElementById("rename-modal").classList.add("hidden");
});
document.getElementById("rename-cancel").addEventListener("click", () => {
  document.getElementById("rename-modal").classList.add("hidden");
});
document.getElementById("rename-input").addEventListener("keydown", e => {
  if (e.key === "Enter") document.getElementById("rename-save").click();
  if (e.key === "Escape") document.getElementById("rename-cancel").click();
});

document.getElementById("color-cancel").addEventListener("click", () => {
  document.getElementById("color-modal").classList.add("hidden");
});

// Close modals on backdrop click
document.querySelectorAll(".modal").forEach(m => {
  m.addEventListener("click", e => {
    if (e.target === m) m.classList.add("hidden");
  });
});

// ── Init ───────────────────────────────────────────────────────────────────
renderColorGrid();
boot();
