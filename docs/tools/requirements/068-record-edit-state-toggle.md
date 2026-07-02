# 068 record edit — 計測状態 (state) のトグル

## 概要

`atcoder record edit` / chat `:record edit` の全画面編集フォームに **計測状態 (state)** の行を
足し、その場でトグルして `未計測 → 計測中 → 停止 → 未計測(リセット)` を 1 打鍵で切り替えられる
ようにする。要件 066 が「将来の拡張余地」として申し送っていた `started_at` / `solved_at` の
書き換えを、時刻直接入力ではなく **計測ライフサイクルのトグル**という形で実装する分。

これまで編集フォームは訂正 (ac/editorial/duration/5 軸) 専用で、計測の開始・停止・やり直しは
フォームを離れて `:record start` / `:record stop` / `:record start restart` を打つ必要があった。
本要件でフォーム内から同じ操作を完結できるようにする。

## 背景・目的

- 編集フォームは現在値を一覧できるのに、`started_at` / `solved_at` は保全されるだけで動かせない。
  「今から計測を始めたい」「完了にしたい」「やり直したい」には一旦フォームを閉じる必要がある。
- `:record start` / `:record stop` / `restart` は個別コマンドで、綴りと状態を頭に入れておく必要がある。
- フォームに状態を出せば、現在が `未計測` / `計測中` / `停止` のどれかが一目でわかり、その場で
  進められる。編集と計測制御が 1 画面に統合される。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 追加フィールド | `state` (計測状態) 1 行。`未計測` / `計測中` / `停止` を表示・トグル | — |
| トグル遷移 | `未計測 →(start)→ 計測中 →(stop)→ 停止 →(reset)→ 未計測` の 1 方向サイクル | 逆方向 (un-stamp) の遷移 |
| 時刻の刻み方 | 遷移時に**実時刻 now** を刻む (`:record start`/`stop` と同じ)。start=`started_at`、stop=`solved_at`+`duration`+`target` スナップショット | `started_at`/`solved_at` の時刻直接編集 |
| リセット | `停止 → 未計測` で **全フィールドを空にする** (`:record start restart` 相当の全クリア。started_at も空) | — |
| chat の REC 同期 | 保存後にヘッダの ● REC インジケーターを保存内容から再導出して一致させる | — |
| 起動経路 | CLI `record edit` (standalone) と chat `:record edit` (埋め込み) の双方 (フォーム共通実装) | — |

計測状態は `started_at` / `solved_at` の有無だけから導出する。時刻の**具体値**を任意編集する
(例: `started_at` を過去の特定時刻へ) のは引き続き将来拡張 (要件 066 の申し送りどおり)。本要件は
「今から start / stop / reset する」ライフサイクル操作に閉じる。

## 計測状態モデル

状態は解答ファイルの `started_at` / `solved_at` から一意に導出する (フォーム起動時の初期表示)。

| 導出状態 | 条件 | 表示 |
|---|---|---|
| `未計測` | `started_at` が空 | `[ 未計測 ]` |
| `計測中` | `started_at` あり かつ `solved_at` が空 | `[ 計測中 ]  開始 <hh:mm>` |
| `停止` | `started_at` あり かつ `solved_at` あり | `[ 停止 ]  開始 <hh:mm> → 完了 <hh:mm>` |

`started_at` が空で `solved_at` だけある破損状態は `未計測` として扱い、トグルで start すると
`solved_at` も空へ整える (下記遷移で吸収する)。

### トグル遷移 (前方サイクル)

トグルキーを押すたびに、**現在の導出状態**に応じて次へ進む。時刻はすべて **now = 押した瞬間の実時刻**。

| 現在 | 操作 | 次 | Stat への作用 |
|---|---|---|---|
| `未計測` | start | `計測中` | `started_at = now`、`solved_at` 空、`duration_ms = 0` |
| `計測中` | stop | `停止` | `solved_at = now`、`duration_ms = now − started_at`、`target_ms = 現在の config 目標` (>0 のとき) |
| `停止` | reset | `未計測` | **全フィールドを空** (`solvestat.Empty()`。`started_at`/`solved_at`/`duration_ms`/`target_ms`/`ac`/`editorial`/5 軸すべてクリア) |

- **1 方向サイクル**。逆行 (un-stamp) は提供しない。トグルキーは常に前方へ進める。
- `stop` の `duration_ms` は `now − started_at` を再計算して確定する。以後フォームの `duration`
  行を手で編集すればその値が優先される (`duration` は従来どおり編集可)。
- `reset` は既存の `:record start restart` と同じく完了系・スコアも含め破棄する (やり直し練習用)。
  ただし `restart` が `started_at=now` (計測中) にするのに対し、本サイクルの `reset` は **完全に空**
  (`未計測`) にする点が異なる (サイクルの起点へ戻すため)。

