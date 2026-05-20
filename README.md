# MimicX-hardware

**製品名: Mimic X**

「Mimic X」プロジェクトのマイコン基板設計データ（KiCad）。

各バリエーションごとにサブフォルダに KiCad プロジェクトと設計仕様 (README) を
置く。共通 MCU は **WCH CH32X035G8U6** (QFN-28)、USB は Type-C で
スマートフォンと接続する。

## 基板バリエーション

- [`atari-joystick/`](atari-joystick/) — ATARI 仕様ジョイスティックアダプタ
  (D-SUB 9pin。X68000 / メガドライブ 6 ボタン互換)
  - [PCBレイアウト](https://kicanvas.org/?repo=https%3A%2F%2Fgithub.com%2Fkunichiko%2FMimicX-hardware%2Fblob%2Fmain%2Fatari-joystick%2Flayouts%2Fdefault%2Fdefault.kicad_pcb) - まだ未完成
- [`x68000-keyboard/`](x68000-keyboard/) — X68000 キーボードアダプタ
  (ミニ DIN 7pin。キーボード + マウス相乗り)
  - [PCBレイアウト](https://kicanvas.org/?repo=https%3A%2F%2Fgithub.com%2Fkunichiko%2FMimicX-hardware%2Fblob%2Fmain%2Fx68000-keyboard%2Flayouts%2Fdefault%2Fdefault.kicad_pcb)
- （今後追加予定）

## 共通設計事項

- **MCU**: CH32X035F8U6 (TSSOP-20、48MHz、USB Full-Speed、5V トレラント)
- **USB**: Type-C Receptacle、CC1/CC2 にそれぞれ 5.1kΩ プルダウン
- **電源**: USB バスパワー (5V) を基本とし、ターゲット機からの電源供給は
  逆流防止 / 切替可能にする
- **デバッグ**: PB3 / PB4 にチップ LED ×2 (基板実装時のみ)
- **デカップリング**: VDD ピンに 4.7µF + 0.1µF を近接配置

## 関連リポジトリ

- [MimicX-app](https://github.com/kunichiko/MimicX-app) - Flutterアプリ
- [MimicX-firmware](https://github.com/kunichiko/MimicX-firmware) - マイコンファームウェア
- [MimicX-protocol](https://github.com/kunichiko/MimicX-protocol) - MIDI通信プロトコルライブラリ
