BLUE = "\x01\x1b[34m\x02"
RESET  = "\x01\x1b[0m\x02"

ANSI_FG = {
    "BLACK"   : ("\x1b[30m",   (0x00, 0x00, 0x00)),      # Black
    "RED"     : ("\x1b[31m",   (0xd4, 0x14, 0x3c)),      # Red – “bright” ANSI‑red
    "GREEN"   : ("\x1b[32m",   (0x23, 0xa6, 0x23)),      # Green – ANSI‑green
    "YELLOW"  : ("\x1b[33m",   (0xe4, 0xb2, 0x3f)),      # Yellow – ANSI‑yellow
    "BLUE"    : ("\x1b[34m",   (0x19, 0x64, 0xc6)),      # Blue – ANSI‑blue
    "MAGENTA" : ("\x1b[35m",   (0xa3, 0x2e, 0xab)),      # Magenta – ANSI‑magenta
    "CYAN"    : ("\x1b[36m",   (0x21, 0xc4, 0xd9)),      # Cyan – ANSI‑cyan
    "WHITE"   : ("\x1b[37m",   (0xe8, 0xeb, 0xea)),      # White – ANSI‑white

    # “Bright” variants (90–97) – useful for a brighter palette on modern terminals.
    "BRIGHT_BLACK"   : ("\x1b[90m",  (0x3e, 0x36, 0x30)),
    "BRIGHT_RED"     : ("\x1b[91m",  (0xff, 0x4d, 0x4f)),
    "BRIGHT_GREEN"   : ("\x1b[92m",  (0x4a, 0xe4, 0x41)),
    "BRIGHT_YELLOW"  : ("\x1b[93m",  (0xff, 0xfa, 0x57)),
    "BRIGHT_BLUE"    : ("\x1b[94m",  (0x6d, 0xa5, 0xff)),
    "BRIGHT_MAGENTA" : ("\x1b[95m",  (0xe0, 0x56, 0xf4)),
    "BRIGHT_CYAN"    : ("\x1b[96m",  (0x8f, 0xd3, 0xff)),
    "BRIGHT_WHITE"   : ("\x1b[97m",  (0xff, 0xff, 0xff)),
}

def ansi_rgb_fg(r: int, g: int, b: int) -> str:
    """Return ESC[38;2;<r>;<g>;<b>m – 24‑bit true colour."""
    return f"\x1b[38;2;{r};{g};{b}m"

