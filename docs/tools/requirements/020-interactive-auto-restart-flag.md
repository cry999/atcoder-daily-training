# `atcoder test --interactive --auto-restart` 要件定義

## 概要

対話モード (`atcoder test --interactive`) の chat TUI で、子プロセス終了後の **auto-restart を CLI フラグ `--auto-restart` (`-R`) で前もって選ぶ**ようにする。現状は子が終わるたびに「press [r] to run again, any other key to quit」と**終了後に対話で選ばせる**が、これを廃止し、起動時のフラグで「毎回自動再起動するか / 1 回で終わるか」を確定させる。

## 背景・目的

- 現状の chat TUI は子プロセスが終了すると `awaitingRestart` 状態に入り、`r` を押すと sticky な auto-restart モード、それ以外のキーで quit、という**終了後の対話選択**を要求する。
- この「終わってから毎回キーを聞かれる」形式は、連続実行したいか最初から分かっている場面 (インタラクティブ問題のリプレイ等) では摩擦になる。`r` の押し忘れや誤打で意図せず終了/継続することもある。
- 「最初に決める」方が明快で、スクリプト的にも素直。auto-restart の選択を**起動フラグ**に移し、終了後プロンプトを無くす。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 選択方法 | 起動フラグ `--auto-restart` (`-R`) の有無で確定 | `config.toml` に既定値 (例 `test.auto_restart`) |
| 対象モード | `--interactive` の **TTY chat TUI** のみ | — |
| 既定 (フラグ無し) | 子終了で即 quit (1 セッション) | — |
| `--auto-restart` 有り | 子終了のたびに自動再起動 (sticky)。`Ctrl+D` で現セッション後に終了、`Ctrl+C` で即中断 | 回数上限 `--auto-restart=N` |
| 廃止するもの | 終了後の `press [r] to run again` プロンプトと `r` キー処理 | — |
| 非 TTY (passthrough) | フラグは受理するが無効 (1 回実行) | — |

### 境界

- `--auto-restart` は**対話モード専用**。`--interactive` 無しでの指定はフラグ誤りとして **exit 2**。
- サンプルモード・ad-hoc ファイル入力 (`--in`/`--out`) とは無関係 (それらは chat TUI を使わない)。

## CLI 仕様

```
atcoder test <contest> --task <task> --interactive [-R | --auto-restart]
```

| フラグ | 説明 |
|---|---|
| `--auto-restart` (`-R`) | 対話モードで子プロセス終了のたびに自動で再起動する (sticky)。`--interactive` 必須。省略時は子終了で終了 |

### 処理ステップ (test.go)

1. `--interactive` / `--auto-restart` を解析。
2. `--auto-restart` が指定され、かつ `--interactive` が無ければ **exit 2** (`--auto-restart requires --interactive`)。
3. ad-hoc/対話モードへ。`autoRestart` を `runAdHoc → runexec.Options → ChatHeader → ui.RunChat` へ通す。
4. TTY なら chat TUI を `autoRestart` 初期値付きで起動。非 TTY passthrough なら `autoRestart` は無視 (1 回実行)。

### 出力イメージ (TTY chat TUI)

`--auto-restart` 有り — 起動時にヒントを出し、子終了のたびに無言で再起動:

```
$ atcoder test abc999 --task a --interactive --auto-restart
(auto-restart on — Ctrl+D to stop after current session, Ctrl+C to abort)
… session 1 …
─ session 2 ─
…
```

`--auto-restart` 無し (既定) — 子が終わったら即終了 (プロンプト無し):

