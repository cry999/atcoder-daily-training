# 073: chat `:open` で現在の問題ページを開く

## 概要

`atcoder test --interactive` / `atcoder start` の chat command モードに `:open` を追加し、現在対応中の問題ページを OS 既定ブラウザで開けるようにする。

## 背景・目的

chat TUI では `Ctrl+E` で解答を開き、`Ctrl+S` で提出ページを開けるが、問題文へ戻る操作はブラウザ側で探す必要がある。考察中に問題文・制約・サンプルを見返す頻度が高いため、chat から現在ターゲットの問題ページを 1 コマンドで開けるようにして往復を軽くする。

## スコープ

| 区分 | 内容 |
|---|---|
| 当面のスコープ | command モード (`Esc` → `:open`) で現在の `contest_id` / `task_id` の問題ページをブラウザ起動する |
| 対象画面 | `test --interactive` の単体 chat、`start` 分割画面の chat |
| URL 解決 | `meta.toml.url` があればそれを優先し、無ければ `https://atcoder.jp/contests/<contest>/tasks/<task>` を使う |
| 将来の拡張余地 | 提出ページ・解説ページなどを開く `:open submit` / `:open editorial` |
| 対象外 | 問題文の fetch / TUI 内表示、ブラウザタブの再利用保証、実提出 |

## CLI / UI 仕様

| 操作 | 動作 |
|---|---|
| `Esc` → `:open` | 現在の問題ページを OS 既定ブラウザで開き、成功時は URL 付き info 行を表示する |
| `Tab` 補完 | `open` を command 名候補に含める |
| `:cheat` | `:open` の説明を表示する |

処理ステップ:

1. chat の `parseCommand` が `open` を `command{name:"open"}` に正規化する。
2. `internal/ui` は `ChatHeader.Open` フックを呼ぶ。
3. `cmd/atcoder` 側で `meta.toml.url` を読む。空または未取得なら標準問題 URL を組み立てる。
4. 既存の `openBrowser` で OS 既定ブラウザへ渡す。
5. 起動に失敗しても chat は継続し、手動で開ける URL を表示する。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `ChatHeader.Open` / `OpenFunc` / `OpenResult` を追加 |
| `internal/ui/chat_casebuilder.go` | `:open` の parse / exec / cheat 表示を追加 |
| `internal/ui/command_complete.go` | command 補完候補へ `open` を追加 |
| `cmd/atcoder/chatopen.go` | 問題 URL 解決とブラウザ起動フックを追加 |
| `cmd/atcoder/adhoc.go` / `cmd/atcoder/start.go` | chat header へ `Open` フックを注入 |
| `docs/tools/usage/test.md` | chat command 一覧へ `:open` を追記 |

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `ChatHeader.Open` 未注入 | info 行で「使えません」と表示し、chat 継続 |
| `meta.toml` 未取得 | 標準問題 URL に fallback |
| ブラウザ起動失敗 | err 行で理由と URL を表示し、chat 継続 |

## 非機能要件

- 解答ファイル・cache は変更しない。
- `:open` は child process の起動・停止・入力履歴・ライブ検証状態に影響しない。
- `:task` / `:contest` で retarget した後は、新しい `ChatHeader.Open` により移動先の問題ページを開く。

## 関連ドキュメント

- 利用手引: [`../usage/test.md`](../usage/test.md)
- `:meta` URL override: [`055-chat-meta-edit.md`](055-chat-meta-edit.md)
- task URL fallback: [`065-task-url-from-tasklist.md`](065-task-url-from-tasklist.md)
