# 位置引数とフラグの順序非依存 (`internal/cliargs`) 要件定義

## 概要

`atcoder <sub> <contest> --task d` のように**位置引数を先頭に置かないと動かない**現状を改め、`atcoder test --task d abc457` のように**位置引数とフラグを任意の順序で混在**できるようにする。Go 標準 `flag` は最初の非フラグ引数で解析を打ち切り (インターリーブ不可)、さらに各サブコマンドは `contest := args[0]` と位置引数を先頭で手剥がししてから `flags.Parse(args[1:])` しているため、位置引数は先頭限定になっている。これを、`flag.Parse` の**前に薄い前処理 (`internal/cliargs.Split`) を 1 枚噛ませて**引数を「フラグ + 値」と「位置引数」に分離する方式で解く。`flag` 本体・flag 定義・exit code 規約は不変。

## 背景・目的

- Go の `flag` は GNU 風のインターリーブをしない。加えて repo の慣習が「位置引数を `args[0]` で先に剥がす」ため、`atcoder test abc457 --task d` は通るが `atcoder test --task d abc457` は通らない (`args[0]` が `--task` になる)。
- 競技中はフラグを足したり消したりしながらコマンドを打ち直すので、「contest をいちいち先頭に戻す」のは地味なフリクション。順序を気にせず打てるのが自然。
- 軽量ライブラリ (pflag) 導入も検討したが、(1) 全サブコマンドの flag 定義書き換え、(2) `-case` のような単ダッシュ長フラグの意味が変わる非互換、(3) 自前 dispatch/補完/usage と二重、というコストがある。一方この repo は **位置引数とフラグを分離する歩進ロジックを `internal/complete` に既に実装・保守している** (`valueFlags` + `positionals`)。これを共有すれば**依存ゼロ・DRY**で解ける (比較は会話ログ参照)。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象サブコマンド | **位置引数とフラグを両方持つ** `test` / `start` / `review` / `new abc` | `config`/`completion` (位置引数のみ・フラグ無し)・`stats`/`update` (フラグのみ) は順序問題が無いので対象外 |
| 分離の単位 | グローバルな value-flag 集合 (どのフラグが次トークンを値として食うか) | サブコマンド別の flag 定義から value-flag を自動導出 |
| value-flag 知識の所在 | 新 `internal/cliargs` に一本化。`internal/complete` も共有 | flag 定義 (`flags.*`) からの生成で手動同期を不要に |
| flag 構文 | Go `flag` のまま (`-x`/`--x` 両対応・`--x=v`・`--` 終端) | — |

### 対象を 4 サブコマンドに絞る理由

順序問題が起きるのは「位置引数 **と** フラグを両方取る」コマンドだけ。`stats`/`update` はフラグのみ (位置引数無し)、`config`/`completion` は位置引数のみ (フラグ無し) なので、フラグと位置引数の前後関係が存在せず、現状で困らない。触る面を最小にする。

## ディレクトリ構造 / 新規パッケージ

```
internal/cliargs/
  cliargs.go       # valueFlags (canonical) + TakesValue + Split
  cliargs_test.go
```

`internal/complete` が今持つ `var valueFlags` をここへ移し、complete は `cliargs` を import して共有する (single source of truth)。`cliargs` は他の internal/cmd に依存しない葉パッケージ (循環なし)。

## CLI 仕様

新フラグ・新サブコマンドは**増やさない**。既存コマンドの**引数の並べ方が自由になるだけ**で、出力も exit code も不変。

```
# すべて等価になる:
atcoder test abc457 --task d
atcoder test --task d abc457
atcoder test --task d abc457 -s --timeout 5s
atcoder test -s abc457 --task d

# 複数位置引数のサブコマンドも順序自由:
atcoder new abc --refresh abc457          # = atcoder new abc abc457 --refresh
atcoder review --month abc                # = atcoder review abc --month
```

### 処理ステップ (各対象サブコマンド)

従来:
```go
contest := args[0]
... flags.Parse(args[1:]) ...
```
変更後:
```go
flagArgs, positionals := cliargs.Split(args)
if len(positionals) < 1 { return 2, errors.New("contest is required") }
contest := positionals[0]
... flags.Parse(flagArgs) ...   // positionals を含まないので flag は最後まで解析される
```

- `cliargs.Split(args)` は args を左から歩進し、`(flagArgs, positionals)` に分ける:
  1. `--` を見たら、それ以降は全て positional (終端)。
  2. `-` 始まり (長さ 2 以上) はフラグ:
     - `=` を含む (`--task=d`) → 値が内包されているので flagArgs に 1 つ追加。
     - 名前が value-flag (`cliargs.TakesValue`) → flagArgs にフラグ + 次トークン (値) を追加し、次を消費。
     - それ以外 → bool フラグとして flagArgs に追加。
  3. それ以外 (`-` 単体含む) は positional。
- `flags.Parse(flagArgs)` は positional を含まないので、Go flag の「最初の非フラグで停止」に当たらず全フラグを解析できる。

### 出力イメージ

