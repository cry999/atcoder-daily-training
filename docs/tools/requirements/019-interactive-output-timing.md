# interactive モードの出力タイミング表示 要件定義

## 概要

`atcoder test --interactive` (chat TUI) で、子プロセスの**出力行が届くたびに、直前のイベント (最後にユーザが入力を送ってから、または直前の出力行から) その出力までの経過時間**を各出力行に添えて表示する。インタラクティブ問題で「入力を送ってから応答が返るまでどれくらいかかったか」「連続する出力の間隔」をひと目で把握できるようにする。

`internal/ui/chat.go` (bubbletea の chat TUI) だけに閉じた表示の追加で、子プロセスの実行や judge、解答ファイルには一切影響しない。

## 背景・目的

- interactive モードでは解答とのやり取り (入力→出力) を 1 画面で見られるが、**応答の速さ (レイテンシ) は分からない**。TLE 気味の対話解法や、特定の入力で急に遅くなる挙動を、目視で気づきたい。
- 「最後の入力を受け付けてから次の出力までの時間」=応答レイテンシ、「直前の出力から次の出力までの時間」=出力間隔。この 2 つを **1 つの「直前イベントからの経過時間」** として各出力行に出せば、対話のテンポが可視化できる。
- judge やバッチ test には関係しない、interactive 限定の補助表示。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象モード | `test --interactive` (chat TUI) のみ | バッチ test の per-case 実時間表示 |
| 計測 | 直前イベント (入力送信 or 直前の出力行) → その出力行までの経過時間 (壁時計) | 累積経過、入力ごとの合計 |
| 対象行 | 子の出力行すべて (stdout `←` / debug `*` / stderr `✖`) | — |
| 表示 | 各出力行の頭に dim な経過時間を添える | 閾値超過の色分け (例 TL の n% で警告色) |
| 切り替え | 常時表示 (フラグ無し) | `--no-timing` 等のトグル、`config` キー |
| 副作用 | 無し (表示のみ。子プロセス・解答・judge に不干渉) | — |

### 境界

- interactive モードは TTY 必須で、非 TTY では既に exit 2 で拒否される (要件 013)。本表示も TTY 上の chat TUI 内だけの話で、バッチ経路 (`--in`/`--out`、judge) には一切出さない。
- 計測は **UI 層 (chat.go)** で行う。`runner` / `runexec` のプロセス実行や judge ロジックには手を入れない。

## CLI 仕様

新しい引数・フラグは無い。`atcoder test <contest> --task <task> --interactive` (TTY) の挙動が変わるだけ。

### 計測と表示の規則

1. **基準時刻 (lastEventAt)** をモデルが 1 つ持つ。セッション開始時 (子プロセス起動時 / restart 時) に「今」で初期化する。
2. ユーザが Enter で入力を送れたら、`lastEventAt = 送信時刻` に更新する。
3. 子の出力行が届いたら、`経過 = 受信時刻 − lastEventAt` を計算してその行に添え、`lastEventAt = 受信時刻` に更新する。
   - 受信時刻は **行を実際に読み出した時点** (scanner が 1 行を返した瞬間) で記録する。Update の処理遅延を含めない。
4. 入力行 (`→`) と TUI の情報行 (`(stdin closed)` 等) には経過時間を**付けない**。

### 経過時間の書式

**最大単位のみ・それ以下は四捨五入**で表示する (小数は使わない)。ただし 10,000ms 未満は `s` ではなく `ms` で出す:

| 範囲 | 例 |
|---|---|
| `>= 10s` | `12s` (秒に四捨五入) |
| `1ms 〜 <10s` | `1100ms` / `218ms` (ms に四捨五入) |
| `1µs 〜 <1ms` | `340µs` (µs に四捨五入) |
| `< 1µs` | `0` / `830ns` |

経過時間は**固定幅で右寄せ**し、その後に矢印・本文を置く (`実行時間 → 矢印 → 出力` の順)。

### 出力イメージ

```
$ atcoder test ahc_interactive --task a --interactive
 a   contest=ahc001  time_limit=2000ms  (interactive)
──────────────────────────────────────────
       → 3
   2ms ← Query? 1 2
       → 5
 840µs ← Query? 3 4
  12µs ← Query? 5 6
 218ms ← Answer: 42        # 入力 → 出力まで 218ms かかった例
──────────────────────────────────────────
» ▌
```

(経過時間は dim カラーで、`←`/`✖`/`*` の直後・本文の前に固定幅で添える。)

## 動作仕様

