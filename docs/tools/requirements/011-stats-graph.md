# `atcoder stats --graph` 草表示 (contribution graph) 要件定義

## 概要

`atcoder stats` に **GitHub の contribution graph 風の草表示** (`--graph` / `-g`) を足す。曜日×週の 2 次元グリッドで「いつ・どれくらい練習したか」を一望できるようにする。各マスの濃淡 (レベル 0〜4) は、その日に解いた問題を **問題レターの重み付きで合計したスコア** から決める。難問 (`g`) 1 問が易問 (`a`) 数問より濃くなるよう、量だけでなく「質 (レベル)」を反映する。

既存の `stats` と同じく **読み取り専用・完全オフライン**。レベルは AtCoder の difficulty を fetch せず、ファイル名のレター (`abc457_d.py` → `d`) だけからローカルに導く。`--week` / `--month` / `--year` / 全期間の期間窓にグリッドの範囲を追従させる。

> 関連: `docs/tools/requirements/005-exercise-stats.md` (stats 本体の要件)。本書はその拡張。

## 背景・目的

- 既存 `stats` の時系列は「by day」「by week」の 1 次元バーで、長い期間を俯瞰しづらい。GitHub の草のような 2 次元グリッドなら、数ヶ月〜1 年の練習リズム (曜日の偏り・空白期間・盛り上がり) を 1 画面で掴める。
- 単純な「解いた問題数」だけだと、`a` を 5 問埋めた日と `f`/`g` を 1 問通した日が同じ濃さになり、練習の「重さ」が見えない。**レター = 難易度の代理指標** として重み付けし、濃淡に反映したい。
- レベルの出所をローカル (ファイル名レター) に限ることで、`stats` の「副作用ゼロ・ネットワーク不要」という設計を一切崩さずに実現できる。実 difficulty (要 fetch) は将来の拡張に回す。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 表示切替 | `--graph` / `-g` フラグで草表示に切替 | 常時表示・`--json` でグリッドも出力 |
| レベルの出所 | 問題レター (`a`=1 … `z`=26、`?`=1) のローカル重み | AtCoder difficulty を fetch して使う `--difficulty` |
| 濃淡の計算 | その日の Σ(レター重み) を固定しきい値でレベル 0〜4 に分類 | しきい値のユーザ設定、相対 (分位数) スケール |
| グリッド範囲 | 期間フラグに追従 (`--week`/`--month`/`--year`/全期間) | `--since`/`--until` の任意範囲 |
| レイアウト | 曜日 (Mon..Sun) = 行、週 (月曜始まり) = 列。最大 53 週 | 列幅・配色テーマの選択 |
| 副作用 | 無し (読み取り専用・オフライン) | — |

### レベル (難易度) の数え方 (境界)

- レベルは **問題レターのみ**から導く。`abc457_d.py` のレター `d` → 重み 4。fetch も提出履歴参照もしない。
- レター重み `letterWeight`:
  - レターが `?` (不明、ファイル名に `_` 無し) なら **1**。
  - それ以外はレター先頭 1 文字を見て `a`→1, `b`→2, …, `z`→26。先頭が英小文字でなければ **1**。
  - 複数文字レター (`abc457_ex.py` → `ex` 等、稀) は先頭文字のみ採用 (`e`→5)。
- 1 日のスコア = その日の全 solve の `letterWeight` の総和。例: ある日に `a`(1) + `d`(4) + `g`(7) を解いたら score = 12。
- スコア → 濃淡レベル (固定しきい値、`shadeLevel`):

  | score | level | 意味 |
  |---|---|---|
  | 0 | 0 | 練習なし (空マス) |
  | 1–3 | 1 | 軽め |
  | 4–7 | 2 | 標準 |
  | 8–12 | 3 | 重め |
  | 13+ | 4 | 濃い |

  しきい値は固定 (データに依存しない)。同じツリー + 同じ「今日」なら濃淡は一意に決まる (決定的)。

## CLI 仕様

```
atcoder stats [-w|--week | -m|--month | -y|--year] [-g|--graph]
```

| フラグ | 説明 |
|---|---|
| `--graph` (`-g`) | 時系列を GitHub 風の草グリッドで表示する。サマリ・カテゴリ別・レター別はそのまま |
| `--week`/`--month`/`--year` | グリッドの範囲を決める (下表)。`--graph` と併用可。期間フラグ同士は従来どおり排他 (exit 2) |

- `--graph` 単独 (期間フラグ無し) は **全期間** をグリッド化 (最大 53 週、超過分は古い週から省略)。
- `--graph` を付けないときの挙動 (バー時系列) は**完全に従来どおり**で不変。

