# インタラクティブ chat の `Ctrl+C` を「プログラム中断・再起動」に再導入 要件定義

## 概要

インタラクティブ chat の `Ctrl+C` を、`Ctrl+D` (chat 終了) とは別の「**走っている子プログラムを中断 (kill) して、新しいプロセスでやり直す**」操作にする。中断後も chat には留まり、新セッション (`─── session #N ───`) として会話を続けられる。文言 (placeholder / 中断時の info 行 / auto-restart ヒント) で「Ctrl+C はプログラムを中断・再起動する」ことが分かるようにする。[022](022-interactive-unify-quit-keys.md) で `Ctrl+C`/`Ctrl+D` を「どちらも終了」に統一したが、両者の役割を再び分ける。

## 背景・目的

- [021](021-interactive-ctrl-d-quit.md)→[022](022-interactive-unify-quit-keys.md) の経緯で、いまは `Ctrl+C` も `Ctrl+D` も「子を kill して chat を quit」で同義。`Ctrl+C` に固有の役割が無く、キーが 1 つ遊んでいる。
- インタラクティブで子に入力を流していると、無限ループ・想定外の待ち・誤った入力で**実行が詰まる**ことがある。今は chat ごと終了して立ち上げ直すしかない。「今の実行だけ捨てて、chat に居たまま新しいプロセスでやり直す」キーが欲しい。
- ターミナルの `Ctrl+C` = 走っているプログラムを止める、という一般的な直感に沿わせる (ただし shell と違い chat は子との会話そのものなので、止めた後は**新プロセスを起こして会話を継続**する)。

## スコープ

| | 当面のスコープ (この要件) | 将来の拡張余地 |
|---|---|---|
| `Ctrl+C` | 子を kill → 即 fresh な子を再 spawn (新セッション)、chat に留まる。auto-restart ON/OFF を問わず同じ | 中断後に「停止して留まる/やり直す」を選ばせるサブメニュー |
| `Ctrl+D` | 従来どおり chat 終了 (子を kill して quit)。変更なし | — |
| 文言 | placeholder・中断時 info 行・auto-restart ヒントで「Ctrl+C = 中断・再起動 / Ctrl+D = 終了」を明示 | — |

**境界:**

- 終了キーの統一を決めた [022](022-interactive-unify-quit-keys.md) を**部分的に覆す**。`Ctrl+D` 側は不変、`Ctrl+C` だけ役割を戻す (中身は新挙動 = 「中断して留まる」)。
- 子の再 spawn は既存の `restart()` (watch-reload・auto-restart で実績あり) を流用する。新しい再起動機構は作らない。
- [024](024-interactive-case-builder.md) (ケースビルダー/command モード) とは独立。024 側の「Ctrl+C/Ctrl+D は終了」という旧記述はこの要件に合わせて更新する。
- 解答ファイル・キャッシュには触れない。

## CLI / TUI 仕様

新サブコマンド・新フラグは増やさない。挙動はインタラクティブ chat (`atcoder test --interactive …` / `atcoder start` の `i`) の内側だけで変わる。

### キー割り当て

| キー | 動作 | 備考 |
|---|---|---|
| `Ctrl+C` | 走っている子を kill し、`spawn()` で新しい子を起動して新セッションを開始。chat に留まる | `spawn` が無い経路 (再起動不可) では従来どおり kill して quit にフォールバック |
| `Ctrl+D` | chat を終了 (子を kill して quit)。子に EOF は送らない ([021](021-interactive-ctrl-d-quit.md)) | 変更なし |
| `Enter` / `Up` / `Down` | 送信 / 履歴 | 変更なし |

### 処理ステップ (`Ctrl+C`)

1. `spawn == nil` (再起動不可) なら、子を kill して `tea.Quit` (中断後に会話を継続できないため従来の終了に倒す)。
2. それ以外: info 行 `(プログラムを中断しました — 再起動します)` を追加。
3. `restart()` を呼ぶ — 現在の子を kill + reap し、`spawn()` で新しい子を起動、`sessionN++`、区切り行 `─── session #N ───` を出して新セッションを開始。
4. 旧セッションの scanner から遅れて届く `streamEndMsg` は epoch 不一致で破棄される (既存の仕組み) ので、中断が「自然終了→quit」に化けることはない。

### 文言 (新しい表示)

| 箇所 | 旧 (022) | 新 (この要件) |
|---|---|---|
| placeholder | `Enter で送信  /  Ctrl+C か Ctrl+D で終了` | `Enter で送信  /  Ctrl+C で中断・再起動  /  Ctrl+D で終了` |
| auto-restart ヒント | `(auto-restart on — Ctrl+C or Ctrl+D to stop)` | `(auto-restart on — Ctrl+C で中断・再起動 / Ctrl+D で終了)` |
| 中断時 info 行 | (なし) | `(プログラムを中断しました — 再起動します)` |

### 出力イメージ

```
   3ms ← 計算中...
(プログラムを中断しました — 再起動します)
─── session #2 ───
»
```

## 動作仕様

