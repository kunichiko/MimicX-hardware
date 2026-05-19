# x68000-keyboard

Mimic X — X68000 キーボードアダプタ基板 (キーボード + マウス相乗り対応)

## 用途

スマートフォン (USB-MIDI ホスト) から CH32X035 経由で、X68000 のキーボード
信号 (KEY TxD/RxD) およびマウス信号 (MSDATA) を生成し、X68000 本体の
ミニ DIN 7pin ポートに接続して使用する。

X68000 のキーボードコネクタは **マウス端子を兼用** しており、本基板も
1 つのコネクタで両方をエミュレートする (ファーム `BOARD_X68K_FULL`)。

## 主要部品

| 部品 | 型番 / 仕様 | 備考 |
|------|-----------|------|
| MCU | WCH CH32X035G8U6 | QFN28、48MHz、USB Full-Speed 内蔵、3.3V 駆動 |
| USB コネクタ | USB Type-C (Receptacle, 16pin) | スマートフォンと接続 |
| 出力コネクタ | Mini DIN 7pin オス | X68000 キーボード端子 (現状はプレースホルダ部品で実装) |
| LDO | LP5907MFX-3.3 (250 mA) | VBUS 5V → MCU VDD 3.3V |
| レベルシフタ | Toshiba TC7MPB9307FT (TSSOP-20) | 8-bit Dual-Supply Bus Switch、3.3V↔5V |
| LED | チップ LED (0603) ×2 | デバッグ用 (PB3, PB4) |
| その他 | デカップリング 0.1µF / 4.7µF, USB Type-C CC 抵抗 5.1kΩ ×2, BOOT ボタン |

## ピン割当 (CH32X035G8U6 QFN28 → コネクタ)

> **注意 (重要)**: 旧版 README には `PA15–PA19` という記載があったが、これは
> CH32X035 別パッケージ (LQFP48 など) のピン名で、MimicX で採用している
> **CH32X035G8U6 (QFN28) には存在しない**。詳細は `../docs/CH32X035.md` §3 参照。
> 以下が QFN28 の実ピンに合わせた最新割当。

| QFN28 Pin | MCU 信号 | レベルシフタ | DIN 7pin | 方向 (MCU 視点) | 用途 |
|---:|---|---|---:|---|---|
| 22 | PB11 (USART1_RX, RX1_2) | a1↔b1 | Pin 4 (KEY TxD) | **IN** | X68000 本体からのコマンド受信 (2400/8N1) |
| 21 | PB10 (USART1_TX, default) | a2↔b2 | Pin 3 (KEY RxD) | **OUT** | キーコード送信 (2400/8N1) |
| 23 | PB12 (GPIO 入力) | a3↔b3 | Pin 5 (READY) | IN | 1=ホスト準備完了、Low 時送信抑止 |
| 20 | PB9 (USART4_TX, TX4_3) | a4↔b4 | Pin 2 (MSDATA) | OUT | マウスデータ送信 (4800/8N2) |
| 19 | PB8 (GPIO) | a5↔b5 | Pin 6 (REMOTE) | (FW 依存) | TV リモコン信号。用途は将来検討 |
| 14 | PB3 | — | — | OUT | Debug LED 0 (緑) |
| 15 | PB4 | — | — | OUT | Debug LED 1 (赤) |
| —  | (GND) | — | Pin 7 | — | 共通 GND |
| —  | (NC) | — | Pin 1 (Vcc2 +5V) | — | 既定では NC (USB バスパワー駆動) |

USART のリマップ設定 (`AFIO_PCFR1`):
- `USART1` は PB10/PB11 を使うため `USART1_REMAP` ビットの設定で
  `RX1_2` (= PB11) にマップする必要がある。
- `USART4` は PB9 の `TX4_3` リマップを使用 (MSDATA は送信のみで RX は不要)。

詳細はファームウェア `MimicX-firmware/src/functions/x68k_keyboard/` および
`x68k_mouse/` 参照。

## DIN ピン名の方向解釈 (重要)

X68000 サービスマニュアル上の `KEY TxD` / `KEY RxD` は **X68000 本体 (ホスト) 視点**
で命名されている:

| Pin | ラベル | データの流れ | MCU (= キーボード側) の動作 |
|----:|---|---|---|
| 3 | KEY RxD | ホストが**受信** ← キーボード | MCU は**送信** (TX) |
| 4 | KEY TxD | ホストが**送信** → キーボード | MCU は**受信** (RX) |

