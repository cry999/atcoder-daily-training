# 提出準備時に solve-stat コメントブロックを除去 要件定義

## 概要

`atcoder test --submit` (および chat の `Ctrl+S`) でクリップボードへコピーする解答ソースから、解答ファイル冒頭の **solve-stat ブロック** (`# >>> atcoder-stat >>>` 〜 `# <<< atcoder-stat <<<`、要件 [061](./061-solve-record-stats.md)) を **除去してからコピー** する。実装時間・正答状況・5 軸スコアといった**個人の練習メタデータを提出コードに混ぜない**のが狙い。**解答ファイル本体は一切書き換えず、クリップボードに載せる中身だけを加工する** (既存の「解答ファイルを壊さない」安全設計を維持)。

`[DEBUG]` print 行のコメントアウト (要件 [043](./043-submit-comment-out-debug.md)) と同じ「提出される中身を組み立てる 1 箇所 (`buildSubmitSource`) で加工する」設計に乗せる。両者は独立した加工段で、solve-stat 除去は `--keep-debug` の有無に関わらず**常時**行う。

## 背景・目的

- 要件 061 で `atcoder start` / `record` が解答ファイル冒頭に solve-stat ブロック (Python コメント) を刻むようになった。実行・サンプル判定には影響しない (コメントなので) が、`--submit` / `Ctrl+S` は解答を **無加工** でクリップボードへ載せるため、この個人メタデータがそのまま提出コードの先頭に貼り付いてしまう。
- 提出コードに `started_at` / `duration_ms` / スコア等が残るのは、機能上の害 (WA/TLE) はないものの、**練習の内部記録を公開提出に混ぜる**ことになり望ましくない。提出物は「解いたコードそのもの」だけであるべき。
- 提出準備という確定したタイミングで solve-stat ブロックを機械的に取り除けば、記録を残す運用 (061) と、提出物をクリーンに保つ運用を両立できる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象経路 | `test --submit` (CLI) と chat `Ctrl+S` の両方 (= `buildSubmitSource` 経由) | — |
| 対象言語 | Python (`#` コメント) のみ。マーカーは 061 と共通 | 他言語 Runner 追加時に言語別マーカー |
| 検出対象 | solve-stat ブロック (開始/終了マーカーで挟まれた範囲、マーカー行含む) | — |
| 加工方法 | ブロック行 (マーカー含む) を丸ごと除去。前後のコードは温存 | — |
| 有効化 | **常時 ON**。オプトアウトフラグは設けない (提出物にメタデータを混ぜる意味がないため) | 必要が生じれば `--keep-stat` 相当を検討 |
| 解答ファイル | **触れない** (読み取りのみ。加工はメモリ上のコピーだけ) | — |

### 境界 (非対象)

- **`[DEBUG]` print のコメントアウト** (要件 043) とは独立した加工段。solve-stat 除去はブロック丸ごとの**削除**、DEBUG は行の**コメントアウト**で、対象も目的も別。両方が両経路で適用される (適用順は下記)。
- solve-stat ブロックが**無い**解答は無加工 (バイト等価)。
- マーカーが**破損** (片方だけ/重複/順序逆転) している場合は、コードを誤って削らないよう**除去せずそのまま**コピーする (061 の Parse と同じ安全側)。破損の通知・修復はしない (提出準備は解答を壊さないことを最優先する)。

## CLI 仕様

新しいフラグ・サブコマンドは**追加しない**。既存の `--submit` / `Ctrl+S` の挙動に、solve-stat 除去段を 1 つ挟むだけ。

```
atcoder test <contest> --task <task> [... 既存フラグ ...] --submit [--no-open] [--keep-debug]
```

### 処理ステップ (`test --submit` / `Ctrl+S` 共通、`buildSubmitSource` 内)

1. 解答ファイルを読む (メモリ上)。
2. **solve-stat ブロックがあれば除去**する (常時)。ブロック無し/破損なら無加工。
3. `--keep-debug` でなければ、残りに対し `[DEBUG]` print 行をコメントアウトする (要件 043。chat 経路は常時 ON)。
4. 加工後の文字列を「提出される中身」(`submitSource.Body`) とする。以降、提出ゲートのサンプル実行 (要件 049) とクリップボードコピーはこの同じ Body を使う。

solve-stat 除去は DEBUG コメントアウトより**前**に行う (ブロックを消してから残りの print を見る)。両者は対象行が重ならない (solve-stat は `# ...` コメント、DEBUG は `print(...)`) ため順序で結果は変わらないが、除去を先にして「素のコード」に対して DEBUG 判定する形にする。

### 加工例

入力 (解答ファイル、無変更):

```python
# >>> atcoder-stat >>>
# started_at  = 2026-07-01T16:00:00+09:00
# duration_ms = 1500000
# ac          = true
# <<< atcoder-stat <<<
n = int(input())
print(f"[DEBUG] n={n}")
print(n * 2)
```

クリップボードに載る内容 (solve-stat 除去 + DEBUG コメントアウト):

```python
n = int(input())
# print(f"[DEBUG] n={n}")
print(n * 2)
```

`--keep-debug` 指定時は solve-stat だけ除去し DEBUG はそのまま:

