#!/usr/bin/env python3
"""
AC'S TWEAKER SM64 — TT64 shell + SM64 ROM Manager core
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GUI workflow follows **Toad's Tool 64** (level tree, 3D viewport
region, bottom inspector tabs). All ROM surgery uses the in-file
**SM64RomManagerEngine** (endian normalize, CIC-6102 CRC, extend,
verify) — same responsibilities as SM64 ROM Manager, not its UI.

Copyright (C) 1999–2026 A.C Holdings / Team Flames
Built with Python 3.14+ and Tkinter.

Features:
  • TT64-style layout: tree | 3D view | bottom tabs
  • SM64RomManagerEngine: header parse, z64/v64/n64, CRC, extend
  • Built-in patch library (60 FPS, Widescreen, etc.)
  • Hex editor, level script disasm, segment table (US v1.0)
  • Full Save / Save As / Export header
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import struct
import os
import sys
import hashlib
import copy

# ════════════════════════════════════════════════════════════════
#  VERSION
# ════════════════════════════════════════════════════════════════
APP_TITLE   = "Toad's Tool 64 — AC Tweaker"
APP_VERSION = "1.0"
APP_FULL    = f"{APP_TITLE}  (ROM Manager core v{APP_VERSION})"
APP_WINDOW_TITLE = "AC SM64 TWEAKER 0.1 "
APP_COPY    = "© 1999–2026 A.C Holdings / Team Flames"
TT64_SHELL_NOTE = (
    "Layout: Toad's Tool 64–style (tree, 3D pane, bottom tabs). "
    "ROM logic: SM64 ROM Manager–compatible engine in this file."
)

# ════════════════════════════════════════════════════════════════
#  COLOR PALETTE — TT64 Dark Revival
# ════════════════════════════════════════════════════════════════
# Inspired by Toad's Tool 64 layout, ported to a modern dark theme

# ── Surfaces ──
C_BG            = "#1a1a2e"      # Main background (deep navy)
C_BG_ALT        = "#16213e"      # Alternate panels
C_BG_RAISED     = "#1f2b47"      # Raised surfaces / cards
C_BG_INPUT      = "#0f1629"      # Input fields / text areas
C_BG_VIEWPORT   = "#0a0e1a"      # 3D viewport area (darkest)
C_BG_TOOLBAR    = "#12192d"      # Toolbar strip
C_BG_STATUSBAR  = "#0d1221"      # Status bar

# ── Borders ──
C_BORDER        = "#2a3a5c"      # Default border
C_BORDER_FOCUS  = "#4a7dff"      # Focused element
C_BORDER_SUBTLE = "#1e2d4a"      # Subtle dividers

# ── Text ──
C_TEXT          = "#d4dae8"      # Primary text
C_TEXT_DIM      = "#8892a8"      # Secondary text
C_TEXT_MUTED    = "#4a5568"      # Disabled / placeholder
C_TEXT_BRIGHT   = "#f0f4ff"      # Emphasized text

# ── Accents ──
C_ACCENT        = "#4a7dff"      # Primary accent (TT64 blue)
C_ACCENT_HOVER  = "#6b9aff"      # Accent hover
C_ACCENT_DIM    = "#2a4a8f"      # Muted accent

# ── Semantic ──
C_GREEN         = "#34d399"      # Success / SM64 detected
C_GREEN_DIM     = "#065f46"      # Green bg
C_RED           = "#f87171"      # Error / danger
C_RED_DIM       = "#7f1d1d"      # Red bg
C_YELLOW        = "#fbbf24"      # Warning / highlights
C_YELLOW_DIM    = "#78350f"      # Yellow bg
C_ORANGE        = "#fb923c"      # Caution
C_PURPLE        = "#a78bfa"      # Offsets / addresses
C_CYAN          = "#22d3ee"      # Special values
C_PINK          = "#f472b6"      # MIO0 / compressed

# ── Tree ──
C_TREE_SEL_BG   = "#1e3a6e"
C_TREE_SEL_FG   = "#6b9aff"

# ── Menu ──
C_MENU_BG       = "#151d33"
C_MENU_ACTIVE   = "#1e3a6e"

# ── Tabs ──
C_TAB_ACTIVE    = "#1a1a2e"
C_TAB_INACTIVE  = "#12192d"

# ── Hex View ──
C_HEX_OFFSET    = "#a78bfa"
C_HEX_BYTE      = "#d4dae8"
C_HEX_ASCII     = "#34d399"
C_HEX_DOT       = "#4a5568"
C_HEX_HEADER    = "#fbbf24"
C_HEX_MAGIC     = "#34d399"
C_HEX_MODIFIED  = "#f87171"
C_HEX_SEPARATOR = "#2a3a5c"

# ── Scrollbar ──
C_SCROLL_BG     = "#12192d"
C_SCROLL_THUMB  = "#2a3a5c"

# ════════════════════════════════════════════════════════════════
#  SM64 DATA TABLES  (SM64 ROM Manager compatible)
# ════════════════════════════════════════════════════════════════

# Known SM64 ROM checksums (US v1.0)
SM64_CHECKSUMS = {
    "US":   {"crc1": 0x3CE60709, "crc2": 0x2C9CDFEF},
    "JP":   {"crc1": 0xD6FBA4A8, "crc2": 0x337EEBE3},
    "EU":   {"crc1": 0xB98BA192, "crc2": 0x042C7D05},
    "SH":   {"crc1": 0xCFD5E95A, "crc2": 0x72F65EE3},
}

# SM64 level data table — matches Toad's Tool 64 layout
SM64_LEVELS = [
    # (ID, Name, Category, Script Offset US, Area Count)
    (0x09, "Bob-omb Battlefield",       "Course",   0x00E6D0, 1),
    (0x18, "Whomp's Fortress",          "Course",   0x00E930, 1),
    (0x0C, "Jolly Roger Bay",           "Course",   0x00EA34, 2),
    (0x05, "Cool, Cool Mountain",       "Course",   0x00EB2C, 2),
    (0x04, "Big Boo's Haunt",           "Course",   0x00EC58, 1),
    (0x07, "Hazy Maze Cave",            "Course",   0x00EDE0, 2),
    (0x16, "Lethal Lava Land",          "Course",   0x00EF28, 2),
    (0x08, "Shifting Sand Land",        "Course",   0x00F044, 2),
    (0x17, "Dire, Dire Docks",          "Course",   0x00F178, 2),
    (0x0A, "Snowman's Land",            "Course",   0x00F280, 2),
    (0x0B, "Wet-Dry World",             "Course",   0x00F38C, 1),
    (0x24, "Tall, Tall Mountain",       "Course",   0x00F474, 2),
    (0x0D, "Tiny-Huge Island",          "Course",   0x00F578, 3),
    (0x0E, "Tick Tock Clock",           "Course",   0x00F6B0, 1),
    (0x0F, "Rainbow Ride",              "Course",   0x00F7A0, 1),

    # Secret / Cap Stages
    (0x1C, "Tower of the Wing Cap",     "Secret",   0x010258, 1),
    (0x1D, "Cavern of the Metal Cap",   "Secret",   0x010368, 1),
    (0x12, "Vanish Cap under the Moat", "Secret",   0x010478, 1),
    (0x1B, "The Princess's Secret Slide","Secret",  0x00FA60, 1),
    (0x14, "The Secret Aquarium",       "Secret",   0x00FB54, 1),
    (0x1F, "Wing Mario over the Rainbow","Secret",  0x010534, 1),

    # Bowser Stages
    (0x11, "Bowser in the Dark World",  "Bowser",   0x00FC48, 2),
    (0x13, "Bowser in the Fire Sea",    "Bowser",   0x00FD78, 2),
    (0x15, "Bowser in the Sky",         "Bowser",   0x00FEA8, 2),

    # Castle
    (0x10, "Castle Grounds",            "Castle",   0x00F898, 1),
    (0x06, "Castle Interior",           "Castle",   0x00F998, 3),
    (0x1A, "Castle Courtyard",          "Castle",   0x010128, 1),

    # Misc
    (0x1E, "Ending / Cake Screen",      "Misc",     0x010624, 1),
]

# SM64 segment table offsets (US v1.0 ROM)
SM64_SEGMENTS_US = {
    0x02: ("Segment 02 – Level Geometry",      0x00108A40, 0x0012A0C0),
    0x04: ("Segment 04 – Goddard / Title",     0x000F5580, 0x000F7990),
    0x05: ("Segment 05 – Behavior Scripts",    0x000F7990, 0x000FCE50),
    0x06: ("Segment 06 – Global Textures",     0x00114750, 0x001178A0),
    0x07: ("Segment 07 – Level-specific GFX",  0x000E84D0, 0x000F1610),
    0x08: ("Segment 08 – Common0 MIO0",        0x00080820, 0x000B6A10),
    0x09: ("Segment 09 – Common0 Geo",         0x000B6A10, 0x000C56D0),
    0x0A: ("Segment 0A – Common1 MIO0",        0x000C56D0, 0x000CA090),
    0x0B: ("Segment 0B – Common1 Geo",         0x000CA090, 0x000CC540),
    0x0C: ("Segment 0C – Group 0–17 MIO0",     0x000CC540, 0x000E84D0),
    0x0D: ("Segment 0D – Group Geo",           0x000F1610, 0x000F5580),
    0x0E: ("Segment 0E – Level-specific MIO0", 0x00108A40, 0x00114750),
    0x0F: ("Segment 0F – Level Collision",     0x001178A0, 0x0012A0C0),
    0x13: ("Segment 13 – Animation Table",     0x006D4E80, 0x006F5750),
    0x14: ("Segment 14 – Demo / Intro Data",   0x007CC620, 0x007CE090),
    0x15: ("Segment 15 – Menu GFX",            0x007CE090, 0x007D7920),
}

# Patch library — built-in SM64 binary patches
SM64_PATCHES = [
    {
        "name": "60 FPS (US v1.0)",
        "desc": "Doubles the frame rate from 30 to 60 FPS.\n"
                "Some animations may play at 2× speed.",
        "category": "Performance",
        "offset": 0x32AB94,
        "original": bytes([0x08, 0x00]),
        "patched":  bytes([0x04, 0x00]),
        "region": "US",
    },
    {
        "name": "Infinite Lives",
        "desc": "Mario always has 99 lives.\n"
                "Life count never decreases.",
        "category": "Gameplay",
        "offset": 0x3D1BC,
        "original": bytes([0x24, 0x02, 0x00, 0x04]),
        "patched":  bytes([0x24, 0x02, 0x00, 0x63]),
        "region": "US",
    },
    {
        "name": "Always Metal Cap",
        "desc": "Mario is always in Metal Cap form.\n"
                "Invulnerable and walks underwater.",
        "category": "Gameplay",
        "offset": 0x12C470,
        "original": bytes([0x00, 0x00, 0x00, 0x00]),
        "patched":  bytes([0x00, 0x00, 0x00, 0x04]),
        "region": "US",
    },
    {
        "name": "Moon Jump (L Trigger)",
        "desc": "Hold L to fly upward continuously.",
        "category": "Gameplay",
        "offset": 0x6C26C,
        "original": bytes([0x05, 0x40, 0x00, 0x03]),
        "patched":  bytes([0x05, 0x40, 0x00, 0x07]),
        "region": "US",
    },
    {
        "name": "Disable Fall Damage",
        "desc": "Mario never takes damage from falling.\n"
                "Safe for speedrun practice.",
        "category": "Gameplay",
        "offset": 0x35934,
        "original": bytes([0x54, 0x22, 0x00, 0x3C]),
        "patched":  bytes([0x10, 0x00, 0x00, 0x07]),
        "region": "US",
    },
    {
        "name": "Widescreen 16:9",
        "desc": "Changes the aspect ratio to 16:9.\n"
                "Objects may pop in closer to edges.",
        "category": "Display",
        "offset": 0x3829E,
        "original": bytes([0x3F, 0x00]),
        "patched":  bytes([0x3F, 0x2B]),
        "region": "US",
    },
]

# SM64 level script commands (for disassembly)
LEVELSCRIPT_CMDS = {
    0x00: ("LOAD_RAW",           8),
    0x01: ("LOAD_MIO0",          8),
    0x02: ("LOAD_MARIO",        12),
    0x03: ("LOAD_FUNC",         8),
    0x05: ("JUMP_ROM",          8),
    0x06: ("JUMP_PUSH",         8),
    0x07: ("RETURN",            4),
    0x08: ("CALL_FUNC",         8),
    0x09: ("CALL_COND_FUNC",   12),
    0x0A: ("CALL_COND_LOOP",   12),
    0x0C: ("COND_POP",          4),
    0x0D: ("COND_SKIP",         8),
    0x0E: ("SKIP_NEXT",         4),
    0x0F: ("SKIP_NOP",          4),
    0x10: ("CLEAR_LEVEL",       4),
    0x11: ("CLEAR_TRIGGER",     4),
    0x12: ("SET_REGISTER",      4),
    0x13: ("PUSH_POOL",         4),
    0x14: ("POP_POOL",          4),
    0x15: ("FIXED_POOL",        8),
    0x16: ("LOAD_SEGMENT",     16),
    0x17: ("LOAD_MIO0_TEX",    16),
    0x18: ("LOAD_LVL_SEG",     16),
    0x19: ("SET_MARIO_POS",    12),
    0x1A: ("LOAD_AREA",         4),
    0x1B: ("UNLOAD_AREA",       4),
    0x1C: ("SET_AREA_ATTR",     8),
    0x1D: ("SET_OBJECT",       24),
    0x1E: ("SET_TERRAIN",       8),
    0x1F: ("SET_ROOMS",         8),
    0x20: ("SHOW_DIALOG",       8),
    0x21: ("SET_TERRAIN_TYPE",  8),
    0x22: ("NOP22",             4),
    0x23: ("FADE_COLOR",       12),
    0x24: ("SET_BLACKOUT",      4),
    0x25: ("SET_MUSIC",         8),
    0x26: ("SET_MENU_MUSIC",    4),
    0x27: ("FADE_BSS_SEQ",      4),
    0x28: ("SET_ECHO",          8),
    0x2B: ("SET_WHIRLPOOL",    12),
    0x2C: ("GET_OR_SET",        8),
    0x2D: ("ADV_DEMO",          4),
    0x2E: ("CLEAR_DEMO_PTR",    4),
    0x2F: ("JUMP_AREA_PUSH",    8),
    0x30: ("SET_TRANSITION",    8),
    0x31: ("SET_MARIO_DEFAULT", 12),
    0x33: ("SHOW_STAR_SEL",     4),
    0x36: ("LOAD_MIO0_SEG",    16),
    0x37: ("PLACE_OBJECT",     24),
    0x39: ("TERRAIN_LOAD_ENV",  8),
    0x3B: ("JET_STREAM",       12),
}


# ════════════════════════════════════════════════════════════════
#  SM64 CRC ALGORITHM  (N64 boot checksum)
# ════════════════════════════════════════════════════════════════

def sm64_recalc_checksum(rom: bytearray) -> tuple:
    """
    Recalculate N64 ROM CRC checksums using the CIC-6102 seed.
    This matches SM64 ROM Manager's checksum fix behavior.
    Returns (crc1, crc2).
    """
    if len(rom) < 0x101000:
        return (0, 0)

    CIC_SEED = 0xF8CA4DDC  # CIC-6102 (SM64, Zelda OoT, etc.)
    t1 = t2 = t3 = t4 = t5 = t6 = CIC_SEED
    MASK = 0xFFFFFFFF

    for i in range(0x1000, 0x101000, 4):
        d = struct.unpack_from('>I', rom, i)[0]

        r = (t6 + d) & MASK
        if r < t6:
            t4 = (t4 + 1) & MASK
        t6 = r

        t3 ^= d

        shift = d & 0x1F
        r = ((d << shift) | (d >> (32 - shift))) & MASK
        t5 = (t5 + r) & MASK

        if t2 > d:
            t2 ^= r
        else:
            t2 ^= (t6 ^ d) & MASK

        t1 = (t1 + (d ^ t5)) & MASK

    crc1 = (t6 ^ t4 ^ t3) & MASK
    crc2 = (t5 ^ t2 ^ t1) & MASK
    return crc1, crc2


# ════════════════════════════════════════════════════════════════
#  SM64 ROM MANAGER ENGINE  (logic only — TT64-style GUI uses this)
# ════════════════════════════════════════════════════════════════

class SM64RomManagerEngine:
    """
    SM64 ROM Manager–compatible operations: endian normalization,
    N64 header fields, CIC-6102 CRC recompute, extend, verify.
    Mutates the caller's bytearray where noted.
    """

    REGION_MAP = {
        0x45: "NTSC-U (USA)", 0x4A: "NTSC-J (Japan)",
        0x50: "PAL (Europe)",  0x55: "NTSC-A (Australia)",
        0x44: "PAL-D (Germany)", 0x46: "PAL-F (France)",
    }

    @classmethod
    def normalize_endian(cls, rom: bytearray) -> tuple:
        """
        Detect and convert ROM to big-endian (.z64) in place.
        Returns (format_description, list of short log lines).
        """
        logs = []
        if len(rom) < 4:
            return "Unknown", logs

        magic = bytes(rom[0:4])

        if magic == b'\x80\x37\x12\x40':
            return "Big Endian (.z64)", logs

        if magic == b'\x37\x80\x40\x12':
            logs.append("Converting .v64 → .z64 (byte-swap)…")
            for i in range(0, len(rom), 2):
                rom[i], rom[i + 1] = rom[i + 1], rom[i]
            return "Byte-Swapped (.v64 → .z64)", logs

        if magic == b'\x40\x12\x37\x80':
            logs.append("Converting .n64 → .z64 (word-swap)…")
            for i in range(0, len(rom), 4):
                rom[i:i + 4] = rom[i:i + 4][::-1]
            return "Little Endian (.n64 → .z64)", logs

        return f"Unknown (0x{magic.hex().upper()})", logs

    @classmethod
    def analyze(cls, rom: bytearray) -> dict:
        """Parse header + SM64 detection; does not modify ROM."""
        empty = {
            "crc1": 0, "crc2": 0, "entry": 0, "title": "",
            "region": "—", "is_sm64": False, "rom_region": "Unknown",
            "crc_ok": False, "md5": "", "extended": "—",
        }
        if len(rom) < 0x40:
            return empty

        crc1 = struct.unpack('>I', rom[0x10:0x14])[0]
        crc2 = struct.unpack('>I', rom[0x14:0x18])[0]
        entry = struct.unpack('>I', rom[0x08:0x0C])[0]
        title = rom[0x20:0x34].decode('ascii', errors='ignore').strip()
        rc = rom[0x3E] if len(rom) > 0x3E else 0
        region = cls.REGION_MAP.get(rc, f"Unknown (0x{rc:02X})")

        title_u = title.upper()
        is_sm64 = "MARIO" in title_u and "SUPER" in title_u

        rom_region = "Unknown"
        for rname, crcs in SM64_CHECKSUMS.items():
            if crc1 == crcs["crc1"] and crc2 == crcs["crc2"]:
                rom_region = rname
                break

        calc1, calc2 = sm64_recalc_checksum(rom)
        crc_ok = (calc1 == crc1 and calc2 == crc2)
        md5 = hashlib.md5(rom).hexdigest().upper()

        sz = len(rom)
        sz_mb = sz / (1024 * 1024)
        if sz >= 64 * 1024 * 1024:
            ext = "Yes (64 MB)"
        elif sz >= 32 * 1024 * 1024:
            ext = "Yes (32 MB)"
        elif sz >= 24 * 1024 * 1024:
            ext = "Yes (24 MB)"
        elif sz <= 8 * 1024 * 1024 + 1:
            ext = "No (8 MB stock)"
        else:
            ext = f"Custom ({sz_mb:.1f} MB)"

        return {
            "crc1": crc1, "crc2": crc2, "entry": entry, "title": title or "UNKNOWN",
            "region": region, "is_sm64": is_sm64, "rom_region": rom_region,
            "crc_ok": crc_ok, "md5": md5, "extended": ext,
            "size_bytes": sz, "size_mb": sz_mb,
        }

    @staticmethod
    def write_crc(rom: bytearray) -> tuple:
        """Recompute CIC-6102 CRC and write ROM header 0x10–0x17."""
        crc1, crc2 = sm64_recalc_checksum(rom)
        struct.pack_into('>I', rom, 0x10, crc1)
        struct.pack_into('>I', rom, 0x14, crc2)
        return crc1, crc2

    @staticmethod
    def extend(rom: bytearray, target_mb: int, pad_byte: int = 0x01) -> int:
        """
        Pad ROM to target_mb with pad_byte (SM64 ROM Manager style).
        Returns new length, or raises ValueError if invalid.
        """
        target = target_mb * 1024 * 1024
        cur = len(rom)
        if cur >= target:
            return cur
        rom.extend(bytes([pad_byte & 0xFF]) * (target - cur))
        return len(rom)

    @staticmethod
    def verify(rom: bytearray) -> dict:
        """Stored vs calculated CRC; MD5/SHA1 for tooling."""
        c1s = struct.unpack('>I', rom[0x10:0x14])[0]
        c2s = struct.unpack('>I', rom[0x14:0x18])[0]
        c1c, c2c = sm64_recalc_checksum(rom)
        return {
            "crc1_stored": c1s, "crc2_stored": c2s,
            "crc1_calc": c1c, "crc2_calc": c2c,
            "ok": (c1s == c1c and c2s == c2c),
            "md5": hashlib.md5(rom).hexdigest().upper(),
            "sha1": hashlib.sha1(rom).hexdigest().upper(),
            "size": len(rom),
        }


# ════════════════════════════════════════════════════════════════
#  TTK DARK STYLE — TT64 Dark Revival
# ════════════════════════════════════════════════════════════════

class TT64DarkStyle(ttk.Style):
    """Toad's Tool 64–inspired dark theme for ttk widgets."""

    def __init__(self, root):
        super().__init__(root)
        self.theme_use("clam")
        self._apply()

    def _apply(self):
        # ── Global ──
        self.configure(".",
            background=C_BG, foreground=C_TEXT,
            bordercolor=C_BORDER, darkcolor=C_BG_ALT,
            lightcolor=C_BG_RAISED, troughcolor=C_BG_INPUT,
            fieldbackground=C_BG_INPUT,
            font=("Segoe UI", 10))
        self.map(".",
            foreground=[("disabled", C_TEXT_MUTED)],
            background=[("disabled", C_BG_ALT)])

        # ── Frames ──
        self.configure("TFrame", background=C_BG)
        self.configure("Toolbar.TFrame", background=C_BG_TOOLBAR)
        self.configure("Viewport.TFrame", background=C_BG_VIEWPORT)
        self.configure("Card.TFrame", background=C_BG_RAISED)
        self.configure("Status.TFrame", background=C_BG_STATUSBAR)
        self.configure("Props.TFrame", background=C_BG_ALT)

        # ── Labels ──
        for name, bg, fg, font in [
            ("TLabel",           C_BG,          C_TEXT,       ("Segoe UI", 10)),
            ("Bold.TLabel",      C_BG,          C_TEXT_BRIGHT,("Segoe UI", 10, "bold")),
            ("Dim.TLabel",       C_BG,          C_TEXT_DIM,   ("Segoe UI", 9)),
            ("Muted.TLabel",     C_BG,          C_TEXT_MUTED, ("Segoe UI", 9, "italic")),
            ("Status.TLabel",    C_BG_STATUSBAR,C_TEXT_DIM,   ("Consolas", 9)),
            ("Accent.TLabel",    C_BG,          C_ACCENT,     ("Segoe UI", 10, "bold")),
            ("Green.TLabel",     C_BG,          C_GREEN,      ("Segoe UI", 10, "bold")),
            ("Red.TLabel",       C_BG,          C_RED,        ("Segoe UI", 10, "bold")),
            ("Brand.TLabel",     C_BG_TOOLBAR,  C_ACCENT,     ("Consolas", 12, "bold")),
            ("BrandDim.TLabel",  C_BG_TOOLBAR,  C_TEXT_DIM,   ("Consolas", 10)),
            ("BrandVer.TLabel",  C_BG_TOOLBAR,  C_GREEN,      ("Consolas", 10, "bold")),
            ("Header.TLabel",    C_BG,          C_ACCENT,     ("Segoe UI", 12, "bold")),
            ("Section.TLabel",   C_BG,          C_TEXT_DIM,   ("Segoe UI", 8, "bold")),
            ("PropKey.TLabel",   C_BG_ALT,      C_TEXT_DIM,   ("Segoe UI", 9)),
            ("PropVal.TLabel",   C_BG_ALT,      C_TEXT_BRIGHT,("Consolas", 10)),
            ("CardTitle.TLabel", C_BG_RAISED,   C_ACCENT,     ("Segoe UI", 10, "bold")),
            ("CardBody.TLabel",  C_BG_RAISED,   C_TEXT,       ("Segoe UI", 9)),
            ("PatchName.TLabel", C_BG_RAISED,   C_TEXT_BRIGHT,("Segoe UI", 10, "bold")),
            ("PatchDesc.TLabel", C_BG_RAISED,   C_TEXT_DIM,   ("Segoe UI", 9)),
            ("PatchCat.TLabel",  C_BG_RAISED,   C_CYAN,       ("Consolas", 8, "bold")),
            ("ViewLabel.TLabel", C_BG_VIEWPORT, C_TEXT_MUTED, ("Segoe UI", 9)),
        ]:
            self.configure(name, background=bg, foreground=fg, font=font)

        # ── Buttons ──
        self.configure("TButton",
            background=C_BG_RAISED, foreground=C_TEXT,
            bordercolor=C_BORDER, lightcolor=C_BG_RAISED,
            darkcolor=C_BG_ALT, font=("Segoe UI", 9), padding=(10, 5))
        self.map("TButton",
            background=[("active", C_BORDER), ("pressed", C_ACCENT)],
            foreground=[("active", C_TEXT_BRIGHT), ("pressed", "#fff")],
            bordercolor=[("focus", C_ACCENT)])

        self.configure("Accent.TButton",
            background=C_ACCENT, foreground="#fff",
            bordercolor=C_ACCENT, font=("Segoe UI", 9, "bold"), padding=(12, 6))
        self.map("Accent.TButton",
            background=[("active", C_ACCENT_HOVER), ("pressed", "#2563eb")])

        self.configure("Danger.TButton",
            background=C_RED_DIM, foreground=C_RED,
            bordercolor="#991b1b", font=("Segoe UI", 9, "bold"), padding=(10, 5))
        self.map("Danger.TButton",
            background=[("active", "#991b1b"), ("pressed", C_RED)],
            foreground=[("active", "#fff"), ("pressed", "#fff")])

        self.configure("Tool.TButton",
            background=C_BG_TOOLBAR, foreground=C_TEXT_DIM,
            bordercolor=C_BORDER_SUBTLE, font=("Segoe UI", 9), padding=(8, 4))
        self.map("Tool.TButton",
            background=[("active", C_BG_RAISED), ("pressed", C_ACCENT)],
            foreground=[("active", C_TEXT_BRIGHT), ("pressed", "#fff")])

        self.configure("Patch.TButton",
            background=C_ACCENT_DIM, foreground=C_ACCENT_HOVER,
            bordercolor=C_ACCENT, font=("Segoe UI", 8, "bold"), padding=(8, 3))
        self.map("Patch.TButton",
            background=[("active", C_ACCENT), ("pressed", "#2563eb")],
            foreground=[("active", "#fff"), ("pressed", "#fff")])

        self.configure("PatchUndo.TButton",
            background=C_BG_RAISED, foreground=C_YELLOW,
            bordercolor=C_YELLOW_DIM, font=("Segoe UI", 8, "bold"), padding=(8, 3))
        self.map("PatchUndo.TButton",
            background=[("active", C_YELLOW_DIM), ("pressed", C_YELLOW)],
            foreground=[("active", C_YELLOW), ("pressed", "#000")])

        # ── Separator ──
        self.configure("TSeparator", background=C_BORDER)
        self.configure("Tool.TSeparator", background=C_BORDER_SUBTLE)

        # ── Notebook ──
        self.configure("TNotebook",
            background=C_BG, bordercolor=C_BORDER, tabmargins=(0, 0, 0, 0))
        self.configure("TNotebook.Tab",
            background=C_TAB_INACTIVE, foreground=C_TEXT_DIM,
            bordercolor=C_BORDER, padding=(14, 7), font=("Segoe UI", 9))
        self.map("TNotebook.Tab",
            background=[("selected", C_TAB_ACTIVE), ("active", C_BG_RAISED)],
            foreground=[("selected", C_ACCENT), ("active", C_TEXT)],
            bordercolor=[("selected", C_ACCENT)])

        # ── Treeview ──
        self.configure("Treeview",
            background=C_BG, foreground=C_TEXT,
            fieldbackground=C_BG, bordercolor=C_BORDER,
            rowheight=26, font=("Segoe UI", 9))
        self.map("Treeview",
            background=[("selected", C_TREE_SEL_BG)],
            foreground=[("selected", C_TREE_SEL_FG)])
        self.configure("Treeview.Heading",
            background=C_BG_RAISED, foreground=C_TEXT_DIM,
            bordercolor=C_BORDER, font=("Segoe UI", 9, "bold"))
        self.map("Treeview.Heading",
            background=[("active", C_BORDER)],
            foreground=[("active", C_TEXT)])

        # ── Scrollbar ──
        for orient in ("Vertical", "Horizontal"):
            self.configure(f"{orient}.TScrollbar",
                background=C_SCROLL_BG, troughcolor=C_BG,
                bordercolor=C_BORDER, arrowcolor=C_TEXT_DIM)
            self.map(f"{orient}.TScrollbar",
                background=[("active", C_SCROLL_THUMB)])

        # ── PanedWindow ──
        self.configure("TPanedwindow", background=C_BG, bordercolor=C_BORDER)

        # ── LabelFrame ──
        self.configure("TLabelframe", background=C_BG,
            bordercolor=C_BORDER, darkcolor=C_BG_ALT,
            lightcolor=C_BG_RAISED)
        self.configure("TLabelframe.Label",
            background=C_BG, foreground=C_ACCENT,
            font=("Segoe UI", 9, "bold"))

        # ── Entry ──
        self.configure("TEntry",
            fieldbackground=C_BG_INPUT, foreground=C_TEXT,
            bordercolor=C_BORDER, insertcolor=C_TEXT,
            font=("Consolas", 10))
        self.map("TEntry",
            bordercolor=[("focus", C_BORDER_FOCUS)],
            fieldbackground=[("focus", C_BG_INPUT)])

        # ── Checkbutton ──
        self.configure("TCheckbutton",
            background=C_BG, foreground=C_TEXT,
            indicatorcolor=C_BG_INPUT, font=("Segoe UI", 9))
        self.map("TCheckbutton",
            indicatorcolor=[("selected", C_ACCENT)],
            background=[("active", C_BG)])

        # ── Combobox ──
        self.configure("TCombobox",
            fieldbackground=C_BG_INPUT, foreground=C_TEXT,
            bordercolor=C_BORDER, arrowcolor=C_TEXT_DIM,
            font=("Consolas", 10))
        self.map("TCombobox",
            bordercolor=[("focus", C_BORDER_FOCUS)],
            fieldbackground=[("focus", C_BG_INPUT)])

        # ── Progressbar ──
        self.configure("TProgressbar",
            background=C_ACCENT, troughcolor=C_BG_INPUT,
            bordercolor=C_BORDER)


