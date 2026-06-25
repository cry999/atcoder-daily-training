# 提出前チェックをコメントアウト後ソースで実行 要件定義

## 概要

`atcoder test --submit` (CLI) と chat の `Ctrl+S` の提出前チェック ([044](./044-submit-precheck-confirm.md)) で、サンプル判定を **解答ファイル本体ではなく「提出される中身」(= `[DEBUG]` print をコメントアウトしたソース) に対して実行する**。これにより、提出ゲートの 3 条件 (実行可否・全通過・`[DEBUG]` 検出) を **実際にクリップボードへ載る中身そのもの** で評価する。`[DEBUG]` の有無確認は「コメントアウトした後の実行結果」で行うことになり、デバッグ中に毎回 DEBUG 検出/サンプル不通過が出てしまう現状のノイズを解消しつつ、コメントアウトの取りこぼし (regex で拾えなかった `[DEBUG]` 出力) だけを確認対象として残す。解答ファイル本体は従来どおり一切書き換えない。

## 背景・目的

- 現状 ([044](./044-submit-precheck-confirm.md)) のゲートは **解答ファイル本体を無加工で実行** し、その生 stdout/stderr から `[DEBUG]` の有無 (`DebugSeen`) を見ている。一方、`[DEBUG]` print のコメントアウト ([043](./043-submit-comment-out-debug.md)) は **クリップボードへ載せる段階の文字列変換** で、実行とは別経路。
- このため、ローカルで無条件 `print("[DEBUG] ...")` を撒いてデバッグしている最中に `Ctrl+S` を押すと、
  - 生実行の stdout に `[DEBUG]` 行が混ざり、`-d` なしのゲート判定では **期待出力と一致せず FAIL** になる (「サンプルが全通過していません」)、
  - かつ `DebugSeen=true` で「実行中に `[DEBUG]` 出力が検出されました」も出る。
  毎回この 2 つが出るため、ゲートが「常に何か言う」状態になり、本当に見たい「**コメントアウト後も残るデバッグ出力**」のシグナルが埋もれる。
- そこで、ゲートの実行対象を **提出される中身 (コメントアウト後ソース)** に切り替える。コメントアウトで消える無条件 `[DEBUG]` print は実行されなくなり、stdout がクリーンになって PASS/FAIL が意味を持ち、`DebugSeen` は「コメントアウトをすり抜けて実行時に残った `[DEBUG]` 出力」だけを拾う安全網になる。提出物そのものを判定するので、ゲートの全条件が「実際に提出される状態」を反映する。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象経路 | `test --submit` (CLI) と chat `Ctrl+S` の両方 | — |
| 実行対象の変更 | ゲートのサンプル判定を **コメントアウト後ソース** (= 提出される中身) で実行 | 他言語 Runner のコメントアウト規則に追従 |
| 適用範囲 | ゲート全体 (PASS/FAIL 判定・`DebugSeen` 検出の両方) を同一実行で判定 (単一実行) | — |
| `--keep-debug` 時 | コメントアウトしないので **解答そのまま (=提出される中身) を実行**。挙動は実質従来どおり | — |
| 解答ファイル | **触れない** (読み取りのみ。実行は一時ファイル経由) | — |
| コメントアウト規則 | [043](./043-submit-comment-out-debug.md) の `debugstrip.CommentOut` をそのまま流用 | — |

### 境界 (非対象)

- **コメントアウト規則そのものは変えない**。検出・安全スキップ・冪等性は [043](./043-submit-comment-out-debug.md) のまま。本件は「その出力を実行対象にする」だけ。
- **確認 UI・exit code 規約・理由文言は [044](./044-submit-precheck-confirm.md) のまま**。変えるのは「何を実行して `DebugSeen`/PASS/FAIL を得るか」。
- **実提出 (POST) はしない** ([ADR 0006](../decisions/0006-fold-submit-into-test.md))。確認後の動作は従来どおりコピー + 提出ページ起動まで。
- 通常の `atcoder test` (`--submit` でない) / `--json` / ad-hoc・対話モードの実行対象は **不変** (解答ファイル本体をそのまま実行)。コメントアウト後実行は提出ゲート専用。

