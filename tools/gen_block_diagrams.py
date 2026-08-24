#!/usr/bin/env python3
"""Generate the block diagrams shipped in <board>/docs/.

atopile describes the circuit in code, so there is no KiCad schematic sheet to
plot. These diagrams are the human-readable equivalent: they show every block,
every net that leaves a block, and the power domains, so a reviewer can follow
the design without reading the .ato source.

Usage:
    python3 tools/gen_block_diagrams.py                  # SVG + PDF, all boards
    python3 tools/gen_block_diagrams.py --svg-only
    python3 tools/gen_block_diagrams.py atari-joystick

SVG is written directly; the PDF is produced by headless Chrome, which keeps the
text as vector glyphs without any font-embedding setup. Run from anywhere — the
output paths are resolved relative to this file.
"""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# A4 landscape: 1400 / 990 == 1.414.
W, H = 1400, 990

SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', Menlo, 'DejaVu Sans Mono', monospace"
MONO_ADV = 0.602  # advance width of one Menlo glyph, in em

INK = "#1b1f24"
MUTED = "#5b6570"
RULE = "#c9d1d9"

SIG = "#374151"          # logic-level signal
PWR = "#c2410c"          # power rail
BUS_W = 4.0
SIG_W = 1.8
PWR_W = 2.6

STYLES = {
    "mcu": ("#eaf1fd", "#1a56db"),
    "conn": ("#f2f4f7", "#4b5563"),
    "power": ("#fff5ec", "#c2410c"),
    "shift": ("#eefbf1", "#15803d"),
    "led": ("#fdf3f7", "#a21caf"),
    "plain": ("#ffffff", "#6b7280"),
}

REPO = "github.com/kunichiko/MimicX-hardware"


