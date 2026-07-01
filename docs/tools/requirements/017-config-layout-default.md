# `config` に既定レイアウト (`layout` キー + `ATCODER_LAYOUT`) を取り込む 要件定義

## 概要

解答ファイルのレイアウト (`auto` / `abc` / `exercise`) を **毎回 `--layout` で渡さなくても** 既定値として固定できるようにする。既定値は **環境変数 `ATCODER_LAYOUT`** と **設定ファイル `config.toml`** の 2 段で持つ。設定の確認・変更は専用サブコマンドを足さず、既存の汎用 **`atcoder config`** (要件 009) の枠組みに `layout` キーを 1 つ登録して `atcoder config get/set layout` で行う。

解決順は `--layout` フラグ > `$ATCODER_LAYOUT` > `config.toml` の `layout` > `auto`。precedence は純粋関数 `layout.Resolve` に集約する。MVP A (`002-exercise-abc-layout.md`) の `layout` パッケージ・`--layout` フラグと、ユーザ設定ファイル (`007-atcoder-config.md` / 汎用 config サブコマンド `009`) の上に「既定レイアウトの解決層」を足すだけで、解答・キャッシュには触れない。

## 背景・目的

- 現状レイアウトは `test`/`run`/`submit` (いずれも `atcoder test` に統合済み) で `--layout` フラグ (デフォルト `auto`) を都度指定する。`auto` は `abc<NNN>` を ABC、それ以外を Exercise に振り分けるが、**ある期間ずっと特定レイアウトで作業したい** ときに毎回フラグを打つのが煩わしい。
- 環境変数でシェルセッション単位の上書きを、設定ファイルで永続的な既定を持てると運用が楽。`007`/`009` で導入した `internal/config` (XDG_CONFIG_HOME 配下の `config.toml`) と汎用 `config` サブコマンドをそのまま使い、`layout` キーを足す。
- **専用 `layout` サブコマンドは作らない**。当初の設計 (旧ブランチ `feat-atcoder-layout-config`) は `atcoder layout show/set/unset` を想定していたが、その後 `009` で汎用 `config show/get/set/path` が入ったため、設定の閲覧・編集はそちらに一本化する (サブコマンドの重複を避ける)。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 設定対象 | レイアウト既定値 (`layout` キー) | timeout / tolerance / jobs など |
| 永続化 | `007`/`009` の `config.toml` に トップレベル `layout` キーを追加 | プロファイル切替、リポジトリローカル設定 |
| 上書き | 環境変数 `ATCODER_LAYOUT` | — |
| 設定 IF | 既存 `atcoder config get/set layout` (専用サブコマンド無し) | — |
| レイアウト値 | `auto` / `abc` / `exercise` (既存と同じ) | `adt` 等 |

### 既存 `--layout` フラグ・`007`/`009` config との関係 (境界)

- `--layout` フラグはそのまま残す。コマンド単位の明示指定で最優先。
- `009` の汎用 config は既知キーをレジストリ (`internal/config` の `fields`) に登録し、`set` は汎用 map に書いて未知キー・他セクションを保全する。本機能は `layout` を **string enum キー** として 1 エントリ追加する。専用 `Save` は新設しない (`009` の `loadRaw`/`saveRaw` 経路に乗る)。
- レイアウトだけは env 層が挟まるため、`007` の「flag デフォルト注入」方式ではなく専用の `layout.Resolve` で flag > env > config > auto を解決する。
- `auto` の検出ロジック (`layout.Detect`) は不変。

## 設定の解決順 (precedence)

| 優先 | 出所 | 値の例 |
|---|---|---|
| 1 | コマンドの `--layout` フラグ (指定時) | `--layout abc` |
| 2 | 環境変数 `ATCODER_LAYOUT` (空でなければ) | `ATCODER_LAYOUT=abc` |
| 3 | 設定ファイル `config.toml` の `layout` | `layout = "abc"` |
| 4 | 既定 (`auto`) | — |

- 値は `auto` / `abc` / `exercise` のいずれか。`auto` は contest_id から検出 (`abc<NNN>`→abc、他→exercise)。
- `--layout` フラグのデフォルトを従来の `"auto"` から **空文字 `""`** に変える (「未指定」を表現)。空なら段 2 以降にフォールバック。`--layout auto` 明示時は段 1 で確定し検出に回る (従来と同じ)。
- 不正な値 (例 `ATCODER_LAYOUT=foo`) は出所に関わらず "unknown layout" で **exit 2**。

