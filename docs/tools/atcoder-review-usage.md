# `atcoder review` 利用手引

`exercise/` で練習したコンテストを **カテゴリ単位で一覧**する。`atcoder review abc` で、これまで取り組んだ ABC を **contest × letter のテーブル**に並べ、各回を最後に解いた日付を添える。`stats` が集計値 (総数・ストリーク・草) を出すのに対し、`review` は個々のコンテストの**列挙**を担う。読み取り専用で、リポジトリには一切書き込まない。

> 要件詳細: `docs/tools/requirements/014-exercise-review.md`

## コマンド

```
atcoder review <category> [-w | --week | -m | --month | -y | --year | -l | --last <dur>]
```

| 引数 / フラグ | 説明 |
|---|---|
| `<category>` (必須) | 列挙するコンテスト種別 (`abc`/`arc`/`agc`/…)。位置引数 (**フラグと任意順で混在可**)。省略すると exit 2 |
| `--week` (`-w`) | 暦の今週 (月曜始まり、今日を含む) の解答に絞る |
| `--month` (`-m`) | 暦の今月に絞る |
| `--year` (`-y`) | 暦の今年に絞る |
| `--last <dur>` (`-l`) | 今日から `<dur>` 分だけ遡るローリング窓に絞る (`7d`/`2w`/`1m`/`1y`、数値省略で 1) |

- 期間フラグは `stats` と同一の文法・排他規則。2 つ以上指定すると exit 2。指定しなければ全期間。
- カテゴリとフラグの順序は自由 (`atcoder review abc --month` も `atcoder review --month abc` も可)。

## 集計対象

**2 つのツリーを横断**して 1 問 = `.py` 1 ファイルと数える (中身は問わない):

| ツリー | 形 | 日付 |
|---|---|---|
| `exercise/<YYYY>/<MM>/<DD>/<contest>_<letter>.py` | 日付がパスにある | **あり** |
| `<category>/<num>/<letter>.py` (`abc/447/d.py` 等) | 練習問題を 1 問 1 ファイルで置くツリー | **なし** |

- 位置引数の `<category>` に対し、`exercise/` の同カテゴリ solve と `<category>/` ツリーの両方を読み、**contest_id** (`abc447`) でグルーピングする。
- 同じ (contest, letter) が両方にあれば**日付ありを優先**する。実際には exercise (旧 D 埋め) とカテゴリツリー (新しい回) はほぼ範囲が分離していて重複は稀。
- 日付は `exercise/` のみパスから取る (mtime/git 非依存)。カテゴリツリーは日付を持たない。
- `<category>/<num>/` の `<num>` は数字を含む dir のみ (`447`, `0001-beta`)。`generate_d_testcase.py` のような letter 形でない補助ファイルは無視する。

## テーブルの見方

- **行** = 1 コンテスト (contest 番号の降順、新しい回が上)。
- **列** = 問題レター。**ABC は a–g を固定列**にするので、解いていないレターも `·` (穴) として並ぶ。ABC 以外のカテゴリは、実際に解いたレターの和集合だけを列にする。
- **マス** = 3 状態を色と文字で表す:

  | マス | 意味 |
  |---|---|
  | `■` 緑の濃淡 | 解いた (日付あり)。色の濃淡で recency (≤7日=最も明るい → 90日超=暗い緑) |
  | `■` 黄色 | **本番** で解いた (カテゴリツリー由来・日付なし) |
  | `·` 薄灰 | 未着手 |

  緑ランプ・記号は `stats --graph` と揃えてある。**非 TTY (パイプ/テスト) では色が出ない**ため 3 状態は `■`/`·` の文字でしか区別できないが、行末の **last solved** が日付の有無を文字で残す。
- **last solved** = その回を最後に解いた日 (日付ありの solve の最大日付)。日付が一切無い回 (カテゴリツリーのみ) は `—`。

## 出力例

`abc/` ツリーの回は a–f に幅広く `■` (黄色・日付なし) が立ち last solved は `—`、`exercise/` の D 埋めは recency 着色 + 日付:

```
$ atcoder review abc
exercise abc review — 237 contests, 387 solves

  contest   a b c d e f g   last solved
  abc461    ■ ■ ■ ■ ■ · ·   —            (abc/ 由来 = 日付なし・黄色)
  abc458    ■ ■ ■ ■ ■ · ·   —
  …
  abc331    · · · ■ · · ·   2026-06-09   (exercise 由来 = recency 着色)
  …
  abc125    · · · ■ · · ·   2026-05-16

  older ■ ■ ■ ■ newer   ■ 本番   · 未着手
  237 contests
```

期間で絞ると、ヘッダが期間ラベルに変わり、**日付なし (カテゴリツリー) の回は除外**される:

```
$ atcoder review abc --month
exercise abc review — this month (2026-06)

  contest   a b c d e f g   last solved
  abc331    · · · ■ · · ·   2026-06-09
  …
```

`arc`/`awc` など他カテゴリも同じ要領 (`atcoder review awc` は `awc/` を読む)。該当カテゴリの solve が両ツリーとも 0 件のときは "no `<category>` solves found ..." を 1 行出して正常終了する。

## exit code

| code | 意味 |
|---|---|
| `0` | 一覧表示成功 (0 件でも成功扱い) |
| `1` | `exercise/` または `<category>/` ツリーの読み取り I/O エラー |
| `2` | 引数誤り (`<category>` 省略、未知フラグ、期間フラグの重複指定、不正な `--last` 値) |

## 注意

- 完全に読み取り専用。解答ファイル・キャッシュ・git には触れない。
- ネットワーク・認証は不要 (オフラインで動く)。recency は AtCoder の difficulty を fetch せず、解答日のみから決まる。
- recency は「今日」基準。`--week` などの境界や色は実行日に依存する。

## 関連

- `docs/tools/atcoder-stats-usage.md` (`stats` 集計コマンド・データ層と期間フラグの定義元)
- `docs/tools/requirements/014-exercise-review.md` (要件定義)
