---
name: bugfix
description: atcoder CLI (cmd/atcoder + internal/) の不具合を「再現 → 原因特定 → 最小修正 → 回帰テストで固定 → 検証 → コミット」で直すデバッグ向けワークフロー。期待と違う出力・誤った exit code・パニック・fetch/ログイン/judge の挙動不良など、既存挙動の「壊れ」を直す作業で使う。feature (新挙動を足す) や smallwork (typo・微修正) とは別物で、バグを再現する fixture / ユニットテストを先に書いて赤にし、修正で緑にするのが肝。練習解答 (Python) の WA/TLE/RE 直しには使わない (それは smallwork)。
---

# bugfix

`atcoder` CLI ツール (Go) の不具合を直すためのデバッグ手順書。typo 直し (smallwork) でも新機能追加 (feature) でもなく、「既存の挙動が壊れている」のを直す作業に特化する。この repo は fixture と `go test` で振る舞いを固定する流儀なので、**バグを再現するテストを先に書いて赤にし、修正で緑にする** のを背骨にする。

## いつ使うか

- `atcoder <cmd>` が期待と違う出力をする / 誤った exit code を返す。
- パニック・nil 参照・想定外のエラーで落ちる。
- fetch・ログイン・submit・judge・diff・キャッシュなど内部機構の挙動不良。
- 既存 fixture / `go test` が落ちる、または「落ちるべきなのに通っている」。
- リファクタや別機能追加で入った regression を戻す。

## いつ使わないか (→ 別の道)

- 練習解答 (Python) が WA/TLE/RE する → **`smallwork`** (`exercise/`・`abc/`・`adt/`・`dp/` 等。再現も検証もサンプル照合で、ツールとは無関係)。
- `atcoder` に**新しい挙動**を足す (新サブコマンド・新フラグ・新モード) → **`feature`**。バグ直しの過程で「仕様判断が要る / 新挙動を生やす」と分かったら、その worktree のまま feature に格上げする。
- typo・コメント・文言など挙動を変えない微修正 → **`smallwork`**。
- 実装 ⇄ ドキュメントのズレを直すだけ → **`maketidy`**。

## ワークフロー

### 0. worktree を切る (CLAUDE.md の必須ルール)

バグを表すブランチ名 (`fix-`接頭辞) で main から切る。

```sh
git worktree add ../atcoder-daily-training.worktrees/fix-<slug> -b fix-<slug>
```

ブランチ名はバグ内容を表す短い kebab (`fix-test-tle-exit-code`, `fix-login-panic-empty-csrf`, `fix-diff-trailing-newline`)。worktree 内は絶対パスで Write/Edit する (`cd` は permission prompt を誘発しやすい)。コミットは `git -C <worktree-path> ...`。

### 1. 再現する (まず確実に再現させる)

直す前に、手元で確実に再現させて症状を握る。憶測で直さない。

- **実コマンドで再現** — `go run ./cmd/atcoder <cmd> ...` を実際に叩き、stdout/stderr と exit code (`echo $?`) を観測する。期待値と実際値を 1 行ずつ書き出す。
- **入力を最小化** — どの引数・どのサンプル・どの環境変数で出るかを削って絞る。ネットワーク絡みは `--no-fetch` 等オフライン経路で切り分け、AtCoder への実アクセスは避ける。
- 再現条件 (コマンド・入力・期待・実際・exit code) を一旦メモしておく。これがそのまま次のテストケースになる。

### 2. 原因を特定する

再現条件から、症状が生まれる場所まで遡る。

- ディスパッチは `cmd/atcoder/main.go` の `switch os.Args[1]`。サブコマンド本体は `cmd/atcoder/<cmd>.go` (`cmdXxx(args []string) (code int, err error)` 形)。
- ドメインロジックは `internal/` に分かれている: `runner/` (プロセス実行)、`testexec/` (test の orchestration・judge・meta・fetch)、`runexec/` (run)、`contestmeta/` (contest.toml)、`layout/` (解答パス解決)、`cachepath/` (XDG キャッシュ位置)、`ui/` (Reporter・diff・chat)、`stats/`・`review/`・`complete/`・`selfupdate/`・`watch/`・`config/`。
- 既存の `*_test.go` (例 `internal/stats/stats_test.go`, `internal/layout/layout_test.go`) を読むと、その機構の期待挙動と境界が分かる。原因の当たりがついたら該当パッケージのテストを `go test ./internal/<pkg>/` で回して挙動を確かめる。

