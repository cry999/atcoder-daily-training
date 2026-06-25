# `config` の alias (git 風コマンド別名) 要件定義

## 概要

`atcoder` に **git のような alias** を入れる。`config.toml` の `[alias]` セクションに `名前 = "コマンド列"` を書いておくと、`atcoder <名前> [追加引数...]` がそのコマンド列に展開されて実行される。例えば `alias.upd-lo = "update --local"` を設定すると `atcoder upd-lo` が `atcoder update --local` を実行する。設定・参照・削除は既存の `config` サブコマンドで行い、削除用に汎用 `config unset <key>` を新設する。

ユーザ設定 (要件 007 / ADR 0003) の自然な拡張で、新しいキー型 (任意名の文字列マップ) と、サブコマンド dispatch 前の **alias 展開** を 1 つ足すだけ。解答・キャッシュには触れない。

## 背景・目的

- `atcoder update --local` のような **よく打つが長いコマンド** を短い名前で呼びたい。git の `[alias]` (`git config alias.co checkout` → `git co`) と同じ使い勝手が欲しい。
- 設定は既に `config.toml` にあるので、別の仕組みを増やさず **既存 config の延長**で実現したい (「config に alias を追加したい」という要望に沿う)。
- 既存サブコマンド (`test`/`run`/`update` …) の挙動は一切変えたくない。alias はあくまで **未知の名前を解決する追加経路**として足す。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 保存先 | `config.toml` の `[alias]` セクション (`名前 = "コマンド列"`) | — |
| 設定インターフェース | `config set/get/show` + 新設 `config unset` | 専用 `alias` サブコマンド |
| 展開対象 | `atcoder` の**サブコマンド列**のみ (例 `update --local`) | `!` 始まりの任意シェルコマンド (git の shell alias) |
| 引数 | 展開後に呼び出し時の追加引数を**後ろに連結** | 位置パラメータ `$1`/`$@` 展開 |
| 値の分割 | 空白区切り (`strings.Fields`) | クォート対応 (shell-words) |
| 名前衝突 | **組み込みサブコマンドが常に優先** (alias は未知名のときだけ) | — |
| 再帰 | alias → alias を再帰展開 (ループ検出付き) | — |
| 副作用 | config.toml の読み書きのみ (set/unset)。展開自体は副作用なし | — |

### 境界 (他機能との分担)

- ストレージと set/get/show は **要件 007 (config)** の枠組みに乗る。typed キー (`test.side_by_side` 等) のレジストリ (`internal/config` の `fields`) とは別経路で、`alias.*` は任意名の文字列として扱う。
- 補完への登録は **要件 008 / 012 (completion)**。alias 名をサブコマンド候補に出す。
- alias が展開する先 (`update --local` 等) の挙動は各サブコマンド要件のまま。alias は dispatch の前段に挟まる薄い層。

## ディレクトリ構造・スキーマ

`config.toml` に `[alias]` テーブルを足す (他セクションは不変):

```toml
[test]
side_by_side = true

[alias]
upd-lo = "update --local"
st     = "status"
t      = "test"
```

| キー | 型 | 説明 |
|---|---|---|
| `[alias]` テーブル | `map[string]string` | alias 名 → 展開するコマンド列 |
| 名前 (`<name>`) | string | `config` 上のキーは `alias.<name>`。許容文字は英数字・`-`・`_`。`.` 不可、空不可 |
| 値 | string | `atcoder` 以降のサブコマンド列 (例 `"update --local"`)。空白区切りで分割 |

- 未知セクション/キーは toml デコードで無視される既存方針 (前方/後方互換) をそのまま継ぐ。

## CLI 仕様

### alias の管理 (config 経由)

```
atcoder config set   alias.<name> "<command>"   # 設定 (作成・更新)
atcoder config get   alias.<name>               # 参照
atcoder config unset <key>                       # 削除 (新設、汎用)
atcoder config show                              # typed キー + [alias] を一覧
```

| コマンド | 動作 |
|---|---|
| `config set alias.upd-lo "update --local"` | `[alias]` に `upd-lo = "update --local"` を書く。値は**1 引数** (空白を含むならクォート必須、git と同じ) |
| `config get alias.upd-lo` | 値 (`update --local`) を表示。未定義なら未知キー (exit 2) |
| `config unset alias.upd-lo` | alias を削除。`config unset test.side_by_side` は typed キーの上書きを消して既定値に戻す |
| `config show` | typed キーに続けて `alias.<name> = <command>` を名前順で一覧 |

- **`config set alias.<name>`** で `<name>` が組み込みサブコマンド名 (`test`/`update` 等) のときは、保存はするが **「この alias は組み込みが優先され無視される」旨を stderr に警告**する (exit 0)。
- `<name>` が不正 (空・`.` を含む・許容外文字) なら設定エラー (exit 2)。

### alias の展開 (dispatch)

`atcoder <arg0> <rest...>` の解決手順:

