# 076: stats の solve-stat 問題別テーブル

## 概要

`atcoder stats` に `--table` (`-t`) を追加し、指定期間に解いた問題を 1 問 1 行のテーブルで表示する。既存の集計 (`recorded` / `score`) は期間内の傾向を見る用途に残し、`--table` は「どの問題が何分かかり、AC できたか、解説を見たか」を直接振り返るための表示モードにする。

## 背景・目的

solve-stat には `duration_ms` / `ac` / `editorial` / 5 軸スコアが残るが、現状の `stats` は期間内の集計値だけを出す。復習時には平均や率だけでなく、問題ごとの記録を時系列で見たい。特に実装時間・AC・解説閲覧は、次に復習する問題や弱点を選ぶ入口になるため、一覧で必ず確認できるようにする。

## スコープ

| 対象 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 表示 | `stats --table` で問題別テーブルを stdout に出す | `--json` / CSV / 並び替えキー |
| 期間 | 既存の `--week` / `--month` / `--year` / `--last` を共有 | 任意の日付範囲 `--from` / `--to` |
| 列 | `date`, `problem`, `duration`, `ac`, `editorial`, `score` | reviewed / target / path / category filter |
| 対象ツリー | 既存 stats と同じ `exercise/YYYY/MM/DD/*.py` | contest ツリー横断は要件 070 側 |

## CLI 仕様

```
atcoder stats [-w|--week | -m|--month | -y|--year | -l|--last <dur>] [-g|--graph] [-t|--table]
```

| フラグ | 意味 |
|---|---|
| `--table`, `-t` | 指定期間の solve を問題別テーブルで表示する |

`--table` は既存の期間指定と併用できる。`--graph` と同時指定された場合、`--table` を優先し、時系列グラフではなく問題別テーブルを表示する。期間指定の排他規則と exit code は既存 `stats` と同じ。

### 出力例

```
$ atcoder stats --last 7d --table
practice records — last 7 days (2026-07-19-07-25)

  date        problem   duration  ac  editorial  score
  2026-07-25  abc457_d  23m       yes no         2/3/2/2/1
  2026-07-24  abc456_e  -         no  yes        -
```

## 動作仕様

| 状況 | 動作 |
|---|---|
| 期間内に solve が無い | `no solves found in exercise/ for <label>` を表示して exit 0 |
| solve-stat が無い問題 | 行には出す。`duration` / `ac` / `editorial` / `score` は `-` |
| `duration_ms` が未記録 | `duration` は `-` |
| `ac` / `editorial` が未記録 | 対応列は `-` |
| 5 軸すべて未記録 | `score` は `-` |
| 5 軸の一部だけ記録 | 未記録軸を `-` として `2/-/1/3/-` の形で表示 |
| 並び順 | 新しい日付を先にし、同日内はファイル名昇順 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/stats/stats.go` | 期間窓で絞った `Solve` を問題別行へ変換する公開関数を追加 |
| `internal/stats/render.go` | 問題別テーブルのレンダリングを追加 |
| `cmd/atcoder/stats.go` | `--table` / `-t` を parse し、通常 `Render` と分岐 |
| `cmd/atcoder/main.go` | usage に `--table` を追記 |
| `docs/tools/usage/stats.md` | 利用手引へ問題別テーブルを追記 |
| `docs/tools/todo.md` | `stats` record テーブルを DONE 項目として記録 |

## エラーハンドリング

| 状況 | exit | 動作 |
|---|---:|---|
| 未知フラグ / 期間フラグ重複 / `--last` 不正 | 2 | 既存 `stats` と同じ |
| `exercise/` 読み取り I/O エラー | 1 | 既存 `stats` と同じ |
| solve-stat ブロック破損 | 0 | 既存 `Scan` と同じく該当問題の stat を無視し、行は欠損表示 |

## 非機能要件

- 読み取り専用。解答ファイル・キャッシュ・git には触れない。
- ネットワーク・認証は不要。
- 既存の `stats` 出力は `--table` を付けない限り変えない。
- `duration`, `ac`, `editorial` は常に列として表示する。

## 関連ドキュメント

- [005-exercise-stats.md](005-exercise-stats.md)
- [010-stats-rolling-window.md](010-stats-rolling-window.md)
- [061-solve-record-stats.md](061-solve-record-stats.md)
- [usage/stats.md](../usage/stats.md)
