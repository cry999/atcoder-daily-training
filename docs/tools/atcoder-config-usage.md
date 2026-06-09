# `atcoder config` 利用手引

`atcoder` のユーザ設定ファイル `config.toml` を CLI から閲覧・編集する。設定は XDG Base Directory に従い `$XDG_CONFIG_HOME/atcoder-daily-training/config.toml` (未設定なら `~/.config/...`) に置かれる。手で開いて編集してもよいが、`atcoder config set` を使えば既知キーの型チェックと、未知キー・他セクションの保全が効く。

> 要件詳細: `docs/tools/requirements/007-atcoder-config.md` (設定ファイルの基盤) / `docs/tools/requirements/009-atcoder-config-subcommand.md` (サブコマンド) / `docs/tools/requirements/017-config-layout-default.md` (`layout` キー)

## コマンド

```
atcoder config show
atcoder config get <key>
atcoder config set <key> <value>
atcoder config path
```

| コマンド | 動作 |
|---|---|
| `atcoder config show` | 全既知キーと現在値 (config 反映後、無ければ既定値) を `key = value` 形式で一覧 |
| `atcoder config get <key>` | 1 キーの現在値を出力 |
| `atcoder config set <key> <value>` | 1 キーを書き込む。`config.toml` が無ければ親 dir ごと作成。未知キー・他セクションは保全 |
| `atcoder config path` | `config.toml` の絶対パスを出力 (存在するとは限らない) |

exit code: 引数誤り / 未知キー / 型・値の不一致 / 既存 `config.toml` の文法エラー = **2**、書き込み失敗 = **1**、成功 = **0**。

## 既知キー

| キー | 型 | 既定 | 説明 |
|---|---|---|---|
| `layout` | enum (`auto` / `abc` / `exercise`) | `auto` | 解答ファイルの既定レイアウト (下記) |
| `test.side_by_side` | bool | `false` | `atcoder test` の FAIL 時 diff を左右 2 カラムで表示する既定値 (`-s` 相当) |

```toml
# $XDG_CONFIG_HOME/atcoder-daily-training/config.toml
layout = "abc"

[test]
side_by_side = true
```

## `layout` 既定レイアウト

レイアウト (`auto` / `abc` / `exercise`) を毎回 `--layout` で渡さなくても、既定値として固定できる。`atcoder test` (ad-hoc / `--submit` 含む) は省略時に次の順で既定を決める:

| 優先 | 出所 | 例 |
|---|---|---|
| 1 | コマンドの `--layout` フラグ | `atcoder test abc457 --task d --layout exercise` |
| 2 | 環境変数 `ATCODER_LAYOUT` | `ATCODER_LAYOUT=abc atcoder test ...` |
| 3 | `config.toml` の `layout` | `atcoder config set layout abc` |
| 4 | 既定 `auto` | `abc<NNN>` なら `abc`、他は `exercise` |

- 最初に空でない出所が採用される。`--layout` を省略 (空) すると 2 以降にフォールバックし、`$ATCODER_LAYOUT` も config も無ければ従来どおり `auto`。
- `--layout auto` を**明示**した場合は段 1 で確定し、env / config を無視して `auto` 検出に回る。
- 不正なレイアウト値はどの出所でも `unknown layout ...` で **exit 2**。

```
# 永続的に abc レイアウトを既定にする
$ atcoder config set layout abc
set layout = abc  (/home/user/.config/atcoder-daily-training/config.toml)

$ atcoder config get layout
abc

# このシェルだけ exercise に上書き (config より優先)
$ ATCODER_LAYOUT=exercise atcoder test abc457 --task d

# その 1 回だけ明示フラグで上書き (env / config より優先)
$ atcoder test abc457 --task d --layout exercise
```

未設定 (`config.toml` に `layout` が無い) のとき、`config get layout` / `config show` は実効既定値の **`auto`** を表示する (env / フラグの上書きは含まない、config 層から見た既定)。`auto` に戻したいときは `atcoder config set layout auto` を明示する。

> レイアウトそのものの定義 (`abc` = `abc/<num>/<letter>.py`、`exercise` = `exercise/YYYY/MM/DD/<task>.py`) は [`atcoder test` の `--layout`](atcoder-test-usage.md) と要件 `002-exercise-abc-layout.md` を参照。

## 補完

`atcoder config <TAB>` は sub-subcommand (`show`/`get`/`set`/`path`) を、`config get|set <TAB>` は既知キーを、`config set <key> <TAB>` は値候補 (`layout` なら `abc auto exercise`、bool キーなら `true false`) を補完する。詳細は [`atcoder-completion-usage.md`](atcoder-completion-usage.md)。

## 関連

- 設定ファイル基盤と XDG: [ADR 0003](decisions/0003-user-config-xdg-toml.md) / 要件 007
- サブコマンドのキーレジストリ: 要件 009
- 既定レイアウト: 要件 017 / [`atcoder-test-usage.md`](atcoder-test-usage.md)
