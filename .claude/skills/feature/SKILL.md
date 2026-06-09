---
name: feature
description: exercise CLI (cmd/exercise + internal/) に新機能 (サブコマンド・フラグ・言語サポート・本番対応機能など) を追加するときの確立済みワークフローを案内する。worktree を切り、要件定義 (docs/tools/requirements/NNN-*.md) → ロードマップ更新 → 実装 → fixture スモークテスト (test-tool) → 利用ドキュメント → Conventional Commits → main へマージ、の順で進める。練習問題の解答 (exercise/・abc/・adt/・dp/ 等) を書くだけの作業や、ツールに無関係なドキュメント整理では使わない。
---

# feature

`exercise` CLI に機能を足すときの開発ワークフロー手順書。この repo は「要件定義を文章化してから実装し、fixture で振る舞いを固定し、利用ドキュメントとロードマップを揃える」流儀で育てている。新機能をその流儀に乗せるための順序とチェックリストをここにまとめる。

## いつ使うか

- `exercise` の新サブコマンド (`new` / `test` / `run` / `commit` に並ぶもの) を足す。
- 既存サブコマンドにフラグ・モード・挙動を追加する (例: `run --interactive`、`new abc <contest>`)。
- `internal/` の機構を増やす (新 Runner 言語、新キャッシュ層、新 fetch 経路 など)。
- `abc-todo.md` / `todo.md` のロードマップ項目 (MVP / Phase) を 1 つ実装に落とす。

## いつ使わないか

- 練習問題の解答を書く・直すだけ (`exercise/`, `abc/`, `arc/`, `awc/`, `adt/`, `dp/`, `tessoku-book/`, `spoj/` 等)。
- ツールに無関係なドキュメント整理・リポジトリ housekeeping。
- 既存挙動を変えない純粋なリファクタリング (それでも fixture は回す → test-tool スキル)。

## ワークフロー

### 0. worktree を切る (CLAUDE.md の必須ルール)

タスクを表すブランチ名で main から worktree を切り、その中で作業・コミットする。

```sh
git worktree add ../atcoder-daily-training.worktrees/<branch> -b <branch>
```

worktree 内のファイルは絶対パスで Write/Edit する (`cd` は permission prompt を誘発しやすい)。コミットは `git -C <worktree-path> ...` で。

### 1. 要件定義を書く — `docs/tools/requirements/NNN-<name>.md`

実装の前に仕様を文章化する。既存の連番に続けて 3 桁ゼロ埋め (`001-exercise-test.md`, `002-exercise-abc-layout.md`, `003-exercise-abc-contest-meta.md` の次は `004-...`)。`003-exercise-abc-contest-meta.md` を雛形にすると速い。構成:

- **概要** — 1 段落で「何を 1 コマンド/1 フラグで済ませたいか」。
- **背景・目的** — 今のフリクション、なぜ要るか。
- **スコープ** (表) — 当面のスコープ / 将来の拡張余地。境界 (他項目との分担) を明記。
- **ディレクトリ構造 / スキーマ** — 触る/作るパス、TOML 等のスキーマを表で。
- **CLI 仕様** — 引数・フラグ表、処理ステップ (番号付き)、出力イメージ (コマンド例とその stdout)。
- **動作仕様** — 冪等性・部分更新・既存ワークフローとの共存など、表で網羅。
- **影響範囲** (表) — ファイルごとの変更内容。新規パッケージは責務と公開 API シグネチャを Go で素描。
- **エラーハンドリング** (表) — 状況 → 動作 (exit code を含む。引数/フラグ誤りは exit 2、実行時失敗は exit 1)。
- **非機能要件** — 冪等性・既存非破壊・前方互換・rate limit 配慮 など。
- **将来の拡張ポイント / 用語 / 関連ドキュメント**。

文章は日本語。ID 用語 (`contest_id`=`abc457` / `contest_num`=`457` / `task_id`=`abc457_d` / `letter`=`d`) は既存要件に合わせる。

### 2. ロードマップを更新する

機能がどちらのロードマップ項目かに応じて状態を進める:

- ABC 本番対応系 → `docs/tools/abc-todo.md` の優先順位表。`✅ DONE (<commit>)` でマークし、その項目に「決まったこと」を引用ブロックで追記する。
- ツール全般 → `docs/tools/todo.md`。