class Svg:
    def __init__(self, w: int = W, h: int = H):
        self.w, self.h = w, h
        self.parts: list[str] = []

    # --- primitives -----------------------------------------------------
    def rect(self, x, y, w, h, fill="#fff", stroke=RULE, sw=1.6, rx=8):
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def text(self, x, y, s, size=14, fill=INK, anchor="start", weight="400",
             family=SANS, ls="0"):
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'letter-spacing="{ls}" xml:space="preserve">'
            f'{html.escape(s)}</text>'
        )

    def line(self, pts, stroke=SIG, sw=SIG_W, arrow="end"):
        """Orthogonal polyline. arrow: none | end | start | both."""
        d = " ".join(f"{x},{y}" for x, y in pts)
        attrs = ""
        if arrow in ("end", "both"):
            attrs += f' marker-end="url(#a-{stroke.lstrip("#")})"'
        if arrow in ("start", "both"):
            attrs += f' marker-start="url(#b-{stroke.lstrip("#")})"'
        self.parts.append(
            f'<polyline points="{d}" fill="none" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linejoin="round"{attrs}/>'
        )

    def dot(self, x, y, color=SIG, r=4.5):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

    # --- composites -----------------------------------------------------
    def block(self, x, y, w, h, title, body=(), style="plain", title_size=17):
        fill, stroke = STYLES[style]
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=2.0)
        cx = x + w / 2
        head = title.split("\n")
        ty = y + 30
        for i, part in enumerate(head):
            self.text(cx, ty + i * 21, part, size=title_size, anchor="middle",
                      weight="700")
        ty += 21 * len(head) + 6
        for i, part in enumerate(body):
            self.text(cx, ty + i * 18, part, size=12.5, anchor="middle",
                      fill=MUTED, family=MONO)

    def label(self, x, y, lines, anchor="middle", color=SIG, size=12.5):
        """Wire label on an opaque plate, so it stays readable over a line.

        (x, y) is the bottom edge of the plate.
        """
        wid = max(len(s) for s in lines) * size * MONO_ADV + 14
        hgt = len(lines) * (size + 4) + 8
        bx = {"middle": x - wid / 2, "start": x - 7, "end": x - wid + 7}[anchor]
        self.parts.append(
            f'<rect x="{bx}" y="{y - hgt}" width="{wid}" height="{hgt}" rx="4" '
            f'fill="#ffffff" fill-opacity="0.94" stroke="none"/>'
        )
        for i, s in enumerate(lines):
            self.text(x, y - hgt + 16 + i * (size + 4), s, size=size,
                      anchor=anchor, fill=color, family=MONO)

    def panel(self, x, y, w, heading, rows, mono=False, bullet=False):
        h = 34 + len(rows) * 20
        self.rect(x, y, w, h, fill="#fbfcfd", stroke=RULE, sw=1.4)
        self.text(x + 16, y + 24, heading, size=13.5, weight="700")
        for i, s in enumerate(rows):
            self.text(x + 16, y + 46 + i * 20, ("•  " + s) if bullet else s,
                      size=12.5, fill=MUTED, family=MONO if mono else SANS)
        return h

    # --- page furniture -------------------------------------------------
    def header(self, title, subtitle, right_lines):
        self.text(44, 46, title, size=27, weight="700", ls="-0.3")
        self.text(44, 72, subtitle, size=14.5, fill=MUTED)
        for i, s in enumerate(right_lines):
            self.text(W - 44, 34 + i * 18, s, size=12.5, anchor="end",
                      fill=MUTED, family=MONO)
        self.parts.append(
            f'<line x1="44" y1="90" x2="{W - 44}" y2="90" stroke="{RULE}" '
            f'stroke-width="1.5"/>'
        )

    def legend(self, x, y):
        self.line([(x, y), (x + 46, y)], stroke=PWR, sw=PWR_W, arrow="none")
        self.text(x + 56, y + 5, "power rail", size=12.5, fill=MUTED)
        self.line([(x + 160, y), (x + 206, y)], stroke=SIG, sw=SIG_W,
                  arrow="none")
        self.text(x + 216, y + 5, "signal", size=12.5, fill=MUTED)
        self.line([(x + 300, y), (x + 346, y)], stroke=SIG, sw=BUS_W,
                  arrow="none")
        self.text(x + 356, y + 5, "multi-bit bus", size=12.5, fill=MUTED)
        self.text(x + 500, y + 5,
                  "Every net shown here is declared in the .ato source; "
                  "this drawing is generated from it by hand, not extracted.",
                  size=12, fill=MUTED)

    def render(self) -> str:
        markers = []
        for color in (SIG, PWR):
            k = color.lstrip("#")
            markers.append(
                f'<marker id="a-{k}" viewBox="0 0 10 10" refX="9" refY="5" '
                f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M0,1 L9,5 L0,9 z" fill="{color}"/></marker>'
                f'<marker id="b-{k}" viewBox="0 0 10 10" refX="1" refY="5" '
                f'markerWidth="7" markerHeight="7" orient="auto">'
                f'<path d="M9,1 L0,5 L9,9 z" fill="{color}"/></marker>'
            )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
            f'height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
            f"<defs>{''.join(markers)}</defs>"
            f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>'
            + "".join(self.parts)
            + "</svg>"
        )


