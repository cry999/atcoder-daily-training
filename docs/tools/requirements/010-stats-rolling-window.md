# `atcoder stats --last` ローリング期間 要件定義

## 概要

`atcoder stats` の期間指定に、**今日から遡る相対窓 (ローリング)** を 1 フラグで切り替えられるようにする。既存の `--week` / `--month` / `--year` は「暦の今週 / 今月 / 今年」(週は月曜始まり・月は同年同月・年は同年) のままにし、新しく `--last <dur>` を足して「今日から N 週間分 / N ヶ月分 / N 年分」を集計できるようにする。`<dur>` は `7d` / `2w` / `1m` / `1y` のように `数値 + 単位` で書き、**数値を省くと `1` 扱い** (`d` = `1d`、`m` = `1m`、`y` = `1y`)。

`docs/tools/todo.md` の一般 TODO 項目 (`atcoder stats` の拡張)。集計対象・読み取り専用・オフラインといった既存の性質はそのまま引き継ぎ、変えるのは「期間窓の決め方」だけ。

## 背景・目的

- 既存の `--week/--month/--year` は**暦境界**で切る。月初・年初の直後は窓が短く、「最近どれくらい練習しているか」を一定の長さで振り返れない (6/1 に `--month` を打つと 1 日分しか出ない)。
- 「ここ 1 週間」「ここ 1 ヶ月」「ここ 1 年」を**常に同じ長さ**で見たいという要望。暦に依存せず今日から遡る窓があると、月初でも年初でも安定して推移を比較できる。
- 任意日付範囲 (`--since`/`--until`) はオーバースペック。打つのが面倒という当初の方針 (005) に沿い、「今日から N 単位分」という短い相対指定だけを足す。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 暦ベース期間 | 既存の `--week/--month/--year` (変更なし) | — |
| ローリング期間 | `--last <dur>`。`dur = (\d*)(d\|w\|m\|y)`、数値省略は 1 | `--since`/`--until` の任意範囲 |
| 単位 | `d` 日 / `w` 週 / `m` 月 / `y` 年 | 時間・四半期など |
| 排他 | `--last` は `--week/--month/--year` と排他 | — |
| 集計対象 | `exercise/YYYY/MM/DD/*.py` のみ (005 と同じ) | 他ツリー横断 |
| 副作用 | 無し (読み取り専用) | — |

## CLI 仕様

```
atcoder stats [-w|--week | -m|--month | -y|--year | -l|--last <dur>]
```

| フラグ | 集計範囲 |
|---|---|
| (なし) | 全期間 (デフォルト) |
| `--week` (`-w`) | 暦の今週 (月曜始まり、今日を含む) |
| `--month` (`-m`) | 暦の今月 (今日と同じ年月) |
| `--year` (`-y`) | 暦の今年 (今日と同じ年) |
| `--last <dur>` (`-l`) | 今日から `<dur>` 分だけ遡るローリング窓 |

### `<dur>` の文法

- 正規表現 `^(\d*)([dwmy])$` (大文字小文字は区別しない、内部で小文字化)。
- `(\d*)` = 件数 `N`。**省略時は `1`**。`0` や負数は不可 (フラグ誤り)。
- `([dwmy])` = 単位。`d`=日 / `w`=週 / `m`=月 / `y`=年。
- 例: `d`→1日, `7d`→7日, `w`→1週, `2w`→2週, `m`→1ヶ月, `3m`→3ヶ月, `y`→1年, `1y`→1年。

### 排他規則

- `--week` / `--month` / `--year` / `--last` のうち **同時に指定できるのは 1 つだけ**。2 つ以上指定したら exit 2 (フラグ誤り)。
- `--last` の値が文法に合わない (`abc`, `1x`, `0d`, 空文字) ときも exit 2。

## 動作仕様 — ローリング窓の定義

ローリング窓は **半開区間 `(start, now]`** とする (今日を必ず含み、ちょうど `dur` 前の日は含めない)。これにより「N 日分」「N ヶ月分」がそれぞれの単位でちょうど 1 周分の長さになる。

`now` は実行日 (ローカル 0 時に丸めた「今日」)。`start` は単位ごとに以下で求め、**集計対象は `start < dayOf(d) <= now`** を満たす解答。

| 単位 | `start` (排他下端) | 含まれる最初の日 (`firstDay`) | 例 (now=2026-06-09, N=1) |
|---|---|---|---|
| `Nd` | `now.AddDate(0, 0, -N)` | `now.AddDate(0, 0, -(N-1))` | 2026-06-09 のみ (1d) / 2026-06-03..09 (7d) |
| `Nw` | `now.AddDate(0, 0, -7N)` | `now.AddDate(0, 0, -(7N-1))` | 2026-06-03..09 (7 日, 1w) |
| `Nm` | `now.AddDate(0, -N, 0)` | `start.AddDate(0, 0, 1)` | 2026-05-10..06-09 (1m) |
| `Ny` | `now.AddDate(-N, 0, 0)` | `start.AddDate(0, 0, 1)` | 2025-06-10..2026-06-09 (1y) |

- ローリング窓は必ず今日を含むので、`current streak` は常に意味を持つ (窓内で途切れていれば 0)。

### 期間と統計のスコープ

- 005 と同じ: 選んだ窓の集合に対して **すべての統計** (解答数・アクティブ日数・ストリーク・カテゴリ別・レター別・時系列) を計算する。

### 時系列の粒度

暦・ローリングを問わず、**窓の日数 (`firstDay`..`now` の inclusive 日数)** で粒度を決める。

