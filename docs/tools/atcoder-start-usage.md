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
   - **上ペイン = watch 要約**: 起動時に 1 回サンプルを判定し、以降は**保存検知のたびに自動で再判定**。全体 (`✓ 4/4` / `✗ 2/4`) に続けて**各ケースの verdict** を出す (`01 AC  02 WA  03 TLE  04 AC`。AC=緑・WA/TLE/RE=赤)。どのケースで落ちているかが一目で分かる (diff は出さない)。ケースが多くペイン幅を超えたら末尾を `…` で切り詰める。Debug (`-d` / chat の `:debug`) が on のときは判定が `[DEBUG]` 行を除外し、タイトルに `[debug]` バッジが付く (下記「コマンドモード — `:debug` は watch ペインにも反映」)。
   - **下ペイン = 対話 chat**: `test --interactive` と同じ chat。**解答は最初に入力を送った瞬間に起動** (遅延起動)、入力ボックスに 1 行 → `Enter` で送信、子の出力は届き次第表示。**複数行を貼り付ける**と各改行を `Enter` 扱いで順に送信する (要件 [035](./requirements/035-chat-multiline-paste.md))。auto-restart 付きなので子が終了しても閉じず、**次の入力で再実行**する (入力を読まず即終了する解答でも無限ループにならない)。
4. 編集 → 保存すると、**上ペイン (サンプル再判定) と下ペイン (chat を最新コードで reload) の両方**が新しいコードを反映する (`test --interactive` の watch-reload と同じ)。
5. 終了:
   - `Ctrl+D` を **2 回連続**で押すと全体を終了 (exit 0)。1 回目はプログラムのリセット (子を再起動)、2 回目で終了。`Ctrl+C` は終了ではなくプログラムの中断・再起動 (chat に留まる)。
   - `--until-pass` 指定時は、**上ペインのサンプルが全通過した回**で自動終了 (exit 0)。

### キー操作

| キー | 動作 |
|---|---|
| 文字入力 + `Enter` | 下ペインの chat に送信 (子の stdin へ)。**複数行ペースト**は各行を順に送信 |
| `↑` / `↓` | chat の入力履歴 |
| `PageUp` / `PageDown` (または `Ctrl+B` / `Ctrl+F`) | 下ペイン chat の scrollback を 1 ページ上下にスクロール (要件 [040](./requirements/040-insert-mode-scrollback-paging.md))。上にスクロール中は出力が来ても引き戻されない。`PageDown` で最下部に戻る or `Enter` 送信で追従再開 |
| `Ctrl+S` | **提出準備** (`test --submit` 相当: 解答をクリップボードへコピー + 提出ページをブラウザで起動)。子は止めず chat に留まり、結果を 1 行表示。**実提出 (POST) はしない** |
| `Ctrl+G` | **詳細表示**: 上ペイン (watch) を下方向に拡張し、サンプル判定の**失敗ケース (WA/TLE/RE) の diff** (期待 vs 実際、RE は stderr) を表示 (chat ペインは縮んで下に残る)。もう一度 `Ctrl+G` か `Esc` で戻る。`PageUp`/`PageDown`/`↑`/`↓` でスクロール。AC は省略 ([要件 036](./requirements/036-start-watch-detail-view.md)) |
| `Ctrl+E` | **解答ファイルをエディタで開く** ([要件 038](./requirements/038-start-edit-in-editor.md))。nvim の `:terminal` 内 (`$NVIM` 在り) なら**親 nvim に送る**: 既定は現在のウィンドウで開いてタブを再利用 (`--remote`)、`editor_nvim_remote = tab` なら問題ごとに新規タブ (`--remote-tab`)。いずれも新しい nvim を起動せずネスト回避 ([要件 041](./requirements/041-edit-nvim-remote-reuse.md))。nvim 外なら `editor` (config) / `$EDITOR` / `nvim` を一時的に前面起動し、終了で分割画面に戻る。ファイルは開くだけ |
| `Ctrl+D` (2 回連続) | 全体を終了 (exit 0)。1 回目はプログラムのリセット (子を再起動)、間に他キーで連続カウントは戻る |
| `Ctrl+C` | プログラムの中断・再起動 (子を kill して再実行・chat に留まる) |
| (解答を保存) | 上ペイン (watch) を自動再判定 + 下ペインの chat を最新コードで reload |

> `Ctrl+S` の提出準備は**サンプル全通過を待たない** (`test --submit` のゲートと違い、対話中はバッチ判定が走っていないため)。提出前に確認したいときは上ペインのサンプル結果を見るか、一度抜けて `atcoder test <contest> --task <task> --submit` を使う。

