# インタラクティブ chat の command モードに `:debug` / `:cheat` を追加 要件定義

## 概要

インタラクティブ chat の vim 風 command モード ([024](024-interactive-case-builder.md)) に、運用を楽にする 2 コマンドを足す。**`:debug`** は chat 実行中に Debug 表示 (`-d` 相当、子 stdout の `[DEBUG]` 行を別カテゴリに振り分け) を on/off トグルする。**`:cheat`** (別名 `:help` / `:?`) は利用可能なコマンド一覧をチートシートとして chat 内に表示する。どちらも新フラグ・新サブコマンドを増やさず、既存の command モード基盤に乗せる。

## 背景・目的

- `-d` (Debug) は **起動時フラグ**でしか切り替えられず、chat に入ってから「今の出力に `[DEBUG]` 行が混ざっているか確認したい」と思っても付け外しできない。対話中にトグルできると、デバッグ print を仕込んだ解答の挙動を確かめながら表示を切り替えられる。
- command モードのコマンド ([024] `:case`/`:w`/`:set verify`、[027] `:task`/`:contest`/`:e`) は増えてきたが、**画面に一覧が出ない**ため覚えていないと使えない。`:cheat` で「今この画面で打てるコマンド」をその場で引ければ学習コストが下がる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| `:debug` | `m.header.Debug` をトグル。`:set debug` / `:set nodebug` で明示 on/off も可 | per-行の DEBUG ハイライト切替など細分化 |
| `:cheat` | 利用可能コマンドを **info 行ダンプ**で一覧表示。`NavEnabled` のときだけ `:task`/`:contest`/`:e` も載せる | モーダル表示・キー割当の併記 |
| 反映範囲 | `:debug` は **以後届く** stdout 行の `[DEBUG]` 振り分けに反映 (既描画行は遡及しない) | 既存行の再分類 (再パース) |

### 境界

- 子プロセス・判定・exit code・`Ctrl+C`/`Ctrl+D`/`Ctrl+S`・既存コマンド (`:case`/`:w`/`:set verify`/`:q`/`:task`/`:contest`/`:e`) は不変。
- stdout には何も書かない (chat 内の info 行のみ)。バッチ `test`/`run` の `-d` 経路 (`runexec`/`testexec`) には触れない。

## CLI / TUI 仕様

新フラグ無し。すべて command モード (insert で `Esc` → `:`) の内側。

### コマンド一覧 (追加分)

| コマンド (別名) | 動作 |
|---|---|
| `:debug` | Debug 表示をトグル。info 行 `(debug on …)` / `(debug off …)` を出す |
| `:set debug` / `:set nodebug` | Debug を明示 on / off (`:set verify` と同じ書式) |
| `:cheat` (`:help` / `:?`) | 利用可能なコマンド一覧を info 行で表示 |

### `:debug` の動作

1. `m.header.Debug` を反転 (`:set debug`/`nodebug` は明示セット)。
2. info 行で新しい状態と「以降の `[DEBUG]` 行に反映」を示す。
3. 以後 `chatLineMsg` で届く stdout 行のうち `[DEBUG]` 接頭辞を持つものが、新しい `Debug` 値に従って `kindDebug` / `kindOut` に振り分けられる。**既に描画済みの行は変えない** (保持済み `chatLine` の kind は遡及更新しない)。

### `:cheat` の表示イメージ (info 行ダンプ)

```
利用可能なコマンド (Esc で command モード):
  :case (:c)            入出力ケース作成画面を開く
  :w [name]             追加ケースを tests-extra に保存
  :set verify|noverify  ライブ検証 on/off
  :debug                Debug 表示 (-d) を切替 (:set debug|nodebug)
  :cheat (:help :?)     このコマンド一覧
  :q                    chat 終了 (作成画面中は破棄)
  :task next|prev (n|p) 問題記号を移動        ← NavEnabled (start) のときだけ
  :contest next|prev    コンテストを移動       ← 同上
  :e <spec>             任意の問題へジャンプ    ← 同上
```

