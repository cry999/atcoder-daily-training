# chat 内からの提出準備 (`Ctrl+S`) 要件定義

## 概要

インタラクティブ chat (`atcoder test --interactive` / `atcoder start` → `i`) の中から、**`Ctrl+S` キー一発**で提出準備 (`test --submit` 相当) を起動できるようにする。提出準備＝**解答ファイルをクリップボードへコピー + 提出ページをブラウザで起動**で、`test --submit` と同じ `prepareSubmission` の中身を再利用する (**実 POST はしない** — 認証は Cloudflare Turnstile 保護で programmatic 不可、todo.md「K」)。chat を抜けずにその場で実行でき、**走行中の子プロセスは kill しない**。新サブコマンド・新フラグは増やさず、chat の予約キーを 1 つ足すだけ。

## 背景・目的

- chat で対話的に挙動を確かめて「よし提出だ」となったとき、今は一度 chat を抜けて (`Ctrl+D`)、ブラウザを自分で開くか `atcoder test --submit` を別途叩く必要がある。`test --submit` は**サンプルモード専用で `--interactive` と併用不可** (`exit 2`) なので、対話中からは使えない。
- `start` → `i` → chat という入れ子で対話していると、提出のためだけに chat を畳むのは編集リズムを切る。「対話で確かめる → そのまま提出準備」が 1 画面で完結するのが自然。
- 提出準備の中身 (`prepareSubmission`: コピー + ブラウザ起動) は既にあり、chat から呼ぶ口を足すだけで済む。実 POST を伴わないので副作用は軽い (クリップボード上書き + ブラウザのタブが 1 つ開く)。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| トリガー | chat 内の予約キー **`Ctrl+S`** | 024 のコマンドモード実装後に `:submit` / `:s` を同 action のエイリアスに |
| 動作 | 解答ファイルをコピー + 提出ページをブラウザ起動 (`prepareSubmission` の中身) | — |
| サンプルゲート | **無し** (chat はバッチ判定が走っていない) | `Ctrl+S` の前に公式サンプルを 1 回回して緑のときだけ準備する option |
| 実 POST | しない (ブラウザに委ねる) | Turnstile を解けるブラウザ自動化が前提。当面不可 (K) |
| `--no-open` 相当 | MVP は常にブラウザを開く | config キー (`[submit] no_open`) で制御 |
| 子プロセス | kill しない・chat 継続 | — |
| 適用範囲 | `test --interactive` と `start` → `i` の chat (両方 `runAdHoc` 経由) | — |

### 024 (ケースビルダー) との関係

024 は chat に **vim 風コマンドモード (`Esc` → `:case` 等)** を導入する未実装の大きめ要件。本要件はそれに依存せず、**独立した予約キー `Ctrl+S`** で submit を実現する。理由:

- 024 のコマンドモードはモーダル UI・`tests-extra/` 保存・ライブ検証まで含む大きな設計で、submit のためだけに先取り実装すると重複・競合のリスクがある。
- `Ctrl+S` は bubbletea が `tea.KeyCtrlS` として受信でき、現状 chat で未使用 (使用済みは `Ctrl+C`=中断再起動 / `Ctrl+D`=終了 / `Enter`=送信 / `Up`/`Down`=履歴)。
- 024 が入ったら、コマンドモードに `:submit` / `:s` を足して**同じ submit コールバックを呼ぶ**だけでよい (キーとコマンドの二経路が同一動作に集約)。

## CLI 仕様

新フラグ・新サブコマンドは**追加しない**。chat 内のキー操作が 1 つ増える。

```
atcoder test <contest> --task <task> --interactive   # chat 中に Ctrl+S で提出準備
atcoder start <contest> --task <task>  → i → chat    # 同上
```

### chat のキー (追加分)

| キー | 動作 |
|---|---|
| **`Ctrl+S`** | 提出準備: 解答をクリップボードへコピー + 提出ページをブラウザで開く。結果を chat に 1 行表示。子は kill しない・chat に留まる |

