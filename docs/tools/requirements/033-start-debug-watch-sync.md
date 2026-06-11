# `atcoder start` の chat `:debug` トグルを watch ペインへ反映 要件定義

## 概要

`atcoder start` の分割画面で、chat ペインの command モードから `:debug`（[030](030-chat-debug-cheat-commands.md)）で Debug を on/off したとき、その状態を **watch ペイン（上ペイン）にも反映**する。Debug は単なる表示切替ではなく **サンプル判定（verdict）を左右する**（`true → 子に DEBUG=1 を渡し、stdout の `[DEBUG]` 行を比較対象から除外）。現状 chat のトグルは chat ペインの `[DEBUG]` 行振り分けにしか効かず、watch ペインの再判定は **起動時 `-d` の値で固定**されたままなので、デバッグ print を仕込んだ解答は chat 側を on にしても watch ペインでは WA のまま表示され続けてしまう。この不整合を解消し、トグルと同時に watch ペインを **新しい Debug 値で即時に再判定**して verdict を揃える。あわせて watch ペインに Debug 状態を示す `[debug]` バッジを出す。

## 背景・目的

- [030] で `:debug` / `:set debug|nodebug` により chat 実行中に Debug をトグルできるようになったが、反映先は chat ペインの **表示（`[DEBUG]` 行の振り分け）だけ**だった。
- 分割画面の watch ペイン（[023](023-start-split-screen.md) / [028](028-start-watch-per-case.md)）は保存検知で `testexec.Run` を回して per-case verdict を出すが、その `Debug` は **起動時フラグ `-d`（`c.debug`）に焼き付き**で、chat の `:debug` トグルとは無関係に動く。
- そのため「`-d` なしで起動 → 解答に `[DEBUG]` print がある → watch は `[DEBUG]` 行込みで比較するので WA」という状況で、chat 側を `:debug` on にしても **watch の WA が消えない**。ユーザは「chat では debug 行として綺麗に見えているのに、watch では落ちている」という食い違いに混乱する。
- chat のトグルを watch の再判定にも波及させれば、`-d` を付け忘れて起動しても対話中に Debug へ切り替えるだけで watch の verdict が正しく揃う（起動時 `-d` と同じ判定になる）。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 反映トリガ | chat の `:debug` / `:set debug` / `:set nodebug`（[030]）による Debug 変化 | キー割当（例 `Ctrl+G`）からの直接トグル |
| watch への反映（判定） | Debug 変化時に watch ペインを **新 Debug 値で即時再判定**（`testexec.Run` の `Debug` に live 値を渡す） | per-case の `[DEBUG]` 出力プレビュー |
| watch への反映（表示） | watch ペインのタイトル行に `[debug]` バッジを出す（on のときだけ） | バッジの色・位置のカスタム |
| 状態の保持 | live Debug 値を分割画面（`startSplitModel`）が保持し、問題ナビ（[027](027-start-problem-navigation.md)）で再ターゲットしても引き継ぐ | コンテストをまたいだ永続化 |

### 境界

- **chat ペイン側の挙動は [030] のまま不変**：`m.header.Debug` のトグル・info 行・`[DEBUG]` 行の振り分け（以後の行のみ反映）は変えない。本要件は「その変化を watch にも伝える」配線を足すだけ。
- **chat の子プロセス（解答）の env は変えない**：chat 下ペインの子は起動時 `-d` の `extraEnv`（`DEBUG=1` 有無）のまま。`:debug` トグルで子を再 spawn したり env を差し替えたりはしない（[030] の境界を踏襲）。watch ペインの再判定（`testexec.Run` が回す別プロセス）にだけ live Debug を渡す。
- バッチ `test` / `run` の `-d` 経路（`runexec` / `testexec` の呼び出し側）・exit code・サンプル取得・キー操作は不変。
- `test --interactive` 単体（`NavEnabled=false`・分割画面でない）には影響しない。`:debug` は従来どおり chat 表示のトグルのみ。

## TUI 仕様

新フラグ・新コマンドは無し。既存の `:debug` / `:set debug|nodebug`（[030]）の副作用を watch ペインへ波及させる。

### 画面イメージ（watch ペイン）

Debug off（従来どおり）:

```
watch  exercise/2026/06/11/abc999_a.py
  ✗ 2/4   01 AC  02 WA  03 AC  04 AC   · 12:35:10
──────────────────────────────────────────────────
```

chat で `:debug` を on にした直後（解答の `[DEBUG]` 行が比較から外れ、再判定で AC に揃う + バッジ表示）:

```
watch  exercise/2026/06/11/abc999_a.py  [debug]
  ✓ 4/4   01 AC  02 AC  03 AC  04 AC   · 12:35:12
