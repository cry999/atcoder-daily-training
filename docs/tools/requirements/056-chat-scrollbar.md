# chat スクロールバー 要件定義

## 概要

chat の scrollback (viewport) の**右端 1 列に縦スクロールバー**を表示し、いま全体のどのあたりを見ているか・上下にどれだけ続きがあるかを視覚化する。スクロールバーは scrollback が 1 画面に収まらず**スクロール可能なときだけ**描画し、収まっているときは描かない (gutter は空白)。位置・つまみ (thumb) の長さは viewport の `ScrollPercent()` / `TotalLineCount()` / 表示高から算出する。挙動 (キー割当・追従・判定・exit code) は一切変えない純粋な表示追加。

## 背景・目的

- insert/command モードのページスクロール ([033](033-command-mode-scrollback-paging.md) / [040](040-insert-mode-scrollback-paging.md)) で過去の入出力を遡れるようになったが、**いま全体のどの位置にいるか**・**まだ上 (下) に続きがあるか**が画面から分からない。長い出力を遡っていると現在地を見失う。
- 040 の「将来の拡張ポイント」に挙げた *スクロール中インジケータ* の視覚版にあたる。テキストのステータス行ではなく、端末 TUI で馴染みのある右端スクロールバーで現在地と相対位置を常時示す。
- viewport (charmbracelet/bubbles) は `TotalLineCount()` / `VisibleLineCount()` / `ScrollPercent()` を公開しており、これらから thumb を算出して 1 列に重ねるだけで実装できる。スクロール機構そのもの (033/040) には手を入れない。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | chat の scrollback (viewport) 表示領域 | builder 画面・start 分割画面 |
| 表示条件 | scrollback がスクロール可能 (`TotalLineCount > 表示高`) なとき | 収まっていても薄い full-track を出す案 |
| 配置 | viewport の**右端 1 列** (gutter)。本文はその左 `width-1` 列に折り返す | 左端配置・幅可変 |
| つまみ位置/長さ | `ScrollPercent()` と `表示高 × 表示高 / 総行数` から算出 | ドラッグ操作・クリックジャンプ (マウス) |
| 対象モード | insert / command 双方 (viewport 描画は共通) | builder モード |
| 追従・キー | 不変 (033/040 のまま) | — |

### gutter は常時確保する

スクロールバーを「スクロール可能になった瞬間に出す」と、本文の折り返し幅が `width` → `width-1` に変わって既存行が 1 桁分リフローしてしまう。これを避けるため **gutter (右端 1 列) は常時確保**し (本文の折り返し幅は常に `width-1`)、スクロールバー (track + thumb) は**スクロール可能なときだけ**その列に描く。収まっているときは同じ列を空白にする。これで overflow の開始/終了でリフローが起きない。

## CLI 仕様

新フラグ・新サブコマンドは増やさない。chat の viewport 描画に右端スクロールバーが加わるだけ。キー操作は 033/040 のまま不変。

### 描画ルール

| 状況 | 右端 gutter (1 列) |
|---|---|
| scrollback がスクロール可能 (`TotalLineCount > 表示高`) | track (`│`, dim) の上に thumb (`█`, やや明るい) を重ねて描画 |
| scrollback が 1 画面に収まる (スクロール不要) | 空白 (描画しない) |
| 端末幅が狭く gutter を確保できない (`width < 2`) | スクロールバー無し・本文が全幅を使う |

### thumb の算出

`h` = viewport の表示高 (= `viewport.Height`、View が返す行数)、`total` = `TotalLineCount()` とする。

1. スクロール可能判定: `total > h` のときだけ描画 (それ以外は空白)。
2. thumb の長さ: `thumb = round(h * h / total)`、下限 1・上限 `h`。
3. thumb の開始行: `p = ScrollPercent()` (0..1) として `start = round(p * (h - thumb))`、`[0, h-thumb]` にクランプ。
4. 各行 `r ∈ [0, h)`: `start <= r < start+thumb` なら thumb 文字、そうでなければ track 文字。

最下部 (`p=1`) で thumb は下端、最上部 (`p=0`) で上端に来る。viewport の `ScrollPercent` は `total <= h` のとき 1.0 を返すため、必ず 1 の判定 (`total > h`) で先にゲートする。

### 出力イメージ

スクロール可能で中ほどを表示中 (右端の `│`/`█` が gutter):

```
abc457_d  contest=abc457  time_limit=2000ms  (interactive)
» 5 3                                       │
← 5 3                                       █
→ 12                                        █
← 1 2 3 4 5                                 █
→ ...                                       │
────────────────────────────────────────────
» |
────────────────────────────────────────────
```

スクロール不要 (収まっている) なら gutter は空白:

```
abc457_d  contest=abc457  time_limit=2000ms  (interactive)
» 5 3
← 12
────────────────────────────────────────────
» |
────────────────────────────────────────────
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| 表示領域 | scrollback (viewport) のみ。header / 入力ボックス / command 行 / builder 画面には付かない |
| 折り返し幅 | 本文は常に `width-1` 列で折り返す (gutter を常時確保)。`renderMsgBlock` に渡す幅を `contentWidth()` に変更 |
| viewport 幅 | `viewport.Width = contentWidth()` に設定。View() が各行を `contentWidth` まで pad するので、その右にスクロールバー 1 列を連結する |
| 追従 (follow) | 不変。`scrolled` 中は最下部に引き戻さない (033/040)。スクロールバーは現在の `YOffset` を反映するだけ |
| スピナー行 | 出力待ちスピナー行も scrollback の一部として数える (`TotalLineCount` に含まれる)。特別扱い無し |
| 空のとき | メッセージが無く `awaiting` でもないときは viewport 自体を描かない (既存挙動)。スクロールバーも出ない |
| command モード | viewport 描画は insert と共通なので command モードでも同じくスクロールバーが出る (不変の挙動に表示が乗るだけ) |
| 子プロセス・判定・exit code | 不変。スクロールバーは表示のみ |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `contentWidth()` ヘルパ追加 (`width>=2` なら `width-1`、それ未満は `width` 下限 1)。`WindowSizeMsg` で `viewport.New`/`viewport.Width` を `contentWidth()` に。`refreshViewport` の `renderMsgBlock(msg, m.width)` を `contentWidth()` に。`View()` の `m.viewport.View()` 呼び出しを新ヘルパ `renderViewport()` に置換。`renderViewport()` は viewport の各表示行の右端にスクロールバー列を連結 (`scrollbarColumn(h)` がスクロール可否を判定して track/thumb 文字列を返す)。スクロールバー用スタイル (track=`│` dim・thumb=`█` やや明るい) を追加 |
| `internal/ui/chatscrollbar_test.go` | (新規) overflow した model で `renderViewport()` がスクロールバー列を含む・最下部では thumb が下端・上スクロールで thumb が上に動く・収まっているときは gutter が空白・`width<2` では列を足さない、を固定 |
| `docs/tools/atcoder-start-usage.md` | チャットの説明に「scrollback がスクロール可能なとき右端にスクロールバーが出る」を追記 |
| `docs/tools/todo.md` | 本項目を追加し ✅ DONE。033/040 と相互リンク |

### 新ヘルパの素描 (Go)

```go
const chatScrollbarWidth = 1

// contentWidth は本文 (折り返し) に使える幅。右端 1 列をスクロールバー gutter に確保する。
func (m *chatModel) contentWidth() int {
	if m.width >= 2 {
		return m.width - chatScrollbarWidth
	}
	if m.width >= 1 {
		return m.width
	}
	return 1
}

// renderViewport は viewport の表示に右端スクロールバー列を重ねて返す。
func (m *chatModel) renderViewport() string {
	body := m.viewport.View()
	if m.width < 2 {
		return body // gutter を確保できない狭い端末
	}
	lines := strings.Split(body, "\n")
	col := m.scrollbarColumn(len(lines)) // 各行の gutter 文字 (スクロール不可なら全て空白)
	for i := range lines {
		lines[i] += col[i]
	}
	return strings.Join(lines, "\n")
}

// scrollbarColumn は h 行分の gutter 文字列を返す。スクロール可能なら track+thumb、
// 不可なら全て空白。
func (m *chatModel) scrollbarColumn(h int) []string { /* thumb 算出は上記の式 */ }
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| scrollback が 1 画面に収まる | gutter は空白 (スクロールバー非表示)。実害なし |
| 端末幅が極端に狭い (`width < 2`) | スクロールバーを足さず本文が全幅を使う (列割れを防ぐ) |
| 表示高 `h <= 0` / 総行数 0 | `total > h` が偽になり空白を返す (描画なし) |
| (注) chat はキー操作の TUI。スクロールバーは exit code に影響しない |

## 非機能要件

- **既存非破壊**: キー割当・追従ロジック (033/040)・送信・入力履歴・command/builder モード・子プロセス・判定・exit code・start 分割画面は不変。スクロールバーは viewport 描画への純粋な追加。
- **リフロー回避**: gutter を常時確保し本文折り返し幅を `width-1` で一定にするため、overflow の開始/終了で既存行がリフローしない。
- **一貫性**: viewport 描画は insert/command で共通なので、両モードで同じスクロールバーが出る。
- **subtle なスタイル**: track/thumb は dim な mocha 色 (track=`surface1`・thumb=`overlay1`) にして本文の可読性を邪魔しない。

## 将来の拡張ポイント

- builder 画面・start 分割画面へのスクロールバー展開。
- マウス対応 (thumb ドラッグ・track クリックでジャンプ)。
- スクロール不要時も薄い full-track を出して gutter を「ここにバーが出る場所」と示す案。
- 行数バッジ (「N / M 行」) の併記。

## 用語

- **scrollback**: chat の viewport が保持する過去の入出力ログ。
- **gutter**: viewport の右端に確保した 1 列。スクロール可能なときスクロールバーを描く。
- **track**: スクロールバーの背景レール (`│`)。
- **thumb**: 現在の表示範囲を示すつまみ (`█`)。長さ・位置が相対位置を表す。
- **follow (追従)**: 出力到着時に viewport を最下部 (最新) に保つ既定挙動 (033/040)。

## 関連ドキュメント

- `docs/tools/requirements/033-command-mode-scrollback-paging.md` (command モードのスクロール)
- `docs/tools/requirements/040-insert-mode-scrollback-paging.md` (insert モードのスクロール。本件はその位置の視覚化)
- `docs/tools/atcoder-start-usage.md` (チャットキー/表示の説明の更新先)