1. `<arg0>` が**組み込みサブコマンド**ならそれを実行 (alias は見ない)。**組み込みが常に優先。**
2. 組み込みでなく、`[alias]` に `<arg0>` があれば展開: `tokens = Fields(値)` とし、新しい引数列を `tokens + rest` にする。
3. 展開後の先頭が再び alias なら再帰的に 2 を繰り返す (同じ alias 名を二度展開したら**ループとしてエラー**、exit 2)。
4. 展開後の先頭が組み込みサブコマンドになったらそれを実行。どの alias でも組み込みでもない名前に行き着いたら未知 (usage 表示、exit 2)。

### 出力イメージ

```
$ atcoder config set alias.upd-lo "update --local"
set alias.upd-lo = update --local  (/Users/.../atcoder-daily-training/config.toml)

$ atcoder config show
test.side_by_side = false
alias.upd-lo = update --local

$ atcoder upd-lo            # → atcoder update --local
  current  abc1234abc12 (2026-06-05T09:00:00Z)
  installing… go install ./cmd/atcoder
  installed from local working tree ✓

$ atcoder upd-lo --check    # 追加引数は後ろに連結 → update --local --check (この組合せは exit 2)
atcoder update: --local and --check cannot be combined

$ atcoder config unset alias.upd-lo
unset alias.upd-lo  (/Users/.../config.toml)
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `<arg0>` が組み込み | 組み込みを実行 (alias 無視) |
| `<arg0>` が alias | コマンド列に展開し、追加引数を後ろに連結して再解決 |
| alias → alias | 再帰展開。ループ (同名再訪) は exit 2 |
| alias 名が組み込みと同名 | dispatch では無視 (組み込み優先)。set 時に警告 |
| alias 値が空文字 | 展開結果が空 → 未知扱い (exit 2)。実質「無効な alias」 |
| `config get alias.<未定義>` | 未知キー (exit 2) |
| `config unset <未定義/不明キー>` | 未知キー (exit 2) |
| 追加引数あり (`atcoder upd-lo X`) | 展開の後ろに `X` を連結 |
| `config.toml` が無い | alias 無し扱い (展開しない)。set/unset は親 dir ごと作成 (既存挙動) |

- **冪等**: 同じ `config set` を二度実行しても結果は同じ。`unset` は存在しない alias でも実害なく削除を試みる (未定義キーは exit 2 で知らせる方針か、no-op exit 0 か → 「エラーハンドリング」で確定)。
- **既存非破壊**: 組み込みサブコマンドの解決・挙動・exit code は不変。alias は未知名のときだけ介在する。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/config/config.go` | `Config` に `Alias map[string]string` (`toml:"alias"`) を追加。`Aliases()` / `AliasKeys()` アクセサ |
| `internal/config/keys.go` | `Set`/`Get`/`All` を `alias.*` 対応に (typed `fields` を迂回し文字列として読み書き)。`Unset(key)` 新設。alias 名のバリデーション |
| 新規 `internal/alias/alias.go` | `Expand(args, aliases, isBuiltin) ([]string, error)` 純粋関数。再帰展開・ループ検出 |
| `cmd/atcoder/main.go` | 組み込み名の集合 `builtins` を持ち、switch の前に `alias.Expand` を通す。`usage()` に alias の一言 |
| `cmd/atcoder/config.go` | `case "unset"` を追加。set/get で `alias.*` を許容。exit code 分類は既存どおり |
| `internal/complete/complete.go` | サブコマンド位置の候補に**現在の alias 名**を追加 (説明 `alias → <expansion>`)。`config` の sub-subcommand に `unset`。`get`/`unset` のキー補完に既存 alias 名 |
| `internal/complete/complete_test.go` | alias 展開候補・`unset` 候補のテスト |
| `internal/alias/alias_test.go` | 展開・連結・再帰・ループ検出・組み込み優先のユニットテスト |
| `internal/config/keys_test.go` | `alias.*` の set/get/unset・名前バリデーションのテスト |
| `fixtures/run.sh` | alias の set→展開実行、unset、不正名 (exit 2)、組み込み優先、ループ (exit 2) を smoke |
| `docs/tools/atcoder-config-usage.md` | 利用手引 (新規。config 全般 + alias + unset) |
| `docs/tools/todo.md` | 項目 N として記載し、本要件へ相互リンク |

### 新規 `internal/alias` パッケージの責務 (素描)

```go
package alias

// Expand は arg0 が alias なら展開し、追加引数を後ろに連結して返す。
// 組み込み (isBuiltin が true) は常に優先し展開しない。再帰展開し、同じ alias を
// 二度たどったらループとして error を返す。alias でも組み込みでもない先頭はそのまま返す
// (呼び出し側が未知として usage を出す)。
//
//   args=["upd-lo","--check"], aliases={"upd-lo":"update --local"}
//     → ["update","--local","--check"]
func Expand(args []string, aliases map[string]string, isBuiltin func(string) bool) ([]string, error)
```

