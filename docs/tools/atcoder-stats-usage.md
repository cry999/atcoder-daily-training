# `exercise stats` 利用手引

日々の練習 (`exercise/YYYY/MM/DD/<task>.py`) の積み上がりを 1 コマンドで振り返る。解答数・連続練習日数 (ストリーク)・コンテスト種別/問題レター別の内訳・最近の推移をテーブル表示する。読み取り専用で、リポジトリには一切書き込まない。

> 要件詳細: `docs/tools/requirements/005-exercise-stats.md`

## コマンド

```
exercise stats [--week | --month | --year]
```

| フラグ | 集計範囲 |
|---|---|
| (なし) | 全期間 |
| `--week` | 今週 (月曜始まり、今日を含む) |
| `--month` | 今月 |
| `--year` | 今年 |

`--week` / `--month` / `--year` は排他。2 つ以上指定すると exit 2。

## 集計対象

- `exercise/<YYYY>/<MM>/<DD>/` 直下の **`.py` ファイル 1 つを 1 問**として数える (中身は問わない)。
- 日付はファイルの**パス**から取る (mtime や git には依存しない)。
- カテゴリ (コンテスト種別) と問題レターはファイル名から導く: `abc457_d.py` → カテゴリ `abc`・レター `d`。先頭が英字でなければ `other`、`_` が無ければレターは `?`。
- `exercise/` 以外のツリー (`abc/`, `adt/`, `dp/` …) は対象外。

## 統計項目

| 項目 | 定義 |
|---|---|
| total solves | 期間内のファイル総数 |
| active days | 1 問以上解いた日数 |
| current streak | 今日から遡って連続して解いた日数。今日未着手でも前日まで続いていれば前日起点で数える |
| longest streak | 期間内の連続練習日数の最大 |
| by category | `abc`/`arc`/…/`other` 別の件数 (多い順) |
| by letter | `a`..`g`/`?` 別の件数 (レター昇順、`?` は末尾) |
| 時系列 | `--week`/`--month` は日別、`--year`/全期間は週別 (最大 16 週、超過分は「…and N more week(s)」) |

ストリーク・各内訳・時系列はすべて**選んだ期間の窓**に対して計算する。相対期間は必ず今日を含むので current streak は常に意味を持つ。

## 出力例

```
$ exercise stats --month
practice stats — this month (2026-06)

  total solves   112
  active days    6
  current streak 6 days
  longest streak 6 days

by category
  abc  112

by letter
  d  112

by day
  2026-06-01  ░ 0
  2026-06-03  ███████████ 15
  ...
  2026-06-08  █████████████████████ 28
  2026-06-09  ░ 0
```

データが 0 件のときは "no solves found ..." を 1 行出して正常終了する。

## exit code

| code | 意味 |
|---|---|
| `0` | 集計成功 (0 件でも成功扱い) |
| `1` | `exercise/` の読み取り I/O エラー |
| `2` | フラグ誤り (未知フラグ、期間フラグの重複指定) |

## 注意

- 完全に読み取り専用。解答ファイル・キャッシュ・git には触れない。
- ネットワーク・認証は不要 (オフラインで動く)。
- 集計は「今日」基準。`--week` などの境界は実行日に依存する。
