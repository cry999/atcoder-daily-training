# command モードでの行スクロール・半ページスクロール 要件定義

> **注記 (要件 [071](071-chat-scroll-mode.md) で置換)**: 本要件が定めた command モードの行 (`Ctrl+P`/`Ctrl+N`) / 半ページ (`Ctrl+U`/`Ctrl+D`) スクロールは撤去し、専用の**スクロールモード**の素キー (`j`/`k` = 行、`d`/`u` = 半ページ) へ集約した。以下は経緯・設計背景の記録として残す。

## 概要

interactive chat の **command モード** (`Esc` → `:` の vim 風モード、要件 024) で、これまで `PageUp` / `PageDown` の **1 ページ単位**しか無かった scrollback スクロールに、より細かい移動手段を足す。**`Ctrl+N` / `Ctrl+P` で 1 行ずつ**、**`Ctrl+D` / `Ctrl+U` で半ページずつ** scrollback を上下できるようにする。要件 033 (command モードのページ移動) の「将来の拡張ポイント」に挙げていた半ページ・行スクロールの実装。追従 (`scrolled`) の仕組み・退出時の最下部復帰は 033 のものをそのまま共有する。新フラグ・新サブコマンドは増やさない。

## 背景・目的

- 要件 033 で command モードの `PageUp`/`PageDown` (1 ページ単位) を導入したが、長い対話ログを「あと数行だけ」遡りたい・「もう少しだけ」戻したいときにページ単位は粗い。
- vim / less に慣れた手には「1 行 = `Ctrl+N`/`Ctrl+P`」「半画面 = `Ctrl+D`/`Ctrl+U`」が馴染む。command モードの `:` 行は単一行 textinput なので、これらの `Ctrl+*` は入力文字・カーソル移動 (`Tab` 補完含む) と衝突しない。
- insert モードは `Ctrl+D` (リセット→終了、要件 051)・`Ctrl+C`・`Ctrl+S` 等が埋まっており `Ctrl+D`/`Ctrl+U` を安全に割り当てられない。よって本要件は **command モード限定**とする (033 と同じ切り分け)。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象モード | command モード (`:` 行表示中) | insert モードでの行/半ページスクロール |
| 行スクロール | `Ctrl+N` = 1 行下、`Ctrl+P` = 1 行上 | 行数プレフィックス (`3Ctrl+N` 等) |
| 半ページ | `Ctrl+D` = 半ページ下、`Ctrl+U` = 半ページ上 | — |
| ページ (既存) | `PageUp`/`PageDown` = 1 ページ (要件 033、不変) | — |
| 追従 | 033 と共有: 上スクロール中は出力到着で最下部に引き戻さない。最下部に達すると追従再開 | — |
| 復帰 | 033 と共有: command モードを抜ける (`Esc`/コマンド実行) と最下部 (最新) に戻る | — |

## CLI 仕様

新フラグ・新サブコマンドは**増やさない**。command モードのキー挙動が増えるだけ。

### command モードのキー (追加分)

| キー | 動作 | 対応 viewport メソッド |
|---|---|---|
| `Ctrl+P` | scrollback を 1 行上へ。以降の出力到着で最下部に引き戻されない (`scrolled` を立てる) | `LineUp(1)` |
| `Ctrl+N` | scrollback を 1 行下へ。最下部に達したら追従を再開 (`scrolled` を解除) | `LineDown(1)` |
| `Ctrl+U` | scrollback を半ページ上へ。`scrolled` を立てる | `HalfViewUp()` |
| `Ctrl+D` | scrollback を半ページ下へ。最下部に達したら追従を再開 | `HalfViewDown()` |
| `PageUp` / `PageDown` (既存) | 1 ページ上/下 (要件 033、不変) | `ViewUp()` / `ViewDown()` |

方向の割り当ては vim / emacs の慣習に合わせる: `Ctrl+P` = previous (上)、`Ctrl+N` = next (下)、`Ctrl+U` = up 半ページ、`Ctrl+D` = down 半ページ。

### 処理ステップ

1. 上方向 (`Ctrl+P`/`Ctrl+U`): 対応する viewport メソッドで上スクロールし、`scrolled = true`。
2. 下方向 (`Ctrl+N`/`Ctrl+D`): 対応する viewport メソッドで下スクロールし、`viewport.AtBottom()` なら `scrolled = false` (追従再開)。
3. `refreshViewport` の追従 (033 と共有): `scrolled` なら `YOffset` を維持、そうでなければ `GotoBottom()`。
4. command モード退出 (`Esc`/コマンド実行) は 033 と同じく `scrolled = false` + 最下部復帰。

### 出力イメージ

