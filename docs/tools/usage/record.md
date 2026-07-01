# `atcoder record` 利用手引

1 問を解いた練習を **実装時間・正答状況 (AC したか / 解説を見たか)・5 軸スコア (知識・翻訳・計算量・実装・検証)** として残す。記録は解答ファイル冒頭の機械可読なコメントブロック (**solve-stat ブロック**) に埋め込まれ、`atcoder stats` から集計・振り返りできる。

> 要件詳細: [requirements/061-solve-record-stats.md](../requirements/061-solve-record-stats.md)。読み取り専用集計は [`stats.md`](stats.md)、着手刻印は [`start.md`](start.md)。

AtCoder への実提出・オンライン AC 判定は範囲外 (Turnstile のため不可能。[ADR 0006](../decisions/0006-fold-submit-into-test.md))。**AC したかは自己申告**で、提出フロー直後に尋ねる導線に乗せて負担を最小化する。

## 記録のライフサイクル

1. **開始** — `atcoder start` / `atcoder record start` が着手時刻 (`started_at`) を解答ファイル冒頭に刻む。
2. **終端** — `test --submit` 後の「AC できたか」プロンプトで yes、または `atcoder record stop` で完了時刻 (`solved_at`) が確定し、実装時間が決まる。
3. **記録** — `atcoder record` の対話 (またはフラグ) で AC / 解説閲覧 / 5 軸スコアを埋め、solve-stat ブロックへ書き戻す。

## solve-stat ブロック

解答ファイル (`exercise/<YYYY>/<MM>/<DD>/<task>.py` 等) の**先頭**に、マーカーで挟んだコメント列として置かれる。Python コメントなので実行・サンプル判定には一切影響しない。提出 (`test --submit` / chat の `Ctrl+S`) の際は、この個人メタデータを公開コードに混ぜないよう**クリップボードへ載せる前に丸ごと除去**される (解答ファイル本体は不変。要件 [063](../requirements/063-submit-strip-solve-stat.md))。

```python
# >>> atcoder-stat >>>
# started_at  = 2026-07-01T16:00:00+09:00
# solved_at   = 2026-07-01T16:25:00+09:00
# duration_ms = 1500000
# target_ms   = 2100000
# ac          = true
# editorial   = false
# knowledge   = 2
# translation = 3
# complexity  = 2
# impl        = 3
# verify      = 1
# <<< atcoder-stat <<<
L, R = map(int, input().split())
...
```

- 各キーは**任意**で、`start` 直後は `started_at` だけ、`stop` 後は `solved_at`/`duration_ms`/(任意で `ac`)、`record` 後に全キー、と段階的に埋まる。
- 書き込みは**キー単位の部分更新** (他キーを消さない)。ブロックが無ければ先頭に新規挿入。temp+rename で atomic に書き、途中失敗で解答を壊さない。
- マーカーが片方だけ/重複するなど**破損**していると、自動修復せず warning を出して書き込みを中止する (exit 1)。

## コマンド

```
atcoder record       <contest> --task <task> [--ac|--no-ac] [--editorial|--no-editorial]
                                             [--score <k,t,c,i,v>] [--knowledge|--translation|--complexity|--impl|--verify <0-3>]
                                             [--time <dur>] [--layout <auto|abc|exercise>]
atcoder record start <contest> --task <task> [--restart] [--layout ...]
atcoder record stop  <contest> --task <task> [--ac|--no-ac] [--time <dur>] [--layout ...]
```

第 1 引数が `start` / `stop` ならそのサブコマンド、そうでなければ (contest 指定) 記録本体。位置引数 (`<contest>`) とフラグの順序は自由。

### `atcoder record` (記録)

| フラグ | 説明 |
|---|---|
| `--task <task>` | タスク ID または短縮形 (`d` → `<contest>_d`)。必須 |
| `--ac` / `--no-ac` | AC 可否を非対話で指定 (両立指定は exit 2) |
| `--editorial` / `--no-editorial` | 解説閲覧を非対話で指定 |
| `--score <k,t,c,i,v>` | 5 軸を一括指定 (各 0–3、例 `2,3,2,3,1`) |
| `--knowledge` / `--translation` / `--complexity` / `--impl` / `--verify <0-3>` | 軸ごとの個別指定 (`--score` より優先) |
| `--time <dur>` | 実装時間を手動指定 (例 `25m`, `1h5m`)。`started_at` 差より優先 |

