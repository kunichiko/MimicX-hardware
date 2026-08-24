# MimicX-hardware

**製品名: Mimic X** — 「Mimic X」プロジェクトのマイコン基板設計データ。

*Mimic X is an open-hardware USB-MIDI adapter family that lets a phone (or any
USB-MIDI / BLE-MIDI host) drive the real peripheral ports of 1980s Japanese
computers — the Sharp X68000 keyboard/mouse port and the ATARI-standard
9-pin joystick port, including Mega Drive 6-button pads. This repository holds
the board designs; the firmware, the protocol spec and the phone app live in the
sibling repositories linked at the bottom.*

- **Licence**: MIT (see [`LICENSE`](LICENSE)) — schematics, layouts and the
  part libraries are all modifiable sources.
- **MCU**: WCH **CH32X035G8U6** (QFN-28, RISC-V, 48 MHz, native USB 2.0 FS).
- **USB VID:PID**: `0x1209:0x9210` (Mimic X) and `0x1209:0x9211` (Mimic X
  Bridge), [requested from pid.codes](https://github.com/pidcodes/pidcodes.github.com/pull/1210).
- **Designed in [atopile](https://atopile.io)** — see
  [Design sources](#design-sources--回路図ファイルが無い理由) for why there is
  no `.kicad_sch` and where to read the circuit instead.

## 基板バリエーション / Boards

### `atari-joystick/` — ATARI / X68000 ジョイスティックアダプタ

D-SUB 9pin メス。X68000 / ATARI 標準ポートに直挿しし、メガドライブ 6 ボタン
パッドもエミュレートする。**rev 1.0.0、JLCPCB で製造済み。**

<p align="center">
  <img src="atari-joystick/docs/images/render-top.png" width="46%" alt="atari-joystick, component side">
  <img src="atari-joystick/docs/images/render-bottom.png" width="46%" alt="atari-joystick, solder side">
</p>

| | |
|---|---|
| ブロック図 / block diagram | [PDF](atari-joystick/docs/atari-joystick-block-diagram.pdf) · [SVG](atari-joystick/docs/atari-joystick-block-diagram.svg) |
| PCB レイヤープロット / layer plots | [PDF](atari-joystick/docs/atari-joystick-pcb.pdf) (silk / Cu / fab, 6 pages) |
| 対話的に眺める / browse the layout | [KiCanvas](https://kicanvas.org/?repo=https%3A%2F%2Fgithub.com%2Fkunichiko%2FMimicX-hardware%2Fblob%2Fmain%2Fatari-joystick%2Flayouts%2Fdefault%2Fdefault.kicad_pcb) |
| 回路の定義 / circuit source | [`atari_joystick.ato`](atari-joystick/atari_joystick.ato) |
| 製造データ / fabrication | [`layouts/default/production/`](atari-joystick/layouts/default/production) (Gerber + BOM + CPL) |
| 設計メモ / design notes | [`README.md`](atari-joystick/README.md) |

### `x68000-keyboard/` — X68000 キーボード / マウスアダプタ

ミニ DIN 7pin オス。X68000 のキーボード端子はマウス端子を兼用しており、本基板も
1 コネクタで両方をエミュレートする。4 層。**rev 1.0.0、JLCPCB で製造済み。**

<p align="center">
  <img src="x68000-keyboard/docs/images/render-top.png" width="46%" alt="x68000-keyboard, component side">
  <img src="x68000-keyboard/docs/images/render-bottom.png" width="46%" alt="x68000-keyboard, solder side">
</p>

| | |
|---|---|
| ブロック図 / block diagram | [PDF](x68000-keyboard/docs/x68000-keyboard-block-diagram.pdf) · [SVG](x68000-keyboard/docs/x68000-keyboard-block-diagram.svg) |
| PCB レイヤープロット / layer plots | [PDF](x68000-keyboard/docs/x68000-keyboard-pcb.pdf) (silk / Cu ×4 / fab, 8 pages) |
| 対話的に眺める / browse the layout | [KiCanvas](https://kicanvas.org/?repo=https%3A%2F%2Fgithub.com%2Fkunichiko%2FMimicX-hardware%2Fblob%2Fmain%2Fx68000-keyboard%2Flayouts%2Fdefault%2Fdefault.kicad_pcb) |
| 回路の定義 / circuit source | [`x68000_keyboard.ato`](x68000-keyboard/x68000_keyboard.ato) |
| 製造データ / fabrication | [`layouts/default/production/`](x68000-keyboard/layouts/default/production) (Gerber + BOM + CPL) |
| 設計メモ / design notes | [`README.md`](x68000-keyboard/README.md) |

### `wireless-combo/` — 無線 (BLE-MIDI) Combined アダプタ

XIAO ESP32-C6 (BLE-MIDI ホスト) + CH32X035 (デバイスエンジン) の 2 チップ構成で、
ジョイスティックとキーボードの両ポートを 1 枚で担当する。ESP32 が CH32 の電源と
BOOT ピンを握っているため、CH32 のファームが壊れても SWD 経由で自力復旧できる。

> **rev 0.1 — 回路は確定、レイアウトは未配線。** このため 3D レンダと
> レイヤープロットはまだ置いていない (載せても中身が空になる)。回路の全体像は
> ブロック図と `.ato` を参照。

| | |
|---|---|
| ブロック図 / block diagram | [PDF](wireless-combo/docs/wireless-combo-block-diagram.pdf) · [SVG](wireless-combo/docs/wireless-combo-block-diagram.svg) |
| 回路の定義 / circuit source | [`wireless_combo.ato`](wireless-combo/wireless_combo.ato) |
| 設計メモ / design notes | [`README.md`](wireless-combo/README.md) |

## Design sources / 回路図ファイルが無い理由

この 3 基板はいずれも **[atopile](https://atopile.io) で設計している**。atopile は
回路を「図」ではなく「コード」で書く EDA で、`.ato` から直接ネットリストと KiCad
レイアウトを生成する。したがって **プロットできる回路図シート (`.kicad_sch`) は
そもそも存在しない**。回路を読むには次のいずれかを使う:

*These boards are designed in atopile, a text-based EDA: the circuit is written
as code and the netlist and KiCad layout are generated from it. There is no
schematic sheet to plot, so a reviewer has three ways in instead:*

1. **ブロック図 PDF** (`<board>/docs/*-block-diagram.pdf`) — 全ブロック、全信号、
   電源ドメイン、ピン割当表を 1 枚に収めた図。`tools/gen_block_diagrams.py` で
   生成しており、内容は `.ato` の記述と 1:1 で対応する。
   *The closest thing to a schematic: every block, every net that leaves a
   block, the power domains and the full pin map on one A4 sheet.*
2. **`.ato` ソース** — 部品・接続・値・設計理由がコメント付きで書かれている
   一次情報。`~` が接続、`~>` が直列挿入を表す。
   *The primary source, with the reasoning in the comments.*
3. **KiCad レイアウト** (`<board>/layouts/default/default.kicad_pcb`) — 上の表の
   KiCanvas リンクからブラウザで開ける。ネット名は `.ato` 側で
   `has_net_name` により意味のある名前 (`UP_3V3`, `KEY_TXD_3V3` など) に固定済み。
   *Browsable in KiCanvas; the nets carry meaningful names, not `Net-(U1-Pad3)`.*

ブロック図とレイヤープロットの再生成:

```sh
# ブロック図 (SVG + PDF)。PDF は headless Chrome で出力する
python3 tools/gen_block_diagrams.py

# PCB レイヤープロット
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$KC pcb export pdf --mode-multipage \
   --layers F.Silkscreen,F.Cu,B.Cu,B.Silkscreen,F.Fab,Cmts.User \
   --common-layers Edge.Cuts \
   -o atari-joystick/docs/out atari-joystick/layouts/default/default.kicad_pcb
```

## 共通設計事項

- **MCU**: CH32X035G8U6 (QFN-28、48MHz、USB Full-Speed 内蔵)。**5V トレラント
  ではない** (絶対最大定格 VIN ≤ VDD+0.3V) ため、ターゲット機の 5V 信号とは
  必ずレベルシフタ (TC7MPB9307FT, パッシブ FET バススイッチ) を介して接続する
- **USB**: Type-C Receptacle、CC1/CC2 にそれぞれ 5.1kΩ プルダウン (Rd = sink/UFP)。
  CC は MCU の PC14/PC15 にも引いて内蔵 USB-PD コントローラで直接サンプリングする
- **電源**: USB バスパワー (VBUS 5V) を LDO (LP5907MFX-3.3) で 3.3V に降圧して MCU に
  供給する。CH32X035 の USB トランシーバ出力は VDD 直結なので、規格準拠ホストと
  正しく enumerate させるため VDD は必ず 3.3V にする。ターゲット機からの 5V は
  レベルシフタの B 側電源としてのみ使い、VBUS とは基板内で分離して逆流を防ぐ
- **デカップリング**: VDD ピンに 4.7µF + 0.1µF を近接配置
- **表示**: 電源 LED (緑 0603、常時点灯) + フルカラー LED (WS2812B-2020、
  DI 直前に 470Ω 直列ダンピング抵抗)
- **書き込み**: BOOT ボタンで PC17 (USB D+) を 4.7kΩ 経由で HIGH に引き上げた状態で
  リセットすると、WCH の USB DFU ブートローダに入る

## 関連リポジトリ / Related repositories

- [MimicX-app](https://github.com/kunichiko/MimicX-app) — Flutter アプリ (USB-MIDI / BLE-MIDI ホスト)
- [MimicX-firmware](https://github.com/kunichiko/MimicX-firmware) — マイコンファームウェア (CH32X035 / ESP32)
- [MimicX-protocol](https://github.com/kunichiko/MimicX-protocol) — USB-MIDI 通信プロトコル仕様
