# insert モードの scrollback ページスクロール 要件定義

> **注記 (要件 [071](071-chat-scroll-mode.md) で置換)**: 本要件が定めた insert モードの scrollback スクロール (`PageUp`/`PageDown`/`Ctrl+B`/`Ctrl+F`) は撤去し、専用の**スクロールモード**へ集約した。insert からは `PageUp`/`PageDown` で**スクロールモードに入る**形になり、`Ctrl+B`/`Ctrl+F` は textinput の既定に戻した。追従 (`scrolled`) の仕組みは 071 が引き継いでいる。以下は経緯・設計背景の記録として残す。

## 概要

chat の **insert モード (通常のチャット入力時)** でも、`PageUp`/`PageDown` (および `Ctrl+B`/`Ctrl+F`) で scrollback (過去の入出力) を 1 ページずつ遡れるようにする。現状スクロールは command モード限定 ([033](033-command-mode-scrollback-paging.md)) で、過去の出力を見るには毎回 `Esc` で command モードに入る必要がある。insert モードでは `PageUp`/`PageDown` が未処理で textinput に流れて実質無視されているので、これをスクロールに割り当てる。追従挙動 (上スクロール中は出力到着で最下部に引き戻さない・最下部に戻したら追従再開) は 033 と同一にする。

## 背景・目的

- 編集ループ中、解答の出力が流れていくと過去のケースの出力を見返したくなるが、insert モードにはスクロールキーが無い。`Esc` → command モードに入ってから `PageUp` する二度手間になっている。
- 033 は insert モードを「キーが埋まっておりスクロール用の空きが乏しい」として対象外にした。だが `PageUp`/`PageDown` は insert モードでも**実際には未使用** (textinput に流れて無視) であり、`Ctrl+B`/`Ctrl+F` も chat では未使用。これらを使えば既存キー (`Enter`=送信・`↑`/`↓`=入力履歴・`Ctrl+C/D/S/E`) と衝突せずスクロールを足せる。
- 033 の `cmdScrolled` 機構 (sticky スクロール + `refreshViewport` の引き戻し抑止) をそのまま insert モードへ広げるだけで実装できる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象モード | insert モード (command モードは 033 で実装済み・不変) | builder モード |
| キー | `PageUp`/`Ctrl+B` で 1 ページ上、`PageDown`/`Ctrl+F` で 1 ページ下 | 行単位スクロール・先頭/末尾ジャンプ |
| 追従挙動 | 033 と同一: 上スクロール中は出力到着で引き戻さない。`PageDown` で最下部に達したら追従再開 | — |
| 解除 | `Enter` 送信時に最下部へ戻し追従再開。`Ctrl+C` 中断・`Ctrl+D` リセット時も最下部へ | — |
| 状態フィールド | `cmdScrolled` → `scrolled` に改名 (command/insert 双方で使うため一般化) | — |

### キー選定の注意

`Ctrl+B`/`Ctrl+F` は bubbles textinput の既定でカーソルを 1 文字左右に動かすバインドだが、本機能で insert モードでは scrollback ページングに横取りする。入力行のカーソル移動は `←`/`→` で従来どおり可能なので実用上の支障は小さい。command モードの `:` 行編集では `Ctrl+B`/`Ctrl+F` をカーソル移動に残す (command モードのスクロールは `PageUp`/`PageDown` のみ・033 のまま不変)。

## CLI 仕様

新フラグ・新サブコマンドは増やさない。insert モードのキーが増えるだけ。

### キー (追加分・insert モード)

| キー | 動作 |
|---|---|
| `PageUp` / `Ctrl+B` | scrollback を 1 ページ上へ。`scrolled = true` (以降の出力で最下部に引き戻さない) |
| `PageDown` / `Ctrl+F` | scrollback を 1 ページ下へ。最下部に達したら `scrolled = false` (追従再開) |
| `Enter` (送信) | 従来どおり送信。送信時に `scrolled = false` で最下部へ戻し追従再開 |
| `↑`/`↓` | 従来どおり入力履歴ナビ (不変) |
| その他 | 従来どおり textinput へ (不変) |

### 処理ステップ

1. insert モードで `PageUp`/`Ctrl+B` → `scrollUp()` (`viewport.ViewUp()` + `scrolled = true`)。
2. `PageDown`/`Ctrl+F` → `scrollDown()` (`viewport.ViewDown()`、`AtBottom()` なら `scrolled = false`)。
3. 出力到着 (`chatLineMsg`) → `refreshViewport()`。`scrolled` なら `SetYOffset` で位置維持、でなければ `GotoBottom()` (033 と同じ分岐)。
4. `Enter` 送信 / `Ctrl+C` 中断 / `Ctrl+D` リセット → `scrolled = false` にして最下部へ戻す。

