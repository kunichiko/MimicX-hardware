# VS Code プラグイン Build ボタンで pcbnew が自動 reload されない件

調査日: 2026-05-21
対象バージョン: atopile 0.15.7 (`atopile.atopile-0.15.7` 拡張)

## 症状

VS Code 拡張の Build ボタン (`atopile.startBuild` コマンド) を押すと PCB 更新
は成功するが、開いている KiCad pcbnew が再読み込みされない。ターミナルで
`ato build` を実行した場合は同じビルド後に pcbnew が自動でリロードされる。

## 原因

`reload_pcb` の呼び出し箇所が **CLI 経路にしか実装されていない**。

| 実行経路 | `reload_pcb` 呼び出し | 関連コード |
|---|---|---|
| `ato build` (ターミナル) | ✅ あり | `atopile/cli/build.py:469` |
| VS Code Build ボタン | ❌ なし | `atopile.startBuild` → WebSocket `startBuild` action → `atopile/server/ui/websocket.py:1623` → `builds.handle_start_build()` |

VS Code 拡張は内部に `atopile core server` を持ち、Build ボタンから
WebSocket メッセージ (`startBuild`) を送る構造になっている。
core server 側のビルドハンドラはディスクへの `.kicad_pcb` 書き出しまで
やっているが、KiCad IPC (`faebryk.libs.kicad.ipc.reload_pcb`) を呼び出す
処理が欠落している。

WebSocket アクション一覧 (`atopile/server/ui/websocket.py`):

- `startBuild`, `cancelBuild`, `getBuildsByProject`, `getRecentBuilds`,
  `getAutolayoutData`, `submitAutolayoutJob`, ...

→ `reloadPcb` / `openKicad` 系のアクションは存在しない。

`_reload_pcb_in_kicad` 関数は `atopile/server/domains/layout.py:28` と
`atopile/server/domains/kicad.py` に存在するが、こちらは「ライブレイアウト
差分同期」用途で、Build フローからは呼ばれない経路。

## 当面の回避策

1. **VS Code 統合ターミナルから `ato build` を打つ** — CLI 経路に乗るので
   IPC reload まで含まれる
2. **pcbnew で手動 Revert** — `File → Revert` (Cmd+Shift+Z)
3. **KiCad の外部変更検知** — KiCad 9 は外部変更を検出するとバナーで
   reload を促す (Preferences > Common 周りの設定に依存)

## 修正提案 (issue / PR にする場合)

`atopile/server/ui/websocket.py` の `startBuild` ケースで build 成功後に
`reload_pcb` を呼ぶようにする。CLI 側と同じインポート:

```python
from faebryk.libs.kicad.ipc import reload_pcb
```

を流用すれば実装は数行で済むと見られる。`handle_start_build` 完了
コールバックに以下相当を入れる:

```python
try:
    reload_pcb(build_cfg.paths.layout,
               backup_path=build_cfg.paths.output_base)
except Exception as e:
    logger.warning(f"{e}\nReload pcb manually in KiCAD")
```

## 関連ファイル (参考用、絶対パスは環境依存)

- `~/.local/share/uv/tools/atopile/lib/python3.14/site-packages/atopile/cli/build.py`
  (CLI build エントリ — reload_pcb 呼び出しあり)
- `~/.local/share/uv/tools/atopile/lib/python3.14/site-packages/atopile/server/ui/websocket.py`
  (WebSocket アクションハンドラ — reload_pcb 呼び出しなし)
- `~/.local/share/uv/tools/atopile/lib/python3.14/site-packages/faebryk/libs/kicad/ipc.py`
  (KiCad IPC ラッパー)
- `~/.vscode/extensions/atopile.atopile-0.15.7/dist/extension.js`
  (VS Code 拡張本体、`startBuild` コマンドハンドラ)

## アクション

- [ ] `atopile/atopile` リポジトリに issue を立てる (本ファイルの内容を貼り付け)
- [ ] 余裕があれば修正 PR を提出