`start` は `new` (ファイル用意) と watch (サンプル自動判定) と chat (対話) を**1 画面に合成**した薄いコマンドで、新しい判定・実行ロジックは持たない。

### コマンドモード — 隣の問題へ移動 (ナビゲーション)

下ペインの chat には `test --interactive` と同じ **vim 風コマンドモード** ([024-interactive-case-builder.md](./requirements/024-interactive-case-builder.md)) がある。`Esc` で `:` 行に入り、1 行打って `Enter` で実行する。`start` の分割画面ではここに**隣の問題へ移動するナビゲーションコマンド**が増える。分割画面に居たまま、一度抜けて `atcoder start ...` を打ち直すことなく次の問題へ移れる。

| コマンド (別名) | 動作 | 例 |
|---|---|---|
| `:task next` (`:task n`) | 問題記号を次へ (letter +1) | `abc457_d` → `abc457_e` |
| `:task prev` (`:task p`) | 問題記号を前へ (letter −1) | `abc457_d` → `abc457_c` |
| `:task <letter>` | 問題記号を**直指定** (現コンテスト) | `:task f` → `abc457_f` |
| `:contest next` (`:contest n`) | コンテストを次へ (contest_num +1、letter 保持) | `abc457_d` → `abc458_d` |
| `:contest prev` (`:contest p`) | コンテストを前へ (contest_num −1、letter 保持) | `abc457_d` → `abc456_d` |
| `:contest <num>` | コンテスト番号を**直指定** (現シリーズ・桁数保持、letter 保持) | `:contest 123` → `abc123_d` |
| `:contest <id>` | コンテストを**直指定** (シリーズごと、letter 保持) | `:contest arc100` → `arc100_d` |
| `:e <spec>` | 任意の問題へジャンプ | `:e f` (現コンテストの `f`) / `:e abc500_d` (コンテストごと) |

- 第 1 トークンは `task` / `contest` の**フルワードのみ** (1 文字略語は無し。`:c` は `:case` と衝突するため)。第 2 トークンが `next`/`n`・`prev`/`p` なら相対移動、それ以外の非空トークンは**直指定** (`:task <letter>` / `:contest <num|id>`)。第 2 トークン無しは `E492` で利用法を案内し再ターゲットしない。
- **移動の 2 軸**: letter 軸 (`:task`) は**同一コンテスト内の問題**、number 軸 (`:contest`) は**同じ letter の別コンテスト**。AtCoder の問題 ID (`contest_num` + `letter`) の 2 成分そのままなので、`next`/`prev` の相対移動でも直指定でも意味が一意に定まる。`:contest <num>` は現在のシリーズ・桁数を保つ (`abc457` から `:contest 5` → `abc005`)。`:e` は種別を問わない自由形式 (`:task`=記号・`:contest`=コンテストの直指定とは役割を分ける)。
- **移動時に着手 + 再ターゲット**: 移動先では start と同じく**着手** (解答ファイルが無ければ空ファイルを作成。`created: <path>` を表示) し、watch ペインのサンプル判定と chat ペインの子プロセスが**新しい問題で作り直される** (再ターゲット)。chat には `(→ abc457_e に移動しました)` の案内行が出る。
- **既存ファイルは温存**: 移動先に解答ファイルが既にあれば**上書きしない** (`solution: <path> (exists)`)。提出コードを壊さない。`--until-pass` 指定時は、移動後の新しい問題に対して全通過判定が掛かる。
- **境界・非対応は 1 行エラーで継続**: letter `a` で `:task prev`、番号が下限で `:contest prev`、番号を持たない contest での `:contest next`/`:contest prev`、複数文字 letter (`ex` 等) での `:task next`/`:task prev`、直指定の不正値 (`:task <非英字>`・`:contest 0` や形不正)、`:e` の引数が空/不正、などは**再ターゲットせず 1 行エラーを出して継続**する (start は落ちず exit code も変わらない)。
- **Tab 補完**: `:` 行で `Tab` を押すとコマンド名 (`:case`/`:test`/`:w`/`:set`/`:q`/`:debug`/`:replay`/`:cheat`/`:task`/`:contest`/`:e`) と `next|prev`・`verify|noverify` などのサブトークンを補完する。一意なら確定し、複数候補は `:` 行直下に一覧表示する (要件 [031](./requirements/031-command-mode-completion.md))。
- **入力リプレイ (`:replay`)**: `:replay` は**直近に流した入力**を子をリスタートして再送する (コード修正後の流し直し)。優先順位は **現セッションの手入力 → 直近の `:test` ケース (再生時は `.out` で再検証) → 直前に完了したセッションの手入力 → 前回 chat 起動の手入力**で、子のリスタートをまたいだ全入力の累積ではなく直近の 1 単位だけ。`:test n` でケースを流したあと手入力していなければそのケースを再入力し、手入力していれば手入力が優先される (要件 [048](./requirements/048-chat-replay-test-case.md))。下ペイン chat の手入力は問題ごとに永続化され、`:task`/`:contest`/`:e` で移動した先でもその問題の前回起動分が最後のフォールバックになる (要件 [039](./requirements/039-chat-replay-previous-session.md))。記録停止は `ATCODER_NO_CHAT_HISTORY=1`。
- **サンプル実行 (`:test [case]`)**: `:test 01` (公式) / `:test x01` (追加) で、そのキャッシュ済みサンプルの `.in` を子をリスタートして順送し `.out` でライブ検証する。`:test` (引数なし) は利用可能なケース ID の一覧を表示する。`:replay` (手入力の再送) と違い**保存済みサンプル**を起点にする (要件 [045](./requirements/045-chat-run-sample-case.md))。fetch はせずキャッシュ済みのものだけ読む。

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

