# `atcoder start` から解答ファイルをエディタで開く (`Ctrl+E`・nvim remote) 要件定義

## 概要

`atcoder start` の分割画面 (および `test --interactive` の chat) で **`Ctrl+E`** を押すと、現在の解答ファイルをエディタで開く。nvim の `:terminal` から `atcoder start` を使っているとき (= 環境変数 `$NVIM` が在るとき) は、**既に動いている親 nvim にファイルを送る** (`nvim --server $NVIM --remote-tab <path>`) ことで、新しい nvim を入れ子に起動せず・端末をネストさせずに開く。nvim 外では通常どおりエディタを起動する。外部ツール (nvr 等) には依存せず、nvim 0.5+ 組み込みの `--server`/`--remote-tab` を使う。

## 背景・目的

- 分割画面で対話・判定を回しながら、解答を直すのに毎回「別ターミナル/別 nvim を開く」「start を抜ける」のは面倒。**その場のキー 1 つで解答を編集に開きたい**。
- ユーザは nvim の `:terminal` から `atcoder start` を起動することが多い。ここで素朴に `nvim <path>` を起動すると **nvim の中で nvim が動く入れ子 (ネスト)** になり、端末・キーバインドが二重になって扱いづらい。**親 nvim に送れば**ネストせず、いつものエディタのタブに解答が開く。
- 既に `Ctrl+S` (提出準備) という「chat に留まったまま外部アクションを起こす」前例があり、同じ注入パターン (`ChatHeader` にコールバック) に乗せられる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| キー | **`Ctrl+E`** (chat のグローバルキー。`Ctrl+S`/`Ctrl+G` と同じ層)。素の `e` は入力欄が文字として食うため不可、`:e` は問題ナビ ([027]) で使用済み | command モード `:edit` 別名 |
| nvim 連携 | `$NVIM` 在り → `nvim --server $NVIM --remote-tab <path>` で親 nvim に送る (ネスト回避・端末を奪わない) | `--remote-send` で行ジャンプ等 |
| フォールバック | `$NVIM` 無し → エディタを端末を奪って起動 (`tea.ExecProcess`)。エディタは config `editor` > `$EDITOR` > `nvim` | GUI エディタの background 起動最適化 |
| 設定 | config に `editor` キー (フォールバック時のエディタコマンド上書き) | 言語別エディタ |
| 対象 | `start` 分割画面 + `test --interactive` の chat (どちらも解答パスを持つ) | — |

### 境界

- 解答ファイルは**開くだけ**。中身は変えない (編集はユーザが行う)。判定・提出・ナビ・exit code には触れない。
- `Ctrl+C`/`Ctrl+D`/`Ctrl+S`/`Ctrl+G`・command モード・既存コマンドは不変。
- 外部 CLI ツール (`nvr` 等) には依存しない (nvim 組み込みの `--server`/`--remote-tab`)。

## CLI / TUI 仕様

新サブコマンド・新フラグ無し (config キー `editor` のみ追加)。`Ctrl+E` は chat の中で処理する。

### キー

| キー | 動作 |
|---|---|
| `Ctrl+E` | 現在の解答ファイルをエディタで開く。`$NVIM` 在り → 親 nvim に `--remote-tab` で送る (端末を奪わない・結果を 1 行表示)。`$NVIM` 無し → `tea.ExecProcess` でエディタを起動 (TUI を一時中断し、エディタ終了後に復帰) |

### エディタ起動の決定 (純粋関数 `planEdit`)

`planEdit(nvimSock, editorOverride, editorEnv, path)` が「何をどう起動するか」を返す:

| 条件 | 起動方法 | argv |
|---|---|---|
| `nvimSock` (= `$NVIM`) が非空 | **remote** (端末を奪わない。`.Start()` で best-effort) | `nvim --server <sock> --remote-tab <path>` |
| `$NVIM` 無し・`editorOverride` (config) 在り | **exec** (`tea.ExecProcess` で端末を奪う) | `<editorOverride を空白分割> <path>` |
| `$NVIM` 無し・`$EDITOR` 在り | exec | `<$EDITOR> <path>` |
| いずれも無し | exec | `nvim <path>` |

- remote は親 nvim 前提なので config `editor` 上書きより優先する (nvim の中に居るなら nvim に開くのが自然・ネスト回避が目的)。`editor`/`$EDITOR` は **nvim 外のフォールバック**を司る。
- remote 起動は `openBrowser` と同じく `.Start()` の best-effort (ブロックしない・TUI を壊さない)。exec 起動は `tea.ExecProcess` (bubbletea 公式の対話サブプロセス実行: TUI を suspend → エディタ → resume)。

### 出力イメージ (chat 内)

```
(nvim で開きました: exercise/2026/06/16/abc457_d.py — :terminal の親 nvim に送信)
```
nvim 外フォールバックは TUI を一時中断してエディタが全画面で開き、終了すると分割画面に戻る。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| nvim の `:terminal` 内 (`$NVIM` 在り) | 親 nvim の新規タブに解答を開く。**新しい nvim は起動しない** (ネスト回避)。bubbletea TUI は裏で動き続ける |
| nvim 外 (`$NVIM` 無し) | config `editor` / `$EDITOR` / `nvim` の順でエディタを `tea.ExecProcess` で起動。終了で分割画面へ復帰 |
| ナビ ([027]) で問題移動後 | `Ctrl+E` は**移動先の**解答パスを開く (`ChatHeader.WatchPath` が再ターゲットで更新される前提) |
| `Edit` 未注入 / 解答パス不明 | `(エディタ起動は利用できません)` を 1 行表示 (chat 継続) |
| remote 送信失敗 (`nvim` が PATH に無い等) | `(エディタ起動に失敗: …)` を 1 行表示 (chat 継続。落とさない) |

