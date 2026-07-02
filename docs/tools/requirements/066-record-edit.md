# 066 record edit — 既存記録の全画面編集フォーム

## 概要

`atcoder record edit <contest> --task <task>` と chat の `:record edit` で、既に記録済みの
solve-stat ブロックを **全画面フォーム**で一覧表示し、任意フィールドを訂正・クリアできる
ようにする。要件 061 (record MVP) / 064 (chat :record) で「対話ウィザードは Phase 2」と
申し送っていた分の実装。

## 背景・目的

現状の記録訂正は「`atcoder record` / `:record` をフラグ付きで再実行してキー単位に上書き」
する形しかない。これには次のフリクションがある:

- 現在値が見えない。何が入っていて何を直すのか、記録前に頭で把握する必要がある。
- フラグの綴りを覚えていないと直せない (`--no-editorial` で false、では未記録に戻すには?)。
- Merge ベースなので「一度 true にした ac を未記録へ戻す」ようなクリアが素直にできない。

`record edit` は現在値を並べて見せ、その場で ↑↓ 移動 + ←→/入力で書き換え、Ctrl+S で保存
する専用フォームを提供する。CLI とオンライン (chat) の双方から同じ体験で開ける。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 編集対象フィールド | `ac` / `editorial` / `duration_ms` / 5 軸 (`knowledge`/`translation`/`complexity`/`impl`/`verify`) | `started_at` / `solved_at` の時刻直接編集 |
| 保全フィールド | `started_at` / `solved_at` / `target_ms` は表示も編集もせず、保存時に元の値を温存する | 時刻編集に伴う duration 再計算 |
| 起動経路 | CLI `record edit` (standalone TUI) と chat `:record edit` (埋め込みモード) | — |
| 保存方式 | フォーム確定時に `solvestat.OverwriteFile` で全置換 (クリア = 当該キーを落とす) | — |
| 前提 | 既存の solve-stat ブロックがあること (無ければエラー案内) | 無記録からの新規作成ウィザード |

`edit` は「訂正」に特化する。新規計測 (`start`) / 完了確定 (`stop`) / 初回記録は従来どおり
`record` / `:record` が担う (要件 061/064)。境界を跨がない。

> **追補 (要件 068)**: 上表「将来の拡張余地」のうち `started_at`/`solved_at` の書き換えは、
> 時刻直接編集ではなく**計測状態 (state) のトグル**という形で
> [`068-record-edit-state-toggle.md`](068-record-edit-state-toggle.md) が実装した
> (フォーム内で `未計測 → 計測中 → 停止 → リセット` を切替え、遷移時に実時刻 now を刻む)。
> `started_at`/`solved_at` を**任意の時刻値**へ直接編集する分は引き続き将来拡張。

## solve-stat スキーマ (再掲・不変)

要件 061 のブロックを前提とする。`edit` はこのうち下記の 8 キーだけを書き換え、残りは温存する。

```python
# >>> atcoder-stat >>>
# started_at  = 2026-07-01T16:00:00+09:00   ← 保全 (edit は触らない)
# solved_at   = 2026-07-01T16:25:00+09:00   ← 保全
# duration_ms = 1500000                      ← 編集可
# target_ms   = 2100000                      ← 保全
# ac          = true                         ← 編集可
# editorial   = false                        ← 編集可
# knowledge   = 2                            ← 編集可
# translation = 3                            ← 編集可
# complexity  = 2                            ← 編集可
# impl        = 3                            ← 編集可
# verify      = 1                            ← 編集可
# <<< atcoder-stat <<<
```

## CLI 仕様

### `atcoder record edit <contest> --task <task> [--layout <auto|abc|exercise>]`

| 引数 / フラグ | 説明 |
|---|---|
| `<contest>` (位置) | contest ID (例 `abc457`)。必須 |
| `--task <task>` | task ID または短縮形 (`d`)。必須 |
| `--layout` | `auto`/`abc`/`exercise` (config 既定を継承)。他の record 系と同じ |

処理ステップ:

1. `--task` を必須チェック + 短縮形展開し、layout から解答パス・category×letter を解決する。
2. 解答ファイルを読み、solve-stat ブロックを取り出す。
   - ファイルが無い / ブロックが無い → 案内エラー (exit 1)。編集は既存記録が前提。
   - ブロック破損 (マーカー不整合) → `solvestat.Parse` の error をそのまま (exit 1)。
