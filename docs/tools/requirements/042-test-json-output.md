# `atcoder test --json` (判定結果の構造化出力) 要件定義

## 概要

`atcoder test` のサンプル判定モードに `--json` フラグを足し、判定結果 (per-case の verdict・I/O・経過時間と、passed/total サマリ・制限時間などのメタ) を **機械可読な JSON** で stdout に 1 オブジェクトとして出力する。人間向けの色付き表示は出さず、外部ツール (nvim プラグイン等) が `atcoder` を**判定エンジン**として呼び出し、結果を自前 UI (quickfix・フローティング diff 等) に流し込めるようにする。

これは「`atcoder` を TUI として育てるか nvim 拡張に作り直すか」の議論で合意した方針 ([[atcoder-tui-vs-nvim-direction]] / 後述「背景・目的」) の **段階 1 (コアを UI 非依存に固める)** の最初の一手。判定ロジック (`internal/testexec`) は据え置き、出力経路だけを 1 本足す。

## 背景・目的

- `atcoder test` の出力は現状すべて人間向け (色付き diff・サマリ行) で、`internal/ui` の `TestReporter` が stdout に直接書く。外部プログラムが結果を構造的に受け取る経路が無い。
- 将来 nvim 側に薄い Lua フロント (`vim.system()` でコア CLI を叩き、結果を quickfix / diff 表示) を増設する方針を決めた。そのフロントが最初に必要とするのは **サンプル判定結果のデータ**。ここを JSON で吐ければ、UI を Go (bubbletea) から nvim に寄せても判定エンジンは Go のまま使い回せる。
- 競プロ界隈のプラグイン (competitest.nvim 等) も「ロジックは外部 CLI、エディタ側は薄いグルー」という構成が定石。本要件はその CLI 側コントラクトを 1 つ用意するもの。
- 既存の `atcoder usage --json` (要件 037) と同じ「人間向け表 / 機械向け JSON を同一コマンドの `--json` で出し分ける」流儀を踏襲する。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | `atcoder test <contest> --task <task> --json` (サンプル判定モードのみ) | `stats --json` / `review --json` (各 nvim 機能を作る段で別途) |
| 出力 | 全ケース実行後に **1 つの JSON オブジェクト**を stdout へ | NDJSON でのケース逐次ストリーム (watch 連携時) |
| 内容 | per-case verdict・I/O・経過 + サマリ + メタ (contest/task/制限時間/許容誤差) | 解答パス・URL・提出可否などの付加メタ |
| モード | サンプル判定のみ。ad-hoc (`--in`/`--out`)・対話 (`--interactive`)・`--watch`・`--submit` とは非併用 | `--watch --json` で再判定ごとに NDJSON を流す |

### 他モードとの境界

`--json` は **サンプル判定モード専用**。次のフラグとは併用不可 (フラグ誤り = exit 2):

- ad-hoc / 対話: `--in` / `--out` / `--interactive` — 出力モデルが per-case 判定でない。
- `--watch` — ライブ再描画 (TTY 前提) と単発 JSON 出力は両立しない。将来 NDJSON で別途対応。
- `--submit` — クリップボードコピー + ブラウザ起動という副作用と機械出力は混ぜない。
- `--side-by-side` (`-s`) — 人間向け diff 整形フラグ。JSON では無視されるべきなので、誤用を避けるため明示時はフラグ誤りにはせず**黙って無視**してよい (config 既定で true になりうるため。値では判定しない)。

`-c`/`--case` (ケース絞り込み)・`-d`/`--debug`・`--timeout`・`--tolerance`・`-j`/`--jobs`・`--refresh`・`--layout` は **併用可** (判定の入力条件であって出力形態と直交する)。`-v`/`--verbose` は人間向け表示制御なので JSON 出力には影響しない (無視)。

## JSON スキーマ

stdout に出すトップレベルオブジェクト (`encoding/json`、2 スペースインデント):

```json
{
  "contest": "abc457",
  "task": "abc457_d",
  "time_limit_ms": 2000,
  "timeout_ms": 2000,
  "tolerance": 0.000001,
  "passed": 2,
  "total": 3,
  "all_passed": false,
  "cases": [
    {
      "name": "01",
      "status": "AC",
      "elapsed_ms": 12,
      "input": "3\n1 2 3",
      "expected": "6",
      "actual": "6",
      "stderr": "",
      "debug": ""
    },
    {
      "name": "02",
      "status": "WA",
      "elapsed_ms": 14,
      "input": "...",
      "expected": "...",
      "actual": "...",
      "stderr": "",
      "debug": ""
    },
    {
      "name": "x01",
      "status": "RE",
      "elapsed_ms": 8,
      "input": "...",
      "expected": "...",
      "actual": "",
      "stderr": "Traceback ...",
      "debug": ""
    }
  ]
}
```

### トップレベル

