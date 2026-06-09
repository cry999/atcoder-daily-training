# `atcoder review <category>` 練習コンテスト一覧 要件定義

## 概要

`exercise/` で取り組んだコンテストを **カテゴリ単位で一覧** できる読み取り専用サブコマンド `atcoder review <category>` を足す。`atcoder review abc` で「これまで練習した ABC を contest × letter のテーブルで並べ、各コンテストを最後に解いた日付を添える」。どの回のどの問題に取り組んだか・どこまで埋めたかを 1 画面で振り返れるようにする。

集計対象・日付の出所・読み取り専用/オフラインという前提は `stats` と完全に共有し、データ層 (`internal/stats` の `Scan`/`Solve`) を流用する。`stats` が「集計値 (総数・ストリーク・カテゴリ別・時系列・草グラフ)」を出すのに対し、`review` は「個々のコンテストの**列挙**」を担う別コマンドとして責務を分ける。

> 関連: `docs/tools/requirements/005-exercise-stats.md` (集計コマンド `stats`、データ層の定義元)。本書はその姉妹コマンド。

## 背景・目的

- `exercise/` には現状 200 件超の解答があり、ほぼ ABC の特定レター埋め (例 ABC-D) を積み上げている。「どの ABC を / どのレターまでやったか」「最後にいつ触れたか」を振り返る手段が無い。`ls exercise/**/abc*.py` を目で追うしかない。
- `stats` は総数やストリークなどの**集計値**は出すが、コンテスト 1 つ 1 つを列挙はしない。「abc457 は D をやった、abc456 は D と E」といった粒度の一覧は別ビューが要る。
- 集計はローカルのファイルツリーだけで完結する。`stats` と同じく副作用ゼロ・ネットワーク不要の読み取り専用にできる。

### なぜ別サブコマンドか (配置の設計判断)

「`stats` 配下のサブモード」案と「別サブコマンド」案を比較し、**別サブコマンド**に倒した。

| 案 | 利点 | 欠点 |
|---|---|---|
| **A. `stats` のサブモード** (`stats --list` 等) | データ層・期間フラグをそのまま流用。stats の隣で発見しやすい | `stats` の語彙は「集計値」。個々のコンテストの**列挙**は intent が違う。期間 × graph × list でモードが多重化し「何でも屋」化。list 固有フィルタ (カテゴリ・完成度・欠け letter) が stats の語彙から外れる |
| **B. 別サブコマンド (採用)** | 「stats = 数字 / review = 列挙」と責務が明快。list 固有フラグを伸ばす余地。出力を独立設計できる | 新トップレベルコマンドの学習/保守/補完コスト。期間フラグの再配線 |

B の主な欠点 (データ重複) は、`Scan`/`Solve`/`Period` が `internal/stats` に公開済みで**そのまま流用できる**ため実質生じない。出力の性質が「集計」でなく「列挙」で、将来 letter 完成度・未着手の穴・カテゴリ横断と伸びる余地が大きいことを重く見て B を採る。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 集計対象 | `exercise/YYYY/MM/DD/*.py` のみ (1 ファイル = 1 問) | `adt/` など他の日付ツリー |
| カテゴリ指定 | **必須の位置引数** `<category>` (`abc`/`arc`/…) | デフォルト全カテゴリ・複数カテゴリ指定 |
| 単位 | contest_id 単位のロールアップ (1 行 = 1 コンテスト) | task 単位のフラット列挙 |
| 列 | テーブル列 = そのカテゴリで実際に解いた letter の和集合 (昇順) | `--full` で a–g 等の全問セットを出し未着手の穴も表示 |
| 日付 | 各コンテストを**最後に解いた日** (その回の solve の最大日付) | letter ごとの最終日・初回日 |
| 期間フィルタ | (任意) `stats` と同じ `--week/--month/--year/--last` を流用 | `--since`/`--until` の任意範囲 |
| 並び順 | contest 番号の降順 (新しい回が上) | `--sort contest\|date`、昇順切替 |
| 出力 | 人間向けテーブル (ターミナル) | `--json` 機械可読出力 |
| 副作用 | 無し (読み取り専用・オフライン) | — |