### グリッドの範囲 (期間フラグ追従)

| 期間 | グリッドが覆う範囲 | 列 (週) 数の目安 |
|---|---|---|
| `--week` | 今週の月曜〜日曜 | 1 列 |
| `--month` | 今月 1 日〜今日 (週境界に整列) | 4〜6 列 |
| `--year` | 今年 1/1〜今日 (週境界に整列) | 最大 53 列 |
| 全期間 | 最初に解いた日〜今日 (週境界に整列) | 最大 53 列。超過分は古い週から省略 |

- 列は必ず**月曜始まりの週**に整列する。範囲の先頭が週の途中なら、その週の範囲外の曜日は **空白パディング** (濃淡を持たないマス) として描く。
- 範囲が 53 週を超える場合 (主に全期間)、**新しい側の 53 週**を残し、切り捨てた古い週数を「…and N older week(s) omitted」と明示する (黙って切り捨てない)。

### 出力イメージ

```
$ atcoder stats --year --graph
practice stats — this year (2026)

  total solves     112
  active days        6
  current streak     6 days
  longest streak     6 days

by category
  abc  112

by letter
  d  112

contribution graph (shade = Σ letter weight/day; a=1…g=7)
            Jan         Feb       Mar  …  Jun
  Mon  · · · ■ ■ ■ … ■
  Tue  · · ■ ■ ■ ■ … ■
  Wed  · · · · ■ ■ … ■
  Thu  · ■ ■ ■ ■ · … ■
  Fri  · · · ■ ■ ■ … ■
  Sat  · · · · · · … ·
  Sun  · · · · · · … ·

  less · ■ ■ ■ ■ more
```

- マスは活動あり (1..4) を GitHub 同様の四角 `■` で揃え、**濃淡は緑系の色グラデーション**で表す (暗→明)。縦長に見える陰影ブロック (`░▒▓█`) は読みづらいため採らない。空 (level 0) だけは `·` にして、色が出ない非 TTY (パイプ/テスト) でも「活動した日 / しない日」を判別できるようにする。
- 上部に月ラベル、左に曜日ラベル (Mon..Sun)。空白パディング (範囲外の曜日) は何も描かない。
- データ 0 件のときは従来どおり "no solves found ..." を出して exit 0 (グリッドは描かない)。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `--graph` 指定 | 時系列セクションをバーから草グリッドに差し替え。他セクションは不変 |
| `--graph` 無し | 従来のバー時系列 (挙動完全に不変) |
| `--graph` + 期間フラグ | 期間窓に応じた範囲でグリッド化 |
| 期間フラグ 2 つ以上 | 従来どおり exit 2 (`--graph` の有無に関わらず) |
| データ 0 件 | "no solves" を出して exit 0 (グリッド描画なし) |
| レター不明 (`?`) | 重み 1 として加算 (空マスにはならない) |
| 全期間で 53 週超 | 新しい 53 週を残し omitted を明示 |

- **読み取り専用**: 解答・キャッシュ・git に一切書き込まない。
- **オフライン**: ネットワーク・認証に触れない。レベルはローカルのレターのみから計算。
- **決定的**: `Now` 注入 (`stats.Options.Now`) で固定でき、しきい値も固定なのでグリッド・濃淡は一意。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/stats.go` | `--graph` / `-g` フラグを追加。`stats.Options.Graph` に渡す |
| `cmd/atcoder/main.go` | `usage()` の `stats` 行に `[-g|--graph]` を追記 |
| `internal/stats/stats.go` | `Options.Graph` 追加。`letterWeight`/`shadeLevel`/`buildGraph` を追加。`Report` に `Graph []GraphColumn` と `GraphOmitted int` を追加。`Compute` で Graph 指定時にグリッドを構築 (その場合バー Series は省く) |
| `internal/stats/render.go` | `Report.Graph` があれば草グリッド + 凡例を描画。月/曜日ラベル・濃淡文字・着色 |
| `internal/complete/complete.go` | `stats` のフラグ候補に `--graph` / `-g` を追加 |
| `internal/stats/stats_test.go` | `letterWeight`/`shadeLevel`/`buildGraph` (整列・パディング・53 週上限・レベル分類) のユニットテスト |
| `fixtures/run.sh` | `stats --graph` 系の smoke (exit 0、期間フラグ併用、排他違反 exit 2) を追加 |
| `docs/tools/usage/stats.md` | `--graph` の説明・出力例・レベル計算の表を追記 |
| `docs/tools/todo.md` | 本項目を ✅ DONE で記載し本要件へリンク |

### `internal/stats` パッケージへの追加 (素描)

```go
// Options に追加。
type Options struct {
    Period Period
    Now    time.Time
    Graph  bool // true で時系列を草グリッドとして構築する
}

