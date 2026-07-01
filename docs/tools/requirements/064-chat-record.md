# `:record` チャットコマンド (計測・記録の chat 統合) 要件定義

## 概要

`atcoder record` の記録機能を、start 分割画面 / `test --interactive` の chat から `:record` コマンドで呼べるようにする。着手 (`:record start`) / 終端 (`:record stop`) の計測ライフサイクルと、AC / 解説閲覧 / 5 軸スコアの**非対話フラグ記録** (`:record ac score=2,3,2,3,1` 等) を chat から一手で済ませ、解答を編集している画面を離れずに solve-stat を残せるようにする。

CLI `atcoder record` が持つ**逐次プロンプトの対話ウィザード** (AC→解説→5 軸を順に尋ねる) は本要件では chat に載せない。対話フォームは将来 `atcoder record edit` を実装するときに専用の編集画面 (chat 内モーダル) として追加する想定 (下記「スコープ」)。

## 背景・目的

- solve-stat の計測ライフサイクル (要件 061) は「`start` で着手 → `test --submit` 後プロンプト / `record stop` で終端 → `record` で記録」だが、着手後の実作業は chat (start 分割画面の下ペイン / `test --interactive`) の中で行う。計測の開始・終端・記録のためだけに chat を抜けて CLI に戻るのは導線が途切れる。
- chat には既に `:meta` (要件 055/057) / `:gen` (要件 060) という「CLI 相当を chat 内から呼ぶ単発コマンド」の前例がある。`record` も同じ単発フック方式に乗せれば、layer 境界 (internal/ui は solvestat/layout を知らない) を保ったまま chat 統合できる。
- 要件 061 は chat TUI 経路の統合を将来拡張として明記済み (「計測終端 | … | chat TUI (Ctrl+S) 経路への統合」/ Phase 2「chat (Ctrl+S) 経路の AC プロンプト」)。本要件はそのうち**コマンド駆動の記録**を先に実装する (Ctrl+S 提出フローへの AC プロンプト差し込みは引き続き将来拡張)。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 計測開始 | `:record start` (`started_at` 刻印、`restart` で再計測) | — |
| 計測終端 | `:record stop` (`solved_at`/`duration_ms` 確定、`ac`/`time=` 任意) | — |
| 記録 | `:record` に非対話フラグ (`ac`/`noac`/`ed`/`noed`/`score=`/`time=`) を与えて一括記録 | — |
| 現在値の表示 | 引数なし `:record` で solve-stat の現在値を読み取り表示 (書き込まない) | — |
| 対話ウィザード | **スコープ外**。5 軸を順に尋ねる記入 UI は作らない | `record edit` 実装時に chat 内編集画面 (モーダル) として追加 |
| Ctrl+S 提出後の AC プロンプト | **スコープ外** (要件 061 の将来拡張のまま) | 提出準備完了後に AC を尋ねる導線 |
| 対象画面 | start 分割画面の chat / `test --interactive` の chat 両方 | — |
| 対象言語 | Python (solve-stat が `#` コメント) のみ (要件 061 に従う) | 言語別プレフィックス |

### 境界

- **書き込みロジックは新設しない**。chat フックは `cmd/atcoder` 側で solve-stat の読み書き (`internal/solvestat`) と layout 解決を行い、CLI `record` と**同じ挙動**を返す。internal/ui は「フックを呼んで返った行を積む」だけ (`:meta`/`:gen` と同じ層境界)。
- **対話は持ち込まない**。chat の `:record` は 1 行コマンド = 1 回の書き込みで完結する単発操作。不足項目 (与えなかった軸など) は「未記録」のまま残す (CLI 非対話経路と同じ)。
- **解答非破壊**は要件 061 のまま (temp+rename の atomic 書き込み、破損ブロックは停止)。chat 経路もこの書き込み経路を共有するので新たな破壊面は増えない。

## CLI 仕様 (chat コマンド)

chat の command モード (`:` 行) に `:record` を追加する。第 1 トークンでサブコマンドを、以降のトークンで値を指定する。すべて**非対話・同期** (ローカル I/O のみ。`:meta url` の表示・編集と同じく tea.Cmd 非同期にはしない)。

| 入力 | 動作 |
|---|---|
| `:record` | solve-stat の現在値を読み取り、要約行を info で表示する (**書き込まない**) |
| `:record start` | `started_at` を刻む (未記録なら今、既にあれば温存) |
| `:record start restart` | `started_at` を今にリセットし `solved_at`/`duration_ms` をクリア (やり直し練習) |
| `:record stop` | `solved_at` を今に確定、`duration_ms` を算出、`target_ms` をスナップショット |
| `:record stop ac` / `:record stop noac` | 終端に加えて `ac` を記録 |
| `:record stop time=25m` | 実装時間を手動指定して終端 |
| `:record ac` / `:record noac` | `ac` を記録 (完了時刻が未記録なら確定) |
| `:record ed` / `:record noed` | `editorial` (解説閲覧) を記録 |
| `:record score=2,3,2,3,1` | 5 軸 (知識,翻訳,計算量,実装,検証) を一括記録 |
| `:record time=25m` | 実装時間を手動上書きして記録 |
| `:record ac ed score=2,3,2,3,1 time=25m` | 複数フラグを 1 行で一括記録 |