```
$ atcoder test --task d abc457        # フラグ先頭でも通る
abc457_d  contest=abc457  ...
[01]  PASS  28 ms
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| 位置引数の順序 | フラグの前・後・間、どこでも可。複数位置引数は**出現順**で `positionals[0,1,…]` |
| `--flag=value` | 値内包として扱い、次トークンは消費しない |
| `--` 終端 | 以降は全て positional (Go flag と同じ) |
| value-flag の値 | `--task d` の `d`、`--in -` の `-` などは値として flagArgs 側に付き、positional に混じらない |
| bool フラグ | 値を取らない (`--refresh`/`-s`/`--watch` 等)。直後のトークンは独立に判定 |
| 未知フラグ | Split は value-flag 集合に無いので bool 扱い → `flags.Parse` が "flag provided but not defined" で **exit 2** (従来どおりエラー) |
| value-flag の値欠落 | `atcoder test abc457 --task` → `flags.Parse` が "flag needs an argument" で **exit 2** |
| 既存の並び | `atcoder test abc457 --task d` (位置引数先頭) も従来どおり動く (非破壊) |
| 位置引数のみ/フラグのみのコマンド | 変更しない (`config`/`completion`/`stats`/`update`/`commit`/`version`) |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| 新規 `internal/cliargs/cliargs.go` | `valueFlags` (canonical) + `TakesValue(name) bool` + `Split(args) (flagArgs, positionals []string)` |
| 新規 `internal/cliargs/cliargs_test.go` | `Split` の表駆動テスト (順序混在・`=`・`--`・value/bool・stdin marker・未知フラグ) |
| `internal/complete/complete.go` | ローカル `valueFlags` を撤去し `cliargs.TakesValue` を使用。`positionals(words)` は `cliargs.Split(words[1:])` の positional 部に委譲 (歩進ロジックも一本化) |
| `cmd/atcoder/test.go` | `args[0]` + `Parse(args[1:])` を `cliargs.Split` 経由に |
| `cmd/atcoder/start.go` | 同上 |
| `cmd/atcoder/review.go` | 同上 (位置引数 = category) |
| `cmd/atcoder/new.go` | `new abc <contest>` の sub-args を `cliargs.Split` 経由に (mode 語 `abc` は dispatch 済み) |
| `fixtures/run.sh` | フラグ先頭・混在順の `run_case` を追加 (exit 0) + 既存の位置引数先頭が不変なことを確認 |
| `docs/tools/usage/test.md` ほか | 「引数の順序は自由」の一文を追記 |

### 新規 API スケッチ (`internal/cliargs`)

```go
package cliargs

// valueFlags は「次のトークンを値として取る」フラグ名の集合 (canonical)。
// flag 定義 (cmd/atcoder/*.go の flags.*) と一致させる。complete も参照する。
var valueFlags = map[string]bool{ /* --task, --tasks, --layout, --timeout,
    --case, -c, --in, -i, --out, -o, --jobs, -j, --tolerance, --last, -l */ }

// TakesValue はそのフラグ名 (先頭の "-"/"--" 込み) が値を取るか。
func TakesValue(name string) bool

// Split は引数列を「フラグ + その値」と「位置引数」に分離する。
// 順序は保持し、flagArgs は flag.Parse へ、positionals は contest/category 等に使う。
func Split(args []string) (flagArgs, positionals []string)
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| 位置引数 (contest/category) が 1 つも無い | **exit 2** (`contest is required` 等、従来メッセージ維持) |
| 未知フラグ | `flags.Parse` が **exit 2** |
| value-flag の値欠落 | `flags.Parse` が **exit 2** |
| Split 自体は失敗しない | 文字列分離のみ。エラーは後段の `flags.Parse` / 位置引数チェックで出す |

## 非機能要件

- **既存非破壊**: 位置引数を先頭に置く従来の打ち方は完全に動く。出力・exit code も不変。fixture で両順序を固定する。
- **DRY / 単一情報源**: value-flag 集合を `cliargs` に一本化し、`complete` と parser が共有する。flag を足したらここ 1 か所を更新。
- **Go flag 意味論の維持**: `-x`/`--x` 両対応・`--x=v`・`--` 終端を保つ。外部依存ゼロ。
- **局所性**: 介入は対象 4 サブコマンドの `Parse` 前 1 行と新パッケージのみ。

## 将来の拡張ポイント

- flag 定義 (`flag.FlagSet`) を走査して value-flag を自動導出し、`valueFlags` の手動同期を不要にする。
- `config`/`completion` 等の複数位置引数コマンドも `Split` に寄せて統一 (現状はフラグが無く順序問題が無いので保留)。

## 用語

- **value-flag**: 次のトークンを値として取るフラグ (`--task d` の `--task`)。bool フラグ (`--refresh`) と区別する。
- **位置引数 (positional)**: フラグでも値でもない引数 (`contest_id` / category / `new abc` の contest 等)。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- `internal/complete/complete.go` (`valueFlags` の現所在・補完の位置引数判定)
- `docs/tools/usage/completion.md` (補完が同じ value-flag 知識を使う)
- `docs/tools/usage/test.md` ほか各 usage (引数順序の追記先)
