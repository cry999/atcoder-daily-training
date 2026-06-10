# インタラクティブ chat の `Ctrl+D` を「chat 終了」に変える 要件定義

## 概要

インタラクティブモード (`test --interactive` の chat TUI) の `Ctrl+D` を、**子プロセスへの EOF 送信 (stdin クローズ) から、chat 側の終了操作へ**変える。現状 `Ctrl+D` は子の stdin を閉じて EOF を送るため、入力を待っていた解答が `EOFError` 等で異常終了し、しかも chat はその子が終わるまで残る — ユーザの体感とずれる。`Ctrl+D` は atcoder CLI 側のキーとして扱い、子プロセスには渡さない。

## 背景・目的

- chat は **インタラクティブ問題**用 (judge と query/response をやり取りし、解答は自分で終了する)。この用途で解答が **stdin を EOF まで読む**ことはまずない (読んだらハングする)。よって `Ctrl+D` で EOF を送る現挙動に**この文脈での実益が無い**。
- EOF まで読む batch 的なプログラムを試したいなら、サンプル判定 (`test`) や `test --in <file>` (全入力 + EOF を流して出力をキャプチャ) が既に担う。chat で EOF を送る必要はない。
- 一方で現状は、`Ctrl+D` を「抜けたい」つもりで押すと子に EOF が渡り、子が異常終了し、chat には残る、という驚きがある。`Ctrl+D` を **chat の終了**に倒す方が直感に合う (REPL/シェルの `Ctrl+D` と同じ感覚)。

### 現挙動の調査結論

| 観点 | 結論 |
|---|---|
| `Ctrl+D`=EOF送信の実益 (この tool) | **無し**。interactive 問題の解答は EOF を読まない。EOF まで読む batch は `test --in` が担う |
| 現挙動の弊害 | 抜けるつもりの `Ctrl+D` が子に EOF → 異常終了、chat は残存 (driver と child の役割が混ざる) |
| 妥当な既定 | `Ctrl+D` は chat 終了 (atcoder CLI 操作)。子には渡さない |

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | `test --interactive` の chat TUI (`internal/ui/chat.go`) の `Ctrl+D` | — |
| 新挙動 | `Ctrl+D` = chat 終了 (子に EOF を送らない) | — |
| auto-restart (R) 連携 | `Ctrl+D` = 再実行ループを止めて**現セッションの子が終わったら quit** (EOF も kill もしない) | — |
| EOF 送信 | chat からは廃止 (batch は `test --in` で) | 必要が出れば別キーに割当 |
| `Ctrl+C` | 不変 (即中断: 子を kill して quit) | — |

## CLI 仕様 (キー操作)

chat 待機中のキー (フラグ変更なし):

| キー | 新動作 | 旧動作 |
|---|---|---|
| `Enter` | 1 行を子の stdin に送信 | 同左 (ただし「stdin 閉じた後は送れない」分岐は廃止) |
| `Ctrl+D` | **chat を終了** (auto-restart 時は現セッション終了後に quit)。子に EOF は送らない | 子の stdin を閉じて EOF 送信 |
| `Ctrl+C` | 即中断 (子を kill して quit) | 同左 |
| `↑`/`↓` | 入力履歴 | 同左 |

### 処理ステップ (`Ctrl+D`)

1. **auto-restart OFF** (既定): 子を kill して quit (「もう終わり」。`Ctrl+C` と同じく安全に抜ける)。
2. **auto-restart ON** (R): 再実行ループを解除し `quitOnChildExit` を立てる。**子は kill せず EOF も送らず**、現セッションの子が自然に終わったら restart せず quit する (R の「graceful 停止」を EOF なしで実現)。

子の stdin は chat 生存中ずっと開いたまま (`Enter` で常に送れる)。`stdinClosed` の状態と「閉じた後は送れない」分岐は廃止する。

### 出力イメージ