> ナビゲーションは**分割画面 (start) の chat 限定**。`test --interactive` 単体の chat では `:task`/`:contest` 等は未知コマンド (`E492`) として無視される。既存の `:case`/`:test`/`:w`/`:set`/`:q` と `Ctrl+C`/`Ctrl+D`/`Ctrl+S` は不変 (`:test` は両方の chat で使える)。scrollback のページスクロールは command モード ([033](./requirements/033-command-mode-scrollback-paging.md)) だけでなく insert モードでも `PageUp`/`PageDown`/`Ctrl+B`/`Ctrl+F` で行える (要件 [040](./requirements/040-insert-mode-scrollback-paging.md))。

### コマンドモード — `:debug` は watch ペインにも反映

下ペインの chat で `:debug` (別名 `:set debug` / `:set nodebug`) で Debug を切り替えると ([030-chat-debug-cheat-commands.md](./requirements/030-chat-debug-cheat-commands.md))、`start` の分割画面では**上ペイン (watch) の再判定にも即反映**される (要件 [034](./requirements/034-start-debug-watch-sync.md))。

- Debug は単なる表示切替ではなく、**子に `DEBUG=1` を渡し、`stdout` の `[DEBUG]` 接頭辞行を比較対象から除外**する (`-d` フラグ相当)。watch ペインの per-case verdict はこの除外の有無で変わる。
- そのため、`-d` を付けずに起動して解答にデバッグ print が混ざっていると watch は `[DEBUG]` 行込みで比較して **WA** になるが、対話中に `:debug` を on にすれば watch が**新しい Debug 値で即再判定**して verdict が正しく揃う (起動時 `-d` と同じ判定になる)。トグルと同時に watch ペインのタイトル行に **`[debug]` バッジ**が出る。
- 問題ナビ (`:task`/`:contest`/`:e`) で移動しても **live Debug は引き継がれる** (起動時 `-d` の値に戻らない)。chat 表示の Debug と watch 判定の Debug は常に同じ値に揃う。
- chat 下ペインの**子プロセスの環境は変わらない** (起動時 `-d` のまま。`:debug` で子を再起動しない)。`test --interactive` 単体では従来どおり chat 表示のトグルのみ (watch ペインが無いため)。

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
- 要件: [018-start-command.md](./requirements/018-start-command.md) / [054-start-key-actions.md](./requirements/054-start-key-actions.md) / [023-start-split-screen.md](./requirements/023-start-split-screen.md) / [027-start-problem-navigation.md](./requirements/027-start-problem-navigation.md) (コマンドモードのナビゲーション) / [030-chat-debug-cheat-commands.md](./requirements/030-chat-debug-cheat-commands.md) (`:debug`/`:cheat`) / [034-start-debug-watch-sync.md](./requirements/034-start-debug-watch-sync.md) (`:debug` を watch へ反映) / [039-chat-replay-previous-session.md](./requirements/039-chat-replay-previous-session.md) (`:replay`) / [045-chat-run-sample-case.md](./requirements/045-chat-run-sample-case.md) (`:test`) / [048-chat-replay-test-case.md](./requirements/048-chat-replay-test-case.md) (`:replay` が直近の `:test` ケースを再生) / [004-exercise-test-watch.md](./requirements/004-exercise-test-watch.md)
