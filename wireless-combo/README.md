# MimicX Wireless Combo Adapter (XIAO ESP32-C6 + CH32X035)

*BLE-MIDI wireless Combined adapter: an ESP32-C6 takes MIDI in over BLE or USB
and relays it to a CH32X035 device engine over I2C, driving both retro ports
from one board. **Board rev 0.1 — the circuit is settled, the layout is not yet
routed**, so there are no renders or layer plots here yet. Designed in
[atopile](https://atopile.io); the circuit lives in
[`wireless_combo.ato`](wireless_combo.ato).*

- **ブロック図 / block diagram**:
  [PDF](docs/wireless-combo-block-diagram.pdf) ·
  [SVG](docs/wireless-combo-block-diagram.svg)
- **USB VID:PID**: `0x1209:0x9211` (Mimic X Bridge — 無線側は ESP32 が USB
  デバイスとして見えるため、有線 2 基板とは別 PID)

BLE-MIDI 無線対応の Combined アダプタ。1 枚の基板に

- **Seeed XIAO ESP32-C6** — BLE-MIDI ホスト / CH32 の自動 OTA (SWD) / 電源・BOOT 制御
- **CH32X035G8U6** — デバイスエンジン (`combined-i2c` ファーム)
- **JST XH 9P** — ケーブル経由で D-SUB 9pin (ATARI / X68000 / MD ジョイスティック)
- **JST XH 7P** — ケーブル経由で Mini DIN 7pin (X68000 キーボード / マウス / REMOTE)
- **JST XH 3P** — WCH-LinkE 用 SWD デバッグ端子 (保険)

D-SUB / Mini DIN は基板直付けせず、JST XH (ロック付き・逆挿し不可・3A) 経由の
ケーブル接続とする。9P ≠ 7P なのでケーブルの挿し間違いは物理的に起きない。

を搭載する。ファームウェアは既存の 2 チップ構成 (protocol §2.5) をそのまま使う:
CH32 側 = `MimicX-firmware/platforms/ch32x035` の `combined-i2c` env、
ESP32 側 = `MimicX-firmware/platforms/esp32c6` (内包イメージを `mimic-x-combo` に設定)。

## ブロック図

```
                USB-C (給電 + 書込/ログ)
                   │
  ┌────────────────┴───┐        VDD33 (常時)
  │  XIAO ESP32-C6     │3V3 ──┬─────────────┐
  │                    │      │             S│
  │ D0: CH32_PWR_OFF ──┼──────┼──────────── G│Q1 AO3401A (default ON)
  │ D1: CH32_BOOT ─────┼─4.7k─┼─┐           D│
  │ D3: CH32_INT ──────┼──┐   │ │   VDD_SW ──┴─┬──[10k]── GND (ブリーダ)
  │ D4: SDA_SWDIO ─────┼─┐│   │ │      │       │
  │ D5: SCL_SWCLK ─────┼┐││ [pull-ups 4.7k/10k は VDD_SW へ]
  └────────────────────┘│││   │ │      │
                        │││   │ │  ┌───┴──────────┐    ┌─ TC7MPB9307FT ─ D-SUB9
             PC19/SCL ──┘││   │ └──│ PC17 (BOOT)  │────┤   (VCCB = D-SUB Pin5)
             PC18/SDA ───┘│   │    │  CH32X035    │    │
             PB1/INT ─────┘   │    │ combined-i2c │    └─ TC7MPB9307FT ─ MiniDIN7
                              │    │   PB0 ─ WS2812B    (VCCB = DIN Pin1 Vcc2)
              BOOTボタン ─4.7k┴────│              │
                                   └──────────────┘
```

## この基板の設計肝: ESP32 による CH32 の電源 / BOOT 制御

既存構成の弱点は「CH32 ファームが起動直後に SDI (SWD) を無効化するため、
I2C が死ぬと SWD でも復旧できない半ブリック状態が生じる」こと (実事例あり)。
本基板は WCH ISP ブートローダが SDI を有効のまま残すこと (実機検証済み) を
利用し、ESP32 の GPIO 2 本で **どんなファーム状態からでも** 復旧できる:

| XIAO ピン | GPIO | 機能 | 極性 |
|---|---|---|---|
| D0 | GPIO0 | `CH32_PWR_OFF` — Q1 ゲート | High=電源OFF (100k PD でデフォルトON) |
| D1 | GPIO1 | `CH32_BOOT` — 4.7k 経由で PC17(UDP) | POR 時 High=ブートローダ突入 |
| D3 | GPIO21 | `CH32_INT` (既存) | active-low, 10k PU→VDD_SW |
| D4 | GPIO22 | `SDA_SWDIO` (既存) | 4.7k PU→VDD_SW |
| D5 | GPIO23 | `SCL_SWCLK` (既存) | 4.7k PU→VDD_SW |

### 復旧シーケンス (ESP32 ファームに実装する)

```
1. SDA/SCL/INT/BOOT を Low 出力 or プルなし Hi-Z にする
   (OFF 中に 1 本でも High があると保護ダイオード経由のバックフィードで
    POR がかからない。プルアップ類を VDD_SW に繋いでいるのも同じ理由)
2. CH32_PWR_OFF = High → 100ms 待つ (10k ブリーダで VDD_SW 放電)
3. CH32_BOOT = High
4. CH32_PWR_OFF = Low → POR。PC17=High でブートローダ突入 (SDI 有効)
5. ~50ms 後 CH32_BOOT = Low (書込後の ndmreset でアプリ起動させるため)
6. 即 SWD 書込 (ブートローダのタイムアウト前に halt すれば以降は安全)
```

`ch32_ota.c` の SWD 失敗時フォールバックとしてこのシーケンスを足せば、
ENTER_SWD ハンドオフ (CH32 ファームの協力前提) に依存しない自己修復になる。

## 電源設計

5V 電源は 3 系統あり、**どれか 1 つでも供給されていれば動作する**:

```
USB-C (XIAO) ────────────────┬── VCC_ESP (5V 幹線 = XIAO 5V ピン)
VCC_JOY (D-SUB Pin5) ─▶|SS14─┤        │ XIAO 内蔵 LDO
VCC_KBD (DIN Pin1)   ─▶|SS14─┘        ▼
                                    VDD33 (3.3V 常時系)
                                      │ Q1 (P-FET)
                                      ▼
                                    VDD_SW (CH32 サブシステム)
```

- XIAO の 3V3 ピンは内蔵 LDO の**出力** (入力不可)。USB 未接続時はホスト 5V を
  ショットキー経由で 5V ピン (VBUS) に注入して XIAO を駆動する (Seeed 公式推奨方式)
- 回路全体の 3.3V は XIAO 内蔵 LDO 出力 (`VDD33`) を使う。CH32 サブシステムの
  追加負荷は最悪 ~60mA 程度 (CH32 ~10mA + WS2812 ≤45mA + プルアップ) で、
  ESP32 自身の無線ピークを賄う前提の内蔵レギュレータの範囲内。
  ノイズや電流に不安が出た場合は VCC_ESP → 外付け 3.3V レギュレータで
  ESP32 以外の 3.3V を分離する代替案あり (既存基板の LP5907MFX-3.3 は 250mA で
  この用途には十分。ただし ESP32 本体は駆動できない点に注意)
- SS14 の Vf ≈ 0.35V → ホスト給電時 VCC_ESP ≈ 4.65V。ダイオードにより
  VCC_JOY / VCC_KBD は相互に直結されず、USB VBUS からホストへの逆流もない
- ホスト給電時は ESP32 の無線 TX バースト (数百 mA) がレトロ機のポート給電に
  乗る。VCC_ESP に 22µF バルクを置いて平滑しているが、**ホスト側ポートの
  給電能力 (ヒューズ/許容電流) は実機で要確認**
- CH32 サブシステム (CH32 / WS2812 / プルアップ / レベルシフタ VCCA) は
  すべて `VDD_SW` (Q1 スイッチド)。**このレールに載せ忘れた常時系プルアップが
  1 本でもあると電源 OFF 復旧が壊れる**ので、変更時は要注意
- レベルシフタ B 側 (5V) はホスト給電: `VCC_JOY` (D-SUB Pin5) と
  `VCC_KBD` (DIN Pin1 Vcc2) を各コネクタから直接取る
- CH32 の USB は未接続 (PC16 = NC, PC17 = BOOT 制御専用)。最終復旧手段も
  ESP32 経由の BOOT+SWD で代替できるため、wchisp 用 USB は設けない

## ケーブル配線 (XH ピン番号 = 先方コネクタのピン番号)

| XH 9P (J: joystick) | D-SUB 9pin | | XH 7P (J: keyboard) | Mini DIN 7pin |
|---|---|---|---|---|
| 1 | 1 Up | | 1 | 1 Vcc2 (+5V) |
| 2 | 2 Down | | 2 | 2 MSDATA |
| 3 | 3 Left | | 3 | 3 KEY RxD |
| 4 | 4 Right | | 4 | 4 KEY TxD |
| 5 | 5 +5V (ホスト給電) | | 5 | 5 READY |
| 6 | 6 TRIG-A | | 6 | 6 REMOTE |
| 7 | 7 TRIG-B | | 7 | 7 GND (シールドもここへ) |
| 8 | 8 COMMON / TH | | | |
| 9 | 9 GND (シェルもここへ) | | | |

- D-SUB シェル / DIN シールドは**ケーブル側コネクタの根元で GND 線に合流**させる
- 基板側: B9B-XH-A(LF)(SN) = LCSC C157966、B7B-XH-A(LF)(SN) = LCSC C144398
- ケーブル側: XHP-9 / XHP-7 ハウジング + SXH-001T-P0.6 コンタクト

### SWD デバッグ端子 (XH 3P, B3B-XH-A = LCSC C144394)

WCH-LinkE でのデバッグ / 強制書き換え用の保険。PC18/PC19 は I2C/SWD 兼用線
なので実体は I2C バスのタップ。

| XH 3P | 信号 |
|---|---|
| 1 | SWCLK (= SCL, CH32 PC19) |
| 2 | SWDIO (= SDA, CH32 PC18) |
| 3 | GND |

使用時の注意:
- ESP32 が同じ線を駆動するため、**WCH-LinkE 使用中は ESP32 を静かにしておく**
  (リセット保持、または I2C/OTA が走っていないタイミングで)
- 通常稼働中の CH32 は SDI off なので、**BOOT ボタン + 電源再投入でブート
  ローダ (SDI 有効) にしてから**繋ぐと確実

## 実装前 TODO

- [ ] `parts/XIAO_ESP32C6/` のフットプリントは**仮置き** (2.54mm ピッチ /
      列間 15.24mm)。Seeed 公式の機械図面と照合して確定させる
- [ ] `parts/AO3401A_SOT23/` の SOT-23 ランド、`parts/SS14_SMA/` の SMA ランド、
      `parts/JST_XH_B9B/` `parts/JST_XH_B7B/` `parts/JST_XH_B3B/` の XH ランドを
      データシート推奨値と照合
- [ ] 信号ラインの TVS (SP3012-04UTG 等) 追加検討 — ケーブル化で配線が伸びる
      ため既存基板より優先度高
- [ ] 10kΩ / 100kΩ 抵抗は初回 `ato build` 時に LCSC ピッカーが解決する
      (ネットワーク必要)。他はローカル parts/ キャッシュで完結
- [ ] ESP32 ファームに `CH32_PWR_OFF` / `CH32_BOOT` の制御と復旧フォール
      バックを実装 (`board_config.h` に BOARD_CH32_PWR_GPIO=0 /
      BOARD_CH32_BOOT_GPIO=1 を追加)

## ビルド

```sh
cd MimicX-hardware/wireless-combo
ato build
```
