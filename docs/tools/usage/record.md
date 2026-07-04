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
atcoder record edit  <contest> --task <task> [--layout ...]
```

第 1 引数が `start` / `stop` / `edit` ならそのサブコマンド、そうでなければ (contest 指定) 記録本体。位置引数 (`<contest>`) とフラグの順序は自由。

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

### `atcoder record edit` (全画面編集フォーム)

既に記録済みの solve-stat を**全画面フォーム**で一覧表示し、任意フィールドを訂正・クリアする (要件 [066](../requirements/066-record-edit.md))。`record` 再実行のフラグ訂正と違い、現在値を見ながら直せて「一度 true にした値を未記録へ戻す」クリアも素直にできる。

- 編集対象は `state` (計測状態) / `ac` / `editorial` / `duration` / 5 軸。`started_at` / `solved_at` / `target_ms` は個別編集しないが、**`state` 行のトグルで start / stop / reset として書き換わる** (下記。要件 [068](../requirements/068-record-edit-state-toggle.md))。トグルしなければ元値を温存する。
- 既存記録が前提。記録・solve-stat ブロックが無ければ案内して exit 1。全画面フォームは**対話端末が必要**で、非対話 (パイプ・CI) では exit 1 でフラグ経路 (`atcoder record ...`) を案内する。
- 保存 (Enter) は `OverwriteFile` で全置換 (クリアしたキーは落ちる)。取消 (Esc) はファイルを書き換えない。

```
> state       [ 計測中 ]  開始 16:00
  ac          [ true ]
  editorial   [ false ]
  duration    [ 23m ]
  knowledge   [ 2 ]
  ...
目標 35m
j/k 移動   Tab/space トグル   h/l 変更   0-3・y/n 入力   Backspace 未記録   Enter 保存   Esc 取消
```

| キー | 動作 |
|---|---|
| `j` / `k` (`↑` / `↓`) | フィールド間を移動 |
| `Tab` / space | **カーソル位置のフィールド値を前方トグル**。`state` 行は計測状態を 1 段前進 (`未計測 → 計測中 → 停止 → 未計測`)、`ac`/`editorial`・5 軸はその場で 1 段回す (`duration` は無操作) |
| `h` / `l` | `ac`/`editorial` は `未記録 ↔ true ↔ false` を循環、5 軸は `未記録 ↔ 0..3` を移動 (`duration` では `h` は時間入力)。`state` 行では前方トグル |
| `y` / `n` | `ac`/`editorial` を true / false に |
| `0`–`3` | 5 軸の値を直接入力 |
| `Backspace` | 選択フィールドを未記録へ (duration は 1 文字削除、`state` 行は未計測へリセット。reset は確認あり。要件 [069](../requirements/069-record-edit-reset-confirm.md)) |
| `duration` 入力 | 数字と `h`/`m`/`s` を打って実装時間を編集 (空で未計測)。未編集なら元の値を桁落ちなく温存 |
| `Enter` (`Ctrl+S`) | 保存して終了 | 
| `Esc` / `Ctrl+C` | 取消して終了 |

**計測状態 (`state`) のトグル** — フォームを離れずに計測ライフサイクルを進める (要件 068)。状態は `started_at` / `solved_at` から導出する:

| 現在 | トグル | 次 | 作用 (実時刻 now を刻む。`:record start`/`stop` と同義) |
|---|---|---|---|
| `未計測` | start | `計測中` | `started_at = now`、`duration` クリア |
| `計測中` | stop | `停止` | `solved_at = now`、`duration = now − started_at`、`target_ms` を config 目標でスナップショット |
| `停止` | reset | `未計測` | **全クリア** (`started_at`/`solved_at`/`duration`/`target_ms`/`ac`/`editorial`/5 軸すべて。`:record start restart` 相当)。破壊的なので**確認あり** |

- **reset は確認を挟む** (要件 [069](../requirements/069-record-edit-reset-confirm.md))。`停止 → 未計測` のトグルや `state` 行の `Backspace` を押すと即クリアせず「リセットしますか」の確認行が出る。`y` / `Y` で実行、それ以外のキーはすべて取消 (誤爆防止)。start / stop トグルは非破壊なので確認なしで即進む。
- chat の `:record edit` では、保存後にヘッダの ● REC インジケーターを保存内容へ同期する (`計測中` を保存すると `started_at` 基準で点灯・毎秒経過、`停止`/`未計測` は消灯)。
- `started_at`/`solved_at` を**任意の時刻値**へ直接編集するのは将来拡張 (state トグルは now を刻むライフサイクル操作)。

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

## chat から記録する (`:record`)

`atcoder start` の分割画面や `test --interactive` の chat では、解答を編集している画面を離れずに `:record` コマンドで計測・記録できる (要件 064)。CLI `atcoder record` と同じ solve-stat 書き込みロジックを**非対話**で呼ぶ (chat では逐次プロンプトの対話ウィザードは持たず、記入はフラグ経由・閲覧は引数なしに割り当てる)。

| 入力 | 動作 |
|---|---|
| `:record start` | `started_at` を刻む (`:record start restart` で再計測) |
| `:record stop` | `solved_at`/`duration_ms` を確定 (`:record stop ac` / `:record stop time=25m` も可) |
| `:record` | solve-stat の現在値を表示する (**書き込まない**) |
| `:record ac ed score=2,3,2,3,1 time=25m` | AC/解説/5 軸/実装時間を非対話フラグで一括記録 |
| `:record edit` | 既存記録を**全画面フォーム**で訂正する (要件 066)。`state` 行で start/stop/reset のトグルも可 (要件 068)。Enter 保存 / Esc 取消 |

- bool フラグは bare 語 (`ac`/`noac`、`ed`/`noed`)、値フラグは `key=value` (`score=k,t,c,i,v`、`time=<dur>`)。相反 bool の併用・`score`/`time` の不正値は err 行で伝えて chat は継続する。
- 実装時間が異常値 (負値 / 12h 超) のとき、chat では確認を挟めないので警告行を添えてそのまま記録する (CLI 非対話経路と同じ)。
- `:record edit` は chat を離れずに CLI `record edit` と同じ全画面フォームを開く (`:case` の作成画面と同様に子プロセスは裏で生かしたまま画面を占有)。記録が無ければ「(まだ記録がありません)」と案内する。保存すると更新結果を info 行で積んで会話へ戻る。
- フォーム内の `state` 行を `Tab` で切り替えれば `:record start`/`stop`/`start restart` と同じ操作をフォームから完結できる (要件 068)。保存後はヘッダの ● REC インジケーターが保存内容に同期する (`計測中` → 点灯・経過表示、`停止`/`未計測` → 消灯)。

```
:record start
  計測を開始しました: exercise/2026/07/01/abc457_d.py