## フォーム UI

`state` を**最上段**に置き、既存 8 フィールドがその下に続く (要件 066 の並びは不変)。

```
record edit  abc457_d

> state       [ 計測中 ]  開始 16:00
  ac          [ — ]
  editorial   [ — ]
  duration    [ — ]
  knowledge   [ — ]
  translation [ — ]
  complexity  [ — ]
  impl        [ — ]
  verify      [ — ]

目標 35m
j/k 移動   Tab/space トグル   h/l 変更   0-3・y/n 入力   Backspace 未記録   Enter 保存   Esc 取消
```

- **`state` 行**: 表示は導出状態 (`未計測` / `計測中` / `停止`)。`計測中`/`停止` では開始・完了時刻
  (`hh:mm`) を淡色で添える。
- **トグルキー**:
  - `Tab` / `space` — **カーソルが当たっているフィールドの値を前方へトグル**する。`state` 行では状態を
    **前方へ 1 段**進め (`未計測 → 計測中 → 停止 → 未計測`)、`ac`/`editorial` は tri-bool を、5 軸は score を
    1 段回す (`l` と同じ前方向)。`duration` はトグルする値がないため無操作。
  - `state` 行にカーソルがあるとき — `l` / `space` / `Tab` はいずれも前方へ 1 段進める。`h` も同様に前方
    (状態は 1 方向サイクルなので `h`/`l` とも前進で統一)。`Backspace` は `未計測` へ即リセット (全クリア)。
  - （当初は `Tab` を「カーソル位置に関係なく state を前進」とする仕様だったが、フォーカス中フィールドを
    トグルする方が直感的なため本挙動へ変更した。）
- 他フィールド (`ac`/`editorial`/`duration`/5 軸) の `h/l`・`0-3`・`y/n`・`Backspace` は要件 066 のまま不変。
- 状態トグルは**他フィールドへ波及する**: `start`/`reset` は `duration` 行を空に、`reset` は
  `ac`/`editorial`/5 軸も未記録へ整える。`stop` は `duration` 行に算出値を反映する。
- `目標 <t>` は従来どおり config の目標時間 (read-only の文脈表示)。この値は状態トグルで変わらない
  (`stop` 時に record の `target_ms` へスナップショットする値でもある)。

## chat 仕様 (`:record edit` からの状態トグル)

- `:record edit` で開いたフォームでも上記トグルは同様に効く (フォーム実装を共有)。
- **保存 (Enter/Ctrl+S) 後、ヘッダの ● REC インジケーターを保存内容から再導出して同期する**:
  - 保存後 Stat が `計測中` (`started_at` あり・`solved_at` 空) → REC 点灯。経過は `started_at`
    を基準に表示し、毎秒 tick を再開する (`recordStart = started_at`、`recordGen++`)。
  - それ以外 (`停止` / `未計測`) → REC 消灯 (`recording=false`、`recordGen++` で走行中 tick を止める)。
  - 取消 (Esc/Ctrl+C) では何も書かず REC も変えない。
- これにより「フォームで start → 保存 → chat に戻ると ● REC が動いている」「stop/reset → 消灯」が
  ファイルの状態と常に一致する。従来の `:record start`/`stop` によるインジケーター制御 (要件 064)
  と矛盾しない。

## 動作仕様

