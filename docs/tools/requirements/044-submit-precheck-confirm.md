# 提出前チェックと確認プロンプト 要件定義

## 概要

`atcoder test --submit` (および chat の `Ctrl+S`) で提出準備に進む前に、サンプル判定の結果と実行時の `[DEBUG]` 出力を点検し、**「サンプルが全通過していない」「実行できなかった」「実行中に `[DEBUG]` 出力が残っていた」のいずれかに当てはまるときは、自動で提出準備をせず「このまま提出準備しますか?」と確認する**。クリーン (全通過・実行成功・DEBUG 出力なし) なときだけ従来どおり確認なしで提出準備へ進む。デバッグ出力の消し忘れや、落ちているコードをうっかり提出ページへ載せる事故を、提出直前のゲートで止めるのが狙い。

## 背景・目的

- 既存の `--submit` は「サンプル全通過 (exit 0) なら提出準備、そうでなければ無条件に中止」という二択 ([015](./015-fold-submit-into-test.md))。中止された側は「直したつもりがまだ落ちている」ことに気づける一方、**「落ちているけど分かった上で提出したい」「ローカルのサンプルが古い等の理由で通過扱いにしたい」ときに一切前へ進めない**。
- [043](./043-submit-comment-out-debug.md) でクリップボードへ載せる解答から `[DEBUG]` print 行を機械的にコメントアウトするようにしたが、これは **ソース行のヒューリスティック** であり、`print(file=sys.stderr)` や複文・動的生成など regex で拾えない経路で `[DEBUG]` が実行時に漏れることはありうる。提出前に **実際の実行出力** を見て `[DEBUG]` の残存を検出できれば、コメントアウトの取りこぼしに対する安全網になる。
- そこで「ハード中止」を「**理由を見せて確認する**」に変える。クリーンなら従来どおり素通り、リスクがあるときだけ一拍置いて人に判断を委ねる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象経路 | `test --submit` (CLI) と chat `Ctrl+S` の両方 | — |
| チェック内容 | (1) サンプル判定の実行可否、(2) 全通過か、(3) 実行出力に `[DEBUG]` が出たか | 静的解析 (未コメントアウトの `[DEBUG]` print 残存)、TLE 余裕の警告 |
| DEBUG 検出 | サンプル実行時の **stdout / stderr** の各行が `[DEBUG]` で始まるか (既存 `DebugPrefix` 規約を流用) | 行頭以外・別マーカー |
| 確認 UI (CLI) | stdin から `y/N` を読む。非 TTY は自動で「いいえ」 (ハングさせない・安全側) | `--yes` で確認スキップ |
| 確認 UI (chat) | TUI 内に理由を出し、`y/N` を 1 打鍵で受ける確認モード | — |
| クリーン時 | 従来どおり確認なしで提出準備 (挙動不変) | — |

### 境界 (非対象)

- **実提出 (POST) はしない**。確認後の動作は従来どおり「クリップボードコピー + 提出ページ起動」まで ([ADR 0006](../decisions/0006-fold-submit-into-test.md))。
- DEBUG 検出は **実行出力ベース**。解答ソースの静的検査 (コメントアウトし損ねた `print("[DEBUG]")` がソースに残っているか) は今回は対象外で、[043](./043-submit-comment-out-debug.md) のコメントアウトに委ねる。
- `--keep-debug` ([043](./043-submit-comment-out-debug.md)) はクリップボードへ載せる加工の有無を制御するもので、本件のゲート判定とは独立。`--keep-debug` でも DEBUG 出力が検出されれば確認する。

## CLI 仕様

フラグの追加はない。`--submit` の **挙動** を変える。

```
atcoder test <contest> --task <task> [... 既存フラグ ...] --submit [--no-open] [--keep-debug]
```

### 処理ステップ (`test --submit`)

1. 通常どおりサンプル判定 (`testexec.Run`) を実行する。実行中、各ケースの **生の stdout / stderr** に `[DEBUG]` 始まりの行があったかを記録する (`DebugSeen`)。
2. 次の「提出前チェック」を評価し、引っかかった理由を集める:
   - サンプルを実行できなかった (`testexec.Run` がエラー: fetch 失敗・ケース無し・実行基盤エラー等) → 理由「テストを実行できませんでした: …」。
   - 実行できたが全通過でない (exit≠0: WA/TLE/RE) → 理由「サンプルが全通過していません」。
   - 実行出力に `[DEBUG]` が検出された → 理由「実行中に [DEBUG] 出力が検出されました」。
