# 006: CLI ツール名を `exercise` から `atcoder` へ改名

## 概要

CLI ツールの名前を `exercise` から `atcoder` に改める。コマンド呼び出し (`exercise test` → `atcoder test`)、ソースディレクトリ (`cmd/exercise/` → `cmd/atcoder/`)、ビルド成果物名、ドキュメント・skill 内の呼び出し表記、ツール名を冠した利用ドキュメントのファイル名を一括で更新する。**練習ディレクトリ `exercise/YYYY/MM/DD/` とレイアウト識別子 `exercise` (`Exercise` struct・`--layout exercise`) は別概念として据え置く。**

> 注: このドキュメントは改名の「旧名 → 新名」を意図的に併記する。一括置換の対象に含めないこと (旧名側の例まで書き換わると自己矛盾する)。

## 背景・目的

- リポジトリ名は `atcoder-daily-training`、Go module も `github.com/cry999/atcoder-daily-training`、キャッシュ階層も `atcoder-tools` と、既に「atcoder」で揃っている。CLI だけが `exercise` を名乗っており、ツールの実体 (AtCoder の問題を fetch/test/run/submit する) と名前が乖離している。
- "exercise" はこの repo で **2 つの別概念**を指す多義語になっている。今回の改名対象は前者のみ:
  1. **CLI ツール** — バイナリ・`cmd/exercise/`・コマンド呼び出し (← 改名する)
  2. **練習ワークフロー** — 日々の練習解答を置く `exercise/YYYY/MM/DD/` ツリーと、それを解決する `Exercise` レイアウト・`--layout exercise` (← 据え置く)

## スコープ

| 区分 | 対象 | 扱い |
|---|---|---|
| 当面のスコープ | CLI ツール名 (コマンド・dir・成果物・呼び出し表記・ツール名を冠した docs) | 改名する |
| スコープ外 (据え置き) | 練習ディレクトリ・`Exercise` レイアウト struct・`"exercise"` レイアウト名・`--layout exercise` | 変更しない (別概念) |
| スコープ外 (据え置き) | コミット済み練習解答ファイル群 (`exercise/**/*.py` 等) | 移動しない |
| スコープ外 (据え置き) | Go module path・`atcoder-tools` キャッシュ名 | 既に atcoder。変更しない |
| スコープ外 (据え置き) | requirements 連番ファイル名 (`001-exercise-test.md` 等) | 歴史的なスペック記録名。ファイル名は据え置き、本文中のコマンド呼び出し表記のみ更新 |

## 改名の判別ルール (変える / 据え置く)

機械置換で事故らないよう、**字面で**判別できるルールに落とす。

### 変える (CLI ツールを指す字面)

| パターン | 置換 |
|---|---|
| `exercise` + 半角スペース + サブコマンド (new/test/run/submit/stats/commit) | 先頭を `atcoder` に |
| `cmd/exercise` | `cmd/atcoder` |
| バッククォート単独のツール名 (ツール文脈のもの) | `atcoder` に |
| 散文中のツール参照 (`exercise CLI` / `exercise ツール` / `exercise コマンド`) | `atcoder …` に |
| ビルド成果物名 (`fixtures/run.sh` の `$TOOL_DIR/exercise`) | `$TOOL_DIR/atcoder` に |
| ツール名を冠した利用 docs のファイル名 (`exercise-{test,run,commit,stats}-{usage,architecture,testing}.md`) | `atcoder-…` に |

### 据え置く (練習ワークフロー / レイアウト / 別概念を指す字面)

| パターン | 理由 |
|---|---|
| スラッシュ付きパス (`exercise/YYYY/MM/DD/`, `filepath.Join("exercise", …)`) | 練習ディレクトリ。CLI 名ではない |
| `--layout exercise` / レイアウト選択肢の `exercise` | レイアウト識別子 |
| Go の `Exercise` struct / `"exercise"` (レイアウト名文字列) | レイアウト実装 |
| `stats.Scan("exercise")` / 「root (通常 "exercise")」 | stats が集計する練習ツリーの root |
| 英文の「exercise directory」 (`failed to create exercise directory`) | 練習ディレクトリの説明文 |
| 英動詞の "exercise" (`so we can exercise --layout=auto/abc`) | 「(機能を)動かす」の意 |
| `atcoder-tools` / `atcoder-daily-training` | キャッシュ名・module path (既に atcoder) |
| requirements 連番ファイル名 | 歴史的スペック記録名 |

## ディレクトリ / ファイルの改名 (git mv)

| 旧 | 新 |
|---|---|
| `cmd/exercise/` | `cmd/atcoder/` |
| `docs/tools/exercise-test-usage.md` | `docs/tools/atcoder-test-usage.md` |
| `docs/tools/exercise-test-architecture.md` | `docs/tools/atcoder-test-architecture.md` |
| `docs/tools/exercise-test-testing.md` | `docs/tools/atcoder-test-testing.md` |
| `docs/tools/exercise-run-usage.md` | `docs/tools/atcoder-run-usage.md` |
| `docs/tools/exercise-commit-usage.md` | `docs/tools/atcoder-commit-usage.md` |
| `docs/tools/exercise-stats-usage.md` | `docs/tools/atcoder-stats-usage.md` |

