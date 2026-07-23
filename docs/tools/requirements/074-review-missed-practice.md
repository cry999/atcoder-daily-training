# 074: 前日の未達問題を復習キューとして一覧・チェックする

## 概要

`atcoder review missed` を追加し、前日に練習した問題のうち **AC できなかった問題 (`ac=false`)** と **解説を見た問題 (`editorial=true`)** を翌日の復習対象として一覧する。復習した問題は `--check <id>` で解答ファイル先頭の solve-stat に `reviewed_at` を記録し、次回一覧で `[x]` として見分けられるようにする。

## 背景・目的

`atcoder record` で AC / editorial / 5 軸スコアは残せるようになったが、翌日に「昨日どれを復習すべきか」を拾うには `stats` や `review abc` の表示を見ながら手で探す必要がある。とくに `ac=false` だけを見ると、AC はしたが解説を見た問題 (`editorial=true`) が復習から漏れる。翌日の最初に 1 コマンドで復習対象を出し、終わったものをチェックできるようにする。

## スコープ

| 区分 | 内容 |
|---|---|
| 当面のスコープ | `exercise/YYYY/MM/DD/*.py` の指定日 1 日ぶんから `ac=false` または `editorial=true` の solve-stat を持つ問題を一覧する |
| 既定日 | `--date` 未指定なら実行日の前日 (ローカル日付) |
| チェック | `--check <id>` で一致する 1 問の solve-stat に `reviewed_at=<now>` を部分更新する |
| 状態保存 | solve-stat の新キー `reviewed_at`。提出時は既存の `solvestat.Strip` により除去される |
| 将来の拡張余地 | `--all` / `--unreviewed`、複数 ID の一括チェック、カテゴリツリー横断、chat からの `:review missed` |
| 対象外 | AtCoder から AC 状態を取得すること、解説ページを開くこと、復習そのものの採点 |

## solve-stat スキーマ

| キー | 型 | 意味 |
|---|---|---|
| `reviewed_at` | RFC3339 timestamp | その問題を復習済みにした日時。未記録なら未復習 |

既存キーと同じコメントブロックへ保存する:

```py
# >>> atcoder-stat >>>
# solved_at   = 2026-07-22T22:15:00+09:00
# ac          = false
# editorial   = true
# reviewed_at = 2026-07-23T07:30:00+09:00
# <<< atcoder-stat <<<
```

## CLI 仕様

```
atcoder review missed [--date YYYY-MM-DD] [--check <id>]
```

| 引数 / フラグ | 説明 |
|---|---|
| `missed` | `review` の復習キューモード。既存の `<category>` 位置引数とは別扱い |
| `--date YYYY-MM-DD` | 対象の練習日。省略時はローカル日付の前日 |
| `--check <id>` | 一覧内の問題を復習済みにする。`id` は `abc357_d` のようなファイル stem、または `contest/letter` (`abc357/d`) |

処理ステップ:

1. `cmdReview` が先頭位置引数 `missed` を見たらカテゴリ一覧ではなく missed モードへ分岐する。
2. `internal/stats.Scan("exercise")` で練習解答を読む。`stats.Solve` は元ファイルパスも保持する。
3. `internal/review.BuildMissed` が対象日 (`--date` または前日) かつ `HasStat` の solve だけを見て、`ac=false` または `editorial=true` を対象にする。
4. 一覧表示では `reviewed_at` の有無で `[ ]` / `[x]` を出す。
5. `--check <id>` 指定時は対象日の missed 一覧から ID に一致する 1 件を探し、`solvestat.Update(path, patch{ReviewedAt: now})` で部分更新する。

出力例:

```console
$ atcoder review missed
missed practice — 2026-07-22

  [ ] abc357_d  ac=false  editorial=true   exercise/2026/07/22/abc357_d.py
  [x] abc356_e  ac=true   editorial=true   reviewed 2026-07-23 07:30

  2 missed, 1 reviewed
```

```console
$ atcoder review missed --check abc357_d
reviewed abc357_d (exercise/2026/07/22/abc357_d.py)
```

## 動作仕様

| 状況 | 動作 |
|---|---|
| `ac=false` | 復習対象に含める |
| `editorial=true` | `ac=true` でも復習対象に含める |
| `ac` 未記録かつ `editorial` 未記録 / `editorial=false` | 復習対象に含めない |
| `reviewed_at` 記録済み | 一覧に残し `[x]` と表示する (完了済みも見えるようにする) |
| `--check` を再実行 | `reviewed_at` を現在時刻へ更新する。冪等な再チェックとして扱い成功 |
| `--check` なし | 読み取り専用。解答ファイルに触れない |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/solvestat/` | `Stat.ReviewedAt`、parse / merge / render の対応 |
| `internal/stats/stats.go` | `Solve.Path` を追加し、`Scan` で元ファイルパスを保持 |
| `internal/review/missed.go` | missed 抽出・ID 照合・描画用レポートを追加 |
| `cmd/atcoder/review.go` | `review missed` の flag parse / check 更新 / render 結線 |
| `cmd/atcoder/main.go` | usage の `review` 構文行を更新 |
| `docs/tools/usage/review.md` | 復習キューの使い方を追記 |
| `docs/tools/todo.md` | 本項を DONE として記録 |

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `--date` が `YYYY-MM-DD` でない | エラー | 2 |
| `--check` が対象日の missed 一覧に無い | エラー | 1 |
| `--check` が複数に一致 | エラー | 1 |
| 対象ファイルパスが無い | エラー | 1 |
| solve-stat 破損 / 書き込み失敗 | エラー | 1 |

## 非機能要件

- ネットワーク・認証は不要。完全オフラインで動作する。
- `--check` 以外では解答ファイルを変更しない。
- `reviewed_at` は solve-stat の一部なので提出ソースには混入しない。
- 既存の `atcoder review <category>` の出力・TUI・期間フラグは壊さない。

## 関連ドキュメント

- 既存 review: [`014-exercise-review.md`](014-exercise-review.md)
- solve-stat: [`061-solve-record-stats.md`](061-solve-record-stats.md)
- 利用手引: [`../usage/review.md`](../usage/review.md)
