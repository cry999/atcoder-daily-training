# インタラクティブ chat に前回セッション入力のリプレイ `:replay` を追加 要件定義

## 概要

インタラクティブ chat の vim 風 command モード ([024](024-interactive-case-builder.md)) に **`:replay`** を足す。子 (解答プログラム) へ送った入力行を、**子をリスタートしてクリーンな状態から順に再送**し、直前の実行を再現する。再生対象は **今回の起動で送った入力を優先し、まだ何も送っていなければ前回セッションの入力にフォールバック**する。これを成立させるため、chat の入力行を**セッションをまたいで永続化**する新パッケージ `internal/chatlog` を追加する (利用統計 `internal/usagelog` ([037](037-usage-telemetry.md)) と同じ JSONL 追記方式)。新フラグ・新サブコマンドは増やさず、永続化は composition root が ChatHeader 経由で注入する。

> **追記 (再生対象の修正)**: 初版は「**前回セッション (別の起動回) の入力のみ**」を再生対象にしていたが、主用途である「**コードを直して同じ入力を流し直す**」(= 今回の起動中に打った入力の再送) を拾えず、初回起動では常に「入力がありません」になっていた。再生対象を **今回の起動で送った入力 (`runInputs`) を優先し、未入力なら前回セッション (`PrevInputs`) にフォールバック**する形に変更した。これでコード修正後の再送と、開いた直後の前回続行の両方をカバーする。永続化の仕組み (`internal/chatlog`・JSONL・注入) は不変。

## 背景・目的

- 対話で解答をデバッグしていると、毎回**同じ入力列を手で打ち直す**ことになる。サンプル入力や再現手順を一度通したら、次に chat を開いたとき (コード修正後の再確認・別日の再開) ワンコマンドで同じ入力を流し直したい。
- chat の入力履歴は現状 `chatModel.history` / `sessionInputs` に**メモリ上だけ**保持され、chat を閉じると消える ([chathistory_test.go] は Up/Down 履歴のテストで、これも揮発)。セッションをまたいだ再利用の仕組みが無い。
- 既に `internal/usagelog` ([037](037-usage-telemetry.md)) が「セッション横断のローカルデータを JSONL で追記する」前例を確立している。同じ規約 (XDG データ領域・環境変数で無効化・best-effort 非 fatal) に乗せれば、新しい設計判断を増やさずに永続化できる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 保存キー | **問題ごと** (contest+task)。`cachepath.Task` と同じ (contest, task) を鍵にする | per-解答ファイルハッシュ / コード版数別 |
| 保存内容 | 子 stdin へ送った**入力行のみ** (insert の Enter・複数行ペースト [035] の各行)。command モードのコマンド (`:case` 等) は保存しない | 出力・タイムスタンプ込みの完全トランスクリプト |
| 「セッション」の単位 | **1 回の chat 起動 = 1 セッション** (`RunChat` 1 回)。セッション内の子リスタート (watch reload / Ctrl+D リセット / `Ctrl+C`) は同一セッション扱い | セッション一覧からの選択再生 |
| `:replay` の対象 | **今回の起動で送った入力 (`runInputs`)** を優先。未入力なら**直近の (= 前回の) セッション (`PrevInputs`)** にフォールバック | N 個前のセッション選択・複数セッション結合 |
| 再生方法 | 子を**リスタート**してクリーンな状態から対象入力を順送 | 現セッションへの追送モード・1 行ずつステップ実行 |
| 無効化 | 環境変数 `ATCODER_NO_CHAT_HISTORY` が非空なら保存しない (= `:replay` で何も無い) | 設定ファイルキー |

### 境界

- 子プロセス・判定・exit code・`Ctrl+C`/`Ctrl+D`/`Ctrl+S`/`Ctrl+E`・既存コマンド (`:case`/`:w`/`:set`/`:debug`/`:cheat`/`:q`/`:task`/`:contest`/`:e`) は不変。
- stdout には何も書かない (chat 内の info 行と、子への stdin 送信のみ)。バッチ `test`/`run` 経路 (`runexec`/`testexec`) には触れない。
- 保存は **`$XDG_DATA_HOME`** 配下 (利用統計と同じデータ領域)。キャッシュ (`$XDG_CACHE_HOME` のサンプル・meta) とは分ける — 入力履歴はユーザ由来で再生成不能なため、消えてよいキャッシュには置かない。