## CLI 仕様

フラグの追加・削除はない。`--submit` / `Ctrl+S` の **ゲート実行対象** を変える。

```
atcoder test <contest> --task <task> [... 既存フラグ ...] --submit [--no-open] [--keep-debug]
```

### 処理ステップ (`test --submit` / chat `Ctrl+S` 共通)

1. 解答ファイルを **読み取り** (本体は書き換えない)、`--keep-debug` でなければ `debugstrip.CommentOut` でコメントアウトした「提出される中身」を作る (コメントアウト件数も得る)。chat は常にコメントアウト ([043](./043-submit-comment-out-debug.md))。
2. その「提出される中身」を **一時ファイル** (解答と同じ拡張子、例 `.py`) に書き出す。
3. 一時ファイルを実行対象として通常どおりサンプル判定 (`testexec.Run`) を回す。各ケースの生 stdout/stderr から `DebugSeen` を集約する ([044](./044-submit-precheck-confirm.md) と同じ仕組み)。
4. 一時ファイルを削除する (実行が終われば不要)。
5. 実行結果 (code / runErr / DebugSeen) からゲート理由を組み立てる (`submitGateReasons`、[044](./044-submit-precheck-confirm.md) のまま)。
6. 理由が無ければクリーン → 従来どおり提出準備 (**手順 1 で作った中身をそのままクリップボードへ**、提出ページ起動)。理由があれば理由を出して確認し、`y` で提出準備、他で中止 ([044](./044-submit-precheck-confirm.md) のまま)。

> 手順 1 で作った「提出される中身」を、ゲート実行とクリップボードコピーの **両方で共有** する。解答の二度読み・二度コメントアウトをせず、判定した中身と提出する中身が必ず一致する。

### 出力イメージ

デバッグ中 (無条件 `print("[DEBUG]…")` あり) に `Ctrl+S` / `--submit`:

```
# 従来: コメントアウト前の生実行 → [DEBUG] が stdout を汚し FAIL + DEBUG 検出が毎回出る
提出前チェックで問題が見つかりました:
  - サンプルが全通過していません
  - 実行中に [DEBUG] 出力が検出されました

# 本件: コメントアウト後ソースを実行 → [DEBUG] print は実行されず stdout クリーン
クリップボードにコピーしました: exercise/2026/06/25/abc457_d.py (DEBUG 出力 2 行をコメントアウト)
提出ページを開きました: https://atcoder.jp/contests/abc457/submit?taskScreenName=abc457_d
```

コメントアウトをすり抜けた `[DEBUG]` 出力が残るとき (例: `sys.stderr.write("[DEBUG]…")` や複文・動的生成):

