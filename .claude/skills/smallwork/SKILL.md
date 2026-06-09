---
name: smallwork
description: 簡単な修正 (typo・コメント・小さなバグ直し・1〜数ファイルの軽微な変更・ドキュメントの細かい修正・練習問題の解答追加など) を最小手順で進める軽量ワークフロー。CLAUDE.md どおり worktree は切るが、要件定義 (docs/tools/requirements/) や fixture・利用ドキュメント一式といった重い手順は省き、worktree → 編集 → 最小限の検証 → Conventional Commits → main へ ff-merge、だけで回す。新サブコマンド/フラグ追加など仕様を伴う変更は使わず feature を使う。
---

# smallwork

軽い変更を素早く片付けるための最小ワークフロー。`feature` のフルセレモニー (要件定義 → ロードマップ → 実装 → fixture → 利用ドキュメント → コミット → マージ) は、typo 直し 1 行のような作業には重すぎる。smallwork はそれを「worktree → 編集 → 最小検証 → コミット → マージ」に削ぎ落とす。**worktree を切る点は CLAUDE.md どおり守る** (緩めるのは worktree 以降の重い手順だけ)。

## いつ使うか (smallwork の目安)

- typo・誤字・コメント・文言の修正。
- 1〜数ファイルに収まる小さなバグ直し・微調整 (仕様変更を伴わない)。
- `docs/` の軽微な更新 (リンク修正・追記・表現直し)。
- 練習問題の解答追加・修正 (`exercise/`, `abc/`, `arc/`, `awc/`, `adt/`, `dp/`, `tessoku-book/`, `spoj/` 等)。
- 既存挙動を変えない局所的なリファクタリング。

## いつ使わないか (→ 別の道)

- `exercise` CLI に**新しい挙動**を足す (新サブコマンド・新フラグ・新モード・新言語 Runner)。仕様を伴うので **`feature`** を使う。
- 影響範囲が読みきれない / 複数パッケージにまたがる / 設計判断が要る変更。重いと感じたら smallwork をやめて `feature` に切り替える。
- 判断に迷う中間サイズは、安全側に倒して `feature` (要件を文章化する) 側へ。

## ワークフロー

### 1. worktree を切る (CLAUDE.md 必須・省略しない)

タスクを表すブランチ名で main から切る。

```sh
git worktree add ../atcoder-daily-training.worktrees/<branch> -b <branch>
```

ブランチ名は内容を表す短い kebab (`fix-typo-run-usage`, `fix-tle-abc457-e`, `docs-fix-link`)。worktree 内のファイルは絶対パスで Write/Edit する (`cd` は permission prompt を誘発しやすい)。コミットは `git -C <worktree-path> ...`。

### 2. 編集する

周辺コードのスタイルに合わせる。練習解答なら terse な競プロ流儀 (短い変数名・`input()`/`print()`・最小の抽象)、ツールコードなら普通の Go。日本語コメントは残す。

### 3. 最小限だけ検証する

触ったものに応じて、必要な分だけ:

- **ツールコード** (`cmd/exercise/`, `internal/runner|testexec|runexec|cachepath|ui/`) を触った → `test-tool` スキル (`./fixtures/run.sh`) を回す。スモークが緑なら十分。Go の変更は `go build ./...` も通す。
- **練習解答** → サンプルがあれば実行して照合: `python <path>/main.py < <path>/input-00.txt` を `output-00.txt` と比べる。フラット配置 (`abc/`, `exercise/` 等) でサンプルが無い問題は、自分で 1 ケース流して目視。
- **`docs/` だけ** → 検証不要 (リンク先の存在だけ確認)。

新しい fixture を足したり利用ドキュメントを書き直したりは smallwork の範囲外 — それが要るならその時点で `feature` 案件。

### 4. コミットする

Conventional Commits + scope で 1 コミットにまとめる。例: `fix(run): correct typo in usage string`、`docs(tools): fix broken link`、`solve(abc457): add e.py`。メッセージ末尾に環境指定の `Co-Authored-By` trailer を付ける。

### 5. main へ ff-merge して worktree を畳む

```sh
git merge --ff-only <branch>
git worktree remove ../atcoder-daily-training.worktrees/<branch>
git branch -d <branch>
```

## 注意

- worktree は省かない。緩めるのは「要件定義・fixture・利用ドキュメント・ロードマップ」といった重い付帯作業だけ。
- 解答ファイル (ユーザの提出コード) を壊さない。
- 着手後に「思ったより大きい / 仕様判断が要る」と分かったら、その worktree のまま `feature` の手順に格上げする。smallwork で押し切らない。

## 関連

- どちらの流儀か迷うとき: `triage` スキル (smallwork / feature を振り分ける入口)
- 重い機能追加: `feature` スキル
- ツールのスモークテスト: `test-tool` スキル
- ルート規約: `CLAUDE.md` (worktree 必須・ディレクトリ規約・解答スタイル)