| 状況 | 挙動 |
|---|---|
| 入力 (Enter で送信成功) | `lastEventAt` を送信時刻に更新。入力行自体に経過は付かない |
| 出力行 (stdout/stderr/debug) | 直前イベントからの経過を添え、`lastEventAt` を受信時刻に更新 |
| 入力前に出力が来た (起動直後の prompt 等) | セッション開始時刻からの経過を表示 |
| 連続する出力行 | 各行が「直前の出力行からの経過」を表示 (µs オーダになることもある) |
| restart ([r] / auto-restart) | `lastEventAt` を新セッション開始時刻にリセット |
| stdin close / 子終了 / 情報行 | 経過は付けない (出力行ではないため) |

- **表示のみ・非破壊**: 子プロセスの stdin/stdout、judge、解答ファイル、scrollback の中身 (テキスト) は変えない。経過時間は表示時に添えるだけで、行のテキストには混ぜない。
- **決定的なロジック**: 経過の算出と書式化は純粋関数に切り出し、ユニットテストする (壁時計依存は注入した時刻で固定)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `chatLineMsg` に受信時刻 `at` を追加 (`readLineCmd` で `time.Now()` を記録)。`chatModel` に `lastEventAt` を追加。`chatLine` に経過 `dur` (と有無フラグ) を追加。Update の入力送信時・出力受信時に `lastEventAt` を更新し出力行に `dur` を載せる。`refreshViewport` で出力行の頭に dim な経過を描画。restart / 初期化で `lastEventAt` をリセット。書式化 `formatDur` と dim スタイル `chatTimeStyle` を追加 |
| 新規 `internal/ui/chat_test.go` | `formatDur` の書式テスト、経過算出 (注入時刻) の単体テスト |
| `docs/tools/usage/test.md` | interactive モードの説明に「出力行に経過時間が出る」旨を追記 |
| `docs/tools/atcoder-test-architecture.md` | chat TUI のイベント/時刻追跡の記述を追記 |
| `docs/tools/todo.md` | 項目 Q として記載し、本要件へ相互リンク |

### chat.go の追加点 (素描)

```go
type chatLineMsg struct {
    kind string
    text string
    at   time.Time // 行を読み出した時刻 (出力行の経過算出に使う)
}

type chatLine struct {
    kind   string
    text   string
    dur    time.Duration
    hasDur bool
}

// chatModel に追加:
//   lastEventAt time.Time // 最後の入力送信 or 出力受信の時刻

// formatDur は最大単位のみ・四捨五入の書式 (12s / 1100ms / 340µs / 0)。純粋関数。
func formatDur(d time.Duration) string
```

- `readLineCmd` は `scanner.Scan()` が true を返した直後に `time.Now()` を記録して `chatLineMsg.at` に載せる。`streamEndMsg` には不要。
- 出力行種別 (`kindOut` / `kindDebug` / `kindErr`) のみ `dur` を計算・表示。`kindIn` / `kindInfo` は対象外。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| (表示のみの機能。新たなエラー経路は無い) | — | — |
| 経過が負になりうる時刻ズレ | 0 にクランプして表示 | — |

- exit code 規約・既存の interactive のエラー (非 TTY 拒否 = 2 等) は不変。

## 非機能要件

- **既存非破壊**: interactive 以外 (judge・バッチ test・run の各経路) の挙動・出力・exit code は不変。chat TUI の既存操作 ([r] restart・履歴・Ctrl+D/C) も不変。
- **副作用ゼロ**: 子プロセス・解答・キャッシュ・設定に触れない。表示の付加のみ。
- **依存ゼロ追加**: 標準 `time` と既存の lipgloss のみ。`go.mod` を変えない。
- **決定的・テスト可能**: 書式化と経過算出を純粋関数にし、注入時刻でユニットテスト。
- **視認性**: 経過は dim カラー + 固定幅で、本文の読みやすさを損なわない (既存の「色=種別 / 明暗=優先度」方針を踏襲)。

## 将来の拡張ポイント

- `--no-timing` トグルや `config` キーで常時表示を切れるように。
- time_limit に対する割合で**閾値色分け** (例 TL の 80% を超えた応答を警告色)。
- 入力ごとの**累積時間**や、セッション全体のサマリ (最大/平均レイテンシ) を子終了時に表示。
- バッチ test の per-case 実時間表示との表現統一。

## 用語

- **イベント (event)**: ユーザの入力送信 (Enter) か、子の出力行 1 つ。経過時間はこの「直前イベント」からの差分。
- **経過時間 (elapsed)**: 直前イベントの時刻から、対象の出力行を読み出した時刻までの壁時計差分。
- **基準時刻 (lastEventAt)**: 直近のイベント時刻。出力受信・入力送信のたびに更新。
- chat TUI / interactive の用語は要件 013 (test/run 統合) に準拠。

## 関連ドキュメント

- `docs/tools/requirements/013-unify-test-run.md` (interactive モード = `--interactive` の導入元)
- `docs/tools/usage/test.md` / `atcoder-test-architecture.md` (interactive の利用手引・内部設計)
- `docs/tools/todo.md` (上位ロードマップ。項目 Q)
