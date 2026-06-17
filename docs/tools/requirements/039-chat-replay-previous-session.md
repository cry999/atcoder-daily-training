# インタラクティブ chat に前回セッション入力のリプレイ `:replay` を追加 要件定義

## 概要

インタラクティブ chat の vim 風 command モード ([024](024-interactive-case-builder.md)) に **`:replay`** を足す。子 (解答プログラム) へ送った入力行を、**子をリスタートしてクリーンな状態から順に再送**し、直前の実行を再現する。再生対象は **直前の 1 (child) セッション分の手入力** — 現セッションの手入力を優先し、(reload 直後など) 現セッションが空なら直前に完了したセッション、いずれも空なら前回 chat 起動の入力 (cross-run フォールバック) にフォールバックする。**起動を通した手入力すべての累積ではない。** cross-run フォールバックのため、chat の手入力を**起動をまたいで永続化**する新パッケージ `internal/chatlog` を追加する (利用統計 `internal/usagelog` ([037](037-usage-telemetry.md)) と同じ JSONL 追記方式)。新フラグ・新サブコマンドは増やさず、永続化は composition root が ChatHeader 経由で注入する。

> **追記 (再生対象の修正)**: 初版は「**前回セッション (別の起動回) の入力のみ**」を再生対象にしていたが、主用途である「**コードを直して同じ入力を流し直す**」(= 今回の起動中に打った入力の再送) を拾えず、初回起動では常に「入力がありません」になっていた。再生対象を **今回の起動で送った入力 (`runInputs`) を優先し、未入力なら前回セッション (`PrevInputs`) にフォールバック**する形に変更した。これでコード修正後の再送と、開いた直後の前回続行の両方をカバーする。永続化の仕組み (`internal/chatlog`・JSONL・注入) は不変。

> **追記 (再生行を記録しない修正)**: 上記変更の初版は `:replay` の再送行も `runInputs`・chatlog に積んでいたため、**前回フォールバックや以前の `:replay` で流れた行が `runInputs` に蓄積**し、次の `:replay` がそれらを巻き込んで膨らんだ (手入力したセッションではなく、過去のサンプル/テストケース値を流してしまう症状)。`submitLines` に `record bool` を足し、**手入力 (Enter/ペースト) のみ `record=true`、`:replay` の再送は `record=false`** とした。`record=false` では手入力集合 (sessionInputs) への追加と `RecordInput` (chatlog 永続化) を行わず、子への送信・echo・`history`・出力待ちはそのまま。これで再生が膨らまない。

> **追記 (セッション単位へのスコープ修正)**: 上記までは「今回の起動 (`RunChat` 1 回) で送った手入力すべて」を 1 つの `runInputs` に貯めて再生していたが、これは**子リスタート (watch reload / Ctrl+D リセット) をまたいだ全入力**であり、ユーザは「**直前の (child) セッション 1 つ分だけ**」を期待していた (例: セッション1 で `A B`、セッション2 で `C D` を打つと、`:replay` が `A B C D` 全部を流す)。`runInputs` を廃止し、再生対象を **child セッション単位**に変更: 現セッションの手入力 `sessionInputs` → 直前に完了したセッション `prevSessionInputs` → 前回起動 `PrevInputs` (cross-run) の順 (`replayLines()`)。子リスタート時に `beginNewSession()` が直前セッションの手入力を `prevSessionInputs` へ退避する (空セッションでは上書きしない)。`sessionInputs` は `record=true` の手入力のみを溜め、子リスタートでリセットされる。これで「直前のセッションのみ」を再生する。

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
| `:replay` の対象 | **直前の 1 (child) セッション分**。現セッションの手入力 (`sessionInputs`) → 直前セッション (`prevSessionInputs`) → 前回起動 (`PrevInputs`) の順。起動を通した累積ではない | N 個前のセッション選択・複数セッション結合 |
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
| `:replay` | 直前の 1 (child) セッション分の手入力 (現セッション→直前セッション→前回起動) を、子をリスタートしてクリーンな状態から順に再送する |

- 補完 (要件 [031](031-command-mode-completion.md)): canonical 名 `replay` を常時候補に出す (`NavEnabled` に依らない)。引数を取らないので末尾空白は足さない。
- 別名は設けない (`:re` から Tab 補完で確定できる。vim の `:r` (ファイル読込) と紛れないよう短縮形は避ける)。

### `:replay` の動作

1. command モードを抜けて元のモード (builder 中なら builder、ふだんは insert) に戻る。
2. 再生対象を `replayLines()` で決める: **現セッションの手入力 (`m.sessionInputs`)** → **直前に完了したセッション (`m.prevSessionInputs`)** → **前回起動 (`m.header.PrevInputs`)** の順。すべて空なら info 行 `(再生できる入力がありません …)` を 1 本積んで終了 (子は起動しない)。
3. 対象をスナップショットする (直後の `restart()` が `sessionInputs` を退避・リセットするため)。
4. 子を **`restart()`** で作り直す (動作中の子も Kill して新規 spawn。`beginNewSession()` が直前セッションの手入力を `prevSessionInputs` に退避し `sessionInputs` をリセット。`─── session #N ───` 区切りが出る)。spawn 失敗時はそこで終了。
5. リスタート後のクリーンな子へ、対象入力行を `submitLines(snap, cmds, record=false)` で**順に送信**する (各行を stdin へ書き、kindIn として echo、出力待ちスピナーを 1 回起動)。**`record=false` なので再生行は `sessionInputs` にも chatlog にも積まない** — 積むと次の `:replay` が再生行を巻き込んで膨らむ。`history`/echo は子へ実際に送った記録として従来どおり積む。