(既存: `Enter`=送信 / `Ctrl+C`=中断・再起動 / `Ctrl+D`=終了 / `Up`/`Down`=履歴)

### 処理ステップ (`Ctrl+S` 押下時)

1. chat が注入された submit コールバック (`ChatHeader.Submit`) を呼ぶ。
2. コールバック (composition root = `adhoc.go` 側) が `submitPrepCore(contest, task, lay)` を実行:
   - 解答ファイルを読み、クリップボードへ書く。
   - 提出 URL (`https://atcoder.jp/contests/<contest>/submit?taskScreenName=<task>`) を組み、ブラウザで開く (best-effort)。
   - 結果 (コピーしたパス・URL・ブラウザを開けたか・エラー) を返す。
3. chat は結果を `chatLine` として 1 行表示する (成功=`info`、失敗=`err`)。**stdout へ直接 print しない** (TUI を壊すため)。
4. chat はそのまま継続 (子も TUI も維持)。

### 出力イメージ (chat 画面内の 1 行)

```
> 3
< 6
(提出準備: クリップボードにコピー abc457/d.py / 提出ページを開きました)
```

失敗時:

```
(提出準備に失敗: 解答ファイルの読み込みに失敗しました: ...)
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| サンプルゲート | **無し**。chat submit は無条件にコピー + ブラウザ起動 (対話中はバッチ判定が走らないため)。`test --submit` (ゲートあり) と意図的に挙動が異なる |
| 子プロセス | kill しない。submit は副作用アクションで chat セッションは継続 (024 の「コマンドモードは子を触らない」原則と整合) |
| 入れ子 | `start` → `i` → chat → `Ctrl+S` → (chat に留まる) → `Ctrl+D` → start watch。submit は chat 内で完結し、start ループにも子にも触らない。auto-restart 中でも押せる |
| クリップボード失敗 | エラー行を表示して chat 継続 (致命的でない) |
| ブラウザ起動失敗 | コピーは済んでいるので、URL を含む案内行を表示して chat 継続 |
| `Submit` 未注入 (nil) | `Ctrl+S` は「提出準備は利用できません」を 1 行表示 (基本は常に注入されるので通常起きない) |
| TUI 安全性 | コールバックは stdout に print しない。clipboard 書き込み・`openBrowser` (exec の `Start`・非ブロッキング) は TUI を壊さないので同期実行し、結果は `chatLine` で描画 |
| 解答ファイル | **読むだけ**。submit は解答にもキャッシュにも書き込まない |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `ChatHeader` に `Submit SubmitFunc` 追加。`SubmitFunc` 型と `SubmitResult` 構造体を定義。`Update` の `tea.KeyMsg` に `case tea.KeyCtrlS` を足し、コールバックを呼んで結果を `chatLine` 化。入力 placeholder / 初期 info 行に「Ctrl+S で提出準備」を追記 |
| `cmd/atcoder/submitprep.go` | `prepareSubmission` から**非印字 core** `submitPrepCore(contest, task, lay) submitOutcome` を切り出す。CLI 経路 (`test --submit`) は core + 印字、chat 経路は core + 行描画 |
| `cmd/atcoder/adhoc.go` | `interactive` 時に `ui.SubmitFunc` クロージャ (contest/task/lay を捕捉) を構築し `ChatHeader.Submit` に注入 (`test --interactive` と `start`→`i` の両方をここでカバー) |
| `internal/ui/chat_test.go` | `Ctrl+S` で `Submit` が呼ばれ結果行が追加されることを、スタブ `SubmitFunc` で検証 (TUI を起動せず model の `Update` に `tea.KeyMsg{Type: tea.KeyCtrlS}` を送る) |
| `cmd/atcoder/submitprep_test.go` | `submitPrepCore` の URL / 解答パス組み立てを単体検証 (ブラウザは開かない経路) |
| `docs/tools/atcoder-test-usage.md` / `atcoder-start-usage.md` | interactive 節に `Ctrl+S` = 提出準備を追記 |
| `docs/tools/todo.md` | 本機能の項目を追加し DONE マーク。`abc-todo.md`「C. 提出」とも相互リンク |

### 新規 API スケッチ (`internal/ui`)

```go
// SubmitResult は chat からの提出準備の結果。chat はこれを 1 行に整形して表示する。
type SubmitResult struct {
    Message string // 表示文 (例 "クリップボードにコピー abc457/d.py / 提出ページを開きました")
    IsError bool   // true なら err 行で表示
}

