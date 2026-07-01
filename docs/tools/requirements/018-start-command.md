# `atcoder start` 着手コマンド 要件定義

## 概要

問題に取り掛かるときの **「ディレクトリ用意 → 解答ファイル作成 → watch テスト起動」** を 1 コマンドにまとめる。`atcoder start <contest> --task <task>` で、レイアウトに応じた解答ファイルを (無ければ) 作り、そのまま `test --watch` の編集ループに入る。`--until-pass` を付けると **サンプルが全通過した時点で watch を終了**して着手〜完了を 1 コマンドで締められる。

既存の部品 (`layout` の解答パス解決・`new abc` のスケルトン生成・`test --watch` の監視ループ) を束ねる薄い orchestration で、新しい実行・判定ロジックは増やさない。

## 背景・目的

- 1 問始めるたびに「`exercise/YYYY/MM/DD/` (or `abc/<num>/`) を作る → `<task>.py` を作る → `atcoder test <contest> --task <task> --watch` を叩く」を手作業で繰り返している。`start` 1 つで済ませたい。
- watch は解答ファイルが存在しないと「解答ファイルが見つかりません」で動かない。`start` が**ファイル作成と watch 起動をまとめる**ことで、空ファイルを手で用意する手間を消す。
- 「テストが通ったら自動で抜けたい」という締めの動作 (`--until-pass`) も、ここに乗せると着手〜完了が 1 コマンドで完結する。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | 新サブコマンド `atcoder start <contest> --task <task>` | — |
| ディレクトリ作成 | 解答パスの親ディレクトリを `MkdirAll` | — |
| 解答ファイル生成 | 無ければ**空ファイル**を作成 (既存は温存) | テンプレート流し込み (ロードマップ H) |
| watch 起動 | 既存 `test --watch` の監視ループを再利用 | — |
| 終了条件 | 既定は `Ctrl+C` (test --watch と同じ)。`--until-pass` で全通過時に終了 | 提出準備まで連結 (`--submit` 連携) |
| レイアウト | `--layout` / `ATCODER_LAYOUT` / config / auto (既存 `resolveLayout`) | — |
| 言語 | Python (`.py`、既存 runner のまま) | 他言語 runner |

### 境界 (他コマンドとの分担)

- 解答パス解決は **`internal/layout`** (002 / 017)。ディレクトリ作成・空ファイル生成は `new abc` のスケルトン生成 (003) と同じ方針 (既存ファイルは上書きしない)。
- サンプル fetch・判定・watch ループは **`test`** (001 / 004)。`start` は最初の watch 実行に委ね、独自 fetch はしない。
- テンプレート (H) が入ったら、空ファイル生成箇所をテンプレート書き込みに差し替えられるようフックを 1 か所に保つ。

## CLI 仕様

```
atcoder start <contest> --task <task> [--until-pass] [--refresh] [--timeout <dur>] [--tolerance <eps>] [-d] [-s] [-j <n>] [--layout <auto|abc|exercise>]
```

| 引数 / フラグ | 説明 |
|---|---|
| `<contest>` | コンテスト ID (例 `abc457`)。`test` と同じ |
| `--task <task>` | タスク ID または短縮形 (`d` → `<contest>_d`)。必須 |
| `--until-pass` | **サンプルが全通過したら watch を終了** (exit 0)。既定は付けない (Ctrl+C で終了) |
| `--refresh` | 初回のみサンプルを再取得 (watch と同じセマンティクス) |
| `--timeout` / `--tolerance` / `-d` / `-s` / `-j` | `test` と同じ。各 watch 実行にそのまま渡す |
| `--layout <auto\|abc\|exercise>` | 解答ファイル配置。既定は `resolveLayout` (flag > env > config > auto) |

### 処理ステップ

1. `<contest>` と `--task` を解決 (短縮形展開)。`--task` 欠落は exit 2。
2. `resolveLayout` でレイアウトを決め、`lay.SolutionPath(contest, task)` で解答パスを得る。不正レイアウト/パスは exit 2。
3. **解答ファイルを用意**: 親ディレクトリを `MkdirAll`、ファイルが無ければ**空ファイル**を作成 (既存は温存。作成有無を 1 行表示)。
4. **watch ループ起動**: `test --watch` と同じ監視ループを回す (初回 `--refresh`、保存検知で再実行)。**TTY 必須** (非 TTY は exit 2)。
5. `--until-pass` 指定時は、各実行で**サンプル全通過 (testexec.Run が 0)** になったら改行して exit 0。未指定なら `Ctrl+C` まで継続 (exit 0)。

### 出力イメージ

