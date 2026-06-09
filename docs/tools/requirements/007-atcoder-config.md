# `atcoder` 設定ファイル 要件定義

## 概要

`atcoder` CLI に **ユーザ設定ファイル** (`config.toml`) を導入し、毎回タイプしているフラグの既定値を 1 か所で固定できるようにする。第一の設定項目として **`atcoder test` の diff を side-by-side 表示 (`-s`) でデフォルト適用**する設定を入れる。設定ファイルは将来項目を足せるよう拡張可能なスキーマで設計し、フラグとの優先順位は **`flag > config > default`** に統一する。

`docs/tools/todo.md` の「K. ユーザ設定ファイル」の要件詳細。既存の XDG ベースのキャッシュ配置 (`internal/cachepath`) と同じ流儀で、設定は **XDG_CONFIG_HOME** 配下に置く。

## 背景・目的

- diff を side-by-side で見たい人は毎回 `-s` を付ける必要がある。好みの表示・並列度・許容誤差などは「いつも同じ値」になりがちで、毎回フラグで渡すのは摩擦が大きい。
- 個人の既定値を 1 か所に書いておければ、`atcoder test <contest> --task d` だけで好みの表示・挙動になる。コマンドラインで明示したフラグはその場で優先されるべき (一時的な上書き)。
- 後から `verbose` / `jobs` / `tolerance` / `layout` 等も設定可能にしたくなる。最初に**拡張可能なスキーマ**と**優先順位ルール**を決めておけば、項目追加は struct にフィールドを足すだけで済む。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 設定ファイル形式 | TOML (`github.com/BurntSushi/toml`、既存 meta/contest と同じ) | — |
| 所在 | `$XDG_CONFIG_HOME/atcoder-daily-training/config.toml` (fallback: `~/.config/...`) | `--config <path>` での明示指定 |
| 設定項目 | `[test] side_by_side` のみ | `[test]` の verbose/debug/jobs/tolerance/timeout/layout、`[run]`、`[global]` 等 |
| 優先順位 | `flag > config > default` | 環境変数層を挟む (`flag > env > config > default`) |
| 適用先コマンド | `atcoder test` | `run` / `submit` など他サブコマンド |
| 書き込み | 対象外 (利用者が手で書く) | `atcoder config set <key> <value>` |

### スコープを `[test] side_by_side` 1 項目に絞る理由

- 機構 (発見・読み込み・優先順位適用) を最小の 1 項目で確立し、fixture で振る舞いを固定する。項目の追加はスキーマにフィールドを足すだけの定型作業になる。
- side_by_side は「出力表示のデフォルト化」という設定ファイル本来の用途を代表する、副作用の小さい良い題材 (判定結果・終了コードを変えない)。

## ディレクトリ構造

```
# ユーザ設定 (新規)。キャッシュ (XDG_CACHE_HOME) とは別軸。
$XDG_CONFIG_HOME/atcoder-daily-training/config.toml
  └ fallback: ~/.config/atcoder-daily-training/config.toml
```

- キャッシュ (`internal/cachepath`, `atcoder-tools/...`) は **XDG_CACHE_HOME**、ユーザ設定は **XDG_CONFIG_HOME**。役割が違うので base を分ける (XDG 仕様に準拠)。
- アプリ名ディレクトリは `atcoder-daily-training` (リポジトリ名)。キャッシュ側の中立名 `atcoder-tools` とは別で、こちらは「このツール個人設定」であることを明示する。

## 設定スキーマ

`config.toml` (サブコマンドごとにセクションを切る。前方互換のため未知キーは無視):

```toml
[test]
side_by_side = true   # atcoder test の diff を side-by-side で表示する既定値 (-s 相当)
```

| キー | 型 | 既定 | 対応フラグ | 用途 |
|---|---|---|---|---|
| `test.side_by_side` | bool | `false` | `-s` / `--side-by-side` | FAIL 時の diff を side-by-side でレンダリングする既定値 |