### 3. 失敗するテストを先に書く (赤にする)

修正コードより先に、バグを捉えるテストを足して **落ちることを確認** する。これが回帰テストになり、同じバグの再発を防ぐ。

- **ロジック単体のバグ** → 該当パッケージに `go test` のケースを足す。`internal/<pkg>/<name>_test.go` の既存テーブル駆動に 1 行足すのが速い。`go test ./internal/<pkg>/` で赤を確認。
- **CLI のエンドツーエンド挙動 (exit code・出力)** → `fixtures/` に再現ケースを 1 組足す (`docs/tools/atcoder-test-testing.md` の手順):
  1. `fixtures/fixture_<name>.py`
  2. `fixtures/fixture_<name>/meta.toml` (`contest = "fixture"`, `task`, `time_limit_ms`, `fetched_at`)
  3. `fixtures/fixture_<name>/tests/01.in` / `01.out`
  4. `fixtures/run.sh` に `run_case` 行 (期待 exit code 付き)
  5. `fixtures/README.md` と `atcoder-test-testing.md` の fixture 一覧に追記
- バグが既存 fixture/テストで本来 assert されているべきだったなら、その期待値を正しい側に直して赤にする。

### 4. 直す (最小の修正)

赤を緑にする最小の変更を入れる。周辺の Go スタイルに合わせ、日本語コメントは残す。スコープを広げない — リファクタしたくなったら別コミット/別作業に分ける。exit code 規約を必ず守る: **引数/フラグ誤り = 2、実行時失敗 (FAIL/RE/TLE/fetch 失敗) = 1、成功 = 0**。解答ファイル (ユーザの提出コード) を壊す副作用を入れない。

### 5. 検証する (緑を確認)

- `go build ./...` が通る。
- 3 で書いたテストが **緑になる**。
- 触ったパッケージのユニットテスト `go test ./internal/<pkg>/...` (あるいは `go test ./...`) が通る。
- `cmd/atcoder/`・`internal/runner|testexec|runexec|cachepath|ui/` を触ったら `test-tool` スキル (`./fixtures/run.sh`) で全 fixture の exit code を assert する。
- 1 で握った実コマンドの再現手順をもう一度叩き、症状が消えていることを確認する。

### 6. コミットする (Conventional Commits + scope)

`fix(<scope>)` でまとめる。scope はサブコマンド/パッケージ名。例: `fix(test): return exit 1 on TLE instead of 0`、`fix(login): guard against empty CSRF token`、`fix(diff): preserve trailing newline in expected output`。回帰テスト追加と修正は同じコミットにまとめてよい (テストが意図を示す)。原因が非自明だったらコミット本文に「なぜ起きたか/なぜこの直しか」を 1〜2 行残す。メッセージ末尾には環境指定の `Co-Authored-By` trailer を付ける。

### 7. main へマージして worktree を畳む

```sh
git merge --ff-only fix-<slug>
git worktree remove ../atcoder-daily-training.worktrees/fix-<slug>
git branch -d fix-<slug>
```

## 注意

- **テストファースト**。再現テストを先に赤にしてから直す。これをやらないと「直ったつもり」「再発検知なし」になる。
- 再現できないバグは直さない。まず確実な再現条件を作る (1 に戻る)。
- スコープを膨らませない。直し中に別のバグや改善点を見つけたら、`docs/tools/todo.md` に書き留めて今回の修正からは切り離す。
- 挙動を直す過程で「新しい挙動を生やす/仕様判断が要る」と分かったら、その worktree のまま `feature` に格上げする (要件を先に文章化)。bugfix で押し切らない。
- `--refresh` 系はキャッシュのみ対象で解答には触れない、ネットワーク fetch は smoke から切り離す (run.sh は AtCoder に触らない) — 既存の安全設計を壊さない。

## 関連

- フル機能追加ワークフロー: `feature` スキル
- 軽量ワークフロー (typo・微修正・練習解答): `smallwork` スキル
- どちらの流儀か迷う入口: `triage` スキル
- 実装 ⇄ ドキュメントの整合性点検: `maketidy` スキル
- ツールのスモークテスト / fixture 追加: `test-tool` スキル + `docs/tools/atcoder-test-testing.md`
- アーキテクチャ: `docs/tools/atcoder-test-architecture.md`
- ルート規約: `CLAUDE.md` (worktree 必須・ディレクトリ規約・exit code 規約)