# ---------------------------------------------------------------------------
# The two single-MCU adapters share one skeleton:
#   USB-C -> CH32X035 -> TC7MPB9307FT bus switch -> retro connector
# ---------------------------------------------------------------------------
def build_single_mcu(*, title, subtitle, pid, conn_title, conn_body,
                     lane_a, lane_b, pin_heading, pin_rows,
                     notes_left, notes_right, host_rail) -> Svg:
    s = Svg()
    s.header(title, subtitle,
             ["board rev 1.0.0   ·   CERN-OHL-S-2.0",
              f"USB VID:PID  {pid}", REPO])

    s.panel(44, 108, 300, notes_left[0], notes_left[1], bullet=True)
    s.panel(1056, 108, 300, notes_right[0], notes_right[1], bullet=True)

    s.block(470, 150, 270, 96, "U2  LP5907MFX-3.3",
            ["LDO, 250 mA, SOT-23-5"], "power")
    s.block(70, 340, 175, 210, "J2\nUSB Type-C",
            ["TYPE-C-31-M-12", "16P receptacle", "sink / UFP"], "conn")
    s.block(455, 340, 300, 210, "U1  CH32X035G8U6",
            ["QFN-28, RISC-V, 48 MHz", "USB 2.0 FS device (native)",
             "VDD = 3.3 V, NOT 5 V tolerant"], "mcu")
    s.block(855, 340, 215, 210, "U3  TC7MPB9307FT",
            ["8-bit dual-supply", "FET bus switch", "TSSOP-20"], "shift")
    s.block(1190, 340, 166, 210, conn_title, conn_body, "conn")

    s.block(90, 660, 150, 105, "SW1  BOOT", ["tact switch"], "plain", 15)
    s.block(265, 660, 150, 105, "LED1  PWR", ["green 0603"], "led", 15)
    s.block(440, 660, 260, 105, "LED2  WS2812B-2020",
            ["addressable RGB"], "led", 15)

    # --- power ----------------------------------------------------------
    s.line([(245, 370), (395, 370), (395, 198), (470, 198)],
           stroke=PWR, sw=PWR_W)
    s.label(400, 192, ["VBUS 5 V"], anchor="start", color=PWR)

    s.line([(605, 246), (605, 340)], stroke=PWR, sw=PWR_W)
    s.label(616, 272, ["VDD33 3.3 V"], anchor="start", color=PWR)

    s.line([(605, 285), (900, 285), (900, 340)], stroke=PWR, sw=PWR_W)
    s.dot(605, 285, PWR)
    s.label(896, 279, ["VCCA = VDD33"], anchor="end", color=PWR)

    s.line([(1272, 340), (1272, 322), (1020, 322), (1020, 340)],
           stroke=PWR, sw=PWR_W)
    s.label(1146, 316, [host_rail], color=PWR)

    # VDD33 down the left edge, then along the bottom to both LEDs
    s.line([(605, 315), (58, 315), (58, 800), (340, 800), (340, 765)],
           stroke=PWR, sw=PWR_W)
    s.dot(605, 315, PWR)
    s.line([(340, 800), (570, 800), (570, 765)], stroke=PWR, sw=PWR_W)
    s.dot(340, 800, PWR)
    s.label(68, 640, ["VDD33"], anchor="start", color=PWR)

    # --- signals --------------------------------------------------------
    s.line([(245, 425), (455, 425)], arrow="both")
    s.label(350, 419, ["USB D+ / D-", "PC17 / PC16"])
    s.line([(245, 495), (455, 495)])
    s.label(350, 549, ["CC1 / CC2", "Rd 5.1 kΩ ×2", "→ PC14 / PC15"])

    s.line([(755, 445), (855, 445)], sw=BUS_W, arrow="both")
    s.label(805, 439, [lane_a])
    s.line([(1070, 445), (1190, 445)], sw=BUS_W, arrow="both")
    s.label(1130, 439, [lane_b])

    s.line([(500, 550), (500, 610), (165, 610), (165, 660)])
    s.label(350, 604, ["VDD33 → SW1 → 4.7 kΩ → PC17 (USB D+)"])
    s.line([(690, 550), (690, 660)])
    s.label(702, 600, ["PB0 → 470 Ω → DIN"], anchor="start")

    s.panel(780, 640, 576, pin_heading, pin_rows, mono=True)
    s.legend(90, 900)
    return s


