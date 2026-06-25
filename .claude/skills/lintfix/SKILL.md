---
name: lintfix
description: atcoder ツールの Go コード (cmd/atcoder + internal/) のリント/フォーマット崩れを gofmt と go vet で整える軽量メンテナンススキル。gofmt の未整形 (整列・コメント間隔など) を gofmt -w で自動修正し、go vet の指摘を直し、go build / go test / fixtures で壊れていないか確認してから worktree でコミットして main へ ff-merge する。Python の練習解答 (exercise/・abc/・arc/・awc/・adt/・dp/・tessoku-book/・spoj/ 等) は terse な競プロスタイルを意図的に保つため触らない (flake8 は報告のみ)。挙動は変えない (純粋な整形)。新挙動を足すなら feature、バグ直しは bugfix。
---

# lintfix

`atcoder` ツールの **Go コード**のフォーマット/リント崩れを機械的に整えるスキル。`gofmt` の整形ズレ (struct タグ整列・var ブロック整列・doc コメントの間隔など) や `go vet` の指摘が溜まると、無関係な差分が後続の diff に混ざってレビューを濁す。lintfix はそれを「worktree → `gofmt -w` で自動整形 → `go vet` を直す → build/test/fixtures で非破壊確認 → コミット → ff-merge」で片付ける。

挙動は**一切変えない** (純粋な整形・リント修正)。仕様変更・新挙動は対象外。

## いつ使うか

- `gofmt -l cmd/ internal/` が未整形ファイルを挙げる (整列・コメント間隔などが崩れている)。
- `go vet ./...` が指摘を出す (printf 不一致・到達不能・shadow など、挙動を変えずに直せるもの)。
- リファクタや機能追加の前後に Go ツリーの整形債務をまとめて返したい。

## いつ使わないか

- **Python の練習解答を整形したい** → やらない。`exercise/`・`abc/`・`arc/`・`awc/`・`adt/`・`dp/`・`tessoku-book/`・`spoj/`・`nikkei2019-final/`・`2025/` 等の解答は **terse な競プロスタイルを意図的に保つ** (CLAUDE.md「Don't restructure for clean code」)。flake8 は報告のみで auto-fix もしないので、ここは触らない。
- 挙動を変える修正が要る → バグなら `bugfix`、新挙動なら `feature`。
- vet の指摘が「直すと挙動が変わる」ものだった → それは整形ではないので `bugfix` へ申し送る。

## 対象範囲

| 対象 | ツール | 動作 |
|---|---|---|
| Go ツーリング (`cmd/atcoder/` + `internal/`) | `gofmt -w` | 未整形を自動整形 (整列・コメント間隔・import 並びなど) |
| 同上 | `go vet ./...` | 指摘を**挙動を変えずに**直す。直すと挙動が変わるものは対象外 (申し送り) |
| Python 練習解答 | (なし) | **触らない**。flake8 は走らせても報告のみで、解答は整形しない |

`gofmt -w` は決定的で安全 (構文を保ったまま整形するだけ)。go vet の修正だけは内容を読んで判断する。

## 手順

### 0. worktree を切る (CLAUDE.md 必須)

```sh
git worktree add ../atcoder-daily-training.worktrees/chore-lintfix -b chore-lintfix
```

worktree 内のファイルは絶対パスで編集し、コミットは `git -C <worktree-path> ...`。

### 1. 現状を把握する

```sh
gofmt -l cmd/ internal/      # 未整形ファイルの一覧
gofmt -d cmd/ internal/      # 何を直すか差分で確認 (安全性の確認)
go vet ./...                 # vet の指摘
```

差分を一度目で見て、整列・コメント間隔などの純粋な整形だけか確認する (想定外の大きな書き換えが無いか)。

### 2. 自動整形を適用する

```sh
gofmt -w cmd/ internal/
```

go vet の指摘があれば、**挙動を変えない範囲で**該当箇所を直す。挙動が変わる修正に踏み込みそうなら手を止めて `bugfix` に切り替える。

### 3. 非破壊を確認する

```sh
gofmt -l cmd/ internal/      # 空になっていること
go build ./...
go vet ./...
go test ./...
./fixtures/run.sh            # cmd/atcoder・internal/runner|testexec|runexec|ui を整形したら
```

整形だけなので全テストが緑のまま通るはず。1 件でも落ちたら整形以外の混入を疑う。

### 4. コミットして main へマージ

scope は `chore`、または整形したパッケージ。例:

```sh
git commit -m "style(ui): gofmt -w で整形ズレを解消"
git commit -m "chore: go vet 指摘を解消"
```

Conventional Commits + 環境指定の `Co-Authored-By` trailer。整形 (`style`/`chore`) と vet 修正は意味の塊で分けてよい。

```sh
git merge --ff-only chore-lintfix
git worktree remove ../atcoder-daily-training.worktrees/chore-lintfix
git branch -d chore-lintfix
```

## 注意

- **解答ファイルを壊さない**。`gofmt -w` の対象は Go (`cmd/` + `internal/`) のみ。Python 解答には触れない。
- **挙動を変えない**。lintfix は整形とリント修正だけ。判定・出力・exit code が変わる変更を混ぜない (混ざったら整形コミットを分け、挙動変更は別スキルへ)。
- **gofmt のバージョン**。この repo は Go 1.25。手元の `gofmt` がツールチェインと一致していること (新しい gofmt ルールで整形差分が出る場合がある)。
- worktree は必ず切る (CLAUDE.md)。整形でも例外にしない。

## 関連

- 軽量ワークフロー全般: `smallwork`
- スモークテスト: `test-tool` (`./fixtures/run.sh`)
- バグ修正: `bugfix` / 新機能: `feature`
- ルート規約: `CLAUDE.md` (worktree 必須・Python 解答スタイル・lint コマンド)