3. 理由が **無ければ** (クリーン): 従来どおり提出準備 (コピー + 提出ページ起動) を行い exit 0。
4. 理由が **あれば**: 理由を stderr に列挙し、`このまま提出準備を続けますか? [y/N]:` と尋ねる。
   - `y`/`yes` (大文字小文字不問) → 提出準備へ進む (exit 0、コピー失敗時のみ 1)。
   - それ以外 / 空 / EOF → 中止 (提出準備しない)。exit code は下記。
   - **stdin が端末でない** (パイプ・CI・fixtures 等) → 確認を出さず自動で「いいえ」とみなして中止 (ハングさせない)。

### 終了コード

| 状況 | exit |
|---|---|
| クリーン → 提出準備成功 | 0 |
| 確認に `y` → 提出準備成功 | 0 |
| 確認で中止 (テスト不通過のため) | 1 |
| 確認で中止 (実行エラーのため) | 1 |
| 確認で中止 (DEBUG 検出のみ、テストは通過) | 1 |
| 提出準備中のクリップボードコピー失敗 | 1 |

「提出準備に進めたか」を 0/1 で表す (0=提出準備した / 1=しなかった・失敗)。

### 出力イメージ

クリーン (従来どおり):

```
$ atcoder test abc457 --task d --submit
abc457_d  contest=abc457  ...  tests=3
[01] PASS ...
Result: 3/3 PASS
クリップボードにコピーしました: exercise/2026/06/24/abc457_d.py
提出ページを開きました: https://atcoder.jp/contests/abc457/submit?taskScreenName=abc457_d
```

リスクあり (確認):

```
$ atcoder test abc457 --task d --submit
abc457_d  contest=abc457  ...  tests=3
[01] PASS ...
[02] WA ...
Result: 2/3 PASS
提出前チェックで問題が見つかりました:
  - サンプルが全通過していません
このまま提出準備を続けますか? [y/N]: y
クリップボードにコピーしました: exercise/2026/06/24/abc457_d.py
提出ページを開きました: https://atcoder.jp/contests/abc457/submit?taskScreenName=abc457_d
```

`n` (または非 TTY):

```
このまま提出準備を続けますか? [y/N]: n
提出準備を中止しました。
```

## chat `Ctrl+S` 仕様

chat は対話モードで起動するため、`Ctrl+S` を押した時点では **まだサンプル判定を回していない**。そこで `Ctrl+S` 押下時に裏で 1 度サンプル判定を実行 (`SummaryReporter`、画面は汚さない) してチェックする。

1. `Ctrl+S` → サンプル判定を実行し、CLI と同じ 3 条件でチェックする。
2. クリーン → 従来どおり即提出準備し、結果を 1 行表示 (挙動は [026](./026-chat-submit.md) と同じ)。
3. リスクあり → 理由を chat の行に出し、`このまま提出準備しますか? [y/N]` を表示して **確認モード** に入る。
   - 次の打鍵が `y`/`Y` → 提出準備して結果を表示。
   - それ以外の打鍵 (`n`/Esc/その他) → 「提出準備を中止しました」を出して確認モードを抜ける (chat は継続)。
4. chat は常に `[DEBUG]` をコメントアウトしてコピーする ([043](./043-submit-comment-out-debug.md)) 点は不変。

> 確認モード中の打鍵は提出可否の回答として消費する (子プロセスへは送らない)。サンプル判定は同期実行のため、その間 TUI は一瞬応答しない (明示操作なので許容する)。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `--submit` / `Ctrl+S` でクリーン | 確認なしで提出準備 (従来どおり) |
| サンプル不通過 | 理由を出して確認。`y` で提出準備、他で中止 |
| 実行エラー (fetch 失敗等) | 理由を出して確認。`y` で提出準備、他で中止 |
| 実行出力に `[DEBUG]` | (通過していても) 理由を出して確認 |
| CLI で stdin が非 TTY かつリスクあり | 自動で「いいえ」(中止)。exit 1 |
| 解答ファイル本体 | **不変** (チェックは読み取りと実行のみ。加工は [043](./043-submit-comment-out-debug.md) のメモリ上コピー) |