──────────────────────────────────────────────────
```

- タイトル行末尾に `[debug]` バッジ（Debug on のときだけ）。watch ペインは従来どおり 3 行を維持する。
- バッジ追加でタイトル行が幅を超える可能性に備え、`solutionPath` 等と同じ 1 行内に収め、行数は増やさない。

### 処理ステップ

1. chat の command モードで `:debug`（または `:set debug|nodebug`）が確定すると、[030] どおり `m.header.Debug` が更新され info 行が積まれる。
2. その確定処理は、新しい Debug 値を載せた **`DebugMsg{On bool}`** を `tea.Cmd` として発火する（[027] の `NavMsg` と同じ親への通知パターン）。
3. 親 `startSplitModel` が `DebugMsg` を受け取り、保持する live Debug 値（`m.debug`）を更新する。
4. 直ちに watch ペインのサンプル再判定を **新 Debug 値で 1 回**起動する（in-flight の旧判定は epoch を進めて破棄し、stale な結果で上書きされないようにする）。
5. 再判定結果（`splitSampleMsg`）が届いたら watch ペインの per-case verdict が新 Debug の判定に更新される。タイトル行のバッジは `m.debug` を見て描画する。

### Debug 値の流れ

- 起動時：`cmd/atcoder/start.go` の `c.debug`（`-d`/`--debug`）が `ChatHeader.Debug` と `runSamples` の初期 Debug を決める（従来どおり）。`startSplitModel.debug` はこの初期値で初期化する。
- 実行中：`:debug` トグル → chat の `m.header.Debug` 更新（chat 表示用）＋ `DebugMsg` 発火 → `startSplitModel.debug` 更新（watch 再判定用）。chat と watch の Debug は常に同じ値に揃う。
- 再ターゲット（[027] のナビ）：`startSplitModel.debug` は保持し、新ターゲットの chat header にも引き継ぐ（`-d` 起動値へ戻さない）。再判定は live `m.debug` で行う。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| chat で `:debug` on（`-d` なし起動） | watch を Debug=true で即再判定。`[DEBUG]` 行を除外した verdict に更新し、タイトルに `[debug]` を出す |
| chat で `:debug` off（`-d` あり起動） | watch を Debug=false で即再判定。`[DEBUG]` 行込みの verdict に戻し、バッジを消す |
| `:set debug` / `:set nodebug` | 明示 on/off。トグルと同じく watch を再判定して反映 |
| トグル時に watch 判定が in-flight | epoch を進めて旧判定（旧 Debug）の結果を破棄し、新 Debug で 1 回判定する |
| 再ターゲット（`:task`/`:contest`/`:e`） | live Debug を保持。新問題の watch 初回判定・chat 表示とも live Debug を使う |
| `test --interactive` 単体（分割画面でない） | 影響なし（`DebugMsg` を受ける親がいない＝従来どおり chat 表示のみ） |
| chat 子プロセスの env | 不変（起動時 `-d` のまま。`:debug` で再 spawn しない） |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/nav.go`（または `startsplit.go`） | `DebugMsg{On bool}` 型を追加（chat → 親への Debug 変化通知。`NavMsg` と同じ場所・流儀） |
| `internal/ui/chat_casebuilder.go` | `setDebug(on bool)` を `tea.Cmd` 返却に変更（`m.header.Debug` 更新＋info 行は従来どおり、加えて `DebugMsg{On: on}` を発火）。`toggleDebug` も `tea.Cmd` 返却。`applySet` を `tea.Cmd` 返却に変更し `debug`/`nodebug` で Cmd を返す。`execCommand` の `:debug` / `:set` 分岐で返った Cmd を伝播する |
| `internal/ui/startsplit.go` | `startSplitModel` に `debug bool` を追加。`RunSamples` / `runSamples` のシグネチャを `func(debug bool) SampleSummary` に変更し、`runSamplesCmd` で `m.debug` を渡す。`RunStartSplit` で `m.debug = t.Header.Debug` 初期化。`Update` に `DebugMsg` ケースを追加（`m.debug` 更新＋epoch 進めて再判定）。`retarget` で live `m.debug` を新ターゲットの chat header に上書きして引き継ぐ。`renderWatchPane` のタイトルに `m.debug` のとき `[debug]` バッジ |
| `cmd/atcoder/start.go` | `runSamples` を `func(debug bool) ui.SampleSummary` に変更し、`buildOpts` の `Debug` を引数 `debug` から取る（`c.debug` の焼き付けをやめる）。`StartTarget.RunSamples` への代入もシグネチャ更新 |
| `internal/ui/startsplit_test.go` | `DebugMsg` で `m.debug` が変わり再判定が起きる（epoch 進行・新 Debug で `runSamples` が呼ばれる）テスト、`renderWatchPane` のバッジ表示テストを追加。`RunSamples` のシグネチャ変更に伴う既存テストの更新 |
| `internal/ui/chat_casebuilder_test.go` | `setDebug`/`toggleDebug`/`applySet` が `DebugMsg` を発火する Cmd を返すテストを追加・更新 |
| `docs/tools/atcoder-start-usage.md` | watch ペインの説明に「chat の `:debug` が watch 判定にも反映される・`[debug]` バッジ」を追記 |
| `docs/tools/requirements/030-chat-debug-cheat-commands.md` | `:debug` が watch ペインにも波及する旨を追記（本要件へ相互リンク） |
| `docs/tools/todo.md` | 本項目を記載し本要件へ相互リンク |

