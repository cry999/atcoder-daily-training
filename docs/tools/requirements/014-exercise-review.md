# `atcoder review <category>` 練習コンテスト一覧 要件定義

## 概要

`exercise/` で取り組んだコンテストを **カテゴリ単位で一覧** できる読み取り専用サブコマンド `atcoder review <category>` を足す。`atcoder review abc` で「これまで練習した ABC を contest × letter のテーブルで並べ、各コンテストを最後に解いた日付を添える」。**ABC は a–g を固定列**にして「どの回のどのレターを埋めたか・どこに穴があるか」を一望でき、**各マスは色の濃淡で「最近解いたか / 古いか (recency)」**を表す。どの回のどの問題に取り組んだか・どこまで埋めたか・最近のリズムを 1 画面で振り返れるようにする。

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
| 集計対象 | **`exercise/YYYY/MM/DD/*.py` (日付あり) + `<category>/<num>/<letter>.py` のカテゴリツリー (日付なし)** を横断 | `adt/` など他の日付ツリー |
| カテゴリ指定 | **必須の位置引数** `<category>` (`abc`/`arc`/`awc`/…)。`exercise/` の同カテゴリ solve と `<category>/` ツリーの両方を読む | デフォルト全カテゴリ・複数カテゴリ指定 |
| 単位 | contest_id 単位のロールアップ (1 行 = 1 コンテスト)。両ツリーを contest_id でマージ | task 単位のフラット列挙 |
| 列 | **ABC は a–g を固定列** (未着手の穴も `·` で見える)。それ以外のカテゴリは実際に解いた letter の和集合 (昇順) | 他カテゴリ (arc/agc/ahc) の全問セット定義を持って固定列化 |
| マスの濃淡 | 解いたマス `■` を**色の濃淡で recency 表現** (最近=明るい緑・古い=暗い緑)。**日付なし (カテゴリツリー由来) は中立色の `■`**、未解は `·` | カテゴリツリーにも日付源 (git 等) を与えて recency 着色 |
| 日付 | 各コンテストを**最後に解いた日** (その回の dated solve の最大日付) を行末に表示。日付が一切無い回は `—` | letter ごとの最終日・初回日 |
| 期間フィルタ | (任意) `stats` と同じ `--week/--month/--year/--last` を流用 | `--since`/`--until` の任意範囲 |
| 並び順 | contest 番号の降順 (新しい回が上) | `--sort contest\|date`、昇順切替 |
| 出力 | 人間向けテーブル (ターミナル) | `--json` 機械可読出力 |
| 副作用 | 無し (読み取り専用・オフライン) | — |

### 「練習したコンテスト」の数え方 (境界)

- **2 つのツリーを横断**して 1 問 = `.py` 1 ファイルと数える (中身は問わない):
  - `exercise/<YYYY>/<MM>/<DD>/<contest>_<letter>.py` — **日付あり** (パス由来)。`stats` と同じデータ。
  - `<category>/<num>/<letter>.py` — **日付なし**。練習問題を 1 問 1 ファイルで置くカテゴリツリー (`abc/447/d.py` 等)。位置引数の `<category>` ディレクトリのみ読む。
- どちらも **contest_id** (`abc447`) と **letter** (`d`) を導き、`<category>` に一致する solve を **contest_id でマージ**して 1 行にまとめる。同じ contest_id に複数 letter があれば複数列に印が立つ。
- **重複の解決**: 同じ (contest_id, letter) が両ツリーにあれば **日付ありを優先**する (exercise の日付で recency 着色)。実際には exercise (旧 D 埋め) とカテゴリツリー (新しい回) はほぼ範囲が分離しており重複は稀。
- **列の決め方**: カテゴリが `abc` のときは **a–g を固定列**にする (解いていない letter も列として出し、`·` で穴を見せる)。その他のカテゴリは「実際に解いた letter の和集合」を列にする (回ごとに問題数が異なり全問セットが一定でないため)。どちらの場合も、固定列に無い letter を解いていれば追加列として末尾に足す (`?` は最末尾)。
- **マスの濃淡 (recency)**: 日付のある solve は経過日数で色の濃淡を変える (最近=明るい緑、古い=暗い緑)。**日付のない (カテゴリツリー由来) solve は中立色の `■`** にして「解いたが日付不明」を表す。未解のマスは `·`。
- 日付は `exercise/` のみパスから取る (mtime/git 非依存)。カテゴリツリーには日付が無いので recency も last solved も持たない (案 A: 分かることだけ正直に出す)。recency は「今日 (`Now`)」基準で決まり、`Now` 注入で決定的にできる。

### recency (濃淡) の決め方

