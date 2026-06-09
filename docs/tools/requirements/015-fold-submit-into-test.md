# `submit` を `test --submit` に畳む 要件定義

## 概要

`atcoder submit` は現状「サンプル全通過を確認 → 解答をクリップボードへコピー → 提出ページをブラウザで開く」という薄い前準備でしかなく、独立コマンドとしての価値が薄い。これを **`atcoder test --submit` フラグに畳み**、`submit` サブコマンドを**削除**する。`--submit` は「サンプルが全通過したら、続けて提出準備 (コピー + ブラウザ起動) を行う」フラグとして振る舞う。

認証付きの実提出 (POST) は `internal/atcoder` のセッション基盤が整えば可能だが、**認証機能がまだ安定していない**ため今回は実装しない。実提出は auth 安定後に別途 (decisions に保留として記録)。

設計判断の記録は [ADR 0006](../decisions/0006-fold-submit-into-test.md)。

## 背景・目的

- `submit` は内部で `testexec.Run` を呼んでサンプル判定し、緑なら clipboard コピー + ブラウザ起動するだけ。実提出は認証回避のためブラウザに委ねている。
- やっていることは「test して、緑なら提出準備」なので、`test` のフラグ (`--watch` 等と同列のモード修飾) として表現するのが自然。直近の `run` 統合と同じ「コマンドを増やさず test に寄せる」方針に沿う。
- 認証 (`login`/`status`) は入ったが**まだ安定していない**ため、submit を「本物の提出」へ格上げする道 (ADR 0006 の案 A) は今回採らない。薄い前準備を test のフラグに整理するに留める。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| `atcoder submit` | **削除** (dispatch・usage・補完から除去) | — |
| 提出準備 | `atcoder test --submit` に移設 (コピー + ブラウザ起動) | 認証付き実提出 (POST)、`status` 連携 |
| `--no-open` | 維持 (`--submit` の修飾。コピーのみで URL 表示) | — |
| 実提出 (認証 POST) | **やらない** (auth 安定後に別案件) | ADR 0006 の案 A |
| `openBrowser` | 残す (`status --open` も使用) → 共有ファイルへ移設 | — |

## CLI 仕様

`test` に提出準備フラグを足す (サンプルモード専用)。

```
atcoder test <contest> --task <task> [... 既存フラグ ...] [--submit [--no-open]]
```

| フラグ | モード | 説明 |
|---|---|---|
| `--submit` | サンプル | サンプルが**全通過したら**、解答をクリップボードへコピーし提出ページをブラウザで開く |
| `--no-open` | サンプル | `--submit` 時にブラウザを開かず URL を表示するだけ |

- `--submit` は**サンプルモード専用**。ad-hoc フラグ (`--in`/`--out`/`--interactive`) との併用は exit 2 (既存の排他チェックに追加)。
- `--submit` と `--watch` の併用は exit 2 (watch は常駐ループで、一回限りの提出準備と意味が衝突する)。
- `--no-open` は `--submit` の修飾。単独指定は無害 (no-op)。

### 処理ステップ (`test --submit`)

1. 通常どおりサンプル判定を実行 (`testexec.Run`)。
2. **全通過 (exit 0) でなければ**、提出準備をせず test の結果コード (1 等) で終了。
3. 全通過なら: 解答ファイルを読みクリップボードへコピー → 提出 URL (`/contests/<contest>/submit?taskScreenName=<task_id>`) を組み立て → `--no-open` でなければブラウザで開く (best-effort)。
4. ブラウザ起動に失敗してもコピーは済んでいるので致命的扱いにせず、URL を表示して exit 0。

### 出力イメージ

```
$ atcoder test abc457 --task d --submit
abc457_d  contest=abc457  ...  tests=3
[01] PASS ...
Result: 3/3 PASS
クリップボードにコピーしました: exercise/2026/06/09/abc457_d.py
提出ページを開きました: https://atcoder.jp/contests/abc457/submit?taskScreenName=abc457_d
```

サンプルが落ちたときは従来の test と同じ出力 + exit 1 で、コピー/ブラウザはしない。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `test --task d --submit` (全 PASS) | test 出力 + コピー + ブラウザ起動、exit 0 |
| `test --task d --submit` (FAIL/RE/TLE 含む) | test 出力のみ、コピー/起動せず exit 1 |
| `test --task d --submit --no-open` | コピー + URL 表示 (開かない)、exit 0 |
| `test --task d --submit --in foo` | exit 2 (ad-hoc と併用不可) |
| `test --task d --submit -w` | exit 2 (watch と併用不可) |
| `atcoder submit ...` | 未知サブコマンド → usage → exit 2 (submit 削除) |