### トークン文法

- **サブコマンド語**: 第 1 トークンが `start` / `stop` のときそのサブコマンド。それ以外 (フラグ or 無し) は記録本体 (`record`)。
- **bool フラグ (bare 語)**: `ac` / `noac` (= AC 可否)、`ed` / `noed` (= 解説閲覧)。相反する 2 語を同時指定するとエラー。
- **key=value**: `score=<k,t,c,i,v>` (各 0〜3 の 5 値)、`time=<dur>` (`25m`, `1h5m`)。
- **`restart`**: `:record start` のときのみ有効な bare 語。

処理ステップ (記録本体 `:record <flags>`):

1. layout 解決 → 解答パス確定。解答ファイルが無ければ「先に `:record start` してください」で error 行。
2. solve-stat ブロックを読む。`solved_at` が未記録なら今に確定し `duration_ms` を `solved_at - started_at` で算出。既に `duration_ms` があれば温存 (壁時計で潰さない)。
3. 与えられたフラグ (`ac`/`editorial`/`score`/`time`) を patch に載せる。`target_ms` を config からスナップショット。
4. solve-stat へキー単位で部分更新 (atomic)。
5. 書き込んだ内容を要約行 (記録先パス / 実装時間・目標比 / ac・editorial / 5 軸) で表示する。

### 出力イメージ

```
:record start
  計測を開始しました: exercise/2026/07/01/abc457_d.py

:record stop
  計測を終了しました: exercise/2026/07/01/abc457_d.py
  実装 23m / 目標 35m (-12m, 達成)
  スコアは :record ac score=… で記録できます。

:record ac ed score=2,3,2,3,1
  記録しました: exercise/2026/07/01/abc457_d.py
  実装 23m / 目標 35m (-12m, 達成)
  ac=true  editorial=true
  score  k=2 t=3 c=2 i=3 v=1

:record
  実装 23m / 目標 35m (-12m, 達成)
  ac=true  editorial=true
  score  k=2 t=3 c=2 i=3 v=1
```

- 表示行の体裁 (実装時間の目標比・要約行) は CLI `record` の `printTimeLine` / `printRecordSummary` と揃える。
- 実装時間が異常値 (負値 / 12h 超) のとき、chat では対話確認を挟めないので**警告行を添えてそのまま記録**する (CLI 非対話経路と同じ安全側)。stderr には出さない (TUI の描画を汚さないため、警告も info/err 行として chat に積む)。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `:record start` (初回) | `started_at` を刻む。「計測を開始しました」 |
| `:record start` (完了前 再実行) | `started_at` 温存 (冪等)。「計測は継続中です」 |
| `:record start` (完了後) | `started_at` 温存 + warning 行 (`restart` を案内)。`restart` 明示時のみリセット |
| `:record stop` / `:record <flags>` (完了確定) | `solved_at` を今に、`duration_ms` 算出、`target_ms` スナップショット |
| `:record` (2 回目以降) | 既存ブロックへキー単位マージ (積み上がらない・部分訂正可) |
| `started_at` 無しで `:record stop` / `:record` | 実装時間は未計測。`time=` があれば採用、無ければ時間系は空で他項目のみ記録 |
| 引数なし `:record` | 現在値を表示のみ (書き込まない) |
| フック未注入 (この画面で使えない) | 「(記録はこの画面では使えません)」を 1 行 (パニックしない) |

- 冪等性・部分更新・解答非破壊・後方互換はすべて要件 061 の solve-stat 書き込み規約をそのまま継承する (chat 経路は同じ `solvestat.Update` を通る)。
- `:record` は同期実行 (ローカル I/O)。`:gen`/`:meta fetch` のようなネットワーク非同期化 (tea.Cmd + DoneMsg) は不要。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `ChatHeader` に `Record func(args []string) (lines []string, err error)` フックを追加 (MetaShow/Gen と同じ層境界の注入点) |
| `internal/ui/chat_casebuilder.go` | `parseCommand` に `case "record"`、`execCommand` に `case "record"`、`execRecord(arg string)` メソッド、cheat 一覧 (`showCheat`) に `:record` 行を追加 |
| `internal/ui/command_complete.go` | `completeNamesBase` に `record`、`completeSubTokens["record"]` に `start`/`stop` を追加 |
| 新規 `cmd/atcoder/chatrecord.go` | `chatRecordFunc(contest, task string) func(args []string) ([]string, error)`。`start`/`stop`/(記録本体) を dispatch し、`buildRecordTarget`/`solvestat`/`resolveDurationMs`/`targetMs` を再利用して行を返す (stderr へ出さない非対話コア) |
| `cmd/atcoder/start.go` | ヘッダ構築に `Record: chatRecordFunc(contestID, task)` を注入 |
| `cmd/atcoder/adhoc.go` | 同上 (`test --interactive` の chat にも注入) |
| `cmd/atcoder/record.go` | (任意) `stampStartedAt` の stderr 警告を返り値化するなど、chat と CLI で warning 文言を共有するリファクタは可 (挙動不変) |
| `internal/ui/chatrecord_test.go` (新規) | `parseCommand("record …")` と `execRecord` の単発フック委譲・エラー/未注入経路のユニットテスト (chatmeta_test.go と同型) |
| `cmd/atcoder/chatrecord_test.go` (新規) | `chatRecordFunc` の start/stop/記録の書き込み挙動テスト (solve-stat のラウンドトリップ) |
| `docs/tools/usage/record.md` | chat `:record` コマンドの節を追記 |
| `docs/tools/todo.md` (AV 節) | chat 統合の進捗を追記し本要件へ相互リンク |

