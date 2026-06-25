# interactive モードのファイル変更リロード 要件定義

## 概要

`atcoder test --interactive` の chat TUI で開いている間に**対象の解答ファイルが更新されたら、自動で検知して子プロセスを最新ファイルで再起動 (再 spawn) する**。再起動の直前にチャットへ「解答ファイルが更新されました — 新しいプログラムを起動します」というメッセージを 1 行出す。これにより、別ターミナルでコードを保存するだけで chat を抜けずに最新版で対話を続けられる (編集→対話の往復から「chat を一度抜ける」手間が消える)。

`internal/ui/chat.go` (bubbletea chat TUI) に `internal/watch` の mtime ポーリングを統合する追加で、judge・バッチ test・非 TTY 経路には影響しない。

## 背景・目的

- `atcoder start` は chat の**外側**で watch しており、対話 (`i`) に入ると監視が止まる。chat の中でコードを直しても、一度 `Ctrl+D` で抜けて入り直さないと反映されない。
- `test --interactive` を直接使う場合も同様で、保存のたびに chat を再起動する必要がある。
- chat TUI の中に watch を入れ、保存検知で**子プロセスだけ**を最新ファイルで差し替えれば、対話のコンテキスト (scrollback) を保ったままコードの変更を即試せる。spawner は毎回ソースを読み直して実行するので、再 spawn すれば自動的に最新版になる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | `test --interactive` の **chat TUI (TTY)**。`start` の `i` 経由も同じ TUI なので含む | 非 TTY passthrough の擬似リロード |
| 監視対象 | 実行中の解答ファイル 1 つ (`solutionPath`) | サンプルファイル・自作ライブラリ |
| 検知 | mtime ポーリング (`internal/watch`、200ms / debounce 120ms) | fsnotify |
| リロード | 実行中の子を kill → 最新ファイルで再 spawn (= 既存の restart) | 差分再ビルドのみ等の最適化 |
| 通知 | 再起動直前にチャットへ info 行を 1 つ | 変更ファイル名・mtime の表示 |
| 切り替え | **常時有効** (chat TUI に入っている間) | `--no-reload` opt-out フラグ |
| 副作用 | 子プロセスの差し替えのみ。解答・キャッシュ・judge に不干渉 (読むのは mtime だけ) | — |

### 境界

- watch-reload は **chat TUI (TTY) 限定**。非 TTY の interactive (passthrough) は単発実行で再 spawn ループを持たないため対象外。
- 監視・リロードは **UI 層 (chat.go)** に閉じる。`runexec` は監視対象パス (`WatchPath`) を chat TUI へ渡すだけ。watch 間隔・debounce は `test --watch` / `start` と同じ値を踏襲する。
- `start` の外側 watch ループ (要件 P) とは独立。chat に入っている間は内側 watch が、抜けたら外側 watch が動く (二重には動かない)。

## CLI 仕様

新しい引数・フラグは無い。`atcoder test <contest> --task <task> --interactive` (TTY) と `atcoder start ... → i` の chat 挙動が変わるだけ。

### 動作ステップ

1. chat TUI 起動時、`solutionPath` を監視する `watch.Watcher` を作る (基準 mtime = 起動時点)。
2. TUI のイベントループで一定間隔 (200ms) ごとに mtime を poll する (bubbletea の tea.Cmd を再発行する形。`readLineCmd` と同じ流儀)。
3. 変化を検知したら (debounce 120ms 後):
   - チャットに `(解答ファイルが更新されました — 新しいプログラムを起動します)` を 1 行追加。
   - **実行中の子プロセスを kill** し、最新ファイルで再 spawn する (既存の `restart()` を流用。区切り `─── session #N ───` も出る)。
   - 監視ポーリングは継続する (リロード後も次の保存を拾う)。
4. ユーザ入力・子の出力・[r]/auto-restart・Ctrl+C/Ctrl+D 等の既存操作はそのまま動く。

### セッション境界の整合 (epoch)

mid-session で子を kill して再 spawn すると、**旧セッションの stream goroutine** (`readLineCmd`) が遅れて `streamEndMsg` を返し、新セッションの状態 (endedOut/endedErr) を誤って汚す恐れがある。これを防ぐため、各 `readLineCmd` に **epoch (= sessionN)** を持たせ、`chatLineMsg` / `streamEndMsg` に埋め込む。Update 側は **epoch が現行 sessionN と一致しないメッセージを破棄**する (旧 scanner の残響を無視)。

### 出力イメージ

