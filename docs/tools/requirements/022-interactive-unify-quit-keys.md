# インタラクティブ chat の終了キーを `Ctrl+C` / `Ctrl+D` で一本化 要件定義

## 概要

インタラクティブ chat の `Ctrl+C` と `Ctrl+D` を、**どちらも「chat を終了 (子を kill して quit)」**に統一する。前回 (021) で `Ctrl+D` を chat 終了に変えた結果、非 auto-restart では `Ctrl+C` (中断) と `Ctrl+D` (終了) が同義になり、唯一の差は auto-restart 時の「graceful 停止 (現セッション終了まで待つ) かどうか」だけになっていた。「途中再開は不要」との方針に沿い、その **graceful 停止 / 中断という区別 (機能) を撤去**してキーの意味を 1 つにする。

`Ctrl+C` キー自体は残す (bubbletea の raw モードでは `Ctrl+C` を自前で処理しないと無反応になり force-quit 手段を失うため)。両キーとも同じ「終了」に倒すことで、区別の複雑さ (`ctrlDActionFor` / `quitOnChildExit` / 現セッション後 quit) を消す。

## 背景・目的

- 021 で `Ctrl+D`=chat 終了 (子に EOF を送らない) に変更。結果、非 auto-restart では `Ctrl+C` と `Ctrl+D` がどちらも「子を kill して quit」で**同義**。
- 唯一の差は auto-restart 時: `Ctrl+C`=即 kill して quit、`Ctrl+D`=再実行を止めて現セッションの子が自然終了したら quit (graceful)。ユーザは**「途中再開は不要」**= この graceful 停止の区別が不要との意向。
- よって「中断 vs graceful 終了」という区別 (= 中断機能) を撤去し、両キーを単純な「終了」に揃える。区別が消えれば `ctrlDActionFor` / `quitOnChildExit` / 現セッション後 quit の分岐も不要になり、実装も単純化する。

### 調査結論

| 観点 | 結論 |
|---|---|
| 非 auto-restart の `Ctrl+C` vs `Ctrl+D` | どちらも kill+quit で**同義** (021 以降) |
| 唯一の差 | auto-restart 時の `Ctrl+D` graceful 停止のみ。ユーザ的に不要 |
| `Ctrl+C` キーを消せるか | **不可 (footgun)**。bubbletea (v1.3.x) の raw モードでは `Ctrl+C` は KeyMsg として届き、自前で処理しないと無反応 = force-quit 不能になる。キーは残す |
| 採る形 | 両キーとも「終了 (kill+quit)」に統一。区別の機構を撤去 |

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | `test --interactive` の chat TUI (`internal/ui/chat.go`) | — |
| `Ctrl+C` / `Ctrl+D` | **どちらも chat 終了 (子を kill して quit)** | — |
| 撤去 | `ctrlDAction`/`ctrlDActionFor`/`ctrlDStopAfterSession`/`quitOnChildExit` と「現セッション後 quit」分岐 | — |
| auto-restart (R) | 子の自然終了で自動再実行は不変。停止は `Ctrl+C`/`Ctrl+D` で即 quit (graceful 停止は廃止) | 必要なら別キーで graceful 停止を復活 |
| `Enter` / 履歴 / 出力タイミング表示 | 不変 | — |

## CLI 仕様 (キー操作)

| キー | 新動作 | 旧動作 (021 時点) |
|---|---|---|
| `Enter` | 1 行を子へ送信 | 同左 |
| `Ctrl+C` | **chat 終了** (子を kill して quit) | 同左 (即中断) |
| `Ctrl+D` | **chat 終了** (子を kill して quit) — `Ctrl+C` と同一 | auto-restart 時は graceful 停止、他は kill+quit |
| `↑`/`↓` | 入力履歴 | 同左 |

- `Ctrl+C` と `Ctrl+D` は完全に同義 (どちらも終了)。区別は無い。
- auto-restart 中も両キーは即 quit (現セッションの完了を待たない)。

### 出力イメージ

```
> 3
← QUERY 1
# Ctrl+C でも Ctrl+D でも chat を終了 (子は kill される)
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `Ctrl+C` / `Ctrl+D` | 子を kill して chat 終了 (exit 0) |
| `Enter` | 子へ 1 行送信 (不変) |
| 子が自然終了 (auto-restart ON) | 再実行 (不変) |
| 子が自然終了 (auto-restart OFF) | `(child process exited)` 表示で quit (不変) |

- **既存非破壊 (それ以外)**: `Enter`・履歴・出力タイミング表示・auto-restart の自動再実行は不変。撤去するのは「中断 vs graceful 終了」の区別と関連状態のみ。
- **後方互換の破壊点**: auto-restart 時の `Ctrl+D` graceful 停止 (現セッション終了まで待つ) が無くなり、即 quit になる。
- 解答ファイルには触れない。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `KeyCtrlC` と `KeyCtrlD` を同一処理 (kill+quit) に。`ctrlDAction`/`ctrlDActionFor`/`ctrlDStopAfterSession`、`quitOnChildExit` フィールド、`streamEnd` の `quitOnChildExit` 分岐を撤去。placeholder と auto-restart ヒント文言を更新 |
| `internal/ui/chat_test.go` | `TestCtrlDActionFor` と `TestStreamEndQuitsWhenQuitOnChildExit` を撤去 (対象機構が無くなるため)。`TestStreamEndQuitsWhenNoAutoRestart` は維持 |
| `docs/tools/atcoder-test-usage.md` | interactive 節の `Ctrl+C`/`Ctrl+D` 説明を「どちらも終了」に統一 |
| `docs/tools/todo.md` | R の注記を「graceful 停止は廃止、両キーで即 quit」に補正、本要件へリンク |

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `Ctrl+C` / `Ctrl+D` / 子の自然終了 | 正常終了 | 0 |
| (キー操作起因のエラーは無い) | — | — |

## 非機能要件

- **force-quit の安全性**: `Ctrl+C` キーの処理は残す。bubbletea raw モードでは自前処理しないと `Ctrl+C` が無反応になるため、削除しない (両キーを「終了」に揃えるだけ)。
- **単純化**: 区別のための状態 (`quitOnChildExit` 等) と純粋関数 (`ctrlDActionFor`) を消し、キー処理を 2 行に統一。
- **テスト**: 撤去対象を参照するテストを削除。chat TUI 全体 (TTY 必須) は手動確認 (run.sh は非 TTY)。

## 将来の拡張ポイント

- もし「現セッションを最後まで見てから停止」を再び欲したら、別キー (例 `Ctrl+\\` や `s`) に graceful 停止を割り当てる。
- `start` のキー層 (019) と chat キーの統一ヘルプ (`?`)。

## 用語

- **中断 / graceful 停止**: (旧) `Ctrl+C`=即 kill、`Ctrl+D`(auto-restart)=現セッション終了まで待って停止。本変更で区別を撤去し、両キー「終了」に統一。
- (`contest_id` / `task_id` は既存要件に準拠)

## 関連ドキュメント

- `docs/tools/requirements/021-interactive-ctrl-d-quit.md` (前段: `Ctrl+D`=chat 終了)
- `docs/tools/requirements/020-interactive-auto-restart-flag.md` (auto-restart / R)
- `docs/tools/atcoder-test-usage.md` (interactive 利用手引)
