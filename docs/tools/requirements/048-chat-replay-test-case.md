# 要件 048: chat の `:replay` が直近の `:test` ケースを再生する

## 概要

chat の command モードの `:replay` を、**直前に流した入力が `:test [case]` のサンプルケースだった場合は、そのケースの入力を再入力 + 再検証する**ように拡張する。「直近の操作を再生する」を一貫した意味づけにし、`:test n` でケースを流したあと `:replay` で同じケースをもう一度流せるようにする。

## 背景・目的

- 要件 [045](045-chat-run-sample-case.md) で `:test [case]` を入れ、キャッシュ済みサンプルの `.in` を子リスタート後に順送 + `.out` でライブ検証できるようになった。
- 要件 [039](039-chat-replay-previous-session.md) の `:replay` は **手入力したセッション入力だけ**を再生する。`:test` の順送は意図的に `record=false` で `sessionInputs` / chatlog に積まないため、`:test n` のあと `:replay` を打っても **手入力分しか流れず、いま試したケースを流し直せない**。
- 実際の使い方では「`:test 1` で落ちた → 解答を直した (watch reload) → もう一度同じケース 1 を流して直ったか確かめたい」という流れが頻出する。今はそのたびに `:test 1` を打ち直す必要がある。`:replay` 一発で「直前に流したもの」を再現できると、コード修正ループが速くなる。
- そこで `:replay` の意味を「**直近の操作 (手入力 or `:test` ケース) を再生する**」に一般化する。コマンドそのものの再実行ではなく、`:test n` が流した**入力の再入力**として処理する (子をリスタートしてその `.in` を順送し直す) ため、`:replay` の既存の実装基盤 (子リスタート + 順送) をそのまま使える。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 / 境界 |
|---|---|---|
| `:replay` の対象 | 手入力セッション入力 **に加えて** 直近の `:test` ケース入力 | 「直近 N 件の操作履歴から選ぶ」「`:replay test` / `:replay input` で明示指定」などは作らない (引数なしの単純再生を維持) |
| 再生時の検証 | `:test` ケースを再生するときは、そのケースの `.out` でライブ検証を**再度有効化** (`✓`/`✗`) | 手入力の再生では検証状態は変えない (従来どおり) |
| 優先順位 | 現セッションに手入力が残っていれば手入力を優先、無ければ直近 `:test` ケース、それも無ければ従来の手入力フォールバック | 「最後の操作が時系列で何だったか」を厳密に追跡する汎用タイムラインは持たない (下記「動作仕様」の近似で足りる) |
| 永続化 | しない (`:test` ケースの再生対象は**今回の chat 起動内**でのみ保持) | `:test` ケースを起動またぎで覚える必要は薄い (公式サンプルは `:test n` ですぐ呼べる) |
| `:test` 自体 | 挙動不変 (キャッシュ済みサンプルを順送 + ライブ検証)。流したケースを `:replay` 用に**覚える**処理だけ足す | — |

境界: 要件 045 (`:test`) / 039 (`:replay` の手入力再生) の挙動は据え置き、両者を `:replay` の優先順位の中で繋ぐだけ。新サブコマンド・新フラグ・新キーは増やさない。

## CLI 仕様

command モードのコマンド表・キーは不変。`:replay` の動作だけ拡張する。

### `:replay` の動作 (拡張後)

引数なし。実行すると、以下の優先順位で「再生対象」を選び、子をリスタートしてクリーンな状態から順送する。

1. **現セッションの手入力** (`sessionInputs`) — `:test` のあとに手入力していれば、それが直近の操作なので手入力を再生する。
2. **直近の `:test` ケース** (今回の起動内で最後に `:test [case]` で流したケース) — 現セッションに手入力が残っていなければ、そのケースの `.in` を再入力し、`.out` でライブ検証を再有効化する。
3. **直前に完了したセッションの手入力** (`prevSessionInputs`) — 1・2 のどちらも無いとき。
4. **前回 chat 起動の手入力** (`PrevInputs`、chatlog 由来) — 上のどれも無い初回起動。

いずれも無ければ従来どおり info 行のみで子は起動しない。

出力イメージ (case 01 を流したあと解答を直して `:replay`):

```
(case 01 を実行 — input 2行 / expected 1行)
→ 5 3
→ 1 2 3
  5ms ← 5            ✗ expected 6
─── session #2 ───   (解答ファイル更新でリロード)
:replay
(case 01 を再生 — input 2行 / expected 1行)
→ 5 3
→ 1 2 3
  4ms ← 6            ✓
```

## 動作仕様

| 状況 | 動作 |
|---|---|
| `:test 1` → `:replay` | case 01 の `.in` を再入力し `.out` で再検証する (直近操作 = テスト) |
| `:test 1` → 手入力 `5` → `:replay` | 手入力 `5` を再生する (直近操作 = 手入力。テストは流さない) |
| 手入力 `3` → `:test 1` → `:replay` | case 01 を再生する (直近操作 = テスト。先の手入力 `3` は流さない) |
| `:test 1` → `:test 2` → `:replay` | case 02 を再生する (直近の `:test` で上書き) |
| `:test 1` → `:replay` → `:replay` | 2 回とも case 01 を再生できる (再生は対象を消費しない) |
| `.out` が空の `:test` ケースを `:replay` | `.in` を再入力するが検証は付けない (`:test` 実行時と同じ) |
| `:test` を一度も流していない | 従来の `:replay` (手入力 → 直前セッション → 前回起動) と完全一致 |
| 再生対象が何も無い | info 行 `(再生できる入力がありません …)` のみ。子は起動しない |

