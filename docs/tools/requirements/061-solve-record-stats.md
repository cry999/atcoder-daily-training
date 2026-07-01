# `atcoder record` 実装記録・正答率・5 軸スコア 要件定義

## 概要

1 問を解いた練習を **実装時間・正答状況 (AC したか / 解説を見たか)・5 軸スコア (知識・翻訳・計算量・実装・検証)** の 3 種のメトリクスとして残せるようにする。記録は解答ファイル冒頭の機械可読なコメントブロック (**solve-stat ブロック**) に埋め込み、`atcoder stats` から集計・振り返りできるようにする。

記録のライフサイクルは 3 段構え:

1. **開始** — `atcoder start` が着手時刻 (`started_at`) を解答ファイル冒頭に刻む。
2. **終端** — 提出準備 (`test --submit`) 完了後の「AC できたか」プロンプトで yes を選ぶ、または `atcoder stop` を叩くと、その時点を完了時刻 (`solved_at`) として実装時間が確定する。
3. **記録** — `atcoder record` の対話で AC / 解説閲覧 / 5 軸スコアを埋め、solve-stat ブロックに書き戻す。

あわせて、問題の難易度 (= 問題 letter。A/B/C/D…) ごとに **目標実装時間** を `atcoder config` で設定できるようにし、実装時間と目標を突き合わせて振り返れるようにする (目標比・目標達成率)。目標は着手 (`start`) 中の watch 表示・記録 (`record`/`stop`) 時の目標比・`stats` の達成率として活きる。

`docs/tools/todo.md` の一般 TODO 項目。既存の `stats` (読み取り専用集計 / 要件 005) と、`start` (着手統合コマンド)・`test --submit` (提出準備 / 要件 015) の上に乗せる。AtCoder への実提出・オンライン AC 判定は依然として範囲外 (要件 015 / ADR 0006 のまま。AC したかは自己申告)。

## 背景・目的

- 現状の `stats` は「`exercise/**/*.py` が存在するか」だけを数える。**どれだけ時間をかけたか・自力で AC できたか・どこでつまずいたか** は一切残らず、振り返りが「解いた/解いてない」の粒度に留まる。
- 練習の質を上げるには「解けた/解けない」より一歩踏み込んだ内省が要る。特に **どの局面 (知識・読解・計算量見積もり・実装・検証) が弱いか** を軸ごとに点数化して積み上げれば、伸ばすべき箇所が見える。
- 実装時間は「体感」ではなく実測で残したい。`start` で着手し、提出準備の直後に AC 可否を尋ねる導線に乗せれば、普段のワークフローの中で自然に計測できる。
- オンライン提出結果の自動取得は Cloudflare Turnstile のため不可能 (ADR 0006)。よって AC 可否は **自己申告** とし、提出フローの直後という「結果が分かった瞬間」に尋ねることで申告の負担と誤差を最小化する。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 記録メトリクス | 実装時間・AC (bool)・解説閲覧 (bool)・5 軸スコア (各 0〜3) | WA 回数・難易度・言語別・タグ |
| 保存先 | 解答ファイル冒頭の solve-stat ブロック (git 管理) | サイドカーファイル / DB 化 |
| 対象言語 | Python (`#` コメント) のみ | 言語別コメントプレフィックスの抽象化 |
| 記録コマンド | `atcoder record` + `record start` / `record stop` (対話 + 非対話フラグ) | `record edit` (Phase 2)・TUI での一覧編集 |
| 計測開始 | `atcoder start` / `atcoder record start` が `started_at` を埋め込む | `new abc` 一括着手時の一括開始 |
| 計測終端 | `test --submit` 後プロンプト / `atcoder record stop` (新規) | chat TUI (Ctrl+S) 経路への統合 |
| 目標時間 | letter (難易度) ごとに config で設定、実装時間と比較 | category×letter 別・個別 task 上書き・パーセンタイル目標 |
| 集計 | `atcoder stats` に実装時間・正答率・5 軸平均を追加 | `review` への per-cell 表示、`--json` |
| 集計対象ツリー | `exercise/` のヘッダ (ADR 0002 と整合) | `abc/`/`arc/` 等 category ツリー横断 |
| AC 判定 | 自己申告 (提出フロー後プロンプト / `record` 対話) | 実提出 API 連携 (Turnstile のため当面不可) |

