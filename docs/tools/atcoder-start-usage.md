# `atcoder start` 利用手引

問題に取り掛かるときの **「解答ファイルを用意 → 対話 + watch を同時起動」** を 1 コマンドで済ませる。`atcoder start <contest> --task <task>` で、レイアウトに応じた解答ファイルを (無ければ) 作り、そのまま**上下分割画面**に入る (上 = サンプル自動判定の watch 要約、下 = 対話 chat)。両方を同時に動かし続けられる。

> 要件詳細: [requirements/018-start-command.md](./requirements/018-start-command.md)

## コマンド

```
atcoder start <contest> --task <task> [--until-pass] [--refresh] [-d] [-s] [-j <n>] [--timeout <dur>] [--tolerance <eps>] [--layout <auto|abc|exercise>]
```

> 位置引数 (`<contest>`) とフラグの順序は自由 (`atcoder start --task d abc457` も可)。

| 引数 / フラグ | 説明 |
|---|---|
| `<contest>` | コンテスト ID (例 `abc457`) |
| `--task <task>` | タスク ID または短縮形 (`d` → `<contest>_d`)。必須 |
| `--until-pass` | **サンプルが全通過したら watch を終了** (exit 0)。未指定なら `Ctrl+C` まで継続 |
| `--refresh` | 初回のみサンプルを再取得 |
| `-d` / `-s` / `-j` / `--timeout` / `--tolerance` | `test` と同じ。各 watch 実行にそのまま渡す |
| `--layout <auto\|abc\|exercise>` | 解答ファイル配置。既定は `--layout` > `ATCODER_LAYOUT` > config > auto |

## 動作 — 上下分割画面

1. レイアウトを解決し、解答パス (`exercise/YYYY/MM/DD/<task>.py` または `abc/<num>/<letter>.py` 等) を決める。
2. **解答ファイルを用意**: 親ディレクトリを作成し、ファイルが無ければ**空ファイル**を生成 (既存は温存)。`created:` / `solution: ... (exists)` を 1 行表示。
3. **上下分割画面に入る**。**chat と watch を同時に動かし続ける**:
   - **上ペイン = watch 要約**: 起動時に 1 回サンプルを判定し、以降は**保存検知のたびに自動で再判定**。全体 (`✓ 4/4` / `✗ 2/4`) に続けて**各ケースの verdict** を出す (`01 AC  02 WA  03 TLE  04 AC`。AC=緑・WA/TLE/RE=赤)。どのケースで落ちているかが一目で分かる (diff は出さない)。ケースが多くペイン幅を超えたら末尾を `…` で切り詰める。
   - **下ペイン = 対話 chat**: `test --interactive` と同じ chat。**解答は最初に入力を送った瞬間に起動** (遅延起動)、入力ボックスに 1 行 → `Enter` で送信、子の出力は届き次第表示。auto-restart 付きなので子が終了しても閉じず、**次の入力で再実行**する (入力を読まず即終了する解答でも無限ループにならない)。
4. 編集 → 保存すると、**上ペイン (サンプル再判定) と下ペイン (chat を最新コードで reload) の両方**が新しいコードを反映する (`test --interactive` の watch-reload と同じ)。
5. 終了:
   - `Ctrl+C` または `Ctrl+D` で全体を終了 (exit 0)。
   - `--until-pass` 指定時は、**上ペインのサンプルが全通過した回**で自動終了 (exit 0)。

### キー操作

| キー | 動作 |
|---|---|
| 文字入力 + `Enter` | 下ペインの chat に送信 (子の stdin へ) |
| `↑` / `↓` | chat の入力履歴 |
| `Ctrl+S` | **提出準備** (`test --submit` 相当: 解答をクリップボードへコピー + 提出ページをブラウザで起動)。子は止めず chat に留まり、結果を 1 行表示。**実提出 (POST) はしない** |
| `Ctrl+D` / `Ctrl+C` | 全体を終了 (exit 0) |
| (解答を保存) | 上ペイン (watch) を自動再判定 + 下ペインの chat を最新コードで reload |

> `Ctrl+S` の提出準備は**サンプル全通過を待たない** (`test --submit` のゲートと違い、対話中はバッチ判定が走っていないため)。提出前に確認したいときは上ペインのサンプル結果を見るか、一度抜けて `atcoder test <contest> --task <task> --submit` を使う。

`start` は `new` (ファイル用意) と watch (サンプル自動判定) と chat (対話) を**1 画面に合成**した薄いコマンドで、新しい判定・実行ロジックは持たない。

### コマンドモード — 隣の問題へ移動 (ナビゲーション)

下ペインの chat には `test --interactive` と同じ **vim 風コマンドモード** ([024-interactive-case-builder.md](./requirements/024-interactive-case-builder.md)) がある。`Esc` で `:` 行に入り、1 行打って `Enter` で実行する。`start` の分割画面ではここに**隣の問題へ移動するナビゲーションコマンド**が増える。分割画面に居たまま、一度抜けて `atcoder start ...` を打ち直すことなく次の問題へ移れる。

| コマンド (別名) | 動作 | 例 |
|---|---|---|
| `:task next` (`:task n`) | 問題記号を次へ (letter +1) | `abc457_d` → `abc457_e` |
| `:task prev` (`:task p`) | 問題記号を前へ (letter −1) | `abc457_d` → `abc457_c` |
| `:contest next` (`:contest n`) | コンテストを次へ (contest_num +1、letter 保持) | `abc457_d` → `abc458_d` |
| `:contest prev` (`:contest p`) | コンテストを前へ (contest_num −1、letter 保持) | `abc457_d` → `abc456_d` |
| `:e <spec>` | 任意の問題へジャンプ | `:e f` (現コンテストの `f`) / `:e abc500_d` (コンテストごと) |

