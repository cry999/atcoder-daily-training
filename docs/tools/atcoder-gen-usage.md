# `atcoder gen` 利用手引

`atcoder gen` は、問題ページの **制約 (Constraints)** と **入力形式 (Input)** をベストエフォートで
認識し、それを満たす **ランダム入力**を生成するサブコマンドです (要件 [060](requirements/060-gen-random-input.md))。
提出で WA/TLE/RE が出たときに、手元で大量・大規模な入力を試すための下準備に使います。

> **正しさは保証しません。** 生成するのは入力だけで、期待出力 (正解) は求めません。制約の
> うち自然言語で書かれた構造的なもの (「A は順列」「グラフは連結」「文字列は英小文字」など) は
> 認識できず、取りこぼした変数は既定レンジ + 警告で埋めます。何を認識できたかは `--show-spec`
> で確認できます。方針は [ADR 0008](decisions/0008-gen-best-effort-raw-cache.md)。

## 使い方

```sh
atcoder gen <contest> --task <letter> [flags]
```

- 対象は `test` と同じく contest + `--task` (短縮形 `d` → `<contest>_d`) で指定します。
- 初回は問題ページを 1 回だけ fetch し、制約 / 入力形式の**生テキスト**を
  `$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/gen.toml` にキャッシュします。以後はそれを
  読むので追加のネットワークアクセスは発生しません (`atcoder test` などで既に fetch 済みなら
  その時点で `gen.toml` も用意されています)。

### フラグ

| フラグ | 説明 |
|---|---|
| `--task <letter>` | 対象タスク (必須。`test --task` と同義) |
| `-n, --count <N>` | 生成するケース数 (既定 1) |
| `-o, --out <path>` | stdout でなくファイルへ。`-n>1` のとき `<path>` をディレクトリ扱いし `01.in`, `02.in`, … を書く |
| `--save` | 生成入力を `tests-extra/` に**入力のみケース** (空 `.out`) として追加保存する (要件 [024](requirements/024-interactive-case-builder.md) の採番・`x` 表示 id に従う) |
| `--size <mode>` | `random` (既定, 範囲内で無作為) / `max` (全サイズを上限に = TLE 探索用) / `min` (下限) |
| `--seed <n>` | 乱数シード (再現生成用)。省略時は毎回異なる |
| `--show-spec` | 生成せず、認識した変数・範囲・入力形式・警告・カバレッジを表示する |
| `--refresh` | `gen.toml` の生セクションを再取得・上書きする (キャッシュのみ) |

- `--show-spec` は生成系フラグ (`-n`/`--out`/`--save`/`--size`/`--seed`) と併用できません (exit 2)。
- `--out` と `--save` は併用できます (ファイルにも書き、`tests-extra/` にも入れる)。

## 例

### 認識結果を確認する

```
$ atcoder gen abc457 --task d --show-spec
recognized input format:
  scalar : N M
  seq    : A_1..A_N  (row, len=N)
  repeat : u_i v_i   (count=M)
variables:
  A    int  1 .. 1000000000
  M    int  1 .. N
  N    int  1 .. 200000
  u    int  1 .. N
  v    int  1 .. N
warnings:
  (none)
coverage: full
```

`coverage: partial` のときは、既定レンジで埋めた変数や理解できなかった構造的制約が warnings に
出ます。生成入力は形式的には妥当ですが、意味的制約 (順列・連結など) を満たさないことがあります。

### ランダム入力を作る

```
$ atcoder gen abc457 --task d --seed 42
5 3
7 2 9 4 1
2 5
1 3
4 5
```

- `--seed` を与えると同じ入力を再生成できます (バグ再現の共有に便利)。
- `--size max` は全変数・全長を上限にして生成します (制限時間ぎりぎりの大きさで TLE の当たりを
  付ける用途)。

### ファイル / 追加ケースに落とす

```sh
atcoder gen abc457 --task d -n 5 -o gen-cases      # gen-cases/01.in .. 05.in を書く
atcoder gen abc457 --task d --save                 # tests-extra/ に入力のみケースを 1 つ追加
```

`--save` で追加した入力のみケース (空 `.out`) は、`atcoder test` / `start` の判定ループに公式
サンプルの後ろ (`x01` …) として載り、「大きな入力でも落ちないこと」の回帰チェックになります
(要件 [024](requirements/024-interactive-case-builder.md))。

## 対話 chat 内から (`:gen`)

`atcoder test --interactive` / `atcoder start` の chat では、command モード (`Esc` → `:`) で
**`:gen`** を実行すると、その問題の制約 / 入力形式からランダム入力を 1 つ生成して**入力欄に
前埋め**します。中身を編集して Enter で子プロセスへ送れます (送信するかはユーザ次第)。初回は
`gen.toml` を非同期に用意するため一瞬 `(生成中…)` と出ます。認識できなかった制約は `warning:`
行で示されます。

## 認識できるもの / できないもの

**認識できる (代表例):**

- スカラ行 (`N M K`)、横並び配列 (`A_1 A_2 … A_N`)、縦の反復 (`M` 行の `u_i v_i` を `:` で表す
  グラフ辺リスト)、縦並び配列、単一文字列 (`S`)。
- `1 ≤ N ≤ 2×10^5` / `1 ≤ A_i ≤ 10^9` / `1 ≤ M ≤ N` のような数値 (と他変数参照) の範囲。LaTeX
  記法 (`\leq`, `\times`, `10^5`) や `≤` / `<=` のゆれを吸収します。
- 絶対値の制約 `|A_i| ≤ 10^9` は整数の対称範囲 `-10^9 ≤ A_i ≤ 10^9` として扱います。ただし
  問題文に「文字列 / 英小文字 / lowercase」等のキーワードがある場合は `|S|` を**文字列長**と
  解釈します (文字列と絶対値の両方が混在する稀な問題では誤ることがあります)。

**認識できない (取りこぼす → 警告 + `coverage: partial`):**

- 「A は順列」「グラフは連結」「木である」「相異なる」「単調増加」などの**構造的制約**。
- 制約の書かれていない変数 (既定レンジ int `1..10^9` / 文字列長 `1..10^5`・`a-z` で埋めます)。
- グリッド (`H` 行 × `W` 列) などの複雑な入力形式。

取りこぼしがある問題では、生成入力をそのまま鵜呑みにせず `--show-spec` で確認するか、必要な
制約を手で調整した入力に直してから使ってください。

## exit code

| 状況 | exit code |
|---|---|
| 生成成功 (取りこぼし警告付きを含む) | 0 |
| 引数・フラグ誤り (contest/`--task` 不正、排他フラグ併用、不正な `--size` 等) | 2 |
| 取得失敗 / 制約・入力形式の節が無い / 形式を解析できない / 書き込み失敗 | 1 |

## 関連

- 仕様: [要件 060](requirements/060-gen-random-input.md)
- 方針の決定記録: [ADR 0008](decisions/0008-gen-best-effort-raw-cache.md)
- 追加ケース (`tests-extra/`・入力のみケース): [要件 024](requirements/024-interactive-case-builder.md) / [`atcoder test` 手引](atcoder-test-usage.md)
- キャッシュ層の準備・補正: [`atcoder meta` 手引](atcoder-meta-usage.md)
