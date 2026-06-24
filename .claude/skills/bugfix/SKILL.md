---
name: bugfix
description: atcoder CLI (cmd/atcoder + internal/) の不具合を「再現 → 原因特定 → 実装範囲・影響範囲の確認 → 回帰テストで固定 → 最小修正 → 検証 → レビュー担当サブエージェントのレビュー → コミット」で直すデバッグ向けワークフロー。期待と違う出力・誤った exit code・パニック・fetch/ログイン/judge の挙動不良など、既存挙動の「壊れ」を直す作業で使う。feature (新挙動を足す) や smallwork (typo・微修正) とは別物で、実装前に直す範囲と波及範囲を確認し、バグを再現する fixture / ユニットテストを先に書いて赤にし、修正で緑にし、別視点のサブエージェントにレビューさせてからコミットするのが肝。練習解答 (Python) の WA/TLE/RE 直しには使わない (それは smallwork)。
---

# bugfix

`atcoder` CLI ツール (Go) の不具合を直すためのデバッグ手順書。typo 直し (smallwork) でも新機能追加 (feature) でもなく、「既存の挙動が壊れている」のを直す作業に特化する。この repo は fixture と `go test` で振る舞いを固定する流儀なので、**バグを再現するテストを先に書いて赤にし、修正で緑にする** のを背骨にする。実装に入る前に直す範囲と影響範囲を確認し、修正後は別視点のレビュー担当サブエージェントにレビューさせてからコミットする。

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

### 3. 実装範囲・影響範囲を確認する (実装に入る前に)

原因が掴めたら、**手を動かす前に** どこを直すか (実装範囲) と、その変更が他に何を揺らすか (影響範囲) を洗い出して言語化する。憶測でいきなり直さない。ここを飛ばすと「直したつもりで別経路が壊れる / 同種の取りこぼしを見逃す」になる。

- **実装範囲** — 直すファイル・関数・行を具体的に挙げる。最小修正で済むか、それとも複数箇所か。修正方針 (どう直すか) を 1〜2 案、トレードオフ込みで書き出す。
- **影響範囲** — その関数/値を呼ぶ他の経路を `grep` で洗い、**同じ不具合が別経路にもないか**を確認する (例: chat の Ctrl+S が `start` と `test --interactive` の両経路から組まれる、ある exit code 規約が全サブコマンドに効く、共有ヘルパーの挙動変更が波及する)。直接の修正点だけでなく、巻き込む可能性のあるパッケージ・fixture・ドキュメント・利用者の解答ファイルを列挙する。
- **確認を取る** — 実装範囲と影響範囲が非自明・広い (複数経路に波及する / 公開挙動や exit code 規約に触る / 解答ファイルや既存 fixture を書き換える) ときは、着手前にユーザへ範囲を提示して合意を取る。局所的で自明な 1 箇所修正ならそのまま進めてよい。
- ここで「影響が広い・仕様判断が要る・新挙動を生やす」と分かったら、bugfix で押し切らず `feature` に格上げする。

整理した実装範囲・影響範囲は、次の回帰テストで「どの経路を assert するか」「どの別経路も守るか」の指針になる。

### 4. 失敗するテストを先に書く (赤にする)

修正コードより先に、バグを捉えるテストを足して **落ちることを確認** する。これが回帰テストになり、同じバグの再発を防ぐ。3 で洗った影響範囲に別経路の取りこぼしがあれば、その経路も assert する (例: 片方の経路だけ直して他方を放置しないよう、構成を固定するテストを足す)。

- **ロジック単体のバグ** → 該当パッケージに `go test` のケースを足す。`internal/<pkg>/<name>_test.go` の既存テーブル駆動に 1 行足すのが速い。`go test ./internal/<pkg>/` で赤を確認。
- **CLI のエンドツーエンド挙動 (exit code・出力)** → `fixtures/` に再現ケースを 1 組足す (`docs/tools/atcoder-test-testing.md` の手順):
  1. `fixtures/fixture_<name>.py`
  2. `fixtures/fixture_<name>/meta.toml` (`contest = "fixture"`, `task`, `time_limit_ms`, `fetched_at`)
  3. `fixtures/fixture_<name>/tests/01.in` / `01.out`
  4. `fixtures/run.sh` に `run_case` 行 (期待 exit code 付き)
  5. `fixtures/README.md` と `atcoder-test-testing.md` の fixture 一覧に追記
