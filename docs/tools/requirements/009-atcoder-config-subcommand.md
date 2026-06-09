# `atcoder config` サブコマンド 要件定義

## 概要

ユーザ設定ファイル (`config.toml`) を **CLI から閲覧・編集** できる `atcoder config` サブコマンドを足す。`config show` / `get` / `set` / `path` の 4 つで、設定ファイルを手で開かずに既定値を確認・変更できるようにする。設定の実体・スキーマ・優先順位は既存の `internal/config` (要件 007) をそのまま土台にし、本要件はその「編集 UI」を被せる。

`docs/tools/todo.md` の「L. `config` サブコマンド」の要件詳細。要件 007 (`docs/tools/requirements/007-atcoder-config.md`) で導入した設定層 (`[test] side_by_side`) の上に乗る。

## 背景・目的

- 要件 007 で設定ファイル自体は導入したが、編集は「`~/.config/atcoder-daily-training/config.toml` を手で開いて TOML を書く」必要がある。所在を覚え、TOML 文法を間違えないよう気を遣うのは摩擦。
- `atcoder config set test.side_by_side true` の 1 コマンドで設定でき、`config show` で現在値を一覧、`config path` で所在を確認できれば、設定ファイルの存在をほぼ意識せずに既定値を管理できる。
- キーと型を CLI 側が知っているので、**未知キー・型不一致をその場で弾ける** (手書き TOML だと `atcoder test` 実行時まで気づけない)。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| サブコマンド | `config show` / `config get <key>` / `config set <key> <value>` / `config path` | `config unset <key>` / `config edit` ($EDITOR 起動) |
| 対象キー | 要件 007 の既知キー (`test.side_by_side`) | 設定項目が増えれば自動的に対象 (キーレジストリ駆動) |
| キー形式 | ドット区切り `<section>.<field>` (例 `test.side_by_side`) | ネスト 3 階層以上 |
| 値の型 | bool (`true`/`false`) | int / float / string / enum (レジストリに型を足す) |
| 書き込み | `config.toml` を作成 / 更新。未知キー・セクションは保全 | コメント保全 (TOML round-trip) |

### 既存設定層 (要件 007) との分担

- **設定の実体** (スキーマ `Config`・XDG パス解決 `Path()`・読み込み `Load()`・優先順位 `flag > config > default`) は `internal/config` が持つ (要件 007)。
- 本要件が足すのは **キーレジストリ** (既知キーと型・get/set 方法の一覧) と、それを使う **`config` サブコマンド**。`atcoder test` 等の既定値適用ロジックは無改修。
- `config set` で書いた値は、次回以降の `atcoder test` が `Load()` 経由で読む。両者は同じ `config.toml` を介して自然に繋がる。

## ディレクトリ構造 / スキーマ

設定ファイルの所在・スキーマは要件 007 のまま (本要件で新たなファイルは作らない)。

```
$XDG_CONFIG_HOME/atcoder-daily-training/config.toml   # 既存 (007)。config set が無ければ作成する
```

```toml
[test]
side_by_side = true
```

### キーレジストリ

CLI が扱える設定キーを「ドットキー → 型・get/set」の表として `internal/config` 内に持つ。`config get/set/show` と補完がこの 1 か所を参照する (キーを足す = レジストリに 1 行足す)。

| ドットキー | 型 | 対応する `Config` フィールド | 値候補 |
|---|---|---|---|
| `test.side_by_side` | bool | `Config.Test.SideBySide` | `true` / `false` |

## CLI 仕様

```
atcoder config show                 # 既知キーと現在値を一覧
atcoder config get <key>            # 1 キーの現在値を出力
atcoder config set <key> <value>    # 1 キーを書き込み (config.toml を作成/更新)
atcoder config path                 # config.toml の絶対パスを出力
```