- セクション (`[test]`) でサブコマンド単位に束ねる。将来 `[run]` / `[global]` を足しても衝突しない。
- 未知のキー・セクションは **エラーにせず無視**する (前方/後方互換: 新しい設定を書いた config を古いバイナリで読んでも壊れない)。
- ファイルが**存在しない**のは正常 (全項目デフォルト)。パースに**失敗**したときだけエラー。

## CLI 仕様

新サブコマンドは増やさず、既存 `atcoder test` の挙動に設定の層を 1 枚噛ませる。

```
atcoder test <contest> --task <task> [-s] [既存フラグ...]
```

### 優先順位の決定方法

`flag > config > default` を Go の `flag` パッケージで実現する:

1. 設定を読み込み、`config.Test.SideBySide` を得る (ファイル無し → `false`)。
2. `-s` / `--side-by-side` の **flag のデフォルト値に config 値を渡す**。
3. パース後の値を採用する:
   - 利用者が `-s` を付けた → `true` (flag が config を上書き)。
   - 利用者が `--side-by-side=false` を付けた → `false` (config が true でも明示 OFF で上書き)。
   - 何も付けない → config 値 (= 既定)。

これにより「設定で true にしておき、特定回だけ `--side-by-side=false` で unified に戻す」が成立する。

### 処理ステップ

`atcoder test abc457 --task d` 実行時:

1. **設定読み込み**: `config.Load()` で `config.toml` を読む。無ければ全項目デフォルト。パース失敗は exit 2 (設定エラー)。
2. **flag 定義**: `-s` / `--side-by-side` のデフォルトに `config.Test.SideBySide` を入れて定義する。他フラグは従来どおり。
3. **パース**: 引数を parse。これで `flag > config > default` の確定値になる。
4. 以降は従来の `atcoder test` と同一 (確定した sideBySide を `ui.NewTestReporter` に渡す)。

### 出力イメージ

```
# ~/.config/atcoder-daily-training/config.toml に side_by_side = true を書いておくと…
$ atcoder test abc457 --task d          # -s 不要で side-by-side になる
abc457_d  contest=abc457  ...
[01]  FAIL   28 ms
       diff (side-by-side):
         <期待> ┊ <実際>
         ...

$ atcoder test abc457 --task d --side-by-side=false   # その回だけ unified に戻す
       diff:
           1 - │ ...
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| config 無し | 全項目デフォルト (= 現行挙動と完全一致)。エラーにしない |
| config あり `side_by_side=true` | `-s` 省略時も diff が side-by-side |
| `-s` 明示 | 常に side-by-side (config 値に依らず) |
| `--side-by-side=false` 明示 | 常に unified (config が true でも OFF) |
| 未知キー / 未知セクション | 無視して継続 (前方互換) |
| config パース失敗 (TOML 文法エラー等) | exit 2、どのファイルが原因かを示すメッセージ |
| `XDG_CONFIG_HOME` 未設定 | `~/.config/atcoder-daily-training/config.toml` を見る |
| 既存サブコマンド (`run`/`new`/...) | 影響なし (config を読むのは `test` のみ) |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| 新規 `internal/config/` | `config.toml` のスキーマ・XDG パス解決・`Load()`。`cachepath` と対をなすユーザ設定層 |
| `cmd/atcoder/test.go` | 起動時に `config.Load()` → `-s` の flag デフォルトに config 値を反映。パース失敗は exit 2 |
| `fixtures/run.sh` | `XDG_CONFIG_HOME` を空 temp dir に固定 (既存テストを config 非依存に) + config 適用 / flag 上書き / パース失敗の smoke を追加 |
| `docs/tools/atcoder-test-usage.md` | 設定ファイルの所在・スキーマ・優先順位・side_by_side の例を追記 |
| `docs/tools/atcoder-test-architecture.md` | `internal/config` をパッケージ構成・依存方向に追記 |
| `docs/tools/todo.md` | 「K. ユーザ設定ファイル」を `✅ DONE` でマーク |

### 新規 `internal/config/` パッケージの責務

`internal/cachepath` (キャッシュ配置) と対になる、**ユーザ設定**の層。

```go
package config