:record ac ed score=2,3,2,3,1
  記録しました: exercise/2026/07/01/abc457_d.py
  実装 23m / 目標 35m (-12m, 達成)
  ac=true  editorial=true
  score  k=2 t=3 c=2 i=3 v=1
```

## exit code

| 状況 | exit |
|---|---|
| 正常記録 (警告付き含む) | 0 |
| 引数・フラグ誤り (`--task` 欠落 / `--score` の値数・範囲 / 相反 bool 併用 / 不正 `--time` / `config set target` の不正 duration) | 2 |
| 解答ファイル不在 (`record`/`record stop`/`record edit`) / solve-stat ブロック破損 / 書き込み失敗 / `record edit` の非対話端末・記録なし | 1 |

## 制約 (現時点 = MVP)

- 対象言語は Python (`#` コメント) のみ。
- `atcoder record edit` / `:record edit` (既存記録の全画面編集フォーム) は実装済み (要件 066)。`state` 行のトグルで start/stop/reset の計測ライフサイクルもフォームから操作できる (要件 068)。`started_at` / `solved_at` を**任意の時刻値**へ直接編集するのは将来拡張。
- chat からは `:record` で計測・記録、`:record edit` で訂正できる (上記)。Ctrl+S 提出後の AC プロンプト・`review` への per-cell 表示は将来拡張。

## 関連

- 要件: [requirements/061-solve-record-stats.md](../requirements/061-solve-record-stats.md) / chat 統合 [requirements/064-chat-record.md](../requirements/064-chat-record.md) / 編集フォーム [requirements/066-record-edit.md](../requirements/066-record-edit.md) / state トグル [requirements/068-record-edit-state-toggle.md](../requirements/068-record-edit-state-toggle.md) / reset 確認 [requirements/069-record-edit-reset-confirm.md](../requirements/069-record-edit-reset-confirm.md)
- 集計: [`stats.md`](stats.md) / [requirements/005-exercise-stats.md](../requirements/005-exercise-stats.md)
- 着手: [`start.md`](start.md) / 提出フロー: [`test.md`](test.md)
- 決定記録: [ADR 0002](../decisions/0002-stats-readonly-exercise-tree.md) (stats read-only) / [ADR 0006](../decisions/0006-fold-submit-into-test.md) (実提出/AC 取得が不可な理由)