| サブコマンド | 引数 | 説明 |
|---|---|---|
| `show` | なし | 既知キーすべてを `key = value` 形式で 1 行ずつ出力。値は `config.toml` 反映後 (無ければ既定値) |
| `get` | `<key>` | 指定キーの現在値だけを出力 (スクリプト向け、値のみ) |
| `set` | `<key> <value>` | 指定キーに値を書き込む。`config.toml` が無ければ親 dir ごと作成。既存の他キー・未知キーは保全 |
| `path` | なし | `config.toml` の絶対パスを出力 (存在しなくても所在を示す) |

### 処理ステップ (`config set`)

`atcoder config set test.side_by_side true`:

1. **キー検証**: 既知キーレジストリに無ければ exit 2 (`unknown config key`、既知キー一覧を併記)。
2. **値パース**: キーの型に従い `value` を解釈 (bool なら `strconv.ParseBool`)。失敗で exit 2 (`invalid config value`)。
3. **既存読み込み**: `config.toml` を**汎用 map**で読む (未知キー・セクションを保全するため、struct ではなく `map[string]any`)。不在なら空。文法エラーは exit 2。
4. **適用**: ドットキーの位置に値を設定 (中間テーブルが無ければ作る)。
5. **書き込み**: 親 dir を作成し `config.toml` を上書き。書き込み失敗 (権限等) は exit 1。
6. 成功時は `set test.side_by_side = true  (<path>)` を出力して exit 0。

### 出力イメージ

```
$ atcoder config show
test.side_by_side = false

$ atcoder config set test.side_by_side true
set test.side_by_side = true  (/Users/you/.config/atcoder-daily-training/config.toml)

$ atcoder config get test.side_by_side
true

$ atcoder config path
/Users/you/.config/atcoder-daily-training/config.toml

# 以降は `atcoder test` が -s 省略で side-by-side になる (007 の優先順位 flag > config > default)。
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| `show` (config 無し) | 全キーを既定値で表示 (`test.side_by_side = false`)。エラーにしない |
| `set` (config 無し) | 親 dir ごと `config.toml` を新規作成して書き込む |
| `set` (config あり) | 該当キーだけ更新。**他キー・未知キー・他セクションは保全** (汎用 map で読み書き) |
| 値の冪等性 | 同じ `set` を 2 回実行しても結果は同じ (上書き) |
| 未知キー (`get`/`set`) | exit 2。`unknown config key: <key> (known: test.side_by_side)` |
| 型不一致 (`set`) | exit 2。`invalid config value`。期待する型を併記 |
| 文法エラーのある既存 config | `show`/`get`/`set` とも exit 2 (設定エラー。ユーザが直すべき入力) |
| 書き込み失敗 (権限等) | exit 1 (実行時失敗) |
| 未知の config サブコマンド / 引数不足 | usage を出して exit 2 |
| 既存 `atcoder test` への影響 | なし。`set` で書いた値を `test` が次回 `Load()` で読むだけ |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| 新規 `cmd/atcoder/config.go` | `cmdConfig(args)`。`show`/`get`/`set`/`path` のディスパッチと出力。exit code 分類 |
| `cmd/atcoder/main.go` | `switch` に `case "config"` を追加。usage 文字列に `atcoder config ...` を追記 |
| `internal/config/config.go` | キーレジストリ (`fields`)・`Keys()`・`Get()`・`Set()`・`All()`・`ValueCandidates()`・sentinel error (`ErrUnknownKey` / `ErrInvalidValue` / `ErrParse`) を追加。汎用 map の read/write helper。stale な "exercise" コメントを "atcoder" に修正 |
| `internal/complete/complete.go` | `Subcommands()` に `config` を追加。`config <show\|get\|set\|path>`・`get`/`set` のキー・`set` の値 (bool は true/false) を補完 |
| `fixtures/run.sh` | `config` の smoke (show / set→get の往復 / set の test への波及 / 未知キー・型不一致・未知サブコマンドの exit 2 / path) を追加 |
| `docs/tools/atcoder-test-usage.md` | 「設定ファイルで既定値を固定する」節に `atcoder config` の使い方を追記 |
| `docs/tools/atcoder-test-architecture.md` | キーレジストリと `config` サブコマンドの位置づけを追記 |
| `docs/tools/todo.md` | 「L. `config` サブコマンド」を `✅ DONE` でマーク |

### `internal/config` に足す公開 API (素描)

```go
// 既知キーの登録簿駆動。キー追加は fields に 1 エントリ足すだけ。
var (
    ErrUnknownKey   = errors.New("unknown config key")
    ErrInvalidValue = errors.New("invalid config value")
    ErrParse        = errors.New("config parse error")
)

