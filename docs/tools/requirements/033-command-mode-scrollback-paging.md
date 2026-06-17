# command モードでのチャット履歴ページ移動 要件定義

## 概要

interactive chat の **command モード** (`Esc` → `:` の vim 風モード、要件 024) のあいだ、**`PageUp` / `PageDown` でチャット履歴 (scrollback) を 1 ページ上下にスクロール**できるようにする。これまで chat の表示領域 (bubbletea `viewport`) は常に最下部 (最新行) に張り付いており、流れていった過去の入出力を遡れなかった。command モードに入って `:` を打ちながら上の履歴を読み返せると、長い対話セッションのデバッグがしやすい。command モードを抜ける (`Esc` / コマンド実行) と最下部 (最新) に戻る。新フラグ・新サブコマンドは増やさない。

## 背景・目的

- chat の `viewport` は `refreshViewport` が**毎回 `GotoBottom()`** するため常に最新行を表示する。出力が画面 (`maxViewportHeight`) を超えると古い行は上にスクロールアウトし、もう見られない。
- 対話問題のデバッグでは「数手前に何を送って何が返ったか」を遡りたい場面がある。insert モードはキーが入力送信・履歴 (`↑`/`↓`) に割り当て済みでスクロールに使いにくいが、**command モードは `:` 行を打つだけで他のキーが空いている**。ここに scrollback のページ移動を載せるのが素直。
- `:` 行は単一行の textinput。`PageUp`/`PageDown` は textinput が使わないので、コマンド入力 (文字・カーソル移動・補完) と衝突しない。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象モード | command モード (`:` 行表示中) | insert モードでのスクロール |
| キー | `PageUp` = 1 ページ上、`PageDown` = 1 ページ下 | 半ページ・行スクロール (`↑`/`↓`)・先頭/末尾 (`gg`/`G` 等) |
| ページ単位 | viewport 1 画面分 (`ViewUp`/`ViewDown`) | 半ページ (`HalfViewUp`/`HalfViewDown`) |
| 追従 | スクロール中は出力到着で最下部に引き戻さない。最下部に居るときは従来どおり追従 | — |
| 復帰 | command モードを抜けると最下部 (最新) に戻る | スクロール位置を保持したまま抜ける option |

### insert モードを当面対象外にする理由

insert モードは `Enter` 送信・`↑`/`↓` 入力履歴・`Ctrl+C`/`Ctrl+D`/`Ctrl+S` などキーが埋まっており、スクロール用の空きキーが乏しい。`PageUp`/`PageDown` を insert にも足す余地はあるが、依頼は「command モード時」なので当面 command モード限定とする (refreshViewport の追従修正は全モード共通で効くので、将来 insert に広げるのは容易)。

## CLI 仕様

新フラグ・新サブコマンドは**増やさない**。command モードのキー挙動が増えるだけ。

### command モードのキー (追加分)

| キー | 動作 |
|---|---|
| `PageUp` | scrollback を 1 ページ上へ。以降の出力到着で最下部に引き戻されない (`scrolled` を立てる) |
| `PageDown` | scrollback を 1 ページ下へ。最下部に達したら追従を再開 (`scrolled` を解除) |
| `Esc` (既存) | command モードを抜ける + **最下部 (最新) に戻す** |
| `Enter` (既存) | コマンド実行。実行後は最下部に戻る (`execCommand` 末尾の refresh) |
| その他 (文字 / `Tab` 補完) | 既存どおり `:` 行の編集 (スクロールには影響しない) |

### 処理ステップ

1. `PageUp` 押下: `viewport.ViewUp()` で 1 画面分上にスクロールし、`scrolled = true`。
2. `PageDown` 押下: `viewport.ViewDown()`。`viewport.AtBottom()` なら `scrolled = false` (追従再開)。
3. `refreshViewport` (出力到着・スピナー tick 等で毎回呼ばれる): content と高さを更新したのち、**`scrolled` ならスクロール位置 (`YOffset`) を維持、そうでなければ `GotoBottom()`**。
4. command モードを抜けるとき (`Esc` / コマンド実行) は `scrolled = false` にし、最下部へ戻す (`GotoBottom`)。

### 出力イメージ