UART の一般則「片側の Tx は相手側の Rx に繋ぐ」を素直に適用すれば良い:
- ホストの TxD (Pin 4) → MCU の RX1 (PB11)
- ホストの RxD (Pin 3) ← MCU の TX1 (PB10)

## ミニ DIN 7pin (本体側 = メス、当基板側 = オス)

```
       _______
      /  4 3  \         (DIN 7pin Male, looking at the plug from outside)
     | 7  6  5 |
      \_2 1__/
```

本基板は **ユーザ手配のコネクタを直接はんだ付け** する想定で、フットプリント
は自作のダミー (`MiniDIN-7P_PLACEHOLDER.kicad_mod`) を仮割当している。
KiCad プロジェクト確定時に実物に合わせて差し替えること。実際のピン番号配置は
コネクタの規格 (例: Hirose HMD-7P 系) と本体側のピンアサインを必ずデータシート
で突き合わせる。X68000 サービスマニュアル準拠:

| Pin | 信号 | 当基板での扱い |
|-----|------|---|
| 1 | Vcc2 (+5V) | NC (既定。後付けジャンパで VBUS に接続可) |
| 2 | MSDATA (キーボード→本体) | MCU PB9 ← レベルシフタ |
| 3 | KEY RxD (キーボード→本体) | MCU PB10 (TX1) ← レベルシフタ |
| 4 | KEY TxD (本体→キーボード) | MCU PB11 (RX1) ← レベルシフタ |
| 5 | READY (本体→キーボード) | MCU PB12 ← レベルシフタ |
| 6 | REMOTE (TV リモコン用) | MCU PB8 ← レベルシフタ |
| 7 | GND | 共通 GND |

## 信号レベルとバッファ

- すべて **5V TTL**
- CH32X035 は **5V トレラントではない** (絶対最大定格 VIN ≤ VDD+0.3V =
  3.6V at VDD=3.3V)。詳細は `../docs/CH32X035.md` §5・§7 参照。
- そのため X68000 側 5V 信号と接続する全 5 ラインに **Toshiba TC7MPB9307FT
  (8 ch パッシブ FET バススイッチ、TSSOP-20)** を介す。
  - VCCA = VDD33 (3.3V、MCU 側) / VCCB = VBUS (5V、X68000 側) / OE = GND 固定
  - チャネル 1〜5 を使用、6〜8 は A 側を GND に落としてフローティング回避
- パッシブ FET 型 (FET パススルー) を選定する理由は ATARI アダプタと同じで、
  X68000 ホスト側 8255 + プルアップとの相性を考慮したもの。`../docs/CH32X035.md`
  §7 参照。

## 電源

- **採用方針 (案 A)**: USB Type-C (スマホ) からのバスパワー 5V を LDO で
  3.3V に降圧して MCU を駆動。X68000 本体側 Vcc2 (+5V, DIN Pin 1) は
  既定で NC とし、本体給電は受け取らない。
- **代替 (案 B / 不採用)**: X68000 本体の Vcc2 を電源として使い、USB は信号のみ。
  スマホから給電できない場合に困るため通常は採用しない。

VBUS と Vcc2 を **同時に通電させない** ことが重要。DIN Pin 1 を使う場合は
後付けで Schottky ダイオード / 0Ω ジャンパを VBUS に向けて挿入する。

## レイアウトのヒント

- USB Type-C コネクタは基板の一辺に
- ミニ DIN 7pin は反対側エッジ。X68000 本体への取り回しを想定して
  ケーブル方向を考える
- QFN28 周りはデカップリング (4.7µF + 0.1µF) を近接配置
- USB 信号 (DP/DM) は 90Ω 差動でルーティング
- KEY TxD / KEY RxD / MSDATA / READY / REMOTE は 1 つの DIN コネクタに
  集約、ESD 保護 (TVS) を入れることを推奨 (TODO)

## 参考

- USB Type-C CC 1/2 ピンには 5.1kΩ プルダウン (VBUS / Source 認識のため必須)
- READY は X68000 起動時にしばらく Low のままなので、送信キューを内部に持つ
  実装を前提 (FW 側で対応済み)
- マウス機能を別基板に分けたい場合は、`functions/x68k_mouse/` を外して
  USART4 関連回路を不実装にし、コネクタも MSDATA を未配線にできる
- REMOTE (Pin 6) は X68000 純正キーボード上の TV リモコン受光部信号。
  当基板では PB8 GPIO に接続しておくだけで、用途は将来 FW 側で検討する
