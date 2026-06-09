# `atcoder stats` 日々の練習統計 要件定義

## 概要

日々の練習 (`exercise/YYYY/MM/DD/<task>.py`) の積み上がりを **1 コマンド** で振り返れるようにする。`atcoder stats` で「これまで何問解いたか・連続して練習できているか・どのコンテスト/レターに偏っているか・最近の推移」を 1 画面のテーブルで出す。`--week` / `--month` / `--year` で「今週 / 今月 / 今年」に手軽に絞れる。

`docs/tools/todo.md` の一般 TODO 項目。既存の fetch / cache / 本番対応とは独立した、純粋にローカルのファイルツリーを集計する読み取り専用コマンド。

## 背景・目的

- 練習は毎日 `exercise/YYYY/MM/DD/` にファイルを足して積み上げているが、「どれくらい続けられているか」「どの種類の問題に偏っているか」を振り返る手段が無い。`find | wc -l` を都度叩くしかない。
- モチベーション維持にはストリーク (連続練習日数) と最近の推移が効く。これを 1 コマンドで可視化したい。
- 集計はローカルのディレクトリ構造だけで完結する。ネットワーク・認証・キャッシュは一切不要で、副作用ゼロの読み取り専用にできる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 集計対象 | `exercise/YYYY/MM/DD/*.py` のみ (1 ファイル = 1 問) | `adt/` など他の日付ツリー、`abc/`/`dp/` 等のカテゴリツリー |
| 日付の出所 | パス上の `YYYY/MM/DD` ディレクトリ | ファイル mtime / git commit 日 |
| 統計 | 解答数・アクティブ日数・ストリーク・カテゴリ別 (コンテスト種別 / 問題レター)・時系列 | 難易度別・AC/WA 等の結果別・目標との比較 |
| 期間指定 | `--week` / `--month` / `--year` の相対 3 種 + デフォルト全期間 | `--since` / `--until` の任意範囲、月次レポート |
| 出力 | 人間向けテーブル (ターミナル) | `--json` 機械可読出力 |
| 副作用 | 無し (読み取り専用) | — |

### 「解いた問題」の数え方 (境界)

- `exercise/<YYYY>/<MM>/<DD>/` 直下の **`.py` ファイル 1 つを 1 問** として数える。中身 (AC したか) は問わない。練習ツリーは「その日に取り組んだ問題を置く場所」なので、ファイルの存在をそのまま「練習した」とみなす。
- 日付はファイルの**パス**から取る (`exercise/2026/06/09/abc457_d.py` → 2026-06-09)。mtime や git には依存しない (ファイルを後で触っても集計がぶれない)。
- `exercise/` 以外のツリー (`abc/`, `adt/`, `dp/` …) は今回は対象外。日付の持ち方がツリーごとに違い、横断集計の設計は別途必要なため、まずは日付がパスに明示される `exercise/` に限定する。

## ディレクトリ構造 (入力)

```
exercise/
  <YYYY>/
    <MM>/
      <DD>/
        <task>.py        ← 1 ファイル = 1 問。task は通常 "<contest>_<letter>" (例 abc457_d)
```

- ファイル名から **カテゴリ (コンテスト種別)** と **問題レター** を導出する:
  - カテゴリ = ファイル名 (拡張子除く) 先頭の連続する英字を小文字化したもの。`abc457_d` → `abc`、`arc180_c` → `arc`。先頭が英字でない / 判別不能なら `other`。
  - 問題レター = ファイル名に `_` があればその**最後の** `_` 以降を小文字化したもの。`abc457_d` → `d`。`_` が無ければ不明 (`?`) 扱い。
- `YYYY`/`MM`/`DD` が数値として妥当でないディレクトリ、`.py` 以外のファイルは無視する (集計から除外、エラーにはしない)。

## CLI 仕様

```
atcoder stats [-w | --week | -m | --month | -y | --year]
```

| フラグ | 説明 |
|---|---|
| (なし) | 全期間を集計 (デフォルト) |
| `--week` (`-w`) | 今週 (月曜始まり、今日を含む週) に絞る |
| `--month` (`-m`) | 今月 (今日と同じ年月) に絞る |
| `--year` (`-y`) | 今年 (今日と同じ年) に絞る |

