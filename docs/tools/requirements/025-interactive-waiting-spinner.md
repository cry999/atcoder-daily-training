# 対話モードの出力待ちスピナー + 経過時間表示 要件定義

## 概要

`atcoder test --interactive` の chat TUI で、**入力を送ってから次の出力が返るまでの待機状態**を可視化する。送信直後に**ローディングアニメ (スピナー) と経過時間**を入力ボックスの下罫線にライブ表示し、出力が来たら消す。「打ったのに反応が無い / 重いのか固まったのか」を一目で判別できるようにする。

## 背景・目的

- 対話問題やデバッグ中、入力を送った後に子プロセスが計算している間は画面が無反応で、**待っているのか固まったのか分からない**。各出力行には直前イベントからの経過時間が出るが、それは**出力が来てから**しか見えない。
- 「送信 → 返答までの待ち時間」をリアルタイムに見せれば、重い処理・無限ループ・入力過不足を早く気づける。
- スピナーで「生きて待っている」ことを示し、経過時間で「どれだけ待ったか」を示す。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 表示契機 | **入力送信 (Enter) 成功後**〜次の出力行が来るまで | 起動直後の初回出力待ちも対象に |
| 表示物 | スピナー (アニメ) + 経過時間 (`送信からの経過`) | 推定 TLE 超過の警告色 |
| 配置 | **入力ボックスの下罫線**に重ねる (画面の高さを変えない) | 別行・ヘッダ等の選択 |
| 解除契機 | 最初の出力行 (stdout/stderr/debug) 到着 / 子プロセス終了 / リロード・再起動 | — |
| 対象 | **TTY の chat TUI のみ** (非 TTY passthrough は対象外) | — |
| 副作用 | 無し (表示のみ。子プロセス・解答・キャッシュに触れない) | — |

### 境界

- スピナーは**送信後の待機専用**。子が自発的に出す出力 (送信前のプロンプト等) では出さない (送信していないので待機状態ではない)。
- `--interactive` の **TTY chat TUI** だけ。非 TTY passthrough・サンプルモード・ad-hoc には影響しない。

## CLI 仕様

- **新フラグは無し**。`atcoder test --interactive` (および `atcoder start` の下ペイン chat) の挙動として常時有効。

### 画面イメージ (chat TUI)

入力送信直後 (待機中):

```
   3ms ← 5
       → 10
────────────────────────────
» _
⠹ 430ms ─────────────────────   ← 入力ボックス下罫線にスピナー + 経過時間
```

出力が返ると消える:

```
   3ms ← 5
       → 10
  412ms ← 20
────────────────────────────
» _
────────────────────────────   ← 待機解除で通常の罫線に戻る
```

### 処理ステップ

1. Enter で入力を子の stdin に書き込み成功 → **待機開始**: `awaiting=true`、`awaitSince=now`、スピナー世代を更新して tick を 1 本起動。
2. `spinnerTickMsg` (約 100ms 間隔・世代タグ付き) ごとにスピナーのコマを進め、待機中なら再アーム。世代不一致・待機解除なら停止 (再アームしない)。
3. 出力行 (stdout/stderr/debug) 到着で `awaiting=false`。子プロセス終了・リロードでも `awaiting=false`。
4. View では待機中だけ、入力ボックスの下罫線にスピナーのコマ + 経過時間 (`now - awaitSince`) を描く。非待機時は通常の罫線。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| Enter 送信成功 | 待機開始。下罫線にスピナー + 経過時間をライブ表示 |
| Enter 送信失敗 (write error) | 待機にしない (従来どおりエラー行のみ) |
| 出力行が到着 | 待機解除 (スピナーを消す)。出力行自体には従来の経過時間カラムが付く |
| 子プロセス終了 (EOF) | 待機解除 |
| リロード / 再起動 | 待機解除。スピナー世代を更新して旧 tick を無効化 |
| 連続送信 (出力前に再度 Enter) | 世代を更新し `awaitSince` をリセット。tick ループは常に 1 本 (二重アニメにしない) |
| 非 TTY passthrough | 影響なし (chat TUI を使わない) |