| フィールド | 型 | 取得元 | 用途 |
|---|---|---|---|
| `contest` | string | CLI 引数 | 表示・キー |
| `task` | string | `--task` 正規化後 (`abc457_d`) | 表示・キー |
| `time_limit_ms` | int | 問題の `meta.toml` (`Header` の timeLimitMs) | 表示・TLE 判断材料 |
| `timeout_ms` | int | 実際に適用した制限時間 (`--timeout` 上書き or 既定) | 経過との比較 |
| `tolerance` | float | 適用した float 許容誤差 | 表示 |
| `passed` | int | 通過ケース数 | サマリ |
| `total` | int | 実行ケース数 | サマリ |
| `all_passed` | bool | `passed == total && total > 0` | フロントの成否判定 |
| `cases` | array | per-case (ケース名順) | 各ケースの verdict・I/O |

### `cases[]` 要素

| フィールド | 型 | 取得元 (`testexec.CaseResult`) | 備考 |
|---|---|---|---|
| `name` | string | `Name` | 表示 id (公式 `01`… / 追加 `x01`…) |
| `status` | string | `Status` を文字列化 | `"AC"` / `"WA"` / `"TLE"` / `"RE"` |
| `elapsed_ms` | int | `Elapsed` を ms 換算 | 経過時間 |
| `input` | string | `Input` | テストケース標準入力 (末尾改行 trim 済み) |
| `expected` | string | `Expected` | normalize 済み期待出力 |
| `actual` | string | `Actual` | normalize 済み実際の stdout (debug 時は `[DEBUG]` 行除外後) |
| `stderr` | string | `Stderr` | RE のときのみ非空 |
| `debug` | string | `Debug` | `-d`/`--debug` 時のみ非空 (`[DEBUG]` 行) |

- `status` のマッピング: `Pass`→`AC` / `Fail`→`WA` / `TLE`→`TLE` / `RE`→`RE`。`testexec.CaseStatus` は内部 enum なので、文字列化は `cmd/atcoder` 側の純粋関数で行う (`internal/testexec` の表示語彙に依存しない)。
- `input`/`expected`/`actual`/`stderr`/`debug` は常にキーを出す (空でも `""`)。フロントが欠落キーを気にせず読めるようにする。

## CLI 仕様

```
atcoder test <contest> --task <task> --json
              [-c <N[,M,...]>] [-d] [--timeout <dur>] [--tolerance <eps>]
              [-j <n>] [--refresh] [--layout <auto|abc|exercise>]
```

| フラグ | 説明 |
|---|---|
| `--json` | 判定結果を JSON で stdout に出力する (サンプル判定モード専用)。人間向け表示は出さない |

### 処理ステップ

`atcoder test fixture --task pass --json` 実行時:

1. フラグ解析。`--json` と非併用フラグ (`--in`/`--out`/`--interactive`/`--watch`/`--submit`) の同時指定は exit 2。
2. レイアウト解決・解答パス確定 (既存と同じ)。
3. `internal/testexec.Run` を **`SummaryReporter` を Reporter にして**実行 (stdout には何も書かない)。サンプルが未取得なら従来どおり fetch (fetch 進捗も stdout には出さない)。
4. `SummaryReporter` から per-case 結果・passed/total と、`Header` で渡るメタ (timeLimitMs/timeoutMs/tolerance) を取得。
5. トップレベルオブジェクトを組み、`encoding/json` で stdout に出力 (末尾改行付き)。
6. exit code は既存の判定セマンティクスを踏襲 (下記)。

### 出力イメージ

```
$ atcoder test fixture --task pass --json
{
  "contest": "fixture",
  "task": "fixture_pass",
  "time_limit_ms": 2000,
  "timeout_ms": 2000,
  "tolerance": 0.000001,
  "passed": 1,
  "total": 1,
  "all_passed": true,
  "cases": [
    {
      "name": "01",
      "status": "AC",
      "elapsed_ms": 5,
      "input": "5",
      "expected": "10",
      "actual": "10",
      "stderr": "",
      "debug": ""
    }
  ]
}
$ echo $?
0
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| stdout の純度 | `--json` 時は stdout に **JSON オブジェクト 1 個だけ**。fetch 進捗・サマリ・diff は出さない (SummaryReporter は表示系すべて no-op) |
| exit code | 全通過 = 0、1 件でも不通過 = 1、フラグ誤り = 2、fetch / 実行失敗 = 1 (JSON は出さずエラーを stderr へ)。`all_passed` フィールドでも成否を読めるが exit code も従来規約を維持する |
| エラー時 | testexec が error を返す (ケース無し・fetch 失敗・実行失敗) ときは JSON を出さず、従来どおり `atcoder test: <err>` を stderr に出し exit 1 |
| ケース絞り込み | `-c 02` 等を併用すると、実行・出力されるのは絞った集合だけ。`total` はその集合の件数 |
| debug | `-d` 併用時は `[DEBUG]` 行を比較から除外し、`cases[].debug` に格納。verdict も `-d` の有無で変わりうる (既存挙動) |
| 決定性 | `cases` はケース名順 (`SummaryReporter.End` がケース名順で渡す)。並列実行しても出力順は安定 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/test.go` | `--json` フラグ追加。非併用バリデーション。`--json` 時は `SummaryReporter` で `testexec.Run` を回し、結果を JSON 化して出力する分岐 (`runTestJSON` 的なヘルパー) |
| `internal/testexec/summaryreporter.go` | `Header` を no-op から **メタ捕捉**に変更 (timeLimitMs/timeoutMs/tolerance/ntests を保持)、`Meta()` アクセサ追加。既存 `start.go` は無視するだけなので非破壊 |
| `cmd/atcoder/test.go` (純粋関数) | `CaseStatus` → 文字列 (`AC`/`WA`/`TLE`/`RE`) の写像をユニットテスト可能な純粋関数で |
| `internal/complete/` | `test` のフラグ候補に `--json` を追加 |
| `fixtures/run.sh` | `test --task pass --json` = exit 0 / `test --task fail --json` = exit 1 / `--json --interactive` 等の併用 = exit 2 を smoke。JSON 本文の妥当性 (`passed`/`status` キー) も最低限 grep で確認 |
| `docs/tools/atcoder-test-usage.md` | `--json` の説明・出力例・非併用の注意を追記 |
| `docs/tools/atcoder-test-architecture.md` | SummaryReporter のメタ捕捉と JSON 出力経路を追記 |
| `docs/tools/todo.md` | 本機能を新項目として記録 (TUI vs nvim 段階 1) し本要件へ相互リンク |

