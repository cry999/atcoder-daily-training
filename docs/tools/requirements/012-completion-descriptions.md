# `atcoder completion` 補完候補の説明文 要件定義

## 概要

シェル補完の候補に **簡単な説明文** を添え、fzf (fzf-tab) や fish のネイティブ補完で「候補名 — 説明」の形で見えるようにする。サブコマンド名・各フラグ・`--layout`/シェル/`config` サブコマンド等の静的候補に 1 行説明を持たせ、隠しヘルパ `atcoder __complete` の出力を `値<TAB>説明` 形式に拡張する。各シェルの補完スクリプトは、説明を出せるもの (zsh の `_describe`・fish のネイティブ tab 区切り) は表示し、出せない bash は従来どおり候補名のみを並べる。

`docs/tools/requirements/008-atcoder-completion.md` (補完の基盤) の上に乗る純粋な追加で、候補集合そのものは変えず「各候補に説明を付ける」だけ。

## 背景・目的

- 補完候補が出ても、`--case` と `--cases`、`-d` と `-s` のような似たフラグは名前だけでは用途を思い出しづらい。**候補の隣に一言説明**があると、思い出しコストが下がる。
- fzf-tab (zsh) を使うと候補が fzf のリストに並び、各行に説明を出せる。fish も `候補<TAB>説明` をネイティブに表示する。この 2 シェルで「補完しながら説明が読める」体験にしたい。
- bash は素の `compgen`/`COMPREPLY` では候補ごとの説明を並べられないため、**bash は候補名のみ** (従来挙動を維持) とする。説明表示の対象は zsh + fish に絞る。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 説明を付ける候補 | サブコマンド名、各サブコマンドのフラグ、`--layout` の値、`completion` のシェル、`config` の sub-subcommand | `config` キー/値、`--case` 番号など動的候補 |
| 説明を表示するシェル | **zsh** (`_describe`、fzf-tab/標準メニュー両対応) と **fish** (tab 区切りネイティブ) | bash (fzf 連携を明示的に挟む方式) / powershell |
| `__complete` 出力 | `値` または `値<TAB>説明` の 1 行 1 件 | 候補のグループ分け・色 |
| 動的候補 (contest_id / letter) | 説明なし (値のみ) | 「手元にある」「キャッシュ済み」等のヒント |
| 副作用 | 読み取り専用 (008 と同じ) | — |

## CLI 仕様

ユーザ向けコマンド (`completion <shell>` / 隠し `__complete`) の **引数仕様は 008 から不変**。変わるのは隠しヘルパの **出力フォーマット** と、生成される補完スクリプトの中身。

### `atcoder __complete -- <words...>` の出力 (拡張)

- 1 行 1 候補。各行は **`値`**、または説明があれば **`値<TAB>説明`** (タブ 1 個区切り)。
- 説明は省略可能。動的候補 (contest_id・letter・config キー/値) は値のみを出す。
- 従来どおり **常に exit 0**、I/O エラーは握りつぶして空出力。
- タブ以降が説明、という約束により、説明を解釈しないシェル (bash) は値列だけを取り出せる。

### 各シェルの補完スクリプト挙動

| シェル | 説明表示 | 実現方法 |
|---|---|---|
| zsh | ✅ する | 各行を `値`/`説明` に分け、説明付きは `_describe` に `値:説明` で渡す。説明なしは `compadd`。fzf-tab でも標準メニューでも説明が出る |
| fish | ✅ する | `complete -a '(…)'` が返す各行の `値<TAB>説明` を fish がネイティブに「値 — 説明」と表示。スクリプトは従来とほぼ同じ (出力を素通し) |
| bash | ❌ しない | 各行をタブで分割し **値列だけ** を集めて `compgen -W` に渡す (説明はターミナルに出さない)。挙動は従来と同じ候補名のみ |

### 出力イメージ