```
$ atcoder test abc999 --task a --interactive
… session 1 …
(child process exited)
$
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `--interactive --auto-restart` (TTY) | 起動時から sticky auto-restart。子終了→即再起動。ヒント 1 回表示 |
| `--interactive` のみ (TTY) | 子終了→即 quit。終了後プロンプトは出さない |
| auto-restart 中の `Ctrl+D` | auto-restart 解除。現セッションの子が綺麗に終わったら quit (graceful) |
| auto-restart 中の `Ctrl+C` | 子を kill して即終了 |
| `--auto-restart` を `--interactive` 無しで指定 | "--auto-restart requires --interactive" で **exit 2** |
| `--auto-restart` + 非 TTY (パイプ) | 受理するが無効。passthrough で 1 回実行して終了 |
| `--auto-restart` + サンプル専用フラグ | 既存どおり、対話フラグとサンプル専用フラグの併用は **exit 2** |

- **挙動変更 (非互換)**: 終了後の `press [r] to run again` プロンプトと `r` キーによる restart は**廃止**する。フラグ無しの既定は「子終了で quit」になり、旧来の「プロンプトを出して待つ」とは異なる。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/test.go` | `--auto-restart` / `-R` フラグ追加。`--interactive` 必須の検証 (exit 2)。`runAdHoc` へ受け渡し。`usage()` 更新 |
| `cmd/atcoder/main.go` | `usage()` の `test` 行に `[-R\|--auto-restart]` を追記 |
| `cmd/atcoder/adhoc.go` | `runAdHoc` に `autoRestart bool` 引数。`runexec.Options.AutoRestart` と `runChat` の `ui.ChatHeader.AutoRestart` に結線 |
| `internal/runexec/runexec.go` | `Options.AutoRestart` と `ChatHeader.AutoRestart` を追加し、chat TUI 起動時に渡す |
| `internal/ui/chat.go` | `ChatHeader.AutoRestart` を追加。`initialChatModel` で `m.autoRestart` を初期化。`awaitingRestart` フィールド・`r` キー処理・終了後プロンプトを削除。`streamEndMsg` の優先度を `quitOnChildExit > autoRestart > quit` に簡約 |
| `internal/complete/complete.go` | `test` のフラグ候補に `--auto-restart` / `-R` を追加 |
| `internal/ui/chat_test.go` (新規 or 既存) | auto-restart 初期化・子終了時の restart/quit 分岐をユニットテスト (bubbletea Model を直接駆動) |
| `fixtures/run.sh` | 非 TTY での `--interactive --auto-restart` (exit 0・1 回実行)、`--auto-restart` 単体 (exit 2) の smoke を追加 |
| `docs/tools/atcoder-test-usage.md` | 対話モード節に `--auto-restart` とキー操作を追記 |
| `docs/tools/atcoder-test-architecture.md` | chat TUI の restart 状態遷移の記述を更新 (awaitingRestart 廃止) |
| `docs/tools/todo.md` | 本項目を記載し本要件へ相互リンク |

### `internal/ui/chat.go` の状態の変化 (素描)

```go
// ChatHeader に追加。
type ChatHeader struct {
    Task        string
    Contest     string
    TimeLimitMs int
    Debug       bool
    AutoRestart bool // true なら起動時から sticky auto-restart (子終了のたびに再起動)
}

// chatModel から削除: awaitingRestart。
// initialChatModel: m.autoRestart = header.AutoRestart で初期化。
//
// streamEndMsg (子の stdout/stderr 両方が EOF) の分岐:
//   quitOnChildExit         → tea.Quit
//   autoRestart && spawn!=nil → m.restart()           (プロンプト無し)
//   spawn != nil            → tea.Quit                (旧: awaitingRestart プロンプト)
//   else                    → tea.Quit
```

- `Ctrl+D` / `Ctrl+C` の意味は据え置き (auto-restart 解除の graceful / 即中断)。
- ヒント `(auto-restart on — …)` は起動時に `autoRestart` が真なら 1 回出す (`autoHintShown` を流用)。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `--auto-restart` を `--interactive` 無しで指定 | "--auto-restart requires --interactive" | 2 |
| 未知フラグ | flag パッケージが usage 表示 | 2 |
| 対話フラグ × サンプル専用フラグ | 既存の併用エラー | 2 |
| 正常 (対話 + auto-restart) | chat TUI で連続実行、最後のセッション結果で終了 | 子の結果に従う (0/1) |

## 非機能要件

- **既存非破壊 (フラグ無し時の chat TUI 以外)**: サンプルモード・ad-hoc ファイル・非 TTY passthrough の挙動は不変。`Ctrl+D`/`Ctrl+C`/履歴/`Enter` 送信などの操作も不変。
- **意図的な非互換**: 終了後プロンプト (`press [r]`) の廃止は本要件の目的。旧挙動には戻さない。
- **決定的・テスト可能**: chat Model を直接駆動し、`AutoRestart` 初期値と `streamEndMsg` 分岐をユニットテストで固定する。
- **exit code 規約**: フラグ誤り = 2、実行時失敗 = 1、成功 = 0。

## 将来の拡張ポイント

- **`config.toml` 既定値** (`test.auto_restart`): 毎回フラグを打たずに既定 ON にできる。`layout` と同じ flag > env > config > 既定の解決。
- **回数上限** `--auto-restart=N`: N 回で自動停止 (現状は無制限の sticky)。
- **手動 restart キー**: auto-restart OFF でもセッション中に明示キーで再起動 (今回は廃止方針なので対象外)。

## 用語

- **auto-restart**: 子プロセスが終了するたびに同じ解答を再起動して新セッションを始める sticky モード。
- **セッション**: 1 回の子プロセス起動〜終了。`--auto-restart` 中は番号付きで区切る。
- **awaitingRestart (廃止)**: 旧来の「子終了後に `r` 待ち」状態。本要件で削除。

## 関連ドキュメント

- `docs/tools/requirements/015-fold-submit-into-test.md` (`test` のモード体系)
- `docs/tools/atcoder-test-usage.md` (対話モードの利用手引)
- `docs/tools/atcoder-test-architecture.md` (chat TUI 内部設計)