| 観点 | 仕様 |
|---|---|
| auto-restart との関係 | `Ctrl+C` は ON/OFF を問わず「中断 → 再起動」。auto-restart ON のときは「いま手動で再起動を促す」操作、OFF のときは「今の実行を捨ててやり直す」操作になる |
| 中断後の状態 | 常に新しい子が走っている状態に戻る (chat は使い続けられる)。子なしのアイドル状態にはならない |
| 旧セッションの残響 | 中断で kill した子の `streamEndMsg` は epoch 不一致で破棄。中断が quit に化けない |
| `Ctrl+D` 不変 | 終了挙動は [022](022-interactive-unify-quit-keys.md) のまま (子を kill して quit) |
| start との入れ子 | `start` → `i` → chat。chat 内で `Ctrl+C` を押すと chat 内で再起動 (start の watch には戻らない)。`Ctrl+D` で chat を抜けると従来どおり start の watch ループに戻る |
| 既存挙動非破壊 | `Enter` 送信・履歴・出力タイミング表示・watch-reload・auto-restart の自動再実行は不変 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat.go` | `KeyCtrlC`/`KeyCtrlD` を別ケースに再分割。`Ctrl+C` → 中断 info 行 + `restart()` (spawn 無しは kill+quit)。`Ctrl+D` → kill+quit (nil ガード追加)。placeholder と 2 箇所の auto-restart ヒント文言を更新 |
| `internal/ui/chat_test.go` | `Ctrl+C`=中断・再起動 (sessionN++・quit しない・中断 info)、`Ctrl+D`=quit、spawn 無し `Ctrl+C`=quit のテストを追加 (`m.handle=nil` で fake の Kill/Wait を回避する既存手筋) |
| `docs/tools/requirements/022-…md` | 「Ctrl+C も終了」を本要件で覆した旨の追記 (相互リンク) |
| `docs/tools/requirements/024-…md` / `decisions/0007-…md` | 「Ctrl+C/Ctrl+D は終了 (不変)」の旧記述を「Ctrl+D=終了 / Ctrl+C=中断・再起動」に更新 |
| `docs/tools/atcoder-test-usage.md` | interactive のキー説明を更新 (`Ctrl+C`=中断・再起動 / `Ctrl+D`=終了) |

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `Ctrl+C` 時に `spawn == nil` | 子を kill して `tea.Quit` (中断後に会話を続けられないため従来の終了へフォールバック) |
| `restart()` の `spawn()` が失敗 | 既存どおり: エラー行を出して `tea.Quit` (chat を継続できないため) |
| 中断対象の子が既に終了 | `Kill` は終了済みプロセスに無害。`restart()` がそのまま新セッションを起こす |
| この変更による exit code への影響 | なし。chat の戻り値 (最後のセッションの `ProcessResult`) と CLI の exit code 規約 (成功 0 / 実行時失敗 1 / 引数誤り 2) は不変 |

## 非機能要件

- **既存非破壊:** `Ctrl+D`・`Enter`・履歴・出力タイミング・watch-reload・auto-restart の挙動を変えない。解答ファイルに触れない。
- **端末キー堅牢性:** `KeyCtrlC` は bubbletea v1.3.10 の raw モードで確実に届く (命名済み Ctrl 組合せ)。[022](022-interactive-unify-quit-keys.md) で確認済みのとおり `Ctrl+C` ハンドラを置かないと無反応になるが、本要件はそのハンドラを中断に転用するだけなので force-quit 不能の懸念は無い (`Ctrl+D` が終了を担保)。
- **前方互換:** 再起動は既存 `restart()` を流用。[024](024-interactive-case-builder.md) の command モード実装時も、`Ctrl+C`=中断 / `Ctrl+D`=終了 の役割分担を前提にできる。

## 却下した代替案

- **中断後は子なしで停止して留まる (アイドル):** `Ctrl+C` で kill し、再 spawn せず `(中断しました — Ctrl+D で終了)` を出して待機する案。「中断=停止」に忠実だが、chat は子との会話そのものなので、子が居ないと入力が無効で会話を続けられない (再実行手段は解答保存か Ctrl+D しかない)。ユーザは「やり直して会話を続けたい」ため不採用。
- **auto-restart 設定に従う (ON=再起動 / OFF=停止して留まる):** メンタルモデルは整合的だが、`Ctrl+C` の振る舞いが文脈依存になり「いま何が起きるか」が読みにくい。一貫して「中断→再起動」に倒した。
- **旧 022 以前の `Ctrl+C` をそのまま復活 (kill して即 quit):** これは「中断」と銘打ちつつ chat も閉じる挙動で、ユーザの「chat には留まる」要望に反する。

## 用語

- **中断 (interrupt):** 走っている子プロセスを kill して、新しいプロセスでやり直すこと (`Ctrl+C`)。chat は終了しない。
- **終了 (quit):** chat 自体を閉じること (`Ctrl+D`)。子も kill する。
- **セッション:** 1 つの子プロセスの実行単位。中断・再起動・watch-reload・auto-restart で `sessionN` が増え、区切り行が出る。

## 関連ドキュメント

- 終了キー統一 (本要件が部分的に覆す): [022](022-interactive-unify-quit-keys.md)
- Ctrl+D を chat 終了にした経緯: [021](021-interactive-ctrl-d-quit.md) / auto-restart: [020](020-interactive-auto-restart-flag.md) / 出力タイミング: [019](019-interactive-output-timing.md)
- ケースビルダー / command モード: [024](024-interactive-case-builder.md) / [ADR 0007](../decisions/0007-interactive-command-mode-trigger.md)
- 利用手引: `docs/tools/atcoder-test-usage.md`
- ロードマップ: `docs/tools/todo.md` (R 節)