// GraphCell は草グリッドの 1 マス。
type GraphCell struct {
    Date    time.Time // そのマスの日 (週パディングは入らない: InRange=false)
    Score   int       // Σ letterWeight。範囲外/0 件は 0
    Level   int       // 0..4 の濃淡レベル
    InRange bool      // グリッド対象範囲 (期間窓内かつ今日以前) なら true。範囲外は空白パディング
}

// GraphColumn は週 (月曜始まり) 1 列、7 マス (index 0=Mon … 6=Sun)。
type GraphColumn struct {
    Monday time.Time
    Cells  [7]GraphCell
}

// Report に追加。
//   Graph        []GraphColumn // Options.Graph 指定時のみ。空なら従来の Series を使う
//   GraphOmitted int           // 53 週上限で切り捨てた古い週数

// letterWeight はレターを難易度の重みに変換する (a=1…z=26, "?"=1)。
func letterWeight(letter string) int

// shadeLevel は日次スコアを濃淡レベル 0..4 に分類する (固定しきい値)。
func shadeLevel(score int) int

// buildGraph は日次スコアから期間窓に追従したグリッドを構築する。
func buildGraph(dayScore map[time.Time]int, p Period, now time.Time) (cols []GraphColumn, omitted int)
```

- `letterWeight` / `shadeLevel` / `buildGraph` は純粋関数。`Compute` を I/O から分離する既存方針に合わせ、ユニットテストで決定的に固定する。
- `Compute` は `Options.Graph` が true のとき `buildGraph` を呼び `rep.Graph`/`rep.GraphOmitted` を埋め、バー `Series` は構築しない (二重表示を避ける)。false のときは従来どおり `Series` のみ。
- レンダリングは既存同様 `lipgloss`。活動マスは `■` で揃え、濃淡はレベルごとの緑系スタイルで着色する。**空 (level 0) は `·`** にして、色が出ない非 TTY でも「活動した日 / しない日」だけは文字で判別できるようにする (レベル 1〜4 の濃淡は色で表す)。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 未知のフラグ | flag パッケージが usage 表示 | 2 |
| 期間フラグ 2 つ以上 (`--graph` 有無問わず) | "only one of --week/--month/--year may be set" | 2 |
| `exercise/` 読み取り I/O エラー | エラー表示 | 1 |
| データ 0 件 | "no solves" 表示 (グリッドなし) | 0 |
| `--graph` 正常 | サマリ + 草グリッド表示 | 0 |

## 非機能要件

- **副作用ゼロ / 読み取り専用 / オフライン**: 既存 `stats` の安全設計を一切崩さない。レベルもローカルのレターのみから計算し、fetch しない。
- **既存非破壊**: `--graph` を付けない `stats` の出力は 1 文字も変えない。他サブコマンドも不変。
- **決定的・テスト可能**: `Now` 注入と固定しきい値で、グリッド・濃淡・53 週上限の挙動をユニットテストで固定する。
- **黙って切り捨てない**: 53 週上限を超えたら omitted を明示する。
- **活動有無は色に依存しない**: 活動マス `■` と空マス `·` の別は文字で表すので、非 TTY でもグリッドの粗密 (練習リズム) が読める。レベル 1〜4 の濃淡は色グラデーションで表す (GitHub と同方式)。

## 将来の拡張ポイント

- **`--difficulty`**: AtCoder Problems の difficulty を fetch してレベルに使う (要ネットワーク・キャッシュ。現状のローカル算出と切替)。
- **`--json`**: `Report.Graph` を含めて機械可読出力。
- **しきい値設定**: `shadeLevel` のしきい値や相対 (分位数) スケールをユーザ設定 (`atcoder config`) で調整可能に。
- **`--since`/`--until`**: 任意日付範囲のグリッド。

## 用語

- **レター重み (letter weight)**: 問題レターを難易度の代理として数値化した重み (`a`=1…`z`=26, `?`=1)。
- **日次スコア (day score)**: その日の全 solve のレター重みの総和。
- **濃淡レベル (shade level)**: 日次スコアを固定しきい値で 0〜4 に分類した値。マスの濃さ。
- **グリッド列 (graph column)**: 月曜始まりの 1 週間 (7 マス、Mon..Sun)。
- (`contest_id` / `task_id` / `letter` は 005 / MVP A 要件に準拠)

## 関連ドキュメント

- `docs/tools/requirements/005-exercise-stats.md` (stats 本体)
- `docs/tools/decisions/0002-stats-readonly-exercise-tree.md` (読み取り専用の決定記録)
- `docs/tools/usage/stats.md` (利用手引)
