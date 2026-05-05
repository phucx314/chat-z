import tkinter as tk

FONT_FAMILY = "Segoe UI"
TEXT_WHITE = "#ffffff"
BG_DARK = "#0f0f13"
ACCENT = "#6c63ff"
BG_INPUT = "#1e1e2a"
TEXT_MUTED = "#6b6b8a"
BORDER = "#2a2a3e"

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, radius=10,
                 bg=None, fg=TEXT_WHITE, hover_bg=None,
                 font_spec=None, padx=18, pady=8, **kwargs):
        bg       = bg       or ACCENT
        hover_bg = hover_bg or self._darken(bg)
        font_spec = font_spec or (FONT_FAMILY, 10, "bold")

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
        self._w       = w
        self._h       = h
        self._cmd     = command
        self._active  = False

        self._draw(bg)

    @staticmethod
    def _darken(hex_color):
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        r, g, b = max(0,int(r*0.85)), max(0,int(g*0.85)), max(0,int(b*0.85))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self, color):
        self.delete("all")

root = tk.Tk()
topbar = tk.Frame(root)
topbar.pack()
b = RoundedButton(
    topbar, text="⚙  Settings", command=lambda: None,
    bg=BG_INPUT, fg=TEXT_MUTED, hover_bg=BORDER,
    font_spec=(FONT_FAMILY, 9), padx=12, pady=5, radius=8
)
print("Widget name:", b._w)