### 永続化の注入 (composition root)

`internal/ui` は filesystem/XDG を知らない。`Submit`/`Edit` ([038](038-start-edit-in-editor.md)) と同じく ChatHeader にフックを注入する:

```go
// ChatHeader へ追加
PrevInputs  []string          // 同じ問題の前回セッション入力 (root が chatlog.LoadLastSession で先読み)
RecordInput func(line string) // 手入力の各行を永続化するフック (非 nil なら submitLines が record=true 時に呼ぶ。:replay 再送では呼ばない)
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
| `:replay` (現セッションに手入力あり) | その現セッション分を再生 (直前セッション/前回起動より優先)。コード修正後の再送の主用途 |
| `:replay` (現セッション空・直前セッションあり) | 直前に完了したセッション分を再生 (reload 直後の続行) |
| 複数の子セッションをまたいだ後 | **直前の 1 セッション分のみ**を再生 (起動を通した全手入力の累積ではない) |
| `:replay` (insert) | 子をリスタートして対象入力を順送。insert に戻る |
| `:replay` (builder 中) | builder に戻ってから再生する (builder は破棄しない。`:set`/`:debug` と同じ復帰) |
| `:replay` (どのセッションにも入力なし) | info 行 1 本のみ。子は起動しない (初回起動で未入力の状態) |
| `:replay` (`ATCODER_NO_CHAT_HISTORY` 有効) | 永続化しないので cross-run の `PrevInputs` は常に空。ただし**今回の起動で打った入力 (現/直前セッション) はメモリ上で再生できる** (無効化の対象外) |
| 子が動作中に `:replay` | リスタート (現在の子を Kill して新規 spawn) してから再生 |
| 再生中に届く出力 | 通常の stdout/stderr として表示・ライブ検証 ([024]) も従来どおり working |
| 同一セッションで複数回 `:replay` | 再生は `record=false` で `sessionInputs` を変えないので膨らまない。何度でも同じ手入力分を流せる |
| `contest`/`task` が空 (識別不能) | 永続化は no-op で `PrevInputs` は空。今回の現/直前セッションの再生は可能 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/chatlog/chatlog.go` | **新規**。`Path`/`Dir`/`Disabled`/`NewSessionID`/`Record`/`LoadLastSession` と `Event` 型。`usagelog` の XDG データ領域・JSONL 追記・無効化規約を踏襲 |
| `internal/chatlog/chatlog_test.go` | **新規**。2 セッション追記 → `LoadLastSession` が直近セッションのみ順序保持で返す roundtrip、無効化時に書かない、`XDG_DATA_HOME` でパスが切替、空 contest/task は no-op、壊れ行スキップ |
| `internal/ui/chat.go` | `ChatHeader` に `PrevInputs []string` / `RecordInput func(string)` を追加。`chatModel` に `sessionInputs`(現セッションの手入力) と `prevSessionInputs`(直前に完了したセッションの手入力) を持つ。`beginNewSession()` (restart で直前セッションを退避) と `replayLines()` (現→直前→前回起動の選択) を追加。`submitLines` に `record bool` を足し、`record=true` の手入力のみ `sessionInputs`/`RecordInput` に積む (`:replay` 再送=false) |
| `internal/runner/python.go` | `ChatHandle.Kill`/`Wait` を nil cmd に対し防御的に no-op 化 (実プロセスを持たない handle で panic しない。テストで restart 経路を駆動可能に) |
| `internal/ui/chat_casebuilder.go` | `parseCommand` に `replay` を追加。`execCommand` に `case "replay"`。`execReplay` ヘルパ (`replayLines()` で対象選択・`submitLines(..., record=false)` で再送) を追加。`newCommandInput` placeholder と `showCheat` に `:replay` を追記 |
| `internal/ui/command_complete.go` | `completeNamesBase` に `replay` を追加 (引数なしなので `completeExpectsArg` には入れない) |
| `internal/ui/command_complete_test.go` | 候補一覧の期待値に `replay` を反映。`:re`→`replay` 確定のケースを追加 |
| `internal/ui/chatreplay_test.go` | **新規/回帰**。`execReplay` の各分岐、`record=false` で再生行を `sessionInputs`/chatlog に積まないこと、**複数セッションをまたいでも直前の 1 セッションだけを流すこと** (`TestReplayScopedToPreviousSession`)、`beginNewSession`/`replayLines` の単体 (`TestSessionRotationAndReplayLines`) を fake spawner で検証 |
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