- 各行は 1 つの `kindInfo` `chatLine` として積む (info の折り返しは既存の `renderMsgBlock` に委ねる)。
- `:task`/`:contest`/`:e` は `NavEnabled` が真 (start 分割画面) のときだけ載せる (`test --interactive` 単体では使えないため一覧にも出さない)。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `:debug` (builder 中) | Debug をトグルして **builder に戻る** (作成画面は破棄しない)。`:set` と同じ復帰挙動 |
| `:cheat` (builder 中) | info 行を積んで builder に戻る (行は閉じた後に見える) |
| `:debug` / `:cheat` (insert) | 実行して insert に戻る |
| 既存出力の `[DEBUG]` 行 | `:debug` 後も再分類しない (以後の行のみ) |
| `:set debug foo` 等の余分引数 | 第 2 トークンだけ見る (`verify` と同じ寛容さ)。未知オプションは `E518` |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat_casebuilder.go` | `parseCommand` に `debug` / `cheat`(別名 `help`,`?`) を追加。`execCommand` にハンドラ。`applySet` に `debug`/`nodebug`。`toggleDebug`/`setDebug`/`showCheat` ヘルパを追加。`newCommandInput` の placeholder にコマンドを追記 |
| `internal/ui/chat.go` | 変更最小。`m.header.Debug` は既にモデル上で可変で、`chatLineMsg` 側の `[DEBUG]` 振り分けが参照する (ロジック変更なし) |
| `internal/ui/chat_casebuilder_test.go` | `parseCommand` 拡張・`toggleDebug`/`setDebug`・`applySet` debug・`showCheat`(NavEnabled 有無) のテスト |
| `docs/tools/atcoder-test-usage.md` | command モードのコマンド表に `:debug` / `:cheat` を追記 |
| `docs/tools/todo.md` | 本項目を記載し本要件へ相互リンク |

### ヘルパの素描

```go
// chat_casebuilder.go (package ui)
func (m *chatModel) setDebug(on bool)   // m.header.Debug=on にして info 行を 1 本積む
func (m *chatModel) toggleDebug()        // setDebug(!m.header.Debug)
func (m *chatModel) showCheat()          // 利用可能コマンドを info 行で積む (NavEnabled で nav 分を足す)
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `:set <未知>` (verify/noverify/debug/nodebug 以外) | `E518: unknown option :set …` を 1 行。副作用なし |
| 未知コマンド | 既存どおり `E492: unknown command :…` を 1 行 |
| exit code | 影響なし (表示のみ。引数誤り=2 / 実行時失敗=1 / 成功=0 は不変) |

## 非機能要件

- **既存非破壊**: 既存コマンド・キー・判定・chat の描画は不変。`:debug`/`:cheat` を打たない限り従来どおり。
- **stdout 非汚染**: 表示は chat 内の info 行のみ。
- **前方互換**: `:set` のオプション語彙 (`verify`/`debug`/…) を増やす形にして、将来 `:set <opt>` を足しやすくする。`:cheat` は `NavEnabled` 等の文脈に応じて一覧を組み立てる。
- **決定的にテスト可能**: `parseCommand` は純粋関数のまま、`setDebug`/`showCheat` は `chatModel` の状態 (`header.Debug` / `msgs`) を見るだけでテストできる。

## 将来の拡張ポイント

- `:cheat` のモーダル表示 (builder と同じオーバーレイ) とキー割当併記。
- `:set` への他オプション (折り返し on/off、タイムスタンプ表示 等)。
- 既描画行の `[DEBUG]` 再分類 (元テキストを保持して再パース)。

## 用語

- **Debug 表示**: 子 stdout の `[DEBUG]` 接頭辞行を比較対象から外し別カテゴリ (`kindDebug`) で見せる表示 (`-d` フラグ相当)。
- **command モード**: chat の `:` ex-command line ([024])。`Esc` で入る。

## 関連ドキュメント

- command モード基盤: [024](024-interactive-case-builder.md) / ナビ追加: [027](027-start-problem-navigation.md)
- 利用手引: `docs/tools/atcoder-test-usage.md`
- ロードマップ: `docs/tools/todo.md`