- 各期間フラグには 1 文字の短縮形 (`-w` / `-m` / `-y`) がある。短縮形と長形は同一フラグで、挙動は変わらない。
- `--week` / `--month` / `--year` (短縮形含む) は **排他**。2 つ以上指定したら exit 2 (フラグ誤り)。長形と短縮形の混在 (例 `-w --month`) も 2 指定とみなす。
- 期間は常に「今日」基準の相対指定。任意の日付範囲指定 (`--since` 等) は将来の拡張に回す (細かい日付を打つのが面倒、という要望に沿う)。

### 期間と統計のスコープ

- 選んだ期間 (デフォルトは全期間) の集合に対して **すべての統計**を計算する。`--month` ならその月のファイルだけを母集合にし、解答数・アクティブ日数・カテゴリ別・時系列・ストリークをすべてその窓内で出す。
- 相対期間 (今週/今月/今年) は必ず今日を含むので、「現在のストリーク」は常に意味を持つ (窓の途中で途切れている場合は 0)。

### 統計項目

| 項目 | 定義 |
|---|---|
| total solves | 期間内の `.py` ファイル総数 |
| active days | 期間内で 1 問以上解いた日数 (日付の異なり数) |
| current streak | 今日から遡って連続して解いた日数。今日未着手でも前日まで続いていれば前日起点で数える (途切れていれば 0) |
| longest streak | 期間内で連続して解いた日数の最大 |
| by category | コンテスト種別 (`abc`/`arc`/…/`other`) ごとの解答数。多い順、同数はキー名昇順 |
| by letter | 問題レター (`a`..`g`/`?`) ごとの解答数。レター昇順 (`?` は末尾) |
| time series | 期間に応じた粒度での解答数推移。簡易バー付き |

### 時系列の粒度

| 期間 | 粒度 | 表示範囲 |
|---|---|---|
| `--week` | 日別 | 今週の月曜〜今日の各日 (0 件の日も表示) |
| `--month` | 日別 | 今月 1 日〜今日の各日 (0 件の日も表示) |
| `--year` / 全期間 | 週別 | 解答のあった週 (月曜始まり) を新しい順に最大 16 週。超過分は「…と他 N 週」を表示 (黙って切り捨てない) |

### 出力イメージ

```
$ atcoder stats --month
practice stats — this month (2026-06)

  total solves      12
  active days        5
  current streak     3 days
  longest streak     4 days

by category
  abc   10
  arc    2

by letter
  a    1
  d    8
  e    3

by day
  2026-06-05  ██ 2
  2026-06-06  █ 1
  2026-06-07  ░ 0
  2026-06-08  ███ 3
  2026-06-09  ██ 2
```

- データが 0 件のときは "no solves found in exercise/ (...)" を 1 行出して exit 0 (エラーにしない)。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `exercise/` が存在しない | 0 件として扱い、"no solves" を出して exit 0 |
| 妥当でない日付 dir / 非 `.py` ファイル | 無視して集計を継続 |
| 期間フラグ無し | 全期間集計 (週別時系列) |
| 期間フラグ 2 つ以上 | "only one of --week/--month/--year" で exit 2 |
| ファイル名がレター不明 (`_` 無し) | カテゴリは先頭英字で分類、レターは `?` バケットに集計 |
| 読み取り I/O エラー (権限等) | エラー表示で exit 1 |

- **読み取り専用**: 解答ファイル・キャッシュ・その他リポジトリ内容に一切書き込まない。
- **決定的**: 同じツリー + 同じ「今日」なら出力は一意。`time.Now()` は注入可能にし (`stats.Options.Now`)、ユニットテストで固定する。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/stats.go` | 新規。`cmdStats(args []string) (int, error)`。フラグ解析・期間決定・`stats` パッケージ呼び出し・レンダリング呼び出し |
| `cmd/atcoder/main.go` | `case "stats"` 追加。`usage()` 文字列更新 |
| 新規 `internal/stats/` | 集計ロジック (純粋関数) + テーブルレンダリング |
| `fixtures/run.sh` | `stats` の smoke (exit 0 / 排他フラグ exit 2) を追加 |
| `internal/stats/stats_test.go` | 集計ロジックのユニットテスト (Now 注入で決定的に) |
| `docs/tools/atcoder-stats-usage.md` | 利用手引 (新規) |
| `docs/tools/todo.md` | ロードマップに本項目を ✅ DONE で記載 |

### 新規 `internal/stats/` パッケージの責務

```go
package stats

// Solve は 1 ファイル = 1 問の集計単位。
type Solve struct {
    Date     time.Time // パス由来の解答日 (ローカル 0 時)
    File     string    // ベース名 (例 "abc457_d.py")
    Category string    // コンテスト種別 ("abc"/"arc"/…/"other")
    Letter   string    // 問題レター ("a".."g") / 不明は "?"
}

