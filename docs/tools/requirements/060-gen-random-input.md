# 問題の制約・入力形式からのランダム入力生成 (`atcoder gen` / chat `:gen`) 要件定義

## 概要

問題ページの **制約 (Constraints)** 節と **入力形式 (Input)** 節を自動認識し、それを満たす **ランダム入力**を生成する。生成した入力は stdout に出す・ファイルに保存する・`tests-extra/` に追加ケースとして落とす、のいずれかで消費できる。CLI 表面は独立サブコマンド `atcoder gen` と、対話 chat 内の `:gen` コマンドの **両方**を用意する。

方針は **ベストエフォート即生成**: 拾えた制約でその場でランダム入力を吐く。自然言語で書かれた構造的制約 (「A は順列」「グラフは連結」等) は原理的に取りこぼすため、取りこぼした変数は既定レンジ + 警告で埋め、**正しさは保証しない下準備ツール**として位置づける。出力の正しさ検証 (愚直解との突合せ = ストレステスト) は本要件のスコープ外とし、将来の拡張余地として設計に織り込む。

技術的成立性は調査済み: 問題ページ HTML 全体は既に `internal/testexec/fetch.go` の `fetchProblem()` が取得しており、制約・入力形式節も同じ HTML 内にある (今は保存していないだけ)。HTML パースは `antchfx/htmlquery` (XPath) が既に依存に入っている。外部ツール `online-judge-template-generator` が同種の解析で generator を自動生成している実績もあり、この方式が成立することの裏付けになる。

## 背景・目的

- サンプルは PASS でも提出で WA/TLE/RE、というとき、手元で大量・大規模な入力を試したい。現状のテストデータ手段は chat `:case` の**手入力** ([要件 024](024-interactive-case-builder.md)) か、他問題のサンプル流用しかなく、edge / 大規模ケースを自分で用意する摩擦が大きい。
- 問題を読めば「入力形式」と「制約」は必ず書いてある。ここから**機械的にランダム入力を作れる**なら、「WA に気づく → でかい/変な入力で再現を試す」までの距離が縮む。
- `:case` の入力ペイン前埋め ([要件 024](024-interactive-case-builder.md)) は「今打った入力」を種にするが、ランダム生成があれば chat 内で `:gen` → 生成入力を子に流す、という**探索的デバッグ**が回せる。空 `.out` の追加ケース (入力のみケース = 「落ちないことの確認」) は 024 が既に許容しているので、生成入力を `tests-extra/` に落とせば RE 検出の回帰ケースにそのまま化ける。

## スコープ

| 項目 | 当面のスコープ (この要件) | 将来の拡張余地 (別要件) |
|---|---|---|
| 認識対象 | 入力形式節の `<pre>` 構造 + 制約節の `lo ≤ VAR ≤ hi` 系 | 自然言語の構造的制約 (順列・連結グラフ・単調列・木・文字集合) |
| 生成対象 | 制約を満たす**ランダム入力** (`.in` 相当) | 期待出力 `.out` (= 参照解の実行結果) |
| 生成の正しさ | ベストエフォート。取りこぼしは既定レンジ + 警告 | 構造制約ヒント (アノテーション) による精度向上 |
| CLI 表面 | `atcoder gen <contest> --task <letter>` + chat `:gen` | `test --gen` 統合 (0005 の統一方針に沿うなら) |
| 消費 | stdout / `--out <path>` / `--save` で `tests-extra/` | repo 内保存、生成ケースの一括判定 |
| 検証 | **しない** (入力を作るだけ) | ストレステスト (参照解 vs 提出解の突合せ) / generator 雛形出力 |

### 境界

- **ストレステスト (参照解との突合せ) は本要件では作らない。** ユーザ選択は「ランダム入力を作るだけ」。ただし後段でストレステストを足せるよう、生成器 (`internal/gen`) は「入力を 1 つ生成する」責務に閉じ、判定ループ (`internal/testexec`) とは疎に保つ。
- **generator 雛形出力 (oj-template 流) も本要件では作らない。** ユーザ選択は「ベストエフォート即生成」。雛形出力は同じ解析結果 (`Spec`) を別レンダラで吐くだけで足せるよう、解析と生成を分離しておく。
- **解答ファイル (ユーザの提出コード) には一切触れない。** 生成物は stdout / `--out` 指定パス / cache 配下 `tests-extra/` のみ。
- `--refresh` の作用は**キャッシュのみ** (解析元セクションの再取得・再キャッシュ)。既存の不変則を踏襲。

