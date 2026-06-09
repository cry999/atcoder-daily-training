# `atcoder completion` 利用手引

`atcoder completion <shell>` でシェル補完スクリプトを生成し、サブコマンド・フラグ・`<contest>`・`--task` などを Tab 補完できるようにする。

- 要件定義: [requirements/008-atcoder-completion.md](./requirements/008-atcoder-completion.md)
- 決定記録: [ADR 0004](./decisions/0004-shell-completion-no-framework.md) (CLI フレームワークを足さず手書きにした理由)

## インストール

生成したスクリプトをシェルに読み込ませる。`atcoder` が `PATH` 上にあること (`go install ./cmd/atcoder` 等) が前提。

### bash

```sh
# その場で有効化 (現在のシェルのみ)
source <(atcoder completion bash)

# 恒久化: ~/.bashrc に追記
echo 'source <(atcoder completion bash)' >> ~/.bashrc
```

### zsh

```sh
# その場で有効化
source <(atcoder completion zsh)

# 恒久化: ~/.zshrc に追記 (compinit より後ろ)
echo 'source <(atcoder completion zsh)' >> ~/.zshrc
```

補完が効かない場合は `~/.zshrc` で `autoload -Uz compinit && compinit` が呼ばれているか確認する。

### fish

```sh
# その場で有効化
atcoder completion fish | source

# 恒久化: 補完ディレクトリに保存
atcoder completion fish > ~/.config/fish/completions/atcoder.fish
```

## 補完できるもの

| 位置 | 補完内容 | ソース |
|---|---|---|
| サブコマンド | `new test run submit stats commit completion` | 静的 |
| フラグ (`-` 始まり) | そのサブコマンドのフラグ (`--task`, `--layout`, `--watch` …) | 静的 (実フラグと手動同期) |
| `<contest>` | `abc457` 等の contest_id | 手元の `abc/`・`arc/`・`awc/` ディレクトリ + fetch 済みキャッシュ |
| `--task <値>` | letter (`a`〜`g` 等) | 既存解答ファイル + `contest.toml` の tasks。無ければ既定の `a`〜`g` |
| `--layout <値>` | `auto abc exercise` | 静的 |

```sh
$ atcoder te<Tab>                 # → test
$ atcoder test ab<Tab>            # → abc453 abc457 abc461 …
$ atcoder test abc457 --ta<Tab>   # → --task
$ atcoder test abc457 --task <Tab># → a b c d e f g
$ atcoder new <Tab>               # → abc
```

## 仕組み

- 補完候補は隠しヘルパ `atcoder __complete -- <words...>` が生成する。各シェルのスクリプトは現在のトークン列をこのヘルパに渡し、返ってきた候補を並べるだけの薄いラッパ。
- `__complete` は**常に終了コード 0**。内部で I/O エラーが起きても握りつぶして空候補を返し、補完を壊さない。
- **読み取り専用・オフライン**。ディレクトリとキャッシュを読むだけで、ネットワーク・認証・解答ファイルに一切触れない。
- contest 候補はカレントディレクトリ (リポジトリルート想定) 基準。repo 外で実行すると手元のディレクトリ分は出ず、キャッシュ分のみになる (エラーにはならない)。

## 制約・注意

- **CLI フレームワークは未導入**。標準 `flag` のまま補完だけを手書きで足しているため、フラグを増やしたら `internal/complete/` のフラグ表 (`subFlags`) も更新する必要がある (乖離するとミスリードな補完になる)。
- 対応シェルは `bash` / `zsh` / `fish`。それ以外を渡すと exit 2。
- `--case` の番号や `--in`/`--out` のファイル補完は未対応 (将来拡張)。ファイルはシェル既定の補完に委ねる。

## 関連

- [requirements/008-atcoder-completion.md](./requirements/008-atcoder-completion.md) — 要件定義
- [atcoder-test-testing.md](./atcoder-test-testing.md) — `fixtures/run.sh` に completion の smoke を追加済み