- 第 1 トークンは `task` / `contest` の**フルワードのみ** (1 文字略語は無し。`:c` は `:case` と衝突するため)、第 2 トークンは `next`/`n` か `prev`/`p`。第 2 トークン無し・不正トークンは `E492` で利用法を案内し再ターゲットしない。
- **移動の 2 軸**: letter 軸 (`:task next`/`:task prev`) は**同一コンテスト内の次/前の問題**、number 軸 (`:contest next`/`:contest prev`) は**同じ letter の隣コンテスト**。AtCoder の問題 ID (`contest_num` + `letter`) の 2 成分そのままなので、移動の意味が一意に定まる。
- **移動時に着手 + 再ターゲット**: 移動先では start と同じく**着手** (解答ファイルが無ければ空ファイルを作成。`created: <path>` を表示) し、watch ペインのサンプル判定と chat ペインの子プロセスが**新しい問題で作り直される** (再ターゲット)。chat には `(→ abc457_e に移動しました)` の案内行が出る。
- **既存ファイルは温存**: 移動先に解答ファイルが既にあれば**上書きしない** (`solution: <path> (exists)`)。提出コードを壊さない。`--until-pass` 指定時は、移動後の新しい問題に対して全通過判定が掛かる。
- **境界・非対応は 1 行エラーで継続**: letter `a` で `:task prev`、番号が下限で `:contest prev`、番号を持たない contest での `:contest next`/`:contest prev`、複数文字 letter (`ex` 等) での `:task next`/`:task prev`、`:e` の引数が空/不正、などは**再ターゲットせず 1 行エラーを出して継続**する (start は落ちず exit code も変わらない)。
- **Tab 補完**: `:` 行で `Tab` を押すとコマンド名 (`:case`/`:w`/`:set`/`:q`/`:task`/`:contest`/`:e`) と `next|prev`・`verify|noverify` などのサブトークンを補完する。一意なら確定し、複数候補は `:` 行直下に一覧表示する (要件 [030](./requirements/030-command-mode-completion.md))。

移動前後の画面イメージ:

```
┌ watch ─ abc/457/d.py ─────────────────────────────────┐
  ✓ PASS  3/3        judged 12:34:56
└───────────────────────────────────────────────────────┘
┌ interactive (auto-restart) ───────────────────────────┐
  > 5
  10
  :task next       ← Esc → `:task next` を入力
└───────────────────────────────────────────────────────┘

  ↓ :task next 実行後 (abc457_e へ着手・再ターゲット)

┌ watch ─ abc/457/e.py ─────────────────────────────────┐
  …  (未判定 → 初回判定でサンプル取得)
└───────────────────────────────────────────────────────┘
┌ interactive (auto-restart) ───────────────────────────┐
  (→ abc457_e に移動しました)
  > _
└───────────────────────────────────────────────────────┘
```

> ナビゲーションは**分割画面 (start) の chat 限定**。`test --interactive` 単体の chat では `:task`/`:contest` 等は未知コマンド (`E492`) として無視される。既存の `:case`/`:w`/`:set`/`:q` と `Ctrl+C`/`Ctrl+D`/`Ctrl+S` は不変。

## 例

```sh
# 当日の演習として abc457_d に着手 (exercise レイアウト)
atcoder start abc457 --task d
# → created: exercise/2026/06/11/abc457_d.py  のあと watch ループへ

# ABC 本番中、abc/ レイアウトに着手し、通ったら自動で抜ける
atcoder start abc457 --task d --layout abc --until-pass
# → created: abc/457/d.py  …編集 → 保存 → 全 PASS で自動終了

# 既にファイルがある問題に watch だけ掛け直す
atcoder start abc457 --task d
# → solution: exercise/.../abc457_d.py (exists)  のあと watch ループへ
```

## exit code

| code | 意味 |
|---|---|
| `0` | `Ctrl+C` で終了、または `--until-pass` で全通過終了 |
| `1` | ディレクトリ作成 / ファイル生成の失敗 |
| `2` | 引数誤り (`--task` 欠落・不正レイアウト)、または **非 TTY** (watch は端末必須)。※非 TTY でも解答ファイルの作成は先に行われる |

## 注意

- **端末 (TTY) が必要**。パイプ/リダイレクト先では `exit 2` で拒否される (分割画面 TUI 前提)。
- 既存の解答ファイルは**上書きしない** (提出コードを壊さない)。`--refresh` はキャッシュのみ対象。
- 生成されるのは現状**空ファイル**。テンプレート流し込みは将来 (ロードマップ H) で差し替え予定。

## 関連

- 利用手引: [atcoder-test-usage.md](./atcoder-test-usage.md) (watch モードの詳細)
- 要件: [018-start-command.md](./requirements/018-start-command.md) / [019-start-key-actions.md](./requirements/019-start-key-actions.md) / [023-start-split-screen.md](./requirements/023-start-split-screen.md) / [027-start-problem-navigation.md](./requirements/027-start-problem-navigation.md) (コマンドモードのナビゲーション) / [004-exercise-test-watch.md](./requirements/004-exercise-test-watch.md)