def build_atari_joystick() -> Svg:
    return build_single_mcu(
        title="Mimic X Adapter — ATARI / X68000 Joystick",
        subtitle="USB-MIDI in from a phone, 9-pin ATARI-standard joystick out. "
                 "Also emulates a Mega Drive 6-button pad.",
        pid="0x1209:0x9210",
        conn_title="J1\nD-SUB 9P\nfemale",
        conn_body=["X68000", "ATARI", "Mega Drive"],
        lane_a="7 × 3.3 V",
        lane_b="7 × 5 V",
        host_rail="VCCB = VCC_HOST (D-SUB pin 5)",
        pin_heading="Pin map — CH32X035 ↔ bus switch ↔ D-SUB 9P",
        pin_rows=[
            "PA7   UP           →   pin 1",
            "PA5   DOWN         →   pin 2",
            "PA3   LEFT         →   pin 3",
            "PA2   RIGHT        →   pin 4",
            "PA6   TRIG-A       →   pin 6",
            "PA4   TRIG-B       →   pin 7",
            "PA0   COMMON / TH  ←   pin 8   MD 6-button select, TIM2_CH1",
            "      +5 V / GND       pin 5 / pin 9",
        ],
        notes_left=("Why the bus switch", [
            "CH32X035 is not 5 V tolerant:",
            "VIN ≤ VDD + 0.3 V = 3.6 V.",
            "The X68000 port runs at 5 V.",
            "TC7MPB9307FT is a passive FET",
            "switch, so the MCU drives 0 /",
            "3.3 V and the host pull-up puts",
            "the line back to 5 V — the host",
            "sees a classic open-drain pad.",
        ]),
        notes_right=("Power domains", [
            "VBUS (USB) and VCC_HOST (D-SUB",
            "pin 5) stay separate on the",
            "board, so nothing back-feeds",
            "when the phone and the retro",
            "machine are both powered.",
            "BOOT pulls PC17 (USB D+) high via",
            "4.7 kΩ for the WCH USB-DFU ROM.",
        ]),
    )


def build_x68000_keyboard() -> Svg:
    return build_single_mcu(
        title="Mimic X Adapter — Sharp X68000 Keyboard / Mouse",
        subtitle="USB-MIDI in from a phone, X68000 mini-DIN 7P keyboard port "
                 "out. Keyboard and mouse share the one connector.",
        pid="0x1209:0x9210",
        conn_title="J1\nMini DIN 7P\nmale",
        conn_body=["X68000", "keyboard", "port"],
        lane_a="5 × 3.3 V",
        lane_b="5 × 5 V TTL",
        host_rail="VCCB = Vcc2 (DIN pin 1)",
        pin_heading="Pin map — CH32X035 ↔ bus switch ↔ mini DIN 7P",
        pin_rows=[
            "PB11  USART1_RX  ch6  ←  pin 4  KEY TxD   2400 8N1, host → kbd",
            "PB10  USART1_TX  ch4  →  pin 3  KEY RxD   2400 8N1, kbd → host",
            "PB12  GPIO in    ch5  ←  pin 5  READY     low blocks transmit",
            "PB9   USART4_TX  ch8  →  pin 2  MSDATA    4800 8N2, mouse",
            "PB8   GPIO       ch7  ↔  pin 6  REMOTE    TV remote line",
            "      +5 V / GND         pin 1 / pin 7  Vcc2, shield",
        ],
        notes_left=("Why the bus switch", [
            "Every signal on the X68000",
            "keyboard port is 5 V TTL, and",
            "CH32X035 is not 5 V tolerant.",
            "TC7MPB9307FT splits the bus into",
            "A = 3.3 V (MCU) and B = 5 V",
            "(host), so the MCU only ever",
            "sees clamped 3.3 V levels.",
            "3 of the 8 channels are spare.",
        ]),
        notes_right=("Power domains", [
            "VBUS (USB) and Vcc2 (DIN pin 1)",
            "stay separate on the board, so",
            "nothing back-feeds when the",
            "phone and the X68000 are both",
            "powered.",
            "BOOT pulls PC17 high via 4.7 kΩ",
            "for the WCH USB-DFU ROM.",
        ]),
    )


