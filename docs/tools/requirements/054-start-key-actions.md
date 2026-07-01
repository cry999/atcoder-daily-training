# `atcoder start` キーアクション 要件定義

## 概要

`atcoder start` の watch ループに、待機中の**キー操作**を足す。`q` (または `Ctrl+C`) で終了、`i` で**インタラクティブモード** (既存の chat。`test --interactive` と同じ) に移り、抜けると start の watch 状態に戻る。保存検知での自動再実行 (既存) はそのまま並走する。

watch 待機中だけ端末を raw モードにして 1 キーを拾い、それ以外 (テスト実行・chat) は通常モードに戻す薄い入力層。判定・実行・chat 本体のロジックは増やさず、`watch` (mtime) と `runexec` の chat を束ねる。

## 背景・目的

- `start` で watch 中、対話問題を試したくなったら一度 `Ctrl+C` で抜けて `atcoder test --interactive` を別に叩く必要がある。watch を抜けずに `i` で対話に入り、終わったら watch に戻れると往復が消える。
- 終了も `Ctrl+C` だけでなく `q` で明示的に抜けたい (raw モードでは `Ctrl+C` はシグナルにならずバイトで届くため、どのみちキー処理が要る)。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | `atcoder start` の watch 待機中のみ | `test --watch` への横展開 |
| キー | `q`/`Q`/`Ctrl+C` = 終了、`i`/`I` = インタラクティブ | `r` = 強制再実行、`s` = 提出準備 など |
| インタラクティブ | 既存 chat (`runAdHoc` の interactive) をそのまま起動し、抜けたら watch に戻る | — |
| 端末 | raw モードは**待機中だけ**。テスト実行・chat 中は通常モード | — |
| 非 TTY | 従来どおり watch 自体が exit 2 (start は元々 TTY 必須) | — |
| raw 化に失敗 | キー無効で mtime のみの watch に**フォールバック** (Ctrl+C で終了) | — |

### 境界 (他機能との分担)

- mtime 監視は `internal/watch` (004)。本機能は待機中のキー入力を `watch.Changed()` (非ブロッキング poll) と多重化する。`WaitForChange` (test --watch 用) は不変。
- インタラクティブ chat は `runexec` + `internal/ui` の chat TUI (013)。`start` から既存の `runAdHoc(..., interactive=true)` を呼ぶだけ。bubbletea が自前で端末を管理するので、起動前に start 側の raw モードは解除しておく。
- `test --watch` の挙動・`start` の `--until-pass` 等は不変。

## CLI 仕様

フラグ追加なし。`atcoder start <contest> --task <task>` の watch 待機中に以下のキーが効く:

| キー | 動作 |
|---|---|
| `q` / `Q` / `Ctrl+C` | watch を終了 (exit 0) |
| `i` / `I` | インタラクティブモード (chat) を起動。抜けたら再実行して watch に戻る |
| (解答ファイルを保存) | 従来どおり自動再実行 |
| その他のキー | 無視 |

### 処理ステップ (待機フェーズ)

1. `/dev/tty` を開き raw モードにする (失敗したら mtime のみの待機にフォールバック)。
2. 別 goroutine で 1 バイトずつ読み、キーをチャネルへ。本体は `select` で多重化:
   - 一定間隔で `watch.Changed()` を poll → 変化があれば**再実行**へ。
   - キー → `q`/`Q`/`Ctrl+C`(0x03) で**終了**、`i`/`I` で**インタラクティブ**、他は無視。
   - `ctx` (SIGINT) done → 終了 (raw 中は通常 byte 0x03 で来るが保険)。
3. アクション確定で raw モードを解除 (defer) し goroutine を止める (tty close)。
4. **再実行**: ループ先頭へ (画面クリア → テスト実行)。`--until-pass` 指定で全通過なら exit 0。
5. **インタラクティブ**: 通常モードで `runAdHoc(contest, task, lay, "", "", true, ...)` を起動 (chat)。抜けたらループ先頭へ (再実行して watch に戻る)。
6. **終了**: 改行して exit 0。

### 出力イメージ

