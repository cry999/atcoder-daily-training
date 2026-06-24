# 提出準備時に DEBUG 出力行をコメントアウト 要件定義

## 概要

`atcoder test --submit` (および chat の `Ctrl+S`) でクリップボードへコピーする解答ソースから、`[DEBUG]` を出力する `print(...)` 行を **コメントアウトしてからコピー** する。提出コードにデバッグ出力を残したまま提出して WA / TLE になる事故を防ぐのが狙い。**解答ファイル本体は一切書き換えず、クリップボードに載せる中身だけを加工する** (既存の「解答ファイルを壊さない」安全設計を維持)。

既存の DEBUG 機構は「実行時の **stdout** で `[DEBUG]` 始まりの行を判定から除外」するもの (`-d`/`--debug`、`internal/testexec/judge.go` の `splitDebug`)。本件はそれと一貫した `[DEBUG]` 規約を **ソース行の判定** に流用し、提出コードからデバッグ出力を取り除く。

## 背景・目的

- ローカルでは `print(f"[DEBUG] ...")` でデバッグ出力を撒き、`atcoder test -d` で `[DEBUG]` 行を判定から除外して通している (推奨パターンは fixture_debug.py 参照)。
- ところが `--submit` / `Ctrl+S` は解答を **無加工** でクリップボードへ載せるため、デバッグ出力を消し忘れたまま提出ページに貼って WA になる、あるいは大量の `print` で TLE になる事故が起きうる。
- 提出直前という確定したタイミングで、`[DEBUG]` を出す print を機械的にコメントアウトしておけば、消し忘れ事故を構造的に防げる。`-d` の `[DEBUG]` 規約をそのまま使うので、ユーザは新しい書き方を覚えなくてよい。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象経路 | `test --submit` (CLI) と chat `Ctrl+S` の両方 (= `submitPrepCore` 経由) | — |
| 対象言語 | Python (`.py`) のみ。コメント文字は `#` | 他言語 Runner 追加時に言語別コメント規則 |
| 検出対象 | 行頭 (インデント可) が `print(...)` で、最初の文字列引数が `[DEBUG]` で始まる行 | 行末マーカー (`# debug`)、`if DEBUG:` ブロック単位の除去 |
| 加工方法 | 行頭インデントを保ったまま `# ` を差し込んでコメントアウト (削除はしない) | — |
| 有効化 | **デフォルト ON**。`--keep-debug` でオプトアウト | config 既定値化 |
| 解答ファイル | **触れない** (読み取りのみ。加工はメモリ上のコピーだけ) | — |

### 境界 (非対象)

- **ガード下の単独 print** (`if os.environ.get("DEBUG"):` の直下にある唯一の print) は **コメントアウトしない**。コメントアウトするとブロックが空になり `IndentationError` を起こすため。そもそもガード下の print はジャッジ上 `DEBUG` 未設定で実行されないので、消さなくても無害。判定ルールは「直前の非空行が `:` で終わる print 行はスキップ」(下記 動作仕様)。
- 複文 (`x = 1; print("[DEBUG]...")` のようにセミコロンで継いだ行) や複数行にまたがる `print(...)` は対象外 (行頭が `print(` の単純な行だけを扱う)。
- 行末マーカー方式 (`... # debug` で任意の文をコメントアウト) は今回は採らない (検出ルールで決定済み: `[DEBUG]` 出力行のみ)。

## CLI 仕様

`--submit` に修飾フラグを 1 つ足す (サンプルモード専用)。

```
atcoder test <contest> --task <task> [... 既存フラグ ...] --submit [--no-open] [--keep-debug]
```

| フラグ | モード | 説明 |
|---|---|---|
| `--submit` | サンプル | サンプルが全通過したら、解答をクリップボードへコピーし提出ページをブラウザで開く (既存) |
| `--no-open` | サンプル | `--submit` 時にブラウザを開かず URL を表示するだけ (既存) |
| `--keep-debug` | サンプル | `--submit` 時に `[DEBUG]` 出力行のコメントアウトを **行わず** 解答を無加工でコピーする (オプトアウト) |

- `--keep-debug` は `--submit` の修飾。`--no-open` と同様、ad-hoc / 対話フラグ (`--in`/`--out`/`--interactive`) との併用は exit 2。`--submit` 無しでの単独指定は無害 (no-op)。
- chat `Ctrl+S` 経路は常にコメントアウトする (デフォルト ON 固定。chat には `--keep-debug` 相当のトグルは設けない)。

### 処理ステップ (`test --submit`)