各マスの色は、その問題を解いた日から「今日 (`Now`)」までの経過日数を**固定しきい値**で 4 段階に分類して決める (`stats --graph` のレベルと同じ緑ランプを流用、暗い緑 = 古い → 明るい緑 = 新しい)。しきい値は固定でデータに依存しないため決定的。

| 経過日数 (now − solved) | レベル | 色 (TTY) | 意味 |
|---|---|---|---|
| ≤ 7 日 | 4 | 最も明るい緑 (`#39d353`) | ごく最近 |
| ≤ 30 日 | 3 | 明るい緑 (`#26a641`) | この 1 ヶ月 |
| ≤ 90 日 | 2 | 緑 (`#006d32`) | この四半期 |
| 90 日超 | 1 | 暗い緑 (`#0e4429`) | それ以前 (古い) |
| (日付なし) | — | 中立色 `■` (`#9399b2`) | カテゴリツリー由来。解いたが日付不明 |
| (未解) | — | 薄灰 `·` | そのマスは未着手 |

- 解いたマスは経過日数に関わらず**塗られた `■`** にして、薄灰の `·` (未解) と文字レベルで区別する。recency は色だけで表すので、`stats --graph` 同様 **非 TTY (パイプ/テスト) では recency の段階・日付有無は潰れる** (が、行末の「最終解答日」列が日付の有無を文字で残す: 日付なしは `—`)。
- 緑ランプ・記号 (`■`/`·`) は `stats --graph` と揃える。日付なしの中立 `■` は recency の緑とも未解 `·` とも別の色にして 3 状態 (recency あり / 日付なし / 未解) を見分けられるようにする。

## ディレクトリ構造 (入力)

```
exercise/                          ← 日付あり (パス由来)
  <YYYY>/<MM>/<DD>/<task>.py       ← task は "<contest_id>_<letter>" (例 abc457_d)
<category>/                        ← 日付なし (位置引数のカテゴリのみ)
  <num>/<letter>.py                ← 例 abc/447/d.py。contest_id = category + num
```

- **exercise** のファイル名 → `category` = 先頭英字、`contest_id` = 先頭英字 + 数字 (`abc457_d` → `abc457`)、`letter` = 最後の `_` 以降 (`d`)。`stats` の `classify` と同一規則。
- **カテゴリツリー** (`<category>/<num>/<letter>.py`) → `contest_id` = `<category>` + `<num>` (`abc` + `447` = `abc447`)、`letter` = ファイル名の拡張子を除いた stem (`d.py` → `d`)。`<num>` が数字でない dir はスキップ。
  - letter は **1〜2 文字の英小文字** (`a`..`g`, 稀に `ex` 等) のみ採用する。`generate_d_testcase.py` のような補助スクリプトは letter 形でないため無視する。
  - カテゴリツリーの solve は**日付を持たない** (`Date` ゼロ値)。

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
3. `stats.Scan("exercise")` (日付あり) と `review.ScanCategoryTree(<category>)` (`<category>/<num>/<letter>.py`、日付なし) を読み、`[]Solve` を結合する (どちらも無ければ空)。
4. 期間窓 + `Category == <category>` で絞る。**日付なし solve は期間フィルタ指定時 (`--week` 等) には窓に入らないので除外され、全期間のときのみ含まれる**。
5. `contest_id` でグルーピングし、(contest, letter) ごとに最良の日付 (日付ありを優先・複数なら最大) と、回ごとの最終解答日 (dated のみ) を求める。
6. 列ヘッダを決める (`abc` は a–g 固定 + 範囲外で解いた letter を末尾追加、その他は解いた letter の和集合)。contest 番号降順で行を並べ、各マスを recency / 日付なし / 未解で着色してテーブル描画。

### 出力イメージ

ABC は a–g を固定列にするので、D だけ埋めていれば a/b/c/e/f/g は `·` (穴) として並ぶ。日付のある exercise 由来のマスは recency (最近=明・古=暗) で着色:

```
$ atcoder review abc --year
exercise abc review — this year (2026)

  contest   a b c d e f g   last solved
  abc331    · · · ■ · · ·   2026-06-09   (■ = 明るい緑 / 最近)
  abc330    · · · ■ · · ·   2026-06-08
  …
  abc257    · · · ■ · · ·   2026-05-16   (■ = 暗い緑 / 古い)

  older ■ ■ ■ ■ newer   ■=日付なし   ·=未着手
  75 contests
```

カテゴリツリー (`abc/<num>/<letter>.py`) は日付が無いので、その回は a–f に幅広く `■` が立ち、last solved は `—` になる (`■` は中立色):

