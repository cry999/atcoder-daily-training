# chat 専用スクロールモード 要件定義

## 概要

interactive chat の scrollback スクロールを、**専用の「スクロールモード」(`modeScroll`)** に集約する。これまで scrollback スクロールは insert モード (`PageUp`/`PageDown`/`Ctrl+B`/`Ctrl+F`。要件 040) と command モード (`PageUp`/`PageDown` + `Ctrl+P`/`Ctrl+N`/`Ctrl+U`/`Ctrl+D`。要件 033/067) の両方に散在していた。これを **両モードから撤去**し、`less`/vim 風の**素キー** (`j`/`k`/`d`/`u`/`f`/`b`/`g`/`G`) でスクロールする専用モードを新設する。スクロールモードへは insert モードの `PageUp`/`PageDown`、または command モードの `:scroll` で入る。抜けるときは `less` のように**明示コマンド `:q` / `:quit`** を打つ (誤爆しやすい単発 `Esc` では抜けない)。新フラグ・新サブコマンドは増やさない。追従 (`scrolled`) の仕組み・退出時の最下部復帰は 040/033 のものをそのまま共有する。

## 背景・目的

- 要件 033 (command)・040 (insert)・067 (command の行/半ページ) と、スクロールキーが 2 モードに分散し、割り当ても不揃い (insert はページのみ、command は行/半ページ/ページ) だった。insert モードは `Ctrl+D`=リセット→終了 (要件 051) 等でキーが埋まり、行/半ページを安全に足せないという制約もあった (067 が command 限定になった理由)。
- スクロールを 1 つの専用モードに切り出すと、そのモードでは修飾キー無しの**素キー**を自由に使える。`less`/vim に慣れた手には `j`/`k` (行)・`d`/`u` (半ページ)・`f`/`b` (ページ)・`g`/`G` (先頭/末尾) が馴染む。insert モードのキー衝突制約からも解放される。
- insert / command モードは「入力・コマンド実行」に専念でき、スクロールで送信キーやコマンドキーを消費しなくなる。
- 退出を単発 `Esc` にすると、スクロール操作中の誤爆で意図せずモードを抜けてしまう。`less` 同様に**明示コマンド (`:q`)** を打たせることで、抜けるのは意図した操作のときだけになる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 新モード | `modeScroll` (専用スクロールモード) を新設 | builder / recordEdit からの突入 |
| 突入 | insert モードの `PageUp`/`PageDown`、command モードの `:scroll` | 専用キー (例 `Ctrl+Y`)・start 分割画面の watch ペイン |
| 移動キー | `j`/`k` (行)・`d`/`u` (半ページ)・`f`/`b` (ページ)・`g`/`G` (先頭/末尾)・`Space` (ページ下)・矢印/`PageUp`/`PageDown` 併用 | 行数プレフィックス (`3j`)・検索 (`/`) |
| 退出 | スクロールモード内の `:` プロンプトで `:q` / `:quit` を打つ。退出で最下部 (最新) へ戻り追従再開 | `:` プロンプトへの他コマンド追加 |
| 追従 | 040/033 と共有: 上スクロール中は出力到着で最下部に引き戻さない。最下部到達で追従再開 | — |
| 撤去 | insert モードの `PageUp`/`PageDown`/`Ctrl+B`/`Ctrl+F` スクロール、command モードの `PageUp`/`PageDown`/`Ctrl+P`/`Ctrl+N`/`Ctrl+U`/`Ctrl+D` スクロール | — |

## CLI 仕様

新フラグ・新サブコマンドは**増やさない**。chat のモードと `:scroll` コマンドが増えるだけ。

### モード遷移

```
insert ──PageUp/PageDown──▶ scroll ──":q"/":quit"──▶ insert
command ──":scroll"───────▶ scroll ──":q"/":quit"──▶ insert
```

- **insert → scroll**: `PageUp` で入り、同時に 1 ページ上へスクロールする (`PageDown` は入って 1 ページ下だが最下部では no-op)。押した瞬間からスクロールが始まり、続けて `j`/`k` 等で細かく動かせる。
- **command → scroll**: `:scroll` を実行して入る。スクロール位置は現在のまま。
- **scroll → insert**: スクロールモード内で `:` を押すと `:` プロンプトが開き、`q` または `quit` を打って `Enter` で insert モードへ戻る。戻るとき最下部 (最新) へ移動し追従を再開する。