## ディレクトリ構造 / スキーマ

`internal/usagelog` と同じデータ領域・同じ JSONL 追記。保存先はパッケージ `internal/chatlog`:

```
$XDG_DATA_HOME/atcoder-tools/chat-history/<contest>/<task>.jsonl
  (XDG_DATA_HOME 未設定時は ~/.local/share、最終 fallback ./.local/share)
```

JSONL 1 行 = 1 入力行イベント:

```json
{"ts":"2026-06-17T10:30:15.123+09:00","session":"<session-id>","text":"5 3"}
```

| フィールド | 型 | 内容 |
|---|---|---|
| `ts` | RFC3339Nano | 送信時刻 |
| `session` | string | chat 起動ごとの一意 ID (時刻ベース)。同一 session の行が 1 セッション分 |
| `text` | string | 子 stdin へ送った 1 行 (空行も保存する — 空 Enter も再現対象) |

> 空文字 (`""`) の入力行も保存・再生する。空 Enter で空行を読む解答があるため、忠実な再現には空行も流す必要がある。

## CLI / TUI 仕様

新フラグ無し。すべて command モード (insert で `Esc` → `:`) の内側。

### コマンド一覧 (追加分)

| コマンド | 動作 |
|---|---|
| `:replay` | 今回の起動で送った入力 (無ければ同じ問題の前回セッションの入力) を、子をリスタートしてクリーンな状態から順に再送する |

- 補完 (要件 [031](031-command-mode-completion.md)): canonical 名 `replay` を常時候補に出す (`NavEnabled` に依らない)。引数を取らないので末尾空白は足さない。
- 別名は設けない (`:re` から Tab 補完で確定できる。vim の `:r` (ファイル読込) と紛れないよう短縮形は避ける)。

### `:replay` の動作

1. command モードを抜けて元のモード (builder 中なら builder、ふだんは insert) に戻る。
2. 再生対象を決める: **今回の起動で送った入力 (`m.runInputs`)** を優先し、空なら **前回セッション入力 (`m.header.PrevInputs`)** にフォールバックする。どちらも空なら info 行 `(再生できる入力がありません …)` を 1 本積んで終了 (子は起動しない)。
3. 対象をスナップショットし、`m.runInputs` をクリアする (4 の `submitLines` が再生行を `runInputs` に積み直すため。二重化を防ぎ、再生後の `runInputs` は再生分そのものに揃う)。
4. 子を **`restart()`** で作り直す (動作中の子も Kill して新規 spawn。`─── session #N ───` 区切りが出る)。spawn 失敗時はそこで終了。
5. リスタート後のクリーンな子へ、対象入力行を `submitLines` で**順に送信**する (各行を stdin へ書き、kindIn として echo、出力待ちスピナーを 1 回起動)。再生行は `history`/`sessionInputs`/`runInputs` に積まれ `RecordInput` フックでも永続化される。

### 永続化の注入 (composition root)

`internal/ui` は filesystem/XDG を知らない。`Submit`/`Edit` ([038](038-start-edit-in-editor.md)) と同じく ChatHeader にフックを注入する:

```go
// ChatHeader へ追加
PrevInputs  []string          // 同じ問題の前回セッション入力 (root が chatlog.LoadLastSession で先読み)
RecordInput func(line string) // 子へ送った各行を永続化するフック (非 nil なら submitLines が各行で呼ぶ)
```

composition root (test --interactive: `makeChatRunner` / start 分割画面: `buildTarget`) で問題ごとに:

```go
sid := chatlog.NewSessionID()
prev, _ := chatlog.LoadLastSession(contest, task)        // 先読み (この時点では今回分は未記録なので「前回」が返る)
header.PrevInputs  = prev
header.RecordInput = func(line string) { _ = chatlog.Record(contest, task, sid, line) }
```