| 条件 | 粒度 | 表示範囲 |
|---|---|---|
| 全期間 (`AllTime`) | 週別 | 解答のあった週を新しい順に最大 16 週、超過分は「…and N more week(s)」 |
| 窓日数 ≤ 31 日 | 日別 | `firstDay`〜`now` の各日 (0 件の日も表示) |
| 窓日数 > 31 日 | 週別 | (週別と同じ。例: `--last 1y`, `--last 3m`) |

- 既存の `--week`(7 日) / `--month`(≤31 日) はこの規則で日別になり、挙動は不変。`--year` は週別。
- ローリングでは `--last 7d` / `--last 1m` が日別、`--last 1y` / `--last 3m` が週別になる。

### ラベル

- ローリング窓のラベルは `last N <unit>(s) (firstDay–now)` 形式。
  - `--last 7d` → `last 7 days (2026-06-03–06-09)`
  - `--last 1m` → `last 1 month (2026-05-10–06-09)`
  - `--last 1y` → `last 1 year (2025-06-10–06-09)`
  - `--last 2w` → `last 2 weeks (...)`
- 暦窓のラベルは既存のまま (`this week (...)` / `this month (YYYY-MM)` / `this year (YYYY)` / `all time`)。

### 出力イメージ

```
$ atcoder stats --last 7d
practice stats — last 7 days (2026-06-03–06-09)

  total solves    12
  active days      5
  current streak   3 days
  longest streak   4 days

by category
  abc   10
  arc    2

by day
  2026-06-03  ██ 2
  2026-06-04  ░ 0
  ...
  2026-06-09  ██ 2
```

- データ 0 件のときは "no solves found ..." を 1 行出して exit 0 (005 と同じ)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/stats/stats.go` | `Unit` 型・`Rolling` 構造体・`Options.Rolling` 追加。`Compute` を「窓 (`window`) を一度求めてから集計する」形に整理。窓計算 (`resolveWindow`)・ラベル・粒度判定を暦/ローリング共通化 |
| `cmd/atcoder/stats.go` | `--last`/`-l` フラグ追加。`<dur>` パース (`parseDur`)。排他チェックを 4 値に拡張。`Options.Rolling` を組み立てて `Compute` へ渡す |
| `cmd/atcoder/main.go` | `usage()` の `stats` 行に `-l\|--last <dur>` を追記 |
| `internal/stats/stats_test.go` | ローリング窓 (7d/1w/1m/1y、N 省略、粒度切替) の決定的テストを追加 |
| `fixtures/run.sh` | `stats --last 1m` (exit 0) と `stats --last 0d` / `--week --last 7d` (exit 2) の smoke を追加 |
| `docs/tools/usage/stats.md` | `--last` の表・文法・出力例を追記 |
| `docs/tools/todo.md` | J 項目にローリング期間対応を追記 (DONE) |

### `internal/stats` の追加 API (素描)

```go
// Unit はローリング窓の単位。
type Unit int
const (
    UnitDay Unit = iota
    UnitWeek
    UnitMonth
    UnitYear
)

// Rolling は「今日から N 単位分」のローリング窓指定。
type Rolling struct {
    N    int
    Unit Unit
}

// Options に追加。Rolling が非 nil なら Period より優先。
type Options struct {
    Period  Period
    Rolling *Rolling // 非 nil でローリング窓
    Now     time.Time
}
```

- `Compute` は内部で `window{start, end, daily, label}` を一度求め、フィルタ・粒度・ラベルをそこから駆動する。暦 (`Period`) とローリング (`Rolling`) の差を `resolveWindow` に閉じ込め、ストリーク・内訳・レンダリングのコードは共通のまま。
- フラグのパース (`<dur>` → `Rolling`) は CLI 層 (`cmd/atcoder/stats.go`) の責務。集計層は `Rolling` を受け取るだけで文字列を解釈しない。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 未知のフラグ | flag パッケージが usage 表示 | 2 |
| 期間フラグ 2 つ以上 (`--week --last 7d` 等) | "only one of --week/--month/--year/--last may be set" | 2 |
| `--last` の値が不正 (`0d`, `1x`, `abc`, 空) | "invalid --last value ..." | 2 |
| `exercise/` 読み取り I/O エラー | エラー表示 | 1 |
| データ 0 件 | "no solves" 表示 | 0 |
| 正常 | テーブル表示 | 0 |

## 非機能要件

- **副作用ゼロ / 読み取り専用 / オフライン**: 005 と同じ。窓の決め方を増やすだけで I/O は不変。
- **決定的・テスト可能**: ローリング窓も `Now` 注入で固定し、半開区間の端 (firstDay を含む / start を含まない) と粒度切替 (31 日境界) をユニットテストで網羅。
- **既存非破壊**: `--week/--month/--year` と全期間の挙動・ラベル・粒度は不変。`--last` は純粋な追加。

## 将来の拡張ポイント

- `--since` / `--until`: 任意日付範囲。`window` を直接受け取る形に一般化できる。
- `--json`: `Report` の機械可読出力 (005 から継続)。
- 単位の追加 (四半期 `q` など) や `Nw` 以外の複合表記。

## 用語

- **ローリング窓 (rolling window)**: 今日を右端に固定し、今日から `dur` 分だけ遡る半開区間 `(start, now]`。暦境界に依存しない。
- **暦窓 (calendar window)**: 今週/今月/今年。境界が暦 (週=月曜始まり / 月 / 年) で決まる。
- その他 (solve / active day / streak / カテゴリ / レター) は 005 に準拠。

## 関連ドキュメント

- `docs/tools/requirements/005-exercise-stats.md` (`atcoder stats` の基本仕様)
- `docs/tools/usage/stats.md` (利用手引)
- `docs/tools/todo.md` (上位ロードマップ J 項目)
