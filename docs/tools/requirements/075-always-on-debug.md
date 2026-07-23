# Debug 常時 on 化 要件定義

## 概要

`atcoder test` / `atcoder start` / chat TUI の Debug モードを常に有効にし、`-d` / `--debug` と chat の `:debug` / `:set debug` / `:set nodebug` による on/off 操作を撤去する。

## 背景・目的

これまで `[DEBUG]` 行の除外と `DEBUG=1` 環境変数は opt-in だったため、デバッグ print を残した状態で `-d` を付け忘れるとサンプル判定が WA になり、chat でも表示切替を都度意識する必要があった。練習用途では `[DEBUG]` 規約は常に有効なほうが自然で、切替 UI は摩擦になっていた。

## スコープ

| 区分 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| CLI | `test` / `start` の `-d` / `--debug` を削除し、指定時は標準 flag の未知フラグとして exit 2 | 別名復活なし |
| 実行 | sample / ad-hoc / interactive / start watch のすべてで `DEBUG=1` を渡し、stdout の `[DEBUG]` 行を比較対象から除外 | stderr の debug 行除外は対象外 (提出前検出は従来どおり見る) |
| chat | `:debug` / `:set debug` / `:set nodebug` と補完候補を削除し、表示は常時 Debug on | 表示だけを隠すフィルタは対象外 |
| pp | `--pp` / `:pp` は Debug 常時 on の表示修飾として残す。`--pp` 単体でも note は出さない | watch 詳細への pp 波及 |
| submit | `--keep-debug` は提出用コピー加工の制御なので残す | なし |

## CLI 仕様

```sh
atcoder test <contest> --task <task> [--pp] ...
atcoder start <contest> --task <task> ...
```

| フラグ / コマンド | 変更 |
|---|---|
| `-d` / `--debug` | `test` / `start` から削除。指定時は flag parse error で exit 2 |
| `--pp` | Debug 行が常に存在しうる前提の表示修飾。`-d` 不在 note は出さない |
| `:debug` | chat command から削除。未知コマンド (`E492`) 扱い |
| `:set debug` / `:set nodebug` | `:set` 候補から削除。指定時は `E518` |
| `--keep-debug` | `--submit` のコピー加工制御として維持 |

## 動作仕様

| 状況 | 動作 |
|---|---|
| sample 判定 | 子に `DEBUG=1` を渡し、stdout の `[DEBUG]` 行を `CaseResult.Debug` に分離して比較から除外 |
| ad-hoc `--out` | `testexec.Judge(..., debug=true, ...)` 相当で比較 |
| ad-hoc 表示のみ | stdout の `[DEBUG]` 行を `debug:` へ分離 |
| interactive chat | `ChatHeader.Debug=true` を強制し、将来の呼び出し漏れでも `[DEBUG]` 行を debug 表示にする |
| start watch | 初回 / 保存検知 / ナビ移動後のすべてで Debug=true。watch タイトルに `[debug]` を表示 |
| `--pp` | `debug:` 表示時に valid JSON payload のみ整形。判定・JSON 出力・exit code は不変 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/test.go` | `-d` / `--debug` フラグ削除、`testexec.Options.Debug=true`、ad-hoc への debug 引数削除、`--pp` note 削除 |
| `cmd/atcoder/adhoc.go` / `internal/runexec/runexec.go` | ad-hoc / interactive で Debug=true を強制し `DEBUG=1` を常時渡す |
| `cmd/atcoder/start.go` | `-d` / `--debug` フラグと config 伝播削除、spawn / watch / header を Debug=true 固定 |
| `internal/ui/chat.go` / `chat_casebuilder.go` | chat header を Debug=true 強制、`:debug` 系コマンドと helper 削除、`:pp` の off 時補足削除 |
| `internal/ui/startsplit.go` | `DebugMsg` と live toggle 再判定経路を削除し Debug=true 固定 |
| `internal/ui/command_complete.go` / `internal/complete/complete.go` | chat 補完と shell 補完から debug toggle / flag を削除 |
| `fixtures/run.sh` / docs | 常時 Debug の smoke と説明へ更新 |

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `atcoder test ... -d` / `--debug` | unknown flag。exit 2 |
| `atcoder start ... -d` / `--debug` | unknown flag。exit 2 |
| chat `:debug` | unknown command (`E492`)。chat 継続 |
| chat `:set debug` / `:set nodebug` | unknown option (`E518`)。chat 継続 |

## 非機能要件

- 解答ファイル本体は不変。変更は実行時の環境変数・判定・表示のみ。
- 提出前チェックの `DebugSeen` は従来どおり生 stdout / stderr を見る。Debug 常時 on でも、提出物に `[DEBUG]` が残る兆候は確認対象にする。
- 既存の `[DEBUG]` 規約を変えない。行頭が `[DEBUG]` の stdout 行のみ比較から除外する。

## 関連ドキュメント

- [`047-debug-json-pretty-print.md`](047-debug-json-pretty-print.md) — `--pp` / `:pp`
- [`044-submit-precheck-confirm.md`](044-submit-precheck-confirm.md) — 提出前 Debug 検出
- [`usage/test.md`](../usage/test.md)
- [`usage/start.md`](../usage/start.md)