// Period は集計窓。
type Period int
const (
    AllTime Period = iota
    ThisWeek
    ThisMonth
    ThisYear
)

// Scan は root (通常 "exercise") 配下の YYYY/MM/DD/*.py を列挙して Solve に変換する。
// root が無ければ空スライスを返す (エラーにしない)。
func Scan(root string) ([]Solve, error)

// Options は集計条件。Now がゼロ値なら time.Now().Local() を使う。
type Options struct {
    Period Period
    Now    time.Time
}

// Report は表示に必要な集計済みデータ。
type Report struct {
    Label         string  // "all time" / "this month (2026-06)" など
    Total         int
    ActiveDays    int
    CurrentStreak int
    LongestStreak int
    Categories    []Count // 多い順
    Letters       []Count // レター昇順
    Series        []Bucket
    SeriesKind    string  // "day" / "week"
    SeriesOmitted int     // 週別で切り捨てた古い週数
}
type Count struct  { Key string; N int }
type Bucket struct { Label string; N int }

// Compute は Solve 群を Options に従って集計する純粋関数。
func Compute(solves []Solve, opts Options) Report

// Render は Report を人間向けテーブルとして w に書き出す。
func Render(w io.Writer, r Report) error
```

- `Scan` / `Compute` は I/O とロジックを分離し、`Compute` を純粋関数にしてユニットテストしやすくする (`layout` パッケージの `Detect` / `Letter` と同じ流儀)。
- カテゴリ / レター抽出は `internal/layout` の `Letter` を流用しつつ、`_` の有無で `?` 分類を加える。
- レンダリングは `lipgloss` で軽く装飾するが、非 TTY (パイプ / テスト) では自動で素のテキストに落ちる。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 未知のフラグ | flag パッケージが usage 表示 | 2 |
| 期間フラグ 2 つ以上 | "only one of --week/--month/--year may be set" | 2 |
| `exercise/` 読み取り I/O エラー | エラー表示 | 1 |
| データ 0 件 | "no solves" 表示 | 0 |
| 正常 | テーブル表示 | 0 |

## 非機能要件

- **副作用ゼロ / 読み取り専用**: いかなる書き込みもしない。解答ファイルを壊さない repo の安全設計に沿う。
- **決定的・テスト可能**: `Now` 注入で固定し、`Compute` をユニットテストで網羅 (集計・ストリーク・期間窓・カテゴリ/レター分類)。
- **オフライン**: ネットワーク・認証・キャッシュに一切触れない。
- **既存非破壊**: 既存サブコマンド (`new`/`test`/`run`/`commit`/`submit`) の挙動は不変。`stats` は独立した読み取り専用の追加。
- **黙って切り捨てない**: 週別時系列で上限を超えた分は「…と他 N 週」と明示する。

## 将来の拡張ポイント

- **`--since` / `--until`**: 任意日付範囲。`Period` を範囲指定に一般化する。
- **`--json`**: `Report` をそのまま JSON 出力 (機械可読・他ツール連携)。
- **他ツリー横断**: `adt/` の日付ツリーや、`abc/`/`dp/` 等のカテゴリツリーも対象に。日付の持ち方の差異を吸収する layout 的な抽象が要る。
- **難易度 / 結果別**: AtCoder の難易度や AC/WA を取り込んだ集計 (要 fetch / 提出履歴連携)。

## 用語

- **集計単位 (solve)**: `exercise/YYYY/MM/DD/` 直下の `.py` ファイル 1 つ。
- **アクティブ日 (active day)**: 1 問以上解いた日。
- **ストリーク (streak)**: 連続したアクティブ日の並び。current = 今日 (or 前日) 起点で遡れる長さ、longest = 期間内最大。
- **カテゴリ**: ファイル名先頭の英字で表すコンテスト種別 (`abc`/`arc`/…/`other`)。
- **レター**: 問題の識別子 (`a`..`g`)。不明は `?`。
- (`contest_id` / `task_id` / `letter` は MVP A 要件定義に準拠)

## 関連ドキュメント

- `docs/tools/todo.md` (上位ロードマップ。本項目を記載)
- `docs/tools/requirements/002-exercise-abc-layout.md` (`layout.Letter` 等 ID 抽出の定義元)
- `docs/tools/atcoder-stats-usage.md` (利用手引)