# ---------------------------------------------------------------------------
# wireless-combo: ESP32-C6 + CH32X035, both retro ports, in-design
# ---------------------------------------------------------------------------
def build_wireless_combo() -> Svg:
    s = Svg()
    s.header(
        "Mimic X Adapter — Wireless Combo (BLE-MIDI)",
        "ESP32-C6 takes MIDI in over BLE or USB and relays it to the CH32X035 "
        "device engine over I2C. Both retro ports on one board.",
        ["board rev 0.1 — in design, layout not routed",
         "USB VID:PID  0x1209:0x9211", REPO],
    )

    s.panel(1050, 108, 306, "Recovery path — the point of this board", [
        "CH32 firmware turns SDI off, so a bad flash",
        "used to be unrecoverable. Now the ESP32",
        "owns the CH32's power and BOOT pin: drop",
        "VDD_SW, hold PC17 high, power up — the ISP",
        "ROM keeps SWD alive, so it can reflash.",
    ], bullet=False)

    s.block(430, 150, 270, 96, "Q1  AO3401A",
            ["P-FET high side, default ON"], "power")
    s.block(50, 330, 220, 230, "U1\nSeeed XIAO\nESP32-C6",
            ["BLE-MIDI host", "USB-C: power + log",
             "OTA-flashes the CH32"], "mcu", 16)
    s.block(460, 330, 300, 230, "U4  CH32X035G8U6",
            ["QFN-28, RISC-V, 48 MHz", "'combined-i2c' firmware",
             "runs on VDD_SW"], "mcu")
    s.block(860, 250, 205, 130, "U3  TC7MPB9307FT",
            ["FET bus switch", "B side = VCC_JOY"], "shift", 15)
    s.block(860, 520, 205, 130, "U2  TC7MPB9307FT",
            ["FET bus switch", "B side = VCC_KBD"], "shift", 15)
    s.block(1160, 250, 170, 130, "J2  XH 9P",
            ["cable to", "D-SUB 9P"], "conn", 15)
    s.block(1160, 520, 170, 130, "J1  XH 7P",
            ["cable to", "mini DIN 7P"], "conn", 15)
    s.block(270, 760, 180, 100, "J3  XH 3P", ["SWD, WCH-LinkE"], "conn", 15)
    s.block(490, 760, 160, 100, "SW1  BOOT", ["tact switch"], "plain", 15)
    s.block(690, 760, 220, 100, "LED2  WS2812B", ["on VDD_SW"], "led", 15)

    # --- power ----------------------------------------------------------
    s.line([(160, 330), (160, 198), (430, 198)], stroke=PWR, sw=PWR_W)
    s.label(170, 192, ["VDD33 — XIAO LDO out, always on"], anchor="start",
            color=PWR)
    s.line([(560, 246), (560, 330)], stroke=PWR, sw=PWR_W)
    s.label(571, 316, ["VDD_SW 3.3 V"], anchor="start", color=PWR)

    s.line([(560, 290), (795, 290), (795, 225), (960, 225), (960, 250)],
           stroke=PWR, sw=PWR_W)
    s.dot(560, 290, PWR)
    s.label(956, 219, ["VCCA = VDD_SW"], anchor="end", color=PWR)
    s.line([(795, 290), (795, 470), (960, 470), (960, 520)],
           stroke=PWR, sw=PWR_W)
    s.dot(795, 290, PWR)
    s.label(956, 464, ["VCCA = VDD_SW"], anchor="end", color=PWR)

    # host 5 V: each port feeds its own switch B side, then OR-s into the XIAO
    s.line([(1160, 360), (1112, 360), (1112, 915), (70, 915), (70, 560)],
           stroke=PWR, sw=PWR_W)
    s.line([(1112, 360), (1065, 360)], stroke=PWR, sw=PWR_W)
    s.dot(1112, 360, PWR)
    s.line([(1160, 630), (1135, 630), (1135, 940), (92, 940), (92, 560)],
           stroke=PWR, sw=PWR_W)
    s.line([(1135, 630), (1065, 630)], stroke=PWR, sw=PWR_W)
    s.dot(1135, 630, PWR)
    s.label(640, 909, ["VCC_JOY (D-SUB pin 5) / VCC_KBD (DIN pin 1) "
                       "→ SS14 Schottky ×2 → VCC_ESP = XIAO 5 V pin"],
            color=PWR)

    # --- signals --------------------------------------------------------
    s.line([(270, 390), (460, 390)], arrow="both")
    s.label(365, 384, ["D4/D5 ↔ PC18/PC19", "I2C 400 kHz | SWD"])
    s.line([(270, 440), (460, 440)], arrow="start")
    s.label(365, 486, ["D3 ← PB1", "INT, active low"])

    s.line([(230, 330), (230, 215), (430, 215)])
    s.label(240, 268, ["D0 → Q1 gate: cut CH32 power"], anchor="start")

    s.line([(270, 545), (420, 545), (420, 620), (620, 620), (620, 560)])
    s.label(430, 614, ["D1 → 4.7 kΩ → PC17: force the ISP bootloader"],
            anchor="start")
    s.line([(570, 760), (570, 660), (620, 660)], arrow="none")
    s.dot(620, 620, SIG)

    s.line([(430, 760), (430, 745)], arrow="none")
    s.label(355, 741, ["SWD tap = the D4/D5 pair"], anchor="start")

    s.line([(700, 560), (700, 760)])
    s.label(712, 700, ["PB0 → 470 Ω → DIN"], anchor="start")

    s.line([(760, 390), (830, 390), (830, 320), (860, 320)], sw=BUS_W,
           arrow="both")
    s.label(770, 384, ["PA0, PA2–PA7"], anchor="start")
    s.line([(760, 500), (830, 500), (830, 580), (860, 580)], sw=BUS_W,
           arrow="both")
    s.label(770, 494, ["PB8–PB12"], anchor="start")
    s.line([(1065, 290), (1160, 290)], sw=BUS_W, arrow="both")
    s.line([(1065, 560), (1160, 560)], sw=BUS_W, arrow="both")
    s.label(1112, 284, ["5 V"])
    s.label(1112, 554, ["5 V"])

    s.panel(110, 606, 230, "Pull-ups tie to VDD_SW", [
        "I2C 4.7 kΩ, INT 10 kΩ and the",
        "PC17 pull-down hang off VDD_SW,",
        "never off 3V3 — on 3V3 they",
        "back-feed the CH32 and a power",
        "cycle stops being a real reset.",
    ], bullet=False)

    s.legend(50, 972)
    return s