```
▸ watch  exercise/2026/06/11/abc457_d.py

[01] PASS ...
Result: 3/3 PASS

watching … — save to re-run, [i] interactive, [q]/Ctrl+C quit
# ここで i を押す → chat TUI が立ち上がり、抜けると上の watch 画面に戻る
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| 待機中に `q` / `Ctrl+C` | exit 0 |
| 待機中に `i` | chat を起動 → 抜けたら再実行して watch 継続 |
| 待機中に保存 | 自動再実行 (従来) |
| `--until-pass` で全通過 | exit 0 (キー操作と独立) |
| raw 化失敗 (tty 開けない等) | キー無効・mtime のみの watch にフォールバック (機能低下のみ、エラーにしない) |
| テスト実行中・chat 中のキー | start のキー層は無効 (raw は待機中だけ)。chat 中は bubbletea が処理 |

- **既存非破壊**: `test --watch` (`runTestWatch`) は無改修。`start` 用に `runStartWatch` を別に持つ。`watch` には非ブロッキング poll `Changed()` を足すだけ (`WaitForChange` は不変)。
- **端末を汚さない**: raw モードは待機中だけ on、defer で必ず restore。chat 起動前は通常モードに戻す。
- 解答ファイルには触れない。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/watch/watch.go` | 非ブロッキング poll `Changed() bool` を追加 (`WaitForChange` と debounce ロジックを共有/温存) |
| `internal/watch/watch_test.go` | `Changed()` のテスト (変化なし=false、変化あり=true で基準更新) |
| `cmd/atcoder/start.go` | `runStartWatch` (キー多重化ループ)・`waitForAction`・純粋関数 `keyToAction(byte) startAction`。`cmdStart` を `runStartWatch` 呼び出しに変更。interactive 起動は既存 `runAdHoc` を再利用 |
| `cmd/atcoder/start_test.go` | `keyToAction` のテーブルテスト (q/Q/Ctrl+C→quit、i/I→interactive、他→none) |
| `internal/ui/watch.go` | `StartWatchFooter(path)` を追加 (キーヒント入りの待機案内) |
| `docs/tools/usage/start.md` | キー操作を追記 |
| `docs/tools/todo.md` | ロードマップ P にキーアクションを追記 |

### 素描

```go
// internal/watch
// Changed は 1 回だけ mtime を poll し、基準から変化していれば debounce 後に基準を
// 更新して true を返す (ブロックしない)。キー入力と多重化したい start が使う。
func (w *Watcher) Changed() bool

// cmd/atcoder/start.go
type startAction int
const (actNone startAction = iota; actRerun; actQuit; actInteractive)

// keyToAction は 1 バイトのキー入力をアクションに写す純粋関数。
//   'q'/'Q'/0x03(Ctrl+C) → actQuit、'i'/'I' → actInteractive、他 → actNone
func keyToAction(b byte) startAction

// runStartWatch は start 用の watch ループ。待機中のキー (q/i) を mtime と多重化する。
func runStartWatch(contest, task string, lay layout.Layout, refresh bool,
    buildOpts func(bool) testexec.Options, untilPass, debug bool,
    timeout time.Duration, tolerance float64) (int, error)
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 非 TTY | "--watch requires a terminal" (start の既存挙動) | 2 |
| `/dev/tty` 開けない / raw 化失敗 | mtime のみの watch にフォールバック (キー無効)。エラーにしない | 0 (Ctrl+C 終了時) |
| interactive (chat) 起動失敗 | エラー表示後、watch に戻る (致命的にしない) | — |
| `q` / `Ctrl+C` / `--until-pass` 全通過 | 正常終了 | 0 |

## 非機能要件

- **薄い入力層**: 新しい判定・実行・chat ロジックを増やさない。`watch`・`runexec`(chat)・`ui` を束ねるだけ。
- **既存非破壊**: `test --watch` 不変。`watch.WaitForChange` 不変 (`Changed` を追加するのみ)。
- **graceful degradation**: raw 化できない環境ではキー無効で従来の watch として動く。
- **テスト**: `keyToAction` と `watch.Changed()` をユニットテストで固定。端末 raw・chat 遷移は TTY 必須のため手動確認 (run.sh は非 TTY=exit 2 のみ assert、従来どおり)。

## 将来の拡張ポイント

- `test --watch` にも同じキー層を展開。
- 追加キー: `r` 強制再実行、`s` 提出準備 (`--submit` 相当)、`?` ヘルプ。
- watch ループ全体を bubbletea 化して、ライブ進捗とキー操作を一体にする。

## 用語

- **キーアクション**: watch 待機中の 1 キー入力に対応する動作 (終了 / インタラクティブ / 無視)。
- **インタラクティブモード**: 子プロセスと live 対話する chat (013 / `test --interactive`)。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- `docs/tools/requirements/018-start-command.md` (start 本体)
- `docs/tools/requirements/004-exercise-test-watch.md` (watch / mtime ポーリング)
- `docs/tools/requirements/013-unify-test-run.md` (interactive chat の統合元)
- `docs/tools/usage/start.md` (利用手引)