// Config は config.toml のスキーマ。サブコマンドごとにセクションを切る。
type Config struct {
    Test TestConfig `toml:"test"`
}

// TestConfig は [test] セクション。atcoder test の既定値。
type TestConfig struct {
    SideBySide bool `toml:"side_by_side"`
}

// Path は config.toml の絶対パスを返す ($XDG_CONFIG_HOME → ~/.config fallback)。
func Path() string

// Load は config.toml を読む。ファイル不在はゼロ値 Config + nil error。
// パース失敗のときだけ error を返す。
func Load() (*Config, error)
```

- XDG 解決は `cachepath.Base()` と同じ構造 (`$XDG_CONFIG_HOME` → `~/.config` → `./.config`)。重複が気になれば将来 xdg 解決を共通ヘルパーに括り出す余地があるが、当面は `config` 内に閉じて持つ。
- `Load()` は `os.Open` → `toml.NewDecoder().Decode`。`os.IsNotExist` はゼロ値で握りつぶす。

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| config.toml が無い | ゼロ値 Config (全デフォルト)。エラーにしない |
| config.toml のパース失敗 (TOML 文法エラー) | "設定ファイルの読み込みに失敗: <path>: <err>" で exit 2 |
| 未知キー / セクション | 無視 (BurntSushi/toml はデフォルトで未知キーを許容)。エラーにしない |
| `XDG_CONFIG_HOME` が相対パス等で不正 | XDG 仕様に倣い無視して fallback (実害が出る前に Path が壊れた値を返さないよう、空でなければそのまま使う = 既存 cachepath と同等の緩さ) |

## 非機能要件

- **既存ワークフロー非破壊**: config が無い・該当キーが無いときは現行挙動と完全一致。`test` 以外のサブコマンドは無影響。
- **前方/後方互換**: 未知キーを無視するので、新項目を書いた config を古いバイナリで読んでも壊れない。逆も同様。スキーマ追加は破壊的変更を避ける。
- **優先順位の一貫性**: `flag > config > default` を全項目で守る。明示フラグは常に勝つ (一時上書きできる)。
- **最小依存**: TOML は既存依存 (`BurntSushi/toml`) を再利用。新規依存なし。
- **解答ファイル非破壊**: config は読むだけ。解答にもキャッシュにも書き込まない。

## 将来の拡張ポイント

- **設定項目の追加**: `[test]` に verbose/debug/jobs/tolerance/timeout/layout を、`[run]` に run 用既定値を足す。各 cmd で flag デフォルトに config 値を流す同じパターンを踏襲。
- **`--config <path>`**: 設定ファイルを明示指定する大域フラグ。
- **`atcoder config` サブコマンド**: `config show` / `config set <key> <value>` で TUI レスに設定を編集。
- **環境変数層**: `flag > env > config > default` に拡張 (CI で一時的に上書き等)。
- **xdg 解決の共通化**: `cachepath.Base()` (CACHE) と `config.Path()` (CONFIG) の XDG ロジックを共通ヘルパーへ。

## 用語

- **ユーザ設定 (config)**: 利用者個人の既定値。`$XDG_CONFIG_HOME/atcoder-daily-training/config.toml`。キャッシュ (`XDG_CACHE_HOME`) とは別軸。
- **優先順位 `flag > config > default`**: コマンドラインで明示したフラグが最優先、次に設定ファイル、最後に組み込み既定値。
- (`contest_id` / `task_id` / `letter` / `layout` 等は 002 / 003 の要件定義に準拠)

## 関連ドキュメント

- `docs/tools/decisions/0003-user-config-xdg-toml.md` (決定記録。完了に伴い todo.md の「K. ユーザ設定ファイル」から移動)
- `docs/tools/requirements/001-exercise-test.md` (test サブコマンドの基盤要件。side-by-side diff の `-s` 定義元)
- `docs/tools/atcoder-test-usage.md` (利用手引。設定ファイルの使い方を追記)
- `docs/tools/atcoder-test-architecture.md` (内部設計。`internal/config` の位置づけを追記)