func Keys() []string                      // 既知ドットキー (ソート済み)
func Get(key string) (string, error)      // 現在値の文字列表現。未知キーは ErrUnknownKey
func All() ([]KeyValue, error)            // 全キー × 現在値 (config show 用)
func Set(key, raw string) error           // 検証 → 汎用 map で読み書き。未知キー/型不一致/文法エラーは sentinel
func ValueCandidates(key string) []string // 補完用の値候補 (bool → ["false","true"])

type KeyValue struct{ Key, Value string }
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `config` にサブコマンド無し | usage、exit 2 |
| 未知の config サブコマンド | usage、exit 2 |
| `get`/`set` でキー未指定 | exit 2 |
| `set` で値未指定 | exit 2 |
| 未知キー (`get`/`set`) | exit 2 (`ErrUnknownKey`) |
| 値が型に合わない (`set`) | exit 2 (`ErrInvalidValue`) |
| 既存 config が文法エラー | exit 2 (`ErrParse`) |
| `config.toml` 書き込み失敗 | exit 1 |
| 正常 | exit 0 |

## 非機能要件

- **既存非破壊**: `atcoder test` の設定適用 (007) は無改修。`config` は同じ `config.toml` を読み書きするだけ。
- **未知キー保全**: `set` は汎用 map で読み書きし、将来バイナリが書いた未知キー・セクションを古いバイナリの `set` で消さない (前方/後方互換)。
- **冪等性**: 同じ `set` の再実行で結果が変わらない。
- **レジストリ単一情報源**: 既知キー・型・値候補を 1 か所 (`fields`) に集約。`config`・補完・将来のバリデーションが同じ表を見る。
- **最小依存**: TOML は既存 `BurntSushi/toml` を再利用。新規依存なし。
- **解答ファイル非破壊**: `config` は `config.toml` 以外に書き込まない。

## 将来の拡張ポイント

- **設定項目の追加**: `fields` にエントリを足すだけで `get`/`set`/`show`/補完が対応。`[run]` 等のセクションも同様。
- **`config unset <key>`**: キーを削除して既定値に戻す。
- **`config edit`**: `$EDITOR` で `config.toml` を開く。
- **値候補の拡充**: enum 型キーに候補リストを持たせ、`set` のバリデーションと補完を強化。
- **コメント保全**: TOML round-trip で既存コメントを残す (現状は再エンコードで失われる)。

## 用語

- **キーレジストリ**: 既知設定キーとその型・get/set・値候補を集めた表 (`internal/config` の `fields`)。
- **ドットキー**: `<section>.<field>` 形式の設定キー指定 (例 `test.side_by_side`)。
- **汎用 map 読み書き**: 設定を `map[string]any` で読み、未知キーを保全したまま 1 キーだけ更新して書き戻す方式。
- (`flag > config > default` / config の所在・スキーマは要件 007 に準拠)

## 関連ドキュメント

- `docs/tools/requirements/007-atcoder-config.md` (設定層の基盤要件。スキーマ・所在・優先順位の定義元)
- `docs/tools/todo.md` (上位ロードマップ。「L. `config` サブコマンド」の要件詳細が本書)
- `docs/tools/atcoder-test-usage.md` (利用手引。`atcoder config` の使い方を追記)
- `docs/tools/atcoder-test-architecture.md` (内部設計。キーレジストリの位置づけを追記)