3. 標準入力が端末でなければ (`term.IsTerminal` が false) → エラー (exit 1)。全画面フォームは
   対話端末が要る。非対話での訂正はフラグ経路 (`atcoder record ...`) を案内する。
4. 全画面フォーム (`ui.RunRecordEdit`) を起動し、現在値を並べて表示する。
5. Ctrl+S で確定 → 編集後の Stat を `solvestat.OverwriteFile` で全置換保存し、要約を印字。
   Esc / Ctrl+C で取消 → 何も書かず「(編集を取消しました)」を印字 (exit 0)。

出力イメージ (保存時):

```
$ atcoder record edit abc457 --task d
（全画面フォームで編集 → Ctrl+S）
記録を更新しました: exercise/2026/07/01/abc457_d.py
  実装 23m / 目標 35m (-12m, 達成)
  ac=true  editorial=false
  score  k=2 t=3 c=2 i=3 v=1
```

### フォーム UI (`ui.RunRecordEdit` / chat 埋め込み共通)

```
record edit  abc457_d

> ac          [ true ]
  editorial   [ false ]
  duration    [ 23m ]
  knowledge   [ 2 ]
  translation [ 3 ]
  complexity  [ 2 ]
  impl        [ 3 ]
  verify      [ 1 ]

目標 35m
↑↓ 移動   ←→/space 変更   0-3・y/n 入力   Backspace 未記録   Ctrl+S 保存   Esc 取消
```

- 選択行は `>` マーカー + 強調色。
- `ac` / `editorial` (tri-bool): `←→` / space で `未記録 → true → false → 未記録` を循環。
  `y`=true / `n`=false / Backspace=未記録。表示は `true` / `false` / `—`。
- 5 軸 (score): `←→` で `未記録 ↔ 0 ↔ 1 ↔ 2 ↔ 3` を移動。`0`-`3` 直接入力、Backspace=未記録。
  表示は `0`..`3` / `—`。
- `duration`: テキスト編集。数字と `h`/`m`/`s` を受け、Backspace で 1 文字削除。空なら未計測。
  未編集なら元の `duration_ms` を保存時にそのまま温存 (分丸め表示による桁落ちを避ける)。
  編集した場合のみ `time.ParseDuration` で解釈し、不正なら保存を止めてフォーム内にエラーを出す。
- `目標 <t>` は read-only の文脈表示 (config の target。編集しない)。target 未設定なら出さない。

## chat 仕様 (`:record edit`)

- command モードで `:record edit` を打つと、chat が **record-edit モード**へ入り、上記フォームを
  ヘッダ直下に全面表示する (`:case` の builder モードと同じ「子は裏で生かしたまま画面を占有」)。
- Ctrl+S で確定 → 保存し、結果行 (更新しました / 実装時間 / 要約) を info 行で積んで insert へ戻る。
- Esc / Ctrl+C で取消 → 「(編集を取消しました)」を info 行で積んで insert へ戻る。
- 記録が無い / ブロックが無い → info 行「(まだ記録がありません。:record start で計測を開始できます)」。
- Tab 補完: `:record ` の第 2 トークン候補に `edit` を追加 (`start` / `stop` と並ぶ)。
- `:cheat` の `:record` 行に `edit` を追記する。

layout は chat 起動時に解決済みの `lay` を使う (auto 再判定で abc<NNN> を常に ABC に落とさない。
要件 064 と同じ理由)。

## 動作仕様