# ════════════════════════════════════════════════════════════════
#  MAIN APPLICATION — TT64 Layout
# ════════════════════════════════════════════════════════════════

def _actweaker_close_rom(app):
    """
    Close / clear ROM state. Kept as a module function so File → Close ROM
    and the toolbar do not use ``self.cmd_close_rom`` when building menus:
    on some Python 3.14 + tk.Tk setups, ``Tk.__getattr__`` delegates to the
    Tcl layer before the subclass method is visible during callback wiring.
    """
    if app.rom_data and app.rom_backup and app.rom_data != app.rom_backup:
        if not messagebox.askyesno(
                "Close ROM",
                "Discard unsaved changes to the in-memory ROM?"):
            return
    app.loaded_path = None
    app.rom_data = bytearray()
    app.rom_backup = bytearray()
    app.is_sm64 = False
    app.rom_region = "Unknown"
    app.rom_format = ""
    app.applied_patches = set()
    app._hex_view_offset = 0

    for item in app.tree.get_children():
        app.tree.delete(item)

    app._ind_var.set("● NO ROM")
    app._ind_label.configure(foreground=C_RED)

    if getattr(app, "pv", None):
        for v in app.pv.values():
            v.set("—")

    app._ctx_var.set(
        "Open a Super Mario 64 ROM to mirror Toad's Tool 64 workflow.\n\n"
        f"{TT64_SHELL_NOTE}")
    app._viewport_msg.set(
        "No ROM loaded.\n\n"
        "Use File → Open ROM. The 3D pane is a TT64-style placeholder "
        "(no live geometry); use Level Script and Memory tabs for data.\n\n"
        + TT64_SHELL_NOTE)
    app._refresh_viewport_banner()
    app._schedule_hex()
    app._refresh_patch_status()
    app._set_status("ROM closed.")