## 動作仕様

| 項目 | 挙動 |
|---|---|
| スクロール機構 | `scrollUp`/`scrollDown` を command/insert で共有 (重複排除)。`viewport` 操作は既存のまま |
| 追従抑止 | `scrolled` 中は `refreshViewport` が `YOffset` を維持。033 と同一ロジック |
| 送信との関係 | `Enter` 送信は最下部へ戻して live view を見せる (送ったものと新出力が見える) |
| command モード | 不変。`PageUp`/`PageDown` のみ。`Ctrl+B`/`Ctrl+F` は `:` 行のカーソル移動のまま |
| builder モード | 対象外 (不変) |
| start 分割画面 | chat の `scrolled` は chat 内部で完結。分割画面 (startsplit) は非依存・不変 |
| 子プロセス・判定・exit code | 不変。スクロールは表示のみ |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `cmdScrolled` → `scrolled` に改名 (宣言・`refreshViewport` の参照)。`scrollUp()`/`scrollDown()` ヘルパ追加。insert ハンドラに `KeyPgUp`/`KeyCtrlB`→`scrollUp`、`KeyPgDown`/`KeyCtrlF`→`scrollDown` を追加。`submitLines`・`restart` で `scrolled = false` |
| `internal/ui/chat_casebuilder.go` | command モードの `KeyPgUp`/`KeyPgDown` を `scrollUp`/`scrollDown` 呼び出しに置換 (挙動不変)。`cmdScrolled` 参照を `scrolled` に改名 |
| `internal/ui/chatscroll_test.go` | `cmdScrolled` → `scrolled` に追従。insert モードで `PageUp`/`Ctrl+B` がスクロールし出力で引き戻さない・`PageDown`/`Ctrl+F` で追従再開・`Enter` 送信で最下部復帰、を固定。command モードの既存テストは挙動不変のまま維持 |
| `docs/tools/usage/start.md` | チャットキーの説明に insert モードのスクロール (`PageUp`/`PageDown`/`Ctrl+B`/`Ctrl+F`) を追記。command モード限定の記述を更新 |
| `docs/tools/todo.md` | 本項目を追加し ✅ DONE。033 と相互リンク |

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| scrollback が 1 画面に収まる (スクロール不要) | `ViewUp`/`ViewDown` は no-op (viewport がクランプ)。`scrolled` は立つが `refreshViewport` で最下部=現状維持。実害なし |
| (注) chat はキー操作の TUI。スクロールは exit code に影響しない |

## 非機能要件

- **既存非破壊**: command モード・builder モード・入力履歴 (`↑`/`↓`)・送信・子プロセス・判定・exit code・start 分割画面は不変。`cmdScrolled`→`scrolled` の改名は内部リファクタで挙動を変えない。
- **キー衝突回避**: `PageUp`/`PageDown`/`Ctrl+B`/`Ctrl+F` は insert モードで未使用だった (textinput に流れて無視 or カーソル移動)。`Ctrl+B`/`Ctrl+F` の横取りで失うのは入力行のカーソル 1 文字移動のみ (`←`/`→` で代替可)。
- **一貫性**: スクロール挙動・追従ロジックを command モードと完全に揃える (`scrollUp`/`scrollDown` 共有)。

## 将来の拡張ポイント

- 行単位スクロール (`Shift+↑`/`↓` 等)、先頭/末尾ジャンプ (`Home`/`End`)。
- builder モードのスクロール。
- スクロール中インジケータ (「上にスクロール中 / N 行下」)。

## 用語

- **scrollback**: chat の viewport が保持する過去の入出力ログ。
- **scrolled**: 上にスクロール中で、出力到着時に最下部へ引き戻さないことを示す内部フラグ (旧 `cmdScrolled`。command/insert 双方で使う)。
- **追従 (follow)**: 出力到着時に viewport を最下部 (最新) に保つ既定挙動。

## 関連ドキュメント

- `docs/tools/requirements/033-command-mode-scrollback-paging.md` (command モードのスクロール。本件はその insert 版・機構を共有)
- `docs/tools/requirements/051-interactive-ctrl-d-reset-then-quit.md` (insert モードのキー割当の前例)
- `docs/tools/usage/start.md` (チャットキーの説明の更新先)