- バグが既存 fixture/テストで本来 assert されているべきだったなら、その期待値を正しい側に直して赤にする。

### 5. 直す (最小の修正)

赤を緑にする最小の変更を入れる。3 で確認した実装範囲に収める — リファクタしたくなったら別コミット/別作業に分ける。周辺の Go スタイルに合わせ、日本語コメントは残す。exit code 規約を必ず守る: **引数/フラグ誤り = 2、実行時失敗 (FAIL/RE/TLE/fetch 失敗) = 1、成功 = 0**。解答ファイル (ユーザの提出コード) を壊す副作用を入れない。

### 6. 検証する (緑を確認)

- `go build ./...` が通る。
- 4 で書いたテストが **緑になる**。
- 触ったパッケージのユニットテスト `go test ./internal/<pkg>/...` (あるいは `go test ./...`) が通る。
- `cmd/atcoder/`・`internal/runner|testexec|runexec|cachepath|ui/` を触ったら `test-tool` スキル (`./fixtures/run.sh`) で全 fixture の exit code を assert する。
- 1 で握った実コマンドの再現手順をもう一度叩き、症状が消えていることを確認する。

### 7. レビュー担当のサブエージェントにレビューを受ける

自分の修正を自分だけで OK としない。検証が緑になったら、**独立したレビュー担当のサブエージェントを立てて差分をレビューさせる**。実装した本人とは別視点で「直し漏れ・別経路への副作用・回帰・規約違反」を突かせ、指摘を潰してからコミットする。

- `git -C <worktree-path> diff main...HEAD` (またはコミット前なら working tree の diff) を対象に、**`Agent` ツールでレビュー担当サブエージェント** (`general-purpose` 等) を 1 体立てる。レビュー観点を明示して渡す:
  - **正しさ** — バグは実際に直っているか。再現条件が消えているか。
  - **影響範囲** — 3 で洗った別経路 (同種の取りこぼし) を本当にカバーできているか。直しが他の経路・公開挙動・exit code 規約を壊していないか。
  - **回帰テスト** — テストはバグを捉えているか (修正を戻すと赤になるか)。範囲は十分か。
  - **規約** — exit code 規約、worktree 内絶対パス、日本語コメント保持、スコープを広げていないか、解答ファイルを壊していないか。
- サブエージェントには「差分を読んで上記観点で問題点と修正提案を返す」ことを指示し、**最終差分だけ手元に残す** (ファイルダンプは渡し返させない)。リポジトリ標準の `code-review` スキルを使ってもよい。
- 指摘が出たら 5〜6 に戻って直す → 再レビュー。**重大な指摘が残ったままコミットしない**。レビューで挙がった非自明な判断はコミット本文か `docs/tools/todo.md` に残す。

### 8. コミットする (Conventional Commits + scope)

`fix(<scope>)` でまとめる。scope はサブコマンド/パッケージ名。例: `fix(test): return exit 1 on TLE instead of 0`、`fix(login): guard against empty CSRF token`、`fix(diff): preserve trailing newline in expected output`。回帰テスト追加と修正は同じコミットにまとめてよい (テストが意図を示す)。原因が非自明だったらコミット本文に「なぜ起きたか/なぜこの直しか」を 1〜2 行残す。メッセージ末尾には環境指定の `Co-Authored-By` trailer を付ける。

### 9. main へマージして worktree を畳む

```sh
git merge --ff-only fix-<slug>
git worktree remove ../atcoder-daily-training.worktrees/fix-<slug>
git branch -d fix-<slug>
```

## 注意

- **テストファースト**。再現テストを先に赤にしてから直す。これをやらないと「直ったつもり」「再発検知なし」になる。
- **実装前に範囲を握る**。直すファイル/関数 (実装範囲) と波及先 (影響範囲) を洗ってから手を動かす。`grep` で**同じ不具合が別経路にもないか**を必ず確認し、非自明・広い範囲なら着手前にユーザへ提示して合意を取る。
- **自分の修正を自分だけで OK としない**。検証が緑になったら、独立したレビュー担当のサブエージェントに差分をレビューさせ、指摘 (直し漏れ・別経路の副作用・回帰・規約違反) を潰してからコミットする。
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