要件ドキュメントへの相互リンクを張る (ロードマップ ⇄ requirements)。

### 3. 実装する — `cmd/exercise/` + `internal/`

- ディスパッチは `cmd/exercise/main.go` の `switch os.Args[1]`。新サブコマンドはここに `case` を足し、**`usage()` の文字列も更新**する。
- サブコマンド本体は `cmd/exercise/{new,test,run,commit}.go`。`cmdXxx(args []string) (code int, err error)` 形 (`new` だけ `error` のみ)。
- ドメインロジックは `internal/` に置く: `runner/` (プロセス実行)、`testexec/` (test の orchestration・judge・meta・fetch)、`runexec/` (run)、`contestmeta/` (contest.toml)、`layout/` (解答パス解決)、`cachepath/` (XDG キャッシュ位置)、`ui/` (Reporter・diff・chat)。新しい機構は新パッケージに切る (要件の「影響範囲」で素描したとおり)。
- スタイルは周辺コードに合わせる。terse な競プロ解答とは別物で、ツール側は普通の Go。

### 4. スモークテストで振る舞いを固定する

新しい振る舞いには fixture をひと組足し、`test-tool` スキル (`./fixtures/run.sh`) で全件の exit code を assert する。手順は `docs/tools/exercise-test-testing.md`:

1. `fixtures/fixture_<name>.py`
2. `fixtures/fixture_<name>/meta.toml` (`contest = "fixture"`, `task`, `time_limit_ms`, `fetched_at`)
3. `fixtures/fixture_<name>/tests/01.in` / `01.out`
4. `fixtures/run.sh` に `run_case` 行 (expected exit code 付き)
5. `fixtures/README.md` と `exercise-test-testing.md` の fixture 一覧に追記

ネットワーク fetch を伴う機能は `--no-fetch` 等のオフライン経路で smoke する (run.sh は AtCoder に触らない)。`cmd/exercise/`・`internal/runner|testexec|runexec|cachepath|ui/` を触ったら必ず回す。

### 5. 利用ドキュメントを更新する

挙動が変わったら手引きを直す: `docs/tools/exercise-<cmd>-usage.md` (利用方法)、`-architecture.md` (内部設計)。新フラグ・新サブコマンドはコマンド表とサンプル出力に反映する。

### 6. コミットする (Conventional Commits + scope)

scope はサブコマンド名。例: `feat(new): add exercise new abc <contest> ...`、`feat(run): split interactive mode into its own --interactive flag`、`docs(tools): write contest-meta requirements`。要件→実装→docs を意味の塊でコミットを分けてよい (履歴上 1 機能が複数コミットに分かれている)。コミットメッセージ末尾には環境指定の `Co-Authored-By` trailer を付ける。

### 7. main へマージして worktree を畳む

```sh
git merge --ff-only <branch>
git worktree remove ../atcoder-daily-training.worktrees/<branch>
git branch -d <branch>
```

ロードマップに書いた `✅ DONE (<commit>)` のハッシュは、マージ後の実コミットに合っていることを確認する。

## 参照ドキュメント

- 要件の雛形: `docs/tools/requirements/003-exercise-abc-contest-meta.md`
- テスト戦略 / fixture 追加: `docs/tools/exercise-test-testing.md` + `test-tool` スキル
- アーキテクチャ: `docs/tools/exercise-test-architecture.md`
- ロードマップ: `docs/tools/abc-todo.md` (ABC 本番系) / `docs/tools/todo.md` (全般)
- 利用手引: `docs/tools/exercise-{test,run,commit}-usage.md`
- ルート規約: `CLAUDE.md` (worktree 必須・ディレクトリ規約)
- 軽量ワークフロー / 振り分け入口: `smallwork` スキル・`triage` スキル

## 注意

- 要件を飛ばして実装に走らない。この repo は「先に文章で仕様を固める」のが流儀で、後から E (本番モード判定) / G (タイマー) が `contest.toml` 等を入力にできるよう前方互換を意識して設計している。
- 解答ファイル (ユーザの提出コード) を壊す副作用を入れない。`--refresh` 系はキャッシュのみ対象で解答には触れない、が確立した安全設計。
- exit code 規約を守る: 引数/フラグ誤り = 2、実行時失敗 (FAIL/RE/TLE/fetch 失敗) = 1、成功 = 0。fixture でここを固定する。