```
$ atcoder __complete -- ""
new	scaffold today's exercise dir (or an abc contest)
test	run a solution against downloaded samples
run	run a solution on ad-hoc stdin
submit	open the AtCoder submission page
stats	show daily practice statistics
config	show or change tool settings
commit	git-commit today's exercise solutions
completion	print a shell completion script

$ atcoder test abc457 --<Tab>     # zsh + fzf-tab
  --task        task ID or short letter (e.g. d)
  --refresh     force refetch sample cases
  --timeout     override time limit (e.g. 5s)
  --case        run only the given case(s)
  --watch       re-run on file change (needs a TTY)
  ...
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| 静的候補 (サブコマンド/フラグ/layout/shell/config sub) | 値 + 説明を返す |
| 動的候補 (contest_id / letter / config キー・値) | 値のみ (説明なし) |
| 末尾語による前方一致フィルタ | 008 と同じ。値で前方一致し、説明はフィルタに影響しない |
| bash で説明付き候補 | 値列のみ抽出して補完 (説明は無視) |
| zsh/fish で説明なし候補 | 値のみ表示 (説明欄は空) |
| 説明に区切り文字 (`:` 等) を含む | zsh `_describe` は最初の `:` までを値とみなすが、**値側に `:` は無い** (サブコマンド/フラグ/値) ため安全。説明側の `:` は表示されるだけ |

- **既存の候補集合は不変**: 何が候補に出るか (008 の判定フロー) は変えない。各候補に説明を添えるだけ。
- **stats の `--last`/`-l` をフラグ表に追加**: 010 (ローリング期間) で追加した `--last`/`-l` が補完のフラグ表に未反映だったので、本変更で併せて登録する (フラグ表と実フラグの一致をとる)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/complete/complete.go` | `Candidate{Value, Desc}` 型を追加。静的テーブル (サブコマンド/フラグ/layout/shell/config sub) を説明付きに。`Complete` の戻り値を `[]Candidate` に変更。動的候補は `plain()` で説明なし Candidate に包む。`filterPrefix` を Value 基準に。stats フラグ表へ `--last`/`-l` を追加 |
| `cmd/atcoder/completion.go` | `cmdComplete` を `値<TAB>説明` 出力に変更。bash/zsh スクリプトを説明対応に書き換え (fish は素通しのまま) |
| `internal/complete/complete_test.go` | `Complete` の戻り値変更に追従。説明が付くこと・動的候補が説明なしであることを検証 |
| `fixtures/run.sh` | `__complete` の出力検証を `値<TAB>説明` 形式に更新 (値列で一致確認 + 説明が付くことの確認) |
| `docs/tools/usage/completion.md` | 説明表示 (zsh/fish) と bash の扱いを追記 |
| `docs/tools/decisions/0004-shell-completion-no-framework.md` | 後続として本要件へのリンクを追記 |

### 型と公開 API (素描)

```go
package complete

// Candidate は補完候補 1 件。Desc は空可 (説明なし)。
type Candidate struct {
    Value string
    Desc  string
}

// Complete は `atcoder` 以降のトークン列を受け取り、次単語の候補 (説明付き) を返す。
// __complete の本体。決して error を返さない。
func Complete(root string, words []string) []Candidate

// Subcommands / Flags は従来どおり値のみ ([]string) を返す薄いラッパとして残す。
func Subcommands() []string
func Flags(sub string) []string
```

- 説明文は `cmd/atcoder/*.go` の各フラグ help 文字列に整合させる (乖離しないよう、フラグ追加時はここも更新する旨を 008 同様に明記)。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `completion` の `<shell>` 欠落 / 未対応 | usage / エラー表示 (008 と同じ) | 2 |
| `__complete` の I/O エラー | 握りつぶして空出力 (008 と同じ) | 0 |
| 説明付き候補の解釈不能なシェル (bash) | 値列のみ使用、説明は無視 | 0 |

- exit code 規約は 008 から不変 (`completion` 引数誤り = 2、`__complete` = 常に 0)。

## 非機能要件

- **既存非破壊**: 候補集合・判定フロー・exit code は不変。`__complete` の出力に説明列が増えるだけで、値列の意味は同じ。
- **依存ゼロ追加**: 標準 `flag` のまま。`go.mod` を変えない。
- **シェル非依存ロジック**: 説明文も含め候補生成は Go (`__complete`) に集約。3 シェルのスクリプトは「説明をどう見せるか」だけを担う薄いラッパに保つ。
- **応答が速い**: 説明は静的テーブルの定数で、列挙コストは増えない。
- **読み取り専用・安全**: 補完経路は副作用を持たない (008 と同じ)。

## 将来の拡張ポイント

- bash でも fzf を明示的に介して説明を見せる方式 (`COMP` を fzf に渡すラッパ)。
- `config` キー/値・`--case` 番号など動的候補への説明付与。
- `--last` の値補完 (`7d`/`1w`/`1m`/`1y` を説明付きで提示)。
- フラグ表と説明を実コードから生成して二重管理を解消する。

## 用語

- **Candidate**: 補完候補 1 件。値 (`Value`) と任意の説明 (`Desc`)。
- **静的候補 / 動的候補**: 008 に準拠。説明は主に静的候補に付ける。
- **fzf-tab**: zsh の補完を fzf のリストに置き換えるプラグイン。`_describe` の説明をそのまま行に出す。

## 関連ドキュメント

- `docs/tools/requirements/008-atcoder-completion.md` (補完の基盤・候補生成)
- `docs/tools/requirements/010-stats-rolling-window.md` (stats `--last`。本変更でフラグ表に登録)
- `docs/tools/decisions/0004-shell-completion-no-framework.md` (FW 非導入の決定記録)
- `docs/tools/usage/completion.md` (利用手引)