```
 218ms ← Query? 1 2
       → 5
  12µs ← Answer: 42
(解答ファイルが更新されました — 新しいプログラムを起動します)
─── session #2 ───
   1ms ← Query? 1 2       # 最新ファイルで再起動された子の出力
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| chat 中に解答ファイルを保存 | info 行 → 実行中の子を kill → 最新ファイルで再 spawn (session 番号 +1) |
| 子が既に終了して [r] 待ち中に保存 | リロード (新セッション開始。awaitingRestart を解除) |
| auto-restart 中に保存 | 即リロード (auto-restart の再起動と同じ経路) |
| 連続保存 (エディタの複数 write) | debounce で 1 回のリロードにまとめる |
| ファイルが一時的に消える→再出現 (atomic save) | mtime 変化として拾い、再出現後の内容で再 spawn |
| 監視対象が無い / 非 TTY | watcher を作らず、watch-reload は無効 (従来どおり) |
| リロード後の旧 stream の遅延イベント | epoch 不一致で破棄され、新セッションを汚さない |

- **非破壊**: 解答ファイル・キャッシュ・judge には書き込まない。読むのは mtime のみ。子プロセスの差し替え以外に副作用はない。
- **既存操作は不変**: 入力履歴・[r] restart・auto-restart・Ctrl+C (kill 終了) ・Ctrl+D (chat 終了)・出力タイミング表示 (要件 019) はそのまま。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `chatModel` に `watcher *watch.Watcher` を追加。`chatLineMsg`/`streamEndMsg` に `epoch int` を追加し、`readLineCmd` を epoch 付きに。`fileChangedMsg` と `pollWatchCmd` を追加 (200ms ポーリング)。Update に `fileChangedMsg` 分岐 (info 行 + restart)。`restart()` を「kill してから spawn」に (実行中の子も差し替えられるよう)。stale epoch の破棄。`ChatHeader` に `WatchPath string` を追加し、非空なら watcher を作る |
| `internal/runexec/runexec.go` | `ChatHeader` に `WatchPath string` を追加。`runChatMode` で `solutionPath` をセット |
| `cmd/atcoder/adhoc.go` | `runChat` で `runexec.ChatHeader.WatchPath` を `ui.ChatHeader.WatchPath` に渡す |
| `internal/ui/chat_test.go` | epoch による stale メッセージ破棄、`fileChangedMsg` でのリロード経路 (注入) のユニットテスト |
| `docs/tools/atcoder-test-usage.md` / `-architecture.md` | interactive の説明に「保存でリロードされる」旨を追記 |
| `docs/tools/todo.md` | 項目 S として記載し、本要件へ相互リンク |

### chat.go の追加点 (素描)

```go
// ChatHeader に追加:
//   WatchPath string // 非空なら解答ファイルを監視して保存で子を再 spawn する

type chatLineMsg struct {
    kind  string
    text  string
    at    time.Time
    epoch int // 発行時の sessionN。現行と不一致なら破棄 (旧 scanner の残響)
}

type streamEndMsg struct {
    kind  string
    epoch int
}

type fileChangedMsg struct{ changed bool }

// pollWatchCmd は interval だけ待って watcher を 1 回 poll し、fileChangedMsg を返す。
// fileChangedMsg を受けるたびに再発行して継続ポーリングする (readLineCmd と同じ流儀)。
func (m *chatModel) pollWatchCmd() tea.Cmd
```

- watch 間隔・debounce は `internal/ui` 内の定数 (`chatWatchInterval = 200ms` / `chatWatchDebounce = 120ms`、`test --watch` と同値)。
- `restart()` は `m.handle.Kill()` (実行中なら終了。終了済みなら無害) → `m.handle.Wait()` (reap) → spawn、の順にする。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 再 spawn 失敗 (ファイル消失・実行不可) | 既存の restart と同じく "restart failed: …" を出して chat を終了 | (chat の戻り値に従う) |
| 監視 stat 失敗 | mtime ゼロ値として扱い、誤検知しても再 spawn するだけ (無害) | — |
| WatchPath 空 | watcher を作らず watch-reload 無効 | — |

- 新たな exit code 経路は増やさない。interactive の終了コード規約 (要件 013) は不変。

## 非機能要件

- **既存非破壊**: judge・バッチ test・非 TTY interactive・既存 chat 操作の挙動・exit code は不変。watch-reload は chat TUI に WatchPath が渡ったときだけ動く純粋な追加。
- **副作用最小**: 読むのは解答ファイルの mtime だけ。書き込みは一切しない。リロードは子プロセスの差し替えのみ。
- **依存ゼロ追加**: 既存の `internal/watch` を流用。`go.mod` を変えない。
- **応答性**: ポーリングは 200ms 間隔の軽量 stat。chat の入力・描画をブロックしない (tea.Cmd の goroutine で実行)。
- **堅牢性**: mid-session リロードでも epoch タグで旧セッションの残響を無視し、状態を壊さない。

## 将来の拡張ポイント

- `--no-reload` で常時リロードを切る opt-out。
- 監視対象に**自作ライブラリ / 複数ファイル**を含める。
- 非 TTY interactive での擬似リロード (passthrough を再起動)。
- 変更ファイル名や mtime を通知に含める。

## 用語

- **watch-reload**: chat TUI 中に解答ファイルの保存を検知して子プロセスを最新ファイルで再 spawn すること。
- **epoch**: セッション世代番号 (= sessionN)。`readLineCmd` が発行時に持ち、Update が現行と照合して旧セッションの stream イベントを破棄する。
- **再 spawn (reload / restart)**: 実行中の子を kill して最新ファイルで起動し直すこと。区切り `─── session #N ───` を伴う。
- chat TUI / interactive / spawner は要件 013 (test/run 統合) に準拠。

## 関連ドキュメント

- `docs/tools/requirements/013-unify-test-run.md` (interactive / chat TUI / spawner の導入元)
- `docs/tools/requirements/019-interactive-output-timing.md` (出力行の経過時間表示。共存する)
- `docs/tools/requirements/018-start-command.md` 系 (`start` の外側 watch ループ)
- `docs/tools/atcoder-test-usage.md` / `atcoder-test-architecture.md` (interactive の手引・内部設計)
- `docs/tools/todo.md` (上位ロードマップ。項目 S)