### `internal/config` の追加 API (素描)

```go
// Aliases は [alias] テーブル (名前→コマンド列) を返す。未設定なら空 map。
func Aliases() (map[string]string, error)

// AliasKeys は補完用に "alias.<name>" を名前順で返す。
func AliasKeys() ([]string, error)

// Unset は key (typed か alias.<name>) を config.toml から削除する。
//   - alias.<name>: [alias] から該当エントリを削除
//   - typed キー: 上書きを消して既定値に戻す
//   - 未知キー: ErrUnknownKey
func Unset(key string) error
```

- `Set`/`Get`/`All` は `alias.` プレフィックスを特別扱いする。alias の値は型を持たない自由文字列なので `fields` レジストリは通さない。
- 組み込み名集合は `cmd/atcoder/main.go` が単一情報源として持ち (switch・usage と同期)、`alias.Expand` に `isBuiltin` として渡す。`complete.Subcommands()` と齟齬が出ないよう注意 (補完の候補表とも整合)。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `config set alias.<不正名>` (空・`.`含む・許容外) | "invalid alias name" | 2 |
| `config set alias.<組み込み名>` | 保存はするが警告を stderr に出す | 0 |
| `config get alias.<未定義>` | 未知キー | 2 |
| `config unset <未定義/不明キー>` | 未知キー | 2 |
| `config unset` (キー引数なし) | usage | 2 |
| alias 展開のループ (同名再訪) | "alias loop detected: <name>" | 2 |
| 展開結果が空 / 未知名に到達 | usage | 2 |
| config.toml 書き込み失敗 (set/unset) | エラー | 1 |
| 正常 (set/get/show/unset/展開実行) | — | 0 (展開先サブコマンドの exit code に従う) |

- exit code 規約踏襲: 引数/設定/解決エラー = 2、書き込み等の実行時失敗 = 1、成功 = 0。alias の誤設定 (不正名・ループ) は**設定エラー扱いで 2**。
- `config unset <未定義>` を no-op (exit 0) にするか未知エラー (exit 2) にするかは、既存の「未知キー = exit 2」に揃えて **exit 2** とする (典型誤りを黙らせない)。

## 非機能要件

- **既存非破壊**: 組み込みサブコマンドの解決・挙動・exit code・usage・既存 config キーは不変。alias は未知名の解決経路を足すだけ。
- **依存ゼロ追加 / FW 非導入**: 標準 `flag` + `BurntSushi/toml` のまま。`go.mod` を変えない。
- **安全 (組み込み優先)**: alias は組み込みを上書きできない。`test`/`update` 等のコア挙動を alias 誤設定で壊さない。
- **決定的・テスト可能**: 展開 (`alias.Expand`) を純粋関数にし、連結・再帰・ループ・組み込み優先をユニットテストで網羅。
- **副作用最小**: 展開は読み取りのみ。書き込みは set/unset の config.toml だけ。解答・キャッシュには触れない。

## 将来の拡張ポイント

- **shell alias** (`!` 始まりで任意コマンド実行)。git にあるが安全面の検討が要るので別途。
- **クォート対応**の値分割 (空白を含む 1 引数を渡せるように shell-words)。
- **位置パラメータ** (`$1` / `$@`) の展開。
- 専用 `atcoder alias add/list/remove` サブコマンド (config 経由の薄い糖衣)。
- 補完で alias 展開先まで考慮した候補 (例 `atcoder upd-lo <TAB>` を `update --local` のフラグで補完)。

## 用語

- **alias**: `config.toml` の `[alias]` に定義する、コマンド列への名前。`atcoder <名前>` で展開される。
- **展開 (expand)**: `<名前>` を `[alias]` の値 (トークン列) に置き換え、追加引数を後ろに連結すること。
- **組み込みサブコマンド (builtin)**: `main.go` の switch が直接持つコマンド (`new`/`test`/`run`/`submit`/`login`/`logout`/`status`/`stats`/`config`/`commit`/`completion`/`update`/`version`)。alias より常に優先。
- typed キー: `fields` レジストリで型付き管理される既知の config キー (`test.side_by_side` 等)。alias.* とは別経路。
- `contest_id` 等の ID 用語は既存要件に準拠 (本機能では使わない)。

## 関連ドキュメント

- `docs/tools/requirements/007-atcoder-config.md` / `docs/tools/decisions/0003-user-config-xdg-toml.md` (config の基盤・XDG/TOML)
- `docs/tools/requirements/008-atcoder-completion.md` / `012-completion-descriptions.md` (alias を補完候補に足す)
- `docs/tools/requirements/050-atcoder-self-update.md` (alias の主目的の 1 つ `update --local`)
- `docs/tools/atcoder-config-usage.md` (利用手引。本機能で新設)
- `docs/tools/todo.md` (上位ロードマップ。項目 N)
