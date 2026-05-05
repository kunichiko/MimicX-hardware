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
| MCU | WCH CH32X035F8U6 | TSSOP-20、48MHz、5V トレラント、USB Full-Speed 内蔵 |
| USB コネクタ | USB Type-C (Receptacle, 16pin) | スマートフォンと接続 |
| 出力コネクタ | ミニ DIN 7pin オス | X68000 キーボード端子 |
| LED | チップ LED (0603) ×2 | デバッグ用 (PB3, PB4) |
| その他 | ESD 保護 (USB), デカップリング 0.1µF / 4.7µF, USB Type-C CC 抵抗 5.1kΩ ×2 |

## ピン割当 (CH32X035 → コネクタ)

ファームウェア `MimicX-firmware/src/functions/x68k_keyboard/` および
`x68k_mouse/` 参照。

| MCU ピン | 信号 | DIN 7pin | 方向 (MCU 視点) | 用途 |
|---------|------|---------|---------------|------|
| PA15 | USART2_TX (KEY TxD) | Pin 4 | OUT | キーコード送信 (2400/8N1) |
| PA16 | USART2_RX (KEY RxD) | Pin 3 | IN  | LED / リピート / MSCTRL コマンド受信 |
| PA17 | READY               | Pin 5 | IN  | 1=ホスト準備完了、Low 時送信抑止 |
| PA18 | USART3_TX (MSDATA)  | Pin 2 | OUT | マウスデータ送信 (4800/8N2) |
| PA19 | (デバッグ: MSCTRL モニタ) | — | OUT | 開発時のみ。リリース基板では未使用ピンに割当て可 |
| PB3  | Debug LED 0 | — | OUT | 基板上 LED |
| PB4  | Debug LED 1 | — | OUT | 基板上 LED |
| —    | +5V  | Pin 1 | — | ホスト→当基板給電 (Vcc2) |
| —    | GND  | Pin 7 | — | 共通 GND |

未使用ピン (Pin 6 = REMOTE) は基板上で未接続。

## ミニ DIN 7pin (本体側 = メス、当基板側 = オス)

```
       _______
      /  4 3  \         (DIN 7pin Male, looking at the plug from outside)
     | 7  6  5 |
      \_2 1__/
```

実際の番号配置はコネクタの規格 (例: Hirose HMD-7P 系) と本体側のピンアサイン
を必ずデータシートで突き合わせること。X68000 サービスマニュアル準拠:

| Pin | 信号 |
|-----|------|
| 1 | Vcc2 (+5V) |
| 2 | MSDATA (マウスデータ、本体方向) |
| 3 | KEY RxD (本体→キーボード) |
| 4 | KEY TxD (キーボード→本体) |
| 5 | READY (本体→キーボード) |
| 6 | REMOTE (TV リモコン用、未使用) |
| 7 | GND |

## 信号レベルとバッファ

- すべて **5V TTL**
- CH32X035 は 5V トレラント入力 / 出力は 3.3V (push-pull)
  - 受信側 (PA16/PA17): 5V → 3.3V 入力可能
  - 送信側 (PA15/PA18): 3.3V 出力で X68000 (TTL) に届くか要検証
    - もし不足するなら 74LVC125 などのレベルシフタ / バッファを挿入
    - または HCT 系 (74HCT125: VIH=2.0V) を 5V 駆動でレベルシフタとして使用

## 電源

- 案 A: USB Type-C (スマホ) からのバスパワー 5V を MCU に供給。
  X68000 本体側 Vcc2 (+5V) は接続しない (ダイオード分離)
- 案 B: X68000 本体の Vcc2 を電源として使い、USB は信号のみ。
  ただしスマホが USB から Mimic X に給電できないと困るので **案 A 推奨**

VBUS と Vcc2 を **同時に通電させない** ことが重要。逆流防止ダイオード or
ジャンパ JP を入れて切替可能にする。

## レイアウトのヒント

- USB Type-C コネクタは基板の一辺に
- ミニ DIN 7pin は反対側エッジ。X68000 本体への取り回しを想定して
  ケーブル方向を考える
- TSSOP-20 周りはデカップリング (4.7µF + 0.1µF) を近接配置
- USB 信号 (DP/DM) は 90Ω 差動でルーティング
- KEY TxD / MSDATA は 1 つの DIN コネクタに集約、ESD 保護 (TVS) を入れる

## 参考

- USB Type-C CC 1/2 ピンには 5.1kΩ プルダウン (VBUS / Source 認識のため必須)
- READY は X68000 起動時にしばらく Low のままなので、送信キューを内部に持つ
  実装を前提 (FW 側で対応済み)
- マウス機能を別基板に分けたい場合は、`functions/x68k_mouse/` を外して
  USART3 関連回路を不実装にし、コネクタも MSDATA を未配線にできる