### 「記録単位」の考え方 (境界)

- 記録は **1 解答ファイル = 1 問** に紐づく。solve-stat ブロックはそのファイルの冒頭に置く。`stats` (要件 005) の「1 ファイル = 1 問」と一致させる。
- solve-stat ブロックは **メタ情報であって解答ではない**。Python コメントなので実行にもサンプル判定にも提出 (要件 043 の DEBUG コメントアウトと同じくコメント行) にも影響しない。
- 記録が無い解答ファイルはこれまで通り「解いた (存在する)」とだけ数える。solve-stat の有無で既存集計は壊れない (後方互換)。

## ディレクトリ構造 / スキーマ

### solve-stat ブロックの位置

解答ファイル (`exercise/<YYYY>/<MM>/<DD>/<task>.py` 等) の **先頭** に、マーカー行で挟んだコメントブロックを置く。

```python
# >>> atcoder-stat >>>
# started_at  = 2026-07-01T16:00:00+09:00
# solved_at   = 2026-07-01T16:25:00+09:00
# duration_ms = 1500000
# ac          = true
# editorial   = false
# knowledge   = 2
# translation = 3
# complexity  = 2
# impl        = 3
# verify      = 1
# <<< atcoder-stat <<<
L, R, D, U = map(int, input().split())
...
```

- ブロックは常に **ファイル先頭** (0 行目) から始まる。ブロックの後に元の解答コードが続く。
- 各行は `# <key><spaces>= <value>` の 1 行 1 キー形式 (自前パース。TOML ライブラリは使わず、行志向で読む方が壊れにくい)。キー幅の空白揃えは表示都合で、パーサは `=` 前後を trim する。
- 開始マーカー `# >>> atcoder-stat >>>` / 終了マーカー `# <<< atcoder-stat <<<` でブロック範囲を特定する。マーカーが揃わない (片方だけ・重複) 場合はブロック無しとみなし、書き込み時は先頭に新規挿入する (壊れた既存ブロックには追記しない → 二重化を防ぐため、破損検出時は warning を出して停止する案も検討: エラーハンドリング参照)。

### フィールドスキーマ

| キー | 型 | 記録元 | 意味 |
|---|---|---|---|
| `started_at` | RFC3339 datetime | `start` | 着手時刻 (ローカルオフセット付き) |
| `solved_at` | RFC3339 datetime | `stop` / submit 後プロンプト / `record` | 完了時刻 |
| `duration_ms` | int | 算出 (`solved_at - started_at`) or 手動 | 実装時間 (ミリ秒) |
| `target_ms` | int | config の目標時間を記録時にスナップショット | 目標実装時間 (ミリ秒)。目標比の分母 |
| `ac` | bool (`true`/`false`) | submit 後プロンプト / `record` | AC できたか (自己申告) |
| `editorial` | bool | `record` | 解説 (editorial) を見たか |
| `knowledge` | int 0〜3 | `record` | 知識: 必要なアルゴリズム/データ構造/定理を知っていたか |
| `translation` | int 0〜3 | `record` | 翻訳: 問題文を正しく数理モデル/方針へ落とせたか (読解・立式) |
| `complexity` | int 0〜3 | `record` | 計算量: TLE を避ける計算量の解法を見積もれたか |
| `impl` | int 0〜3 | `record` | 実装: バグなく素早くコードに落とせたか |
| `verify` | int 0〜3 | `record` | 検証: サンプル/コーナーケース確認・デバッグができたか |

- すべてのキーは **任意 (部分的に埋まる)**。`start` 直後は `started_at` だけ、`stop` 後は `solved_at`/`duration_ms`/(可能なら `ac`) まで、`record` 後に全キー、という段階的な埋まり方をする。欠けたキーは集計時に「未記録」として扱い、平均などの母集団から除外する。
- `duration_ms` は原則 `solved_at - started_at` の壁時計差。`record`/`stop` で手動上書き可能 (下記「動作仕様」)。

### 5 軸スコアの評価基準 (目安)

主観評価だが、ブレを抑えるため各軸共通の 0〜3 の目安を置く (`record` のプロンプトにも短縮版を表示する):

| 点 | 目安 |
|---|---|
| 0 | 手が出なかった / その軸に到達できず (例: 解法自体が思いつかない = knowledge 0) |
| 1 | 大きくつまずいた / ヒント・解説・長考を要した |
| 2 | 概ね自力でできたが手間取った・ミスした |
| 3 | スムーズに正しくできた |