- **既存非破壊**: `Ctrl+E` を押さない限り従来どおり。解答ファイルは開くだけで書き換えない。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `ChatHeader` に `Edit EditFunc` を追加。`EditFunc func(path string) EditPlan` と `EditPlan{Exec *exec.Cmd; Message string; IsError bool}` 型。`Ctrl+E` ハンドラ: `Edit(WatchPath)` を呼び、`Exec` 非 nil なら `tea.ExecProcess`、nil なら `Message` を info/err 行に。`editDoneMsg` で復帰後の結果表示 |
| `cmd/atcoder/edit.go` (新規) | 純粋関数 `planEdit(nvimSock, editorOverride, editorEnv, path) editAction` と、それを `EditPlan` に変換する `editFunc(editorOverride string) ui.EditFunc` (remote は `exec.Command(...).Start()`、exec は `*exec.Cmd` を `EditPlan.Exec` に載せる) |
| `cmd/atcoder/start.go` / `adhoc.go` | `ChatHeader.Edit: editFunc(cfg.Editor)` を注入 (`Submit` と同じ流儀)。`start` は再ターゲットでも注入を保つ |
| `internal/config/keys.go` + config 構造体 | トップレベル `editor` キー (string、既定 "") を `fields` に登録し `cfg.Editor` で読む (`layout` と同じ作法) |
| `internal/ui/chat_test.go` / `cmd/atcoder/edit_test.go` | `planEdit` の `$NVIM` 在り (remote argv) / 無し (config 上書き・`$EDITOR`・既定 nvim) を test。`Ctrl+E` → `Edit` 呼び出し・未注入時の info 行を test |
| `docs/tools/atcoder-start-usage.md` / `atcoder-test-usage.md` / `atcoder-config-usage.md` | キー表に `Ctrl+E`、config に `editor` キーを追記 |

### 型の素描

```go
// internal/ui/chat.go
type EditPlan struct {
    Exec    *exec.Cmd // 非 nil: tea.ExecProcess で端末を奪って起動 (nvim 外)
    Message string    // 端末を奪わず即完了したとき (remote 送信済み) の表示文
    IsError bool
}
type EditFunc func(path string) EditPlan // ChatHeader.Edit に注入

// cmd/atcoder/edit.go
type editAction struct { remote bool; argv []string }
func planEdit(nvimSock, editorOverride, editorEnv, path string) editAction // 純粋
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `Edit` 未注入 (test の一部経路) | `(エディタ起動は利用できません)` を info 行。exit code 不変 |
| 解答パスが空 | 同上 (開く対象が無い) |
| remote `.Start()` 失敗 / exec 起動失敗 | `(エディタ起動に失敗: …)` を err 行。chat は継続 (落とさない) |
| config `editor` が空白のみ | 無効として `$EDITOR`/`nvim` にフォールバック |
| exit code | 影響なし (TUI 内アクション。引数誤り=2 / 実行時失敗=1 は不変) |

## 非機能要件

- **ネスト回避**: nvim 内 (`$NVIM` 在り) では新 nvim を起動せず親に送る。これが本要件の主目的。
- **TUI 非破壊**: remote は `.Start()` で非ブロッキング、exec は `tea.ExecProcess` (公式の suspend/resume)。bubbletea の描画を壊さない。
- **既存非破壊**: 解答ファイルは開くだけ。判定・提出・ナビ・他キーは不変。
- **外部依存なし**: nvim 組み込みの `--server`/`--remote-tab` のみ (nvr 不要)。
- **決定的にテスト可能**: 起動方法の決定を純粋関数 `planEdit` に隔離し、`$NVIM` 有無・config 上書き・`$EDITOR`・既定を argv 単位でユニットテストする。

## 将来の拡張ポイント

- command モード `:edit` 別名 (`Ctrl+E` と同じ `Edit` を呼ぶ)。
- `--remote-send` で特定行へジャンプ (失敗ケースの行など)。
- 言語別・レイアウト別のエディタ設定。

## 用語

- **`$NVIM`**: nvim 0.5+ が `:terminal` の子プロセスに渡すサーバ (named pipe) のパス。在れば「nvim の中で動いている」と判定できる。
- **remote / exec**: remote = 親 nvim に `--remote-tab` で送る (端末を奪わない)。exec = エディタを `tea.ExecProcess` で前面起動 (端末を奪う)。

> **後日変更 ([041](041-edit-nvim-remote-reuse.md))**: nvim 内 remote の既定は `--remote-tab` (新規タブ) から `--remote` (現在のウィンドウで開く = タブ再利用) に変更された。config `editor_nvim_remote = tab` で本要件の旧既定 (`--remote-tab`) に戻せる。

## 関連ドキュメント

- nvim remote ターゲット (タブ再利用) の選択: [041](041-edit-nvim-remote-reuse.md)
- chat の外部アクション前例 (Ctrl+S 提出): [026](026-chat-submit.md) / 分割画面: [023](023-start-split-screen.md) / ナビ: [027](027-start-problem-navigation.md)
- 端末キーの罠 (確実に届くキーを選ぶ): [ADR 0007](../decisions/0007-interactive-command-mode-trigger.md)
- 利用手引: `docs/tools/atcoder-start-usage.md` / `atcoder-test-usage.md` / `atcoder-config-usage.md`