### スクロールモードのキー

| キー | 動作 | 対応 viewport メソッド |
|---|---|---|
| `j` / `↓` | 1 行下へ。最下部到達で追従再開 | `LineDown(1)` |
| `k` / `↑` | 1 行上へ。追従停止 (`scrolled=true`) | `LineUp(1)` |
| `d` | 半ページ下へ。最下部到達で追従再開 | `HalfViewDown()` |
| `u` | 半ページ上へ。追従停止 | `HalfViewUp()` |
| `f` / `Space` / `PageDown` | 1 ページ下へ。最下部到達で追従再開 | `ViewDown()` |
| `b` / `PageUp` | 1 ページ上へ。追従停止 | `ViewUp()` |
| `g` | 先頭へジャンプ。追従停止 | `GotoTop()` |
| `G` | 末尾 (最新) へジャンプ。追従再開 | `GotoBottom()` |
| `:` | スクロールモードの `:` プロンプトを開く (下記) | — |
| その他のキー | 無視 (no-op)。スクロールモードから勝手に抜けない | — |

方向は vim/less の慣習: `j`=下・`k`=上、`d`=down 半ページ・`u`=up 半ページ、`f`=forward ページ・`b`=backward ページ、`g`=先頭・`G`=末尾。

### スクロールモードの `:` プロンプト

| キー | 動作 |
|---|---|
| `:` (スクロール中) | `:` プロンプトを開き、以降の打鍵をコマンド文字列として受ける |
| `q` / `quit` + `Enter` | insert モードへ退出 (最下部へ戻り追従再開) |
| (空) + `Enter` | プロンプトを閉じてスクロールモードに戻る (退出しない) |
| その他 + `Enter` | `E492: unknown command :<arg>` を info 行に出し、プロンプトを閉じてスクロールモードに戻る |
| `Esc` | プロンプトのみキャンセルしてスクロールモードに戻る (**chat は終了しない・スクロールモードも抜けない**) |

> `:q` は command モードでは「chat 終了」だが (要件 024)、スクロールモードの `:q` は**スクロールモードから insert への退出**を意味する。スクロールモードは専用の `:` プロンプトを持ち、command モードとは独立に解釈する。

### 表示 (ステータス行)

スクロールモードでは入力ボックス (`» `) の代わりに、モードを明示するステータス行を出す:

```
── scrollback (過去の入出力) ──
< 6
> 3
< 2
> 1
────────────────────────────────
-- SCROLL --  j/k 行  d/u 半ページ  f/b ページ  g/G 先頭/末尾  : でコマンド (:q 退出)
```

`:` プロンプトを開いている間はステータス行の代わりに `:` 行を出す:

```
:q
```

### 出力イメージ (突入 → スクロール → 退出)