### フック署名 (新規注入点)

```go
// Record は :record コマンドで solve-stat の計測・記録を行うフック。args は :record の
// 第 2 トークン以降 (start/stop/フラグ)。返った行を chat が info/err で積む。書き込み・
// 検証・layout 解決は composition root (cmd/atcoder) に逃がす (MetaShow/Gen と同じ層境界)。
Record func(args []string) (lines []string, err error)
```

- internal/ui は `args []string` を渡すだけで、start/stop/フラグの解釈・solve-stat 書き込みは `cmd/atcoder/chatrecord.go` が握る (層境界の維持)。
- 表示は他のコマンドと同じく「成功なら行を info、失敗なら error を err 行 1 本」。

## エラーハンドリング

| 状況 | 動作 | 表示 |
|---|---|---|
| `score=` の値数が 5 でない / 0〜3 外 | フックが error を返す | err 行 1 本、chat 継続 |
| `time=` がパース不能 | フックが error | err 行 1 本 |
| `ac` と `noac` の同時指定 (`ed`/`noed` も) | フックが error | err 行 1 本 |
| 解答ファイルが無い (stop / 記録) | フックが error | 「先に `:record start` してください」 |
| solve-stat ブロックが破損 | フックが error (自動修復せず停止) | err 行 1 本 |
| 書き込み I/O 失敗 | フックが error | err 行 1 本 |
| 実装時間が異常値 | 警告行を添えてそのまま記録 (対話確認は挟めない) | warning + 要約行、記録は成功 |
| フック未注入 | 「(記録はこの画面では使えません)」 | info 行 1 本 |
| 未知トークン | フックが error | err 行 1 本 |

- chat コマンドは exit code を持たない (TUI 継続) が、フックの error は「操作失敗を 1 行で伝えて継続」に写す。CLI の exit 2/1 相当の区別は chat では設けず、いずれも err 行で表示する。

## 非機能要件

- **層境界の維持**: internal/ui は solvestat/layout/config を知らない。`Record` フックで cmd/atcoder に逃がす (Submit/Edit/Meta/Gen と同じ)。
- **解答非破壊・冪等・後方互換・前方互換**: 要件 061 の solve-stat 書き込み規約をそのまま継承 (同じ `solvestat.Update` を通る)。
- **TUI 非破壊**: 記録処理は stderr に出さない (CLI が stderr に出す warning は chat では info/err 行に写す)。bubbletea の描画を壊さない。
- **オフライン**: 記録はローカルのみ。ネットワーク/認証に触れない (AC は自己申告)。
- **同期・軽量**: ローカル I/O のみなので tea.Cmd 非同期化は不要。

## 将来の拡張ポイント

- **`record edit` の chat 編集画面**: 5 軸スコアを順に見ながら訂正する対話フォーム (chat 内モーダル)。本要件が非対話フラグで残した「対話ウィザード」を埋める。
- **Ctrl+S 提出後の AC プロンプト**: 提出準備完了後に AC を尋ねて `solved_at`/`ac` を確定する導線 (要件 061 の将来拡張)。
- **ヘッダの経過タイマー表示**: `started_at` を基点に chat/watch ヘッダで経過時間を刻む (要件 061 のタイマー G)。

## 用語

- **solve-stat ブロック / 実装時間 / 正答状況 / 5 軸スコア / 目標時間**: 要件 061 の定義に準拠。
- **単発フック方式**: chat の 1 コマンドが composition root の 1 関数を呼び、返った行を積む方式 (`:meta`/`:gen` の前例)。
- (`contest_id` = `abc457` / `task_id` = `abc457_d` / `letter` = `d` は要件 002 に準拠)

## 関連ドキュメント

- `docs/tools/requirements/061-solve-record-stats.md` (`record` 本体・solve-stat スキーマ・目標時間・chat 統合を将来拡張として明記)
- `docs/tools/requirements/055-chat-meta-edit.md` / `057-chat-meta-fetch.md` / `060-gen-random-input.md` (chat 単発コマンドの前例・層境界)
- `docs/tools/usage/record.md` (利用手引) / `docs/tools/todo.md` の **AV.** (ロードマップ)
- `CLAUDE.md` (worktree 必須・chat コマンド `:gen` の言及)
</content>
</invoke>