| 状況 | 動作 |
|---|---|
| フォーム起動 | `started_at`/`solved_at` から状態を導出して `state` 行に表示 (書き込みはしない) |
| `start` トグル | `started_at=now`、`solved_at`/`duration` クリア。他フィールドは保持 |
| `stop` トグル | `solved_at=now`、`duration=now−started_at`、`target_ms` を config 目標でスナップショット |
| `reset` トグル | Stat 全体を空へ (started_at/solved_at/duration/target/ac/editorial/5 軸すべて) |
| トグル後に手編集 | `duration`/`ac`/`editorial`/5 軸は従来どおり個別に上書きできる (state と独立) |
| 保存 (Enter/Ctrl+S) | 編集後 Stat を `OverwriteFile` で全置換。started_at/solved_at も反映される |
| 取消 (Esc/Ctrl+C) | ファイルは一切書き換えない。chat の REC も変えない |
| chat 保存後 | REC インジケーターを保存 Stat から再導出して同期 (上記) |
| CLI `record edit` 保存後 | ファイルに started_at/solved_at 込みで書かれる (CLI に REC 表示はない) |
| 記録・ブロック無し | 要件 066 のまま (CLI: exit 1 案内 / chat: info 行案内)。フォーム自体を開かない |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/recordedit.go` | `state` フィールド種別 (`recFieldState`) を追加。モデルに可変な時刻 (`startedAt`/`solvedAt`)・record 目標スナップショット (`recordTargetMs`)・config 目標 (`configTargetMs`) を持たせ、`orig` 固定参照をやめる。`advanceState(now)` (状態前進 + 他フィールドへの波及)・`resetState()`・状態導出ヘルパを追加。`handleKey` に `Tab` と `state` 行のトグルを配線。`resultStat` は可変時刻/目標を反映。`View` に state 行と時刻の淡色表示、ヒント行更新。`RunRecordEdit` は変更なし (結果 Stat に時刻が乗るだけ) |
| `internal/ui/chat_casebuilder.go` | `updateRecordEdit` で保存確定時に、保存 Stat の `started_at`/`solved_at` から `recording`/`recordStart`/`recordGen` を再導出し、`計測中` なら `recordTickCmd()` を返して REC を同期 |
| `internal/ui/chat.go` | 変更なし想定 (既存の `recording`/`recordStart`/`recordGen`/`recordTickCmd` を再利用)。必要なら REC 同期ヘルパを 1 つ足す |
| `docs/tools/usage/record.md` | `:record edit` / `record edit` の項に state トグルの説明を追記 |
| `docs/tools/requirements/066-record-edit.md` | 「将来の拡張余地」から state トグル分を本要件へ相互リンク |
| `docs/tools/todo.md` | 該当項目に本要件の DONE を記録・相互リンク |

`internal/ui` の層境界は不変: フォームは `solvestat.Stat` (純データ) と config 目標だけを入出力し、
`now` の取得 (`time.Now`) は既に ui 内で使われている (chat の tick / recordedit の duration 解釈)。
ファイル I/O・layout・config 解決は composition root (cmd/atcoder) が握る (要件 064/066 と同じ委譲)。

新規/変更する ui 内部要素 (公開 API は不変):

```go
const recFieldState recEditKind = iota // ... 既存種別に追加

// recordEditModel に追加する可変状態 (orig 参照を置き換える)
type recordEditModel struct {
    // ...
    startedAt      time.Time // 可変 (状態トグルで書き換わる)
    solvedAt       time.Time // 可変
    recordTargetMs int64     // 保存する target_ms (stop でスナップショット)
    configTargetMs int64     // 目標ヒント表示 + stop スナップショット元 (不変)
    // ...
}

// advanceState は now を刻んで状態を 1 段前進させ、duration/score 等へ波及させる。
func (m *recordEditModel) advanceState(now time.Time)
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 記録・ブロック無し (CLI) | 要件 066 のまま案内 | 1 |
| 保存 I/O 失敗 | error | 1 |
| 取消 (保存せず) | 案内のみ | 0 |
| `duration` 手編集が不正 | 要件 066 のままフォーム内エラーで保存中断 | — |
| `stop` 時に `started_at` が空 (破損由来) | `duration` は算出せず 0 のまま `solved_at=now` (負値/異常値を書かない安全側) | — |

state トグル自体はローカルなモデル操作でエラーを出さない (I/O を伴わない)。異常な時刻計算は
負値を書かず 0 に落とす防御をとる (`chatRecordAnomalyWarn` と同じ思想だが、フォームでは確認を
挟めないため単に 0 とする)。

## 非機能要件

- **既存非破壊**: 解答コード本体には触れない。トグルしなければ従来どおり時刻は保全される
  (可変フィールドの初期値は `orig` から取り、トグルされたときだけ書き換わる)。
- **冪等/安全**: 保存は `OverwriteFile` (temp+rename の atomic)。取消時は書き込み 0。
- **層境界**: `internal/ui` は layout/config/testexec/file I/O を知らない。solve-stat の読み書きは
  composition root。`now` は ui 内の `time.Now`。
- **前方互換**: 状態は `started_at`/`solved_at` から導出する派生値で、スキーマは不変
  (新キーを増やさない)。将来の時刻直接編集は state トグルと併存できる (トグル=now 刻み、
  直接編集=任意時刻)。
- **既存挙動との整合**: 時刻の刻み方は `:record start`/`stop`、全クリアは `:record start restart`
  と同じ意味論に揃える。chat の REC 制御は要件 064 の既存フィールドを再利用する。

## 用語

要件 061/064/066 に準拠 (`contest_id`=`abc457` / `task_id`=`abc457_d` / `letter`=`d` /
`category`=`abc`)。「状態 (state)」は `started_at`/`solved_at` から導出する `未計測`/`計測中`/`停止`。

## 関連ドキュメント

- 要件 061 (solve-stat / record MVP): `061-solve-record-stats.md`
- 要件 064 (chat :record + REC インジケーター): `064-chat-record.md`
- 要件 066 (record edit フォーム本体): `066-record-edit.md` (本要件がその「将来拡張」を実装)
- 利用手引: `docs/tools/usage/record.md`
- ロードマップ: `docs/tools/todo.md`