```
» 3                        ← insert モードで入力していた
< 6
> 3
(PageUp を押す)
-- SCROLL --  j/k 行  ...   ← スクロールモードへ。1 ページ上へスクロール
(j/k/d/u/f/b/g/G で移動)
: (":" を押す)
:q (q を打って Enter)       ← insert へ退出。最新行へ戻り追従再開
» ▎                        ← insert モードに戻った
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| スクロール対象 | scrollback (`viewport`)。子プロセス・stdin・解答・キャッシュには一切触れない (040/033 と同一) |
| 追従の維持 | `scrolled` 中は出力が届いても `YOffset` を維持。最下部に戻すと追従再開 (`refreshViewport` の既存分岐をそのまま使う) |
| 内容が画面に収まる場合 | `LineUp`/`LineDown`/`HalfView*`/`ViewUp`/`ViewDown` は no-op (viewport がクランプ)。エラーにしない |
| insert からの突入 | `PageUp`/`PageDown` は insert では textinput に流れて実質無視だった → スクロールモード突入 + そのページスクロールに割り当てる。`Ctrl+B`/`Ctrl+F` は insert から撤去し textinput の既定 (カーソル移動) に戻す |
| command からの突入 | `:scroll` で入る。command モードの `PageUp`/`PageDown`/`Ctrl+P`/`Ctrl+N`/`Ctrl+U`/`Ctrl+D` スクロールは撤去 (`Ctrl+*` は textinput の既定挙動に戻る) |
| 退出時の復帰 | `:q`/`:quit` で insert へ。`scrolled=false` + `viewport.GotoBottom()` で最新行へ戻し追従再開 |
| Esc の扱い | スクロールモード本体では Esc は no-op (抜けない)。`:` プロンプト中の Esc はプロンプトのみキャンセル。いずれも chat は終了しない |
| Ctrl+Z | 全モード共通でサスペンド (要件 058)。スクロールモードでも有効 (mode switch より前で処理) |
| builder / recordEdit | 本要件では対象外 (突入させない)。従来どおり |
| scrollbar | 要件 056 の右端スクロールバーはスクロールモードでもそのまま位置を示す |
| start 分割画面 | chat 内部で完結。watch ペイン (startsplit) は非依存・不変 |
| exit code | スクロールは表示のみ。chat の終了コードに影響しない |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat_casebuilder.go` | `modeScroll` を `chatMode` const に追加。`enterScrollMode()`/`exitScrollMode()`/`updateScroll(msg)`/`updateScrollPrompt(msg)` を追加。`updateCommand` から `PageUp`/`PageDown`/`Ctrl+P`/`Ctrl+N`/`Ctrl+U`/`Ctrl+D` の scroll case を撤去。`parseCommand` に `:scroll` を追加。`execCommand` に `case "scroll"` を追加。`showCheat` に `:scroll` を追記 |
| `internal/ui/chat.go` | insert ハンドラの `KeyPgUp`/`KeyCtrlB`→`scrollUp`、`KeyPgDown`/`KeyCtrlF`→`scrollDown` を撤去し、`KeyPgUp`/`KeyPgDown` を「スクロールモードへ突入 + ページスクロール」に置換 (`Ctrl+B`/`Ctrl+F` は default=textinput へ戻す)。`scrollTop()`/`scrollBottom()` ヘルパを追加。`Update` の mode switch に `case modeScroll: return m.updateScroll(msg)` を追加。`View` にスクロールモードのステータス行/`:` 行の描画を追加。スクロールモードの `:` プロンプト用フィールド (`scrollPrompt bool`、`cmdInput` を流用) を `chatModel` に追加 |
| `internal/ui/command_complete.go` | `completeNamesBase` に `"scroll"` を追加 (Tab 補完候補) |
| `internal/ui/chatscroll_test.go` | 撤去したキー (insert/command の scroll) のテストを、新挙動へ書き換え: insert `PageUp` でスクロールモードへ入り 1 ページ上 + `scrolled=true`、スクロールモードで `k`/`u`/`b`/`g` が上・`scrolled` を立てる・出力到着で引き戻さない、`j`/`d`/`f`/`G` で最下部に達すると追従再開、`:q` で insert へ退出 + 最下部復帰、を viewport offset / mode で固定。command モードは `:scroll` で突入することを固定 |
| `docs/tools/usage/test.md` | 対話モード節を「スクロールモード」の説明に更新 (突入 `PageUp`/`:scroll`、移動 `j/k/d/u/f/b/g/G`、退出 `:q`) |
| `docs/tools/usage/start.md` | チャットキーの説明を更新 (insert から `PageUp`/`PageDown` でスクロールモード、`:scroll`、退出 `:q`) |

### 新規ヘルパ (`internal/ui/chat.go`)

```go
// scrollTop は先頭へジャンプし追従を止める。scrollBottom は末尾 (最新) へ戻し追従を再開する。
func (m *chatModel) scrollTop()    { m.viewport.GotoTop(); m.scrolled = true }
func (m *chatModel) scrollBottom() { m.viewport.GotoBottom(); m.scrolled = false }
```

### 新規メソッド (`internal/ui/chat_casebuilder.go`)