```
提出前チェックで問題が見つかりました:
  - 実行中に [DEBUG] 出力が検出されました
このまま提出準備を続けますか? [y/N]:
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| 無条件 `print("[DEBUG]…")` を撒いてデバッグ中 → `--submit`/`Ctrl+S` | コメントアウト後ソースを実行 → 出力クリーン → クリーン判定で確認なし提出準備 |
| コメントアウトで消えない `[DEBUG]` 出力が実行時に残る | `DebugSeen=true` → 理由を出して確認 |
| コメントアウト後ソースがサンプル不通過 (本物の WA/TLE/RE) | 「サンプルが全通過していません」で確認 |
| `--keep-debug` | コメントアウトせず提出される中身 (=解答そのまま) を実行。`[DEBUG]` 出力があれば検出・確認 (実質従来どおり) |
| コメントアウト対象 0 行 | 解答と同内容を一時ファイルで実行 (挙動は無加工実行と等価) |
| 解答ファイル本体 | **不変** (読み取りのみ。実行は一時ファイル経由) |
| 通常の `test` / `--json` / ad-hoc | **不変** (解答ファイル本体を実行) |

### `DebugSeen` の意味の変化

- [044](./044-submit-precheck-confirm.md): 「解答ファイル本体を実行したときの生 stdout/stderr に `[DEBUG]` があったか」。
- 本件: 「**コメントアウト後ソース** を実行したときの生 stdout/stderr に `[DEBUG]` があったか」。
  - 無条件 `print("[DEBUG]…")` はコメントアウトされ実行されないので検出されない。
  - `debugstrip` の regex で拾えない経路 (stderr 書き込み・複文・動的生成・f-string 以外の組み立て等) で出た `[DEBUG]` は残るので検出される = **コメントアウト漏れの安全網**。
- 理由文言 (`実行中に [DEBUG] 出力が検出されました`) は据え置き (コメントアウト後の実行でも「実行中に検出された」は正確)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/testexec/test.go` | `Options` に実行対象パスの上書き口 `SolutionPathOverride string` を追加。非空ならその値を実行対象 (`solutionPath`) として使い、`os.Stat` 存在チェック・`ExecutorFor` の拡張子判定もそれに従う。空 (既定) なら従来どおり `Layout.SolutionPath` から解決 (既存挙動不変) |
| `cmd/atcoder/submitprep.go` | 「提出される中身」を 1 度だけ構築する純粋寄りヘルパー `buildSubmitSource` (解答読込 + `keepDebug` に応じた `CommentOut`)、一時ファイル書き出しヘルパー `writeTempSource` を追加。`runSubmitPrep` を「中身構築 → 一時ファイル → `SolutionPathOverride` 付き `testexec.Run` → ゲート → 確認 → **同じ中身を**クリップボードへ」に組み替える。`submitPrepCore`/`prepareSubmission` は構築済み中身を受け取る形へ整理 (解答の二度読みを除去) |
| `cmd/atcoder/adhoc.go` | `chatSubmitCheckFunc` を、コメントアウト後ソースを一時ファイルに書いて `SolutionPathOverride` 付きで実行する形へ変更。`chatSubmitFunc` (実コピー) と同じ「提出される中身」を使う |
| `internal/testexec/test_test.go` (新規 or 追記) | `SolutionPathOverride` 指定時にその実行対象が使われ、空なら Layout 解決が使われることのユニットテスト |
| `fixtures/fixture_<name>.py` + `fixtures/cache/.../` | コメントアウト後に DEBUG が消えて PASS する fixture / コメントアウトをすり抜けて DEBUG が残る fixture (詳細はテスト戦略) |
| `fixtures/run.sh` | 「無条件 `[DEBUG]` print 入り解答を `--submit` (非 TTY) → コメントアウト後実行でクリーン → 提出準備に進む (exit 0)」を固定する run_case を追加 |
| `fixtures/README.md` / `docs/tools/atcoder-test-testing.md` | fixture 一覧に追記 |
| `docs/tools/atcoder-test-usage.md` | `--submit` 節に「提出前チェックはコメントアウト後の中身で判定する」を追記 |
| `docs/tools/atcoder-test-architecture.md` | 提出ゲートの内部設計に「提出される中身を一時ファイルで実行」段を追記 |
| `docs/tools/todo.md` | 本要件の項目を追加し相互リンク |

### 素描