> この基準表はレビュー対象。軸の定義・点の刻みは運用しながら調整してよい (solve-stat スキーマは前方互換を保つ)。

### 目標時間 (config)

目標実装時間は per-solve の記録ではなく **設定値** なので、`atcoder config` (`internal/config`) に持たせる。既存 `[alias]` (動的マップ) と同じ流儀で、`[target]` 配下に **category × letter** の 2 階層で `target.<category>.<letter>` = duration 文字列を置く。難易度は category (`abc`/`arc`/…) と letter (`a`〜`g`) の組で決まる (`abc` の d と `arc` の d は別物) ため、両軸で持つ。

```toml
[target.abc]
a = "5m"
b = "10m"
c = "20m"
d = "35m"
e = "50m"
f = "60m"
g = "90m"

[target.arc]
a = "20m"
b = "40m"
c = "60m"
d = "80m"
```

| 項目 | 仕様 |
|---|---|
| 保存先 | `config.toml` の `[target.<category>]` テーブル (`<XDG_CONFIG_HOME>/atcoder-daily-training/config.toml`) |
| キー | `target.<category>.<letter>` (例 `target.abc.d`)。値は duration 文字列 (`35m`, `1h5m`) |
| 粒度 | **category × letter**。`abc` の d と `arc` の d は別々に設定できる |
| 設定 | `atcoder config set target.abc.d 35m` / 解除 `atcoder config unset target.abc.d` / 一覧 `atcoder config show`。TOML 手編集も可 |
| 解決 | `start`/`record` が category (ファイル名先頭英字 / contest_id の種別) と letter (`layout.Letter`) を求め `[target.<category>]` から引く |
| フォールバック | category×letter が未設定なら「目標なし」。将来: category 非依存の共通デフォルト (`target.default.<letter>`) |
| スナップショット | `record`/`record stop` が記録時点の目標を solve-stat の `target_ms` に保存。後で config を変えても当時の目標比が残る |

- 目標が未設定の (category, letter) では目標比・達成率を出さず、実装時間のみを表示・集計する (目標は任意)。
- `config set target.<category>.<letter>` の値が duration としてパースできなければ exit 2 (フラグ/値エラー)。
- config は 2 階層の動的マップ (`map[string]map[string]string`)。`internal/config` の `setNested`/`unsetNested` (dot path 処理) で対応し、未知 category/letter は保全する。

## CLI 仕様

### コマンド構成

記録系の操作は `atcoder record` に集約する。`stop` を単体トップレベルに置くと「何を止めるのか」文脈が無いため、計測の開始/終端は `record` のサブコマンドとしてぶら下げる。

| コマンド | 役割 | フェーズ |
|---|---|---|
| `atcoder start <contest> --task <t>` | (既存) 着手統合。ファイル生成 + watch に加え、着手時に `started_at` を自動で刻む | MVP |
| `atcoder record start <contest> --task <t>` | 計測開始 (着手コマンドを使わず計測だけ始める軽量版) | MVP |
| `atcoder record stop <contest> --task <t>` | 計測終端 (`solved_at` 確定、任意で `--ac`) | MVP |
| `atcoder record <contest> --task <t>` | 記録: 正答/解説/5 軸スコアを対話 or フラグで書く (完了時刻も確定) | MVP |
| `atcoder record edit <contest> --task <t>` | 既存記録の編集 (フラグ非対話 / 対話プリフィル) | Phase 2 |

- `atcoder start` (着手) と `atcoder record start` (計測開始) は両方 `started_at` を刻む。前者はファイル生成 + watch を伴う着手ワークフロー、後者は計測だけの軽量開始。
- サブコマンド語 (`start`/`stop`/`edit`) と contest ID (`abc457` 等) は形が重ならないので曖昧性なし。`record` の第 1 引数が既知サブコマンド語ならサブコマンド、そうでなければ contest とみなす (dispatch は `cmd/atcoder/record.go` に一本化)。

### `atcoder start` の拡張

既存の着手統合コマンド (`start.go`) に、着手時刻の刻印を足す。フラグ・引数は現行のまま。