### 「練習したコンテスト」の数え方 (境界)

- `stats` と同じく `exercise/<YYYY>/<MM>/<DD>/` 直下の **`.py` ファイル 1 つを 1 問** とみなす (中身は問わない)。
- カテゴリ (`abc`) と問題レター (`d`) はファイル名から導く (`stats` の `classify` と同一規則)。本コマンドではさらに **contest_id (`abc457`)** を導く (先頭英字 + 続く数字)。
- 位置引数 `<category>` に一致する solve だけを対象に、**contest_id でグルーピング**して 1 行にまとめる。
- 同じ contest_id に複数 letter があれば、その行に複数列分の印が立つ (例 abc457 で D と E を解いていれば両方)。
- 日付は `stats` 同様ファイルの**パス**から取る (mtime/git 非依存)。

## ディレクトリ構造 (入力)

```
exercise/
  <YYYY>/<MM>/<DD>/<task>.py     ← task は "<contest_id>_<letter>" (例 abc457_d)
```

- ファイル名 → `category` = 先頭の連続英字を小文字化 (`abc457_d` → `abc`)。
- ファイル名 → `contest_id` = 先頭英字 + 続く数字 (`abc457_d` → `abc457`)。数字が無ければ contest_id = ファイル名先頭の英字 (`scratch` → `scratch`)。
- ファイル名 → `letter` = 最後の `_` 以降を小文字化 (`abc457_d` → `d`)。`_` 無しは `?`。

## CLI 仕様

```
atcoder review <category> [-w|--week | -m|--month | -y|--year | -l|--last <dur>]
```

| 引数 / フラグ | 説明 |
|---|---|
| `<category>` (必須・位置引数) | 列挙するコンテスト種別 (`abc`/`arc`/…)。省略は exit 2 |
| `--week` (`-w`) / `--month` (`-m`) / `--year` (`-y`) / `--last <dur>` (`-l`) | (任意) 解答日でフィルタ。`stats` と同一の排他・文法 (2 つ以上は exit 2)。`stats` の `resolvePeriod`/`Period` を流用 |

### 処理ステップ

1. 位置引数 `<category>` を取得 (無ければ usage を出して exit 2)。
2. 期間フラグを `stats` 同様に解決 (排他違反は exit 2)。
3. `stats.Scan("exercise")` で `[]Solve` を得る (`exercise/` が無ければ空)。
4. 期間窓 + `Category == <category>` で絞る。
5. `contest_id` でグルーピングし、各グループの letter 集合と最終解答日を求める。
6. 出現した letter の和集合を列ヘッダに、contest 番号降順で行を並べてテーブル描画。

### 出力イメージ

現状のように各回 D だけを解いている場合 (列は `d` の 1 列):

```
$ atcoder review abc
exercise abc review — 202 contests, 202 solves

  contest   d   last solved
  abc458    ■   2026-06-09
  abc457    ■   2026-06-08
  abc456    ■   2026-06-07
  …
  abc125    ■   2026-05-16

  202 contests
```

複数レターを解いている場合 (列がレターの和集合に広がる):

```
$ atcoder review abc --month
exercise abc review — this month (2026-06)

  contest   c d e   last solved
  abc458    · ■ ■   2026-06-09
  abc457    · ■ ·   2026-06-08
  abc456    ■ ■ ·   2026-06-07

  3 contests
```