## ディレクトリ構造 / スキーマ

問題ページから抽出した**生の**制約・入力形式テキストを、タスク単位キャッシュに新ファイル `gen.toml` として保存する。`gen` はこれを読んで**その場で**構造解析 (`Spec`) し、生成する。

```
$XDG_CACHE_HOME/atcoder-tools/<contest_id>/<task_id>/
  meta.toml            # 既存。time_limit_ms / url / fetched_at。変更なし
  tests/               # 既存。公式サンプル
    01.in  01.out
  tests-extra/         # 既存 (要件 024)。--save の落とし先
    01.in  01.out      # 生成ケースは空 .out で保存 = 入力のみケース
  gen.toml             # 新規。解析元となる生セクションのキャッシュ
```

### `gen.toml` スキーマ

**生テキストを source-of-truth として保存する** (解析済み `Spec` ではなく)。理由: 解析ヒューリスティックは今後改善されるので、生テキストを持っておけば **再 fetch なしで再解析**できる。`gen.toml` はタスク meta と同じ `BurntSushi/toml` で読み書きする。

```toml
fetched_at = 2026-07-01T12:34:56+09:00

[raw]
# 入力形式節の <pre> をそのまま (HTML エンティティは解除)
input_format = """
N M
A_1 A_2 \ldots A_N
u_1 v_1
:
u_M v_M
"""

# 制約節の InnerText をそのまま (LaTeX 記法込み)
constraints = """
1 \leq N \leq 2 \times 10^5
1 \leq M \leq N
1 \leq A_i \leq 10^9
1 \leq u_i, v_i \leq N
"""
```

| フィールド | 型 | 取得元 | 用途 |
|---|---|---|---|
| `fetched_at` | time | 取得時刻 | キャッシュ鮮度 / `--refresh` 判断 |
| `raw.input_format` | string | 入力形式節 (`<pre>` or `h3=入力` 直後) の InnerText | 構造解析の入力 |
| `raw.constraints` | string | 制約節 (`h3=制約` 直後の `<ul>`/段落) の InnerText | 範囲解析の入力 |

- どちらかのセクションが取れなくても `gen.toml` は書く (取れた分だけ)。両方空なら生成不能 (エラーハンドリング参照)。
- ID 用語は既存要件に準拠: `contest_id`=`abc457` / `contest_num`=`457` / `task_id`=`abc457_d` / `letter`=`d`。

### 内部モデル (`Spec` — 永続化しない中間表現)

`gen.toml.raw` を解析して得る、生成器が直接使う構造。**ファイルには保存しない** (毎回生テキストから組む)。

- **`Var`**: 変数の型と範囲。`Name` (基底名。`A_i` は `A`)、`Type` (`int`/`float`/`string`)、`Min`/`Max` (整数に解決した値、または他変数を含む式)、`Charset` (文字列型のみ、既定 `a-z`)。
- **`Block`**: 入力形式の 1 まとまり。種別:
  - `scalar` — 1 行のスカラ列 (`N M K`)。
  - `seq` — 配列 (`A_1 … A_N`)。`layout` = `row` (1 行空白区切り) / `col` (1 要素 1 行)。長さは変数参照 (`N`)。
  - `repeat` — 行テンプレートの反復 (`M` 行の `u_i v_i`)。`count` = 変数参照。
  - `grid` — `H` 行それぞれ長さ `W` の文字列。
  - `string` — 単一文字列 (`S`)。
- **`Spec`**: `Vars []Var` + 順序付き `Blocks []Block` + `Warnings []string` + `Coverage`(`full`/`partial`)。

## CLI 仕様

### `atcoder gen <contest> --task <letter>`

