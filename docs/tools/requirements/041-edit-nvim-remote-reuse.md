# `Ctrl+E` の nvim remote で tab を再利用する (`editor_nvim_remote`) 要件定義

## 概要

`atcoder start` / `test --interactive` の `Ctrl+E` でファイルを開くとき、nvim の `:terminal` 内 (`$NVIM` 在り) では親 nvim に remote 送信する ([038](038-start-edit-in-editor.md))。従来は `--remote-tab` で送っていたため**問題を切り替えるたびに親 nvim に新しいタブが増えて**煩わしかった。本要件では nvim remote のターゲットを config キー `editor_nvim_remote` で選べるようにし、**既定を「現在のウィンドウで開く (`--remote`) = タブを再利用」に変更**する。`tab` を選べば従来の `--remote-tab` (問題ごとに新規タブ) に戻せる。

## 背景・目的

- ユーザは nvim の `:terminal` から `atcoder start` を回しながら、問題を `]`/`[`・`:e` でナビして連続で解く。問題が変わるたびに `Ctrl+E` を押すと、[038] の `--remote-tab` は**毎回**親 nvim に新規タブを作る (別ファイルなら必ず新タブ)。結果、解いた問題数だけタブが溜まり、目的のタブを探すのが面倒になっていた。
- nvim には `--remote <file>` があり、これは**サーバ nvim の現在のウィンドウ**でファイルを開く (= いま見ているタブのバッファを差し替える)。問題を切り替えても 1 つのタブを使い回せる。
- `--remote-tab` を望む人 (前問を別タブに残して参照したい等) もいるため、挙動を壊し切らず **config で切り替え可能**にする。設定を司る単一情報源 (`internal/config/keys.go` の `fields`) は `layout` の enum 前例があり、そこに 1 エントリ足すだけで config / 補完が対応する。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 設定キー | トップレベル `editor_nvim_remote` (enum: `current` / `tab`)。既定 `current` | `-silent` 変種・`--remote-send` での行ジャンプ |
| `current` | nvim 内 remote を `nvim --server <sock> --remote <path>` にする (現在のウィンドウで開く = タブ再利用) | — |
| `tab` | 従来どおり `nvim --server <sock> --remote-tab <path>` (問題ごとに新規タブ。[038] の旧既定) | — |
| 対象経路 | nvim 内 (`$NVIM` 在り) の remote 起動のみ | — |
| 適用範囲 | `start` 分割画面 + `test --interactive` の chat (どちらも `editFunc` 経由) | — |

### 境界

- **nvim 外フォールバック (`$NVIM` 無し) には影響しない**。そちらは従来どおり config `editor` > `$EDITOR` > `nvim` で起動する。`editor_nvim_remote` は nvim 内 remote のターゲットだけを司る。
- 解答ファイルは**開くだけ**。中身・判定・提出・ナビ・exit code には触れない。
- 外部ツール (`nvr` 等) には依存しない (nvim 組み込みの `--server`/`--remote`/`--remote-tab`)。

## CLI / TUI 仕様

新サブコマンド・新フラグ無し。config キー `editor_nvim_remote` を 1 つ足し、`Ctrl+E` の nvim 内分岐がそれを読む。

### 設定キー

| キー | 型 | 既定 | 値 | 説明 |
|---|---|---|---|---|
| `editor_nvim_remote` | enum | `current` | `current` / `tab` | nvim の `:terminal` 内で `Ctrl+E` したときの remote ターゲット。`current`=現在のウィンドウで開く (タブ再利用)、`tab`=新規タブ (従来) |

```sh
atcoder config get editor_nvim_remote      # → current (未設定でも既定を表示)
atcoder config set editor_nvim_remote tab  # 従来の新規タブ挙動に戻す
atcoder config unset editor_nvim_remote    # 既定 (current) に戻す
```

### エディタ起動の決定 (純粋関数 `planEdit`)

`planEdit(nvimSock, nvimRemote, editorOverride, editorEnv, path)` が「何をどう起動するか」を返す:

| 条件 | 起動方法 | argv |
|---|---|---|
| `nvimSock` (= `$NVIM`) 在り・`nvimRemote` != `tab` (既定) | **remote** | `nvim --server <sock> --remote <path>` |
| `nvimSock` 在り・`nvimRemote` == `tab` | remote | `nvim --server <sock> --remote-tab <path>` |
| `$NVIM` 無し・`editorOverride` (config) 在り | **exec** | `<editorOverride を空白分割> <path>` |
| `$NVIM` 無し・`$EDITOR` 在り | exec | `<$EDITOR> <path>` |
| いずれも無し | exec | `nvim <path>` |

- `nvimRemote` が空文字 (config 未設定) のときは既定の `current` 扱い = `--remote`。
- remote 起動は [038] と同じく `.Start()` の best-effort (端末を奪わない・非ブロッキング)。nvim 外 exec 経路は本要件で不変。

### 出力イメージ (chat 内)