```
$ atcoder review abc
exercise abc review — 237 contests, 387 solves

  contest   a b c d e f g   last solved
  abc461    ■ ■ ■ ■ ■ ■ ·   —            (abc/ 由来 = 日付なし・中立色)
  abc458    ■ ■ ■ ■ ■ · ·   —
  …
  abc331    · · · ■ · · ·   2026-06-09   (exercise 由来 = recency 着色)
  …
  abc125    · · · ■ · · ·   2026-05-16

  older ■ ■ ■ ■ newer   ■=日付なし   ·=未着手
  237 contests
```

- 解いたマスは `■`、未解のマスは `·`。日付のある solve は recency の緑で着色、日付のない (カテゴリツリー) solve は中立色の `■`。記号・緑ランプは `stats --graph` と揃える (上の例は色を出せないため一様に見える)。
- ABC 以外のカテゴリ (例 `atcoder review arc`) は固定列を持たず、実際に解いた letter の和集合だけを列にする。
- 期間フィルタ (`--month` 等) を付けると**日付なしの solve は除外**され、exercise の dated solve だけが対象になる。
- データ 0 件 (そのカテゴリの solve が両ツリーとも無い) のときは `no abc solves found in exercise/ (...)` を 1 行出して exit 0 (エラーにしない)。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `<category>` 省略 | usage を出して exit 2 |
| 該当カテゴリの solve が両ツリーとも 0 件 | "no <category> solves found" を出して exit 0 |
| 期間フラグ 2 つ以上 | "only one of --week/--month/--year/--last" で exit 2 (`stats` と同文言・同挙動) |
| カテゴリが `abc` | 列を a–g に固定 (未解は `·`)。a–g 外の letter を解いていれば末尾に追加列 |
| カテゴリが `abc` 以外 | 固定列なし。実際に解いた letter の和集合を列にする |
| 同一 contest に複数 letter | 1 行にまとめ、複数列に `■` を立てる |
| 同一 (contest, letter) が両ツリー | 日付ありを優先 (recency 着色)。日付なしで上書きしない |
| カテゴリツリー由来 (日付なし) | マスは中立色の `■`、last solved は `—`。期間フィルタ時は除外 |
| マスの着色 | dated は経過日数で `■` を 4 段階の緑、undated は中立 `■`。非 TTY では色が潰れる |
| レター不明 (`?`) | `?` 列に集計 (列の末尾) |
| カテゴリツリーの非 letter ファイル | `generate_d_testcase.py` 等 (letter 形でない) は無視 |
| 読み取り I/O エラー | エラー表示で exit 1 |