- セルは解いた letter に `■`、その行で未解の (表示列の) letter に `·`。`stats --graph` と濃淡記号を揃える。
- データ 0 件 (そのカテゴリの solve が無い) のときは `no abc solves found in exercise/ (...)` を 1 行出して exit 0 (エラーにしない)。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `<category>` 省略 | usage を出して exit 2 |
| 該当カテゴリの solve が 0 件 | "no <category> solves found" を出して exit 0 |
| 期間フラグ 2 つ以上 | "only one of --week/--month/--year/--last" で exit 2 (`stats` と同文言・同挙動) |
| 同一 contest に複数 letter | 1 行にまとめ、複数列に印を立てる |
| 同一 task_id が複数日 (本来起きないが) | 最終日を採用 (max date) |
| レター不明 (`?`) | `?` 列に集計 (列の末尾) |
| contest_id に数字が無い | ファイル名先頭英字を contest_id とみなして 1 グループ化 |
| 読み取り I/O エラー | エラー表示で exit 1 |

- **読み取り専用**: 解答・キャッシュ・git に一切書き込まない。
- **決定的**: 同じツリー + 同じ「今日」なら出力は一意。`stats` 同様 `Now` を注入可能にしてユニットテストで固定する。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/review.go` | 新規。`cmdReview(args []string) (int, error)`。位置引数 `<category>` 解析・期間フラグ解決 (`stats` の `resolvePeriod` 相当を共有)・`review` パッケージ呼び出し・描画 |
| `cmd/atcoder/main.go` | `case "review"` 追加。`usage()` 文字列更新 |
| `internal/stats/stats.go` | `Solve` に `Contest string` を追加し、`classify`/`Scan` で contest_id を埋める (既存 `stats` の挙動は不変・後方互換) |
| 新規 `internal/review/` | カテゴリ絞り・contest グルーピング・テーブルモデル構築 (純粋関数) + レンダリング |
| `internal/complete/complete.go` | `review` を補完候補に追加。`review` の位置引数にカテゴリ候補 (`abc`/`arc`/…)、フラグに `--week` 等 |
| `fixtures/run.sh` | `review` の smoke (正常 exit 0・カテゴリ省略 exit 2・期間フラグ排他 exit 2・0 件 exit 0) を追加 |
| `internal/review/review_test.go` | グルーピング・列の和集合・最終日・並び順・期間窓のユニットテスト (Now 注入で決定的に) |
| `docs/tools/atcoder-review-usage.md` | 利用手引 (新規) |
| `docs/tools/todo.md` | ロードマップに本項目を記載し本要件へ相互リンク |

### `internal/review/` パッケージの責務 (設計のみ・実装は feature)

```go
package review

import (
    "io"
    "time"

    "github.com/cry999/atcoder-daily-training/internal/stats"
)

// Options は一覧条件。Category は必須。Period/Now は stats と共通の期間窓。
type Options struct {
    Category string
    Period   stats.Period
    Rolling  *stats.Rolling
    Now      time.Time
}

// Row は 1 コンテスト分の行。
type Row struct {
    Contest    string         // contest_id (例 "abc457")
    Letters    map[string]bool // 解いた letter 集合
    LastSolved time.Time       // その回を最後に解いた日
}

// Report は表示に必要な集計済みデータ。
type Report struct {
    Label    string   // "abc review" / "this month (2026-06)" など
    Category string
    Columns  []string // 表示する letter 列 (出現 letter の和集合、昇順、"?" 末尾)
    Rows     []Row    // contest 番号降順
    Contests int      // 行数
    Solves   int      // 対象 solve 総数
}

// Build は Solve 群を Options に従ってカテゴリ絞り・グルーピングする純粋関数。
func Build(solves []stats.Solve, opts Options) Report

