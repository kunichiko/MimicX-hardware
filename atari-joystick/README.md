# atari-joystick

Mimic X — ATARI 仕様ジョイスティックアダプタ基板

## 用途

スマートフォン (USB-MIDI ホスト) から CH32X035 経由で、ATARI / メガドライブ 6
ボタンファイティングパッド互換のジョイスティック信号を出力する。X68000 等の
9pin D-SUB ジョイスティックポートに接続して使用する。

## 主要部品

| 部品 | 型番 / 仕様 | 備考 |
|------|-----------|------|
| MCU | WCH CH32X035G8U6 | QFN28 (4×4 mm)、48MHz、5V トレラント、USB Full-Speed 内蔵 |
| USB コネクタ | USB Type-C (Receptacle, 16pin, TYPE-C-31-M-12) | スマートフォンと接続 |
| 出力コネクタ | D-SUB 9pin **メス** (CONNFLY DS1037-09FNAKT74-0CC) | ATARI/X68000 ジョイスティックポート (ホスト側オスに直挿し) |
| LED | チップ LED (0603) ×2 | デバッグ用 (PB3, PB4) |
| その他 | ESD 保護 (USB), デカップリング 0.1µF / 4.7µF, USB Type-C CC 抵抗 5.1kΩ ×2 |

## ピン割当 (CH32X035 → コネクタ)

ファームウェア `MimicX-firmware/src/functions/joystick/joystick.c` 参照。

| MCU ピン | 信号 | D-SUB 9pin | 機能 |
|---------|------|-----------|------|
| PA0     | COMMON / TH (TIM2_CH1) | Pin 8 | MD 6B 切替検出 (input capture + DMA) |
| PA1     | Up   | Pin 1 | アクティブ Low (open-drain 推奨) |
| PA2     | Down | Pin 2 | 同上 |
| PA3     | Left | Pin 3 | 同上 |
| PA4     | Right | Pin 4 | 同上 |
| PA6     | TRIG-A | Pin 6 | 同上 |
| PA7     | TRIG-B | Pin 7 | 同上 |
| PB3     | Debug LED 0 | — | (基板上、緑/赤) |
| PB4     | Debug LED 1 | — | (基板上、緑/赤) |
| —       | GND  | Pin 9 | ホスト側と共通 |
| —       | +5V  | Pin 5 | ホスト→当基板給電 (任意、または USB 給電のみ) |

## D-SUB 9pin (ホスト側 = オス、当基板側 = メス) ピンアサイン

X68000 等のホスト機側 D-SUB 9pin ジョイスティックポートは **オス**。本基板は
そこに直挿しできるよう **メス** を実装する。

```
   5 4 3 2 1     (D-SUB 9pin Female, looking at the mating face)
    9 8 7 6
```

| Pin | 信号 (ATARI / X68000 標準) |
|-----|------|
| 1 | Up |
| 2 | Down |
| 3 | Left |
| 4 | Right |
| 5 | +5V (host-supplied; 通常 NC) |
| 6 | TRIG-A |
| 7 | TRIG-B |
| 8 | COMMON (TH) |
| 9 | GND |

## 出力段の検討事項

- ATARI 規格では各信号線は本来 open-collector / open-drain。**5V トレラント**
  であっても CH32X035 の GPIO は出力 push-pull がデフォルトなので、ピンに
  直結するとホスト側 (X68000) のプルアップに対して干渉する可能性がある。
  - 案 A: **GPIO 出力モードを open-drain に設定** (ファーム側で `GPIO_CNF_OUT_OD`)
    かつ外付けプルアップなしで、ホスト側プルアップを利用
  - 案 B: 各信号にバスバッファ (74HC125 等) を入れる
  - 案 C: 個別 N-MOSFET (BSS138 など) で擬似 open-drain
- TH (PA0) は **入力**。MD 6 ボタンモードで本体からの信号変化を input capture
  で検出するため、ESD/サージ保護 (TVS ダイオード) の挿入を推奨

## 電源

- 通常はスマホからの USB バスパワー (5V) で動作
- D-SUB Pin 5 は接続/未接続を検討 (オプションで JP / 0Ω ジャンパ)

## レイアウトのヒント

- USB Type-C コネクタは基板端に配置
- D-SUB 9pin は反対側または隣接エッジに配置
- QFN28 (4×4 mm) 周りはデカップリング (4.7µF + 0.1µF) を近接配置 (VDD ピン直近)
- USB 信号 (DP/DM) は 90Ω 差動でルーティング (短ければそこまでシビアではない)

## 参考

- USB Type-C CC 1/2 ピンには 5.1kΩ プルダウンを VBUS と Source 認識のため必須
- 本基板は Sink (Device 側) のため、CC2 抵抗だけでも動作する場合があるが両方
  実装が無難