1. 解答ファイルを用意する (現行: 無ければ空ファイル)。
2. solve-stat ブロックを読む。`started_at` が **未記録なら** 現在時刻を刻む。**既にあれば温存** (再開しても着手時刻を巻き戻さない = 冪等)。
3. `solved_at` が既にある (= 一度完了済み) 状態で再度 `start` した場合は、着手時刻を触らず warning のみ (「既に完了記録があります。再計測するなら `atcoder record start --restart` を使ってください」)。`--restart` フラグで `started_at` を今にリセットし `solved_at`/`duration_ms` をクリアできる (やり直し練習用)。
4. 以降は現行どおり `test --watch` の分割 UI を起動する。watch ペインのヘッダに、letter に対応する **目標時間**と着手からの**経過時間**を表示する (`目標 35m / 経過 12m`。目標が未設定なら経過のみ)。経過時間は着手時刻 `started_at` を基点に UI 側で刻む (タイマー G の芽)。

> `started_at` はプロセスの生死ではなくファイルに永続化されるため、`start` を Ctrl+C で抜けても、後日 `test`/`stop`/`record` で計測を続けられる。

### `atcoder record` (記録)

記録系サブコマンドの親。contest/task を指定して起動すると、対話で AC / 解説閲覧 / 5 軸スコア (と必要なら実装時間) を埋め、solve-stat ブロックに書き戻す。第 1 引数が `start`/`stop`/`edit` ならそれぞれのサブコマンドへ委譲する。

```
atcoder record <contest> --task <task> [flags]
```

| 引数 / フラグ | 説明 |
|---|---|
| `<contest>` | contest ID (例 `abc457`)。`start`/`test` と同じ解決 |
| `--task <task>` | task ID または短縮形 (`d` → `abc457_d`)。必須 |
| `--layout <auto\|abc\|exercise>` | 解答ファイル配置 (現行 `start`/`test` と同じ) |
| `--ac` / `--no-ac` | AC 可否を非対話で指定 |
| `--editorial` / `--no-editorial` | 解説閲覧を非対話で指定 |
| `--score <k,t,c,i,v>` | 5 軸を一括指定 (例 `--score 2,3,2,3,1`)。0〜3 の 5 値 |
| `--knowledge` / `--translation` / `--complexity` / `--impl` / `--verify <0-3>` | 軸ごとの個別指定 (`--score` より優先) |
| `--time <dur>` | 実装時間を手動指定 (例 `25m`, `1h5m`)。`started_at` 差より優先 |

処理ステップ:

1. レイアウト解決 → 解答ファイルパス確定 (無ければ「先に `atcoder start` か `atcoder record start` してください」で exit 1)。
2. solve-stat ブロックを読み、現在値を提示。
3. `solved_at` が未記録なら **完了時刻を今に確定**し、`duration_ms` を `solved_at - started_at` で算出。`started_at` も無ければ実装時間は「未計測」とし、対話で手入力を促す。
4. 実装時間が **異常値** (負値 / 上限超; 既定上限は 12 時間) の場合、確認プロンプトを出して「その値で記録 / 手入力し直す / 未記録にする」を選ばせる (日跨ぎ放置の誤計測対策)。
5. 対話プロンプト (フラグで与えられた項目はスキップ):
   - `AC できましたか? [y/N]`
   - `解説を見ましたか? [y/N]`
   - `実装時間 [25m] >` (算出値を既定として表示。Enter で採用、`30m` 等で上書き)
   - `知識 [0-3] >` … `検証 [0-3] >` (各軸。基準の 1 行ヒントを添える)
6. 全項目を solve-stat ブロックへ **部分更新** で書き戻す (既存ブロックがあればキーを更新、無ければ先頭に挿入)。記録時点の目標時間を `target_ms` にスナップショットする。
7. 書き込んだ内容を 1 画面で要約表示。目標が設定されていれば **目標比** も出す (`実装 23m / 目標 35m (-12m, 達成)`。超過なら `(+8m, 超過)`)。

- **非対話**: 必要な値がすべてフラグで与えられていれば、プロンプトを一切出さずに書き込む (スクリプト / CI・fixture 用)。stdin が非 TTY で不足項目があれば、その項目を「未記録」のまま書ける範囲で書き、exit 0 (ハングしない)。

### `atcoder record start` (計測開始)

着手コマンド `start` を使わず、計測だけ始めたいとき用 (既にファイルがある問題を「今から測る」等)。