`test` と同じ位置引数 + `--task` の作法に揃える。

| 引数 / フラグ | 説明 |
|---|---|
| `<contest>` | contest_id (`abc457`)。`test` と同じパース |
| `--task <letter>` | 対象タスクの letter (必須。`test --task` と同義) |
| `-n, --count <N>` | 生成するケース数 (既定 1) |
| `-o, --out <path>` | stdout でなくファイルへ。`-n>1` のとき `<path>` をディレクトリ扱いし `01.in`, `02.in`, … を書く |
| `--save` | 生成入力を `tests-extra/` に**入力のみケース** (空 `.out`) として追加保存 (要件 024 の採番・`x` 表示 id に従う) |
| `--size <mode>` | `random` (既定, 範囲内で無作為) / `max` (全サイズを上限に = TLE 探索用) / `min` | 
| `--seed <n>` | 乱数シード (再現生成用)。省略時は毎回異なる |
| `--show-spec` | 生成せず、解析した `Spec` (変数・範囲・認識できた形式・警告) を表示 (認識結果の透明化) |
| `--refresh` | `gen.toml` の生セクションを再取得・上書き (キャッシュのみ) |

- `--out` と `--save` は併用可 (ファイルにも書き、tests-extra にも入れる)。`--show-spec` は生成系フラグ (`-n`/`-o`/`--save`/`--size`/`--seed`) と排他 (指定併用は exit 2)。

### 処理ステップ

`atcoder gen abc457 --task d`:

1. **引数検証**: contest_id / letter が不正なら exit 2。
2. **生セクションの用意**: `gen.toml` があり `--refresh` でなければそれを読む。無ければ問題ページを fetch し、制約・入力形式節を抽出して `gen.toml` に保存 (既存 fetch 経路を再利用 → 下記「影響範囲」)。
3. **解析**: `internal/gen.ParseSpec(raw)` で `Spec` と警告を得る。両セクションとも解析できず変数が 1 つも取れないなら exit 1。
4. **`--show-spec` なら** `Spec` を整形表示して終了 (exit 0)。
5. **生成**: `--seed` (or 乱数) で RNG を作り、`--count` 回 `Generate(spec, rng, size)` を呼ぶ。
6. **出力**: stdout (既定) / `--out` / `--save` に応じて書き出す。取りこぼし警告は stderr に出す (生成は続行、exit 0)。

### 出力イメージ

```
$ atcoder gen abc457 --task d --seed 42
5 3
7 2 9 4 1
2 5
1 3
4 5
```

```
$ atcoder gen abc457 --task d --show-spec
recognized input format:
  scalar : N M
  seq    : A_1..A_N  (row, len=N)
  repeat : u_i v_i   (count=M)
variables:
  N   int   1 .. 200000
  M   int   1 .. N
  A   int   1 .. 1000000000
  u   int   1 .. N
  v   int   1 .. N
warnings:
  (none)
coverage: full
```

```
$ atcoder gen abc457 --task f --show-spec
...
warnings:
  - variable K: no constraint found; defaulted to 1 .. 10^9
  - constraint "P is a permutation of 1..N" not understood; A treated as independent ints
coverage: partial
```

### chat `:gen` コマンド

対話 chat (`test --interactive` / `start` の `i`) の command モード ([要件 024](024-interactive-case-builder.md) / [ADR 0007](../decisions/0007-interactive-command-mode-trigger.md)) に `:gen` を足す。

| コマンド (別名) | 動作 |
|---|---|
| `:gen [n]` | 現在のタスクの `Spec` からランダム入力を 1 つ生成し、**insert の入力欄に前埋め**する (複数行対応)。`n` 指定時は `--size` 相当を将来拡張。ユーザは中身を編集して Enter で子に送信できる |
| `:gen` → `:case` 連携 | ケースビルダー ([要件 024](024-interactive-case-builder.md)) の `.in` ペイン前埋めソースとしても生成入力を選べる (将来) |

