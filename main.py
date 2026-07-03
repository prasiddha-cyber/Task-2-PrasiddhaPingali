"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║          ENCRYPTION & DECRYPTION WORKBENCH — Cybersecurity Internship           ║
║                        Built by Pingali Prasiddha                               ║
║         Python 3 • CustomTkinter • OOP • Caesar Cipher • ROT13                 ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""
 
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import datetime
import os
import re
import threading
 
# ══════════════════════════════════════════════════════════════════════════════
#  CUSTOMTKINTER GLOBAL CONFIG
# ══════════════════════════════════════════════════════════════════════════════
 
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  THEME — All visual constants in one place
# ══════════════════════════════════════════════════════════════════════════════
 
class Theme:
    # ── Core palette ──────────────────────────────────────────────────────────
    BG_ROOT       = "#080D13"   # Deepest background — window root
    BG_SIDEBAR    = "#0D1117"   # Sidebar
    BG_MAIN       = "#080D13"   # Main content area
    BG_CARD       = "#0F1923"   # Card surface (glass base)
    BG_CARD2      = "#131E2B"   # Nested card / input background
    BG_INPUT      = "#0A1520"   # Text input background
    BG_HEADER     = "#0B1520"   # Header bar
    BORDER        = "#1E2D3D"   # Card border
    BORDER_ACCENT = "#00D9FF22" # Glowing accent border (translucent)
    SIDEBAR_SEP   = "#1A2535"   # Sidebar separator
 
    # ── Accent palette ────────────────────────────────────────────────────────
    ACCENT        = "#00D9FF"   # Cyan — primary
    ACCENT_DIM    = "#007A91"   # Dim cyan
    ACCENT_GLOW   = "#00D9FF18" # Very translucent, for glow borders
    SUCCESS       = "#3FB950"   # Green — decrypted / ok
    SUCCESS_DIM   = "#2A7A35"
    WARNING       = "#E3B341"   # Amber — ROT13 / caution
    WARNING_DIM   = "#9C7A2C"
    DANGER        = "#F85149"   # Red — clear / error
    DANGER_DIM    = "#A33530"
    PURPLE        = "#BC8CFF"   # Purple — export
    PURPLE_DIM    = "#7A5AAA"
    BLUE          = "#58A6FF"   # Blue — copy
 
    # ── Text ──────────────────────────────────────────────────────────────────
    TEXT_PRIMARY  = "#CDD9E5"
    TEXT_SECONDARY= "#6E7F8D"
    TEXT_MUTED    = "#3D5166"
    TEXT_ACCENT   = "#00D9FF"
 
    # ── Typography ────────────────────────────────────────────────────────────
    FONT_MONO     = ("Cascadia Code", 12)
    FONT_MONO_LG  = ("Cascadia Code", 14)
    FONT_MONO_SM  = ("Cascadia Code", 10)
    FONT_MONO_XL  = ("Cascadia Code", 22, "bold")

    FONT_SANS     = ("Segoe UI", 13)
    FONT_SANS_SM  = ("Segoe UI", 11)
    FONT_SANS_LG  = ("Segoe UI", 15)
    FONT_SANS_XL  = ("Bahnschrift SemiBold", 18)

    FONT_TITLE    = ("Bahnschrift SemiBold", 28)
    FONT_SUBTITLE = ("Segoe UI", 12)

    FONT_SECTION  = ("Bahnschrift SemiBold", 13)

    FONT_BADGE    = ("Segoe UI Semibold", 10)

    FONT_CARD_NUM = ("Bahnschrift SemiBold", 26)
    FONT_CARD_LBL = ("Segoe UI", 11)

    FONT_NAV      = ("Bahnschrift", 12)
    FONT_NAV_BOLD = ("Bahnschrift SemiBold", 12)
    FONT_NAV_SM   = ("Segoe UI", 10)
    
    # ── Geometry ──────────────────────────────────────────────────────────────
    PAD           = 16
    PAD_SM        = 8
    RADIUS        = 14     # Card corner radius
    RADIUS_SM     = 10     # Button / badge corner radius
    RADIUS_LG     = 18     # Large panel corner radius
    BTN_HEIGHT    = 44
    SIDEBAR_W     = 235
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  CIPHER ENGINE  (unchanged — pure logic, zero UI dependency)
# ══════════════════════════════════════════════════════════════════════════════
 
class CipherEngine:
    VALID_SHIFT_MIN = 1
    VALID_SHIFT_MAX = 25
 
    @staticmethod
    def caesar_encrypt(text: str, shift: int) -> str:
        return CipherEngine._caesar_transform(text, shift)
 
    @staticmethod
    def caesar_decrypt(text: str, shift: int) -> str:
        return CipherEngine._caesar_transform(text, -shift)
 
    @staticmethod
    def rot13(text: str) -> str:
        return CipherEngine._caesar_transform(text, 13)
 
    @staticmethod
    def generate_char_map(text: str, shift: int) -> list:
        mapping = []
        for ch in text:
            if ch.isalpha():
                base  = ord('A') if ch.isupper() else ord('a')
                trans = chr((ord(ch) - base + shift) % 26 + base)
                mapping.append((ch, trans))
            else:
                mapping.append((ch, ch))
        return mapping
 
    @staticmethod
    def validate_input(text: str, shift_raw: str) -> tuple:
        if not text or not text.strip():
            return False, "⚠  Plain text cannot be empty."
        if not shift_raw or not shift_raw.strip():
            return False, "⚠  Shift key is required."
        if not re.fullmatch(r"-?\d+", shift_raw.strip()):
            return False, "⚠  Shift key must be a whole number."
        shift = int(shift_raw.strip())
        if not (CipherEngine.VALID_SHIFT_MIN <= shift <= CipherEngine.VALID_SHIFT_MAX):
            return False, (f"⚠  Shift must be between "
                           f"{CipherEngine.VALID_SHIFT_MIN} and "
                           f"{CipherEngine.VALID_SHIFT_MAX}.")
        return True, ""
 
    @staticmethod
    def validate_text_only(text: str) -> tuple:
        if not text or not text.strip():
            return False, "⚠  Plain text cannot be empty."
        return True, ""
 
    @staticmethod
    def statistics(text: str) -> dict:
        words = len(text.split()) if text.strip() else 0
        return {"char_count": len(text), "word_count": words}
 
    @staticmethod
    def _caesar_transform(text: str, shift: int) -> str:
        result = []
        for ch in text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                result.append(chr((ord(ch) - base + shift) % 26 + base))
            else:
                result.append(ch)
        return "".join(result)
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  REPORT GENERATOR  (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
 
class ReportGenerator:
    @staticmethod
    def export(original: str, result: str, method: str,
               shift: int, stats: dict) -> str:
        ts      = datetime.datetime.now()
        ts_tag  = ts.strftime("%Y_%m_%d_%H_%M_%S")
        ts_nice = ts.strftime("%Y-%m-%d %H:%M:%S")
        filename = f"Encryption_Report_{ts_tag}.txt"
        separator = "═" * 60
        lines = [
            separator,
            "   ENCRYPTION & DECRYPTION WORKBENCH — OPERATION REPORT",
            "   Built by Pingali Prasiddha | Cybersecurity Internship",
            separator,
            "",
            f"  Timestamp      : {ts_nice}",
            f"  Method Used    : {method}",
            f"  Shift Value    : {shift if 'Caesar' in method else 'N/A (ROT13 = 13)'}",
            "",
            separator,
            "  INPUT / OUTPUT",
            separator,
            "",
            f"  Original Text  : {original}",
            f"  Result Text    : {result}",
            "",
            separator,
            "  TEXT STATISTICS",
            separator,
            "",
            f"  Character Count: {stats['char_count']}",
            f"  Word Count     : {stats['word_count']}",
            "",
            separator,
            "  Stay Secure. Stay Informed. Stay Ahead.",
            separator,
            "",
        ]
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath   = os.path.join(script_dir, filename)
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        return filename
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  UI COMPONENT HELPERS
# ══════════════════════════════════════════════════════════════════════════════
 
def make_glass_card(parent, corner_radius=None, fg_color=None, border_color=None,
                    border_width=1):
    """Return a CTkFrame styled as a glass card with optional glow border."""
    r  = corner_radius if corner_radius is not None else Theme.RADIUS
    fc = fg_color      if fg_color      is not None else Theme.BG_CARD
    bc = border_color  if border_color  is not None else Theme.BORDER
    return ctk.CTkFrame(parent, corner_radius=r, fg_color=fc,
                        border_color=bc, border_width=border_width)
 
 
def make_section_header(parent, title: str, fg_color=None):
    """Accent-bar + title label row used at the top of every card."""
    bg = fg_color if fg_color else Theme.BG_CARD
    row = ctk.CTkFrame(parent, fg_color=bg, corner_radius=0)
    row.pack(fill="x", padx=0, pady=(0, 0))
 
    # Cyan left bar
    bar = ctk.CTkFrame(row, fg_color=Theme.ACCENT, width=3,
                       corner_radius=0, height=20)
    bar.pack(side="left", fill="y", padx=(14, 8), pady=10)
    bar.pack_propagate(False)
 
    ctk.CTkLabel(row, text=title, font=Theme.FONT_SECTION,
                 text_color=Theme.ACCENT).pack(side="left", anchor="w")
 
    # Divider below
    div = ctk.CTkFrame(parent, fg_color=Theme.BORDER, height=1,
                       corner_radius=0)
    div.pack(fill="x", padx=0, pady=(0, 10))
    return row
 
 
def make_ctk_btn(parent, text, color, command,
                 width=120, height=36, font=None):
    """Styled CTkButton with hover colour computed from accent."""
    hover = _dim(color, 0.75)
    f = font if font else ("Segoe UI", 10, "bold")
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=color, hover_color=hover,
        text_color=Theme.BG_ROOT,
        font=f, corner_radius=Theme.RADIUS_SM,
        width=width, height=height,
        cursor="hand2",
    )
 
 