### `SummaryReporter` のメタ捕捉 (追記内容)

```go
// Header で渡るメタを捕捉する (これまで no-op)。JSON 出力がトップレベルの
// time_limit_ms / timeout_ms / tolerance を必要とするため。start.go は Meta() を
// 読まないので既存挙動は不変。
func (r *SummaryReporter) Header(task, contest string, timeLimitMs, timeoutMs, ntests int, tolerance float64) {
    r.mu.Lock()
    r.timeLimitMs, r.timeoutMs, r.tolerance, r.ntests = timeLimitMs, timeoutMs, ntests, tolerance
    r.mu.Unlock()
}

// Meta は捕捉した Header メタを返す。
func (r *SummaryReporter) Meta() (timeLimitMs, timeoutMs, ntests int, tolerance float64)
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `--json` と `--in`/`--out`/`--interactive` 同時 | "... cannot be combined with --json" 等で exit 2 |
| `--json` と `--watch` 同時 | exit 2 (将来 NDJSON で対応する旨はドキュメントに) |
| `--json` と `--submit` 同時 | exit 2 |
| サンプル未取得 + fetch 失敗 | JSON を出さず stderr にエラー、exit 1 |
| テストケースが無い | JSON を出さず stderr にエラー、exit 1 |
| 一部 / 全ケース不通過 | **JSON は正常に出力** (FAIL は実行エラーではない)、exit 1 |
| JSON encode 失敗 (通常起きない) | stderr にエラー、exit 1 |

## 非機能要件

- **stdout コントラクト**: `--json` 指定時の stdout は厳密に JSON 1 オブジェクト。外部パーサが安定して読める (人間向け文字列を混ぜない)。
- **既存非破壊**: `--json` 無しの `test` 挙動・exit code・`start` の SummaryReporter 利用は不変。`Header` 捕捉は追加フィールドのみ。
- **判定ロジック不可侵**: 判定・fetch・normalize は `internal/testexec` のまま再利用。出力経路だけを足す。
- **前方互換**: スキーマはキー追加で拡張できる形 (フロントは未知キーを無視)。`status` 語彙は安定文字列。
- **オフライン smoke 可能**: fixture のキャッシュ済みケースで JSON 出力を検証でき、`run.sh` は AtCoder に触れない。

## 将来の拡張ポイント

- **`--watch --json` (NDJSON)**: 再判定のたびに 1 行 JSON を流し、nvim 側がライブ更新する。
- **`stats --json` / `review --json`**: それぞれの nvim 機能を作る段で、同じ流儀で機械出力を足す (段階 1 の続き)。
- **解答パス・URL の同梱**: フロントが「どのファイルを開くか」「提出ページ URL」を JSON から得られるようにする。
- **共通 JSON ヘルパー**: `usage --json` と本機能で encode 設定 (indent) が重複するなら小ヘルパーに括り出す余地。

## 用語

- **判定エンジン**: サンプル取得・実行・judge を行うコア (`internal/testexec`)。UI から切り離して外部から呼べる状態を「UI 非依存」と呼ぶ。
- **段階 1**: TUI vs nvim 議論で決めた「コアを UI 非依存に固める」フェーズ。本要件はその最初の deliverable。
- (`contest_id` / `task_id` / `letter` / `layout` は要件 002 に準拠)

## 関連ドキュメント

- `docs/tools/requirements/001-exercise-test.md` (test サブコマンド本体・fetch / judge / meta の基盤)
- `docs/tools/requirements/037-usage-telemetry.md` (`usage --json` の先例。人間向け表 / 機械向け JSON の出し分け)
- `docs/tools/requirements/028-start-watch-per-case.md` / `036-start-watch-detail-view.md` (`SummaryReporter` の per-case 捕捉・I/O 同梱の前例)
- `docs/tools/atcoder-test-usage.md` / `atcoder-test-architecture.md` (利用手引 / 内部設計)
- `docs/tools/todo.md` (TUI vs nvim 段階 1 の記録先)