```
(nvim で開きました: exercise/2026/06/18/abc357_d.py — :terminal の親 nvim に送信)
```
表示文は [038] と同じ (remote の送信先が tab か current かで文言は変えない)。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| nvim 内・`editor_nvim_remote` 未設定 or `current` | 親 nvim の**現在のウィンドウ**に解答を開く。タブは増えない (前問のタブを使い回す) |
| nvim 内・`editor_nvim_remote` = `tab` | 親 nvim の**新規タブ**に解答を開く ([038] の従来挙動) |
| nvim 外 (`$NVIM` 無し) | 本要件で不変 (config `editor` / `$EDITOR` / `nvim`) |
| ナビ ([027]) で問題移動後 | `Ctrl+E` は移動先の解答パスを `current`/`tab` の設定どおりに開く |
| `editor_nvim_remote` に未知の値 | `config set` 時に `ErrInvalidValue` (exit 2)。`current`/`tab` のみ許容 |

- **既存非破壊**: `Ctrl+E` を押さない限り従来どおり。解答ファイルは開くだけで書き換えない。
- **挙動変更点**: nvim 内 remote の既定が `--remote-tab` → `--remote` に変わる ([038] からの差分。本要件が上書きする)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/config/config.go` | `Config` に `EditorNvimRemote string` (`toml:"editor_nvim_remote,omitempty"`) を追加 |
| `internal/config/keys.go` | `fields` に `editor_nvim_remote` を enum (`cands: ["current","tab"]`) で登録。`repr` は未設定時 `current` を返す。`set` は `current`/`tab` 以外を `ErrInvalidValue` で弾く |
| `cmd/atcoder/edit.go` | `planEdit` に `nvimRemote` 引数を追加し、`tab` なら `--remote-tab`・それ以外は `--remote` を選ぶ。`editFunc(editorOverride, nvimRemote string)` に変更 |
| `cmd/atcoder/start.go` | `startConfig` に `nvimRemote` を追加し `cfg.EditorNvimRemote` を格納、`editFunc(c.editor, c.nvimRemote)` を注入 |
| `cmd/atcoder/test.go` / `adhoc.go` | `runAdHoc` / `makeChatRunner` に `nvimRemote` を通し、`editFunc(editorOverride, nvimRemote)` を注入 |
| `cmd/atcoder/edit_test.go` | `planEdit` の test に `nvimRemote` 列を足し、既定 (current=`--remote`) / `tab` (`--remote-tab`) の両 argv を assert |
| `internal/config/keys_test.go` | `editor_nvim_remote` の get 既定 (`current`) / set 正常 (`tab`) / set 異常 (未知値→`ErrInvalidValue`) を test |
| `docs/tools/usage/config.md` / `docs/tools/usage/start.md` / `docs/tools/usage/test.md` | config キー一覧・`Ctrl+E` 説明に `editor_nvim_remote` と既定 `current` を追記 |
| `docs/tools/requirements/038-start-edit-in-editor.md` | remote 既定が本要件で `--remote` に変わった旨の注記と相互リンク |

### 型の素描

```go
// internal/config/config.go
type Config struct {
    Layout           string `toml:"layout,omitempty"`
    Editor           string `toml:"editor,omitempty"`
    EditorNvimRemote string `toml:"editor_nvim_remote,omitempty"` // current(既定) / tab
    // ...
}

// cmd/atcoder/edit.go
func planEdit(nvimSock, nvimRemote, editorOverride, editorEnv, path string) editAction // 純粋
func editFunc(editorOverride, nvimRemote string) ui.EditFunc
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `editor_nvim_remote` に `current`/`tab` 以外を `set` | `ErrInvalidValue` → exit 2 (既存 `config set` の分類に乗る) |
| config 未設定 (空文字) | 既定 `current` 扱い (= `--remote`)。`config get` は `current` を表示 |
| remote `.Start()` 失敗 | `(エディタ起動に失敗: …)` を err 行 (chat 継続。[038] と同じ) |
| exit code | TUI 内アクションは不変。`config set` の値エラーのみ exit 2 |

## 非機能要件

- **前方互換**: config キーを足すだけ。既存の `config.toml` (キー無し) は既定 `current` で動く。`tab` を設定すれば [038] の旧挙動に完全復帰できる。
- **決定的にテスト可能**: 起動方法の決定は純粋関数 `planEdit` に隔離されており、`nvimRemote` の値ごとに argv をユニットテストする。
- **既存非破壊**: nvim 外フォールバック・他キー・解答ファイルは不変。
- **外部依存なし**: nvim 組み込みの `--remote`/`--remote-tab` のみ。

## 将来の拡張ポイント

- `--remote-silent` / `--remote-tab-silent` 変種 (ファイルが既に開いていても警告を出さない) を別の値として足す。
- `--remote-send` で失敗ケースの行へジャンプ。
- 言語別・レイアウト別のエディタ/remote 設定。

## 用語

- **`--remote`**: nvim サーバの**現在のウィンドウ**でファイルを開く (タブを使い回す)。
- **`--remote-tab`**: nvim サーバに**新規タブ**でファイルを開く (既に開いていればそのタブへジャンプ)。
- ID 用語 (`contest_id` / `task_id` / `letter`) は既存要件に準ずる。

## 関連ドキュメント

- 親要件 (Ctrl+E エディタ起動): [038](038-start-edit-in-editor.md)
- chat の外部アクション前例: [026](026-chat-submit.md) / 分割画面: [023](023-start-split-screen.md) / ナビ: [027](027-start-problem-navigation.md)
- 利用手引: `docs/tools/usage/config.md` / `docs/tools/usage/start.md` / `docs/tools/usage/test.md`
</content>
</invoke>