```
atcoder record start <contest> --task <task> [--restart]
```

1. レイアウト解決 → 解答ファイル (無ければ空ファイルで作成)。
2. `started_at` が未記録なら今を刻む。既にあれば温存 (warning)。
3. `--restart` で `started_at` を今にリセットし `solved_at`/`duration_ms`/完了系をクリア (やり直し練習)。

- watch は起動しない (着手 UI が要るなら `atcoder start`)。計測開始だけの軽量コマンド。

### `atcoder record stop` (計測終端)

時間計測だけを止めたいとき用。スコア対話には入らない。

```
atcoder record stop <contest> --task <task> [--ac|--no-ac] [--time <dur>]
```

1. レイアウト解決 → solve-stat ブロックを読む。
2. `solved_at` を今に確定し `duration_ms` を算出 (`--time` があれば上書き)。config の目標時間 (category×letter) を `target_ms` にスナップショットし、目標比を表示する。
3. `--ac`/`--no-ac` が指定されていれば `ac` も記録。
4. 「あとで `atcoder record <contest> --task <task>` でスコアを記録できます」を案内して終了。

> `record stop` は `record` の対話をスキップした最小終端。実体は同じ solve-stat 書き込みロジックを共有する。

### `atcoder record edit` (既存記録の編集 / Phase 2)

一度記録した solve-stat を後から訂正する。`record` が「計測終端 + 初回入力」なのに対し、`edit` は既存値の訂正に特化する。2 モード:

- **フラグ非対話**: `atcoder record edit abc457 --task d --score 3,3,3,3,2 --time 40m --no-editorial` のように、指定したキーだけ上書き (与えないキーは温存)。一括修正・スクリプト向き。
- **対話プリフィル**: フラグ無しで起動すると、既存値を初期表示した対話フォームを開き、各項目を見ながら訂正する (`record` の対話 UI を共有し「Enter で現状維持」)。

- 実装が重いので **Phase 2 として別実装**でよい。`edit` は完了時刻 (`solved_at`) を動かさない (訂正なので再確定しない) 点で `record` と挙動を分ける。MVP でも `record` 自体が「既存ブロックへのキー単位マージ」なので、`atcoder record abc457 --task d --score ...` の再実行で単一キー訂正は可能 (`edit` はその編集 UX を洗練させる位置づけ)。

### `test --submit` 後の AC プロンプト

提出準備 (`submitPrepCore` / 要件 015・044) が完了した直後、以下を満たすときにプロンプトを出す:

- 解答ファイルに solve-stat ブロックがあり `started_at` が記録済み、かつ `solved_at` が未記録。
- stdin が TTY (非 TTY なら尋ねずスキップ。`confirmSubmit` と同じ安全側)。

プロンプト:

```
提出準備が完了しました。ブラウザで提出して結果を確認してください。
AC できましたか? [y/N/skip]
```

- `y`: `solved_at` を今に確定、`ac = true`、`duration_ms` 算出。続けて「スコアも記録しますか? [Y/n]」→ yes なら `record` の対話へ流し込む (5 軸 + editorial)。
- `N`: `ac = false` を記録するかは尋ねない (WA 直後に何度も提出し直すため)。計測は継続し、何も書かない。
- `skip` / Enter: 何もしない。

> この導線は当面 CLI 経路 (`test --submit`) のみ。chat TUI (Ctrl+S / 要件 026) への統合は将来拡張。

### `atcoder stats` の拡張

既存の集計 (要件 005) に、solve-stat を読んだ **実装時間・正答率・5 軸平均** のセクションを追加する。solve-stat が 1 件も無ければ従来出力のまま (セクションを出さない)。

追加セクション (期間フラグ `--week`/`--month`/`--year` は既存どおり効く):

```
recorded (12 solves, 8 with stats)
  ac rate           75%   (6/8)
  self-solved       50%   (4/8, AC かつ解説なし)
  editorial rate    38%   (3/8)
  median time       23m   (min 8m / max 51m)
  target hit rate   62%   (5/8, 実装 ≤ 目標。目標設定のある solve のみ)

score (avg, n=8)
  knowledge    2.1  ██████
  translation  1.8  █████
  complexity   2.4  ███████
  impl         2.6  ███████
  verify       1.5  ████
```