| 状況 | 動作 |
|---|---|
| 未編集フィールド | 保存時に元の値をそのまま温存 (duration は ms 単位で桁落ちなし) |
| フィールドを未記録へ | tri-bool/score を Backspace 等でクリア → `OverwriteFile` が当該キーを落とす |
| `started_at`/`solved_at`/`target_ms` | フォームに出さず、保存 Stat には元の値を引き継ぐ |
| duration が不正な文字列 | 保存を止めてフォーム内にエラー表示 (端末に留まる) |
| 取消 (Esc/Ctrl+C) | ファイルは一切書き換えない |
| 記録・ブロック無し | CLI: exit 1 で案内 / chat: info 行で案内 (どちらも書き込まない) |
| ブロック破損 | `Parse` の error を返す (自動修復しない安全側。要件 061 踏襲) |
| 非対話端末 (CLI) | exit 1 で「フラグ経路で訂正」を案内 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/recordedit.go` (新規) | 全画面編集フォーム。`solvestat.Stat` を入力に取り、編集後の Stat と保存可否を返す純粋な bubbletea モデル + standalone 起動 `RunRecordEdit`。file I/O・layout は持たない (composition root へ委譲) |
| `internal/ui/chat.go` | `ChatHeader` に `RecordEditLoad` / `RecordEditSave` フックを追加。`chatMode` に `modeRecordEdit` を足し、Update/View/WindowSize で編集モードを配線 |
| `internal/ui/chat_casebuilder.go` | `parseCommand` は既存の `record` 経路のまま。`execRecord` で第 1 トークン `edit` を record-edit モード起動に分岐。`:cheat` に追記 |
| `internal/ui/command_complete.go` | `completeSubTokens["record"]` に `edit` を追加 |
| `cmd/atcoder/record.go` | `cmdRecord` の `edit` スタブを `recordEdit` 実装へ差し替え。`internal/ui` を import |
| `cmd/atcoder/chatrecord.go` | `chatRecordEditLoadFunc` / `chatRecordEditSaveFunc` を追加 (solve-stat の読み込み・全置換保存を閉じ込める) |
| `cmd/atcoder/start.go` / `adhoc.go` | `ChatHeader` に `RecordEditLoad` / `RecordEditSave` を注入 |
| `cmd/atcoder/main.go` | `usage()` に `record edit` 行を追加 |
| `docs/tools/usage/record.md` | `record edit` / `:record edit` の項を追記 |
| `docs/tools/todo.md` (AV) / `064-chat-record.md` | Phase 2 (record edit) の DONE を記録・相互リンク |

新規 UI 型の公開 API 素描 (`internal/ui`):

```go
// RecordEditResult は編集結果 (保存された Stat と保存可否)。
type RecordEditResult struct {
	Stat  solvestat.Stat
	Saved bool
}

// RunRecordEdit は standalone (CLI record edit) で全画面フォームを起動する。
func RunRecordEdit(title string, st solvestat.Stat, targetMs int64) (RecordEditResult, error)

// ChatHeader へ追加するフック。
type ChatHeader struct {
	// ...
	RecordEditLoad func() (st solvestat.Stat, targetMs int64, found bool, err error)
	RecordEditSave func(st solvestat.Stat) (lines []string, err error)
}
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `--task` 欠落 | `--task is required` | 2 |
| フラグ解析失敗 | flag パッケージの usage | 2 |
| 解答ファイル無し / ブロック無し (CLI) | 案内エラー | 1 |
| ブロック破損 | `Parse` の error | 1 |
| 非対話端末 (CLI) | フラグ経路を案内 | 1 |
| 保存 I/O 失敗 | error | 1 |
| 取消 (保存せず) | 案内のみ | 0 |
| duration 不正 (フォーム内) | フォームに留まり保存しない | — |

## 非機能要件

- **既存非破壊**: 解答コード本体には触れない。保全フィールドは保存時に元値を引き継ぐ。
- **冪等/安全**: 保存は `OverwriteFile` (temp+rename の atomic)。取消時は書き込み 0。
- **層境界**: `internal/ui` は layout/config/testexec/file I/O を知らない。solve-stat の読み書きは
  composition root (cmd/atcoder) が握り、UI には `solvestat.Stat` (純データ) だけ渡す。
  Meta/Gen/Record と同じフック委譲パターン。
- **前方互換**: フォームはキー集合を固定で持つ。将来 `started_at`/`solved_at` 編集や言語別
  コメント接頭辞を足すときは、フィールド定義とレンダラを拡張して差し込む。

## 用語

要件 061/064 に準拠 (`contest_id`=`abc457` / `task_id`=`abc457_d` / `letter`=`d` /
`category`=`abc`)。

## 関連ドキュメント

- 要件 061 (solve-stat / record MVP): `061-solve-record-stats.md`
- 要件 064 (chat :record): `064-chat-record.md` (本要件が Phase 2 を実装)
- 利用手引: `docs/tools/usage/record.md`
- ロードマップ: `docs/tools/todo.md` (AV)