- chat では既存 `gen.toml` を使い、無ければ非同期 fetch (`:meta fetch` と同様の流儀, [要件 057](057-chat-meta-fetch.md)) で用意する。
- `:gen` は**入力欄への前埋めまで**で止め、送信 (子への流し込み) はユーザの Enter に委ねる (`:case` が builder を開くだけで子を触らないのと同じ非破壊方針)。未知タスク・解析不能時は command line に 1 行エラーを出して insert へ (副作用なし)。

## 動作仕様

| 観点 | 仕様 |
|---|---|
| 冪等性 (キャッシュ) | `gen.toml` は fetch 済みなら再利用。`--refresh` のみ再取得・上書き。生成そのものは乱数なので毎回変わる (`--seed` で固定可) |
| 再現性 | `--seed <n>` を与えれば同じ `Spec` から同じ入力列を再生成。バグ再現の共有に使える |
| `--refresh` 非破壊 | `--refresh` は `gen.toml` (と経路上取得する `tests/`/`meta.toml`) のみ。`tests-extra/` と解答ファイルには触れない |
| `--save` の採番 | 要件 024 の `extracase.Save` を再利用。空 `.out` で保存し、表示 id は `x01` 系。上書きせず新規追加 |
| 取りこぼしの扱い | 制約が取れない変数は既定レンジ (int: `1..10^9`, string: 長さ `1..10^5`・`a-z`) で埋め、warning を出す。構造制約 (順列・連結等) は無視して独立生成し warning。`coverage=partial` を示す |
| 既存ワークフロー共存 | `gen` は独立サブコマンドで既存 `test`/`run`/`start` の挙動を変えない。同じ task キャッシュ dir を共有するだけ。chat `:gen` は insert 既存挙動を壊さない (`Esc` 起点の command モード内に閉じる) |
| サイズ選択 | `--size max` は全変数・全長を上限で固定生成 (TLE の当たりを付ける)。`random` は各変数を範囲内一様、配列長も範囲内でランダム。`min` は下限 |

## 影響範囲

| ファイル / パッケージ | 変更内容 |
|---|---|
| `internal/testexec/fetch.go` | `fetchProblem` の抽出を拡張し、制約節 (`h3` が `制約`/`Constraints`) と入力形式節 (`h3` が `入力`/`Input`) の InnerText を取り出す関数を追加。取得結果を `gen.toml` に保存するフックを `ensureTests`/`EnsureTests` 経路に足す (既存の time limit / サンプル抽出と同じ `doc` から拾えるので追加 HTTP は不要) |
| 新規 `internal/gen/` | `Raw`/`Var`/`Block`/`Spec` 型、`ParseSpec(raw) (Spec, warnings)` (入力形式の `<pre>` 構造解析 + 制約の範囲解析)、`Generate(spec, rng, size) ([]byte, error)`、`gen.toml` の load/save |
| 新規 `cmd/atcoder/gen.go` | `cmdGen(args)` — 引数/フラグパース、生セクション用意、解析、生成、出力 (stdout/`--out`/`--save`)、`--show-spec` |
| `cmd/atcoder/main.go` | `builtins` / dispatch に `gen` 追加、`usage` 文字列更新 |
| `internal/cliargs/cliargs.go` | `--task`/`--out`/`--count`/`--size`/`--seed` を値フラグとして登録 (既存 `--task` 定義を共有) |
| `internal/complete/complete.go` | `gen` サブコマンド候補と `--task` 等のフラグ補完を追加 |
| `internal/extracase/` | `--save` から既存 `Save`(空 expected) を呼ぶだけ。変更は基本不要 (要件 024 で入力のみケースは許容済み) |
| `internal/ui/chat.go` | command モードに `:gen` を追加。生成入力を insert の textinput へ前埋め。`gen.toml` 未取得時は非同期 fetch (要件 057 の仕組みを流用) |
| `fixtures/run.sh` | ネットワーク無しで回すため、既知の `gen.toml` を置いた fixture で `atcoder gen --seed <固定> --show-spec` と生成を検証 (決定論的に範囲内・形式一致を assert)。exit code (成功=0 / 解析不能=1 / 引数誤り=2) を固定 |

### 新規 `internal/gen/` パッケージの責務 (API 素描)