1. 通常どおりサンプル判定 (`testexec.Run`)。全通過 (exit 0) でなければ提出準備せず終了。
2. 解答ファイルを読む (メモリ上)。
3. `--keep-debug` でなければ、`[DEBUG]` を出力する `print` 行をコメントアウトした文字列を作る (ファイルは書き換えない)。コメントアウトした行数を数える。
4. 加工後 (または無加工) の文字列をクリップボードへコピー。
5. 提出 URL を組み立て、`--no-open` でなければブラウザで開く (best-effort)。
6. 結果を表示して exit 0。コメントアウトが 1 行以上あれば、その件数を併せて表示する。

### 出力イメージ

```
$ atcoder test abc457 --task d --submit
abc457_d  contest=abc457  ...  tests=3
[01] PASS ...
Result: 3/3 PASS
クリップボードにコピーしました: exercise/2026/06/09/abc457_d.py (DEBUG 出力 2 行をコメントアウト)
提出ページを開きました: https://atcoder.jp/contests/abc457/submit?taskScreenName=abc457_d
```

`--keep-debug` 指定時、またはコメントアウト対象が 0 行のときは、件数の補足を付けず従来どおりの 1 行 (`クリップボードにコピーしました: <path>`) を出す。

### 加工例

入力 (解答ファイル、無変更):

```python
n = int(input())
print(f"[DEBUG] n={n}")
total = 0
for i in range(n):
    print("[DEBUG]", i)
    total += i
print(total)
```

クリップボードに載る内容 (デフォルト ON):