// Render は Report を人間向けテーブルとして w に書き出す。
func Render(w io.Writer, r Report) error
```

- データ層 (`Scan`/`Solve`/`Period`/`Rolling`) は `internal/stats` を流用し、`review` は「絞り込み + グルーピング + 描画」だけを担う。`Build` を純粋関数にして `stats.Compute` と同じ流儀でテストする。
- 期間窓の判定ロジック (`inWindow` 相当) は `stats` 側に既にあるが非公開。**設計判断**: 二重実装を避けるため、必要なら `stats` に期間窓判定の公開ヘルパ (例 `stats.InPeriod(date, opts)` か、`resolveWindow` 相当の公開) を切り出して `review` から共有する。詳細な公開 API 形は feature 実装時に確定する。
- レンダリングは `stats` 同様 `lipgloss` で軽く装飾し、非 TTY では素のテキストに落ちる。濃淡記号 `■`/`·` は `stats --graph` と揃える。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 位置引数 `<category>` 無し | usage 表示 | 2 |
| 未知のフラグ | flag パッケージが usage 表示 | 2 |
| 期間フラグ 2 つ以上 | "only one of --week/--month/--year/--last may be set" | 2 |
| `exercise/` 読み取り I/O エラー | エラー表示 | 1 |
| 該当カテゴリ 0 件 | "no <category> solves" 表示 | 0 |
| 正常 | テーブル表示 | 0 |

## 非機能要件

- **副作用ゼロ / 読み取り専用 / オフライン**: `stats` と同じ安全設計。解答ファイル・キャッシュ・git に触れない。ネットワーク・認証不要。
- **既存非破壊**: `Solve` への `Contest` フィールド追加は加算的で、既存 `stats` の出力・挙動は 1 文字も変えない。他サブコマンドも不変。
- **データ層共有**: `Scan`/`Solve`/`Period` を `stats` と共有し、exercise の走査・分類ロジックを二重に持たない。
- **決定的・テスト可能**: `Now` 注入と確定した分類規則で、グルーピング・列・並び順をユニットテストで固定する。
- **exit code 規約**: 引数/フラグ誤り = 2、実行時失敗 = 1、成功 (0 件含む) = 0。fixture で固定する。
- **標準 `flag` 維持**: FW を導入せず標準 `flag` パッケージで実装する。

## 将来の拡張ポイント

- **`--full`**: a–g 等カテゴリの全問セットを列に固定し、**未着手の letter (穴)** を可視化する。ABC-D 埋めの進捗や「あと何問で全埋め」が見える。全問セットの定義 (ABC は回によって a–d/a–f/a–g と異なる) をどう持つかが論点。
- **`--sort contest|date`**: 並び順の切替 (既定は contest 番号降順)。
- **`--json`**: `Report` を機械可読出力。他ツール連携。
- **デフォルト全カテゴリ / 複数カテゴリ**: 位置引数を任意化し、省略時は全カテゴリをカテゴリ別セクションで出す。
- **他ツリー横断**: `adt/` 等の日付ツリーも対象に (日付の持ち方の差異を吸収する layout 的抽象が要る)。

## 用語

- **カテゴリ (category)**: ファイル名先頭の英字で表すコンテスト種別 (`abc`/`arc`/…)。本コマンドの必須位置引数。
- **contest_id**: コンテストの識別子 (`abc457`)。先頭英字 + 数字。グルーピングの単位。
- **contest_num**: contest_id の数字部 (`457`)。並び順のキー。
- **task_id**: 問題の識別子 (`abc457_d`)。1 solve = 1 task_id。
- **letter**: 問題のレター (`a`..`g`)。不明は `?`。
- **最終解答日 (last solved)**: あるコンテストの solve の最大日付。
- (`contest_id` / `task_id` / `letter` は 002 / 005 要件に準拠)

## 関連ドキュメント

- `docs/tools/requirements/005-exercise-stats.md` (集計コマンド `stats`・データ層 `Scan`/`Solve`/`Period` の定義元)
- `docs/tools/requirements/011-stats-graph.md` (`stats --graph`・濃淡記号 `■`/`·` の前例)
- `docs/tools/requirements/002-exercise-abc-layout.md` (`layout` の ID 抽出規則)
- `docs/tools/atcoder-review-usage.md` (利用手引・feature 実装時に作成)
