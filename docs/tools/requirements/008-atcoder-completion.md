# `atcoder completion` シェル補完 要件定義

## 概要

`atcoder completion <bash|zsh|fish>` で各シェル用の補完スクリプトを出力する新サブコマンドを追加する。サブコマンド名・フラグ・`<contest>` 引数・`--task` の値などを Tab 補完できるようにし、本番中・練習中の打鍵と思い出しコストを減らす。**CLI フレームワーク (cobra 等) は導入せず**、現状の標準 `flag` + 手書き dispatch をそのまま維持する。動的補完 (リポジトリ内の contest / task の列挙) は隠しヘルパ `atcoder __complete` 経由で実現し、シェルスクリプト側は「候補を Go に問い合わせて並べるだけ」に保つ。

## 背景・目的

- サブコマンドが 6 つ (`new` / `test` / `run` / `submit` / `stats` / `commit`) + 多数のフラグ (`--task` / `--layout` / `--case` / `--watch` …) に増え、毎回フラグ名を思い出して打つ手間が大きい。
- 本番でも練習でも `atcoder test abc457 --task d` のように **contest_id と letter を頻繁に手打ち**する。番号や letter の打ち間違いは無駄なフリクション。
- Tab 補完があれば、サブコマンド・フラグ・既に手元にある contest・letter を思い出さずに選べる。
- フレームワーク全面移行 (cobra) は補完が標準装備になる反面、既存 6 サブコマンド・usage・exit code 規約を全面再実装する大改修になり、コスト/リスクが見合わない。**決定: FW を入れず、補完だけを手書きで足す** (標準 `flag` のまま、依存追加なし)。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象シェル | `bash` / `zsh` / `fish` | `powershell` / `elvish` |
| 静的補完 | サブコマンド名、各サブコマンドのフラグ名 | — |
| 動的補完 | `<contest>` (手元の contest ディレクトリ + fetch 済みキャッシュ)、`--task` の letter、`--layout` の値 | `--case` の番号、`--in`/`--out` のファイル、adt の日付/letter |
| インストール | 出力スクリプトをユーザが `source` / `eval` する手動方式 | `completion --install` で rc に追記 |
| 副作用 | 読み取り専用 (ファイル列挙のみ)。ネットワーク・認証・解答ファイルに触れない | — |

## ディレクトリ構造・補完ソース

新規に作るパスは無い (コードのみ)。動的補完の **入力ソース** は既存の配置を読むだけ:

```
# contest 候補のソース (cwd = リポジトリルート基準)
abc/<contest_num>/   → contest_id = "abc<contest_num>"   (例 abc/457/ → abc457)
arc/<contest_num>/   → contest_id = "arc<contest_num>"
awc/<contest_num>/   → contest_id = "awc<contest_num>"
$XDG_CACHE_HOME/atcoder-tools/<contest_id>/  → fetch 済み contest_id (キャッシュ)

# task(letter) 候補のソース (contest が確定しているとき)
abc/<contest_num>/<letter>.py                → 既存解答ファイルの letter
$XDG_CACHE_HOME/atcoder-tools/<contest_id>/contest.toml の tasks → letter
```

- contest 候補は repo 内ディレクトリとキャッシュの **和集合** を取り、重複排除してソートする。
- task 候補は、ABC レイアウト (`abc<NNN>`) なら既存の `abc/<num>/*.py` の letter を優先し、無ければ `a`〜`g` を既定候補とする。`contest.toml` があればその `tasks` から `layout.Letter` で letter を抽出して併合する。

## CLI 仕様

```
atcoder completion <shell>        # 新規: 補完スクリプトを stdout に出力
atcoder __complete -- <words...>  # 隠し: 補完候補を 1 行 1 件で出力 (スクリプトからのみ呼ぶ)
```

### `atcoder completion <shell>`

| 引数 | 説明 |
|---|---|
| `<shell>` | `bash` / `zsh` / `fish` のいずれか。欠落・未対応は exit 2 |

- 指定シェル用の補完スクリプトを **stdout** に出力するだけ (ファイルは書かない、ネットワーク無し)。
- ユーザは出力を `source` / `eval` するか、rc ファイルに保存して読み込む (利用手引に記載)。

### 隠しヘルパ `atcoder __complete -- <words...>`