### `DebugSeen` の検出ルール

- サンプル各ケースの実行で得た **生の stdout と stderr** を行に分割し、いずれかの行が `DebugPrefix` (`[DEBUG]`) で始まれば、そのケースは「DEBUG 出力あり」。1 ケースでも該当すれば suite 全体で `DebugSeen=true`。
- `-d`/`--debug` の有無に関係なく検出する (生出力で見る)。`-d` 併用時は `[DEBUG]` 行が判定からは除外され通過しうるが、提出物にデバッグ出力が混じる兆候なので確認対象とする。
- 既存 `splitDebug` ([001](./001-exercise-test.md)) と同じ `[DEBUG]` 規約を、判定からの除外ではなく **確認の根拠** に流用する。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/testexec/judge.go` | `CaseResult` に `DebugSeen bool` を追加。`judge()` で生 stdout / stderr から `[DEBUG]` 行の有無を計算する純粋ヘルパーを追加 |
| `internal/testexec/judge_test.go` (新規 or 追記) | `DebugSeen` の検出 (stdout / stderr / なし) のユニットテスト |
| `cmd/atcoder/submitprep.go` | 提出ゲートを実装: `submitGateReporter` (Reporter をラップし `DebugSeen` を集約)、`submitGateReasons()` (理由組み立ての純粋関数)、`confirmSubmit()` (stdin の y/N。非 TTY は false)、`runSubmitPrep()` (サンプル実行→ゲート→確認→提出準備) |
| `cmd/atcoder/test.go` | `--submit` を `runSubmitPrep` 経由に変更。従来の「全通過時のみ prepareSubmission / それ以外は中止メッセージ」を置き換える |
| `cmd/atcoder/adhoc.go` | chat へ `SubmitCheck` フックを注入する `chatSubmitCheckFunc` を追加 (`SummaryReporter` + ゲートでチェック) |
| `internal/ui/chat.go` | `SubmitCheck` / `SubmitCheckFunc` 型と `ChatHeader.SubmitCheck` を追加。`Ctrl+S` でチェック→クリーンなら即提出 / リスクありなら確認モード (`submitConfirm`) に入り次打鍵で y/N を処理 |
| `fixtures/fixture_okdebug.py` + `fixtures/cache/.../fixture_okdebug/` | 「stdout は正解・stderr に `[DEBUG]`」= 通過するが DEBUG 検出される fixture |
| `fixtures/run.sh` | 非 TTY での `--submit` 確認スキップ (中止 → exit 1) を固定する run_case を追加 |
| `fixtures/README.md` / `docs/tools/atcoder-test-testing.md` | fixture 一覧に `fixture_okdebug` を追記 |
| `docs/tools/atcoder-test-usage.md` | `--submit` 節に提出前チェックと確認の挙動を追記 |
| `docs/tools/atcoder-test-architecture.md` | 提出準備の内部設計にゲート段 (`runSubmitPrep` / `submitGateReporter`) を追記 |
| `docs/tools/todo.md` | 本要件の項目を追加し相互リンク |

### 素描

```go
// internal/testexec/judge.go
type CaseResult struct {
    // ...既存...
    DebugSeen bool // 生 stdout / stderr のいずれかに [DEBUG] 始まりの行があったか (要件 044)
}

// cmd/atcoder/submitprep.go
// submitGateReporter は Reporter をラップし、各ケースの DebugSeen を OR で集約する。
type submitGateReporter struct {
    testexec.Reporter
    mu        sync.Mutex
    debugSeen bool
}
func (r *submitGateReporter) CaseFinished(cr testexec.CaseResult) { /* OR して委譲 */ }
func (r *submitGateReporter) DebugSeen() bool { /* ... */ }

// submitGateReasons は実行結果から確認を促す理由を返す (空ならクリーン)。CLI/chat 共有。
func submitGateReasons(code int, runErr error, debugSeen bool) []string