```
$ atcoder start abc457 --task d
created: abc/457/d.py
# → 画面がクリアされ test --watch の編集ループに入る
#   (保存するたび再実行。--until-pass なら全 PASS で自動終了)
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| 解答ファイルが無い | 親 dir を作成し空ファイルを生成 (`created: <path>`) |
| 解答ファイルが既にある | 上書きせず温存 (`solution: <path> (exists)`)。提出コードを壊さない |
| 非 TTY (パイプ/リダイレクト) | watch と同じく exit 2 (画面クリア前提)。**ただしファイル作成は先に済ませる** |
| `--until-pass` 全通過 | watch を抜けて exit 0 |
| `--until-pass` 未指定 | `Ctrl+C` まで継続 (FAIL/RE/TLE でも止まらない)。Ctrl+C = exit 0 |
| `--refresh` | 初回のみ再 fetch (毎保存での再取得を避ける) |

- **既存非破壊**: `test` / `new` の挙動は不変。`start` は両者の薄い orchestration。`runTestWatch` に `untilPass` 引数を足すが、`test --watch` は `false` 固定で従来どおり。
- **解答ファイル安全**: 既存ファイルは絶対に上書きしない (`--refresh` はキャッシュのみ)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| 新規 `cmd/atcoder/start.go` | `cmdStart(args) (int, error)`。引数/レイアウト解決・スケルトン生成・watch 起動 |
| `cmd/atcoder/test.go` | `runTestWatch` に `untilPass bool` を追加し、全通過 (code==0) で終了する分岐。`cmdTest` は `false` で呼ぶ。skeleton 生成ヘルパ `ensureSolutionFile` を切り出し (start と共有) |
| `cmd/atcoder/main.go` | `case "start"` 追加、`builtins` と `usage()` を更新 |
| `internal/complete/complete.go` | `subcommandCands` に `start`、`subFlags["start"]`、`takesContest`・位置引数判定に `start` を追加 |
| `internal/complete/complete_test.go` | start の期待値を追加 |
| `fixtures/run.sh` | start のスケルトン生成 + 非 TTY 拒否 (exit 2)・`--task` 欠落 (exit 2) の smoke |
| `docs/tools/usage/start.md` | 利用手引 (新規) |
| `docs/tools/todo.md` | ロードマップ P に記載 |

### ヘルパの素描

```go
// ensureSolutionFile は lay/contest/task の解答パスを返し、無ければ親 dir を作って
// 空ファイルを生成する (既存は温存)。created はこの呼び出しで作ったかどうか。
func ensureSolutionFile(lay layout.Layout, contest, task string) (path string, created bool, err error)

// runTestWatch(..., untilPass bool): untilPass なら testexec.Run が 0 を返した回に exit 0。
func runTestWatch(contest, task string, lay layout.Layout, refresh bool, buildOpts func(bool) testexec.Options, untilPass bool) (int, error)
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `<contest>` 欠落 | "contest is required" | 2 |
| `--task` 欠落 | "--task is required" | 2 |
| 不明フラグ / 不正レイアウト | usage / "unknown layout" | 2 |
| 非 TTY で watch 起動 | "--watch requires a terminal" 相当 | 2 |
| ディレクトリ作成 / ファイル生成失敗 (権限等) | エラー表示 | 1 |
| 解答実行の失敗 (fetch 失敗等) | watch ループ内で表示し継続 (ループの exit は Ctrl+C/until-pass 依存) | 0/1 |

## 非機能要件

- **薄い orchestration**: 新しい実行・判定・fetch ロジックを増やさない。既存 `layout` / `testexec` / `watch` / `ui` を束ねるだけ。
- **既存非破壊・前方互換**: `runTestWatch` の引数追加は内部的で、`test --watch` の挙動は不変。
- **解答ファイルを壊さない**: 既存ファイルは温存。
- **fixtures で固定**: スケルトン生成・非 TTY 拒否・引数誤りを smoke で assert (`--until-pass` の全通過終了は TTY 必須のため run.sh では扱わず、手動確認)。

## 将来の拡張ポイント

- **テンプレート流し込み (H)**: 空ファイル生成をテンプレート書き込みに差し替え。
- **`--submit` 連携**: `--until-pass` 後にそのまま提出準備へ。
- **ABC 一括 start**: `new abc` と連携して複数タスクを一気に start。

## 用語

- **スケルトン**: 解答ファイルの初期状態。本機能では空 `.py` (H 実装後はテンプレート入り)。
- **着手 (start)**: ディレクトリ作成 → 解答ファイル生成 → watch 起動の一連。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- `docs/tools/requirements/001-exercise-test.md` (test・watch の基盤)
- `docs/tools/requirements/004-exercise-test-watch.md` (watch モード)
- `docs/tools/requirements/002-exercise-abc-layout.md` / `017-config-layout-default.md` (レイアウト解決)
- `docs/tools/requirements/003-exercise-abc-contest-meta.md` (スケルトン生成方針)
- `docs/tools/usage/start.md` (利用手引)