BOARDS = {
    "atari-joystick": ("atari-joystick-block-diagram", build_atari_joystick),
    "x68000-keyboard": ("x68000-keyboard-block-diagram", build_x68000_keyboard),
    "wireless-combo": ("wireless-combo-block-diagram", build_wireless_combo),
}


def svg_to_pdf(svg_path: Path, pdf_path: Path) -> bool:
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not Path(chrome).exists():
        found = shutil.which("chromium") or shutil.which("google-chrome")
        if not found:
            return False
        chrome = found
    with tempfile.TemporaryDirectory() as tmp:
        # Chrome takes the page size from @page; stretch the SVG over A4.
        wrapper = Path(tmp) / "page.html"
        wrapper.write_text(
            "<!doctype html><meta charset=utf-8>"
            "<style>@page{size:297mm 210mm;margin:0}"
            "html,body{margin:0;padding:0}"
            "img{display:block;width:297mm;height:210mm}</style>"
            f'<img src="{svg_path.resolve().as_uri()}">',
            encoding="utf-8",
        )
        out = Path(tmp) / "out.pdf"
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={out}", wrapper.as_uri()],
            check=True, capture_output=True, timeout=180,
        )
        pdf_path.write_bytes(out.read_bytes())
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--svg-only", action="store_true")
    ap.add_argument("boards", nargs="*")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    for board in (args.boards or list(BOARDS)):
        if board not in BOARDS:
            print(f"unknown board: {board}", file=sys.stderr)
            return 2
        stem, builder = BOARDS[board]
        outdir = root / board / "docs"
        outdir.mkdir(parents=True, exist_ok=True)
        svg = outdir / f"{stem}.svg"
        svg.write_text(builder().render(), encoding="utf-8")
        print(f"wrote {svg.relative_to(root)}")
        if not args.svg_only:
            pdf = outdir / f"{stem}.pdf"
            if svg_to_pdf(svg, pdf):
                print(f"wrote {pdf.relative_to(root)}")
            else:
                print("  (no Chrome found — skipped PDF)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