start 分割画面は `buildTarget` が問題ごとに ChatHeader を組むため、`:task`/`:contest`/`:e` で別問題へ移ると、その問題の `PrevInputs` と新しい session ID が自然に割り当たる。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `:replay` (今回入力あり) | 今回の起動で送った入力を再生 (PrevInputs より優先)。コード修正後の再送の主用途 |
| `:replay` (今回未入力・前回入力あり) | 前回セッションの入力にフォールバックして再生 (開いた直後の続行) |
| `:replay` (insert) | 子をリスタートして対象入力を順送。insert に戻る |
| `:replay` (builder 中) | builder に戻ってから再生する (builder は破棄しない。`:set`/`:debug` と同じ復帰) |
| `:replay` (今回も前回も入力なし) | info 行 1 本のみ。子は起動しない (初回起動で未入力の状態) |
| `:replay` (`ATCODER_NO_CHAT_HISTORY` 有効) | 永続化しないので PrevInputs は常に空。ただし**今回の起動で打った入力は `runInputs` で再生できる** (メモリ上の保持は無効化の対象外) |
| 子が動作中に `:replay` | リスタート (現在の子を Kill して新規 spawn) してから再生 |
| 再生中に届く出力 | 通常の stdout/stderr として表示・ライブ検証 ([024]) も従来どおり working |
| 同一起動で複数回 `:replay` | 3 で `runInputs` を再生分に揃えるので二重化しない。何度でも同じ入力を流せる |
| `contest`/`task` が空 (識別不能) | 永続化は no-op で PrevInputs は空。今回の `runInputs` 再生は可能 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/chatlog/chatlog.go` | **新規**。`Path`/`Dir`/`Disabled`/`NewSessionID`/`Record`/`LoadLastSession` と `Event` 型。`usagelog` の XDG データ領域・JSONL 追記・無効化規約を踏襲 |
| `internal/chatlog/chatlog_test.go` | **新規**。2 セッション追記 → `LoadLastSession` が直近セッションのみ順序保持で返す roundtrip、無効化時に書かない、`XDG_DATA_HOME` でパスが切替、空 contest/task は no-op、壊れ行スキップ |
| `internal/ui/chat.go` | `ChatHeader` に `PrevInputs []string` / `RecordInput func(string)` を追加。`chatModel` に `runInputs []string` (今回起動分の入力。子リスタートをまたいで保持) を追加。`submitLines` が各送信行を `runInputs` に積み、`RecordInput` を呼ぶ (非 nil 時) |
| `internal/ui/chat_casebuilder.go` | `parseCommand` に `replay` を追加。`execCommand` に `case "replay"`。`execReplay` ヘルパ (今回入力優先・前回フォールバック・二重化防止のスナップショット) を追加。`newCommandInput` placeholder と `showCheat` に `:replay` を追記 |
| `internal/ui/command_complete.go` | `completeNamesBase` に `replay` を追加 (引数なしなので `completeExpectsArg` には入れない) |
| `internal/ui/command_complete_test.go` | 候補一覧の期待値に `replay` を反映。`:re`→`replay` 確定のケースを追加 |
| `internal/ui/chatreplay_test.go` | **新規**。`parseCommand("replay")`、`execReplay` (入力なし=info のみ・子未起動 / 今回入力優先 / 前回フォールバックで spawn して各行送信) を fake spawner で検証 |
| `internal/ui/chatreplaywiring_test.go` | **新規 (回帰)**。composition root どおり 2 回の起動を再現し、起動をまたいだ `PrevInputs` 先読みが機能することを確認 |
| `cmd/atcoder/adhoc.go` | `makeChatRunner` で `chatlog` を結線 (session ID 生成・`LoadLastSession` 先読み・`RecordInput` 注入)。鍵は `TaskDir` と同じ捕捉済み `contest, task` |
| `cmd/atcoder/start.go` | `buildTarget` で同様に結線 (問題ごと = ナビ再ターゲットごとに `PrevInputs`/session が更新される) |
| `docs/tools/atcoder-test-usage.md` / `atcoder-start-usage.md` | command モードのコマンド表に `:replay` を追記 |
| `docs/tools/todo.md` | ロードマップ項目 (AF) を追記し本要件へ相互リンク |

### 新規パッケージの素描

```go
// internal/chatlog (package chatlog)
const AppName = "atcoder-tools"
const DisableEnv = "ATCODER_NO_CHAT_HISTORY"