- 「12 solves, 8 with stats」で **母集団と記録済み件数の差** を明示する (黙って一部だけ集計しない = 要件 005 の「黙って切り捨てない」に倣う)。
- 各集計は「記録のある solve」のみを母集団にする。欠損キーはその軸の平均から個別に除外。

## 動作仕様

### 計測ライフサイクルと冪等性

| 状況 | 挙動 |
|---|---|
| `start` (初回) | `started_at` を刻む。`solved_at` 無し |
| `start` (再開・完了前) | `started_at` を温存 (巻き戻さない) |
| `start` (完了後) | warning。`--restart` 明示時のみ `started_at` リセット + 完了系クリア |
| `record stop` / submit 後 y / `record` (完了確定) | `solved_at` を今に、`duration_ms` を算出 |
| `record` (2 回目) | 既存値を提示し、上書き入力を受け付ける (部分更新) |
| `record edit` (Phase 2) | 既存値を訂正。`solved_at` は動かさない |
| `started_at` 無しで `record stop`/`record` | 実装時間は未計測。手入力 (`--time`/対話) があればそれを記録、無ければ時間系は空のまま他項目を記録 |

### 部分更新 (solve-stat ブロックの書き込み)

- 書き込みは **キー単位のマージ**。既存ブロックの他キーを消さず、与えられたキーだけ更新する。
- ブロックが無ければファイル先頭に新規挿入し、既存コードはそのまま後ろへ。
- 空白揃え (キー幅) は書き込み時に再整形してよい。値の順序はスキーマ定義順に固定 (diff を安定させる)。
- 書き込みは一時ファイル + rename で atomic に行い、途中失敗で解答を壊さない。

### 実装時間の算出と手動上書き

- 既定は `solved_at - started_at` の壁時計差 (中断除外はしない = 単純差)。
- `--time` / 対話入力があればそれを `duration_ms` に採用し、`solved_at` は「今」を保持 (時間だけ上書き、完了時刻は記録)。
- 異常値 (負値 / 12h 超) は確認を挟む。日跨ぎ放置などの誤計測を黙って記録しない。上限値は定数で持ち将来フラグ化余地を残す。

### 既存ワークフローとの共存

- solve-stat はコメントなので、`test` のサンプル判定・`run`・`test --submit` のクリップボードコピー (要件 043 で DEBUG 行のみコメントアウト、solve-stat は元からコメントなので影響なし) いずれにも影響しない。
- `stats` の既存集計 (solve 数・ストリーク等) は不変。追加セクションは solve-stat がある場合のみ増える。
- `commit` (要件のコミットコマンド) は当日 dir を丸ごと add するので、solve-stat 入りの解答も従来どおりコミットされる。

## フェーズ分け (実装段階)

重めなので MVP と Phase 2 に分けて実装してよい (要件・コミットも分割可)。

| フェーズ | 内容 |
|---|---|
| MVP | `internal/solvestat` / `start` 刻印 / `record`・`record start`・`record stop` / `test --submit` 後の AC プロンプト / `stats` の集計セクション / config `[target.<category>]` (category×letter) / fixtures / docs |
| Phase 2 | `atcoder record edit` (フラグ非対話 + 対話プリフィル) / chat (Ctrl+S / 要件 026) 経路の AC プロンプト / `review` への per-cell 表示 |

