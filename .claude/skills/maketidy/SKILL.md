---
name: maketidy
description: 実装 (cmd/atcoder + internal/) とドキュメント (docs/・skills・CLAUDE.md) の整合性、およびドキュメント内部の自己整合 (採番・索引・相互リンク) を点検し、見つかったズレを「ドキュメント側を直す」整頓スキル。usage 構文行とフラグ表の実装との一致、リンク切れ (実体のない doc 参照)、ロードマップの DONE 状態、requirements 相互リンク、要件番号やロードマップ節レターの重複、ADR 索引の網羅、陳腐化した注記を系統的にチェックする。実装の挙動は変えない。新しい利用ドキュメントの書き起こしや新フラグ追加が要るギャップは feature へ申し送る。
---

# maketidy

コードは進むがドキュメントは置いていかれる。フラグを足したのに usage 表に書き忘れる、doc を再編してリンクが宙に浮く、ロードマップの DONE マークが実装に追いつかない — こうした **実装 ⇄ ドキュメントのドリフト** を系統的に洗い出し、**ドキュメント側を実装の現状に合わせて**直すのが maketidy。

整頓 (tidy) であって変更ではない。**実装の挙動には触れない**。ズレを埋めるのに新しい挙動や新規ドキュメントの書き起こしが要ると分かったら、それは maketidy ではなく `feature` の仕事 — 申し送る。

## いつ使うか

- 「実装とドキュメントの整合性を確認して」「docs が古くなっていないか点検して」といった整頓依頼。
- 機能追加やリネームの後、波及した docs/skills/ロードマップを揃え直したいとき。
- リリース前・節目に、CLI の表面 (usage・フラグ) と手引きの突き合わせをしたいとき。
- **並行 worktree が増えた後の棚卸し**: 要件番号の重複・ロードマップ節レターの重複・ADR 索引の漏れ・陳腐化した注記をまとめて掃除したいとき (下の **軸 B**)。

## いつ使わないか (→ 別の道)

- 新サブコマンド・新フラグ・新挙動を **足す** → `feature` (仕様を伴う)。
- 未作成の利用ドキュメントを **新規に書き起こす** → `feature` の手順 5 (利用ドキュメント整備)。maketidy は既存 docs の追従・修正まで。
- 実装側のバグ直し → `smallwork` か `feature` (規模で判断)。
- 純粋な練習解答の追加・修正 → `smallwork`。

## 点検チェックリスト

点検は 2 軸ある。**A. 実装 ⇄ ドキュメント** (実装を「正」にドキュメントを合わせる) と、**B. ドキュメント内部の自己整合** (採番・索引・相互リンクが doc 群の中で破綻していないか)。並行 worktree が増えるほど B のドリフト (要件番号の衝突・節レターの重複・索引漏れ) が起きやすい。どちらも**実装挙動は変えない**。

### A. 実装 ⇄ ドキュメント (実装が正)

| # | 点検対象 | 突き合わせ方 |
|---|---|---|
| 1 | **usage 構文行** | `cmd/atcoder/main.go` の `usage()` ⇄ 各 `docs/tools/atcoder-<cmd>-usage.md` の構文行。フラグの過不足・表記揺れ (`-c` vs `--case` 等) を見る |
| 2 | **フラグ表** | 各サブコマンドの `flags.*` / `*Var` 定義 ⇄ usage doc のフラグ表。**実装にあるのに表に無いフラグ**、実装から消えたのに残る行を洗う |
| 3 | **リンク切れ** | docs 内の相互リンク・コードスパンのパス参照先が実在するか。再編で移動した先 (例: `requirements/00N-*.md`) に張り直す |
| 4 | **ロードマップ状態** | `docs/tools/{abc-todo,todo}.md` の `✅ DONE (<commit>)` と実装の有無が一致するか。実装済みなのに TODO のまま等を拾う |
| 5 | **requirements 相互リンク** | `docs/tools/requirements/00N-*.md` 間・living docs からの参照が現行のファイル名/パスに合っているか |
| 6 | **skills / CLAUDE.md** | コマンド名・ディレクトリ規約・doc パスの記述が実装と一致するか (リネーム後に特に効く) |

### B. ドキュメント内部の自己整合 (採番・索引・相互リンク)