- `solved_at` が未記録なら**完了時刻を今に確定**し、`duration_ms` を `solved_at - started_at` で算出する。既に記録済みなら完了時刻・実装時間は温存する (再実行はスコアのキー単位訂正)。
- **対話**: TTY で、フラグ未指定の項目だけプロンプトで尋ねる (AC・解説・実装時間・5 軸)。5 軸は `0=手が出ず / 1=大きくつまずいた / 2=手間取った / 3=スムーズ` の目安を表示。
- **非対話** (パイプ・CI・fixture): 尋ねずにフラグ分だけ書き、足りない項目は未記録のまま exit 0 (ハングしない)。

### `atcoder record start` (計測開始)

着手 UI (`atcoder start` の watch) を伴わずに計測だけ始める軽量版。無ければ解答ファイルを空で作り、`started_at` を刻む (既にあれば温存)。`--restart` で `started_at` を今にリセットし、完了記録 (`solved_at`/`duration_ms`/スコア) をクリアする (やり直し練習用)。

### `atcoder record stop` (計測終端)

スコア対話に入らない最小終端。`solved_at` を今に確定し `duration_ms` を算出 (`--time` があれば上書き)、config の目標時間を `target_ms` にスナップショットする。`--ac`/`--no-ac` で AC も記録できる。異常値 (負値 / 12h 超) は warning を出しつつ記録する (日跨ぎ放置対策)。

## 目標実装時間 (`config`)

難易度 (= **category × letter**) ごとの目標実装時間を `atcoder config` に持たせ、実装時間と突き合わせて振り返れる (`abc` の d と `arc` の d は別物なので両軸で持つ)。

```
atcoder config set   target.abc.d 35m     # abc の D 問題の目標を 35 分に
atcoder config get   target.abc.d
atcoder config unset target.abc.d
atcoder config show                        # target.<category>.<letter> = <dur> を一覧
```

- 値は duration 文字列 (`35m`, `1h5m`)。パースできなければ exit 2。
- `record` / `record stop` は記録時点の目標を solve-stat の `target_ms` にスナップショットするので、後で config を変えても当時の目標比が残る。
- 目標未設定の (category, letter) では目標比を出さず、実装時間だけを表示・集計する。

## 出力例

```
$ atcoder record start abc457 --task d
計測を開始しました: exercise/2026/07/01/abc457_d.py

$ atcoder record stop abc457 --task d --ac
計測を終了しました: exercise/2026/07/01/abc457_d.py
  実装 23m / 目標 35m (-12m, 達成)
スコアは `atcoder record abc457 --task d` で記録できます。

$ atcoder record abc457 --task d --score 2,3,2,3,1 --no-editorial
記録しました: exercise/2026/07/01/abc457_d.py
  実装 23m / 目標 35m (-12m, 達成)
  ac=true  editorial=false
  score  k=2 t=3 c=2 i=3 v=1
```

`atcoder stats` に solve-stat があると、実装時間・正答率・5 軸平均の `recorded` / `score` セクションが増える (詳細は [`stats.md`](stats.md))。

## exit code

| 状況 | exit |
|---|---|
| 正常記録 (警告付き含む) | 0 |
| 引数・フラグ誤り (`--task` 欠落 / `--score` の値数・範囲 / 相反 bool 併用 / 不正 `--time` / `config set target` の不正 duration) | 2 |
| 解答ファイル不在 (`record`/`record stop`) / solve-stat ブロック破損 / 書き込み失敗 | 1 |

## 制約 (現時点 = MVP)

- 対象言語は Python (`#` コメント) のみ。
- `atcoder record edit` (既存記録の専用編集 UI) は Phase 2。今は `record` の再実行でキー単位訂正できる。
- chat TUI (Ctrl+S) 経路の AC プロンプト、`review` への per-cell 表示は将来拡張。

## 関連

- 要件: [requirements/061-solve-record-stats.md](../requirements/061-solve-record-stats.md)
- 集計: [`stats.md`](stats.md) / [requirements/005-exercise-stats.md](../requirements/005-exercise-stats.md)
- 着手: [`start.md`](start.md) / 提出フロー: [`test.md`](test.md)
- 決定記録: [ADR 0002](../decisions/0002-stats-readonly-exercise-tree.md) (stats read-only) / [ADR 0006](../decisions/0006-fold-submit-into-test.md) (実提出/AC 取得が不可な理由)