class ACTweakerSM64(tk.Tk):
    """
    Toad's Tool 64–style window layout + SM64RomManagerEngine (ROM Manager logic).
    """

    def __init__(self):
        super().__init__()

        self.title(APP_WINDOW_TITLE)
        self.geometry("1240x820")
        self.minsize(960, 600)

        # ── Dark title bar (Windows 10/11) ──
        try:
            self.update_idletasks()
            if sys.platform == "win32":
                from ctypes import windll, c_int, byref, sizeof
                hwnd = windll.user32.GetParent(self.winfo_id())
                windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 20, byref(c_int(2)), sizeof(c_int))
        except Exception:
            pass

        self.configure(bg=C_BG)
        self._style = TT64DarkStyle(self)
        self.rom_engine = SM64RomManagerEngine()

        # ── State ──
        self.loaded_path = None
        self.rom_data = bytearray()
        self.rom_backup = bytearray()  # undo buffer
        self.is_sm64 = False
        self.rom_region = "Unknown"
        self.rom_format = ""
        self.applied_patches = set()
        self._hex_job = None
        self._hex_view_offset = 0
        self._hex_chunk_size = 0x1000  # 4 KB per page
        self._search_results = []
        self._search_idx = 0

        # ── Build UI ──
        self._create_menu()
        self._create_toolbar()
        self._create_main_panes()
        self._create_statusbar()

        # ── Keybinds ──
        self.bind_all("<Control-o>", lambda e: self.cmd_open())
        self.bind_all("<Control-s>", lambda e: self.cmd_save())
        self.bind_all("<Control-Shift-S>", lambda e: self.cmd_save_as())
        self.bind_all("<Control-g>", lambda e: self.cmd_hex_goto())
        self.bind_all("<Control-f>", lambda e: self.cmd_hex_search())
        self.bind_all("<Control-q>", lambda e: self.quit())

    # ────────────────────────────────────────────────
    #  MENU BAR  (TT64 layout)
    # ────────────────────────────────────────────────

    def _create_menu(self):
        mbar = tk.Menu(self, bg=C_MENU_BG, fg=C_TEXT,
                       activebackground=C_MENU_ACTIVE,
                       activeforeground=C_TREE_SEL_FG,
                       borderwidth=0, relief=tk.FLAT,
                       font=("Segoe UI", 9))
        self.config(menu=mbar)

        def _menu(**kw):
            return tk.Menu(mbar, tearoff=False, bg=C_MENU_BG, fg=C_TEXT,
                           activebackground=C_MENU_ACTIVE,
                           activeforeground=C_TREE_SEL_FG,
                           borderwidth=0, font=("Segoe UI", 9), **kw)

        # ── File  (Toad's Tool 64–style labels + ROM Manager actions) ──
        m_file = _menu()
        m_file.add_command(label="Open ROM…", command=self.cmd_open, accelerator="Ctrl+O")
        m_file.add_command(
            label="Close ROM",
            command=(lambda w=self: _actweaker_close_rom(w)))
        m_file.add_separator()
        m_file.add_command(label="Save ROM", command=self.cmd_save, accelerator="Ctrl+S")
        m_file.add_command(label="Save ROM As…", command=self.cmd_save_as,
                           accelerator="Ctrl+Shift+S")
        m_file.add_separator()
        m_file.add_command(label="Export Header (0x40 bytes)…", command=self.cmd_export_header)
        m_file.add_separator()
        m_file.add_command(label="Exit", command=self.quit, accelerator="Ctrl+Q")
        mbar.add_cascade(label="File", menu=m_file)

        # ── Edit  (TT64: ROM / memory helpers) ──
        m_edit = _menu()
        m_edit.add_command(label="Undo All Changes", command=self.cmd_undo_all)
        m_edit.add_separator()
        m_edit.add_command(label="Go to Offset in ROM…", command=self.cmd_hex_goto,
                           accelerator="Ctrl+G")
        m_edit.add_command(label="Find Bytes in ROM…", command=self.cmd_hex_search,
                           accelerator="Ctrl+F")
        mbar.add_cascade(label="Edit", menu=m_edit)

        # ── Level  (TT64) ──
        m_level = _menu()
        m_level.add_command(label="Go to Level Script in Hex", command=self.cmd_jump_level_script)
        m_level.add_command(label="View Level Objects…", command=self.cmd_view_objects)
        m_level.add_separator()
        m_level.add_command(label="Import Level…", command=self._not_impl)
        m_level.add_command(label="Export Level…", command=self._not_impl)
        mbar.add_cascade(label="Level", menu=m_level)

        # ── Textures  (TT64 placeholder — no software renderer) ──
        m_tex = _menu()
        m_tex.add_command(label="Texture Browser…", command=self._not_impl)
        m_tex.add_command(label="Replace Texture…", command=self._not_impl)
        mbar.add_cascade(label="Textures", menu=m_tex)

        # ── Tools  (ROM Manager engine) ──
        m_tools = _menu()
        m_tools.add_command(label="Fix N64 Checksum (CIC-6102)…", command=self.cmd_fix_crc)
        m_tools.add_separator()
        m_ext = _menu()
        m_ext.add_command(label="Extend to 24 MB", command=lambda: self.cmd_extend(24))
        m_ext.add_command(label="Extend to 32 MB", command=lambda: self.cmd_extend(32))
        m_ext.add_command(label="Extend to 64 MB", command=lambda: self.cmd_extend(64))
        m_tools.add_cascade(label="Extend ROM…", menu=m_ext)
        m_tools.add_separator()
        m_tools.add_command(label="Verify ROM (CRC / MD5 / SHA1)…", command=self.cmd_verify)
        m_tools.add_command(label="SM64 Region / CRC Table…", command=self.cmd_region_info)
        m_tools.add_separator()
        m_tools.add_command(label="Show Segment Table Tab", command=self.cmd_show_segments)
        mbar.add_cascade(label="Tools", menu=m_tools)

        # ── View  (TT64 + panels) ──
        m_view = _menu()
        m_view.add_command(
            label="Refresh 3D Pane Text",
            command=lambda: (self._refresh_viewport_banner(),
                             self._set_status("3D pane text refreshed.")))
        m_view.add_command(label="Refresh Hex Viewer", command=self._schedule_hex)
        m_view.add_command(label="Jump Hex to 0x00000000", command=lambda: self._hex_goto(0))
        m_view.add_separator()
        m_view.add_command(label="ROM Properties Tab", command=lambda: self.nb.select(self.tab_props))
        m_view.add_command(label="Hex Editor Tab", command=lambda: self.nb.select(self.tab_hex))
        m_view.add_command(label="Level Script Tab", command=lambda: self.nb.select(self.tab_script))
        mbar.add_cascade(label="View", menu=m_view)

        # ── Help ──
        m_help = _menu()
        m_help.add_command(label="About…", command=self.cmd_about)
        mbar.add_cascade(label="Help", menu=m_help)

    # ────────────────────────────────────────────────
    #  TOOLBAR  (TT64 style)
    # ────────────────────────────────────────────────

    def _create_toolbar(self):
        bar = ttk.Frame(self, style="Toolbar.TFrame", padding=(6, 3))
        bar.pack(side=tk.TOP, fill=tk.X)

        # Brand  (TT64-style primary label + ROM Manager subtitle)
        brand = ttk.Frame(bar, style="Toolbar.TFrame")
        brand.pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(brand, text="TT64", style="Brand.TLabel").pack(side=tk.LEFT)
        ttk.Label(brand, text=" Shell", style="BrandDim.TLabel").pack(side=tk.LEFT)
        ttk.Label(brand, text=" · ROM Mgr", style="BrandVer.TLabel").pack(side=tk.LEFT)

        ttk.Separator(bar, orient=tk.VERTICAL,
                       style="Tool.TSeparator").pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)

        # File  (classic TT64 toolbar cluster)
        ttk.Button(bar, text="Open ROM", style="Tool.TButton",
                   command=self.cmd_open).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Save ROM", style="Tool.TButton",
                   command=self.cmd_save).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Close", style="Tool.TButton",
                   command=(lambda w=self: _actweaker_close_rom(w))).pack(
                       side=tk.LEFT, padx=2)

        ttk.Separator(bar, orient=tk.VERTICAL,
                       style="Tool.TSeparator").pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)

        # ROM Manager tools
        ttk.Button(bar, text="Fix CRC", style="Tool.TButton",
                   command=self.cmd_fix_crc).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Extend 32MB", style="Tool.TButton",
                   command=lambda: self.cmd_extend(32)).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Verify", style="Tool.TButton",
                   command=self.cmd_verify).pack(side=tk.LEFT, padx=2)

        ttk.Separator(bar, orient=tk.VERTICAL,
                       style="Tool.TSeparator").pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)

        # Hex / memory nav  (TT64 “memory” workflow)
        ttk.Button(bar, text="⏮", style="Tool.TButton",
                   command=lambda: self._hex_goto(0)).pack(side=tk.LEFT, padx=1)
        ttk.Button(bar, text="◀", style="Tool.TButton",
                   command=self._hex_page_prev).pack(side=tk.LEFT, padx=1)
        ttk.Button(bar, text="▶", style="Tool.TButton",
                   command=self._hex_page_next).pack(side=tk.LEFT, padx=1)
        ttk.Button(bar, text="⏭", style="Tool.TButton",
                   command=self._hex_page_end).pack(side=tk.LEFT, padx=1)
        ttk.Button(bar, text="Go To…", style="Tool.TButton",
                   command=self.cmd_hex_goto).pack(side=tk.LEFT, padx=(4, 2))

        # Right indicator
        self._ind_var = tk.StringVar(value="● NO ROM")
        self._ind_label = ttk.Label(bar, textvariable=self._ind_var,
                                    style="BrandDim.TLabel",
                                    foreground=C_RED,
                                    font=("Consolas", 9, "bold"))
        self._ind_label.pack(side=tk.RIGHT, padx=8)

    # ────────────────────────────────────────────────
    #  MAIN LAYOUT — TT64 Three-Pane
    # ────────────────────────────────────────────────

    def _create_main_panes(self):
        """
        Toad's Tool 64 layout: narrow level tree (left), wide right stack:
        large 3D viewport on top, bottom notebook for scripts / ROM / memory.
        """
        outer = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        outer.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 0))

        # ═══ LEFT: Level tree  (TT64 “course / area” browser) ═══
        left = ttk.Frame(outer)
        outer.add(left, weight=0)

        ttk.Label(left, text="  LEVELS / SEGMENTS", style="Section.TLabel"
                  ).pack(anchor=tk.W, pady=(4, 2), padx=4)

        tree_box = ttk.Frame(left)
        tree_box.pack(fill=tk.BOTH, expand=True)

        ts = ttk.Scrollbar(tree_box, orient=tk.VERTICAL)
        ts.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree = ttk.Treeview(tree_box, yscrollcommand=ts.set,
                                 selectmode="browse", show="tree", height=22)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ts.config(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # ═══ RIGHT: TT64 vertical split  (3D viewport + bottom tabs) ═══
        right = ttk.Frame(outer)
        outer.add(right, weight=1)

        vpaned = ttk.PanedWindow(right, orient=tk.VERTICAL)
        vpaned.pack(fill=tk.BOTH, expand=True)

        vp_outer = ttk.Frame(vpaned, style="Viewport.TFrame")
        vpaned.add(vp_outer, weight=5)
        self._build_tt64_viewport(vp_outer)

        bottom = ttk.Frame(vpaned)
        vpaned.add(bottom, weight=4)

        self.nb = ttk.Notebook(bottom)
        self.nb.pack(fill=tk.BOTH, expand=True)

        # Bottom tabs — TT64 naming where it matches workflow
        self.tab_props = ttk.Frame(self.nb)
        self.nb.add(self.tab_props, text="  ROM / Info  ")
        self._build_props_tab()

        self.tab_hex = ttk.Frame(self.nb)
        self.nb.add(self.tab_hex, text="  Memory (Hex)  ")
        self._build_hex_tab()

        self.tab_script = ttk.Frame(self.nb)
        self.nb.add(self.tab_script, text="  Level Script  ")
        self._build_script_tab()

        self.tab_patches = ttk.Frame(self.nb)
        self.nb.add(self.tab_patches, text="  Hacks / Patches  ")
        self._build_patches_tab()

        self.tab_segments = ttk.Frame(self.nb)
        self.nb.add(self.tab_segments, text="  Segments  ")
        self._build_segments_tab()

        self.after(200, lambda: self._tt64_init_sashes(outer, vpaned))

    def _tt64_init_sashes(self, outer, vpaned):
        """Approximate classic TT64 proportions after geometry exists."""
        try:
            w = outer.winfo_width()
            if w > 200:
                outer.sashpos(0, max(220, int(w * 0.22)))
        except tk.TclError:
            pass
        try:
            h = vpaned.winfo_height()
            if h > 200:
                vpaned.sashpos(0, max(220, int(h * 0.48)))
        except tk.TclError:
            pass

    def _build_tt64_viewport(self, parent):
        """TT64 central 3D pane — grid placeholder (no DirectX / GL in Tk)."""
        bar = ttk.Frame(parent, style="Viewport.TFrame", padding=(8, 4))
        bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(bar, text="3D Level View", style="Header.TLabel"
                  ).pack(side=tk.LEFT)
        ttk.Label(bar, text="  (geometry preview N/A — use hex / script tabs)",
                  style="ViewLabel.TLabel").pack(side=tk.LEFT)

        self._viewport_msg = tk.StringVar(
            value="No ROM loaded.\n\n"
                  "Open a Super Mario 64 ROM to enable the level tree and scripts.\n"
                  + TT64_SHELL_NOTE)
        self.viewport_canvas = tk.Canvas(
            parent, highlightthickness=0, bg=C_BG_VIEWPORT,
            bd=0)
        self.viewport_canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 2))
        self._vp_msg_id = self.viewport_canvas.create_text(
            20, 20, anchor=tk.NW, text=self._viewport_msg.get(),
            fill=C_TEXT_DIM, font=("Segoe UI", 10), width=680)
        self.viewport_canvas.bind("<Configure>", self._on_viewport_configure)

    def _on_viewport_configure(self, event):
        if not hasattr(self, "viewport_canvas"):
            return
        w, h = event.width, event.height
        self.viewport_canvas.delete("grid")
        step = 32
        g = C_BORDER_SUBTLE
        for x in range(0, w, step):
            self.viewport_canvas.create_line(x, 0, x, h, fill=g, tags="grid")
        for y in range(0, h, step):
            self.viewport_canvas.create_line(0, y, w, y, fill=g, tags="grid")
        self.viewport_canvas.tag_raise(self._vp_msg_id)
        try:
            tw = max(260, w - 36)
            self.viewport_canvas.itemconfigure(self._vp_msg_id, width=tw)
        except tk.TclError:
            pass

    def _refresh_viewport_banner(self):
        if not hasattr(self, "viewport_canvas") or not hasattr(self, "_vp_msg_id"):
            return
        try:
            w = max(260, self.viewport_canvas.winfo_width() - 36)
        except tk.TclError:
            w = 640
        self.viewport_canvas.itemconfigure(
            self._vp_msg_id, text=self._viewport_msg.get(), width=w)

    # ── Properties Tab (TT64 info panel) ──

    def _build_props_tab(self):
        f = self.tab_props
        pad = ttk.Frame(f, padding=16)
        pad.pack(fill=tk.BOTH, expand=True)

        # Header
        hdr = ttk.Frame(pad)
        hdr.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(hdr, text="ROM PROPERTIES", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Separator(hdr).pack(fill=tk.X, pady=(6, 0))

        # Properties grid
        props = ttk.Frame(pad, style="Props.TFrame", padding=12)
        props.pack(fill=tk.X)

        rows = [
            ("File Name:",     "filename"),
            ("Internal Title:","title"),
            ("Format:",        "format"),
            ("Size:",          "size"),
            ("Region:",        "region"),
            ("CRC 1:",         "crc1"),
            ("CRC 2:",         "crc2"),
            ("CRC Status:",    "crc_status"),
            ("Entry Point:",   "entry"),
            ("Extended:",      "extended"),
            ("MD5:",           "md5"),
        ]

        self.pv = {}
        for i, (label, key) in enumerate(rows):
            r = ttk.Frame(props, style="Props.TFrame")
            r.pack(fill=tk.X, pady=2)
            ttk.Label(r, text=label, style="PropKey.TLabel",
                      width=16, anchor=tk.E).pack(side=tk.LEFT, padx=(0, 10))
            v = tk.StringVar(value="—")
            self.pv[key] = v
            ttk.Label(r, textvariable=v, style="PropVal.TLabel").pack(side=tk.LEFT)

        # Separator
        ttk.Separator(pad).pack(fill=tk.X, pady=12)

        # Context area
        self._ctx_var = tk.StringVar(
            value="Open a Super Mario 64 ROM to get started.\n\n"
                  "Supported formats: .z64 (Big Endian), .v64 (Byte-Swapped), .n64 (Little Endian)\n\n"
                  "This tool is compatible with SM64 ROM Manager checksums\n"
                  "and Toad's Tool 64 level data tables."
        )
        ttk.Label(pad, textvariable=self._ctx_var, style="Muted.TLabel",
                  wraplength=550, justify=tk.LEFT).pack(anchor=tk.W)

    # ── Hex Editor Tab ──

    def _build_hex_tab(self):
        f = self.tab_hex
        hfont = ("Consolas", 10) if sys.platform == "win32" else ("Courier New", 10)

        # Header bar
        hbar = ttk.Frame(f)
        hbar.pack(fill=tk.X, padx=6, pady=(4, 2))

        self._hex_range_var = tk.StringVar(value="HEX DUMP — No ROM loaded")
        ttk.Label(hbar, textvariable=self._hex_range_var,
                  style="Section.TLabel").pack(side=tk.LEFT)

        # Offset entry
        ttk.Label(hbar, text="Offset:", style="Dim.TLabel").pack(side=tk.RIGHT, padx=(8, 2))
        self._hex_entry = ttk.Entry(hbar, width=12, font=("Consolas", 9))
        self._hex_entry.pack(side=tk.RIGHT, padx=2)
        self._hex_entry.bind("<Return>", lambda e: self._hex_entry_go())

        # Text widget
        tf = ttk.Frame(f)
        tf.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        sy = ttk.Scrollbar(tf, orient=tk.VERTICAL)
        sy.pack(side=tk.RIGHT, fill=tk.Y)

        self.hex_text = tk.Text(tf, font=hfont, state=tk.DISABLED,
                                wrap=tk.NONE, bg=C_BG_VIEWPORT, fg=C_HEX_BYTE,
                                insertbackground=C_TEXT,
                                selectbackground=C_TREE_SEL_BG,
                                selectforeground=C_TREE_SEL_FG,
                                borderwidth=0, highlightthickness=1,
                                highlightcolor=C_BORDER_FOCUS,
                                highlightbackground=C_BORDER,
                                padx=8, pady=8, cursor="arrow",
                                spacing1=1, spacing3=1)
        self.hex_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sy.config(command=self.hex_text.yview)

        # Tags
        self.hex_text.tag_configure("offset",   foreground=C_HEX_OFFSET)
        self.hex_text.tag_configure("hex",      foreground=C_HEX_BYTE)
        self.hex_text.tag_configure("ascii",    foreground=C_HEX_ASCII)
        self.hex_text.tag_configure("dot",      foreground=C_HEX_DOT)
        self.hex_text.tag_configure("header",   foreground=C_HEX_HEADER)
        self.hex_text.tag_configure("magic",    foreground=C_HEX_MAGIC)
        self.hex_text.tag_configure("modified", foreground=C_HEX_MODIFIED)
        self.hex_text.tag_configure("sep",      foreground=C_HEX_SEPARATOR)
        self.hex_text.tag_configure("search",   foreground="#000", background=C_YELLOW)
        self.hex_text.tag_configure("mio0",     foreground=C_PINK)

    # ── Level Script Tab ──

    def _build_script_tab(self):
        f = self.tab_script
        sfont = ("Consolas", 10) if sys.platform == "win32" else ("Courier New", 10)

        hbar = ttk.Frame(f)
        hbar.pack(fill=tk.X, padx=6, pady=(4, 2))
        self._script_title_var = tk.StringVar(value="LEVEL SCRIPT — Select a level")
        ttk.Label(hbar, textvariable=self._script_title_var,
                  style="Section.TLabel").pack(side=tk.LEFT)

        tf = ttk.Frame(f)
        tf.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        sy = ttk.Scrollbar(tf, orient=tk.VERTICAL)
        sy.pack(side=tk.RIGHT, fill=tk.Y)

        self.script_text = tk.Text(tf, font=sfont, state=tk.DISABLED,
                                   wrap=tk.NONE, bg=C_BG_VIEWPORT, fg=C_TEXT,
                                   insertbackground=C_TEXT,
                                   selectbackground=C_TREE_SEL_BG,
                                   selectforeground=C_TREE_SEL_FG,
                                   borderwidth=0, highlightthickness=1,
                                   highlightcolor=C_BORDER_FOCUS,
                                   highlightbackground=C_BORDER,
                                   padx=8, pady=8, cursor="arrow")
        self.script_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sy.config(command=self.script_text.yview)

        self.script_text.tag_configure("addr",   foreground=C_PURPLE)
        self.script_text.tag_configure("cmd",    foreground=C_CYAN)
        self.script_text.tag_configure("name",   foreground=C_YELLOW)
        self.script_text.tag_configure("data",   foreground=C_TEXT_DIM)
        self.script_text.tag_configure("comment", foreground=C_TEXT_MUTED)

    # ── Patches Tab ──

    def _build_patches_tab(self):
        f = self.tab_patches
        pad = ttk.Frame(f, padding=16)
        pad.pack(fill=tk.BOTH, expand=True)

        hdr = ttk.Frame(pad)
        hdr.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(hdr, text="PATCH LIBRARY", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(hdr, text="  Built-in SM64 binary patches (US v1.0)",
                  style="Dim.TLabel").pack(anchor=tk.W, pady=(2, 0))
        ttk.Separator(hdr).pack(fill=tk.X, pady=(6, 0))

        # Scrollable patch list
        canvas = tk.Canvas(pad, bg=C_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(pad, orient=tk.VERTICAL, command=canvas.yview)
        self._patches_frame = ttk.Frame(canvas)

        self._patches_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self._patches_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._patch_widgets = {}
        self._build_patch_cards()

    def _build_patch_cards(self):
        for w in self._patches_frame.winfo_children():
            w.destroy()
        self._patch_widgets = {}

        for i, p in enumerate(SM64_PATCHES):
            card = ttk.Frame(self._patches_frame, style="Card.TFrame", padding=10)
            card.pack(fill=tk.X, pady=(0, 6), padx=2)

            # Top row: category + name
            top = ttk.Frame(card, style="Card.TFrame")
            top.pack(fill=tk.X)
            ttk.Label(top, text=f"[{p['category']}]",
                      style="PatchCat.TLabel").pack(side=tk.LEFT, padx=(0, 8))
            ttk.Label(top, text=p['name'],
                      style="PatchName.TLabel").pack(side=tk.LEFT)

            # Status label
            status_var = tk.StringVar(value="")
            status_lbl = ttk.Label(top, textvariable=status_var,
                                   style="Dim.TLabel", font=("Consolas", 8))
            status_lbl.pack(side=tk.RIGHT, padx=4)

            # Desc
            ttk.Label(card, text=p['desc'], style="PatchDesc.TLabel",
                      wraplength=500, justify=tk.LEFT).pack(
                          anchor=tk.W, pady=(4, 6))

            # Buttons
            btn_row = ttk.Frame(card, style="Card.TFrame")
            btn_row.pack(fill=tk.X)

            apply_btn = ttk.Button(btn_row, text="Apply Patch",
                                   style="Patch.TButton",
                                   command=lambda idx=i: self._apply_patch(idx))
            apply_btn.pack(side=tk.LEFT, padx=(0, 4))

            undo_btn = ttk.Button(btn_row, text="Undo",
                                  style="PatchUndo.TButton",
                                  command=lambda idx=i: self._undo_patch(idx))
            undo_btn.pack(side=tk.LEFT, padx=(0, 4))

            offset_lbl = ttk.Label(btn_row,
                                   text=f"Offset: 0x{p['offset']:06X}",
                                   style="Dim.TLabel",
                                   font=("Consolas", 8))
            offset_lbl.pack(side=tk.RIGHT)

            self._patch_widgets[i] = {
                "status_var": status_var,
                "status_lbl": status_lbl,
                "apply_btn": apply_btn,
                "undo_btn": undo_btn,
            }

    # ── Segments Tab ──

    def _build_segments_tab(self):
        f = self.tab_segments
        pad = ttk.Frame(f, padding=16)
        pad.pack(fill=tk.BOTH, expand=True)

        hdr = ttk.Frame(pad)
        hdr.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(hdr, text="SEGMENT TABLE", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(hdr, text="  SM64 ROM segment layout (US v1.0)",
                  style="Dim.TLabel").pack(anchor=tk.W, pady=(2, 0))
        ttk.Separator(hdr).pack(fill=tk.X, pady=(6, 0))

        # Treeview for segments
        cols = ("name", "start", "end", "size")
        self.seg_tree = ttk.Treeview(pad, columns=cols, show="headings",
                                     height=16)
        self.seg_tree.heading("name",  text="Segment")
        self.seg_tree.heading("start", text="Start")
        self.seg_tree.heading("end",   text="End")
        self.seg_tree.heading("size",  text="Size")
        self.seg_tree.column("name",  width=280)
        self.seg_tree.column("start", width=100, anchor=tk.CENTER)
        self.seg_tree.column("end",   width=100, anchor=tk.CENTER)
        self.seg_tree.column("size",  width=100, anchor=tk.CENTER)
        self.seg_tree.pack(fill=tk.BOTH, expand=True)

        self.seg_tree.bind("<Double-1>", self._on_segment_dblclick)

        # Populate
        for seg_id in sorted(SM64_SEGMENTS_US.keys()):
            name, start, end = SM64_SEGMENTS_US[seg_id]
            sz = end - start
            self.seg_tree.insert("", "end", values=(
                f"0x{seg_id:02X} — {name}",
                f"0x{start:08X}",
                f"0x{end:08X}",
                f"{sz:,} bytes"
            ))

    # ────────────────────────────────────────────────
    #  STATUS BAR
    # ────────────────────────────────────────────────

    def _create_statusbar(self):
        sf = ttk.Frame(self, style="Status.TFrame")
        sf.pack(side=tk.BOTTOM, fill=tk.X)

        # Left
        self._status_var = tk.StringVar(
            value=f"Ready — {APP_FULL} — {APP_COPY}")
        ttk.Label(sf, textvariable=self._status_var, style="Status.TLabel",
                  padding=(10, 4)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Right
        pyver = f"Python {sys.version_info.major}.{sys.version_info.minor}"
        self._status_r = tk.StringVar(value=pyver)
        ttk.Label(sf, textvariable=self._status_r, style="Status.TLabel",
                  padding=(10, 4), foreground=C_TEXT_MUTED).pack(side=tk.RIGHT)

    def _set_status(self, msg):
        self._status_var.set(msg)
        self.update_idletasks()

    # ════════════════════════════════════════════════════════════
    #  ROM OPERATIONS
    # ════════════════════════════════════════════════════════════

    def _fix_endianness(self):
        """Detect and normalize ROM to Big Endian (.z64) via ROM Manager engine."""
        fmt, logs = self.rom_engine.normalize_endian(self.rom_data)
        for line in logs:
            self._set_status(line)
        return fmt

    def _parse_header(self):
        """Parse N64 / SM64 header using SM64RomManagerEngine.analyze()."""
        if len(self.rom_data) < 0x40:
            return

        info = self.rom_engine.analyze(self.rom_data)
        self.is_sm64 = info["is_sm64"]
        self.rom_region = info["rom_region"]

        crc_ok = info["crc_ok"]
        md5 = info["md5"]

        fn = os.path.basename(self.loaded_path) if self.loaded_path else "—"
        self.pv["filename"].set(fn)
        self.pv["title"].set(info["title"])
        self.pv["format"].set(self.rom_format)
        self.pv["size"].set(
            f"{info['size_mb']:.2f} MB ({info['size_bytes']:,} bytes)")
        self.pv["region"].set(info["region"])
        self.pv["crc1"].set(f"0x{info['crc1']:08X}")
        self.pv["crc2"].set(f"0x{info['crc2']:08X}")
        self.pv["crc_status"].set("✅ Valid" if crc_ok else "❌ Invalid — use Fix CRC")
        self.pv["entry"].set(f"0x{info['entry']:08X}")
        self.pv["extended"].set(info["extended"])
        self.pv["md5"].set(md5[:16] + "…" + md5[16:])

    # ════════════════════════════════════════════════════════════
    #  FILE COMMANDS
    # ════════════════════════════════════════════════════════════

    def cmd_open(self):
        fp = filedialog.askopenfilename(
            title=f"Open N64 ROM — {APP_FULL}",
            filetypes=(("N64 ROMs", "*.z64 *.v64 *.n64 *.rom *.bin"),
                       ("All Files", "*.*")))
        if not fp:
            return

        try:
            self._set_status("Loading ROM…")
            with open(fp, 'rb') as f:
                self.rom_data = bytearray(f.read())

            self.loaded_path = fp
            self.rom_backup = bytearray(self.rom_data)
            self.applied_patches = set()

            self.rom_format = self._fix_endianness()
            self._parse_header()

            fn = os.path.basename(fp)
            self._set_status(f"Loaded: {fn} — {len(self.rom_data):,} bytes")

            # Indicator
            if self.is_sm64:
                self._ind_var.set(f"● SM64 ({self.rom_region})")
                self._ind_label.configure(foreground=C_GREEN)
            else:
                self._ind_var.set("● N64 ROM")
                self._ind_label.configure(foreground=C_YELLOW)

            # Populate views
            self._populate_tree()
            self._hex_view_offset = 0
            self._schedule_hex()
            self._refresh_patch_status()

            if self.is_sm64:
                self._ctx_var.set(
                    f"Super Mario 64 detected! Region: {self.rom_region}\n\n"
                    f"SM64RomManagerEngine handles endian, CRC, and extend; use the\n"
                    f"level tree (TT64-style), Level Script tab, Memory (hex), and\n"
                    f"Hacks / Patches. Tools menu = ROM Manager actions.\n\n"
                    f"3D viewport: placeholder only (no TT64 DirectX renderer)."
                )
                self._viewport_msg.set(
                    f"SM64 loaded — region {self.rom_region}.\n\n"
                    f"Pick a course in the left tree; scripts open in Level Script.\n"
                    f"{TT64_SHELL_NOTE}")
            else:
                self._ctx_var.set(
                    f"N64 ROM loaded; title does not match stock SM64.\n"
                    f"Header, Memory (hex), and ROM Manager tools still apply.\n"
                    f"Level tree uses SM64 tables only when the ROM is SM64."
                )
                self._viewport_msg.set(
                    "Non-SM64 or unknown build.\n\n"
                    "ROM Manager engine: Fix CRC, Extend, Verify still run on this image.\n"
                    + TT64_SHELL_NOTE)
            self._refresh_viewport_banner()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ROM:\n{e}")
            self._set_status("Error loading ROM.")

    def cmd_save(self):
        if not self.rom_data or not self.loaded_path:
            messagebox.showwarning("No ROM", "No ROM loaded to save.")
            return
        try:
            self._set_status("Saving…")
            with open(self.loaded_path, 'wb') as f:
                f.write(self.rom_data)
            self._set_status(f"Saved: {os.path.basename(self.loaded_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def cmd_save_as(self):
        if not self.rom_data:
            return
        fp = filedialog.asksaveasfilename(
            title=f"Save ROM As — {APP_FULL}",
            defaultextension=".z64",
            filetypes=(("Z64 ROM", "*.z64"), ("All Files", "*.*")))
        if fp:
            self.loaded_path = fp
            self.cmd_save()
            self.pv["filename"].set(os.path.basename(fp))

    def cmd_close_rom(self):
        """TT64-style close: clear ROM and panels (prompt if dirty)."""
        _actweaker_close_rom(self)

    def cmd_export_header(self):
        if not self.rom_data or len(self.rom_data) < 0x40:
            messagebox.showwarning("No ROM", "No ROM loaded.")
            return
        fp = filedialog.asksaveasfilename(
            title="Export Header",
            defaultextension=".bin",
            filetypes=(("Binary", "*.bin"), ("All Files", "*.*")))
        if fp:
            with open(fp, 'wb') as f:
                f.write(self.rom_data[0:0x40])
            self._set_status(f"Header exported to {os.path.basename(fp)}")

    def cmd_undo_all(self):
        if not self.rom_backup:
            messagebox.showwarning("No Backup", "No backup data available.")
            return
        if messagebox.askyesno("Undo All", "Revert ROM to original loaded state?"):
            self.rom_data = bytearray(self.rom_backup)
            self.applied_patches = set()
            self._parse_header()
            self._schedule_hex()
            self._refresh_patch_status()
            self._set_status("All changes reverted.")

    # ════════════════════════════════════════════════════════════
    #  TOOL COMMANDS
    # ════════════════════════════════════════════════════════════

    def cmd_fix_crc(self):
        if not self.rom_data:
            messagebox.showwarning("No ROM", "No ROM loaded.")
            return

        self._set_status("Recalculating CRC…")
        crc1, crc2 = self.rom_engine.write_crc(self.rom_data)

        self._parse_header()
        self._schedule_hex()

        self._set_status(f"CRC fixed: 0x{crc1:08X} / 0x{crc2:08X}")
        messagebox.showinfo("CRC Fixed",
            f"Checksums recalculated and written:\n\n"
            f"  CRC 1: 0x{crc1:08X}\n"
            f"  CRC 2: 0x{crc2:08X}\n\n"
            f"Save the ROM to apply to disk.")

    def cmd_extend(self, target_mb=32):
        if not self.rom_data:
            messagebox.showwarning("No ROM", "No ROM loaded.")
            return

        target = target_mb * 1024 * 1024
        cur = len(self.rom_data)

        if cur >= target:
            messagebox.showinfo("Already Extended",
                f"ROM is already {cur / (1024*1024):.0f} MB ≥ {target_mb} MB.")
            return

        if not messagebox.askyesno("Extend ROM",
            f"Extend ROM from {cur / (1024*1024):.1f} MB to {target_mb} MB?\n\n"
            f"Padding with 0x01 bytes (SM64 ROM Manager compatible)."):
            return

        self._set_status(f"Extending to {target_mb} MB…")
        try:
            self.rom_engine.extend(self.rom_data, target_mb, pad_byte=0x01)
        except Exception as e:
            messagebox.showerror("Extend ROM", str(e))
            return
        self._parse_header()
        self._schedule_hex()
        self._set_status(f"Extended to {target_mb} MB — save to apply.")

    def cmd_verify(self):
        if not self.rom_data:
            messagebox.showwarning("No ROM", "No ROM loaded.")
            return

        v = self.rom_engine.verify(self.rom_data)
        ok = v["ok"]

        msg = (
            f"Stored CRC1:     0x{v['crc1_stored']:08X}\n"
            f"Calculated CRC1: 0x{v['crc1_calc']:08X}  "
            f"{'✅' if v['crc1_stored'] == v['crc1_calc'] else '❌'}\n\n"
            f"Stored CRC2:     0x{v['crc2_stored']:08X}\n"
            f"Calculated CRC2: 0x{v['crc2_calc']:08X}  "
            f"{'✅' if v['crc2_stored'] == v['crc2_calc'] else '❌'}\n\n"
            f"Overall: {'✅ VALID' if ok else '❌ INVALID — Run Fix CRC'}\n\n"
            f"MD5:  {v['md5']}\n"
            f"SHA1: {v['sha1']}\n\n"
            f"Size: {v['size']:,} bytes"
        )

        messagebox.showinfo("ROM Integrity", msg)
        self._set_status("Verification complete." if ok else "CRC mismatch detected!")

    def cmd_region_info(self):
        if not self.rom_data:
            messagebox.showwarning("No ROM", "No ROM loaded.")
            return

        crc1 = struct.unpack('>I', self.rom_data[0x10:0x14])[0]
        crc2 = struct.unpack('>I', self.rom_data[0x14:0x18])[0]

        lines = ["Known SM64 ROM signatures:\n"]
        for rname, crcs in SM64_CHECKSUMS.items():
            match = " ◀ MATCH" if (crc1 == crcs["crc1"] and crc2 == crcs["crc2"]) else ""
            lines.append(
                f"  {rname:4s}  CRC1=0x{crcs['crc1']:08X}  CRC2=0x{crcs['crc2']:08X}{match}")

        lines.append(f"\nYour ROM: CRC1=0x{crc1:08X}  CRC2=0x{crc2:08X}")
        lines.append(f"Region byte (0x3E): 0x{self.rom_data[0x3E]:02X}")

        messagebox.showinfo("Region Info", "\n".join(lines))

    def cmd_show_segments(self):
        self.nb.select(self.tab_segments)

    # ════════════════════════════════════════════════════════════
    #  LEVEL TREE  (TT64 layout)
    # ════════════════════════════════════════════════════════════

    def _populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        title = self.pv["title"].get()
        root = self.tree.insert("", "end", text=f"📁 {title}", open=True)

        # Header
        hdr = self.tree.insert(root, "end", text="📦 Header (0x0000–0x003F)",
                               tags=("header",))
        self.tree.insert(hdr, "end", text="   PI Configuration",   tags=("header",))
        self.tree.insert(hdr, "end", text="   Clock Rate",         tags=("header",))
        self.tree.insert(hdr, "end", text="   Entry Point",        tags=("header",))
        self.tree.insert(hdr, "end", text="   CRC Checksums",      tags=("header",))
        self.tree.insert(hdr, "end", text="   Game Title",         tags=("header",))
        self.tree.insert(hdr, "end", text="   Region / Country",   tags=("header",))

        if not self.is_sm64:
            self.tree.insert(root, "end", text="📄 Raw Binary Data", tags=("raw",))
            return

        # ── SM64 Levels (TT64 layout) ──
        categories = {}
        for lvl in SM64_LEVELS:
            cat = lvl[2]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(lvl)

        cat_icons = {
            "Course": "⭐", "Secret": "🔑", "Bowser": "🔥",
            "Castle": "🏰", "Misc": "📎"
        }

        for cat_name in ["Course", "Secret", "Bowser", "Castle", "Misc"]:
            if cat_name not in categories:
                continue
            icon = cat_icons.get(cat_name, "📁")
            cat_node = self.tree.insert(root, "end",
                                        text=f"{icon} {cat_name}",
                                        open=(cat_name == "Course"))

            for lvl_id, lvl_name, _, script_off, area_count in categories[cat_name]:
                node = self.tree.insert(
                    cat_node, "end",
                    text=f"   {lvl_name}",
                    tags=("level",),
                    values=(lvl_id, script_off, area_count))

                # Areas
                for a in range(1, area_count + 1):
                    self.tree.insert(node, "end",
                                    text=f"      Area {a}",
                                    tags=("area",),
                                    values=(lvl_id, script_off, a))

        # Segments
        seg_node = self.tree.insert(root, "end", text="🗂️ Segments")
        for seg_id in sorted(SM64_SEGMENTS_US.keys()):
            name, start, end = SM64_SEGMENTS_US[seg_id]
            self.tree.insert(seg_node, "end",
                             text=f"   0x{seg_id:02X} {name.split('–')[-1].strip()}",
                             tags=("segment",),
                             values=(seg_id, start, end))

        # Assets placeholder
        assets = self.tree.insert(root, "end", text="🎨 Assets")
        for a in ["Geo Layouts (3D Models)", "Textures (MIO0)",
                   "Audio / Sequences", "Collision Maps", "Behavior Scripts"]:
            self.tree.insert(assets, "end", text=f"   {a}", tags=("asset",))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        item = sel[0]
        text = self.tree.item(item, "text").strip()
        tags = self.tree.item(item, "tags")
        vals = self.tree.item(item, "values")

        if "level" in tags and vals:
            lvl_id, script_off, area_count = int(vals[0]), int(vals[1]), int(vals[2])
            self._ctx_var.set(
                f"Level: {text}\n"
                f"ID: 0x{lvl_id:02X}    Script Offset: 0x{script_off:06X}    Areas: {area_count}\n\n"
                f"Double-click to view level script disassembly.\n"
                f"Use Hex Editor → Go To to jump to the script offset."
            )
            self._viewport_msg.set(
                f"Selected: {text.strip()}\n"
                f"Level ID 0x{lvl_id:02X} · script @ 0x{script_off:06X} · {area_count} area(s)\n\n"
                f"(TT64 would render geometry here — open Level Script / Memory tabs.)")
            self._refresh_viewport_banner()
            self._disassemble_level_script(script_off, text)
            self._set_status(f"Level: {text} — Script @ 0x{script_off:06X}")

        elif "segment" in tags and vals:
            seg_id, start, end = int(vals[0]), int(vals[1]), int(vals[2])
            name = SM64_SEGMENTS_US.get(seg_id, ("Unknown",))[0]
            self._ctx_var.set(
                f"Segment 0x{seg_id:02X}: {name}\n"
                f"Range: 0x{start:08X} – 0x{end:08X}  ({end - start:,} bytes)\n\n"
                f"Double-click to jump to this segment in the Hex Editor."
            )
            self._set_status(f"Segment 0x{seg_id:02X} — 0x{start:08X}–0x{end:08X}")

        elif "header" in tags:
            self._ctx_var.set(
                f"{text}\n\n"
                "The N64 ROM header (0x00–0x3F) contains:\n"
                "  • PI configuration & clock rate\n"
                "  • Program entry point\n"
                "  • CRC-32 checksums (CIC-6102)\n"
                "  • 20-byte game title (ASCII)\n"
                "  • Region/country code\n\n"
                "Header bytes are highlighted yellow in the Hex Editor."
            )
        elif "asset" in tags:
            self._ctx_var.set(
                f"{text}\n\n"
                "Asset extraction requires MIO0 decompression\n"
                "and format-specific parsers.\n"
                "Planned for AC'S TWEAKER SM64 2.0."
            )
        else:
            self._ctx_var.set(f"Selected: {text}")

        self._set_status(f"Selected: {text}")

    # ════════════════════════════════════════════════════════════
    #  HEX EDITOR
    # ════════════════════════════════════════════════════════════

    def _schedule_hex(self):
        if self._hex_job:
            self.after_cancel(self._hex_job)
        self._hex_job = self.after(40, self._render_hex)

    def _render_hex(self):
        self._hex_job = None
        self.hex_text.config(state=tk.NORMAL)
        self.hex_text.delete("1.0", tk.END)

        if not self.rom_data:
            self.hex_text.insert(tk.END, "  No ROM loaded.\n", "dot")
            self.hex_text.config(state=tk.DISABLED)
            return

        offset = self._hex_view_offset
        chunk_sz = self._hex_chunk_size
        end_off = min(offset + chunk_sz, len(self.rom_data))
        chunk = self.rom_data[offset:end_off]

        self._hex_range_var.set(
            f"HEX DUMP — 0x{offset:08X}–0x{end_off:08X}  "
            f"({end_off - offset:,} bytes / {len(self.rom_data):,} total)")

        # Check if we have backup for diff highlighting
        has_backup = len(self.rom_backup) > 0

        for i in range(0, len(chunk), 16):
            row = chunk[i:i + 16]
            abs_off = offset + i

            # Offset column
            self.hex_text.insert(tk.END, f"{abs_off:08X}  ", "offset")

            # Hex bytes
            for j, b in enumerate(row):
                pos = abs_off + j
                # Determine tag
                if has_backup and pos < len(self.rom_backup) and \
                   self.rom_backup[pos] != b:
                    tag = "modified"
                elif pos < 0x40:
                    tag = "header"
                    if pos < 4:
                        tag = "magic"
                else:
                    tag = "hex"

                # Check for MIO0 magic
                if pos + 3 < len(self.rom_data) and \
                   self.rom_data[pos:pos+4] == b'MIO0' and j == 0:
                    tag = "mio0"

                self.hex_text.insert(tk.END, f"{b:02X}", tag)
                self.hex_text.insert(tk.END, " " if j < 15 else "", "dot")

            # Padding for short last row
            pad = 16 - len(row)
            if pad > 0:
                self.hex_text.insert(tk.END, "   " * pad, "dot")

            # Separator
            self.hex_text.insert(tk.END, "  │", "sep")

            # ASCII
            for b in row:
                if 32 <= b <= 126:
                    self.hex_text.insert(tk.END, chr(b), "ascii")
                else:
                    self.hex_text.insert(tk.END, ".", "dot")

            self.hex_text.insert(tk.END, "│\n", "sep")

        # Footer
        if end_off < len(self.rom_data):
            remaining = len(self.rom_data) - end_off
            self.hex_text.insert(tk.END,
                f"\n  … {remaining:,} bytes remaining. "
                f"Use ▶ or Go To to navigate. …\n", "dot")

        self.hex_text.config(state=tk.DISABLED)

    def _hex_goto(self, offset):
        if not self.rom_data:
            return
        offset = max(0, min(offset, len(self.rom_data) - 16))
        offset = (offset // 16) * 16  # Align to 16-byte boundary
        self._hex_view_offset = offset
        self._schedule_hex()
        self.nb.select(self.tab_hex)

    def _hex_page_prev(self):
        self._hex_view_offset = max(0, self._hex_view_offset - self._hex_chunk_size)
        self._schedule_hex()

    def _hex_page_next(self):
        if not self.rom_data:
            return
        new = self._hex_view_offset + self._hex_chunk_size
        if new < len(self.rom_data):
            self._hex_view_offset = new
            self._schedule_hex()

    def _hex_page_end(self):
        if not self.rom_data:
            return
        self._hex_view_offset = max(0, len(self.rom_data) - self._hex_chunk_size)
        self._hex_view_offset = (self._hex_view_offset // 16) * 16
        self._schedule_hex()

    def _hex_entry_go(self):
        txt = self._hex_entry.get().strip()
        try:
            if txt.lower().startswith("0x"):
                off = int(txt, 16)
            else:
                off = int(txt, 16)
            self._hex_goto(off)
        except ValueError:
            messagebox.showwarning("Invalid Offset",
                f"'{txt}' is not a valid hex offset.")

    def cmd_hex_goto(self):
        if not self.rom_data:
            return
        result = simpledialog.askstring(
            "Go to Offset", "Enter hex offset (e.g. 0x3F00):",
            parent=self)
        if result:
            try:
                off = int(result.strip().replace("0x", "").replace("0X", ""), 16)
                self._hex_goto(off)
            except ValueError:
                messagebox.showwarning("Invalid", f"'{result}' is not valid hex.")

    def cmd_hex_search(self):
        if not self.rom_data:
            return
        result = simpledialog.askstring(
            "Search Hex", "Enter hex bytes to search (e.g. 80 37 12 40):",
            parent=self)
        if not result:
            return

        try:
            needle = bytes.fromhex(result.replace(" ", ""))
        except ValueError:
            messagebox.showwarning("Invalid", f"'{result}' is not valid hex.")
            return

        # Search
        results = []
        data = bytes(self.rom_data)
        start = 0
        while True:
            idx = data.find(needle, start)
            if idx == -1:
                break
            results.append(idx)
            start = idx + 1

        if not results:
            messagebox.showinfo("Not Found",
                f"Pattern {needle.hex().upper()} not found in ROM.")
            return

        self._search_results = results
        self._search_idx = 0
        self._hex_goto(results[0])
        self._set_status(
            f"Found {len(results)} occurrence(s). Showing first at 0x{results[0]:08X}")

    # ════════════════════════════════════════════════════════════
    #  LEVEL SCRIPT DISASSEMBLER
    # ════════════════════════════════════════════════════════════

    def _disassemble_level_script(self, offset, level_name):
        """Simple level script disassembler (read-only)."""
        self.script_text.config(state=tk.NORMAL)
        self.script_text.delete("1.0", tk.END)

        self._script_title_var.set(f"LEVEL SCRIPT — {level_name} @ 0x{offset:06X}")

        if not self.rom_data or offset >= len(self.rom_data):
            self.script_text.insert(tk.END, "  Offset out of range.\n", "comment")
            self.script_text.config(state=tk.DISABLED)
            return

        self.script_text.insert(tk.END,
            f"; ═══════════════════════════════════════════════\n", "comment")
        self.script_text.insert(tk.END,
            f"; Level Script: {level_name}\n", "comment")
        self.script_text.insert(tk.END,
            f"; Offset: 0x{offset:06X}\n", "comment")
        self.script_text.insert(tk.END,
            f"; ═══════════════════════════════════════════════\n\n", "comment")

        pos = offset
        max_cmds = 128
        count = 0

        while pos < len(self.rom_data) - 1 and count < max_cmds:
            cmd_byte = self.rom_data[pos]

            if cmd_byte in LEVELSCRIPT_CMDS:
                name, length = LEVELSCRIPT_CMDS[cmd_byte]
            else:
                name, length = f"UNK_0x{cmd_byte:02X}", 4

            if pos + length > len(self.rom_data):
                break

            raw = self.rom_data[pos:pos + length]

            # Address
            self.script_text.insert(tk.END, f"  {pos:08X}  ", "addr")
            # Command hex
            self.script_text.insert(tk.END,
                " ".join(f"{b:02X}" for b in raw).ljust(length * 3), "cmd")
            self.script_text.insert(tk.END, "  ", "data")
            # Mnemonic
            self.script_text.insert(tk.END, name, "name")

            # Extra decode for common commands
            if cmd_byte in (0x00, 0x01) and length >= 8:
                seg = raw[3]
                addr_start = struct.unpack('>I', raw[4:8])[0] if length >= 8 else 0
                self.script_text.insert(tk.END,
                    f"  ; seg=0x{seg:02X} addr=0x{addr_start:08X}", "comment")
            elif cmd_byte == 0x1D and length >= 24:
                # Object placement
                obj_model = raw[3]
                x = struct.unpack('>h', raw[4:6])[0]
                y = struct.unpack('>h', raw[6:8])[0]
                z = struct.unpack('>h', raw[8:10])[0]
                self.script_text.insert(tk.END,
                    f"  ; model={obj_model} pos=({x},{y},{z})", "comment")
            elif cmd_byte == 0x19 and length >= 12:
                area = raw[2]
                y = struct.unpack('>h', raw[4:6])[0]
                x = struct.unpack('>h', raw[6:8])[0]
                z = struct.unpack('>h', raw[8:10])[0]
                angle = struct.unpack('>h', raw[10:12])[0]
                self.script_text.insert(tk.END,
                    f"  ; area={area} mario=({x},{y},{z}) angle={angle}", "comment")

            self.script_text.insert(tk.END, "\n")

            # Stop on RETURN
            if cmd_byte == 0x07:
                self.script_text.insert(tk.END, "\n", "data")
                self.script_text.insert(tk.END, "  ; ── End of script ──\n", "comment")
                break

            pos += length
            count += 1

        if count >= max_cmds:
            self.script_text.insert(tk.END,
                f"\n  ; … truncated at {max_cmds} commands …\n", "comment")

        self.script_text.config(state=tk.DISABLED)
        self.nb.select(self.tab_script)

    def cmd_jump_level_script(self):
        sel = self.tree.selection()
        if sel:
            tags = self.tree.item(sel[0], "tags")
            vals = self.tree.item(sel[0], "values")
            if "level" in tags and vals:
                off = int(vals[1])
                self._hex_goto(off)
                return
        messagebox.showinfo("Select Level",
            "Select a level in the tree first.")

    def cmd_view_objects(self):
        messagebox.showinfo("Coming Soon",
            "Object list viewer is planned for v2.0.\n\n"
            "For now, use the Level Script tab to see\n"
            "SET_OBJECT (0x1D) commands with positions.")

    # ════════════════════════════════════════════════════════════
    #  PATCHES
    # ════════════════════════════════════════════════════════════

    def _refresh_patch_status(self):
        for i, p in enumerate(SM64_PATCHES):
            w = self._patch_widgets.get(i)
            if not w:
                continue

            if not self.rom_data:
                w["status_var"].set("")
                continue

            off = p["offset"]
            plen = len(p["patched"])

            if off + plen > len(self.rom_data):
                w["status_var"].set("⚠ Out of range")
                w["status_lbl"].configure(foreground=C_ORANGE)
                continue

            current = bytes(self.rom_data[off:off + plen])

            if current == p["patched"]:
                w["status_var"].set("✅ Applied")
                w["status_lbl"].configure(foreground=C_GREEN)
                self.applied_patches.add(i)
            elif current == p["original"]:
                w["status_var"].set("○ Not applied")
                w["status_lbl"].configure(foreground=C_TEXT_DIM)
                self.applied_patches.discard(i)
            else:
                w["status_var"].set("⚠ Modified (unknown state)")
                w["status_lbl"].configure(foreground=C_YELLOW)

    def _apply_patch(self, idx):
        if not self.rom_data:
            messagebox.showwarning("No ROM", "No ROM loaded.")
            return

        p = SM64_PATCHES[idx]
        off = p["offset"]
        plen = len(p["patched"])

        if off + plen > len(self.rom_data):
            messagebox.showerror("Error",
                f"Patch offset 0x{off:06X} is beyond ROM size.")
            return

        self.rom_data[off:off + plen] = p["patched"]
        self.applied_patches.add(idx)
        self._refresh_patch_status()
        self._schedule_hex()
        self._set_status(f"Applied: {p['name']}")

    def _undo_patch(self, idx):
        if not self.rom_data:
            return

        p = SM64_PATCHES[idx]
        off = p["offset"]
        plen = len(p["original"])

        if off + plen > len(self.rom_data):
            return

        self.rom_data[off:off + plen] = p["original"]
        self.applied_patches.discard(idx)
        self._refresh_patch_status()
        self._schedule_hex()
        self._set_status(f"Reverted: {p['name']}")

    # ════════════════════════════════════════════════════════════
    #  SEGMENT EVENTS
    # ════════════════════════════════════════════════════════════

    def _on_segment_dblclick(self, event):
        sel = self.seg_tree.selection()
        if not sel:
            return
        vals = self.seg_tree.item(sel[0], "values")
        if vals and len(vals) >= 2:
            try:
                off_str = vals[1]
                off = int(off_str, 16)
                self._hex_goto(off)
            except (ValueError, IndexError):
                pass

    # ════════════════════════════════════════════════════════════
    #  MISC
    # ════════════════════════════════════════════════════════════

    def _not_impl(self):
        messagebox.showinfo("Coming Soon",
            f"This feature is planned for {APP_TITLE} 2.0.\n\n"
            f"Currently implemented in v{APP_VERSION}:\n"
            "  ✓ ROM loading (z64/v64/n64) with auto format fix\n"
            "  ✓ Full N64 header parsing\n"
            "  ✓ CRC-32 checksum recalculation (CIC-6102)\n"
            "  ✓ ROM extending (24/32/64 MB)\n"
            "  ✓ Syntax-highlighted hex editor with paging\n"
            "  ✓ Go-to-offset and hex search\n"
            "  ✓ TT64-style level browser (all 25 levels)\n"
            "  ✓ Level script disassembler (40+ commands)\n"
            "  ✓ SM64 segment table viewer\n"
            "  ✓ Built-in patch library (6 patches)\n"
            "  ✓ ROM integrity verification (MD5/SHA1/CRC)\n"
            "  ✓ Full Save / Save As / Export Header\n"
            "  ✓ Undo all changes"
        )

    def cmd_about(self):
        messagebox.showinfo(
            f"About — {APP_TITLE}",
            f"{APP_FULL}\n"
            f"{'━' * 40}\n\n"
            f"{TT64_SHELL_NOTE}\n\n"
            f"• Shell: Toad's Tool 64–like layout (tree, 3D pane, bottom tabs).\n"
            f"• Core: class SM64RomManagerEngine — endian, CIC-6102 CRC, extend, verify.\n"
            f"• 3D view: informational grid only (not a TT64 geometry port).\n\n"
            f"{APP_COPY}\n\n"
            f"Python {sys.version_info.major}.{sys.version_info.minor}+ · Tkinter"
        )


# ════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = ACTweakerSM64()
    app.mainloop()