```go
// Package gen は問題の制約・入力形式の生テキストを構造解析 (Spec) し、
// それを満たすランダム入力を生成する。判定 (testexec) とは疎に保つ。
package gen

// Raw は gen.toml に保存する生セクション (解析の入力)。
type Raw struct {
    FetchedAt   time.Time
    InputFormat string // 入力形式節の InnerText
    Constraints string // 制約節の InnerText
}

// Var は認識した変数の型と範囲。A_i のような添字変数は基底名 (A) に畳む。
type Var struct {
    Name    string
    Type    VarType // Int / Float / String
    Min     Expr    // 整数 or 他変数を含む式 ("N" 等)
    Max     Expr
    Charset string  // String 型のみ (既定 "a-z")
}

// Block は入力形式の 1 まとまり (scalar/seq/repeat/grid/string)。
type Block struct {
    Kind   BlockKind
    Tokens []string // scalar/repeat の変数列
    Var    string   // seq の配列基底名
    Count  Expr     // repeat/seq の反復・長さ
    Layout Layout   // seq: Row / Col
}

// Spec は生成器が直接使う中間表現 (永続化しない)。
type Spec struct {
    Vars     []Var
    Blocks   []Block
    Warnings []string
    Coverage Coverage // Full / Partial
}

// ParseSpec は生テキストから Spec を組む。認識できない部分は警告に落とし、
// 変数が 1 つも取れなければ error (生成不能)。
func ParseSpec(raw Raw) (Spec, error)

// Generate は size モードに従い spec を満たす入力を 1 つ返す。
func Generate(spec Spec, rng *rand.Rand, size SizeMode) ([]byte, error)

// Load / Save は gen.toml の読み書き (BurntSushi/toml)。
func Load(path string) (*Raw, error)
func Save(path string, r *Raw) error
```

### 制約解析ヒューリスティック (ベストエフォートの中身)

- 制約テキストを正規化: `\leq`/`≤`/`<=` → `≤`、`\times`/`×` → `*`、`10^5`/`10^{5}` → `100000`、`2 \times 10^5` → `200000`、桁区切りカンマ除去。
- `lo ≤ VAR ≤ hi` / `VAR ≤ hi` / `lo ≤ VAR` パターンを 1 行ずつ抽出し `Var` の範囲に割り当てる。`1 ≤ u_i, v_i ≤ N` のような複数変数同時記述にも対応。
- 添字変数 (`A_i`, `u_i`) は基底名に畳む。入力形式側の `A_1 … A_N` と突き合わせて配列と認識する。
- `S` が英小文字列、等の**文字集合**記述は簡易パターンのみ対応 (`英小文字`/`lowercase` → `a-z`)。拾えなければ既定 `a-z` + warning。
- **拾えない構造的制約**は無視し warning + `coverage=partial`。生成入力は形式的には妥当だが意味的制約 (順列・連結・単調) を満たさない可能性があると明示する。

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| contest_id / letter 不正 | メッセージを出して exit 2 |
| 未知フラグ / 排他フラグ併用 (`--show-spec` と生成系) | usage を出して exit 2 |
| 問題ページ取得失敗 (ネットワーク / 404) | エラー表示で exit 1。`gen.toml` は書かない |
| 制約・入力形式節が両方取れない | "could not locate constraints/input format" で exit 1 |
| 解析できたが変数 0 個 (形式不明) | "could not parse input format" で exit 1。原文を見るヒントを添える |
| 一部変数の制約が取れない | warning を stderr に出し、既定レンジで生成継続。exit 0 |
| 構造制約 (順列・連結等) を理解できない | warning + `coverage=partial`。生成継続。exit 0 |
| `--out` / `--save` 書き込み失敗 (権限等) | エラー表示で exit 1 |
| chat `:gen` で未取得・解析不能 | command line に 1 行エラー、insert へ戻る (chat の exit code には影響しない) |

## 非機能要件