## ディレクトリ構造 / スキーマ

`007`/`009` と同じ `config.toml` に `layout` トップレベルキーを足す。

```toml
# $XDG_CONFIG_HOME/atcoder-daily-training/config.toml
layout = "abc"        # ← 本要件で追加 (test/run/submit 横断の既定)

[test]
side_by_side = true   # 007 で導入済み
```

| フィールド | 型 | 説明 |
|---|---|---|
| `layout` | string (enum: `auto`/`abc`/`exercise`) | 既定レイアウト。未設定なら段 4 の `auto` |

- `layout` は特定サブコマンドに属さない横断設定なので **トップレベルキー** として持つ。TOML はトップレベルキーをテーブルより先に書く必要があるため、`Config` struct でも `Test` セクションより前に declare する。
- 未知キーは無視 (前方/後方互換)。`007`/`009` の `[test]` セクションは温存する。

## CLI 仕様

専用サブコマンドは追加しない。既存 `atcoder config` (要件 009) の `show`/`get`/`set`/`path` でそのまま扱う。

### 設定する

```
$ atcoder config set layout abc
set layout = abc  (/home/user/.config/atcoder-daily-training/config.toml)
```

不正値は exit 2:

```
$ atcoder config set layout foo
atcoder config: invalid config value: "foo" (layout は auto/abc/exercise)
# exit 2
```

### 確認する

```
$ atcoder config get layout
abc

$ atcoder config show
layout = abc
test.side_by_side = false
```

- `layout` 未設定時、`config get layout` / `config show` は **`auto`** を表示する (config 層で適用される実効既定値。env / flag の上書きは含まない)。

### 解除する

汎用 `config unset` は要件 016 (alias) で新設予定。本要件の範囲では `config set layout auto` で実効的に既定 (`auto`) に戻せる (`auto` を明示的に書く形)。

### 処理ステップ (`atcoder test` 側)

1. `--layout` をパース (デフォルト `""`)。
2. `resolveLayout(flag, contest)` が `ATCODER_LAYOUT` → `config.toml` の `layout` → `auto` の順で既定値を引く (`layout.Resolve`)。
3. 解決値を `layout.Parse(value, contest)` に渡して `Layout` を得る。不正値は exit 2。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `--layout abc` 明示 | env / config を無視して abc (段 1) |
| `--layout` 省略 + `ATCODER_LAYOUT=exercise` | exercise (段 2) |
| `--layout` 省略 + env 未設定 + config `layout="abc"` | abc (段 3) |
| すべて未設定 | `auto` 検出 (段 4、従来と同一) |
| `ATCODER_LAYOUT=""` (空) | 未設定扱い、段 3 へ |
| 不正なレイアウト値 (どの出所でも) | "unknown layout ..." で exit 2 |
| `config set layout <不正値>` | "invalid config value" で exit 2 (書き込まない) |
| `config.toml` 読み取り失敗 (権限等) | エラー表示で exit 1 |

- **既存非破壊**: env も config の `layout` も無ければ、`atcoder test` の挙動は従来 (`--layout auto` 相当) と一致。`007` の `[test]` 設定も不変。
- **読み取り側は副作用なし**: `atcoder test` は config を読むだけ。書くのは `config set` のみ。
- **解答ファイルに触れない**: 設定ファイルのみ対象。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/layout/layout.go` | `Resolve(flag, env, cfg, contestID)` (precedence 集約)・`Known(name)`・`Names()` 追加 |
| `internal/layout/layout_test.go` | `Resolve`/`Known`/`Names` テスト追加 |
| `internal/config/config.go` | `Config` に `Layout` トップレベルキー追加 (`Test` より前に declare)・package doc に env 層を追記 |
| `internal/config/keys.go` | `fields` に `layout` (enum) エントリ追加。`field` に値候補 `cands` を持たせ `ValueCandidates` を拡張 |
| `internal/config/keys_test.go` | `layout` の get/set/不正値・候補のテスト追加 |
| `cmd/atcoder/flags.go` | `--layout` デフォルトを `""` に変更、help 文更新。`resolveLayout(flag, contest)` ヘルパ + `ATCODER_LAYOUT` 定数を追加 |
| `cmd/atcoder/test.go` | `layout.Parse(*layoutFlag, contest)` を `resolveLayout(*layoutFlag, contest)` に置換 |
| `cmd/atcoder/main.go` | 変更なし (`--layout <auto\|abc\|exercise>` の syntax 表記は既に正確。専用サブコマンドは追加しない) |
| `fixtures/run.sh` | `ATCODER_LAYOUT` unset 下で config set/get layout・不正値 (exit 2)・env/config/flag precedence smoke |
| `docs/tools/usage/config.md` | `layout` キーと precedence を追記 (config usage に統合) |
| `docs/tools/todo.md` | ロードマップに DONE 記載 |

### `internal/layout` への追加

```go
// Names は既知レイアウト名を正規順 (auto, abc, exercise) で返す (補完・検証の単一情報源)。
func Names() []string