- `usage()` には**出さない**隠しコマンド。各シェルの補完スクリプトからのみ呼ばれる。
- 引数 `<words...>` は、コマンドライン上の `atcoder` 以降のトークン列 (末尾が補完中の単語で、空文字列のこともある)。
- 次に来る単語の候補を **1 行 1 件**で stdout に出力し、**常に exit 0**。内部で I/O エラー等が起きても握りつぶして空出力で終える (補完を壊さない)。

### 処理ステップ (`__complete` の判定)

`words` (= `atcoder` の後ろのトークン列) を見て、上から順に当てはめる:

1. **サブコマンド未確定** (`words` が 0〜1 語、かつ 1 語目がサブコマンド名として未確定): サブコマンド候補 (`new test run submit stats commit completion`) を末尾語で前方一致フィルタして返す。
2. **直前が値を取るフラグ**: `--task` の直後なら task(letter) 候補、`--layout` の直後なら `auto abc exercise`、`completion` の引数位置なら `bash zsh fish`。
3. **末尾語が `-` で始まる**: そのサブコマンドのフラグ名候補 (例 `test` なら `--task --refresh --timeout --case --layout --jobs --watch -v -d -s …`) を前方一致で返す。
4. **位置引数 `<contest>` の位置**: contest 候補 (上記ソースの和集合) を前方一致で返す。
5. **いずれにも当てはまらない**: 空 (候補なし)。

### 出力イメージ

```
$ atcoder completion bash
# bash completion for atcoder
_atcoder() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  local cands
  cands="$(atcoder __complete -- "${COMP_WORDS[@]:1:COMP_CWORD}")"
  COMPREPLY=( $(compgen -W "${cands}" -- "${cur}") )
}
complete -F _atcoder atcoder

$ source <(atcoder completion bash)
$ atcoder te<Tab>            # → test
$ atcoder test ab<Tab>       # → abc453 abc457 abc461 …  (手元の abc/ + キャッシュ)
$ atcoder test abc457 --ta<Tab>   # → --task
$ atcoder test abc457 --task <Tab># → a b c d e f g
```

## 動作仕様

### 静的補完

- サブコマンド位置では `new test run submit stats commit completion` を返す (`__complete` 自身は隠すので候補に出さない)。
- `-` 始まりの語では、確定済みサブコマンドの **flag 表**から候補を出す。flag 表は `internal/complete` に各サブコマンドぶん持つ (実フラグ定義と一致させる)。

### 動的補完

- `<contest>`: `abc/`・`arc/`・`awc/` のサブディレクトリ名から組んだ contest_id と、キャッシュ dir の contest_id を和集合 → 重複排除 → ソート → 末尾語で前方一致。
- `--task <値>`: contest が `words` から取れていれば task(letter) 候補。取れなければ空。
- `--layout <値>`: `auto abc exercise` 固定。
- `stats` の期間フラグ: `--week --month --year`。

### カレントディレクトリ依存

- contest 列挙は **cwd (リポジトリルート想定) 基準**。repo 外で実行した場合は repo 内ソースが空になり、キャッシュ分だけが候補になる (エラーにはしない)。
- キャッシュ列挙は `cachepath.Base()` に従う (`XDG_CACHE_HOME` 尊重)。

### 補完が壊れない設計

- `__complete` は**常に exit 0**。候補が無ければ空出力。内部の `os.ReadDir` 失敗等は無視する。
- 補完スクリプトは候補の取得を丸ごと `__complete` に委譲し、シェル間でロジックを重複させない。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| 新規 `cmd/atcoder/completion.go` | `cmdCompletion(args []string) (int, error)` (`completion <shell>` のスクリプト出力) と `cmdComplete(args []string) (int, error)` (`__complete` ヘルパ)。各シェルのスクリプトテンプレートを `//go:embed` か文字列定数で保持 |
| `cmd/atcoder/main.go` | dispatch に `case "completion"` と隠し `case "__complete"` を追加。`usage()` に `atcoder completion <bash\|zsh\|fish>` を追記 (`__complete` は載せない) |
| 新規 `internal/complete/` | 候補列挙ロジックを集約 (`cmd` から分離してテスト可能に)。サブコマンド表・フラグ表・contest/task 列挙・`Complete` 本体 |
| `internal/complete/complete_test.go` | `Complete` のトークン列 → 候補のテーブルテスト (cwd を一時 dir に差し替えて contest 列挙を検証) |
| `fixtures/run.sh` | `completion bash\|zsh\|fish` が exit 0、未対応シェル/欠落が exit 2、`__complete` がサブコマンド/contest 候補を返す smoke を追加 |
| `docs/tools/atcoder-completion-usage.md` | 利用手引 (3 シェルのインストール手順 + 補完対象の一覧) |
| `docs/tools/todo.md` | 項目 L として追記し、本要件へ相互リンク |