// confirmSubmit は stdin から y/N を読む。非 TTY は false (中止)。
func confirmSubmit() bool

// runSubmitPrep は --submit 本体: サンプル実行 → ゲート → 確認 → 提出準備。
func runSubmitPrep(contest, task string, lay layout.Layout, opts testexec.Options, noOpen, keepDebug bool) (int, error)
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| サンプル実行エラー + 確認で中止 | 理由表示 → 中止 | 1 |
| 全通過せず + 確認で中止 | 理由表示 → 中止 | 1 |
| DEBUG 検出 + 確認で中止 | 理由表示 → 中止 | 1 |
| 確認に `y` → クリップボードコピー失敗 | エラー表示 | 1 |
| クリーン or 確認 `y` → 提出準備成功 | 既存どおり表示 | 0 |
| 非 TTY (stdin) + リスクあり | 確認を出さず中止 | 1 |

- `submitGateReasons` / `confirmSubmit` は文字列・入出力処理のみで panic させない。
- 非 TTY 判定は `golang.org/x/term` の `IsTerminal(os.Stdin)` を使う (watch の stdout 判定と同系統)。

## 非機能要件

- **解答ファイル非破壊**: チェックは解答の読み取りと実行のみ。書き戻しは一切しない (既存の安全設計を維持)。
- **既存非破壊 (クリーン時)**: クリーンなときの `--submit` / `Ctrl+S` は従来とバイト等価の挙動 (確認を挟まない)。`DebugSeen` は `CaseResult` への追加フィールドで、通常 (`--submit` でない) の `test` / `--json` の挙動は不変。
- **ハングしない**: 非対話環境では確認を待たず安全側 (中止) に倒す。fixtures / CI で `--submit` がブロックしない。
- **前方互換**: ゲートのチェック関数 (`submitGateReasons`) を純粋関数に切り出し、将来の本番モード判定 (`contest.toml`) や `--yes` スキップから再利用できる形にする。
- **TUI を汚さない**: chat のチェックは `SummaryReporter` (stdout 非汚染) で回し、結果は chat の行としてのみ表示する。

## 将来の拡張ポイント

- `--yes` / `-y` で確認をスキップ (自動 `y`)。スクリプトからの一括提出準備向け。
- 解答ソースの静的検査 (コメントアウトし損ねた `[DEBUG]` print が残っていないか) をチェック項目に追加。
- TLE 余裕 (制限時間に対する実行時間の比) が小さいときの警告。
- config 既定で「常に確認」/「クリーン時のみ確認」を切り替え。

## 用語

- **提出前チェック (ゲート)**: 提出準備に進む前に評価する 3 条件 (実行可否・全通過・DEBUG 検出) の判定。
- **クリーン**: 3 条件すべて問題なし (全通過・実行成功・DEBUG 出力なし)。確認を挟まない。
- **`DebugSeen`**: サンプル実行の生 stdout/stderr に `[DEBUG]` 始まりの行が 1 つでもあった状態。
- **提出準備**: サンプル通過後の「(必要なら DEBUG print をコメントアウトした) 解答のクリップボードコピー + 提出ページ起動」。実提出 (POST) は含まない。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- [015-fold-submit-into-test.md](./015-fold-submit-into-test.md) / [ADR 0006](../decisions/0006-fold-submit-into-test.md) (`--submit` を test に畳んだ前例・全通過ゲート)
- [043-submit-comment-out-debug.md](./043-submit-comment-out-debug.md) (提出時の `[DEBUG]` コメントアウト。本件の安全網が補完する)
- [049-submit-precheck-run-commented-source.md](./049-submit-precheck-run-commented-source.md) (本件のゲート実行対象を「提出される中身=コメントアウト後ソース」に変える改訂)
- [026-chat-submit.md](./026-chat-submit.md) (chat `Ctrl+S` の提出準備)
- [001-exercise-test.md](./001-exercise-test.md) (`-d`/`--debug` と `[DEBUG]` 規約 / `splitDebug` の初出)
- `docs/tools/atcoder-test-usage.md` (test 利用手引) / `docs/tools/atcoder-test-architecture.md` (内部設計)