ここは「実装→doc」ではなく **doc 群どうしの整合**。並行作業 (worktree) は同じ「次番号/次レター」を取り合うため、衝突や索引漏れが定常的に溜まる。

| # | 点検対象 | 突き合わせ方・直し方 |
|---|---|---|
| 7 | **要件番号の重複** | `docs/tools/requirements/` の `NNN-` 番号が一意か。重複分は**次の空き番号にリネーム + 参照を全て追従** (todo・他要件の相互リンク・本文)。新規採番は **`git ls-tree main`** で確認する (ローカル `ls` は in-flight ブランチの番号を見落とすので衝突する)。本文には番号を書かずファイル名にだけ持たせると追従が楽 |
| 8 | **ロードマップの節識別子** | `todo.md` / `abc-todo.md` の `## X.` レターが一意か・枯渇していないか。重複は振り直し、`A`–`Z` を使い切ったら `AA`/`AB`… へ継続する |
| 9 | **ADR 索引の網羅** | `docs/tools/decisions/README.md` の一覧 ⇄ 実在する `NNNN-*.md`。掲載漏れ (過去に 0005/0006 が欠落) を埋める |
| 10 | **陳腐化した注記** | 「未実装」「設計済み (実装待ち)」等が、実装済みになった機能を指したまま残っていないか (but-now-false な状態注記・相互参照) |

便利な探索コマンド:

```sh
# --- A: 実装 ⇄ ドキュメント ---
sed -n '/func usage/,/^}/p' cmd/atcoder/main.go              # usage() の現物
grep -rn 'flags\.\(String\|Bool\|Int\|Float64\|Duration\)\|.*Var(' cmd/atcoder/*.go  # 各サブコマンドの実フラグ
grep -rn 'exercise-[a-z-]*-requirements\.md' docs            # 実体のない doc 参照 (旧名など)

# --- B: ドキュメント内部の自己整合 ---
# B-7 要件番号の重複 / 次の空き番号 (採番は in-flight も拾う main 基準で)
ls docs/tools/requirements/ | sed -E 's/^([0-9]+).*/\1/' | sort | uniq -d
git ls-tree --name-only main docs/tools/requirements/ | sed -E 's#.*/##' | sort | tail -3
# B-8 ロードマップ節レターの重複
grep -hoE '^## [A-Z]+\.' docs/tools/todo.md docs/tools/abc-todo.md | sort | uniq -d
# B-9 ADR 索引の漏れ (実在にあって README に無い番号)
comm -23 <(ls docs/tools/decisions/ | grep -oE '^[0-9]{4}' | sort -u) \
         <(grep -oE '[0-9]{4}-[a-z]' docs/tools/decisions/README.md | grep -oE '^[0-9]{4}' | sort -u)
# B-10 陳腐化注記の候補 (目視で実装済みを指すものを選別)
grep -rn '未実装\|実装待ち\|設計済み' docs/tools/todo.md docs/tools/abc-todo.md docs/tools/requirements/
```

## ワークフロー (smallwork に乗せる)

整頓は基本 docs 修正なので、`smallwork` の最小手順で回す。

1. **worktree を切る** (CLAUDE.md 必須)。ブランチ名は `docs-sync-usage`・`tidy-broken-links` など。
2. **点検する** — 上のチェックリストを実装起点で回し、ズレを洗い出す。直す前に「全件のズレ」を把握してからまとめて直すと取りこぼしが減る。
3. **ドキュメント側を直す** — 実装の現状に合わせる。構文行・フラグ表は `usage()` と `flags.*` の文言に寄せる。リンクは実在する現行パスへ。**実装は変えない。**
4. **検証する** — docs のみなのでビルド不要。代わりに:
   - リンクの**張り直し先が実在**することを確認 (`[ -f <path> ]`)。
   - 直した種類のズレが**残っていない**ことを再 grep で確認 (例: dangling パターンが 0 件)。
   - **軸 B を直したら、上の B-7〜B-9 コマンドを再実行して `uniq -d` / `comm` の出力が空になる**ことを確認する (番号・レターの重複ゼロ、ADR 索引の漏れゼロ)。
   - 要件番号をリネームしたら、`grep -rn '<旧番号>-<name>' docs` で**古い参照が残っていない**ことを確認する。
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