`cmd/exercise/` 配下の Go ファイルは `package main` で他からは import されないため、import path の書き換えは発生しない (module path も不変)。

## 影響範囲

| ファイル / 範囲 | 変更内容 |
|---|---|
| `cmd/exercise/` → `cmd/atcoder/` | dir 改名。`main.go` の `usage()` 文字列・エラープレフィックスを改名。`new.go` の起動例コメント。練習 dir メッセージ (「exercise directory」) は据え置き |
| `internal/cachepath/cachepath.go` | doc コメントのツール参照を改名。`AppName = "atcoder-tools"` は据え置き |
| `internal/testexec/{test,judge}.go` | コメントのコマンド呼び出し表記 |
| `internal/runexec/runexec.go` | package コメントのコマンド呼び出し / `cmd/exercise` |
| `internal/contestmeta/contestmeta.go` | コメントのコマンド呼び出し表記 |
| `internal/{layout,stats}/…` | **変更なし** (Exercise レイアウト・`stats.Scan("exercise")` は据え置き) |
| `fixtures/run.sh`, `fixtures/README.md` | `BIN` 名・`./cmd/exercise` ビルド・コマンド呼び出しコメント。練習 dir staging パス (`$STAGE/exercise/…`) は据え置き |
| `docs/tools/*.md` (living docs 6 本) | ファイル改名 + 本文のコマンド/相互リンク更新 |
| `docs/tools/{abc-todo,todo}.md` | コマンド呼び出し・doc 相互リンク・ツール参照を更新 (レイアウト名 `exercise` は据え置き) |
| `docs/tools/requirements/00[1-5]-*.md` | 本文のコマンド呼び出し・living doc 相互リンク更新 (ファイル名は据え置き) |
| `.claude/skills/{feature,smallwork,triage,test-tool}/SKILL.md` | frontmatter description と本文のツール参照 / コマンド呼び出し / `cmd/exercise` / doc path 参照 |
| `CLAUDE.md` | コマンド呼び出しを更新。練習 dir レイアウト規約 (`exercise/<YYYY>/…`) は据え置き |

## 動作仕様

| 項目 | 仕様 |
|---|---|
| 振る舞いの変化 | なし。コマンド名と内部識別子のみの改名で、サブコマンド・フラグ・exit code・出力フォーマットは不変 |
| 後方互換 | 旧名のエイリアスは設けない (一人称 repo であり、移行期間を持つ利得が薄い)。古いビルド成果物は各自で再ビルド |
| 練習ワークフロー非破壊 | 練習 dir への解答配置・`--layout exercise`・当日 dir 検出は従来どおり動く |
| キャッシュ互換 | キャッシュは `atcoder-tools` のままなので、改名前に取得したサンプル/メタはそのまま再利用される |

## エラーハンドリング

改名のみで制御フローは変えないため、新規のエラー経路はない。exit code 規約 (引数/フラグ誤り = 2、実行時失敗 = 1、成功 = 0) は不変で、fixture スモークで全件の exit code を従来どおり assert する。

## 非機能要件

- **振る舞い不変**: `fixtures/run.sh` の全 `run_case` が改名前と同じ exit code を返すこと。
- **練習解答非破壊**: コミット済みの `exercise/**` 解答ファイルには一切触れない。
- **多義語の取り違え防止**: 上記「判別ルール」に従い、レイアウト/練習 dir を指す `exercise` を CLI 名と取り違えて置換しない。実装後に `exercise` 残存箇所を全 grep し、各々が「据え置き」側であることを確認する。

## 検証

1. `go build ./...` が通る。
2. `./fixtures/run.sh` (test-tool skill) が全件 PASS (ビルド対象を `./cmd/atcoder` に更新後)。
3. `grep -rI 'exercise' .` の残存が、すべて「据え置き」区分 (練習 dir / レイアウト / requirements 連番名 / atcoder-tools / 英動詞) に該当することを目視確認。

## 用語

- `contest_id`=`abc457` / `contest_num`=`457` / `task_id`=`abc457_d` / `letter`=`d` (既存要件に準拠)。
- **CLI ツール**: `atcoder` (旧 `exercise`)。バイナリ・`cmd/atcoder/`・コマンド呼び出し。
- **練習ワークフロー / レイアウト**: `exercise/YYYY/MM/DD/` ツリーと `Exercise` レイアウト。改名対象外。

## 関連ドキュメント

- 利用手引 (改名後): `docs/tools/atcoder-{test,run,commit,stats}-usage.md`, `atcoder-test-architecture.md`
- ロードマップ: `docs/tools/abc-todo.md` / `docs/tools/todo.md`
- ルート規約: `CLAUDE.md`