- MVP と Phase 2 は独立に出荷できる粒度で切る。MVP 時点でも `record` の再実行で単一キー訂正は可能 (`edit` は編集 UX の洗練)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| 新規 `internal/solvestat/` | solve-stat ブロックのスキーマ・parse・部分更新書き込み (行志向 / atomic)。純粋関数中心でテスト容易に |
| `cmd/atcoder/start.go` | 解答ファイル用意後に `solvestat` で `started_at` を刻む。`--restart` フラグ追加 |
| 新規 `cmd/atcoder/record.go` | `cmdRecord(args) (int, error)` を親 dispatch とし、第 1 引数で `record start`/`record stop`/`record edit`(Phase 2) へ分岐。既定 (contest 指定) は記録対話。`record` / `record stop` / `record start` は `solvestat` 書き込みロジックを共有 |
| `cmd/atcoder/submitprep.go` | `runSubmitPrep` 完了後に AC プロンプト → `solvestat` 書き込み → (任意で) record 対話呼び出し |
| `cmd/atcoder/main.go` | `case "record"` 追加 (start/stop/edit は record 内 dispatch)。`usage()` 更新 |
| `internal/stats/stats.go` | `Solve` に solve-stat を読み込む経路を追加。`Report` に record 系集計フィールドを追加。`Render` に新セクション |
| `internal/layout/` | 既存の解決 API を record 系から流用 (追加不要見込み)。`Letter`・category で目標時間の引き当て |
| `internal/config/` | `[target.<category>]` の 2 階層動的マップ (`target.<category>.<letter>` = duration) を追加。(category, letter)→目標の解決ヘルパー (`config.Target(category, letter) (time.Duration, bool)`) |
| `cmd/atcoder/config.go` | `config set/get/unset/show target.<category>.<letter>` の受理 (keys.go の動的ネストマップ登録)。値は duration としてパース検証 |
| `fixtures/` | record / record start / record stop / start 刻印 / stats 新セクションの smoke (非対話フラグ経路でネット無し) |
| `docs/tools/usage/record.md` (新規) / `usage/stats.md` / `usage/start.md` | 利用手引 |
| `docs/tools/todo.md` | ロードマップに本項目を追加 |

### 新規 `internal/solvestat/` パッケージの責務

```go
package solvestat

// Stat は solve-stat ブロックの内容。各フィールドは任意 (未記録は nil/ゼロ + Has* で判別)。
type Stat struct {
    StartedAt  time.Time
    SolvedAt   time.Time
    DurationMs int64
    TargetMs   int64 // 記録時にスナップショットした目標時間 (0 = なし)
    AC         *bool
    Editorial  *bool
    Score      Score // 各軸 -1 = 未記録
}

type Score struct {
    Knowledge, Translation, Complexity, Impl, Verify int // 0..3, 未記録は -1
}

// Parse は解答ソースから solve-stat ブロックを読む。ブロックが無ければ zero Stat と found=false。
func Parse(src []byte) (Stat, bool, error)

// Merge は既存 src のブロックに patch を部分マージした新ソースを返す (ブロック無しなら先頭挿入)。
func Merge(src []byte, patch Stat) ([]byte, error)

// ReadFile / WriteFile はファイル単位のヘルパー (WriteFile は temp+rename で atomic)。
func ReadFile(path string) (Stat, bool, error)
func Update(path string, patch Stat) error

// コメントプレフィックスは当面 "#" 固定 (Python)。将来言語別に差し替えるフック。
```

- `Parse` / `Merge` は I/O から分離した純粋関数にし、ユニットテストで「新規挿入・部分更新・破損ブロック・空白揺れ・値のラウンドトリップ」を網羅する。
- `stats` からは `ReadFile` で各解答の `Stat` を集めて集計する (ADR 0002 の read-only は維持: `stats` は書かない。書くのは `start`/`record` 系 (`record start`/`record stop`/`record edit`)/submit 経路のみ)。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `record` 系 (`record`/`record start`/`record stop`) で `--task` 未指定 | usage 表示 | 2 |
| `record` の未知サブコマンド語 (`start`/`stop`/`edit` 以外を誤入力) | usage 表示 | 2 |
| `--score` の値数が 5 でない / 0〜3 外 | エラー表示 | 2 |
| 軸フラグの値が 0〜3 外 | エラー表示 | 2 |
| `--time` がパース不能 | エラー表示 | 2 |
| `config set target.<letter>` の値が duration でない | エラー表示 | 2 |
| 解答ファイルが存在しない (record/stop) | 「先に `atcoder start` してください」 | 1 |
| solve-stat ブロックが破損 (マーカー片方だけ/重複) | warning 表示、書き込みを中止 (自動修復せず手当てを促す) | 1 |
| 書き込み I/O 失敗 (権限/rename 失敗) | エラー表示。temp を残さず解答は無傷 | 1 |
| 実装時間が異常値 | 対話なら確認プロンプト / 非対話なら warning 付きで指定値採用 | 0 |
| 対話を Ctrl+C / EOF で中断 | 何も書き込まず終了 | 1 |
| submit 後プロンプト (非 TTY) | 尋ねずスキップ | (submit の code を踏襲) |
| 正常記録 | 要約表示 | 0 |