### 新規 `internal/complete/` パッケージの責務

```go
package complete

// Subcommands は補完対象のサブコマンド名 (__complete は含めない)。
func Subcommands() []string

// Flags は指定サブコマンドのフラグ候補 (例 "--task", "-v")。未知サブコマンドは nil。
func Flags(sub string) []string

// Contests は root 配下の abc/arc/awc とキャッシュから contest_id 候補を集める
// (和集合・重複排除・ソート)。I/O エラーは無視。
func Contests(root string) []string

// Tasks は contest の letter 候補を返す (既存解答ファイル + contest.toml の tasks)。
func Tasks(root, contest string) []string

// Complete は `atcoder` 以降のトークン列を受け取り、次単語の候補を返す。
// __complete の本体。決して error を返さない (壊れない補完)。
func Complete(root string, words []string) []string
```

- `Flags` の各表は `cmd/atcoder/*.go` の実フラグと一致させる (乖離するとミスリードな補完になるため、フラグ追加時はここも更新する旨を要件・利用手引に明記)。
- contest_id の組み立てとレイアウト判定は既存 `internal/layout` (`ContestNum` / `Letter` / `Detect`) を流用する。

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `completion` の `<shell>` 欠落 | usage を出して exit 2 |
| `completion` に未対応シェル | "unsupported shell: <x> (want bash, zsh, or fish)" で exit 2 |
| `__complete` 実行中の I/O エラー (ディレクトリ読めない等) | 握りつぶして空候補、exit 0 |
| `__complete` の引数が空 | サブコマンド候補を返す (exit 0) |
| repo 外で補完 | repo 内ソースは空、キャッシュ分のみ。エラーにしない |

## 非機能要件

- **既存非破壊**: 既存 6 サブコマンドの挙動・usage・exit code は不変。dispatch に case を足すだけ。
- **依存ゼロ追加**: 標準 `flag` のまま。`go.mod` は変えない (FW 非導入の帰結)。
- **応答が速い**: 補完は対話的に毎 Tab 呼ばれる。動的列挙はディレクトリ 1 階層の走査のみ。ネットワーク・再帰探索をしない。
- **読み取り専用・安全**: 補完経路は CLI 本体の状態や解答ファイルに副作用を持たない。
- **シェル非依存ロジック**: 候補生成は Go (`__complete`) に集約。3 シェルのスクリプトは薄いラッパに保ち、ロジック重複を避ける。
- **exit code 規約遵守**: `completion` の引数エラーは 2。`__complete` は常に 0 (補完の安定性を最優先)。

## 将来の拡張ポイント

- `atcoder completion --install` で rc ファイル (`~/.bashrc` 等) に追記する補助。
- `--case` の番号補完 (`tests/` 走査)、`--in`/`--out` のファイル補完 (シェル既定に委譲も可)。
- `powershell` / `elvish` 対応。
- adt レイアウト (日付 + letter) の補完。
- フラグ表を実コードから生成して二重管理を解消する (現状は手書き表で同期)。

## 用語

- **静的補完**: コンテキストに依存しない固定候補 (サブコマンド名・フラグ名・`--layout` の値)。
- **動的補完**: 実行環境 (手元のディレクトリ・キャッシュ) を読んで組む候補 (contest_id・letter)。
- **隠しヘルパ (`__complete`)**: usage に出さず、補完スクリプトからのみ呼ばれる候補生成コマンド。
- **補完スクリプト**: `completion <shell>` が出力する、シェルに読み込ませる定義 (`complete -F` 等)。
- `contest_id` (`abc457`) / `contest_num` (`457`) / `task_id` (`abc457_d`) / `letter` (`d`) は既存要件に準拠。

## 関連ドキュメント

- `docs/tools/requirements/003-exercise-abc-contest-meta.md` (要件雛形 / contest.toml・キャッシュ配置)
- `docs/tools/requirements/006-rename-cli-to-atcoder.md` (CLI 名 `atcoder` 化)
- `docs/tools/todo.md` (一般 TODO。項目 L が本要件)
- `docs/tools/exercise-test-testing.md` (fixture 追加手順)
- `docs/tools/atcoder-completion-usage.md` (利用手引。本機能で新設)
