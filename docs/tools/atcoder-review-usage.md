# `atcoder review` 利用手引

`exercise/` で練習したコンテストを **カテゴリ単位で一覧**する。`atcoder review abc` で、これまで取り組んだ ABC を **contest × letter のテーブル**に並べ、各回を最後に解いた日付を添える。`stats` が集計値 (総数・ストリーク・草) を出すのに対し、`review` は個々のコンテストの**列挙**を担う。読み取り専用で、リポジトリには一切書き込まない。

> 要件詳細: `docs/tools/requirements/014-exercise-review.md`

## コマンド

```
atcoder review <category> [-w | --week | -m | --month | -y | --year | -l | --last <dur>]
```

| 引数 / フラグ | 説明 |
|---|---|
| `<category>` (必須) | 列挙するコンテスト種別 (`abc`/`arc`/`agc`/…)。**位置引数で先頭に置く**。省略すると exit 2 |
| `--week` (`-w`) | 暦の今週 (月曜始まり、今日を含む) の解答に絞る |
| `--month` (`-m`) | 暦の今月に絞る |
| `--year` (`-y`) | 暦の今年に絞る |
| `--last <dur>` (`-l`) | 今日から `<dur>` 分だけ遡るローリング窓に絞る (`7d`/`2w`/`1m`/`1y`、数値省略で 1) |

- 期間フラグは `stats` と同一の文法・排他規則。2 つ以上指定すると exit 2。指定しなければ全期間。
- カテゴリはフラグより前に置く (例 `atcoder review abc --month`)。

## 集計対象

- `stats` と同じく `exercise/<YYYY>/<MM>/<DD>/` 直下の **`.py` ファイル 1 つを 1 問**として数える (中身は問わない)。
- ファイル名から **contest_id** (`abc457`) と **letter** (`d`) を導き、`<category>` に一致する solve を contest_id でグルーピングする。
- 日付はファイルの**パス**から取る (mtime/git 非依存)。
- `exercise/` 以外のツリー (`abc/`, `adt/`, `dp/` …) は対象外。

## テーブルの見方

- **行** = 1 コンテスト (contest 番号の降順、新しい回が上)。
- **列** = 問題レター。**ABC は a–g を固定列**にするので、解いていないレターも `·` (穴) として並ぶ。ABC 以外のカテゴリは、実際に解いたレターの和集合だけを列にする。
- **マス** = 解いていれば `■`、未解は `·`。`■` の**色の濃淡で recency (最近解いたか / 古いか)** を表す:

  | 経過日数 (今日 − 解答日) | 色 (TTY) |
  |---|---|
  | ≤ 7 日 | 最も明るい緑 (ごく最近) |
  | ≤ 30 日 | 明るい緑 |
  | ≤ 90 日 | 緑 |
  | 90 日超 | 暗い緑 (古い) |

  色ランプ・記号は `stats --graph` と揃えてある。**非 TTY (パイプ/テスト) では色が出ない**ため濃淡は一様に見えるが、行末の **last solved (最終解答日)** が recency を文字で残す。
- **last solved** = その回を最後に解いた日。

## 出力例

```
$ atcoder review abc
exercise abc review — 181 contests, 181 solves

  contest   a b c d e f g   last solved
  abc458    · · · ■ · · ·   2026-06-09
  abc457    · · · ■ · · ·   2026-06-08
  …
  abc125    · · · ■ · · ·   2026-05-16

  older ■ ■ ■ ■ newer   ·=未着手
  181 contests
```

期間で絞ると、ヘッダが期間ラベルに変わる:

```
$ atcoder review abc --month
exercise abc review — this month (2026-06)

  contest   a b c d e f g   last solved
  abc458    · · · ■ ■ · ·   2026-06-09
  abc457    · · · ■ · · ·   2026-06-08
  …
```

該当カテゴリの solve が 0 件のときは "no `<category>` solves found ..." を 1 行出して正常終了する。

## exit code

| code | 意味 |
|---|---|
| `0` | 一覧表示成功 (0 件でも成功扱い) |
| `1` | `exercise/` の読み取り I/O エラー |
| `2` | 引数誤り (`<category>` 省略、未知フラグ、期間フラグの重複指定、不正な `--last` 値) |

## 注意

- 完全に読み取り専用。解答ファイル・キャッシュ・git には触れない。
- ネットワーク・認証は不要 (オフラインで動く)。recency は AtCoder の difficulty を fetch せず、解答日のみから決まる。
- recency は「今日」基準。`--week` などの境界や色は実行日に依存する。

## 関連

- `docs/tools/atcoder-stats-usage.md` (`stats` 集計コマンド・データ層と期間フラグの定義元)
- `docs/tools/requirements/014-exercise-review.md` (要件定義)
