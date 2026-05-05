import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file (nếu có) — override bởi config.json, nhưng env vars → priority cao nhất
_ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(_ENV_FILE, override=False)  # không ghi đè biến đã set trong shell

# ── Config ──────────────────────────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

# ── Provider presets ────────────────────────────────────────────────────────
PROVIDERS = {
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "MiMo (Pay-As-You-Go)": {
        "base_url": "https://api.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
        "models": ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-omni"],
    },
    "MiMo (Token Plan — SG)": {
        "base_url": "https://token-plan-sgp.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
        "models": ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-omni"],
    },
    "MiMo (Token Plan — EU)": {
        "base_url": "https://token-plan-ams.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
        "models": ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-omni"],
    },
    "MiMo (Token Plan — CN)": {
        "base_url": "https://token-plan-cn.xiaomimimo.com/v1",
        "default_model": "mimo-v2.5-pro",
        "models": ["mimo-v2.5-pro", "mimo-v2-pro", "mimo-omni"],
    },
}

def load_config():
    """Load config: file JSON là base, env vars ghi đè lên trên."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
    else:
        cfg = {
            "api_key": "",
            "provider": "OpenAI",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini",
            "system_prompt": "You are a helpful assistant.",
        }

    # Env vars có priority cao nhất
    mimo_key   = os.getenv("MIMO_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # Auto-detect provider: nếu chỉ có MIMO_API_KEY → tự chuyển sang MiMo
    if os.getenv("PROVIDER"):
        provider = os.getenv("PROVIDER")
    elif mimo_key and not openai_key:
        provider = "MiMo (Pay-As-You-Go)"          # auto-detect
        cfg["base_url"] = PROVIDERS["MiMo (Pay-As-You-Go)"]["base_url"]
        if not cfg.get("model") or cfg.get("model", "").startswith("gpt-"):
            cfg["model"] = "mimo-v2.5-pro"
    elif openai_key and not mimo_key:
        provider = "OpenAI"
    else:
        provider = cfg.get("provider", "OpenAI")

    # Chọn key phù hợp với provider
    if "MiMo" in provider:
        env_key = mimo_key or openai_key or cfg.get("api_key", "")
    else:
        env_key = openai_key or mimo_key or cfg.get("api_key", "")

    cfg["api_key"]  = env_key
    cfg["provider"] = provider
    if os.getenv("BASE_URL"):
        cfg["base_url"] = os.getenv("BASE_URL")
    if os.getenv("MODEL"):
        cfg["model"] = os.getenv("MODEL")

    # Đánh dấu key đến từ env
    cfg["_key_from_env"] = bool(mimo_key or openai_key)
    return cfg

def save_config(cfg):
    # Không lưu api_key nếu nó đến từ .env — giữ config.json sạch
    to_save = {k: v for k, v in cfg.items() if not k.startswith("_")}
    if cfg.get("_key_from_env"):
        to_save["api_key"] = ""  # giữ trống, key thật nằm trong .env
    with open(CONFIG_FILE, "w") as f:
        json.dump(to_save, f, indent=2)

# ── Color Palette ────────────────────────────────────────────────────────────
BG_DARK      = "#0f0f13"
BG_PANEL     = "#16161e"
BG_INPUT     = "#1e1e2a"
BG_MSG_USER  = "#6c63ff"
BG_MSG_BOT   = "#1e1e2e"
ACCENT       = "#6c63ff"
ACCENT2      = "#a78bfa"
TEXT_PRIMARY = "#e2e2f0"
TEXT_MUTED   = "#6b6b8a"
TEXT_WHITE   = "#ffffff"
BORDER       = "#2a2a3e"
SUCCESS      = "#34d399"
ERROR        = "#f87171"

FONT_FAMILY  = "Segoe UI"   # fallback to system sans-serif on Linux

# ── Rounded Button (Canvas-based) ─────────────────────────────────────────────
class RoundedButton(tk.Canvas):
    """A button with rounded corners drawn on a Canvas."""
    def __init__(self, parent, text, command=None, radius=10,
                 bg=None, fg=TEXT_WHITE, hover_bg=None,
                 font_spec=None, padx=18, pady=8, **kwargs):
        bg       = bg       or ACCENT
        hover_bg = hover_bg or self._darken(bg)
        font_spec = font_spec or (FONT_FAMILY, 10, "bold")

        # Measure text size
        tmp = tk.Label(parent, text=text, font=font_spec)
        tmp.update_idletasks()
        tw = tmp.winfo_reqwidth()
        th = tmp.winfo_reqheight()
        tmp.destroy()

        w = tw + padx * 2
        h = th + pady * 2

        parent_bg = parent.cget("bg") if hasattr(parent, 'cget') else BG_DARK
        super().__init__(parent, width=w, height=h,
                         highlightthickness=0, bd=0, bg=parent_bg, **kwargs)

        self._bg      = bg
        self._hbg     = hover_bg
        self._fg      = fg
        self._text    = text
        self._font    = font_spec
        self._r       = radius
        self._width   = w
        self._height  = h
        self._cmd     = command
        self._active  = False

        self._draw(bg)
        self.bind("<Enter>",    lambda e: self._draw(hover_bg))
        self.bind("<Leave>",    lambda e: self._draw(bg))
        self.bind("<Button-1>", self._on_click)
        self.configure(cursor="hand2")

    @staticmethod
    def _darken(hex_color):
        """Darken a hex color by ~15%."""
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        r, g, b = max(0,int(r*0.85)), max(0,int(g*0.85)), max(0,int(b*0.85))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self, color):
        self.delete("all")
        r, w, h = self._r, self._width, self._height
        # Four arcs + two rects = filled rounded rectangle
        items = []
        items.append(self.create_arc(0,   0,   r*2, r*2, start=90,  extent=90, fill=color, outline=""))
        items.append(self.create_arc(w-r*2, 0, w,   r*2, start=0,   extent=90, fill=color, outline=""))
        items.append(self.create_arc(0, h-r*2, r*2, h,   start=180, extent=90, fill=color, outline=""))
        items.append(self.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=color, outline=""))
        items.append(self.create_rectangle(r, 0,   w-r, h,   fill=color, outline=""))
        items.append(self.create_rectangle(0, r,   w,   h-r, fill=color, outline=""))
        items.append(self.create_text(w//2, h//2, text=self._text, fill=self._fg, font=self._font))
        
        # Bind click to all items just in case
        for item in items:
            self.tag_bind(item, "<Button-1>", self._on_click)

    def _on_click(self, _):
        if self._cmd:
            self._cmd()

# ── Main App ─────────────────────────────────────────────────────────────────
class ChatbotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config_data = load_config()
        self.conversation: list[dict] = []
        self.is_thinking = False

        self._setup_window()
        self._build_ui()
        self._apply_theme()

        # Auto-focus input
        self.input_box.focus_set()

    # ── Window setup ─────────────────────────────────────────────────────────
    def _setup_window(self):
        self.title("AI Chatbot")
        self.geometry("860x680")
        self.minsize(600, 480)
        self.configure(bg=BG_DARK)

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 860) // 2
        y = (self.winfo_screenheight() - 680) // 2
        self.geometry(f"860x680+{x}+{y}")

        # Icon (colored title bar on some WMs)
        self.iconname("AI Chatbot")

    # ── UI Construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Top bar ──────────────────────────────────────────────────────────
        topbar = tk.Frame(self, bg=BG_PANEL, height=56)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(
            topbar, text="✦  AI Chatbot", font=(FONT_FAMILY, 15, "bold"),
            fg=ACCENT2, bg=BG_PANEL
        ).pack(side="left", padx=20, pady=12)

        # Provider badge
        provider = self.config_data.get("provider", "OpenAI")
        provider_color = "#f97316" if "MiMo" in provider else ACCENT
        self.provider_label = tk.Label(
            topbar, text=f"  {provider.split(' (')[0]}  ",
            font=(FONT_FAMILY, 9), fg=TEXT_WHITE, bg=provider_color,
            relief="flat", padx=4, pady=2
        )
        self.provider_label.pack(side="left", padx=(0, 4), pady=18)

        # Model badge
        self.model_label = tk.Label(
            topbar, text=f"  {self.config_data.get('model','gpt-4o-mini')}  ",
            font=(FONT_FAMILY, 9), fg=TEXT_WHITE, bg=BG_INPUT,
            relief="flat", padx=4, pady=2
        )
        self.model_label.pack(side="left", padx=0, pady=18)

        # Settings button
        RoundedButton(
            topbar, text="⚙  Settings", command=self._open_settings,
            bg=BG_INPUT, fg=TEXT_MUTED, hover_bg=BORDER,
            font_spec=(FONT_FAMILY, 9), padx=12, pady=5, radius=8
        ).pack(side="right", padx=12, pady=10)

        # Clear button
        RoundedButton(
            topbar, text="✕  Clear", command=self._clear_chat,
            bg=BG_INPUT, fg=TEXT_MUTED, hover_bg="#3a1a1a",
            font_spec=(FONT_FAMILY, 9), padx=12, pady=5, radius=8
        ).pack(side="right", padx=4, pady=10)

        # Thin accent line under top bar
        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x")

        # ── Chat area ────────────────────────────────────────────────────────
        chat_outer = tk.Frame(self, bg=BG_DARK)
        chat_outer.pack(fill="both", expand=True, padx=0, pady=0)

        self.chat_canvas = tk.Canvas(
            chat_outer, bg=BG_DARK, highlightthickness=0, bd=0
        )
        scrollbar = tk.Scrollbar(
            chat_outer, orient="vertical", command=self.chat_canvas.yview,
            bg=BG_PANEL, troughcolor=BG_DARK, activebackground=ACCENT
        )
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.chat_canvas.pack(side="left", fill="both", expand=True)

        self.messages_frame = tk.Frame(self.chat_canvas, bg=BG_DARK)
        self.canvas_window = self.chat_canvas.create_window(
            (0, 0), window=self.messages_frame, anchor="nw"
        )

        self.messages_frame.bind("<Configure>", self._on_frame_configure)
        self.chat_canvas.bind("<Configure>", self._on_canvas_configure)
        self.chat_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.chat_canvas.bind_all("<Button-4>",   self._on_mousewheel)
        self.chat_canvas.bind_all("<Button-5>",   self._on_mousewheel)

        # Welcome message
        self._add_welcome()

        # ── Bottom input area ─────────────────────────────────────────────────
        bottom = tk.Frame(self, bg=BG_PANEL, pady=12)
        bottom.pack(fill="x", side="bottom")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", side="bottom")

        input_row = tk.Frame(bottom, bg=BG_PANEL)
        input_row.pack(fill="x", padx=16)

        input_container = tk.Frame(
            input_row, bg=BG_INPUT,
            highlightbackground=BORDER, highlightthickness=1
        )
        input_container.pack(side="left", fill="x", expand=True)

        self.input_box = tk.Text(
            input_container, height=3, font=(FONT_FAMILY, 11),
            fg=TEXT_PRIMARY, bg=BG_INPUT, insertbackground=ACCENT2,
            relief="flat", padx=12, pady=10, wrap="word",
            highlightthickness=0
        )
        self.input_box.pack(fill="both", expand=True)
        self.input_box.bind("<Return>",       self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)
        self.input_box.bind("<FocusIn>",      lambda e: input_container.config(highlightbackground=ACCENT))
        self.input_box.bind("<FocusOut>",     lambda e: input_container.config(highlightbackground=BORDER))


        send_btn = RoundedButton(
            input_row, text="Send  ▶", command=self._send_message,
            bg=ACCENT, fg=TEXT_WHITE, hover_bg="#5a52e0",
            font_spec=(FONT_FAMILY, 11, "bold"), padx=22, pady=10, radius=10
        )
        send_btn.pack(side="left", padx=(10, 0))

        tk.Label(
            bottom, text="Enter to send  ·  Shift+Enter for new line",
            font=(FONT_FAMILY, 8), fg=TEXT_MUTED, bg=BG_PANEL
        ).pack(pady=(4, 0))

    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")

    # ── Welcome message ───────────────────────────────────────────────────────
    def _add_welcome(self):
        frame = tk.Frame(self.messages_frame, bg=BG_DARK)
        frame.pack(fill="x", padx=40, pady=32)

        tk.Label(
            frame, text="✦", font=(FONT_FAMILY, 28), fg=ACCENT, bg=BG_DARK
        ).pack()
        tk.Label(
            frame, text="Xin chào! Tôi có thể giúp gì cho bạn?",
            font=(FONT_FAMILY, 14, "bold"), fg=TEXT_PRIMARY, bg=BG_DARK
        ).pack(pady=(8, 4))
        tk.Label(
            frame, text="Hỏi bất cứ điều gì — tôi ở đây để hỗ trợ bạn.",
            font=(FONT_FAMILY, 10), fg=TEXT_MUTED, bg=BG_DARK
        ).pack()

    # ── Message rendering ─────────────────────────────────────────────────────
    def _add_message(self, role: str, text: str):
        is_user = role == "user"
        outer = tk.Frame(self.messages_frame, bg=BG_DARK)
        outer.pack(fill="x", padx=20, pady=6)

        row = tk.Frame(outer, bg=BG_DARK)
        row.pack(anchor="e" if is_user else "w")

        if not is_user:
            avatar = tk.Label(
                row, text="✦", font=(FONT_FAMILY, 12), fg=ACCENT2,
                bg=BG_MSG_BOT, width=3, pady=6
            )
            avatar.pack(side="left", anchor="n", padx=(0, 4))

        bubble_color = BG_MSG_USER if is_user else BG_MSG_BOT
        bubble = tk.Frame(
            row, bg=bubble_color,
            highlightbackground=ACCENT if is_user else BORDER,
            highlightthickness=1
        )
        bubble.pack(side="left" if not is_user else "right")

        msg_text = tk.Text(
            bubble, font=(FONT_FAMILY, 10), fg=TEXT_WHITE if is_user else TEXT_PRIMARY,
            bg=bubble_color, relief="flat", wrap="word",
            padx=14, pady=10, cursor="arrow",
            highlightthickness=0, borderwidth=0
        )
        msg_text.insert("1.0", text)
        msg_text.config(state="disabled")

        # Auto-size height
        lines = text.count("\n") + 1
        chars_per_line = 55
        estimated_lines = max(lines, sum(len(p)//chars_per_line + 1 for p in text.split("\n")))
        msg_text.config(height=min(estimated_lines, 30), width=55)
        msg_text.pack()

        # Timestamp
        ts = datetime.now().strftime("%H:%M")
        tk.Label(
            outer, text=ts, font=(FONT_FAMILY, 7), fg=TEXT_MUTED, bg=BG_DARK
        ).pack(anchor="e" if is_user else "w", padx=8)

        self._scroll_to_bottom()
        return outer

    def _add_typing_indicator(self):
        frame = tk.Frame(self.messages_frame, bg=BG_DARK)
        frame.pack(fill="x", padx=24, pady=6, anchor="w")

        bubble = tk.Frame(frame, bg=BG_MSG_BOT, highlightbackground=BORDER, highlightthickness=1)
        bubble.pack(anchor="w")

        self._dot_label = tk.Label(
            bubble, text="● ● ●", font=(FONT_FAMILY, 10),
            fg=ACCENT2, bg=BG_MSG_BOT, padx=16, pady=10
        )
        self._dot_label.pack()
        self._typing_frame = frame
        self._animate_dots()
        self._scroll_to_bottom()
        return frame

    def _animate_dots(self, step=0):
        if not hasattr(self, "_typing_frame") or not self._typing_frame.winfo_exists():
            return
        dots = ["●  ○  ○", "●  ●  ○", "●  ●  ●", "○  ●  ●", "○  ○  ●"]
        self._dot_label.config(text=dots[step % len(dots)])
        self._anim_id = self.after(280, self._animate_dots, step + 1)

    def _remove_typing_indicator(self):
        if hasattr(self, "_anim_id"):
            self.after_cancel(self._anim_id)
        if hasattr(self, "_typing_frame"):
            self._typing_frame.destroy()

    # ── Send logic ────────────────────────────────────────────────────────────
    def _on_enter(self, event):
        if not (event.state & 0x1):   # Shift not held
            self._send_message()
            return "break"

    def _send_message(self):
        print("DEBUG: Send clicked")
        if self.is_thinking:
            print("DEBUG: is_thinking -> return")
            return
        raw = self.input_box.get("1.0", "end-1c").strip()
        print(f"DEBUG: raw='{raw}'")
        if not raw:
            print("DEBUG: empty raw -> return")
            return

        # Check API key
        api_key = self.config_data.get("api_key", "").strip()
        if not api_key:
            self._add_message("assistant", "⚠️  Chưa có API key. Vui lòng vào ⚙ Settings để chọn provider và thêm API key.")
            return

        self.input_box.delete("1.0", "end")

        self._add_message("user", raw)
        self.conversation.append({"role": "user", "content": raw})
        self.is_thinking = True
        self._add_typing_indicator()

        threading.Thread(target=self._call_api, args=(raw,), daemon=True).start()

    def _call_api(self, user_text: str):
        try:
            base_url = self.config_data.get("base_url", "").strip() or None
            client = OpenAI(
                api_key=self.config_data["api_key"],
                base_url=base_url,
            )
            messages = [
                {"role": "system", "content": self.config_data.get("system_prompt", "You are a helpful assistant.")}
            ] + self.conversation

            response = client.chat.completions.create(
                model=self.config_data.get("model", "gpt-4o-mini"),
                messages=messages,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            self.conversation.append({"role": "assistant", "content": reply})
            self.after(0, self._on_reply, reply)
        except Exception as e:
            self.after(0, self._on_reply, f"❌ Lỗi: {str(e)}", is_error=True)

    def _on_reply(self, text: str, is_error=False):
        self._remove_typing_indicator()
        self.is_thinking = False
        self._add_message("assistant", text)

    # ── Settings dialog ───────────────────────────────────────────────────────
    def _open_settings(self):
        win = tk.Toplevel(self)
        win.title("Settings")
        win.geometry("560x480")
        win.configure(bg=BG_DARK)
        win.grab_set()
        win.resizable(False, False)

        # Center
        win.update_idletasks()
        x = self.winfo_x() + (860 - 560) // 2
        y = self.winfo_y() + (680 - 480) // 2
        win.geometry(f"560x480+{x}+{y}")

        tk.Label(win, text="⚙  Settings", font=(FONT_FAMILY, 14, "bold"),
                 fg=ACCENT2, bg=BG_DARK).pack(pady=(20, 4))
        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=20, pady=8)

        def entry_row(label, default, show=None):
            f = tk.Frame(win, bg=BG_DARK)
            f.pack(fill="x", padx=24, pady=5)
            tk.Label(f, text=label, font=(FONT_FAMILY, 10), fg=TEXT_MUTED,
                     bg=BG_DARK, width=14, anchor="w").pack(side="left")
            e = tk.Entry(f, font=(FONT_FAMILY, 10), fg=TEXT_PRIMARY, bg=BG_INPUT,
                         insertbackground=ACCENT2, relief="flat",
                         highlightbackground=BORDER, highlightthickness=1,
                         show=show)
            e.insert(0, default)
            e.pack(side="left", fill="x", expand=True, ipady=6, padx=(8, 0))
            return e

        # ── Provider dropdown ─────────────────────────────────────────────────
        prow = tk.Frame(win, bg=BG_DARK)
        prow.pack(fill="x", padx=24, pady=5)
        tk.Label(prow, text="Provider", font=(FONT_FAMILY, 10), fg=TEXT_MUTED,
                 bg=BG_DARK, width=14, anchor="w").pack(side="left")

        provider_var = tk.StringVar(value=self.config_data.get("provider", "OpenAI"))
        provider_menu = ttk.Combobox(
            prow, textvariable=provider_var,
            values=list(PROVIDERS.keys()),
            font=(FONT_FAMILY, 10), state="readonly", width=30
        )
        provider_menu.pack(side="left", padx=(8, 0), ipady=4)

        api_entry   = entry_row("API Key", self.config_data.get("api_key", ""), show="•")

        # .env status badge
        key_from_env = self.config_data.get("_key_from_env", False)
        env_badge_frame = tk.Frame(win, bg=BG_DARK)
        env_badge_frame.pack(fill="x", padx=38, pady=(0, 4))
        if key_from_env:
            tk.Label(
                env_badge_frame, text="✓  Key đang được load từ .env",
                font=(FONT_FAMILY, 8), fg=SUCCESS, bg=BG_DARK
            ).pack(side="left")
        else:
            tk.Label(
                env_badge_frame, text="⚠  Chưa có key trong .env — đang dùng key nhập tay",
                font=(FONT_FAMILY, 8), fg="#fbbf24", bg=BG_DARK
            ).pack(side="left")

        base_entry  = entry_row("Base URL", self.config_data.get("base_url", ""))
        model_entry = entry_row("Model",   self.config_data.get("model", "gpt-4o-mini"))


        # ── Model quick-select ────────────────────────────────────────────────
        model_hint_frame = tk.Frame(win, bg=BG_DARK)
        model_hint_frame.pack(fill="x", padx=38, pady=(0, 6))
        self._model_btns = []

        def refresh_provider_ui(*_):
            p = provider_var.get()
            preset = PROVIDERS.get(p, {})
            # Update base URL
            base_entry.delete(0, "end")
            base_entry.insert(0, preset.get("base_url", ""))
            # Clear model hint buttons
            for b in model_hint_frame.winfo_children():
                b.destroy()
            tk.Label(model_hint_frame, text="Quick:", font=(FONT_FAMILY, 8),
                     fg=TEXT_MUTED, bg=BG_DARK).pack(side="left", padx=(0, 4))
            for m in preset.get("models", []):
                btn = tk.Button(
                    model_hint_frame, text=m, font=(FONT_FAMILY, 8),
                    fg=ACCENT2, bg=BG_INPUT, relief="flat", cursor="hand2",
                    activeforeground=TEXT_WHITE, activebackground=ACCENT,
                    command=lambda v=m: [model_entry.delete(0, "end"), model_entry.insert(0, v)]
                )
                btn.pack(side="left", padx=2)

        provider_var.trace_add("write", refresh_provider_ui)
        refresh_provider_ui()  # populate on open

        # ── System Prompt ─────────────────────────────────────────────────────
        tk.Label(win, text="System Prompt", font=(FONT_FAMILY, 10),
                 fg=TEXT_MUTED, bg=BG_DARK).pack(anchor="w", padx=24, pady=(4, 2))
        sp_box = tk.Text(win, height=4, font=(FONT_FAMILY, 10), fg=TEXT_PRIMARY,
                         bg=BG_INPUT, relief="flat", padx=8, pady=6,
                         highlightbackground=BORDER, highlightthickness=1,
                         insertbackground=ACCENT2)
        sp_box.insert("1.0", self.config_data.get("system_prompt", "You are a helpful assistant."))
        sp_box.pack(fill="x", padx=24)

        def save():
            p = provider_var.get()
            self.config_data["provider"]      = p
            self.config_data["api_key"]       = api_entry.get().strip()
            self.config_data["base_url"]      = base_entry.get().strip()
            self.config_data["model"]         = model_entry.get().strip()
            self.config_data["system_prompt"] = sp_box.get("1.0", "end-1c").strip()
            save_config(self.config_data)
            self.model_label.config(text=f"  {self.config_data['model']}  ")
            pcolor = "#f97316" if "MiMo" in p else ACCENT
            self.provider_label.config(
                text=f"  {p.split(' (')[0]}  ", bg=pcolor
            )
            win.destroy()

        btn_row = tk.Frame(win, bg=BG_DARK)
        btn_row.pack(pady=14)

        RoundedButton(btn_row, text="Save", command=save,
                      bg=ACCENT, fg=TEXT_WHITE, hover_bg="#5a52e0",
                      font_spec=(FONT_FAMILY, 10, "bold"), padx=24, pady=7, radius=10
                      ).pack(side="left", padx=8)
        RoundedButton(btn_row, text="Cancel", command=win.destroy,
                      bg=BG_INPUT, fg=TEXT_MUTED, hover_bg=BORDER,
                      font_spec=(FONT_FAMILY, 10), padx=24, pady=7, radius=10
                      ).pack(side="left")

    # ── Clear chat ────────────────────────────────────────────────────────────
    def _clear_chat(self):
        self.conversation.clear()
        for w in self.messages_frame.winfo_children():
            w.destroy()
        self._add_welcome()



    # ── Canvas / scroll helpers ───────────────────────────────────────────────
    def _on_frame_configure(self, event=None):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.chat_canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.chat_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.chat_canvas.yview_scroll(1, "units")
        else:
            self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_to_bottom(self):
        self.after(50, lambda: self.chat_canvas.yview_moveto(1.0))


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ChatbotApp()
    app.mainloop()
