# ── Messenger Dark Navy Palette ───────────────────────────────────────────────
BG_NAV         = "#0e1117"   # Leftmost icon nav column
BG_SIDEBAR     = "#13151c"   # Conversation list panel
BG_SIDEBAR_HOV = "#1e2230"
BG_ACTIVE      = "#1e2330"
BG_CHAT        = "#0e1117"   # Main chat background
BG_BUBBLE_USER = "#4f6ef7"   # Vibrant blue — user messages
BG_BUBBLE_BOT  = "#1e2533"   # Dark slate — bot messages
BG_INPUT       = "#1a1d27"   # Input pill background
BG_HEADER      = "#13151c"
ACCENT         = "#4f6ef7"
ACCENT_HOVER   = "#3d5ce5"
ACCENT2        = "#6c84f8"
ACCENT_BAR     = "#4f6ef7"   # Left active-conv highlight bar
TEXT_PRIMARY   = "#e4e6f0"
TEXT_SECONDARY = "#8b90a7"
TEXT_MUTED     = "#545872"
TEXT_WHITE     = "#ffffff"
BORDER         = "#1e2230"
SUCCESS        = "#25d366"   # Online green
ERROR          = "#ff4d4f"

# ── Global QSS ────────────────────────────────────────────────────────────────
GLOBAL_STYLE = f"""
* {{
    font-family: 'Segoe UI', 'Inter', 'SF Pro Display', sans-serif;
    color: {TEXT_PRIMARY};
    border: none;
    outline: none;
    margin: 0;
    padding: 0;
}}

QMainWindow, QDialog {{
    background-color: {BG_CHAT};
}}

QWidget {{
    background-color: transparent;
}}

/* ── Icon Nav (leftmost column) ── */
#icon_nav {{
    background-color: {BG_NAV};
    border-right: 1px solid {BORDER};
}}

#nav_icon_btn {{
    background-color: transparent;
    color: {TEXT_SECONDARY};
    border-radius: 22px;
    font-size: 18px;
    padding: 4px;
    min-width: 44px;
    min-height: 44px;
    max-width: 44px;
    max-height: 44px;
}}
#nav_icon_btn:hover {{
    background-color: {BG_SIDEBAR_HOV};
    color: {TEXT_PRIMARY};
}}
#nav_icon_btn_active {{
    background-color: {BG_ACTIVE};
    color: {ACCENT};
    border-radius: 22px;
    font-size: 18px;
    padding: 4px;
    min-width: 44px;
    min-height: 44px;
    max-width: 44px;
    max-height: 44px;
}}

/* ── Sidebar ── */
#sidebar {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid {BORDER};
}}
#sidebar_title {{
    font-size: 22px;
    font-weight: 800;
    color: {TEXT_PRIMARY};
    background: transparent;
}}
#new_conv_btn {{
    background-color: {BG_ACTIVE};
    color: {ACCENT};
    border-radius: 20px;
    font-size: 16px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-weight: 700;
}}
#new_conv_btn:hover {{
    background-color: #252a3e;
}}
#search_box {{
    background-color: {BG_ACTIVE};
    border-radius: 20px;
    padding: 8px 16px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    min-height: 36px;
}}

/* ── Conv items ── */
#conv_item_active {{
    background-color: {BG_ACTIVE};
    border-radius: 10px;
    border-left: 3px solid {ACCENT_BAR};
}}
#conv_item {{
    background-color: transparent;
    border-radius: 10px;
    border-left: 3px solid transparent;
}}
#conv_item:hover {{
    background-color: {BG_SIDEBAR_HOV};
}}
#conv_name {{
    font-size: 13px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    background: transparent;
}}
#conv_preview {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
    background: transparent;
}}
#conv_time {{
    font-size: 11px;
    color: {TEXT_MUTED};
    background: transparent;
}}
#delete_btn {{
    background: transparent;
    color: {TEXT_MUTED};
    font-size: 11px;
    border-radius: 12px;
    min-width: 22px;
    max-width: 22px;
    min-height: 22px;
    max-height: 22px;
}}
#delete_btn:hover {{
    background: #3a1a1a;
    color: #ff6b6b;
}}

/* ── Bottom sidebar actions ── */
#sidebar_action_btn {{
    background: transparent;
    color: {TEXT_SECONDARY};
    text-align: left;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 13px;
}}
#sidebar_action_btn:hover {{
    background: {BG_SIDEBAR_HOV};
    color: {TEXT_PRIMARY};
}}

/* ── Chat Header ── */
#chat_header {{
    background-color: {BG_HEADER};
    border-bottom: 1px solid {BORDER};
}}
#chat_title {{
    font-size: 15px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
    background: transparent;
}}
#chat_online {{
    font-size: 12px;
    font-weight: 600;
    color: {SUCCESS};
    background: transparent;
}}
#header_model_lbl {{
    font-size: 11px;
    color: {TEXT_MUTED};
    background: transparent;
    padding: 4px 10px;
    border-radius: 10px;
    background-color: {BG_ACTIVE};
}}

/* ── Chat Area ── */
#chat_scroll {{
    background-color: {BG_CHAT};
    border: none;
}}
#date_pill {{
    background-color: {BG_ACTIVE};
    color: {TEXT_MUTED};
    border-radius: 12px;
    padding: 4px 14px;
    font-size: 11px;
    font-weight: 600;
}}

/* ── Input Area ── */
#input_wrapper {{
    background-color: {BG_HEADER};
    border-top: 1px solid {BORDER};
}}
#input_pill {{
    background-color: {BG_INPUT};
    border-radius: 24px;
    border: 1px solid {BORDER};
    min-height: 48px;
}}
#chat_input {{
    background-color: transparent;
    color: {TEXT_PRIMARY};
    font-size: 14px;
    padding: 0px 4px;
    border: none;
}}
#model_pill_btn {{
    background-color: transparent;
    color: {ACCENT};
    font-size: 12px;
    font-weight: 700;
    border-radius: 12px;
    padding: 3px 10px;
}}
#model_pill_btn:hover {{
    background-color: {BG_ACTIVE};
}}
#send_btn {{
    background-color: {ACCENT};
    border-radius: 22px;
    min-width: 44px;
    max-width: 44px;
    min-height: 44px;
    max-height: 44px;
    color: {TEXT_WHITE};
    font-size: 17px;
    font-weight: 900;
}}
#send_btn:hover {{
    background-color: {ACCENT_HOVER};
}}
#send_btn:disabled {{
    background-color: {BG_ACTIVE};
    color: {TEXT_MUTED};
}}
#hint_label {{
    color: {TEXT_MUTED};
    font-size: 11px;
    background: transparent;
}}

/* ── Settings Dialog ── */
QDialog {{
    background-color: {BG_SIDEBAR};
}}
QDialog QWidget {{
    background-color: transparent;
}}
QDialog QFrame {{
    background-color: transparent;
}}
#section_label {{
    color: {TEXT_MUTED};
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
    background: transparent;
}}
#dialog_title {{
    font-size: 18px;
    font-weight: 800;
    color: {TEXT_PRIMARY};
    background: transparent;
}}
QLineEdit {{
    background-color: {BG_ACTIVE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px 14px;
    color: {TEXT_PRIMARY};
    font-size: 14px;
    min-height: 20px;
}}
QLineEdit:focus {{
    border: 1px solid {ACCENT};
}}
QComboBox {{
    background-color: {BG_ACTIVE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px 14px;
    color: {TEXT_PRIMARY};
    font-size: 14px;
    min-height: 20px;
}}
QComboBox:focus {{
    border: 1px solid {ACCENT};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 30px;
    border: none;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_ACTIVE};
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
    border-radius: 8px;
    padding: 4px;
    border: 1px solid {BORDER};
}}
#dialog_primary {{
    background-color: {ACCENT};
    color: {TEXT_WHITE};
    border-radius: 10px;
    padding: 10px 28px;
    font-weight: 700;
    font-size: 14px;
    min-height: 40px;
}}
#dialog_primary:hover {{
    background-color: {ACCENT_HOVER};
}}
#dialog_cancel {{
    background-color: {BG_ACTIVE};
    color: {TEXT_SECONDARY};
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 14px;
    min-height: 40px;
}}
#dialog_cancel:hover {{
    background-color: {BG_SIDEBAR_HOV};
    color: {TEXT_PRIMARY};
}}

/* ── Scrollbar ── */
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}

/* ── Context Menu (model picker) ── */
QMenu {{
    background-color: {BG_ACTIVE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 6px;
}}
QMenu::item {{
    color: {TEXT_PRIMARY};
    padding: 9px 20px;
    border-radius: 7px;
    font-size: 13px;
}}
QMenu::item:selected {{ background-color: {ACCENT}; color: white; }}
"""