近似の根拠: `:test` は必ず子リスタート (`restart` → `beginNewSession`) を伴い、流した手入力を `prevSessionInputs` へ退避し `sessionInputs` を空にする。`:test` の順送は `record=false` なので `sessionInputs` には積まれない。したがって「現セッションに手入力が残っている (= `sessionInputs` 非空)」ことが、そのまま「`:test` より後に手入力した」ことと一致する。これを使えば、明示的なタイムライン追跡なしに「直近の操作が手入力か `:test` か」を `sessionInputs` の空・非空で判定できる。

非破壊性:

- `:replay` での `:test` ケース再生も `record=false` を維持し、`sessionInputs` / chatlog ([039]) を汚さない (次回の `:replay` 対象や永続化を膨らませない)。
- 直近 `:test` ケースのスナップショット (`input`/`expected`/`id`) は実行時にコピーして持ち、`sessionInputs` の退避・リセットに影響されない。
- 解答ファイル・キャッシュ・`tests-extra/` には触れない (再生は stdin 順送のみ)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/chat_casebuilder.go` | `testReplay` 型 (直近 `:test` ケースのスナップショット) を追加。`execTest` で流したケースを `m.lastTest` に記録。`execReplay` を優先順位 (手入力 / 直近 `:test`) で分岐。`:test`/`:replay` 共通の順送ヘルパ `flowInput` を抽出。`showCheat` の `:replay` 説明文を更新 |
| `internal/ui/chat.go` | `chatModel` に `lastTest *testReplay` フィールドを追加 (今回の起動内でのみ保持。コメントで意味を明記) |
| `internal/ui/chatreplay_test.go` | 直近 `:test` ケースの再生・手入力優先・再検証・反復再生のユニットテストを追加 |
| `docs/tools/atcoder-test-usage.md` | `:replay` 行・解説節を「直近の操作 (手入力 / `:test` ケース) を再生」に更新。`:test` 節の「`:test` のあと `:replay` は手入力だけ」という記述を改める |
| `docs/tools/atcoder-start-usage.md` | `:replay` の解説を同様に更新 |
| `docs/tools/atcoder-test-architecture.md` | `chat_casebuilder.go` の説明に `:replay` の `:test` ケース再生を追記 |

新規パッケージは無し。`testReplay` は `internal/ui` 内の小さな値型。

```go
// testReplay は直近に :test で流したサンプルケースのスナップショット (要件 048)。
type testReplay struct {
    id       string   // 表示用ケース ID ("01" / "x01")
    input    []string // 流した .in の行
    expected []string // .out の行 (空なら検証なし)
}

// flowInput は snap の入力をクリーンな子で順送する共通処理 (:test / :replay 共有)。
// expected が非空ならライブ検証を (再) 有効化する。順送は record=false。
func (m *chatModel) flowInput(snap, expected []string) (tea.Model, tea.Cmd)
```

## エラーハンドリング

chat 内の 1 行 info で完結し、exit code には影響しない (TUI セッション中)。

| 状況 | 動作 |
|---|---|
| 再生対象が無い | info 行 `(再生できる入力がありません — まだ何も送っていない初回起動です)`。子は起動しない |
| 子の spawn 失敗 | `restart()` が `spawn failed: …` を出して quit (既存挙動) |
| stdin 書き込み失敗 | `(write failed: …)` を出して以降を送らない (既存 `submitLines` の挙動) |

## 非機能要件

- **既存非破壊**: `:test` を一度も使わない限り `:replay` の挙動は要件 039 と完全一致。`:test` 自体の順送・検証も不変。
- **層境界**: `internal/ui` は `testexec`/`cmd` を import しない。サンプル読込は既存 `chat_sample.go` ([045]) のまま。
- **冪等**: `:replay` での `:test` ケース再生は対象を消費せず、同じケースを何度でも再生できる。
- **前方互換**: 直近 `:test` ケースの保持は起動内のみ。将来「操作履歴の選択再生」へ広げるとしても、引数なし `:replay` の既定挙動 (直近) はそのまま残せる。

## テスト戦略

interactive な chat TUI の振る舞いなので、fixture (`fixtures/run.sh` = バッチ `atcoder test` の exit code 固定) ではなく、要件 039 / 045 と同じく `internal/ui` の Go ユニットテストで固定する (`chatreplay_test.go` / `chattest_test.go`)。fake spawner で stdin を捕捉し、`:test` → `:replay` の順送内容と検証状態 (`m.verify` / `m.lastExpected`) を assert する。`fixtures/run.sh` は CLI 表面を変えないので回帰確認として 1 回流す (新ケースは足さない)。

## 用語

- `contest_id` = `abc457` / `task_id` = `abc457_d` / `letter` = `d`。
- ケース ID 表記: 公式 `tests/` = `01`、追加 `tests-extra/` = `x01` (要件 045 / `chat_sample.go` の `normalizeSampleRef`)。

## 関連ドキュメント

- 要件 [045](045-chat-run-sample-case.md): `:test [case]` (この要件が再生する対象を作るコマンド)。
- 要件 [039](039-chat-replay-previous-session.md): `:replay` の手入力再生と chatlog 永続化 (この要件が拡張する基盤)。
- 要件 [024](024-interactive-case-builder.md): command モード・ライブ検証の基盤。
- ロードマップ: [`docs/tools/todo.md`](../todo.md) の AM。
