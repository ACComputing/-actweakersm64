#!/usr/bin/env python3
"""
AC'S SM64 TWEAKER 0.1
A dark-themed Super Mario 64 ROM manager built with Python 3.14+ and Tkinter.
Features real ROM parsing, hex viewing, format fixing, and ROM extending logic.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import struct
import os
import sys

# ──────────────────────────────────────────────────────────────
# AC'S SM64 TWEAKER 0.1 — Color Palette
# ──────────────────────────────────────────────────────────────
C_BG          = "#050505"
C_BG_ALT      = "#0a0a0a"
C_BG_RAISED   = "#111111"
C_BG_INPUT    = "#0a0a0a"
C_BORDER      = "#262626"
C_BORDER_FOCUS= "#3b82f6"
C_TEXT        = "#e5e5e5"
C_TEXT_DIM    = "#a3a3a3"
C_TEXT_MUTED  = "#525252"
C_ACCENT      = "#3b82f6"
C_ACCENT_HOVER= "#60a5fa"
C_GREEN       = "#22c55e"
C_RED         = "#ef4444"
C_YELLOW      = "#eab308"
C_ORANGE      = "#f97316"
C_PURPLE      = "#a855f7"
C_TREE_SEL_BG = "#1e3a5f"
C_TREE_SEL_FG = "#60a5fa"
C_MENU_BG     = "#111111"
C_MENU_ACTIVE = "#1e3a5f"
C_TAB_ACTIVE  = "#050505"
C_TAB_INACTIVE= "#111111"
C_HEX_OFFSET  = "#a855f7"
C_HEX_BYTE    = "#e5e5e5"
C_HEX_ASCII   = "#22c55e"
C_HEX_DOT     = "#525252"
C_STATUS_BG   = "#080808"
C_STATUS_BORDER = "#1e1e1e"
C_TOOLBAR_BG  = "#080808"
C_TOOLBAR_SEP = "#262626"
C_SCROLLBAR_BG= "#111111"
C_SCROLLBAR_TR = "#333333"


class DarkStyle(ttk.Style):
    """Custom dark ttk style for AC'S SM64 TWEAKER."""

    def __init__(self, root):
        super().__init__(root)
        self.theme_use("clam")
        self._configure_all()

    def _configure_all(self):
        # ── Global ──
        self.configure(".", background=C_BG, foreground=C_TEXT,
                       bordercolor=C_BORDER, darkcolor=C_BG_ALT,
                       lightcolor=C_BG_RAISED, troughcolor=C_BG_INPUT,
                       fieldbackground=C_BG_INPUT, font=("Segoe UI", 10))
        self.map(".", foreground=[("disabled", C_TEXT_MUTED)],
                 background=[("disabled", C_BG_ALT)])

        # ── Frame ──
        self.configure("TFrame", background=C_BG)
        self.configure("Toolbar.TFrame", background=C_TOOLBAR_BG)
        self.configure("Status.TFrame", background=C_STATUS_BG)

        # ── Label ──
        self.configure("TLabel", background=C_BG, foreground=C_TEXT,
                       font=("Segoe UI", 10))
        self.configure("Bold.TLabel", background=C_BG, foreground=C_TEXT,
                       font=("Segoe UI", 10, "bold"))
        self.configure("Dim.TLabel", background=C_BG, foreground=C_TEXT_DIM,
                       font=("Segoe UI", 9))
        self.configure("Muted.TLabel", background=C_BG, foreground=C_TEXT_MUTED,
                       font=("Segoe UI", 9, "italic"))
        self.configure("Status.TLabel", background=C_STATUS_BG,
                       foreground=C_TEXT_DIM, font=("Consolas", 9))
        self.configure("Accent.TLabel", background=C_BG, foreground=C_ACCENT,
                       font=("Segoe UI", 10, "bold"))
        self.configure("Green.TLabel", background=C_BG, foreground=C_GREEN,
                       font=("Segoe UI", 10, "bold"))
        self.configure("Red.TLabel", background=C_BG, foreground=C_RED,
                       font=("Segoe UI", 10, "bold"))
        self.configure("Version.TLabel", background=C_TOOLBAR_BG,
                       foreground=C_TEXT_MUTED, font=("Consolas", 9))

        # ── Button ──
        self.configure("TButton", background=C_BG_RAISED, foreground=C_TEXT,
                       bordercolor=C_BORDER, lightcolor=C_BG_RAISED,
                       darkcolor=C_BG_ALT, font=("Segoe UI", 9),
                       padding=(10, 5))
        self.map("TButton",
                 background=[("active", C_BORDER), ("pressed", C_ACCENT)],
                 foreground=[("active", C_TEXT), ("pressed", "#ffffff")],
                 bordercolor=[("focus", C_ACCENT)])

        self.configure("Accent.TButton", background=C_ACCENT, foreground="#ffffff",
                       bordercolor=C_ACCENT, lightcolor="#2563eb",
                       darkcolor="#1d4ed8", font=("Segoe UI", 9, "bold"),
                       padding=(12, 6))
        self.map("Accent.TButton",
                 background=[("active", C_ACCENT_HOVER), ("pressed", "#2563eb")],
                 foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])

        self.configure("Danger.TButton", background="#7f1d1d", foreground=C_RED,
                       bordercolor="#991b1b", lightcolor="#450a0a",
                       darkcolor="#7f1d1d", font=("Segoe UI", 9, "bold"),
                       padding=(10, 5))
        self.map("Danger.TButton",
                 background=[("active", "#991b1b"), ("pressed", C_RED)],
                 foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])

        self.configure("Tool.TButton", background=C_TOOLBAR_BG, foreground=C_TEXT_DIM,
                       bordercolor=C_TOOLBAR_SEP, lightcolor=C_TOOLBAR_BG,
                       darkcolor=C_TOOLBAR_BG, font=("Segoe UI", 9),
                       padding=(8, 4))
        self.map("Tool.TButton",
                 background=[("active", C_BG_RAISED), ("pressed", C_ACCENT)],
                 foreground=[("active", C_TEXT), ("pressed", "#ffffff")],
                 bordercolor=[("active", C_BORDER), ("pressed", C_ACCENT)])

        # ── Separator ──
        self.configure("TSeparator", background=C_BORDER)
        self.configure("Tool.TSeparator", background=C_TOOLBAR_SEP)

        # ── Notebook ──
        self.configure("TNotebook", background=C_BG, bordercolor=C_BORDER,
                       tabmargins=(0, 0, 0, 0))
        self.map("TNotebook", background=[("selected", C_TAB_ACTIVE)])

        self.configure("TNotebook.Tab", background=C_TAB_INACTIVE,
                       foreground=C_TEXT_DIM, bordercolor=C_BORDER,
                       lightcolor=C_TAB_INACTIVE, darkcolor=C_BG_ALT,
                       padding=(16, 8), font=("Segoe UI", 9))
        self.map("TNotebook.Tab",
                 background=[("selected", C_TAB_ACTIVE), ("active", C_BG_RAISED)],
                 foreground=[("selected", C_ACCENT), ("active", C_TEXT)],
                 bordercolor=[("selected", C_ACCENT)])

        # ── Treeview ──
        self.configure("Treeview", background=C_BG, foreground=C_TEXT,
                       fieldbackground=C_BG, bordercolor=C_BORDER,
                       lightcolor=C_BG, darkcolor=C_BG_ALT,
                       rowheight=28, font=("Segoe UI", 9))
        self.map("Treeview",
                 background=[("selected", C_TREE_SEL_BG)],
                 foreground=[("selected", C_TREE_SEL_FG)])

        self.configure("Treeview.Heading", background=C_BG_RAISED,
                       foreground=C_TEXT_DIM, bordercolor=C_BORDER,
                       lightcolor=C_BG_RAISED, darkcolor=C_BG_ALT,
                       font=("Segoe UI", 9, "bold"))
        self.map("Treeview.Heading",
                 background=[("active", C_BORDER)],
                 foreground=[("active", C_TEXT)])

        # ── Scrollbar ──
        self.configure("Vertical.TScrollbar", background=C_SCROLLBAR_BG,
                       troughcolor=C_BG, bordercolor=C_BORDER,
                       lightcolor=C_SCROLLBAR_BG, darkcolor=C_SCROLLBAR_BG,
                       arrowcolor=C_TEXT_DIM)
        self.map("Vertical.TScrollbar",
                 background=[("active", C_SCROLLBAR_TR)])

        self.configure("Horizontal.TScrollbar", background=C_SCROLLBAR_BG,
                       troughcolor=C_BG, bordercolor=C_BORDER,
                       lightcolor=C_SCROLLBAR_BG, darkcolor=C_SCROLLBAR_BG,
                       arrowcolor=C_TEXT_DIM)
        self.map("Horizontal.TScrollbar",
                 background=[("active", C_SCROLLBAR_TR)])

        # ── PanedWindow ──
        self.configure("TPanedwindow", background=C_BG, bordercolor=C_BORDER)

        # ── Menu ──
        self.configure("Menu", background=C_MENU_BG, foreground=C_TEXT,
                       activebackground=C_MENU_ACTIVE, activeforeground=C_TREE_SEL_FG,
                       bordercolor=C_BORDER, lightcolor=C_MENU_BG,
                       darkcolor=C_MENU_BG, font=("Segoe UI", 9))
        self.map("Menu",
                 background=[("active", C_MENU_ACTIVE)],
                 foreground=[("active", C_TREE_SEL_FG)])