- **既存非破壊**: `gen` は新サブコマンドで、`test`/`run`/`start`/`meta` の挙動・キャッシュ規約を変えない。chat `:gen` は `Esc` を押さない限り insert の既存挙動を変えない。
- **解答ファイル不可侵**: 生成物は stdout / `--out` パス / `tests-extra/` のみ。提出コードに触れない。
- **`--refresh` はキャッシュのみ**: `gen.toml` (と経路上の `tests/`/`meta.toml`) の再取得に限定。`tests-extra/`・解答は対象外。
- **exit code 規約**: 引数・フラグ誤り = 2 / 実行時失敗 (取得・解析不能・書き込み失敗) = 1 / 成功 (警告付き生成含む) = 0。
- **rate limit 配慮**: 生セクションは既存 fetch の同一 HTML から拾うため追加 HTTP を発生させない。`gen` 単独初回のみ 1 回 fetch。
- **再現性**: `--seed` で決定論的。fixture スモークもシード固定で回す。
- **前方互換**: `gen.toml` に**生テキスト**を持つことで、(a) 解析ヒューリスティック改善を再 fetch なしで反映でき、(b) 将来のストレステスト / generator 雛形出力が同じ `gen.toml`→`Spec` を入力にできる。解析と生成を分離し、判定ループと疎に保つ。
- **標準 `flag` 維持**: 外部 CLI フレームワークは導入しない。

## 将来の拡張ポイント

- **ストレステスト**: 参照解 (愚直解) を指定し、生成入力で `提出解 vs 参照解` の出力を突合せて WA を炙り出す (`atcoder gen --stress --ref brute.py` 等)。本要件の `Generate` + 既存 `runner`/`judge` を組み合わせるだけで足せるよう設計を分離済み。
- **generator 雛形出力** (oj-template 流): `Spec` を Python の `generate.py` 雛形にレンダリングし、ユーザが構造制約を手直しして使う。解析結果を別レンダラで吐く。
- **対話式スペック確認**: chat で `Spec` を提示し、範囲・構造を確認・補正してから生成。
- **構造的制約の理解**: 順列 (`permutation`) / 連結グラフ / 木 / 単調列 / 文字集合 の記述を認識し、意味的に妥当な入力を生成 (`coverage=full` の範囲を広げる)。
- **`test --gen` 統合**: 0005 の「test 一本化」方針に沿うなら、独立サブコマンドをサブモードに畳む選択肢。

## 用語

- **入力形式 (Input format)**: 問題ページの入力の与えられ方を示す節 (`<pre>` の `N M` / `A_1 … A_N` 等)。`Block` 列の抽出元。
- **制約 (Constraints)**: 各変数の範囲・性質を示す節。`Var` の範囲の抽出元。
- **Spec**: 生テキストを解析して得る、生成器が使う中間表現 (変数 + 形式ブロック + 警告 + カバレッジ)。永続化しない。
- **coverage**: `full` = 全変数の範囲を認識 / `partial` = 一部を既定レンジ・構造制約無視で埋めた。
- **入力のみケース**: `.out` が空の追加ケース ([要件 024](024-interactive-case-builder.md))。生成入力の `--save` 先。「落ちないことの確認」に使う。
- `contest_id` / `contest_num` / `task_id` / `letter` は既存要件 ([002](002-exercise-abc-layout.md)) に準拠。

## 関連ドキュメント

- 決定記録: [ADR 0008 — ランダム入力生成はベストエフォート解析 + 生セクションキャッシュ](../decisions/0008-gen-best-effort-raw-cache.md)
- 追加ケースの保存規約 (`tests-extra/`・空 `.out`・`x` 表示 id): [要件 024](024-interactive-case-builder.md)
- fetch / cache / meta の基盤: [要件 001](001-exercise-test.md) / [要件 046](046-meta-command.md)
- chat command モードと非同期 fetch: [ADR 0007](../decisions/0007-interactive-command-mode-trigger.md) / [要件 057](057-chat-meta-fetch.md)
- ロードマップ: [`todo.md`](../todo.md) の **AU. 制約・入力形式からのランダム入力生成**
- 利用手引: `docs/tools/usage/gen.md` (実装時に新規作成 — feature フェーズ)