```go
// internal/testexec/test.go
type Options struct {
    // ...既存...
    // SolutionPathOverride は実行対象の解答パスを上書きする (要件 049)。非空なら
    // Layout.SolutionPath の解決結果ではなくこのパスを実行する。提出ゲートが
    // 「コメントアウト後ソースを書き出した一時ファイル」を走らせるために使う。
    SolutionPathOverride string
}

func Run(opts Options) (int, error) {
    // ...
    solutionPath, err := lay.SolutionPath(opts.Contest, opts.Task)
    if err != nil { return 1, err }
    if opts.SolutionPathOverride != "" {
        solutionPath = opts.SolutionPathOverride
    }
    // os.Stat / ExecutorFor(solutionPath) は以降そのまま
}

// cmd/atcoder/submitprep.go
// submitSource は提出ゲートと提出準備で共有する「提出される中身」。
type submitSource struct {
    Path           string // 原本の解答パス (表示・拡張子判定用)
    Body           string // 提出される中身 (keepDebug=false ならコメントアウト済み)
    DebugCommented int    // コメントアウトした [DEBUG] 行数
}

func buildSubmitSource(contest, task string, lay layout.Layout, keepDebug bool) (submitSource, error)

// writeTempSource は body を Path と同じ拡張子の一時ファイルに書き、パスと後始末を返す。
func writeTempSource(origPath, body string) (tmpPath string, cleanup func(), err error)
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 解答パス解決失敗 (task/layout 誤り) | エラー表示 | 2 |
| 解答ファイル読込失敗 | エラー表示 | 1 |
| 一時ファイル書き出し失敗 | エラー表示 | 1 |
| ゲート実行エラー + 確認で中止 | 理由表示 → 中止 | 1 |
| 全通過せず / DEBUG 検出 + 確認で中止 | 理由表示 → 中止 | 1 |
| クリーン or 確認 `y` → 提出準備成功 | 既存どおり表示 | 0 |
| 非 TTY (stdin) + リスクあり | 確認を出さず中止 | 1 |

- 一時ファイルは実行後 (成功・失敗いずれでも) 必ず削除する (`defer cleanup()`)。書き出し失敗時は解答本体に影響しない。
- `buildSubmitSource` の `CommentOut` は失敗経路を持たない ([043](./043-submit-comment-out-debug.md))。

## 非機能要件

- **解答ファイル非破壊**: 解答は読み取りのみ。実行はコメントアウト後の中身を書いた一時ファイルに対して行い、終了後に削除する。本体への書き戻しは一切しない。
- **判定と提出の一致**: ゲートで実行する中身とクリップボードへ載せる中身は **同一の文字列** (1 度の構築を共有)。「判定は通ったが別物を提出する」ズレを構造的に排除する。
- **既存非破壊**: `SolutionPathOverride` 未指定時の `testexec.Run` は従来とバイト等価。通常の `test` / `--json` / ad-hoc は不変。`--keep-debug` 時の提出物・検出結果も実質従来どおり。
- **ハングしない / TUI を汚さない**: 確認の非 TTY 自動「いいえ」・chat の `SummaryReporter` 実行は [044](./044-submit-precheck-confirm.md) のまま。
- **前方互換**: `SolutionPathOverride` は Options への追加フィールド。将来の本番モード判定 (`contest.toml`) や他言語コメントアウトからも、同じ「提出される中身を実行する」経路を再利用できる。

## 将来の拡張ポイント

- 他言語 Runner 追加時、`debugstrip` の言語別規則に追従して「提出される中身」を構築 (本経路はそのまま使える)。
- 一時ファイルではなく実行 API へソースバイト列を直接渡す経路 (Executor インターフェース拡張)。当面は blast radius の小さい一時ファイル方式を採る。
- コメントアウト後ソースに対する静的検査 (残存 `[DEBUG]` の指摘) をゲート理由に追加。

## 用語

- **提出される中身 (submitSource.Body)**: 解答ファイルを読み、`--keep-debug` でなければ `[DEBUG]` print をコメントアウトした文字列。クリップボードに載るものと同一。
- **提出ゲート**: 提出準備に進む前に評価する 3 条件 (実行可否・全通過・`DebugSeen`) の判定 ([044](./044-submit-precheck-confirm.md))。
- **`SolutionPathOverride`**: `testexec.Run` の実行対象を Layout 解決ではなく明示パスにする上書き口。提出ゲートが一時ファイルを走らせるのに使う。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- [044-submit-precheck-confirm.md](./044-submit-precheck-confirm.md) (提出前チェックと確認。本件はそのゲート実行対象を「提出される中身」に変える)
- [043-submit-comment-out-debug.md](./043-submit-comment-out-debug.md) (`[DEBUG]` print のコメントアウト。本件はその出力を実行対象にする)
- [026-chat-submit.md](./026-chat-submit.md) (chat `Ctrl+S` の提出準備)
- [001-exercise-test.md](./001-exercise-test.md) (`-d`/`--debug` と `[DEBUG]` 規約 / `splitDebug`)
- [015-fold-submit-into-test.md](./015-fold-submit-into-test.md) / [ADR 0006](../decisions/0006-fold-submit-into-test.md) (`--submit` を test に畳んだ前例)
- `docs/tools/atcoder-test-usage.md` (test 利用手引) / `docs/tools/atcoder-test-architecture.md` (内部設計)