type Event struct {
    TS      time.Time `json:"ts"`
    Session string    `json:"session"`
    Text    string    `json:"text"`
}

func Disabled() bool                                   // ATCODER_NO_CHAT_HISTORY が非空
func Dir() string                                      // $XDG_DATA_HOME/atcoder-tools/chat-history
func Path(contest, task string) string                 // Dir/<contest>/<task>.jsonl
func NewSessionID() string                             // 時刻ベースの一意 ID
func Record(contest, task, session, text string) error // JSONL 追記。Disabled / 空キーなら no-op
func LoadLastSession(contest, task string) ([]string, error) // 直近 session の text を順序保持で返す
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| 保存 (`Record`) の失敗 (権限・I/O) | best-effort で error を返すが呼び出し側 (フック) は無視 (non-fatal)。chat は継続 (`usagelog` と同じ) |
| 先読み (`LoadLastSession`) の失敗 | 空スライスとして扱い、`:replay` は「ありません」info (chat は継続) |
| JSONL の壊れ行 | スキップして読み進める (best-effort) |
| `:replay` 中の spawn 失敗 | 既存 `restart()` の spawn 失敗経路どおり (err 行 + `tea.Quit`)。引数誤りではないので exit code 規約には影響しない |
| exit code | 影響なし (表示と stdin 送信のみ。引数誤り=2 / 実行時失敗=1 / 成功=0 は不変) |

## 非機能要件

- **既存非破壊**: 既存コマンド・キー・判定・chat の描画は不変。`:replay` を打たない限り従来どおり。`RecordInput` 未注入 (フック nil) なら `submitLines` は従来挙動。
- **stdout 非汚染**: 表示は chat 内の info 行のみ。永続化はデータ領域のファイルへ。
- **ネットワーク非依存**: ローカルファイルのみ。AtCoder へは一切出さない (`usagelog` と同じ)。
- **best-effort / 非 fatal**: 保存・先読みの失敗は chat 本体を止めない。
- **前方互換**: JSONL は 1 行 = 1 イベントの追記専用。フィールド追加 (出力・コード版数等) は後方互換に足せる。
- **決定的にテスト可能**: `chatlog` は (contest, task, session, text) → ファイルの純粋な追記/読込でテストできる (`usagelog_test.go` と同型)。`parseCommand` は純粋関数のまま、`execReplay` は fake spawner で送信行を検証できる。
- **スモーク**: 本機能は TUI/永続化で `atcoder test` の判定 exit code 経路を増やさないため、fixture (`fixtures/run.sh`) は新規追加せず**既存スモークが緑のまま**を確認する。挙動は `internal/chatlog` と `internal/ui` の Go ユニットテストで固定する。

## 将来の拡張ポイント

- N 個前のセッション選択 (`:replay <n>`) / セッション一覧表示。
- 1 行ずつステップ実行 (確認しながら再生) / 現セッションへの追送モード。
- 出力込みの完全トランスクリプト保存と差分表示。
- 解答コード版数 (ハッシュ) を session に紐づけ、「このコードで通した入力」を引く。

## 用語

- **セッション**: 1 回の chat 起動 (`RunChat` 1 回)。内部の子リスタートは同一セッション。
- **command モード**: chat の `:` ex-command line ([024](024-interactive-case-builder.md))。`Esc` で入る。
- **入力行**: insert の Enter / 複数行ペースト ([035](035-chat-multiline-paste.md)) で子 stdin へ送った 1 行。

## 関連ドキュメント

- command モード基盤: [024](024-interactive-case-builder.md) / コマンド追加の前例: [030](030-chat-debug-cheat-commands.md) / 補完: [031](031-command-mode-completion.md)
- フック注入の前例: [038](038-start-edit-in-editor.md) (`Edit`) / 提出 (`Submit`)
- 永続化の前例 (JSONL・XDG データ領域・無効化): [037](037-usage-telemetry.md) (`internal/usagelog`)
- 利用手引: `docs/tools/atcoder-test-usage.md` / `docs/tools/atcoder-start-usage.md`
- ロードマップ: `docs/tools/todo.md`
</content>
</invoke>