class ACTweakerGUI(tk.Tk):
    """AC'S SM64 TWEAKER 0.1 — Main Application Window."""

    def __init__(self):
        super().__init__()

        self.title("AC'S SM64 TWEAKER 0.1")
        self.geometry("1000x650")
        self.minsize(750, 450)

        # Force dark window chrome on Windows 10/11 (Python 3.14 compat)
        try:
            self.update_idletasks()
            if sys.platform == "win32":
                from ctypes import windll, c_int, byref, sizeof
                hwnd = windll.user32.GetParent(self.winfo_id())
                windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 20, byref(c_int(2)), sizeof(c_int)
                )
        except Exception:
            pass

        # Apply dark theme
        self.configure(bg=C_BG)
        self._style = DarkStyle(self)

        # State
        self.loaded_rom_path = None
        self.rom_data = bytearray()
        self.is_sm64 = False
        self._hex_update_job = None

        # Build UI
        self._create_menu()
        self._create_toolbar()
        self._create_main_layout()
        self._create_statusbar()

        # Key bindings
        self.bind_all("<Control-o>", lambda e: self.open_rom())
        self.bind_all("<Control-s>", lambda e: self.save_rom())
        self.bind_all("<Control-q>", lambda e: self.quit())

    # ──────────── MENU BAR ────────────

    def _create_menu(self):
        menubar = tk.Menu(self, bg=C_MENU_BG, fg=C_TEXT,
                          activebackground=C_MENU_ACTIVE,
                          activeforeground=C_TREE_SEL_FG,
                          borderwidth=0, relief=tk.FLAT,
                          font=("Segoe UI", 9))
        self.config(menu=menubar)

        # File
        file_menu = tk.Menu(menubar, tearoff=False, bg=C_MENU_BG, fg=C_TEXT,
                            activebackground=C_MENU_ACTIVE,
                            activeforeground=C_TREE_SEL_FG,
                            borderwidth=0, font=("Segoe UI", 9))
        file_menu.add_command(label="Open ROM...", command=self.open_rom, accelerator="Ctrl+O")
        file_menu.add_command(label="Save ROM", command=self.save_rom, accelerator="Ctrl+S")
        file_menu.add_command(label="Save ROM As...", command=self.save_rom_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        # Tools
        tools_menu = tk.Menu(menubar, tearoff=False, bg=C_MENU_BG, fg=C_TEXT,
                             activebackground=C_MENU_ACTIVE,
                             activeforeground=C_TREE_SEL_FG,
                             borderwidth=0, font=("Segoe UI", 9))
        tools_menu.add_command(label="Extend ROM (8MB → 32MB)", command=self.extend_rom)
        tools_menu.add_separator()
        tools_menu.add_command(label="Level Importer", command=self.not_implemented)
        tools_menu.add_command(label="Text Editor", command=self.not_implemented)
        tools_menu.add_command(label="Music Editor", command=self.not_implemented)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help
        help_menu = tk.Menu(menubar, tearoff=False, bg=C_MENU_BG, fg=C_TEXT,
                            activebackground=C_MENU_ACTIVE,
                            activeforeground=C_TREE_SEL_FG,
                            borderwidth=0, font=("Segoe UI", 9))
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

    # ──────────── TOOLBAR ────────────

    def _create_toolbar(self):
        toolbar = ttk.Frame(self, style="Toolbar.TFrame", padding=(8, 4))
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Brand
        brand_frame = ttk.Frame(toolbar, style="Toolbar.TFrame")
        brand_frame.pack(side=tk.LEFT, padx=(0, 16))
        ttk.Label(brand_frame, text="AC'S", style="Version.TLabel",
                  font=("Consolas", 11, "bold"), foreground=C_ACCENT
                  ).pack(side=tk.LEFT)
        ttk.Label(brand_frame, text=" SM64 TWEAKER", style="Version.TLabel"
                  ).pack(side=tk.LEFT)
        ttk.Label(brand_frame, text=" 0.1", style="Version.TLabel",
                  foreground=C_GREEN
                  ).pack(side=tk.LEFT)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL,
                       style="Tool.TSeparator").pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=2)

        # Buttons
        ttk.Button(toolbar, text="⬆  Open ROM", style="Tool.TButton",
                   command=self.open_rom).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="⬇  Save ROM", style="Tool.TButton",
                   command=self.save_rom).pack(side=tk.LEFT, padx=2)

        ttk.Separator(toolbar, orient=tk.VERTICAL,
                       style="Tool.TSeparator").pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=2)

        ttk.Button(toolbar, text="🚀 Extend to 32MB", style="Tool.TButton",
                   command=self.extend_rom).pack(side=tk.LEFT, padx=2)

        # Right side: ROM indicator
        self.rom_indicator_var = tk.StringVar(value="● NO ROM")
        self.rom_indicator = ttk.Label(toolbar, textvariable=self.rom_indicator_var,
                                       style="Version.TLabel", foreground=C_RED,
                                       font=("Consolas", 9, "bold"))
        self.rom_indicator.pack(side=tk.RIGHT, padx=8)

    # ──────────── MAIN LAYOUT ────────────

    def _create_main_layout(self):
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=(2, 0))

        # ── Left: ROM Tree ──
        left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=1)

        tree_label = ttk.Label(left_frame, text="  ROM STRUCTURE",
                               style="Dim.TLabel",
                               font=("Segoe UI", 8, "bold"))
        tree_label.pack(anchor=tk.W, pady=(4, 2), padx=4)

        tree_container = ttk.Frame(left_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_container, yscrollcommand=tree_scroll.set,
                                 selectmode="browse", show="tree")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # ── Right: Notebook ──
        right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(right_frame, weight=3)

        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Properties
        self.info_tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.info_tab, text="  Properties  ")
        self._setup_info_tab()

        # Tab 2: Hex Viewer
        self.hex_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.hex_tab, text="  Hex Viewer  ")
        self._setup_hex_tab()

        # Tab 3: Patches (placeholder)
        self.patches_tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.patches_tab, text="  Patches  ")
        self._setup_patches_tab()

    def _setup_info_tab(self):
        # Header section
        header_frame = ttk.Frame(self.info_tab)
        header_frame.pack(fill=tk.X, pady=(0, 16))

        ttk.Label(header_frame, text="ROM PROPERTIES",
                  style="Accent.TLabel",
                  font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        ttk.Separator(header_frame).pack(fill=tk.X, pady=(6, 0))

        # Properties grid
        props_frame = ttk.Frame(self.info_tab)
        props_frame.pack(fill=tk.X)

        labels = [
            ("ROM Name:", "name"),
            ("Internal Title:", "title"),
            ("Format:", "format"),
            ("Size:", "size"),
            ("Checksum 1:", "crc1"),
            ("Checksum 2:", "crc2"),
            ("Region:", "region"),
            ("Extended:", "extended"),
        ]

        self.info_vars = {}
        for i, (label_text, key) in enumerate(labels):
            row_frame = ttk.Frame(props_frame)
            row_frame.pack(fill=tk.X, pady=3)

            ttk.Label(row_frame, text=label_text, style="Dim.TLabel",
                      width=16, anchor=tk.E).pack(side=tk.LEFT, padx=(0, 12))
            var = tk.StringVar(value="—")
            self.info_vars[key] = var
            ttk.Label(row_frame, textvariable=var, style="Bold.TLabel",
                      foreground=C_TEXT).pack(side=tk.LEFT)

        # Divider
        ttk.Separator(self.info_tab).pack(fill=tk.X, pady=16)

        # Context area
        self.context_var = tk.StringVar(value="Load a ROM to get started.")
        self.context_label = ttk.Label(self.info_tab, textvariable=self.context_var,
                                       style="Muted.TLabel", wraplength=500,
                                       justify=tk.LEFT)
        self.context_label.pack(anchor=tk.W)

    def _setup_hex_tab(self):
        hex_font = ("Consolas", 10) if sys.platform == "win32" else ("Courier New", 10)

        # Header
        hex_header = ttk.Frame(self.hex_tab)
        hex_header.pack(fill=tk.X, padx=8, pady=(6, 2))
        ttk.Label(hex_header, text="HEX DUMP — FIRST 4KB",
                  style="Dim.TLabel", font=("Segoe UI", 8, "bold")).pack(anchor=tk.W)

        # Text widget
        text_frame = ttk.Frame(self.hex_tab)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        hex_scroll_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        hex_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.hex_text = tk.Text(text_frame, font=hex_font, state=tk.DISABLED,
                                wrap=tk.NONE, bg=C_BG_ALT, fg=C_HEX_BYTE,
                                insertbackground=C_TEXT, selectbackground=C_TREE_SEL_BG,
                                selectforeground=C_TREE_SEL_FG,
                                borderwidth=0, highlightthickness=1,
                                highlightcolor=C_BORDER_FOCUS,
                                highlightbackground=C_BORDER,
                                padx=8, pady=8, cursor="arrow",
                                spacing1=1, spacing3=1)
        self.hex_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hex_scroll_y.config(command=self.hex_text.yview)

        # Hex tag styling
        self.hex_text.tag_configure("offset", foreground=C_HEX_OFFSET)
        self.hex_text.tag_configure("hex", foreground=C_HEX_BYTE)
        self.hex_text.tag_configure("ascii", foreground=C_HEX_ASCII)
        self.hex_text.tag_configure("dot", foreground=C_HEX_DOT)
        self.hex_text.tag_configure("header_highlight", foreground=C_YELLOW)
        self.hex_text.tag_configure("sm64_magic", foreground=C_GREEN)
        self.hex_text.tag_configure("separator_line", foreground=C_TEXT_MUTED)

    def _setup_patches_tab(self):
        ttk.Label(self.patches_tab, text="PATCHES",
                  style="Accent.TLabel",
                  font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(0, 8))
        ttk.Separator(self.patches_tab).pack(fill=tk.X, pady=(0, 16))

        ttk.Label(self.patches_tab, text="Load a ROM to view available patches.",
                  style="Muted.TLabel", wraplength=500,
                  justify=tk.LEFT).pack(anchor=tk.W)

        self.patches_container = ttk.Frame(self.patches_tab)
        self.patches_container.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

    # ──────────── STATUS BAR ────────────

    def _create_statusbar(self):
        status_frame = ttk.Frame(self, style="Status.TFrame")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar(value="Ready — Open a Super Mario 64 ROM to begin.")
        ttk.Label(status_frame, textvariable=self.status_var,
                  style="Status.TLabel", padding=(12, 4)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.status_right_var = tk.StringVar(value="Python 3.14+")
        ttk.Label(status_frame, textvariable=self.status_right_var,
                  style="Status.TLabel", padding=(12, 4),
                  foreground=C_TEXT_MUTED).pack(side=tk.RIGHT)

    # ──────────── ROM LOGIC ────────────

    def fix_endianness(self):
        """Normalizes the ROM to Big Endian (.z64) format."""
        if len(self.rom_data) < 4:
            return "Unknown"

        magic = self.rom_data[0:4]

        if magic == b'\x80\x37\x12\x40':
            return "Big Endian (.z64)"

        elif magic == b'\x37\x80\x40\x12':
            self.status_var.set("Byte-swapping .v64 → .z64 ...")
            self.update_idletasks()
            # Pair-swap; stop before last byte if length is odd (corrupt / trimmed ROM)
            for i in range(0, len(self.rom_data) - 1, 2):
                self.rom_data[i], self.rom_data[i + 1] = (
                    self.rom_data[i + 1], self.rom_data[i])
            return "Byte-Swapped (.v64 → .z64)"

        elif magic == b'\x40\x12\x37\x80':
            self.status_var.set("Word-swapping .n64 → .z64 ...")
            self.update_idletasks()
            for i in range(0, len(self.rom_data), 4):
                self.rom_data[i:i + 4] = self.rom_data[i:i + 4][::-1]
            return "Little Endian (.n64 → .z64)"

        return "Unknown Magic"

    def parse_header(self):
        """Parses real N64 ROM header information."""
        if len(self.rom_data) < 0x40:
            size_mb = len(self.rom_data) / (1024 * 1024)
            self.info_vars["name"].set("—")
            self.info_vars["title"].set("—")
            self.info_vars["size"].set(
                f"{size_mb:.4f} MB ({len(self.rom_data):,} bytes)"
            )
            self.info_vars["crc1"].set("—")
            self.info_vars["crc2"].set("—")
            self.info_vars["region"].set("—")
            mb8 = 8 * 1024 * 1024
            mb32 = 32 * 1024 * 1024
            n = len(self.rom_data)
            self.info_vars["extended"].set(
                "Yes (≥32MB)" if n >= mb32
                else "No (≤8MB vanilla)" if n <= mb8
                else f"Custom ({size_mb:.1f} MB)"
            )
            self.is_sm64 = False
            return

        # Clock rate / version (reserved for future UI)
        _clock_rate = struct.unpack('>I', self.rom_data[0x04:0x08])[0]
        _version = self.rom_data[0x0B]

        # Checksums
        crc1 = struct.unpack('>I', self.rom_data[0x10:0x14])[0]
        crc2 = struct.unpack('>I', self.rom_data[0x14:0x18])[0]

        # PC offset / entry point (reserved for future UI)
        _pc_entry = struct.unpack('>I', self.rom_data[0x08:0x0C])[0]

        # Game Title (N64 internal: 0x20 – 0x34)
        title_bytes = self.rom_data[0x20:0x34]
        game_title = title_bytes.decode('ascii', errors='ignore').strip()

        # Region code (0x3E)
        region_map = {
            0x45: "NTSC (USA)",
            0x4A: "NTSC (JAP)",
            0x50: "PAL (EUR)",
            0x55: "NTSC-A (AUS)",
        }
        region_code = self.rom_data[0x3E] if len(self.rom_data) > 0x3E else 0
        region = region_map.get(region_code, f"Unknown (0x{region_code:02X})")

        size_mb = len(self.rom_data) / (1024 * 1024)

        # Update UI
        self.info_vars["name"].set(game_title if game_title else "UNKNOWN")
        self.info_vars["title"].set(game_title if game_title else "UNKNOWN")
        self.info_vars["size"].set(f"{size_mb:.2f} MB ({len(self.rom_data):,} bytes)")
        self.info_vars["crc1"].set(f"0x{crc1:08X}")
        self.info_vars["crc2"].set(f"0x{crc2:08X}")
        self.info_vars["region"].set(region)
        mb8 = 8 * 1024 * 1024
        mb32 = 32 * 1024 * 1024
        n = len(self.rom_data)
        self.info_vars["extended"].set(
            "Yes (≥32MB)" if n >= mb32
            else "No (≤8MB vanilla)" if n <= mb8
            else f"Custom ({size_mb:.1f} MB)"
        )

        self.is_sm64 = "MARIO" in game_title.upper()

    # ──────────── FILE OPERATIONS ────────────

    def open_rom(self):
        filepath = filedialog.askopenfilename(
            title="Open N64 ROM — AC'S SM64 TWEAKER",
            filetypes=(("N64 ROMs", "*.z64 *.v64 *.n64 *.rom *.bin"),
                       ("All Files", "*.*"))
        )
        if not filepath:
            return

        try:
            self.status_var.set("Loading ROM into memory ...")
            self.update_idletasks()

            with open(filepath, 'rb') as f:
                self.rom_data = bytearray(f.read())

            self.loaded_rom_path = filepath

            # Process
            fmt = self.fix_endianness()
            self.info_vars["format"].set(fmt)
            self.parse_header()

            filename = os.path.basename(filepath)
            self.status_var.set(f"Loaded: {filename}")

            # Update indicator
            self.rom_indicator_var.set("● SM64" if self.is_sm64 else "● ROM")
            self.rom_indicator.configure(foreground=C_GREEN if self.is_sm64 else C_YELLOW)

            # Update views
            self._populate_tree()
            self._schedule_hex_update()

            if self.is_sm64:
                self.context_var.set(
                    "Super Mario 64 detected!\n\n"
                    "You can extend this ROM, view the hex dump,\n"
                    "and browse the ROM structure in the tree."
                )
            else:
                self.context_var.set(
                    "ROM loaded, but this doesn't appear to be\n"
                    "Super Mario 64. Some features may not work."
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ROM:\n{e}")
            self.status_var.set("Error loading ROM.")

    def save_rom(self):
        if not self.rom_data or not self.loaded_rom_path:
            messagebox.showwarning("Warning", "No ROM loaded to save!")
            return
        try:
            self.status_var.set("Saving ROM ...")
            self.update_idletasks()
            with open(self.loaded_rom_path, 'wb') as f:
                f.write(self.rom_data)
            self.status_var.set("ROM saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save ROM:\n{e}")

    def save_rom_as(self):
        if not self.rom_data:
            messagebox.showwarning("Warning", "No ROM loaded to save!")
            return
        filepath = filedialog.asksaveasfilename(
            title="Save ROM As — AC'S SM64 TWEAKER",
            defaultextension=".z64",
            filetypes=(("Z64 ROM", "*.z64"), ("All Files", "*.*"))
        )
        if filepath:
            self.loaded_rom_path = filepath
            self.save_rom()

    def extend_rom(self):
        if not self.rom_data:
            messagebox.showwarning("Warning", "No ROM loaded!")
            return

        current_size = len(self.rom_data)
        mb_8 = 8 * 1024 * 1024
        mb_32 = 32 * 1024 * 1024

        if current_size >= mb_32:
            messagebox.showinfo("Info", "ROM is already 32MB or larger!")
            return

        if current_size != mb_8:
            if not messagebox.askyesno(
                "Warning",
                f"ROM is {current_size / (1024 * 1024):.2f} MB, not exactly 8MB.\n"
                f"Extend anyway?"
            ):
                return

        self.status_var.set("Extending ROM to 32MB ...")
        self.update_idletasks()

        padding = mb_32 - current_size
        self.rom_data.extend(b'\x01' * padding)

        self.parse_header()
        self._schedule_hex_update()

        # Update indicator
        self.rom_indicator_var.set("● 32MB")
        self.rom_indicator.configure(foreground=C_GREEN)

        self.status_var.set("ROM extended to 32MB in memory. Save to apply.")
        messagebox.showinfo(
            "Success",
            "ROM extended to 32MB in memory.\n\n"
            "Use File → Save to write changes to disk."
        )

    # ──────────── TREE ────────────

    def _populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        name = self.info_vars["name"].get()
        root = self.tree.insert("", "end", text=f"📁 {name}", open=True)

        # Header
        hdr = self.tree.insert(root, "end", text="📦 ROM Header (0x0000–0x003F)",
                               tags=("header",))
        self.tree.insert(hdr, "end", text="   Boot Code / IPL3", tags=("bootcode",))
        self.tree.insert(hdr, "end", text="   Checksums", tags=("header",))
        self.tree.insert(hdr, "end", text="   Entry Point", tags=("header",))

        if self.is_sm64:
            # SM64 structure
            seg = self.tree.insert(root, "end", text="🗂️ Segments", open=True)
            segments = [
                "Segment 0x02: Level Data",
                "Segment 0x04: Level Scripts",
                "Segment 0x05: Behavior Scripts",
                "Segment 0x08: MIO0 Compressed",
                "Segment 0x09: MIO0 Compressed",
                "Segment 0x0A: MIO0 Compressed",
                "Segment 0x0B: MIO0 Compressed",
                "Segment 0x0C: MIO0 Compressed",
                "Segment 0x0D: MIO0 Compressed",
                "Segment 0x0E: MIO0 Compressed",
                "Segment 0x0F: MIO0 Compressed",
                "Segment 0x13: Animation Data",
                "Segment 0x14: Demo Data",
            ]
            for s in segments:
                self.tree.insert(seg, "end", text=f"   {s}", tags=("segment",))

            levels = self.tree.insert(root, "end", text="🎮 Levels", open=True)
            level_names = [
                ("Bob-omb Battlefield", "0x00000001"),
                ("Whomp's Fortress", "0x00000002"),
                ("Jolly Roger Bay", "0x00000003"),
                ("Cool, Cool Mountain", "0x00000004"),
                ("Big Boo's Haunt", "0x00000005"),
                ("Hazy Maze Cave", "0x00000006"),
                ("Lethal Lava Land", "0x00000007"),
                ("Shifting Sand Land", "0x00000008"),
                ("Dire, Dire Docks", "0x00000009"),
                ("Snowman's Land", "0x0000000A"),
                ("Wet-Dry World", "0x0000000B"),
                ("Tall, Tall Mountain", "0x0000000C"),
                ("Tiny-Huge Island", "0x0000000D"),
                ("Tick Tock Clock", "0x0000000E"),
                ("Rainbow Ride", "0x0000000F"),
                ("Bowser in the Dark World", "0x00000016"),
                ("Bowser in the Fire Sea", "0x00000017"),
                ("Bowser in the Sky", "0x00000018"),
                ("Castle Grounds", "0x00000010"),
                ("Castle Interior", "0x00000012"),
                ("Castle Courtyard", "0x00000013"),
                ("Castle Secret Stars", "0x0000001A"),
                ("The End (Credits)", "0x0000001C"),
            ]
            for lname, lcode in level_names:
                self.tree.insert(levels, "end",
                                 text=f"   {lname}  [{lcode}]",
                                 tags=("level",))

            assets = self.tree.insert(root, "end", text="🎨 Assets")
            self.tree.insert(assets, "end", text="   3D Models (Geo Layouts)", tags=("asset",))
            self.tree.insert(assets, "end", text="   Textures", tags=("asset",))
            self.tree.insert(assets, "end", text="   Audio / Sequences", tags=("asset",))
            self.tree.insert(assets, "end", text="   Collision Data", tags=("asset",))
        else:
            self.tree.insert(root, "end", text="📄 Raw Binary Data",
                             tags=("binary",))

    # ──────────── HEX VIEWER ────────────

    def _schedule_hex_update(self):
        """Defer hex update so the GUI stays responsive."""
        if self._hex_update_job:
            self.after_cancel(self._hex_update_job)
        self._hex_update_job = self.after(50, self._update_hex_dump)

    def _update_hex_dump(self):
        self._hex_update_job = None
        self.hex_text.config(state=tk.NORMAL)
        self.hex_text.delete("1.0", tk.END)

        if not self.rom_data:
            self.hex_text.config(state=tk.DISABLED)
            return

        display_len = min(len(self.rom_data), 4096)
        chunk = self.rom_data[0:display_len]

        for i in range(0, len(chunk), 16):
            row = chunk[i:i + 16]

            # Offset
            self.hex_text.insert(tk.END, f"{i:08X}  ", "offset")

            # Hex bytes — highlight header region
            for j, b in enumerate(row):
                tag = "header_highlight" if (i + j) < 0x40 else "hex"
                if self.is_sm64 and i == 0 and j < 4:
                    tag = "sm64_magic"
                self.hex_text.insert(tk.END, f"{b:02X}", tag)
                if j < 15:
                    self.hex_text.insert(tk.END, " ", "dot")

            # Padding
            pad = 16 - len(row)
            if pad > 0:
                self.hex_text.insert(tk.END, "   " * pad, "dot")

            # Separator
            self.hex_text.insert(tk.END, "  │", "separator_line")

            # ASCII
            for b in row:
                if 32 <= b <= 126:
                    self.hex_text.insert(tk.END, chr(b), "ascii")
                else:
                    self.hex_text.insert(tk.END, ".", "dot")

            self.hex_text.insert(tk.END, "│", "separator_line")
            self.hex_text.insert(tk.END, "\n")

        if len(self.rom_data) > 4096:
            self.hex_text.insert(tk.END, "\n", "dot")
            self.hex_text.insert(
                tk.END,
                f"  ... showing first 4KB of {len(self.rom_data):,} bytes total ...\n",
                "dot"
            )

        self.hex_text.config(state=tk.DISABLED)

    # ──────────── TREE EVENTS ────────────

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        text = self.tree.item(sel[0], "text")
        tags = self.tree.item(sel[0], "tags")

        if "level" in tags:
            self.context_var.set(
                f"Selected: {text.strip()}\n\n"
                "Level editing requires MIO0 decompression\n"
                "and a 3D renderer — planned for future versions."
            )
        elif "segment" in tags:
            self.context_var.set(
                f"{text.strip()}\n\n"
                "Segments contain compressed game data.\n"
                "Decompression support coming in v0.2."
            )
        elif "header" in tags:
            self.context_var.set(
                f"{text.strip()}\n\n"
                "The N64 header contains the game title,\n"
                "checksums, entry point, and boot configuration.\n"
                "Header bytes 0x00–0x3F are highlighted in the hex viewer."
            )
        elif "asset" in tags:
            self.context_var.set(
                f"{text.strip()}\n\n"
                "Asset extraction requires format-specific parsers.\n"
                "Planned for future releases."
            )
        else:
            self.context_var.set("Select an item in the tree to see details.")

        self.status_var.set(f"Selected: {text.strip()}")

    # ──────────── MISC ────────────

    def not_implemented(self):
        messagebox.showinfo(
            "Coming Soon",
            "This feature is planned for a future version of\n"
            "AC'S SM64 TWEAKER.\n\n"
            "Currently implemented:\n"
            "  ✓ ROM loading (z64/v64/n64)\n"
            "  ✓ Auto byte/word swapping\n"
            "  ✓ Header parsing\n"
            "  ✓ Syntax-highlighted hex viewer\n"
            "  ✓ ROM extending (8MB → 32MB)\n"
            "  ✓ Save / Save As"
        )

    def show_about(self):
        messagebox.showinfo(
            "About AC'S SM64 TWEAKER",
            "AC'S SM64 TWEAKER 0.1\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "A dark-themed Super Mario 64 ROM manager\n"
            "built with Python 3.14+ and Tkinter.\n\n"
            "Features:\n"
            "  • Real ROM parsing & format detection\n"
            "  • Auto endianness correction\n"
            "  • Syntax-highlighted hex viewer\n"
            "  • ROM extending to 32MB\n"
            "  • Full save/export support\n\n"
            "Made with 💙 for the SM64 modding community."
        )


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = ACTweakerGUI()
    app.mainloop()