```
:                          ← command モード。PageUp で上の履歴へ
< 6
> 3                        ← 数手前の入出力が見えている
< 2
> 1
...(PageDown で最新へ。Esc でコマンドモードを抜けると最新行に戻る)
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| スクロール対象 | scrollback (`viewport`)。子プロセス・stdin・解答・キャッシュには触れない |
| 追従の維持 | `scrolled` 中は出力が届いても `YOffset` を維持 (保存→`SetContent`→`SetYOffset` で復元)。最下部に戻すと追従再開 |
| insert / builder モード | 本要件の時点では `scrolled` は command モードでしか立たない (insert/builder は最下部追従)。**※ insert モードは後続の [040](040-insert-mode-scrollback-paging.md) でスクロール対応し、`scrolled` を共有する。builder は引き続き非対象** |
| 内容が画面に収まる場合 | `ViewUp`/`ViewDown` は no-op (スクロールする行が無い)。エラーにしない |
| command モード退出 | `Esc`・コマンド実行で最下部 (最新) に戻る。insert モードはスクロールキーを持たないので「上に張り付いたまま操作不能」を避ける |
| `:` 行の編集 | `PageUp`/`PageDown` は `:` 行の文字列・カーソルを変えない (scrollback だけ動かす) |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `chatModel` に `scrolled bool` を追加。`refreshViewport` の末尾 `GotoBottom()` を「`scrolled` 中は `YOffset` 保存→復元、それ以外は `GotoBottom`」に変更 |
| `internal/ui/chat_casebuilder.go` | `updateCommand` に `PageUp`/`PageDown` の case を追加 (`ViewUp`/`ViewDown` + `scrolled` 更新)。`Esc` case で `scrolled=false` + `GotoBottom`。`execCommand` 先頭で `scrolled=false` (末尾 refresh が最下部に戻す) |
| `internal/ui/chatscroll_test.go` (新規) | command モードで `PageUp` が `YOffset` を上げる・`scrolled` が立つ、`refreshViewport` がスクロール中は最下部に引き戻さない、`PageDown` で最下部に戻ると追従再開、`Esc` で最下部に戻る、を viewport offset で固定 |
| `docs/tools/atcoder-test-usage.md` | command モード節に `PageUp`/`PageDown` でのページ移動を追記 |
| `docs/tools/todo.md` | 本項目を追加し ✅ DONE。要件 024 と相互リンク |

### 状態フィールド (`internal/ui/chat.go`)

```go
// scrolled は command モードで scrollback を上にスクロール中 (= 出力到着で
// 最下部に引き戻さない) ことを表す。command モードを抜けると false に戻す。
scrolled bool
```

### refreshViewport の追従 (擬似コード)

```go
saved := m.viewport.YOffset
m.viewport.SetContent(content)
m.viewport.Height = lines
if m.scrolled {
    m.viewport.SetYOffset(saved) // 上スクロール位置を維持 (出力で引き戻さない)
} else {
    m.viewport.GotoBottom()
}
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| スクロールできる行が無い (内容が画面に収まる) | `ViewUp`/`ViewDown` は no-op。`scrolled` は立つが表示は変わらない (実害なし) |
| (注) chat はキー操作の TUI。exit code ではなく viewport の表示位置で表現する。スクロールは chat 終了コードに影響しない |

## 非機能要件

- **既存非破壊**: insert / builder モード・コマンド実行・`Ctrl+*` キー・出力待ちスピナーは不変。`refreshViewport` の追従修正は「最下部に居るときだけ `GotoBottom`」で、スクロールキーを持たない insert モードでは常に最下部 = 従来と同一挙動。
- **子プロセス非干渉**: スクロールは表示のみ。子・stdin・解答・キャッシュに触れない。
- **前方互換**: command モード (024)・Tab 補完 (031) と独立。将来 insert モードや半ページに広げても `scrolled` + 追従修正をそのまま使える。

## 将来の拡張ポイント

- insert モードでのスクロール (`PageUp`/`PageDown` を insert にも)。
- 半ページ (`HalfViewUp`/`HalfViewDown`)・行スクロール (`↑`/`↓`)・先頭/末尾 (`GotoTop`/`GotoBottom`)。
- スクロール中であることの視覚インジケータ (`-- more --` 等)。

## 用語

- **scrollback**: chat の過去メッセージ表示領域 (bubbletea `viewport`)。
- **command モード**: `Esc` → `:` で入る vim 風モード (要件 024)。`updateCommand` が全キーを横取りする。
- **追従 (follow)**: 出力到着のたびに最下部 (最新行) を表示し続けること。`scrolled` 中は一時停止する。

## 関連ドキュメント

- `docs/tools/requirements/024-interactive-case-builder.md` (command モードの導入。本機能はそのモード中のキーを増やす)
- `docs/tools/requirements/031-*` (command モードの Tab 補完。同じ `updateCommand` を触る)
- `docs/tools/atcoder-test-usage.md` (command モードのキー説明の更新先)