- **既存非破壊 (test 本体)**: `--submit` 無しの `test` の挙動は不変。`testexec` は無改修。
- **後方互換の破壊点**: `atcoder submit <c> --task d [--no-open]` → `atcoder test <c> --task d --submit [--no-open]` へ移行。
- 解答ファイルには触れない (読み取りのみ。`--refresh` はキャッシュのみ)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/test.go` | `--submit` / `--no-open` フラグ追加。サンプル全通過後に提出準備を呼ぶ。排他チェックに `--submit`/`--no-open` を追加、`--submit`+`--watch` を exit 2 |
| 新規 `cmd/atcoder/submitprep.go` | 提出準備ヘルパ (`prepareSubmission`: clipboard コピー + URL 組み立て + ブラウザ起動)。submit.go から移設 |
| 新規 `cmd/atcoder/browser.go` | `openBrowser` を移設 (submit.go から。`status --open` も使う共有関数) |
| `cmd/atcoder/submit.go` | **削除** |
| `cmd/atcoder/main.go` | `case "submit"` と usage 行を削除。`test` の usage に `--submit` を追記 |
| `internal/complete/complete.go` | `subcommandCands`/`subFlags`/`takesContest`/位置引数判定から `submit` を除去。`test` に `--submit`/`--no-open` を追加 |
| `internal/complete/complete_test.go` | `submit` を含む期待値を更新 |
| `fixtures/run.sh` | `submit` smoke を `test --submit --no-open` に変換 (pass=0 / fail=1)。`submit` 削除 (exit 2) を追加 |
| `docs/tools/atcoder-test-usage.md` | `--submit`/`--no-open` の節を追記 |
| `docs/tools/atcoder-completion-usage.md` | サブコマンド一覧から `submit` (および既に削除済みの `run`) を除去 |
| 新規 `docs/tools/decisions/0006-fold-submit-into-test.md` | 決定記録 (ADR) |

### `prepareSubmission` の素描

```go
// prepareSubmission は test --submit のサンプル全通過後に呼ばれる。解答をコピーし
// 提出ページを開く (実提出はしない。認証が安定するまでブラウザに委ねる)。
func prepareSubmission(contest, task string, lay layout.Layout, noOpen bool) (int, error)
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `--submit` + ad-hoc フラグ | "…cannot be combined with --in/--out/--interactive" | 2 |
| `--submit` + `--watch` | "--submit cannot be combined with --watch" | 2 |
| サンプル未通過 | test の結果のまま (コピー/起動せず) | 1 |
| クリップボードコピー失敗 | エラー表示 | 1 |
| ブラウザ起動失敗 | warning + URL 表示 (致命的でない) | 0 |
| `atcoder submit ...` | usage | 2 |
| 正常 (全 PASS + 準備完了) | — | 0 |

## 非機能要件

- **test 本体は既存非破壊**: `--submit` 未指定なら従来どおり。`testexec` 無改修。
- **`openBrowser` を壊さない**: `status --open` が依存するため共有関数として残す。
- **認証に踏み込まない**: 実提出 (POST) はしない。認証安定後に ADR 0006 案 A として再検討。
- **fixtures で固定**: `--submit` の pass/fail・排他・`submit` 削除を smoke で assert。

## 将来の拡張ポイント

- **認証付き実提出**: auth (`internal/atcoder`) 安定後、`--submit` をブラウザ起動から実 POST へ。`status` で verdict を追う導線 (ADR 0006 案 A)。
- ad-hoc モードでの提出準備 (現状はサンプルモード専用)。

## 用語

- **提出準備**: サンプル全通過後の「クリップボードコピー + 提出ページ起動」。実提出 (POST) は含まない。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- [ADR 0006](../decisions/0006-fold-submit-into-test.md) (本決定)
- [013-unify-test-run.md](./013-unify-test-run.md) / [ADR 0005](../decisions/0005-unify-test-run-into-test.md) (run を test に畳んだ前例)
- `docs/tools/atcoder-test-usage.md` (統一後の test 利用手引)
- `docs/tools/requirements/009-atcoder-status.md` (認証・status。実提出の将来連携先)
