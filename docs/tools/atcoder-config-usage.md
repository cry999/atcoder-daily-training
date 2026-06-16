# `atcoder config` 利用手引

`atcoder` のユーザ設定ファイル `config.toml` を CLI から閲覧・編集する。サブコマンド既定値 (例 `layout` / `test.side_by_side`) と、**git 風のコマンド alias** (`[alias]`) を管理する。設定は XDG Base Directory に従い `$XDG_CONFIG_HOME/atcoder-daily-training/config.toml` (未設定なら `~/.config/...`) に置かれる。手で開いて編集してもよいが、`atcoder config set` を使えば既知キーの型チェックと、未知キー・他セクションの保全が効く。

> 要件詳細: `docs/tools/requirements/007-atcoder-config.md` (設定ファイルの基盤) / `docs/tools/requirements/009-atcoder-config-subcommand.md` (サブコマンド) / `docs/tools/requirements/017-config-layout-default.md` (`layout` キー) / `docs/tools/requirements/016-config-alias.md` (alias)

## コマンド

```
atcoder config show
atcoder config get   <key>
atcoder config set   <key> <value>
atcoder config unset <key>
atcoder config path
```

| コマンド | 動作 |
|---|---|
| `atcoder config show` | 全既知キーと現在値 (config 反映後、無ければ既定値)、`[alias]` を `key = value` 形式で一覧 |
| `atcoder config get <key>` | 1 キーの現在値を出力 |
| `atcoder config set <key> <value>` | 1 キーを書き込む。`config.toml` が無ければ親 dir ごと作成。未知キー・他セクションは保全 |
| `atcoder config unset <key>` | キーを削除する (typed キーは既定値に戻す / `alias.<name>` は alias を消す) |
| `atcoder config path` | `config.toml` の絶対パスを出力 (存在するとは限らない) |

exit code: 引数誤り / 未知キー / 型・値の不一致 / 不正な alias 名・alias ループ / 既存 `config.toml` の文法エラー = **2**、書き込み失敗 = **1**、成功 = **0**。

## 既知キー

| キー | 型 | 既定 | 説明 |
|---|---|---|---|
| `layout` | enum (`auto` / `abc` / `exercise`) | `auto` | 解答ファイルの既定レイアウト (下記) |
| `editor` | string | `(unset)` | `atcoder start` / `test --interactive` の `Ctrl+E` で**nvim 外**のとき使うエディタコマンド (空白区切りで argv 展開、例 `nvim -p` / `code -w`)。未設定は `$EDITOR` → `nvim`。nvim の `:terminal` 内 (`$NVIM` 在り) は親 nvim へ送るのでこのキーは効かない ([要件 038](requirements/038-start-edit-in-editor.md)) |
| `test.side_by_side` | bool | `false` | `atcoder test` の FAIL 時 diff を左右 2 カラムで表示する既定値 (`-s` 相当) |