// Known はレイアウト名が既知 (auto/abc/exercise) かを返す (config set の検証用)。
func Known(name string) bool

// Resolve は precedence (flag > env > config > auto) で 1 つの Layout に解決する。
// value は採用値、source は出所 ("flag"/"env"/"config"/"default")。不正値は err。
func Resolve(flag, env, cfg, contestID string) (lay Layout, value, source string, err error)
```

### `internal/config` への追加

```go
type Config struct {
    Layout string     `toml:"layout,omitempty"` // ← 追加 (Test より前に declare)
    Test   TestConfig `toml:"test"`
}
```

`keys.go` の `field` に値候補スロットを足し、`layout` を enum キーとして登録する:

```go
type field struct {
    key   string
    kind  string
    cands []string // ← 追加: 値候補 (補完 + set 検証)。空なら kind=="bool" の既定挙動
    repr  func(*Config) string
    set   func(m map[string]any, raw string) error
}
```

`layout` の `repr` は `cfg.Layout` が空なら `"auto"` を返す (実効既定値)。`set` は `layout.Known` で検証して不正値を `ErrInvalidValue` で弾く。`ValueCandidates` は `cands` があればそれを返し、無ければ従来の bool 候補。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `config set layout` の引数欠落 | usage 表示 (既存 config の挙動) | 2 |
| `config set layout <不正値>` | "invalid config value" (`ErrInvalidValue`) | 2 |
| `--layout` / env / config の不正値 (実行時) | "unknown layout ..." | 2 |
| `config.toml` 読み取り I/O・文法エラー | "config parse error" (`ErrParse`) | 2 |
| `config.toml` 書き込み失敗 | エラー表示 | 1 |
| 正常 | 表示 / 更新 | 0 |

## 非機能要件

- **既存非破壊 / 後方互換**: env・config の `layout` 未設定なら従来挙動と一致。`--layout` は最優先。`007`/`009` の `[test]` 設定・汎用 config の挙動も温存。
- **決定的・テスト可能**: precedence は `layout.Resolve` の純粋関数に集約しユニットテスト。config は tmp `XDG_CONFIG_HOME` で round-trip テスト。
- **副作用の局所化**: 書き込みは `config set` のみ。`atcoder test` は read-only。
- **XDG 準拠**: `007` の `internal/config` をそのまま利用。
- **単一情報源**: 既知レイアウト名は `layout.Names()` に集約し、config の検証・補完候補もそこを参照する (値リストの二重管理を避ける)。

## 将来の拡張ポイント

- **他の既定値**: `timeout` / `tolerance` / `jobs` を同じ仕組みで。env 層が要るものは `Resolve` 同様の解決関数を用意。
- **新レイアウト**: `adt` 等を `layout.Names()`/`Parse` に足せば env/config/補完がそのまま受け付ける。
- **`config unset`**: 要件 016 (alias) で新設される汎用 `config unset <key>` が入れば、`config unset layout` で明示的な未設定化 (auto フォールバック) ができる。

## 用語

- **レイアウト**: 解答ファイル配置規約 (`auto`/`abc`/`exercise`)。定義は `002-exercise-abc-layout.md`。
- **既定レイアウト (effective default)**: `--layout` 抜きで適用されるレイアウト。env → config → auto の順で決まる。
- **出所 (source)**: 既定を決めた段 (`flag`/`env`/`config`/`default`)。

## 関連ドキュメント

- `docs/tools/todo.md` (上位ロードマップ)
- `docs/tools/requirements/002-exercise-abc-layout.md` (layout パッケージ・`--layout`・auto 検出)
- `docs/tools/requirements/007-atcoder-config.md` (ユーザ設定ファイル `internal/config` の定義元)
- `docs/tools/requirements/009-atcoder-config-subcommand.md` (汎用 `config` サブコマンドとキーレジストリ)
- `docs/tools/requirements/016-config-alias.md` (将来の `config unset`)
- `docs/tools/usage/config.md` (利用手引)