// SubmitFunc は chat の Ctrl+S で呼ばれる提出準備フック。
// internal/ui は cmd/atcoder を import できないため、composition root が注入する。
type SubmitFunc func() SubmitResult

// ChatHeader に追加:
//   Submit SubmitFunc // nil 可 (nil のとき Ctrl+S は「利用できません」を表示)
```

```go
// cmd/atcoder 側 (submitprep.go):
type submitOutcome struct {
    CopiedPath string
    URL        string
    Opened     bool
}
// submitPrepCore は印字せずに副作用 (コピー + ブラウザ起動) を行い結果を返す。
func submitPrepCore(contest, task string, lay layout.Layout, noOpen bool) (submitOutcome, error)
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| 解答ファイル読込失敗 | chat に err 行を表示して継続 (chat は終了しない) |
| クリップボード書込失敗 | chat に err 行を表示して継続 |
| ブラウザ起動失敗 | コピーは成功しているので、URL を含む info 行で手動オープンを案内し継続 |
| `Submit` 未注入 | 「提出準備は利用できません」を表示 |
| (注) chat はキー操作で動く TUI なので、これらは exit code ではなく**画面内の 1 行**で表現する。chat 自体の終了コードは submit 結果に依存しない |

## 非機能要件

- **既存非破壊**: `Ctrl+S` を足すだけで、`Enter`/`Ctrl+C`/`Ctrl+D`/履歴の既存挙動は不変。`test --submit` (サンプルモード) の挙動も不変。
- **解答ファイル非破壊**: submit は解答を読むだけ。書き込まない。
- **TUI 非破壊**: コールバックは stdout に直接書かない。副作用は clipboard / ブラウザのみ。
- **前方互換**: トリガーをコールバック化したので、024 のコマンドモードから `:submit` を同じ `SubmitFunc` に繋げられる。
- **層の分離**: `internal/ui` は `cmd/atcoder` を import しない。submit ロジックはコールバックで注入。

## 将来の拡張ポイント

- 024 コマンドモードの `:submit` / `:s` を同 action へ。
- `Ctrl+S` 前に公式サンプルを 1 回判定して緑のときだけ準備する option (chat を止めずに別経路で `testexec.Run`)。
- `[submit] no_open` config キーでブラウザ起動を抑止。
- 提出後に (Turnstile 解決を前提とした) verdict 追跡へ繋ぐ導線 — ただし認証は当面不可 (K)。

## 用語

- **提出準備**: サンプルゲートの後の「クリップボードコピー + 提出ページ起動」。実提出 (POST) は含まない (015 / ADR 0006 と同義)。
- **chat**: `test --interactive` / `start`→`i` で開く対話 TUI (`internal/ui/chat.go`)。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- `docs/tools/requirements/015-fold-submit-into-test.md` / `decisions/0006-fold-submit-into-test.md` (提出準備の本体 `prepareSubmission`)
- `docs/tools/requirements/019-start-key-actions.md` (start の watch キー。将来欄に `s`=提出準備があるが、本要件は chat 内の `Ctrl+S`)
- `docs/tools/requirements/024-interactive-case-builder.md` (chat のコマンドモード。`:submit` を将来エイリアスにする接続先)
- `docs/tools/abc-todo.md`「C. 提出」(submit ロードマップ)
- `docs/tools/todo.md` (本機能の項目)