- **既存非破壊**: 出力行の経過時間カラム・折り返し・入力履歴・auto-restart・watch-reload は不変。スピナーは下罫線への重ね描きで、**画面の行数を増やさない** (分割画面 `start` の高さ計算も崩さない)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `chatModel` に待機状態 (`awaiting`/`awaitSince`/`spinnerFrame`/`spinGen`) を追加。`spinnerTickMsg` と `spinnerTickCmd`。Enter ハンドラで待機開始、`chatLineMsg`/`streamEndMsg`/`restart` で解除。`renderInputBox` の下罫線に待機表示を重ねる。純粋関数 `waitStatus(frame int, elapsed time.Duration) string` |
| `internal/ui/chat_test.go` (または新規) | `waitStatus` のフォーマットと、待機状態の遷移 (送信で on・出力で off・世代タグで stale 破棄) をユニットテスト |
| `docs/tools/atcoder-test-usage.md` | 対話モード節に「送信後の待機スピナー + 経過時間」を 1 行追記 |
| `docs/tools/atcoder-test-architecture.md` | chat の状態遷移にスピナー待機を追記 (あれば) |
| `docs/tools/todo.md` | 本項目を記載し本要件へ相互リンク |

### `internal/ui/chat.go` への追加 (素描)

```go
// chatModel に追加:
//   awaiting    bool      // 送信後・出力待ちなら true (スピナー + 経過時間を出す)
//   awaitSince  time.Time // 待機開始時刻 (経過時間の基準)
//   spinnerFrame int      // スピナーのコマ index
//   spinGen     int       // スピナー tick の世代。Enter/restart で更新し旧 tick を無効化

type spinnerTickMsg struct{ gen int }

// spinnerTickCmd は spinnerInterval 後に世代タグ付き tick を返す。
func (m *chatModel) spinnerTickCmd() tea.Cmd

// waitStatus はスピナーのコマと経過時間を 1 行の文字列にする純粋関数。
//   例: "⠹ 430ms" / "⠋ 5000ms" (formatDur 表記)
func waitStatus(frame int, elapsed time.Duration) string
```

- スピナーは bubbles/spinner を使わず、braille のコマ配列 + `tea.Tick` の自前実装にする (状態が `spinnerFrame` の int だけで済み、決定的にテストしやすい)。
- 経過時間は既存の `formatDur` を流用 (出力行の経過時間カラムと表記を揃える)。
- 待機表示は下罫線に重ねるため `View` の行数は不変。

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| 送信 write error | 待機にしない。従来のエラー行表示のみ |
| スピナー tick が stale (世代不一致) | 無視 (再アームしない) |

- exit code への影響なし (表示のみ)。

## 非機能要件

- **既存非破壊**: 出力経過時間・折り返し・履歴・auto-restart・watch-reload・分割画面の高さ計算を壊さない。下罫線への重ね描きで行数不変。
- **busy-loop にしない**: tick は待機中だけ回す。非待機時は再アームせず止まる。
- **決定的にテスト可能**: `waitStatus` を純粋関数にし、待機の状態遷移を Model 直接駆動でユニットテストする (アニメの見た目自体は TTY 必須で手動確認)。
- **TTY 専用**: 非 TTY passthrough には一切影響しない。

## 将来の拡張ポイント

- **TLE 超過の警告**: 経過が問題の制限時間を超えたら色を変える / 警告を出す。
- **起動直後の初回出力待ち**もスピナー対象に。
- スピナーのスタイル (コマ・色・位置) を `config` で選べるように。

## 用語

- **待機 (awaiting)**: 入力送信後、次の出力行が来るまでの状態。
- **スピナー (spinner)**: 待機中に回す braille のローディングアニメ。
- **経過時間 (elapsed)**: `awaitSince` から現在までの時間。`formatDur` で表記。

## 関連ドキュメント

- `docs/tools/requirements/020-interactive-auto-restart-flag.md` / `021` / `022` (chat の挙動)
- `docs/tools/atcoder-test-usage.md` (対話モードの利用手引)
- `docs/tools/atcoder-test-architecture.md` (chat TUI 内部設計)