def _dim(hex_color: str, factor: float = 0.75) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
 
class EncryptionWorkbenchApp:
 
    STATUS_MESSAGES = [
        ("●", "SYSTEM READY",               Theme.SUCCESS),
        ("●", "CIPHER ENGINE ONLINE",        Theme.ACCENT),
        ("●", "SECURE CHANNEL ESTABLISHED",  Theme.ACCENT),
        ("●", "ENCRYPTION PROTOCOLS LOADED", Theme.SUCCESS),
        ("●", "AES-GRADE INTERFACE ACTIVE",  Theme.WARNING),
        ("●", "DATA INTEGRITY VERIFIED",     Theme.SUCCESS),
    ]
 
    # ── Pages that the sidebar can navigate to ────────────────────────────────
    PAGES = [
        ("🔒", "Cipher Lab",      "cipher"),
        ("📊", "Metrics",         "metrics"),
        ("🛡", "Security Info",  "awareness"),
        ("📤", "Export Report",   "export"),
    ]
 
    def __init__(self, root: ctk.CTk):
        self.root   = root
        self.engine = CipherEngine()
 
        # Runtime state
        self._last_result  = ""
        self._last_method  = "—"
        self._last_shift   = 0
        self._status_idx   = 0
        self._lock_state   = "LOCKED"
        self._active_page  = "cipher"
        self._nav_btns     = {}
 
        self._configure_window()
        self._build_shell()
        self._show_page("cipher")
        self._start_status_rotation()
        self._update_clock()
 
    # ─────────────────────────────────────────────────────────────────────────
    #  Window
    # ─────────────────────────────────────────────────────────────────────────
 
    def _configure_window(self):
        self.root.title("Encryption & Decryption Workbench  |  Cybersecurity Internship")
        self.root.configure(fg_color=Theme.BG_ROOT)
        self.root.geometry("1400x860")
        self.root.minsize(1100, 700)
 
    # ─────────────────────────────────────────────────────────────────────────
    #  Shell: Header + Sidebar + Main area
    # ─────────────────────────────────────────────────────────────────────────
 
    def _build_shell(self):
        # ── Header bar ────────────────────────────────────────────────────────
        self._build_header()
 
        # ── Body (sidebar + main) ─────────────────────────────────────────────
        body = ctk.CTkFrame(self.root, fg_color=Theme.BG_ROOT,
                            corner_radius=0)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
 
        self._build_sidebar(body)
 
        # Main content host — holds swappable page frames
        self.main_host = ctk.CTkFrame(body, fg_color=Theme.BG_MAIN,
                                      corner_radius=0)
        self.main_host.grid(row=0, column=1, sticky="nsew")
        self.main_host.columnconfigure(0, weight=1)
        self.main_host.rowconfigure(0, weight=1)
 
        # ── Build all pages (hidden until navigated to) ───────────────────────
        self.pages = {}
        self._build_page_cipher()
        self._build_page_metrics()
        self._build_page_awareness()
        self._build_page_export()
 
    # ─────────────────────────────────────────────────────────────────────────
    #  HEADER
    # ─────────────────────────────────────────────────────────────────────────
 
    def _build_header(self):
        hdr = ctk.CTkFrame(self.root, fg_color=Theme.BG_HEADER,
                           corner_radius=0, height=70,
                           border_color=Theme.BORDER, border_width=0)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
 
        # Top cyan accent strip
        strip = ctk.CTkFrame(hdr, fg_color=Theme.ACCENT, height=2,
                             corner_radius=0)
        strip.pack(fill="x", side="top")
 
        inner = ctk.CTkFrame(hdr, fg_color="transparent", corner_radius=0)
        inner.pack(fill="both", expand=True, padx=18)
 
        # ── Left: decorative canvas lock + brand ─────────────────────────────
        left = ctk.CTkFrame(inner, fg_color="transparent", corner_radius=0)
        left.pack(side="left", pady=8)
 
        self.lock_icon = ctk.CTkLabel(
            left,
            text="🔐",
            font=("Segoe UI Emoji", 24),
            text_color=Theme.ACCENT,
        )
        self.lock_icon.pack(side="left", padx=(12, 8))
       
 
        brand = ctk.CTkFrame(left, fg_color="transparent", corner_radius=0)
        brand.pack(side="left")
 
        ctk.CTkLabel(brand,
                     text="Basic Encryption & Decryption",
                     font=("Segoe UI Semibold", 24),
                     text_color=Theme.ACCENT).pack(anchor="w")
 
        ctk.CTkLabel(brand,
                     text="Classical Cipher Analysis Platform  •  Cybersecurity Internship",
                     font=Theme.FONT_SANS_SM,
                     text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
 
        # ── Right cluster: lock-state pill + engine status + clock ────────────
        right = ctk.CTkFrame(inner, fg_color="transparent", corner_radius=0)
        right.pack(side="right", pady=10)
 
        # Clock
        self.clock_label = ctk.CTkLabel(right, text="",
                                        font=("Consolas", 10),
                                        text_color=Theme.TEXT_SECONDARY)
        self.clock_label.pack(side="right", padx=(14, 0))
 
        ctk.CTkLabel(right, text="🕐",
                     font=Theme.FONT_SANS,
                     text_color=Theme.TEXT_SECONDARY).pack(side="right")
 
        # Separator
        ctk.CTkFrame(right, fg_color=Theme.BORDER, width=1,
                     corner_radius=0).pack(side="right", fill="y",
                                           padx=12, pady=6)
 
        # Engine status
        eng = ctk.CTkFrame(right, fg_color="transparent", corner_radius=0)
        eng.pack(side="right", padx=(0, 0))
 
        self.engine_status_label = ctk.CTkLabel(
            eng, text="● SYSTEM READY",
            font=("Consolas", 11, "bold"),
            text_color=Theme.SUCCESS)
        self.engine_status_label.pack(anchor="e")
 
        self.engine_sub_label = ctk.CTkLabel(
            eng, text="Cipher engine online",
            font=Theme.FONT_SANS_SM,
            text_color=Theme.TEXT_SECONDARY)
        self.engine_sub_label.pack(anchor="e")
 
        # Separator
        ctk.CTkFrame(right, fg_color=Theme.BORDER, width=1,
                     corner_radius=0).pack(side="right", fill="y",
                                           padx=12, pady=6)
 
        # Lock state pill badge
        self.lock_pill = ctk.CTkFrame(right, fg_color=Theme.BG_CARD2,
                                      corner_radius=20,
                                      border_color=Theme.WARNING,
                                      border_width=1)
        self.lock_pill.pack(side="right", padx=(0, 4))
 
        self.lock_pill_label = ctk.CTkLabel(
            self.lock_pill, text="🔒  LOCKED",
            font=("Consolas", 10, "bold"),
            text_color=Theme.WARNING)
        self.lock_pill_label.pack(padx=14, pady=6)
 
    
    # ─────────────────────────────────────────────────────────────────────────
    #  SIDEBAR
    # ─────────────────────────────────────────────────────────────────────────
 
    def _build_sidebar(self, parent):
        sb = ctk.CTkFrame(parent, fg_color=Theme.BG_SIDEBAR,
                          corner_radius=0, width=Theme.SIDEBAR_W,
                          border_color=Theme.SIDEBAR_SEP, border_width=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.pack_propagate(False)
        sb.grid_propagate(False)
 
        # Right border line
        border = ctk.CTkFrame(sb, fg_color=Theme.SIDEBAR_SEP,
                              width=1, corner_radius=0)
        border.pack(side="right", fill="y")
 
        content = ctk.CTkFrame(sb, fg_color="transparent", corner_radius=0)
        content.pack(fill="both", expand=True, side="left")
 
        # ── Section label ─────────────────────────────────────────────────────
        ctk.CTkLabel(content, text="NAVIGATION",
                     font=("Segoe UI", 7, "bold"),
                     text_color=Theme.TEXT_MUTED).pack(
                         anchor="w", padx=18, pady=(18, 6))
 
        # ── Nav buttons ───────────────────────────────────────────────────────
        for icon, label, page_id in self.PAGES:
            self._nav_btn(content, icon, label, page_id)
 
        # ── Divider ───────────────────────────────────────────────────────────
        ctk.CTkFrame(content, fg_color=Theme.SIDEBAR_SEP,
                     height=1, corner_radius=0).pack(
                         fill="x", padx=16, pady=14)
 
        # ── Live status section ───────────────────────────────────────────────
        ctk.CTkLabel(content, text="LIVE STATUS",
                     font=("Segoe UI", 7, "bold"),
                     text_color=Theme.TEXT_MUTED).pack(
                         anchor="w", padx=18, pady=(0, 6))
 
        self.sidebar_status_dot = ctk.CTkLabel(
            content, text="● SYSTEM READY",
            font=("Consolas", 9, "bold"),
            text_color=Theme.SUCCESS)
        self.sidebar_status_dot.pack(anchor="w", padx=18)
 
        self.sidebar_status2 = ctk.CTkLabel(
            content, text="CIPHER ENGINE ONLINE",
            font=("Consolas", 9),
            text_color=Theme.ACCENT)
        self.sidebar_status2.pack(anchor="w", padx=18, pady=(2, 0))
 
        # ── Divider ───────────────────────────────────────────────────────────
        ctk.CTkFrame(content, fg_color=Theme.SIDEBAR_SEP,
                     height=1, corner_radius=0).pack(
                         fill="x", padx=16, pady=14)
 
        # ── Bottom branding ───────────────────────────────────────────────────
        ctk.CTkLabel(content, text="Built by",
                     font=("Segoe UI", 8),
                     text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=18)
        ctk.CTkLabel(content, text="Pingali Prasiddha",
                     font=("Segoe UI", 12, "bold"),
                     text_color=Theme.TEXT_PRIMARY).pack(
                         anchor="w", padx=18, pady=(1, 0))
        ctk.CTkLabel(content, text="Decodelabs Internship 2026",
                     font=("Segoe UI", 9),
                     text_color=Theme.TEXT_MUTED).pack(
                         anchor="w", padx=18, pady=(1, 12))
 
    def _nav_btn(self, parent, icon, label, page_id):
        """Build a sidebar nav button that highlights the active page."""
        frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        frame.pack(fill="x", padx=10, pady=2)
 
        btn = ctk.CTkButton(
            frame,
            text=f"  {icon}   {label}",
            anchor="w",
            font=Theme.FONT_NAV,
            fg_color="transparent",
            hover_color=Theme.BG_CARD2,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Theme.RADIUS_SM,
            height=38,
            command=lambda p=page_id: self._show_page(p),
            cursor="hand2",
        )
        btn.pack(fill="x")
        self._nav_btns[page_id] = btn
 
    def _show_page(self, page_id: str):
        """Hide all pages, show the requested one, update nav highlight."""
        # Update nav button styles
        for pid, btn in self._nav_btns.items():
            if pid == page_id:
                btn.configure(fg_color=Theme.BG_CARD2,
                              text_color=Theme.ACCENT,
                              font=Theme.FONT_NAV_BOLD)
            else:
                btn.configure(fg_color="transparent",
                              text_color=Theme.TEXT_SECONDARY,
                              font=Theme.FONT_NAV)
 
        # Hide all, show active
        for pid, frame in self.pages.items():
            if pid == page_id:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_remove()
 
        self._active_page = page_id
 
    # ─────────────────────────────────────────────────────────────────────────
    #  PAGE: CIPHER LAB
    # ─────────────────────────────────────────────────────────────────────────
 
    def _build_page_cipher(self):
        page = ctk.CTkScrollableFrame(self.main_host,
                                      fg_color=Theme.BG_MAIN,
                                      corner_radius=0,
                                      scrollbar_button_color=Theme.BG_CARD2,
                                      scrollbar_button_hover_color=Theme.BORDER)
        self.pages["cipher"] = page
 
        # Page title row
        self._page_title(page, "🧪  Cipher Lab",
                         "Encrypt, decrypt, and analyse text using classical ciphers.")
 
        # ── Status bar strip ──────────────────────────────────────────────────
        self._build_cipher_statusbar(page)
 
        # ── Two-column row: Input + Output ────────────────────────────────────
        two_col = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
        two_col.pack(fill="x", padx=14, pady=(8, 8))
        two_col.columnconfigure(0, weight=3)
        two_col.columnconfigure(1, weight=2)
 
        self._build_input_card(two_col)
        self._build_output_card(two_col)
 
        # ── Character map card (full width) ───────────────────────────────────
        self._build_char_map_card(page)
 
    def _build_cipher_statusbar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="#080D13",
                           corner_radius=0, height=34)
        bar.pack(fill="x", padx=0, pady=(0, 4))
        bar.pack_propagate(False)
 
        inner = ctk.CTkFrame(bar, fg_color="transparent", corner_radius=0)
        inner.pack(fill="both", expand=True, padx=16)
 
        self.status_dot = ctk.CTkLabel(inner, text="●",
                                       font=("Consolas", 9, "bold"),
                                       text_color=Theme.SUCCESS)
        self.status_dot.pack(side="left", pady=8)
 
        self.status_text = ctk.CTkLabel(inner, text=" SYSTEM READY",
                                        font=("Consolas", 9, "bold"),
                                        text_color=Theme.SUCCESS)
        self.status_text.pack(side="left")
 
        ctk.CTkLabel(inner, text="  ·  ",
                     font=("Consolas", 9),
                     text_color=Theme.TEXT_MUTED).pack(side="left")
 
        self.status_text2 = ctk.CTkLabel(inner, text="CIPHER ENGINE ONLINE",
                                         font=("Consolas", 9, "bold"),
                                         text_color=Theme.ACCENT)
        self.status_text2.pack(side="left")
 
    # ── Input card ────────────────────────────────────────────────────────────
 
    def _build_input_card(self, parent):
        card = make_glass_card(parent)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
 
        make_section_header(card, "✏  INPUT CONTROLS")
 
        body = ctk.CTkFrame(card, fg_color="transparent", corner_radius=0)
        body.pack(fill="both", expand=True, padx=14, pady=(0, 14))
 
        # Plain text label
        ctk.CTkLabel(body, text="Plain Text",
                     font=Theme.FONT_SANS,
                     text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
 
        # Textbox
        self.txt_input = ctk.CTkTextbox(
            body, height=140,
            font=Theme.FONT_MONO_LG,
            fg_color=Theme.BG_INPUT,
            text_color=Theme.TEXT_PRIMARY,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=Theme.RADIUS_SM,
            scrollbar_button_color=Theme.BG_CARD2,
            wrap="word",
        )
        self.txt_input.pack(fill="x", pady=(4, 0))
        self.txt_input.bind("<KeyRelease>", self._on_text_change)
 
        self.char_count_label = ctk.CTkLabel(
            body, text="0 characters",
            font=Theme.FONT_SANS_SM,
            text_color=Theme.TEXT_SECONDARY,
            anchor="e")
        self.char_count_label.pack(fill="x", pady=(2, 10))
 
        # ── Shift key row ─────────────────────────────────────────────────────
        ctk.CTkLabel(body, text="Shift Key",
                     font=Theme.FONT_SANS,
                     text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
 
        key_row = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0)
        key_row.pack(fill="x", pady=(4, 0))
 
        self.shift_var = ctk.StringVar(value="3")
        self.shift_entry = ctk.CTkEntry(
            key_row,
            textvariable=self.shift_var,
            width=90,
            font=Theme.FONT_MONO_LG,
            fg_color=Theme.BG_INPUT,
            text_color=Theme.ACCENT,
            border_color=Theme.BORDER,
            border_width=1,
            corner_radius=Theme.RADIUS_SM,
        )
        self.shift_entry.pack(side="left", padx=(0, 10))
        self.shift_var.trace_add("write", self._on_shift_change)
 
        self.shift_badge = ctk.CTkLabel(
            key_row, text="✔ Valid (shift=3)",
            font=Theme.FONT_SANS_SM,
            text_color=Theme.SUCCESS)
        self.shift_badge.pack(side="left")
 
        # Tip
        ctk.CTkLabel(body,
            text="ⓘ  Shift range: 1–25.  ROT13 always uses shift = 13.",
            font=Theme.FONT_SANS_SM,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w", wraplength=460,
            justify="left").pack(anchor="w", pady=(6, 4))
 
        # Validation error
        self.error_label = ctk.CTkLabel(
            body, text="",
            font=Theme.FONT_SANS_SM,
            text_color=Theme.DANGER,
            anchor="w", wraplength=460,
            justify="left")
        self.error_label.pack(anchor="w", pady=(0, 6))
 
        # ── Action buttons ────────────────────────────────────────────────────
        btn_row1 = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0)
        btn_row1.pack(fill="x", pady=(4, 4))
        btn_row1.columnconfigure((0, 1, 2), weight=1)
 
        make_ctk_btn(btn_row1, "🔒  Encrypt", Theme.ACCENT,
                     self._do_encrypt, height=Theme.BTN_HEIGHT).grid(
                     row=0, column=0, sticky="ew", padx=(0, 4))
        make_ctk_btn(btn_row1, "🔓  Decrypt", Theme.SUCCESS,
                     self._do_decrypt, height=Theme.BTN_HEIGHT).grid(
                     row=0, column=1, sticky="ew", padx=4)
        make_ctk_btn(btn_row1, "🔄  ROT13", Theme.WARNING,
                     self._do_rot13, height=Theme.BTN_HEIGHT).grid(
                     row=0, column=2, sticky="ew", padx=(4, 0))
 
        btn_row2 = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0)
        btn_row2.pack(fill="x", pady=(0, 0))
        btn_row2.columnconfigure((0, 1, 2), weight=1)
 
        make_ctk_btn(btn_row2, "📋  Copy Result", Theme.BLUE,
                     self._do_copy, height=Theme.BTN_HEIGHT).grid(
                     row=0, column=0, sticky="ew", padx=(0, 4))
        make_ctk_btn(btn_row2, "🗑  Clear All", Theme.DANGER,
                     self._do_clear, height=Theme.BTN_HEIGHT).grid(
                     row=0, column=1, sticky="ew", padx=4)
        make_ctk_btn(btn_row2, "📤  Export", Theme.PURPLE,
                     self._do_export, height=Theme.BTN_HEIGHT).grid(
                     row=0, column=2, sticky="ew", padx=(4, 0))
 
    # ── Output card ───────────────────────────────────────────────────────────
 
    def _build_output_card(self, parent):
        card = make_glass_card(parent)
        card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
 
        make_section_header(card, "⬇  OUTPUT PANEL")
 
        body = ctk.CTkFrame(card, fg_color="transparent", corner_radius=0)
        body.pack(fill="both", expand=True, padx=14, pady=(0, 14))
 
        self.out_original  = self._output_field(body, "Original Text",   "INPUT")
        self.out_encrypted = self._output_field(body, "Encrypted Text",  "NOT APPLICABLE")
        self.out_decrypted = self._output_field(body, "Decrypted Text",  "—")
 
        # Status line
        status_card = make_glass_card(body, fg_color=Theme.BG_CARD2,
                                      corner_radius=Theme.RADIUS_SM)
        status_card.pack(fill="x", pady=(8, 4))
 
        status_inner = ctk.CTkFrame(status_card, fg_color="transparent",
                                    corner_radius=0)
        status_inner.pack(fill="x", padx=12, pady=8)
 
        self.out_status_icon = ctk.CTkLabel(status_inner, text="🛡",
                                            font=("Segoe UI", 12),
                                            text_color=Theme.SUCCESS)
        self.out_status_icon.pack(side="left", padx=(0, 6))
 
        self.out_status_text = ctk.CTkLabel(
            status_inner, text="Awaiting input…",
            font=Theme.FONT_SANS,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w")
        self.out_status_text.pack(side="left", fill="x", expand=True)
 
        # Report filename
        self.report_label = ctk.CTkLabel(
            body, text="",
            font=Theme.FONT_SANS_SM,
            text_color=Theme.TEXT_SECONDARY,
            anchor="w", wraplength=340,
            justify="left")
        self.report_label.pack(anchor="w", pady=(4, 0))
 
    def _output_field(self, parent, label_text, badge_text):
        row = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        row.pack(fill="x", pady=(0, 10))
 
        hdr = ctk.CTkFrame(row, fg_color="transparent", corner_radius=0)
        hdr.pack(fill="x", pady=(0, 3))
 
        ctk.CTkLabel(hdr, text=label_text,
                     font=Theme.FONT_NAV_BOLD,
                     text_color=Theme.TEXT_PRIMARY).pack(side="left")
 
        badge_frame = ctk.CTkFrame(hdr, fg_color=Theme.BG_CARD2,
                                   corner_radius=10)
        badge_frame.pack(side="right")
        badge_lbl = ctk.CTkLabel(badge_frame, text=badge_text,
                                 font=Theme.FONT_BADGE,
                                 text_color=Theme.TEXT_SECONDARY)
        badge_lbl.pack(padx=8, pady=2)
 
        var = ctk.StringVar(value="—")
        entry = ctk.CTkEntry(row, textvariable=var,
                             font=Theme.FONT_MONO,
                             fg_color=Theme.BG_INPUT,
                             text_color=Theme.ACCENT,
                             border_color=Theme.BORDER,
                             border_width=1,
                             corner_radius=Theme.RADIUS_SM,
                             state="readonly")
        entry.pack(fill="x")
 
        return {"var": var, "badge": badge_lbl, "badge_frame": badge_frame,
                "entry": entry}
 
    # ── Character map card ────────────────────────────────────────────────────
 
    def _build_char_map_card(self, parent):
        card = make_glass_card(parent)
        card.pack(fill="x", padx=14, pady=(0, 14))
 
        make_section_header(card, "🔣  CHARACTER TRANSFORMATION")
 
        body = ctk.CTkFrame(card, fg_color="transparent", corner_radius=0)
        body.pack(fill="x", padx=14, pady=(0, 14))
 
        self.map_count_label = ctk.CTkLabel(
            body, text="Awaiting operation…",
            font=Theme.FONT_SANS_SM,
            text_color=Theme.TEXT_SECONDARY)
        self.map_count_label.pack(anchor="w", pady=(0, 8))
 
        # Scrollable inner frame for char-map rows
        self.map_scroll_frame = ctk.CTkScrollableFrame(
            body, fg_color=Theme.BG_CARD2,
            corner_radius=Theme.RADIUS_SM,
            height=120,
            scrollbar_button_color=Theme.BG_CARD,
            scrollbar_button_hover_color=Theme.BORDER,
        )
        self.map_scroll_frame.pack(fill="x")
 
    # ─────────────────────────────────────────────────────────────────────────
    #  PAGE: METRICS
    # ─────────────────────────────────────────────────────────────────────────
 
    def _build_page_metrics(self):
        page = ctk.CTkScrollableFrame(self.main_host,
                                      fg_color=Theme.BG_MAIN,
                                      corner_radius=0,
                                      scrollbar_button_color=Theme.BG_CARD2,
                                      scrollbar_button_hover_color=Theme.BORDER)
        self.pages["metrics"] = page
 
        self._page_title(page, "📊  Metrics Dashboard",
                         "Live statistics from your cipher operations.")
 
        # ── Five metric tiles ─────────────────────────────────────────────────
        tiles_host = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
        tiles_host.pack(fill="x", padx=14, pady=(0, 12))
        for i in range(5):
            tiles_host.columnconfigure(i, weight=1)
 
        specs = [
            ("Aa", "Characters", "0",    Theme.ACCENT,  "metric_chars"),
            ("📄", "Words",       "0",    Theme.SUCCESS, "metric_words"),
            ("🔑", "Shift",       "—",    Theme.WARNING, "metric_shift"),
            ("🔒", "Method",      "—",    Theme.PURPLE,  "metric_method"),
            ("✅", "Status",      "IDLE", Theme.SUCCESS, "metric_status"),
        ]
        for col, (icon, label, value, color, attr) in enumerate(specs):
            lbl = self._metric_tile(tiles_host, icon, label, value, col, color)
            setattr(self, attr, lbl)
 
        # ── Operation log card ────────────────────────────────────────────────
        log_card = make_glass_card(page)
        log_card.pack(fill="x", padx=14, pady=(0, 14))
        make_section_header(log_card, "📋  OPERATION LOG")
 
        log_body = ctk.CTkFrame(log_card, fg_color="transparent",
                                corner_radius=0)
        log_body.pack(fill="x", padx=14, pady=(0, 14))
 
        self.log_scroll = ctk.CTkScrollableFrame(
            log_body, fg_color=Theme.BG_CARD2,
            corner_radius=Theme.RADIUS_SM,
            height=200,
            scrollbar_button_color=Theme.BG_CARD,
            scrollbar_button_hover_color=Theme.BORDER,
        )
        self.log_scroll.pack(fill="x")
        self._log_entries = []
 
        self._log_add("System", "Cipher workbench initialised.", Theme.SUCCESS)
 
    def _metric_tile(self, parent, icon, label, value, col, color):
        tile = make_glass_card(parent, fg_color=Theme.BG_CARD2,
                               corner_radius=Theme.RADIUS_SM)
        tile.grid(row=0, column=col, sticky="nsew", padx=4, pady=4)
 
        inner = ctk.CTkFrame(tile, fg_color="transparent", corner_radius=0)
        inner.pack(padx=12, pady=12, fill="x")
 
        ctk.CTkLabel(inner, text=icon, font=("Segoe UI", 18),
                     text_color=color).pack(anchor="w")
        ctk.CTkLabel(inner, text=label, font=Theme.FONT_CARD_LBL,
                     text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
 
        val_lbl = ctk.CTkLabel(inner, text=value,
                               font=Theme.FONT_CARD_NUM,
                               text_color=color)
        val_lbl.pack(anchor="w", pady=(2, 0))
 
        # Accent underline
        ctk.CTkFrame(tile, fg_color=color, height=2,
                     corner_radius=0).pack(fill="x", padx=0, pady=(4, 0),
                                           side="bottom")
        return val_lbl
 
    def _log_add(self, action: str, detail: str, color: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        row = ctk.CTkFrame(self.log_scroll, fg_color="transparent",
                           corner_radius=0)
        row.pack(fill="x", pady=2)
 
        ctk.CTkLabel(row, text=ts, font=("Consolas", 9),
                     text_color=Theme.TEXT_MUTED,
                     width=58, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=f"[{action}]",
                     font=("Consolas", 9, "bold"),
                     text_color=color,
                     width=80, anchor="w").pack(side="left", padx=(4, 0))
        ctk.CTkLabel(row, text=detail,
                     font=("Consolas", 9),
                     text_color=Theme.TEXT_SECONDARY,
                     anchor="w").pack(side="left", padx=(6, 0))
 
    # ─────────────────────────────────────────────────────────────────────────
    #  PAGE: SECURITY AWARENESS
    # ─────────────────────────────────────────────────────────────────────────
 
    def _build_page_awareness(self):
        page = ctk.CTkScrollableFrame(self.main_host,
                                      fg_color=Theme.BG_MAIN,
                                      corner_radius=0,
                                      scrollbar_button_color=Theme.BG_CARD2,
                                      scrollbar_button_hover_color=Theme.BORDER)
        self.pages["awareness"] = page
 
        self._page_title(page, "🛡  Security Awareness",
                         "Foundational concepts in cryptography and information security.")
 
        # Three glass cards side by side
        three = ctk.CTkFrame(page, fg_color="transparent", corner_radius=0)
        three.pack(fill="x", padx=14, pady=(0, 12))
        three.columnconfigure((0, 1, 2), weight=1)
 
        # Card 1 — What is Encryption
        c1 = make_glass_card(three, fg_color=Theme.BG_CARD2)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)
        self._awareness_card_body(c1, "What is Encryption?",
                                  Theme.ACCENT, "🔒",
            "Encryption converts readable data into ciphertext using an "
            "algorithm and key. Only authorised parties holding the correct "
            "key can reverse the process to recover the original message.")
 
        # Card 2 — Caesar Cipher
        c2 = make_glass_card(three, fg_color=Theme.BG_CARD2)
        c2.grid(row=0, column=1, sticky="nsew", padx=6, pady=4)
        self._awareness_card_body(c2, "Caesar Cipher",
                                  Theme.SUCCESS, "©",
            "A substitution cipher that shifts every letter by a fixed offset. "
            "It is one of history's oldest known encryption techniques, used by "
            "Julius Caesar to protect military communications.")
 
        # Card 3 — ROT13
        c3 = make_glass_card(three, fg_color=Theme.BG_CARD2)
        c3.grid(row=0, column=2, sticky="nsew", padx=(6, 0), pady=4)
        self._awareness_card_body(c3, "ROT13",
                                  Theme.WARNING, "🔄",
            "ROT13 is a Caesar Cipher with a fixed shift of 13. Because the "
            "English alphabet has 26 letters, applying ROT13 twice returns the "
            "original text, making encryption and decryption identical.")
 
        # Comparison table card
        tbl_card = make_glass_card(page)
        tbl_card.pack(fill="x", padx=14, pady=(0, 14))
        make_section_header(tbl_card, "⚖  ENCRYPTION vs ENCODING vs HASHING")
 
        tbl_body = ctk.CTkFrame(tbl_card, fg_color="transparent",
                                corner_radius=0)
        tbl_body.pack(fill="x", padx=14, pady=(0, 14))
 
        headers = ["Type", "Purpose", "Reversible?", "Example"]
        rows    = [
            ("Encryption", "Protect Confidentiality", "Yes",  "AES, Caesar"),
            ("Encoding",   "Data Representation",     "Yes",  "Base64, URL"),
            ("Hashing",    "Ensure Integrity",         "No",   "SHA-256, MD5"),
        ]
        row_colors = [Theme.ACCENT, Theme.SUCCESS, Theme.WARNING]
 
        tbl = ctk.CTkFrame(tbl_body, fg_color=Theme.BG_CARD2,
                           corner_radius=Theme.RADIUS_SM)
        tbl.pack(fill="x")
 
        # Header row
        hdr_row = ctk.CTkFrame(tbl, fg_color=Theme.BG_CARD,
                               corner_radius=0)
        hdr_row.pack(fill="x", padx=1, pady=(1, 0))
        weights = [2, 3, 2, 2]
        for j, (h, w) in enumerate(zip(headers, weights)):
            ctk.CTkLabel(hdr_row, text=h,
                         font=("Segoe UI", 9, "bold"),
                         text_color=Theme.TEXT_SECONDARY,
                         anchor="w").pack(side="left", padx=16,
                                          pady=10, expand=(w==3), fill="x")
 
        for i, (rtype, purpose, rev, example) in enumerate(rows):
            color = row_colors[i]
            data_row = ctk.CTkFrame(tbl, fg_color="transparent",
                                    corner_radius=0)
            data_row.pack(fill="x", padx=1, pady=0)
 
            vals_colors = [
                (rtype,   color),
                (purpose, Theme.TEXT_PRIMARY),
                (rev,     Theme.DANGER if rev == "No" else Theme.SUCCESS),
                (example, Theme.TEXT_SECONDARY),
            ]
            for v, fc in vals_colors:
                ctk.CTkLabel(data_row, text=v,
                             font=Theme.FONT_SANS_SM,
                             text_color=fc,
                             anchor="w").pack(side="left", padx=16,
                                              pady=8, expand=True, fill="x")
 
            if i < len(rows) - 1:
                ctk.CTkFrame(tbl, fg_color=Theme.BORDER, height=1,
                             corner_radius=0).pack(fill="x", padx=12)
 
    def _awareness_card_body(self, card, title, color, icon, body_text):
        inner = ctk.CTkFrame(card, fg_color="transparent", corner_radius=0)
        inner.pack(fill="both", padx=14, pady=12, expand=True)
 
        top = ctk.CTkFrame(inner, fg_color="transparent", corner_radius=0)
        top.pack(fill="x")
 
        ctk.CTkLabel(top, text=title,
                     font=("Segoe UI", 11, "bold"),
                     text_color=color, anchor="w").pack(side="left")
        ctk.CTkLabel(top, text=icon,
                     font=("Segoe UI", 22),
                     text_color=color).pack(side="right")
 
        ctk.CTkFrame(inner, fg_color=color, height=1,
                     corner_radius=0).pack(fill="x", pady=(6, 8))
 
        ctk.CTkLabel(inner, text=body_text,
                     font=Theme.FONT_SANS_SM,
                     text_color=Theme.TEXT_PRIMARY,
                     wraplength=240,
                     justify="left",
                     anchor="nw").pack(anchor="nw", fill="x")
 
    # ─────────────────────────────────────────────────────────────────────────
    #  PAGE: EXPORT
    # ─────────────────────────────────────────────────────────────────────────
 
    def _build_page_export(self):
        page = ctk.CTkScrollableFrame(self.main_host,
                                      fg_color=Theme.BG_MAIN,
                                      corner_radius=0,
                                      scrollbar_button_color=Theme.BG_CARD2,
                                      scrollbar_button_hover_color=Theme.BORDER)
        self.pages["export"] = page
 
        self._page_title(page, "📤  Export Report",
                         "Generate a timestamped TXT report of your last operation.")
 
        # Export action card
        exp_card = make_glass_card(page)
        exp_card.pack(fill="x", padx=14, pady=(0, 12))
        make_section_header(exp_card, "📄  REPORT GENERATOR")
 
        exp_body = ctk.CTkFrame(exp_card, fg_color="transparent",
                                corner_radius=0)
        exp_body.pack(fill="x", padx=14, pady=(0, 16))
 
        info = ctk.CTkFrame(exp_body, fg_color=Theme.BG_CARD2,
                            corner_radius=Theme.RADIUS_SM)
        info.pack(fill="x", pady=(0, 12))
        info_inner = ctk.CTkFrame(info, fg_color="transparent", corner_radius=0)
        info_inner.pack(fill="x", padx=14, pady=12)
 
        ctk.CTkLabel(info_inner,
                     text="Reports are saved as .txt files in the same directory as this script.",
                     font=Theme.FONT_SANS,
                     text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(info_inner,
                     text="Run at least one cipher operation first, then click Export Report.",
                     font=Theme.FONT_SANS_SM,
                     text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(3, 0))
 
        make_ctk_btn(exp_body, "📤  Export Report Now", Theme.PURPLE,
                     self._do_export, width=220, height=40,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w",
                                                         pady=(0, 10))
 
        self.export_page_label = ctk.CTkLabel(
            exp_body, text="",
            font=Theme.FONT_SANS,
            text_color=Theme.SUCCESS,
            anchor="w")
        self.export_page_label.pack(anchor="w")
 
    # ─────────────────────────────────────────────────────────────────────────
    #  PAGE TITLE HELPER
    # ─────────────────────────────────────────────────────────────────────────
 
    def _page_title(self, parent, title: str, subtitle: str):
        row = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        row.pack(fill="x", padx=18, pady=(18, 6))
 
        ctk.CTkLabel(row, text=title,
                     font=Theme.FONT_TITLE,
                     text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(row, text=subtitle,
                     font=Theme.FONT_SUBTITLE,
                     text_color=Theme.TEXT_SECONDARY).pack(anchor="w",
                                                            pady=(2, 0))
        ctk.CTkFrame(parent, fg_color=Theme.BORDER, height=1,
                     corner_radius=0).pack(fill="x", padx=14,
                                           pady=(6, 0))
 
    # ─────────────────────────────────────────────────────────────────────────
    #  ACTION HANDLERS  (logic unchanged; only widget calls remapped)
    # ─────────────────────────────────────────────────────────────────────────
 
    def _do_encrypt(self):
        text  = self.txt_input.get("1.0", "end-1c")
        shift = self.shift_var.get()
        ok, msg = CipherEngine.validate_input(text, shift)
        if not ok:
            self._show_error(msg)
            return
        self._clear_error()
        n      = int(shift.strip())
        result = CipherEngine.caesar_encrypt(text, n)
        self._last_result = result
        self._last_method = "Caesar Cipher"
        self._last_shift  = n
        stats = CipherEngine.statistics(text)
        self._update_outputs(text, result, "—",
                             "Encryption Successful!", Theme.SUCCESS,
                             "ENCRYPTED ✔", "N/A",
                             "Caesar Cipher", n, stats, "ENCRYPTED")
        self._update_char_map(CipherEngine.generate_char_map(text, n))
        self._update_engine_status("● ENCRYPTION SUCCESSFUL", Theme.SUCCESS,
                                   "Caesar cipher applied")
        self._log_add("ENCRYPT", f"Caesar shift={n}  |  {len(text)} chars",
                      Theme.ACCENT)
 
    def _do_decrypt(self):
        text  = self.txt_input.get("1.0", "end-1c")
        shift = self.shift_var.get()
        ok, msg = CipherEngine.validate_input(text, shift)
        if not ok:
            self._show_error(msg)
            return
        self._clear_error()
        n      = int(shift.strip())
        result = CipherEngine.caesar_decrypt(text, n)
        self._last_result = result
        self._last_method = "Caesar Cipher"
        self._last_shift  = n
        stats = CipherEngine.statistics(text)
        self._update_outputs(text, "—", result,
                             "Decryption Successful!", Theme.SUCCESS,
                             "NOT APPLICABLE", "DECRYPTED ✔",
                             "Caesar Cipher", n, stats, "DECRYPTED")
        self._update_char_map(CipherEngine.generate_char_map(text, -n))
        self._update_engine_status("● DECRYPTION SUCCESSFUL", Theme.SUCCESS,
                                   "Secure channel is active")
        self._log_add("DECRYPT", f"Caesar shift={n}  |  {len(text)} chars",
                      Theme.SUCCESS)
 
    def _do_rot13(self):
        text = self.txt_input.get("1.0", "end-1c")
        ok, msg = CipherEngine.validate_text_only(text)
        if not ok:
            self._show_error(msg)
            return
        self._clear_error()
        result = CipherEngine.rot13(text)
        self._last_result = result
        self._last_method = "ROT13"
        self._last_shift  = 13
        stats = CipherEngine.statistics(text)
        self._update_outputs(text, result, "—",
                             "ROT13 Applied — run again to reverse.",
                             Theme.WARNING,
                             "ROT13 ✔", "—",
                             "ROT13", 13, stats, "ROT13")
        self._update_char_map(CipherEngine.generate_char_map(text, 13))
        self._update_engine_status("● ROT13 MODE ACTIVE", Theme.WARNING,
                                   "Shift=13 transformation applied")
        self._log_add("ROT13", f"shift=13  |  {len(text)} chars", Theme.WARNING)
 
    def _do_copy(self):
        if not self._last_result:
            self._show_error("⚠  No result to copy. Run an operation first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self._last_result)
        self._set_status_line("📋  Result copied to clipboard!", Theme.BLUE)
        self._log_add("COPY", "Result copied to clipboard.", Theme.BLUE)
 
    def _do_clear(self):
        self.txt_input.delete("1.0", "end")
        self.shift_var.set("3")
        self._last_result = ""
        self._last_method = "—"
        self._last_shift  = 0
        self._clear_error()
        for field in (self.out_original, self.out_encrypted, self.out_decrypted):
            field["var"].set("—")
        self._update_lock_state("LOCKED")
        self._set_status_line("All fields cleared.", Theme.TEXT_SECONDARY)
        self._update_metrics(0, 0, "—", "—", "IDLE")
        self._clear_char_map()
        self.report_label.configure(text="")
        self.map_count_label.configure(text="Awaiting operation…",
                                       text_color=Theme.TEXT_SECONDARY)
        self._update_engine_status("● SYSTEM READY", Theme.SUCCESS,
                                   "Cipher engine online")
        self._log_add("CLEAR", "All fields reset.", Theme.TEXT_SECONDARY)
 
    def _do_export(self):
        if not self._last_result:
            self._show_error("⚠  Run an operation before exporting a report.")
            return
        text  = self.txt_input.get("1.0", "end-1c")
        stats = CipherEngine.statistics(text)
        try:
            filename = ReportGenerator.export(
                original=text, result=self._last_result,
                method=self._last_method, shift=self._last_shift,
                stats=stats)
            msg = f"📄  Report saved: {filename}"
            self.report_label.configure(text=msg,
                                        text_color=Theme.SUCCESS)
            try:
                self.export_page_label.configure(text=msg,
                                                 text_color=Theme.SUCCESS)
            except Exception:
                pass
            self._set_status_line(f"✅  Saved → {filename}", Theme.SUCCESS)
            self._log_add("EXPORT", filename, Theme.PURPLE)
        except Exception as exc:
            self._show_error(f"⚠  Export failed: {exc}")
 
    # ─────────────────────────────────────────────────────────────────────────
    #  STATE UPDATE HELPERS
    # ─────────────────────────────────────────────────────────────────────────
 
    def _update_outputs(self, original, encrypted, decrypted,
                        status_text, status_color,
                        badge_enc, badge_dec,
                        method, shift, stats, lock_state):
        trunc = lambda s: s[:80] + ("…" if len(s) > 80 else "")
        self.out_original["var"].set(trunc(original))
        self.out_encrypted["var"].set(trunc(encrypted))
        self.out_decrypted["var"].set(trunc(decrypted))
        self.out_encrypted["badge"].configure(text=badge_enc)
        self.out_decrypted["badge"].configure(text=badge_dec)
        self._set_status_line(status_text, status_color)
        self._update_lock_state(lock_state)
        self._update_metrics(stats["char_count"], stats["word_count"],
                             shift, method, lock_state)
 
    def _update_metrics(self, chars, words, shift, method, status):
        color_map = {
            "ENCRYPTED": Theme.ACCENT,
            "DECRYPTED": Theme.SUCCESS,
            "ROT13":     Theme.WARNING,
            "LOCKED":    Theme.TEXT_SECONDARY,
            "IDLE":      Theme.TEXT_SECONDARY,
        }
        sc = color_map.get(status, Theme.TEXT_SECONDARY)
        self.metric_chars.configure(text=str(chars))
        self.metric_words.configure(text=str(words))
        self.metric_shift.configure(text=str(shift))
        self.metric_method.configure(text=str(method)[:12])
        self.metric_status.configure(text=str(status), text_color=sc)
 
    def _update_char_map(self, mapping: list):
        self._clear_char_map()
        count = len(mapping)
        self.map_count_label.configure(
            text=f"Showing {count} character mapping{'s' if count != 1 else ''}",
            text_color=Theme.ACCENT)
 
        for orig, trans in mapping:
            row = ctk.CTkFrame(self.map_scroll_frame,
                               fg_color="transparent", corner_radius=0)
            row.pack(side="left", padx=6, pady=4)
 
            ctk.CTkLabel(row, text=orig,
                         font=("Consolas", 10),
                         text_color=Theme.TEXT_PRIMARY,
                         width=16, anchor="e").pack(side="left")
            ctk.CTkLabel(row, text="→",
                         font=("Consolas", 10),
                         text_color=Theme.TEXT_MUTED).pack(side="left", padx=3)
            color = Theme.ACCENT if trans != orig else Theme.TEXT_SECONDARY
            ctk.CTkLabel(row, text=trans,
                         font=("Consolas", 10, "bold"),
                         text_color=color,
                         width=16, anchor="w").pack(side="left")
 
    def _clear_char_map(self):
        for w in self.map_scroll_frame.winfo_children():
            w.destroy()
 
    def _update_lock_state(self, state: str):
        self._lock_state = state
        icons = {
            "LOCKED":    ("🔒", "LOCKED",    Theme.WARNING),
            "ENCRYPTED": ("🔒", "ENCRYPTED", Theme.ACCENT),
            "DECRYPTED": ("🔓", "DECRYPTED", Theme.SUCCESS),
            "ROT13":     ("🔄", "ROT13 MODE",Theme.WARNING),
        }
        icon_ch, label, color = icons.get(state, ("🔒", "LOCKED", Theme.WARNING))
        self.lock_pill_label.configure(text=f"{icon_ch}  {label}",
                                       text_color=color)
        self.lock_pill.configure(border_color=color)
 
        # Decorative canvas icon
 
    def _update_engine_status(self, text: str, color: str, sub: str):
        self.engine_status_label.configure(text=text, text_color=color)
        self.engine_sub_label.configure(text=sub)
 
    def _set_status_line(self, text: str, color: str):
        self.out_status_icon.configure(text_color=color)
        self.out_status_text.configure(text=text, text_color=color)
 
    def _show_error(self, msg: str):
        self.error_label.configure(text=msg, text_color=Theme.DANGER)
        self.shift_badge.configure(text="✖ Invalid",
                                   text_color=Theme.DANGER)
 
    def _clear_error(self):
        self.error_label.configure(text="")
 
    # ─────────────────────────────────────────────────────────────────────────
    #  LIVE UPDATES — status rotation, clock, shift validation
    # ─────────────────────────────────────────────────────────────────────────
 
    def _start_status_rotation(self):
        self._rotate_status()
 
    def _rotate_status(self):
        msgs = self.STATUS_MESSAGES
        idx  = self._status_idx % len(msgs)
        dot, text, color = msgs[idx]
        idx2 = (idx + 1) % len(msgs)
        _, text2, color2 = msgs[idx2]
 
        # Status bar in cipher page
        try:
            self.status_dot.configure(text=dot, text_color=color)
            self.status_text.configure(text=f" {text}", text_color=color)
            self.status_text2.configure(text=text2, text_color=color2)
        except Exception:
            pass
 
        # Sidebar live status
        try:
            self.sidebar_status_dot.configure(
                text=f"● {text}", text_color=color)
            self.sidebar_status2.configure(text=text2, text_color=color2)
        except Exception:
            pass
 
        self._status_idx += 1
        self.root.after(3500, self._rotate_status)
 
    def _update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            self.clock_label.configure(text=now)
        except Exception:
            pass
        self.root.after(1000, self._update_clock)
 
    def _on_text_change(self, _evt=None):
        text = self.txt_input.get("1.0", "end-1c")
        n    = len(text)
        self.char_count_label.configure(
            text=f"{n} character{'s' if n != 1 else ''}")
 
    def _on_shift_change(self, *_args):
        raw = self.shift_var.get().strip()
        if re.fullmatch(r"\d+", raw):
            n = int(raw)
            if CipherEngine.VALID_SHIFT_MIN <= n <= CipherEngine.VALID_SHIFT_MAX:
                self.shift_badge.configure(text=f"✔ Valid (shift={n})",
                                           text_color=Theme.SUCCESS)
                self._clear_error()
                return
        if raw:
            self.shift_badge.configure(text="✖ Invalid",
                                       text_color=Theme.DANGER)
        else:
            self.shift_badge.configure(text="— Enter shift",
                                       text_color=Theme.TEXT_SECONDARY)
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
 
def main():
    root = ctk.CTk()
    app  = EncryptionWorkbenchApp(root)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()