- **読み取り専用**: 解答・キャッシュ・git に一切書き込まない。
- **決定的**: 同じツリー + 同じ「今日」なら出力は一意。`stats` 同様 `Now` を注入可能にしてユニットテストで固定する。日付なし solve は `Now` に依存しない。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/review.go` | `stats.Scan("exercise")` に加え `review.ScanCategoryTree(<category>)` を読んで結合してから `Build` に渡す |
| `internal/review/scan.go` (新規) | `ScanCategoryTree(category string) ([]stats.Solve, error)` — `<category>/<num>/<letter>.py` を日付なし solve として列挙 |
| `internal/review/review.go` | `Build` のマージで (contest, letter) ごとに日付ありを優先・undated を保持。期間フィルタは `stats.InWindow` がゼロ日付を全期間のみ通すのを利用 |
| `internal/review/render.go` / `tui.go` | undated マスを中立色 `■`、last solved が無ければ `—`。凡例に `■=日付なし` を追加 |
| `internal/review/*_test.go` | カテゴリツリー走査・マージ (日付優先)・undated 描画・期間除外のテストを追加 |
| `fixtures/run.sh` | カテゴリツリーを stage した `review` の smoke を追加 |
| `docs/tools/atcoder-review-usage.md` | 集計対象 (2 ツリー)・undated の見方を追記 |

> 既存実装からの差分のみ記載 (`review` 本体・`stats.Solve.Contest`・補完・usage は実装済み)。

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
    Contest    string               // contest_id (例 "abc457")
    Solved     map[string]time.Time // letter → 解いた日。ゼロ値 = 解いたが日付なし (カテゴリツリー由来)。未解の letter は不在
    LastSolved time.Time            // その回を最後に解いた日 (dated のみ・全部 undated ならゼロ → "—")
}

// ScanCategoryTree は <category>/<num>/<letter>.py を日付なし solve (Date ゼロ) として列挙する。
func ScanCategoryTree(category string) ([]stats.Solve, error)

// Report は表示に必要な集計済みデータ。
type Report struct {
    Label    string   // "abc review" / "this month (2026-06)" など
    Category string
    Columns  []string // 表示する letter 列 (abc は a–g 固定 + 範囲外 letter を末尾、他は和集合昇順、"?" 末尾)
    Rows     []Row    // contest 番号降順
    Contests int      // 行数
    Solves   int      // 対象 solve 総数
}

// Build は Solve 群を Options に従ってカテゴリ絞り・グルーピングする純粋関数。
// Columns の決定 (abc 固定 a–g) もここで行う。
func Build(solves []stats.Solve, opts Options) Report

// recencyLevel は解答日と now の経過日数を 0..4 のレベルに分類する (固定しきい値)。
// 0 は未解 (· 用)、1..4 が古い→新しい。Render が色を引くのに使う。
func recencyLevel(solved, now time.Time) int

// Render は Report を人間向けテーブルとして w に書き出す。マスは recencyLevel で着色。
func Render(w io.Writer, r Report) error
```

- データ層 (`Scan`/`Solve`/`Period`/`Rolling`) は `internal/stats` を流用し、`review` は「絞り込み + グルーピング + 描画」だけを担う。`Build` / `recencyLevel` を純粋関数にして `stats.Compute` と同じ流儀でテストする。
- recency の色ランプは `stats --graph` の `grassStyles` (緑 4 段階 + 薄灰) を流用する。**設計判断**: 二重定義を避けるため、`stats` 側の色ランプを `review` から参照できるよう公開するか、共通の小パッケージに切り出すかは feature 実装時に決める (記号 `■`/`·` と色は両コマンドで一致させる)。
- 期間窓の判定ロジック (`inWindow` 相当) は `stats` 側に既にあるが非公開。**設計判断**: 二重実装を避けるため、必要なら `stats` に期間窓判定の公開ヘルパ (例 `stats.InPeriod(date, opts)` か、`resolveWindow` 相当の公開) を切り出して `review` から共有する。詳細な公開 API 形は feature 実装時に確定する。
- レンダリングは `stats` 同様 `lipgloss` で軽く装飾し、非 TTY では素のテキストに落ちる (recency の色は消えるが、行末の最終解答日で補える)。

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
- **決定的・テスト可能**: `Now` 注入と固定しきい値で、グルーピング・列 (abc 固定 a–g)・並び順・recency レベルをユニットテストで固定する。
- **色に依存しすぎない**: 解いた/未解は `■`/`·` の文字で表し、recency の段階だけ色に載せる。非 TTY では recency は潰れるが、最終解答日列が主信号を文字で残す (`stats --graph` と同方針)。
- **exit code 規約**: 引数/フラグ誤り = 2、実行時失敗 = 1、成功 (0 件含む) = 0。fixture で固定する。
- **標準 `flag` 維持**: FW を導入せず標準 `flag` パッケージで実装する。

## 将来の拡張ポイント

- **他カテゴリの固定列**: ABC の a–g 固定を arc/agc/ahc 等にも広げる。回によって問題数が異なるカテゴリの「全問セット」をどう定義・保持するかが論点 (当面 ABC のみ固定)。
- **相対 recency スケール**: 固定しきい値 (7/30/90 日) でなく、表示集合の日付レンジを分位数で 4 段階に割る相対スケール。練習履歴が短い/長いどちらでも段階が均等に出る。
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
- **最終解答日 (last solved)**: あるコンテストの dated solve の最大日付。行末に表示。日付が一切無ければ `—`。
- **カテゴリツリー**: `<category>/<num>/<letter>.py` 形式の解答ツリー (`abc/`, `arc/`, `awc/` …)。日付を持たない。
- **日付なし solve (undated)**: カテゴリツリー由来の solve。`Date` ゼロ値。recency 着色されず中立色の `■` で描かれ、期間フィルタ時は除外される。
- **固定列 (fixed columns)**: カテゴリに対して常に表示する letter 列。ABC は a–g。未解の列は `·` で穴として見える。
- **recency (濃淡)**: 各マスを「解いた日から今日までの経過日数」で 4 段階に着色したもの。最近=明るい緑、古い=暗い緑。`stats --graph` の色ランプを流用。
- (`contest_id` / `task_id` / `letter` は 002 / 005 要件に準拠)

## 関連ドキュメント

- `docs/tools/requirements/005-exercise-stats.md` (集計コマンド `stats`・データ層 `Scan`/`Solve`/`Period` の定義元)
- `docs/tools/requirements/011-stats-graph.md` (`stats --graph`・濃淡記号 `■`/`·` の前例)
- `docs/tools/requirements/002-exercise-abc-layout.md` (`layout` の ID 抽出規則)
- `docs/tools/atcoder-review-usage.md` (利用手引・feature 実装時に作成)
