---
name: maketidy
description: 実装 (cmd/atcoder + internal/) とドキュメント (docs/・skills・CLAUDE.md) の整合性を点検し、見つかったズレを「ドキュメント側を実装に合わせて直す」整頓スキル。usage 構文行とフラグ表の実装との一致、リンク切れ (実体のない doc 参照)、ロードマップの DONE 状態、requirements 相互リンクを系統的にチェックする。実装の挙動は変えない。新しい利用ドキュメントの書き起こしや新フラグ追加が要るギャップは feature へ申し送る。
---

# maketidy

コードは進むがドキュメントは置いていかれる。フラグを足したのに usage 表に書き忘れる、doc を再編してリンクが宙に浮く、ロードマップの DONE マークが実装に追いつかない — こうした **実装 ⇄ ドキュメントのドリフト** を系統的に洗い出し、**ドキュメント側を実装の現状に合わせて**直すのが maketidy。

整頓 (tidy) であって変更ではない。**実装の挙動には触れない**。ズレを埋めるのに新しい挙動や新規ドキュメントの書き起こしが要ると分かったら、それは maketidy ではなく `feature` の仕事 — 申し送る。

## いつ使うか

- 「実装とドキュメントの整合性を確認して」「docs が古くなっていないか点検して」といった整頓依頼。
- 機能追加やリネームの後、波及した docs/skills/ロードマップを揃え直したいとき。
- リリース前・節目に、CLI の表面 (usage・フラグ) と手引きの突き合わせをしたいとき。

## いつ使わないか (→ 別の道)

- 新サブコマンド・新フラグ・新挙動を **足す** → `feature` (仕様を伴う)。
- 未作成の利用ドキュメントを **新規に書き起こす** → `feature` の手順 5 (利用ドキュメント整備)。maketidy は既存 docs の追従・修正まで。
- 実装側のバグ直し → `smallwork` か `feature` (規模で判断)。
- 純粋な練習解答の追加・修正 → `smallwork`。

## 点検チェックリスト

実装を「正」とし、ドキュメントがそれに一致しているかを上から確認する。

| # | 点検対象 | 突き合わせ方 |
|---|---|---|
| 1 | **usage 構文行** | `cmd/atcoder/main.go` の `usage()` ⇄ 各 `docs/tools/atcoder-<cmd>-usage.md` の構文行。フラグの過不足・表記揺れ (`-c` vs `--case` 等) を見る |
| 2 | **フラグ表** | 各サブコマンドの `flags.*` / `*Var` 定義 ⇄ usage doc のフラグ表。**実装にあるのに表に無いフラグ**、実装から消えたのに残る行を洗う |
| 3 | **リンク切れ** | docs 内の相互リンク・コードスパンのパス参照先が実在するか。再編で移動した先 (例: `requirements/00N-*.md`) に張り直す |
| 4 | **ロードマップ状態** | `docs/tools/{abc-todo,todo}.md` の `✅ DONE (<commit>)` と実装の有無が一致するか。実装済みなのに TODO のまま等を拾う |
| 5 | **requirements 相互リンク** | `docs/tools/requirements/00N-*.md` 間・living docs からの参照が現行のファイル名/パスに合っているか |
| 6 | **skills / CLAUDE.md** | コマンド名・ディレクトリ規約・doc パスの記述が実装と一致するか (リネーム後に特に効く) |

便利な探索コマンド:

```sh
# usage() の現物
sed -n '/func usage/,/^}/p' cmd/atcoder/main.go
# 各サブコマンドの実フラグ
grep -rn 'flags\.\(String\|Bool\|Int\|Float64\|Duration\)\|.*Var(' cmd/atcoder/*.go
# 実体のない doc 参照 (リンク切れ候補)
grep -rn 'exercise-[a-z-]*-requirements\.md' docs   # 再編前の旧名など
```

## ワークフロー (smallwork に乗せる)

整頓は基本 docs 修正なので、`smallwork` の最小手順で回す。

1. **worktree を切る** (CLAUDE.md 必須)。ブランチ名は `docs-sync-usage`・`tidy-broken-links` など。
2. **点検する** — 上のチェックリストを実装起点で回し、ズレを洗い出す。直す前に「全件のズレ」を把握してからまとめて直すと取りこぼしが減る。
3. **ドキュメント側を直す** — 実装の現状に合わせる。構文行・フラグ表は `usage()` と `flags.*` の文言に寄せる。リンクは実在する現行パスへ。**実装は変えない。**
4. **検証する** — docs のみなのでビルド不要。代わりに:
   - リンクの**張り直し先が実在**することを確認 (`[ -f <path> ]`)。
   - 直した種類のズレが**残っていない**ことを再 grep で確認 (例: dangling パターンが 0 件)。
   - ツールコードにも触れた場合のみ `test-tool` (`./fixtures/run.sh`) と `go build ./...`。
5. **コミット** — `docs(tools): sync usage docs with implementation` のように Conventional Commits。末尾に環境指定の `Co-Authored-By` trailer。
6. **main へ ff-merge** して worktree を畳む。`--ff-only` が拒否されたら (main が進んでいたら) worktree 内で `git rebase main` してから再度 ff-merge。

## ギャップの申し送り

点検中に「ドキュメント追従では埋まらないギャップ」を見つけたら、勝手に埋めずに**明示して残す**:

- 実装済みなのに**利用ドキュメントが丸ごと無い** (例: あるサブコマンドの usage doc 未作成) → `feature` 案件として申し送る (新規 doc 書き起こしは maketidy 外)。
- ドキュメントが正しく実装側がバグ/未実装 → 整頓では直さない。`smallwork`/`feature` で実装を直す話として分ける。

silent に埋めると「整頓した」が実態と乖離する。残ったギャップは利用者に伝える。

## 注意

- **方向を間違えない**: maketidy は「実装 → ドキュメント」。ドキュメントに合わせて実装を変えるのは整頓ではない。
- 解答ファイル (ユーザの提出コード) には触れない。
- worktree は省かない (緩めるのは要件定義・fixture など重い付帯作業だけ)。

## 関連

- 軽量ワークフローの土台: `smallwork` スキル
- 新挙動・新規ドキュメント: `feature` スキル
- どの流儀か迷うとき: `triage` スキル
- ルート規約: `CLAUDE.md`