```python
n = int(input())
print(f"[DEBUG] n={n}")
print(n * 2)
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `--submit` / `Ctrl+S` (ブロックあり) | solve-stat ブロックを除去してコピー |
| `--submit` / `Ctrl+S` (ブロックなし) | 無加工 (solve-stat 段はバイト等価) |
| solve-stat ブロック破損 (マーカー不整合) | 除去せずそのままコピー (誤削除回避の安全側) |
| `--keep-debug` | solve-stat は除去、DEBUG はコメントアウトしない |
| 解答ファイル本体 | **不変** (加工はメモリ上のコピーのみ) |

### 除去ルール

- **検出**: 061 と同じマーカー (`# >>> atcoder-stat >>>` / `# <<< atcoder-stat <<<`) を行単位で探す (`solvestat.locateMarkers` を再利用)。
- **除去**: 開始マーカー行から終了マーカー行までを (マーカー行を含めて) すべて取り除き、前後の行を連結する。ブロックは常に先頭にある (061) ので、実際には「先頭のブロックを剥がして素のコードを残す」動作になる。
- **バイト等価性**: ブロックが無ければ入力をそのまま返す。ブロックが先頭にある通常ケースでは、除去後は 061 がブロックを挿入する前の元コードとバイト等価になる (`block + src` から `block` を剥がすと `src` に戻る)。

### 冪等性

- solve-stat 除去は一度で完結する (除去後のソースにはマーカーが残らないため、再適用しても no-op)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/solvestat/solvestat.go` | 純粋関数 `Strip(src []byte) []byte` を追加 — solve-stat ブロックを除去した新ソースを返す。ブロック無し/破損時は `src` をそのまま返す |
| `internal/solvestat/solvestat_test.go` | `Strip` の除去・バイト等価 (ブロック無し)・破損時非除去・冪等のユニットテスト |
| `cmd/atcoder/submitprep.go` | `buildSubmitSource` で `os.ReadFile` 後に `solvestat.Strip` を適用してから `debugstrip.CommentOut` にかける (solvestat は import 済み) |
| `docs/tools/usage/test.md` | 提出準備節に「solve-stat ブロックを除去してコピー」を追記 |
| `docs/tools/usage/record.md` | 「提出のクリップボードコピーには影響しない」旨の記述を「提出時は除去される」に更新 |
| `docs/tools/todo.md` | 本要件へ相互リンク (該当があれば DONE 化) |

### `solvestat.Strip` の素描

```go
// Strip は src から solve-stat ブロックを取り除いた新ソースを返す。ブロックが無ければ
// src をそのまま返す。マーカーが破損している (片方だけ/重複/順序逆転) 場合は、コードを
// 誤って削らないよう src をそのまま返す (Parse と同じ安全側)。提出される中身から
// 個人の練習メタデータ (solve-stat) を除くのに使う (要件 063)。解答ファイルは書き換えない。
func Strip(src []byte) []byte
```

`buildSubmitSource` 側の結線 (素描):

```go
src, err := os.ReadFile(solutionPath)
// ...
body := string(solvestat.Strip(src)) // solve-stat を除去 (常時)
commented := 0
if !keepDebug {
    body, commented = debugstrip.CommentOut(body)
}
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| solve-stat ブロック破損 | 除去せずそのままコピー (エラーにしない) | 既存どおり |
| ブロックなし | 無加工でコピー | 既存どおり |
| 正常 (除去 + コピー) | 従来の提出準備メッセージ (件数表示は DEBUG 側のみ) | 0 |

- `solvestat.Strip` は文字列変換のみで失敗経路を持たない (panic させない)。想定外入力 (空・末尾改行の有無・複数マーカー) でも素直に返す。
- solve-stat 除去は**件数・通知を出さない** (常時 ON の透過的なクリーンアップ)。DEBUG コメントアウトのような件数表示は付けない。

## 非機能要件

- **解答ファイル非破壊**: 加工はメモリ上のコピー文字列に対してのみ。ファイルへの書き戻しは絶対にしない (061 の記録運用と共存)。
- **既存非破壊**: solve-stat ブロックが無い解答は従来とバイト等価の内容をコピーする。`--submit` 無しの `test` の挙動は不変。
- **判定と提出物の一致**: 除去は `buildSubmitSource` の 1 箇所で行うため、提出ゲートのサンプル実行 (要件 049) とクリップボードコピーは同じ Body を使う。「判定は通ったが別物を提出」は起きない。
- **冪等・安全側**: 破損ブロックは触らない。除去は一度で完結。
- **前方互換**: `Strip` は 061 のマーカー定数・`locateMarkers` を再利用するので、将来の言語別マーカー対応でも 1 箇所の差し替えで追随できる。

## 将来の拡張ポイント

- 他言語 Runner 追加時の言語別マーカー (061 の `commentPrefix` 抽象化と連動)。
- 必要が生じたときの `--keep-stat` 相当のオプトアウト (現状は不要と判断)。

## 用語

- **solve-stat ブロック**: 解答冒頭の機械可読コメント列 (要件 061)。開始/終了マーカーで挟まれる。
- **提出される中身**: `buildSubmitSource` が組み立てる、クリップボードに載りゲート実行の対象にもなる文字列 (要件 049 の `submitSource.Body`)。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- [061-solve-record-stats.md](./061-solve-record-stats.md) (solve-stat ブロックの読み書き。本件が除去する対象)
- [043-submit-comment-out-debug.md](./043-submit-comment-out-debug.md) (提出準備時の DEBUG コメントアウト。同じ `buildSubmitSource` に乗る独立段)
- [049-submit-precheck-run-commented-source.md](./049-submit-precheck-run-commented-source.md) (提出される中身を判定対象にする。除去後 Body がゲート実行対象になる)
- [044-submit-precheck-confirm.md](./044-submit-precheck-confirm.md) (提出前チェック)
- `docs/tools/usage/test.md` (提出準備の利用手引) / `docs/tools/usage/record.md` (solve-stat 記録)