```toml
# $XDG_CONFIG_HOME/atcoder-daily-training/config.toml
layout = "abc"

[test]
side_by_side = true

[alias]
upd-lo = "update --local"
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

### starship に現在のレイアウトを表示する

`atcoder config get layout` は現在の既定レイアウト (未設定なら `auto`) を 1 行で吐いて **exit 0** で返るので、[starship](https://starship.rs/) の [custom module](https://starship.rs/config/#custom-commands) からそのまま呼べる。`~/.config/starship.toml` に次を足すと、プロンプトに選択中のレイアウトが出る。

下の `format` は Catppuccin powerline 風の `[directory]` (角丸キャップ + アイコンをアクセント色・値を `surface0` に乗せる) に合わせてある。アクセント色は `[directory]` の `mauve` と区別して `peach` にしている:

```toml
[custom.atcoder_layout]
# env (ATCODER_LAYOUT) > config > auto を忠実に表示する。
command = 'echo "${ATCODER_LAYOUT:-$(atcoder config get layout)}"'
shell = ["bash", "--noprofile", "--norc"]
when = true
symbol = ""
format = "[](fg:peach)[ $symbol](fg:mantle bg:peach)[](fg:peach bg:surface0)[ $output](bg:surface0)[](fg:surface0)"
```

- `command` を `echo "${ATCODER_LAYOUT:-...}"` にしておくと、`atcoder` 本体と同じ **env > config > auto** の優先順で表示できる (config 層だけで良ければ `atcoder config get layout` 単体でもよい)。
- `format` は `[directory]` と同じセグメント構成: `` 角丸左キャップ → アイコンを `peach` 背景に → `` 矢印で `surface0` へ → `$output` (レイアウト名) を `surface0` 背景に → `` 角丸右キャップ。`[directory]` の直後に置くなら、間に連結線を入れたい場合は先頭へ `[─](fg:peach)` を足す。
- アクセント色 (`peach`) と `symbol` のグリフは好みで差し替えてよい (パレット名は `[directory]` と同じ Catppuccin を流用)。
- `layout` はグローバル設定なので既定では**どのディレクトリでも**出る。練習リポジトリ内だけに絞りたいなら `detect_folders = ["exercise", "abc", "arc"]` を足す (cwd にそのフォルダがある時だけ表示)。`auto` のときは隠したいなら `when = '[ "$(atcoder config get layout)" != auto ]'` のようにガードする。

> `atcoder` が PATH に無いと custom module は何も出さない (command 失敗で自動的に隠れる)。

## alias (git 風コマンド別名)

よく打つ長いコマンドに短い名前を付けられる。`config.toml` の `[alias]` セクションに `名前 = "コマンド列"` を置くと、`atcoder <名前> [追加引数]` がそのコマンド列に展開されて実行される (git の `[alias]` と同じ)。

```
$ atcoder config set alias.upd-lo "update --local"
set alias.upd-lo = update --local  (~/.config/atcoder-daily-training/config.toml)

$ atcoder upd-lo            # → atcoder update --local
  current  abc1234abc12 (...)
  installing… go install ./cmd/atcoder
  installed from local working tree ✓

$ atcoder upd-lo --check    # 追加引数は後ろに連結 → update --local --check
...

$ atcoder config get alias.upd-lo
update --local

$ atcoder config unset alias.upd-lo
unset alias.upd-lo  (...)
```

### ルール

- **値は 1 引数**。空白を含むのでクォートする (`"update --local"`)。展開時は空白で分割される。
- **追加引数は後ろに連結**される (`atcoder upd-lo --check` → `update --local --check`)。
- **組み込みサブコマンドが常に優先**。`test`/`update` 等と同名の alias を定義しても無視される (`config set` 時に警告)。alias は未知の名前のときだけ解決される。
- **alias → alias** も再帰展開される。循環 (`a = "b"`, `b = "a"`) は検出してエラー (exit 2)。
- alias 名に使えるのは英数字・`-`・`_` (`upd-lo` 可、`.` や空白は不可)。
- `!` 始まりの任意シェルコマンドや、値中のクォート (空白を含む 1 引数) は未対応 (将来拡張)。

## 補完

`atcoder config <TAB>` は sub-subcommand (`show`/`get`/`set`/`unset`/`path`) を、`config get|set|unset <TAB>` は既知キー + 既存 `alias.<name>` を、`config set <key> <TAB>` は値候補 (`layout` なら `abc auto exercise`、bool キーなら `true false`) を補完する。`atcoder <TAB>` のサブコマンド位置には組み込みに加え `[alias]` の名前も出る (説明は展開先)。詳細は [`atcoder-completion-usage.md`](atcoder-completion-usage.md)。

## 注意

- config は**手編集も可**。`[alias]` を直接書いてもよい。`config set`/`unset` は他セクション・未知キーを保全して書き戻す。
- alias は展開して**組み込みサブコマンドに解決される**だけで、それ自体は副作用を持たない (解答・キャッシュには触れない)。

## 関連

- 設定ファイル基盤と XDG: [ADR 0003](decisions/0003-user-config-xdg-toml.md) / 要件 007
- サブコマンドのキーレジストリ: 要件 009
- 既定レイアウト: 要件 017 / [`atcoder-test-usage.md`](atcoder-test-usage.md)
- alias: 要件 016 / [`atcoder-completion-usage.md`](atcoder-completion-usage.md)