- exit code は repo 規約に従う: 引数/フラグ誤り = 2、実行時失敗 (I/O・破損・中断) = 1、成功 = 0。

## 非機能要件

- **解答非破壊**: solve-stat 書き込みは temp+rename で atomic。既存コードを 1 バイトも失わない (先頭挿入 or キー部分更新のみ)。破損ブロックは自動修復せず停止する安全側。
- **冪等性**: `start` 再実行で着手時刻は巻き戻らない。`record` 再実行は上書き (積み上がらない)。
- **後方互換**: solve-stat の無い既存解答・既存 `stats` 出力は不変。ブロックはコメントなので実行/判定/提出に影響しない。
- **前方互換**: スキーマへのキー追加は非破壊 (未知キーは読み飛ばし保持)。将来の言語別コメントプレフィックスを見据え、プレフィックスを 1 箇所に閉じる。
- **決定的・テスト可能**: `solvestat.Parse`/`Merge` と `stats.Compute` は純粋関数。`Now` を注入して固定 (要件 005 と同じ流儀)。
- **オフライン**: 記録・集計はローカルのみ。ネットワーク/認証に触れない (AC は自己申告)。
- **read-only の維持**: `stats` は読むだけ (ADR 0002)。書き込むのは記録系コマンドに限定。

## 将来の拡張ポイント

- **chat TUI (Ctrl+S) 経路の AC プロンプト** (要件 026 との統合)。
- **`review` への per-cell 表示**: category テーブルの各マスに実装時間や自力 AC を色/記号で重ねる。
- **`--json` 出力**: record 系集計を機械可読で出し、外部可視化へ。
- **言語別コメントプレフィックス**: Go/C++ 等の解答に対応 (`//` 等)。`solvestat` のプレフィックスフックを差し替え。
- **category ツリー横断集計**: `abc/`/`arc/` 等の solve-stat も読む (日付の持ち方の差異吸収が前提)。
- **目標時間の粒度**: category×letter (`target.abc.d`) 別・個別 task 上書き・過去実績からのパーセンタイル目標の自動提案。
- **WA 回数 / 難易度**: 実提出 API が可能になれば自動取り込み (当面 Turnstile のため不可)。
- **中断除外の実装時間**: pause/resume を持つ精緻な計測 (当面は壁時計単純差)。

## 用語

- **solve-stat ブロック**: 解答ファイル冒頭に置く機械可読なコメントブロック。本要件の記録の格納先。
- **実装時間 (duration)**: 着手 (`started_at`) から完了 (`solved_at`) までの壁時計差、または手動指定値。
- **正答状況**: `ac` (AC できたか) と `editorial` (解説を見たか) の 2 bool。「自力 AC」= `ac && !editorial`。
- **5 軸スコア**: 知識 (knowledge)・翻訳 (translation)・計算量 (complexity)・実装 (impl)・検証 (verify) を各 0〜3 で自己評価した値。
- **記録済み solve**: solve-stat ブロックを持つ解答ファイル。集計セクションの母集団。
- **目標時間 (target)**: letter (難易度) ごとに config へ設定する目標実装時間。実装時間との差 (**目標比**) と、実装時間 ≤ 目標の割合 (**目標達成率**) を振り返りに使う。記録時に `target_ms` としてスナップショット。
- (`contest_id` = `abc457` / `contest_num` = `457` / `task_id` = `abc457_d` / `letter` = `d` は要件 002 に準拠)

## 関連ドキュメント

- `docs/tools/requirements/005-exercise-stats.md` (既存 `stats`。集計の母体・Now 注入の流儀)
- `docs/tools/requirements/015-fold-submit-into-test.md` / `docs/tools/decisions/0006-fold-submit-into-test.md` (提出準備・実提出/AC 取得が不可な理由)
- `docs/tools/requirements/043-submit-comment-out-debug.md` / `044-submit-precheck-confirm.md` (submit フローと確認プロンプトの前例)
- `docs/tools/requirements/002-exercise-abc-layout.md` (レイアウト解決・ID 用語)
- `docs/tools/decisions/0002-stats-readonly-exercise-tree.md` (stats read-only の決定。書き込みは記録系コマンドに限定)
- `docs/tools/usage/record.md` (利用手引) / `docs/tools/todo.md` の **AV.** (ロードマップ)
- `docs/tools/todo.md` (上位ロードマップ)
</content>
</invoke>