```python
n = int(input())
# print(f"[DEBUG] n={n}")
total = 0
for i in range(n):
    # print("[DEBUG]", i)
    total += i
print(total)
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `--submit` (全 PASS、デフォルト) | `[DEBUG]` print 行をコメントアウトしてコピー、件数を表示、exit 0 |
| `--submit --keep-debug` | 無加工でコピー (件数表示なし)、exit 0 |
| `--submit` で対象 0 行 | 無加工と同じ内容をコピー、件数表示なし、exit 0 |
| chat `Ctrl+S` | 常にコメントアウトしてコピー、結果行に件数を併記 |
| 解答ファイル本体 | **不変** (加工はメモリ上のコピーのみ) |

### コメントアウトの検出・変換ルール

- **検出**: 行の先頭 (任意のインデント) が `print(` で始まり、最初の引数が `[DEBUG]` で始まる文字列リテラル (`"`/`'`、`f`/`r` 等のプレフィックス可) である行。
  - 該当: `print("[DEBUG] ...")` / `print(f"[DEBUG] {x}")` / `print("[DEBUG]", x)` / 先頭にインデントがあるもの。
  - 非該当: 既に `#` でコメントアウト済みの行 (行頭が `print` でないため自然にスキップ → **冪等**)、`[DEBUG]` を含まない print、複文・複数行 print。
- **変換**: 行頭インデントを保持したまま、最初の非空白文字の直前に `# ` を差し込む (`    print(...)` → `    # print(...)`)。インデント後のコメントは Python で合法。
- **安全スキップ**: 検出にマッチしても、**直前の非空行が `:` で終わる** (= ブロック先頭の文) 場合はコメントアウトしない。空ブロック化による `IndentationError` を避けるため。ガード下のデバッグ print はジャッジで実行されないので、残しても無害。

### 冪等性

- 同じソースに 2 回適用しても結果は同じ (コメントアウト済み行は行頭が `#` で `print` 始まりにならず再マッチしないため)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| 新規 `internal/debugstrip/debugstrip.go` | 純粋関数 `CommentOut(src string) (out string, n int)` — Python ソース文字列から `[DEBUG]` print 行をコメントアウトし、件数を返す |
| 新規 `internal/debugstrip/debugstrip_test.go` | 検出・変換・安全スキップ・冪等性・件数のユニットテスト |
| `cmd/atcoder/submitprep.go` | `submitPrepCore` に `keepDebug bool` 引数追加。`!keepDebug` のとき `debugstrip.CommentOut` を適用してからクリップボードへ書く。`submitOutcome` に `DebugCommented int` を追加 |
| `cmd/atcoder/test.go` | `--keep-debug` フラグ追加。ad-hoc 排他チェックの対象に追加。`prepareSubmission` へ `keepDebug` を渡す |
| `cmd/atcoder/adhoc.go` | chat `Ctrl+S` (`chatSubmitFunc`) は `keepDebug=false` で呼び、件数を結果メッセージに併記 |
| `cmd/atcoder/main.go` | `test` の usage 文字列に `--keep-debug` を追記 |
| `internal/complete/complete.go` (+ test) | `test` のフラグ候補に `--keep-debug` を追加 |
| `fixtures/...` + `fixtures/run.sh` | コメントアウト挙動を固定する fixture と run_case (詳細は テスト戦略) |
| `docs/tools/atcoder-test-usage.md` | `--submit` 節に `--keep-debug` とコメントアウト挙動を追記 |
| `docs/tools/atcoder-test-architecture.md` | 提出準備の内部設計に DEBUG コメントアウト段を追記 |
| `docs/tools/todo.md` | 該当項目を `✅ DONE` 化し本要件へ相互リンク |

### `internal/debugstrip` の素描

```go
// Package debugstrip は提出準備時に Python 解答ソースから [DEBUG] 出力 print を
// コメントアウトする。判定・実行には関与せず、文字列変換のみを行う純粋パッケージ。
package debugstrip

// CommentOut は src 中の「行頭 (インデント可) が print(...) で最初の文字列引数が
// [DEBUG] で始まる」行をコメントアウトし、加工後ソースとコメントアウト件数を返す。
// 直前の非空行が ':' で終わる print 行は空ブロック化を避けるためスキップする。
// 冪等 (コメントアウト済み行は再マッチしない)。
func CommentOut(src string) (out string, n int)
```

`submitPrepCore` 側の結線 (素描):

```go
func submitPrepCore(contest, task string, lay layout.Layout, noOpen, keepDebug bool) (submitOutcome, error) {
    // ...解答読込...
    body := string(src)
    commented := 0
    if !keepDebug {
        body, commented = debugstrip.CommentOut(body)
    }
    if err := clipboard.WriteAll(body); err != nil { /* exit 1 */ }
    out := submitOutcome{CopiedPath: solutionPath, URL: ..., DebugCommented: commented}
    // ...
}
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `--keep-debug` + ad-hoc フラグ (`--in`/`--out`/`--interactive`) | "…cannot be combined with …" | 2 |
| クリップボードコピー失敗 (加工後) | エラー表示 | 1 |
| 加工対象 0 行 | 無加工と同等にコピー (エラーでない) | 0 |
| 正常 (コメントアウト + コピー) | 件数を表示 | 0 |

- `debugstrip.CommentOut` は文字列変換のみで失敗経路を持たない (panic させない)。想定外入力 (空文字列・末尾改行の有無) でも素直に返す。

## 非機能要件

- **解答ファイル非破壊**: 加工はメモリ上のコピー文字列に対してのみ。ファイルへの書き戻しは絶対にしない (既存の安全設計を維持)。
- **既存非破壊**: `--keep-debug` 指定時、または対象 0 行のときは従来とバイト等価の内容をコピーする。`--submit` 無しの `test` の挙動は不変。
- **冪等**: 同一ソースへの複数回適用で結果不変。
- **前方互換**: `submitPrepCore` のシグネチャ変更は内部のみ (2 つの呼び出し元を同時更新)。将来の本番モード判定 (`contest.toml`) からも `keepDebug` を入力にできるよう、フラグは引数で渡す形にする。
- **言語非依存に拡張しやすく**: 当面 Python 専用だが、`debugstrip` を独立パッケージに切ることで言語別ルールを足しやすくする。

## 将来の拡張ポイント

- 行末マーカー (`... # debug`) による任意文のコメントアウト。
- `if os.environ.get("DEBUG"):` ガードブロックごとの除去 (空ブロック化を伴うため、ブロック単位の構文認識が必要)。
- config 既定での ON/OFF 切り替え (`[test] strip_debug = false` 等)。
- 他言語 Runner 追加時の言語別コメント規則。

## 用語

- **提出準備**: サンプル全通過後の「(必要なら DEBUG print をコメントアウトした) 解答のクリップボードコピー + 提出ページ起動」。実提出 (POST) は含まない。
- **`[DEBUG]` 規約**: stdout 先頭が `[DEBUG]` の行をデバッグ出力とみなす既存規約 (`-d`/`--debug` の `splitDebug`)。本件はこの規約を **ソース行の print** に流用する。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- [015-fold-submit-into-test.md](./015-fold-submit-into-test.md) / [ADR 0006](../decisions/0006-fold-submit-into-test.md) (`--submit` を test に畳んだ前例)
- [001-exercise-test.md](./001-exercise-test.md) (`-d`/`--debug` と `[DEBUG]` 規約の初出)
- [026-chat-submit.md](./026-chat-submit.md) (chat `Ctrl+S` の提出準備)
- [044-submit-precheck-confirm.md](./044-submit-precheck-confirm.md) (提出前チェックと確認。実行時の DEBUG 検出で本件のコメントアウト漏れを補完する)
- `docs/tools/atcoder-test-usage.md` (test 利用手引) / `docs/tools/atcoder-test-architecture.md` (内部設計)