### 型・シグネチャの素描

```go
// internal/ui (nav.go か startsplit.go)
// DebugMsg は chat が親 (startSplitModel) に Debug 変化を伝える tea.Msg。
// NavEnabled 相当の分割画面でのみ親が受ける (単体 chat では受け手がいない)。
type DebugMsg struct{ On bool }

// internal/ui (chat_casebuilder.go)
func (m *chatModel) setDebug(on bool) tea.Cmd   // header.Debug=on + info 行 + DebugMsg{On} を発火
func (m *chatModel) toggleDebug() tea.Cmd        // setDebug(!m.header.Debug)
func (m *chatModel) applySet(arg string) tea.Cmd // debug/nodebug は setDebug の Cmd を返す。他は nil

// internal/ui (startsplit.go)
type StartTarget struct {
    // ...
    RunSamples func(debug bool) SampleSummary // 再判定時の Debug を呼び出し側が渡す
}
// startSplitModel に debug bool を追加。runSamplesCmd は run(m.debug) を呼ぶ。
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| watch 再判定がテスト無し等で失敗 | 従来どおり `SampleSummary.Err` → ペインに `判定不可: …`（Debug 値に関係なく不変） |
| `:set <未知>` | [030] どおり `E518` 1 行。Debug は変えず再判定もしない（Cmd は nil） |
| exit code | 影響なし（表示・再判定のみ。引数誤り=2 / 実行時失敗=1 / 成功=0 は不変） |

## 非機能要件

- **既存非破壊**：chat ペインの [030] 挙動・キー・判定ロジック・exit code・非 TTY は不変。`:debug` を打たない限り従来どおり（起動時 `-d` の値で watch も判定）。
- **chat 表示と watch 判定の一貫性**：`m.header.Debug`（chat 表示）と `startSplitModel.debug`（watch 判定）は `:debug` のたびに同じ値へ揃う。片方だけ変わる状態を残さない。
- **stale 結果の非反映**：トグル直後の再判定中に旧 Debug の in-flight 結果が遅れて届いても、epoch 不一致で破棄して新 Debug の結果だけを反映する（[027] の target epoch を Debug 変化にも使う）。
- **ペイン高さ不変**：`[debug]` バッジはタイトル行内に収め、watch ペインを 3 行（`splitTopLines`）に保つ。chat 高さ計算を崩さない。
- **stdout を汚さない**：再判定は捕捉 Reporter のみ（[028] と同じ）。バッジ・info は TUI 内のみ。
- **前方互換**：`DebugMsg` の親通知は `NavMsg` と同じ仕組みに乗せ、将来 Debug を起点に watch 表示を増やしやすくする。`RunSamples` を `func(debug bool)` 化することで、将来 watch が判定オプション（tolerance 等）を実行時に切り替える拡張の足場にする。

## 将来の拡張ポイント

- watch ペインでの per-case `[DEBUG]` 出力プレビュー（落ちたケースのデバッグ行を覗く）。
- Debug を含む実行時オプション（tolerance・timeout 等）の chat → watch 反映（`RunSamples` の引数を options 構造体に拡張）。
- キー割当（`Ctrl+G` 等）からの Debug トグル。

## 用語

- **Debug（表示／判定）**：子 stdout の `[DEBUG]` 接頭辞行を比較対象から外す挙動（`-d` フラグ相当）。chat では別カテゴリ表示、watch（`testexec.Run`）では比較からの除外＋子への `DEBUG=1` 付与として効く。
- **watch ペイン**：`start` 分割画面の上ペイン。保存検知でサンプルを再判定して per-case verdict を出す（[028]）。
- **live Debug**：起動時 `-d` ではなく、実行中の `:debug` トグルで決まる現在の Debug 値（`startSplitModel.debug`）。

## 関連ドキュメント

- `:debug` コマンドの定義元：[030](030-chat-debug-cheat-commands.md)
- watch ペイン per-case verdict：[028](028-start-watch-per-case.md) / 分割画面：[023](023-start-split-screen.md) / 親通知パターン：[027](027-start-problem-navigation.md)
- 利用手引：`docs/tools/atcoder-start-usage.md`
- ロードマップ：`docs/tools/todo.md`