```
:                          ← command モード
< 6
> 3
< 2                        ← Ctrl+P で 1 行ずつ、Ctrl+U で半画面ずつ遡れる
> 1
...(Ctrl+N/Ctrl+D で最新へ。最下部に達すると追従再開。Esc で最新行に戻る)
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| スクロール対象 | scrollback (`viewport`)。子プロセス・stdin・解答・キャッシュには触れない (033 と同一) |
| 追従の維持 | `scrolled` 中は出力が届いても `YOffset` を維持。最下部に戻すと追従再開 (033 の `refreshViewport` をそのまま使う) |
| 内容が画面に収まる場合 | `LineUp`/`LineDown`/`HalfView*` は no-op (スクロールする行が無い)。エラーにしない |
| `:` 行の編集 | `Ctrl+N/P/D/U` は `:` 行の文字列・カーソルを変えない (scrollback だけ動かす) |
| insert / builder モード | 本要件でも insert/builder には割り当てない。`Ctrl+D` は insert モードでは従来どおりリセット→終了 (要件 051) |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | 行/半ページ用のスクロールヘルパを追加 (`scrollLineUp`/`scrollLineDown`/`scrollHalfUp`/`scrollHalfDown`)。既存 `scrollUp`/`scrollDown` (ページ) と同じ `scrolled` 更新則を踏襲 |
| `internal/ui/chat_casebuilder.go` | `updateCommand` に `Ctrl+P`/`Ctrl+N`/`Ctrl+U`/`Ctrl+D` の case を追加 (上記ヘルパを呼ぶ) |
| `internal/ui/chatscroll_test.go` | command モードで `Ctrl+P`/`Ctrl+U` が上スクロール + `scrolled` を立てる、出力到着で引き戻さない、`Ctrl+N`/`Ctrl+D` で最下部に戻ると追従再開、を viewport offset で固定 |
| `docs/tools/usage/test.md` | command モード節に `Ctrl+N/P` (行) / `Ctrl+D/U` (半ページ) を追記 |

### スクロールヘルパ (`internal/ui/chat.go`)

```go
// scrollLineUp/Down は scrollback を 1 行、scrollHalfUp/Down は半ページ動かす。
// up 系は追従を止め、down 系は最下部に達したら追従を再開する (scrollUp/scrollDown と同則)。
func (m *chatModel) scrollLineUp()   { m.viewport.LineUp(1); m.scrolled = true }
func (m *chatModel) scrollLineDown() { m.viewport.LineDown(1); m.followIfAtBottom() }
func (m *chatModel) scrollHalfUp()   { m.viewport.HalfViewUp(); m.scrolled = true }
func (m *chatModel) scrollHalfDown() { m.viewport.HalfViewDown(); m.followIfAtBottom() }
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| スクロールできる行が無い (内容が画面に収まる) | viewport メソッドは no-op。`scrolled` は立つが表示は変わらない (実害なし) |
| (注) chat はキー操作の TUI。exit code ではなく viewport の表示位置で表現する。スクロールは chat 終了コードに影響しない |

## 非機能要件

- **既存非破壊**: insert / builder モード・コマンド実行・既存の `PageUp`/`PageDown` (033)・`Ctrl+*` の insert 側割り当て (`Ctrl+C`/`Ctrl+D`/`Ctrl+S`/`Ctrl+Z`) は不変。追加キーは command モードの `updateCommand` の中だけに閉じる。
- **子プロセス非干渉**: スクロールは表示のみ。子・stdin・解答・キャッシュに触れない。
- **前方互換**: 033 の `scrolled` + `refreshViewport` 追従をそのまま再利用する。将来 insert モードや行数プレフィックスに広げても同じ土台で足せる。

## 将来の拡張ポイント

- insert モードでの行/半ページスクロール (insert 側は空きキーが乏しいので別途キー設計が要る)。
- 行数プレフィックス (`3` → `Ctrl+N` で 3 行) や `gg`/`G` 相当の先頭/末尾ジャンプ。

## 用語

- **scrollback**: chat の過去メッセージ表示領域 (bubbletea `viewport`)。
- **command モード**: `Esc` → `:` で入る vim 風モード (要件 024)。`updateCommand` が全キーを横取りする。
- **追従 (follow)**: 出力到着のたびに最下部 (最新行) を表示し続けること。`scrolled` 中は一時停止する (要件 033)。

## 関連ドキュメント

- `docs/tools/requirements/033-command-mode-scrollback-paging.md` (command モードのページ移動。本要件はその「将来の拡張ポイント」の行/半ページを実装する)
- `docs/tools/requirements/040-insert-mode-scrollback-paging.md` (insert モードのページ移動。`scrolled` を共有する)
- `docs/tools/requirements/024-interactive-case-builder.md` (command モードの導入)
- `docs/tools/usage/test.md` (command モードのキー説明の更新先)