```
> 3
← QUERY 1
> 5
← QUERY 2
# ここで Ctrl+D → (auto-restart OFF) chat 即終了 / (ON) 現セッション終了後に quit
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `Ctrl+D` (auto-restart OFF) | 子を kill して chat 終了 (exit 0) |
| `Ctrl+D` (auto-restart ON) | restart を止め、現セッションの子が終わったら quit (kill/EOF なし) |
| `Ctrl+C` | 子を kill して即終了 (不変) |
| `Enter` | 子へ 1 行送信 (常に可能。stdin は閉じない) |
| 子が自然終了 | auto-restart ON なら restart、OFF なら従来どおり quit |

- **既存非破壊 (それ以外)**: `Ctrl+C`・`Enter`・履歴・出力タイミング表示・auto-restart の自動再実行は不変。変えるのは `Ctrl+D` の意味と、それに伴う `stdinClosed` 経路の除去のみ。
- **R との整合**: R の `Ctrl+D` は「graceful 停止」だったが EOF クローズに紐付いていた。EOF を外し、graceful 停止 (現セッション終了後 quit) は維持する。
- 解答ファイルには触れない。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `KeyCtrlD` 処理を「終了 / auto-restart 時は graceful 停止」に変更 (`handle.Stdin.Close()` をやめる)。`stdinClosed` フィールドと `Enter` の閉鎖後分岐を除去。placeholder 文言を更新。`Ctrl+D` の動作を純粋関数 `ctrlDActionFor(autoRestart bool)` に切り出し |
| `internal/ui/chat_test.go` (新規 or 追記) | `ctrlDActionFor` のテスト (auto-restart OFF→quit、ON→stopAfterSession) |
| `docs/tools/atcoder-test-usage.md` | interactive 節の `Ctrl+D` 説明を「chat 終了」に修正 (EOF 記述を削除) |
| `docs/tools/todo.md` | R の `Ctrl+D graceful` 注記を「EOF を送らず graceful 停止」に補正、本要件へリンク |

### 素描

```go
// ctrlDActionFor は Ctrl+D 押下時の chat の動作を決める純粋関数。
type ctrlDAction int
const (
    ctrlDQuit            ctrlDAction = iota // 子を kill して即 quit (auto-restart OFF)
    ctrlDStopAfterSession                    // restart を止め、現セッション終了後に quit (auto-restart ON)
)
func ctrlDActionFor(autoRestart bool) ctrlDAction
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `Ctrl+D` / `Ctrl+C` / 子の自然終了 | 正常終了 | 0 |
| (キー操作起因のエラーは無い。chat の終了パスは従来どおり) | — | — |

## 非機能要件

- **最小変更**: `Ctrl+D` の意味と `stdinClosed` 経路の除去に限定。`Ctrl+C`/`Enter`/履歴/auto-restart の他挙動は不変。
- **テスト**: `ctrlDActionFor` をユニットテストで固定。chat TUI 全体 (bubbletea, TTY 必須) の手触りは手動確認 (run.sh は非 TTY のため対象外)。
- **後方互換の破壊点 (明示)**: chat で `Ctrl+D` による EOF 送信が無くなる。EOF まで読むプログラムの確認は `test --in <file>` を使う。

## 将来の拡張ポイント

- どうしても chat から EOF を送りたい需要が出たら、別キー (例 `Ctrl+E`) に「子へ EOF」を割り当てる。
- `start` のキー層 (019) と chat のキーを統一的に説明するヘルプ (`?`)。

## 用語

- **EOF 送信**: 子プロセスの stdin を閉じて end-of-file を通知すること (本変更で chat から廃止)。
- **graceful 停止 (auto-restart)**: 現セッションの子が自然終了したら restart せず quit すること。
- (`contest_id` / `task_id` / `letter` は既存要件に準拠)

## 関連ドキュメント

- `docs/tools/requirements/013-unify-test-run.md` (interactive chat の統合元)
- `docs/tools/requirements/020-interactive-auto-restart-flag.md` (auto-restart / R)
- `docs/tools/atcoder-test-usage.md` (interactive 利用手引)
