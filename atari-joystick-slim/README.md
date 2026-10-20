# atari-joystick-slim

Mimic X — ATARI 仕様ジョイスティックアダプタ基板 (スリム版)

*USB-MIDI to ATARI-standard 9-pin joystick adapter, slim variant for hosts
whose joystick port sits deep inside the chassis (MSX, FM TOWNS). Same circuit
as [`atari-joystick`](../atari-joystick) v1.0.0; only the D-SUB connector and
the board shape differ. Designed in [atopile](https://atopile.io) — the circuit
lives in [`atari_joystick_slim.ato`](atari_joystick_slim.ato).*

> **状態: 設計中。** 基板外形・部品配置・配線は未確定。製造データはまだ無い。

## atari-joystick (v1.0.0) との違い

| 項目 | atari-joystick | atari-joystick-slim |
|---|---|---|
| 回路 | — | **同一** (MCU / レベルシフタ / 電源 / LED / BOOT ボタン) |
| D-SUB 9pin | 基板実装ライトアングル品 (CONNFLY DS1037-09FNAKT74-0CC) | ハンダカップ型の **樹脂ブロックのみ** (金属シェルを外す) |
| コネクタ接続 | スルーホールにはんだ付け | 基板エッジの表 5 / 裏 4 パッドをカップ列の間に差し込み、カップに直接はんだ付け |
| シェル接続 | シェル → GND | なし (シェルを外すため) |
| 基板形状 | 約 35×31 mm | コネクタ幅程度の細長い形 (x68000-keyboard と同じ形態) |
| 層数 | 2 層 | **4 層** (x68000-keyboard と同じスタックアップ、総厚 1.6 mm) |
| BOM / CPL | コネクタも JLCPCB で実装 | コネクタは手はんだ (ダミー LCSC `C0000000`) |

MSX や FM TOWNS のジョイスティック端子は筐体のかなり奥にあり、金属シェル付きの
D-SUB や幅の広い基板では届かない。シェルを外した樹脂ブロックと細い基板にする
ことで、スリムなプラグとして差し込めるようにする。

## D-SUB 9pin の取り付け

フットプリントは自作の [`parts/DSUB9_SolderCup_Edge`](parts/DSUB9_SolderCup_Edge)。

- 基板厚 **1.6 mm** がハンダカップの上下の列の間に入ることを実物で確認済み
- パッド: ピッチ 2.77 mm、1.5 × 4.0 mm、基板エッジから 0.3 mm 内側
- ハンダカップ側 (= 基板側) から見るため、嵌合面とは **左右が逆** になる

```
  嵌合面 (ホストに挿す側) から見たメス     ハンダカップ側 (基板側) から見たとき
       5 4 3 2 1                         部品面 (F.Cu):  1 2 3 4 5
        9 8 7 6                          はんだ面 (B.Cu):  6 7 8 9
```

ピンアサインは atari-joystick と同じ (ATARI / X68000 標準):

| Pin | 信号 | Pin | 信号 |
|-----|------|-----|------|
| 1 | Up | 6 | TRIG-A |
| 2 | Down | 7 | TRIG-B |
| 3 | Left | 8 | COMMON (TH) |
| 4 | Right | 9 | GND |
| 5 | +5V (host-supplied) | | |

## 回路・ピン割当・電源

atari-joystick と同一なので [`../atari-joystick/README.md`](../atari-joystick/README.md)
を参照。ファームウェアも同じ (`joystick` env) をそのまま使う。

## ビルド

```sh
cd atari-joystick-slim
~/.local/bin/ato build --keep-picked-parts
```

atopile は **0.15.8 以降 + `ato auth login` が必須** (2026-10 時点)。0.15.7 が使う
部品 API (`components.atopileapi.com`) は廃止され、0.15.8+ はサインイン済み
トークン付きで `legacy.atopileapi.com` を使う。CLI 自体も 0.15.x で保守モード
(後継は app.atopile.io / 0.16+)。`--keep-picked-parts` を付けると PCB に記録
済みの部品をそのまま使い、抵抗・コンデンサの再選定を避けられる。

`layouts/default/default.kicad_pcb` は atari-joystick v1.0.0 のレイアウトを
出発点としてコピーし、旧 D-SUB フットプリントだけを取り除いたもの。部品の
配置と配線の一部は v1.0.0 のまま残っているので、細長い外形に合わせて
組み直す。