```go
// enterScrollMode は insert / command から専用スクロールモードへ入る。
func (m *chatModel) enterScrollMode() { m.mode = modeScroll; m.scrollPrompt = false }

// exitScrollMode は insert へ戻り最下部 (最新) を表示して追従を再開する (:q / :quit)。
func (m *chatModel) exitScrollMode() { m.scrollPrompt = false; m.scrolled = false; m.viewport.GotoBottom(); m.mode = modeInsert }

// updateScroll はスクロールモードのキー処理 (素キーで移動、":" でプロンプト)。
func (m *chatModel) updateScroll(msg tea.KeyMsg) (tea.Model, tea.Cmd) { /* j/k/d/u/f/b/g/G/: */ }

// updateScrollPrompt はスクロールモードの ":" プロンプトのキー処理 (:q で退出)。
func (m *chatModel) updateScrollPrompt(msg tea.KeyMsg) (tea.Model, tea.Cmd) { /* Enter/Esc/textinput */ }
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| スクロールできる行が無い (内容が画面に収まる) | viewport メソッドは no-op。`scrolled` は立つが表示は変わらない (実害なし) |
| スクロールモードで未定義キー | 無視 (no-op)。スクロールモードから勝手に抜けない |
| `:` プロンプトで未知コマンド | `E492: unknown command :<arg>` を info 行に出し、プロンプトを閉じてスクロールモードに戻る (退出しない) |
| (注) chat はキー操作の TUI。exit code ではなくモード・viewport の表示位置で表現する。スクロールは chat 終了コードに影響しない |

## 非機能要件

- **既存非破壊**: builder / recordEdit モード・コマンド実行・入力履歴 (`↑`/`↓` は insert モードのもの)・送信・子プロセス・判定・exit code・start 分割画面・scrollbar (056) は不変。スクロールの撤去先 (insert/command) では、空いたキー (`Ctrl+B`/`Ctrl+F`/`Ctrl+P`/`Ctrl+N`/`Ctrl+U`/`Ctrl+D`) は textinput の既定挙動に戻すだけで新たな副作用を持たせない。
- **子プロセス非干渉**: スクロールは表示のみ。子・stdin・解答・キャッシュに触れない。
- **追従ロジックの再利用**: 040/033 の `scrolled` + `refreshViewport` の引き戻し抑止をそのまま使う。`scrollUp`/`scrollDown`/`scrollLineUp`/`scrollLineDown`/`scrollHalfUp`/`scrollHalfDown`/`followIfAtBottom` は既存のものを流用し、`scrollTop`/`scrollBottom` を足すだけ。
- **前方互換**: 突入キー・退出コマンドは将来 builder への拡張や専用突入キーの追加に耐える形にする。

## 将来の拡張ポイント

- builder / recordEdit モードや start 分割画面の watch ペインからのスクロールモード突入。
- 行数プレフィックス (`3j` で 3 行) や `/` 検索、`H`/`M`/`L` (画面内ジャンプ)。
- スクロールモード中の位置インジケータ (「N 行下 / 上にスクロール中」)。

## 用語

- **scrollback**: chat の過去メッセージ表示領域 (bubbletea `viewport`)。
- **スクロールモード (`modeScroll`)**: scrollback スクロール専用のモード。素キーで移動し、`:q` で抜ける。
- **追従 (follow)**: 出力到着のたびに最下部 (最新行) を表示し続けること。`scrolled` 中は一時停止する (要件 033/040)。

## 関連ドキュメント

- `docs/tools/requirements/033-command-mode-scrollback-paging.md` (command モードのページ移動。本要件が撤去 → スクロールモードへ集約)
- `docs/tools/requirements/040-insert-mode-scrollback-paging.md` (insert モードのページ移動。本要件が撤去 → スクロールモードへ集約)
- `docs/tools/requirements/067-command-mode-line-half-scroll.md` (command モードの行/半ページ。本要件が撤去 → スクロールモードの `j/k`・`d/u` へ集約)
- `docs/tools/requirements/056-chat-scrollbar.md` (右端スクロールバー。スクロールモードでもそのまま位置を示す)
- `docs/tools/requirements/024-interactive-case-builder.md` (chat のモード機構・command モードの導入)
- `docs/tools/usage/test.md` / `docs/tools/usage/start.md` (キー説明の更新先)
