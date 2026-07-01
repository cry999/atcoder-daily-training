# `atcoder` DEBUG 行の最小 JSON pretty print 要件定義

## 概要

`-d`/`--debug` で集約される `[DEBUG]` 行のうち、**ペイロードが単独で valid JSON のものだけ**を 2-space インデントで整形して人間向け表示する、オプトインの軽量整形機能。バッチ `test`/`run` では `--pp` フラグ、chat では `:pp` (`:set pp`/`:set nopp`) トグルで有効化する。言語パース (Python `repr`)・2 次元グリッド自動検出・`key = {...}` のラベル分離などの構造検出には**踏み込まない**。

debug パイプライン本体 (`splitDebug`・`CaseResult.Debug`・`reporter.printContent`・chat `:debug`・`--json` の `debug` フィールド) は要件 [030](030-chat-debug-cheat-commands.md) / [034](034-start-debug-watch-sync.md) / [042](042-test-json-output.md) で既に整備済み。本要件はその**表示層に整形を一段足すだけ**で、判定 (verdict)・`--json` 出力・exit code は一切変えない。

## 背景・目的

- 競プロのデバッグでは dp テーブル・グリッド・隣接リスト・状態 dict などを `print` で吐くことが多い。Python なら `print("[DEBUG]", json.dumps(state))` のように JSON 文字列で出すと、`[DEBUG] {"dp": [[0,1],[2,3]], "n": 5}` の **1 行ベタ**になり、ネストが読みにくい。
- 現状 `printContent("debug:", ...)` ([reporter.go:139,254](../../../internal/ui/reporter.go)) は改行を保持してインデント表示するだけで、行内の構造は整形しない。複数行で吐けば今でも綺麗に出るが、1 行 JSON dump を読みやすくする手段はツール側にない。
- 価値は限定的 (解答側で整形すれば 1 行で済む) と判断済みのため、**言語非依存・opaque text という既存設計を壊さない最小スコープ**に絞る: 「行ペイロードがそのまま valid JSON のときだけ再インデントする」。これは `encoding/json` だけで完結し、言語別パーサを持たない。

## スコープ

| 項目 | 当面のスコープ | 非スコープ / 将来の拡張余地 |
|---|---|---|
| 整形対象 | `[DEBUG]` 行のペイロードが `{`/`[` 始まりかつ valid JSON のもの | Python `repr` (`'`/`True`/`None`/タプル)・`key = {...}` のラベル付き行・行末 JSON の部分抽出 |
| 整形内容 | `encoding/json` の `json.Indent` で 2-space 再インデント (キー順・数値表記は保持) | グリッド整列・dict の縦展開・色付け・幅揃え |
| 有効化 | バッチ: `--pp` フラグ / chat: `:pp` トグル (オプトイン、既定 off) | 既定 on 化・`config` キーでの恒久化 |
| 適用面 | バッチ `test`/`run` の reporter・chat トランスクリプトの `debug:` 表示 | watch ペイン詳細表示 ([036](036-start-watch-detail-view.md)) への波及 |
| 判定 / 出力への影響 | **なし** (verdict・`--json` の `debug` フィールド・exit code は不変) | — |

### 整形しない設計境界 (なぜ最小か)

- **ペイロード全体が JSON のときだけ**整形する。`[DEBUG] dp = {...}` は `dp = {...}` 全体が valid JSON でないため**整形対象外**で、原文のまま表示する。ラベル分離や行末 JSON 抽出はやらない (曖昧・壊れやすく ROI が低い)。
- **`encoding/json` で受理できるものだけ**。Python の `repr` (シングルクォート・`True`/`False`/`None`・タプル `(1, 2)`) は JSON ではないので整形されない。「JSON で吐けば整形される」という単純規約に倒し、言語別パーサを導入しない。
- スカラ (`[DEBUG] 42`・`[DEBUG] "hi"`) は整形で得るものがないため対象外 (先頭が `{`/`[` のものに限定)。

## CLI 仕様

### バッチ `atcoder test` / `atcoder run`

| フラグ | 説明 |
|---|---|
| `--pp` | `debug:` セクションの表示時に、valid JSON ペイロードの `[DEBUG]` 行を 2-space インデントで整形する (既定 off)。短縮形なし。`-d`/`--debug` とは直交 (下記) |

- **`-d` との関係 (直交 + フットガン回避):** `--pp` は debug **表示の整形だけ**を司る純粋なレンダリング修飾で、debug パイプライン自体は有効化しない。`-d` 無しでは `debug:` セクションが空なので `--pp` は無表示になる。これを「効かない」と誤認させないため、**`--pp` を `-d` 無しで渡したら stderr に 1 行 note を出す**: `note: --pp has no effect without -d/--debug`。これは情報表示であり exit code は変えない。
  - *却下した代替案:* 「`--pp` が `-d` を含意する」案。一見親切だが、フラグが別フラグの状態を暗黙に立てる隠れ結合は予測しづらく、chat の `:pp`/`:debug` 直交モデルとも噛み合わない。note 方式なら結合なしでフットガンだけ消せる。
- `--json` ([042](042-test-json-output.md)) と併用された場合、`--pp` は**何もしない** (`--json` は人間向け表示を出さず、`debug` フィールドは常に生のまま)。

### chat command モード (`:pp`)

要件 [030](030-chat-debug-cheat-commands.md) の `:debug` と同じ流儀でトグルを 1 つ追加する。

| コマンド | 動作 |
|---|---|
| `:pp` | pp 表示を on/off トグル。状態を info 行で示す (`pp on` / `pp off`) |
| `:set pp` / `:set nopp` | 明示的に on / off |

- `:debug` と**直交**: `:pp` は以降に描画される `debug:` ブロックの整形有無だけを切り替える (既描画行は遡及しない、`:debug` と同じ非遡及ルール)。debug 自体が off なら整形対象が無いので、`:pp` on 時の info 行に補足を添える: `pp on (turn on :debug to see formatted output)`。
- command モード補完 ([031](031-command-mode-completion.md)) の常時コマンド集合に `pp` を、`:set` のサブトークンに `pp`/`nopp` を追加する。

### 出力イメージ

解答が `print("[DEBUG]", json.dumps({"dp": [[0,1],[2,3]], "n": 5}))` を出した場合:

```
# --pp なし (現状)
       debug:
         [DEBUG] {"dp": [[0, 1], [2, 3]], "n": 5}

# atcoder test abc457 --task d -d --pp
       debug:
         [DEBUG] {
           "dp": [
             [
               0,
               1
             ],
             [
               2,
               3
             ]
           ],
           "n": 5
         }
```

- 整形ブロックの 1 行目に `[DEBUG] ` を残し、`json.Indent` の出力をそのまま続ける (継続行に `[DEBUG]` は付けない)。すべて `debug:` セクション配下なので文脈は明確。整形対象外の行は原文のまま (整形済み行と素の行が混在しうる)。
- ブロック全体は `printContent` が一律にインデントするため、セクション内で揃う。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| ペイロードが `{`/`[` 始まり かつ valid JSON | `json.Indent` で 2-space 再インデント。先頭行に `[DEBUG] ` を付与 |
| ペイロードが valid JSON でない / `{`/`[` 始まりでない | 原文の行をそのまま表示 (整形しない) |
| `[DEBUG]` 行が複数 | 行ごとに独立判定。整形対象だけ整形、他は素のまま |
| `--pp` あり・`-d` なし (バッチ) | 整形対象なし。stderr に note を 1 行。exit code 不変 |
| `:pp` on・`:debug` off (chat) | 整形対象なし。info 行に補足。verdict 不変 |
| `--json` 併用 | `--pp` は無視。`debug` フィールドは生のまま |

### 整形アルゴリズム (キー順・数値の保存)

- 再整形は **`json.Indent` (再インデンタ) を使い、`Unmarshal`+`Marshal` はしない**。`json.Indent` は入力のバイト順をそのまま整形するため、**キー順が保たれ**、数値表記 (`1e9`・`0.50` 等) も改変されない。`map` 経由のキー順シャッフルや `float64` 化による桁落ちを避ける。
- ペイロード抽出は「`[DEBUG]` プレフィックスを除去 → 前後の空白を Trim」。残りが `{`/`[` 始まりで `json.Valid` が真なら整形対象。

### 既存挙動の非破壊

- `CaseResult.Debug` / `Result.Debug` (生の `[DEBUG]` 行集合) は**生のまま保持**する。整形は**表示時にだけ**適用する純粋なプレゼンテーション層の処理で、保存値・`--json` 出力・`DebugSeen` ([044](044-submit-precheck-confirm.md)) ゲートには触れない。
- `--pp`/`:pp` 既定 off。既存の `test`/`run`/chat の出力は `--pp` を付けない限り 1 byte も変わらない。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| 新規 `internal/ui/prettydebug.go` | `prettifyDebug(debug string) string` を実装。`[DEBUG]` 行を走査し、valid JSON ペイロードだけ `json.Indent` で整形して返す純関数 |
| `internal/ui/reporter.go` | `TestReporter` / `RunReporter` に `pp bool` を追加。`printCaseDetail` / `RunReporter.Result` の `debug:` 出力前に `pp` なら `prettifyDebug` を通す。コンストラクタ (`NewTestReporter`/`NewRunReporter`) に引数追加 |
| `cmd/atcoder/test.go` | `--pp` フラグ定義 (test 経路)。reporter 構築に渡す。`--pp` かつ `!debug` のとき stderr に note |
| `cmd/atcoder` の run 経路 | `run` のフラグにも `--pp` を追加し `RunReporter` へ伝播 (test/run 統合は [013](013-unify-test-run.md)) |
| `internal/ui/chat_casebuilder.go` | `parseCommand`/`execCommand` に `pp` を追加 (`:debug` の隣)。`header` に `PP bool` を持たせ、`:pp`/`:set pp|nopp` でトグル。info 行表示 |
| `internal/ui/chat.go` | `debug:` ブロック描画時に `header.PP` なら `prettifyDebug` を通す ([chat.go:644](../../../internal/ui/chat.go) 周辺の `[DEBUG]` 振り分け表示) |
| `internal/ui/command_complete.go` | 常時コマンドに `pp`、`:set` サブトークンに `pp`/`nopp` を追加 ([031](031-command-mode-completion.md)) |
| `fixtures/` | 既存 `fixture_debug.py` を JSON 行を吐くケースに拡張するか、`fixture_debug_json.py` を追加。`fixtures/run.sh` に `-d --pp` で整形・非整形が出し分くスモークを追加 ([test-tool] スキルの対象) |
| `docs/tools/usage/test.md` | `--pp` フラグ・`:pp` コマンド・JSON 出力推奨パターン (`json.dumps`) を追記 (実装は feature フェーズ) |

### `prettifyDebug` の API 素描 (実装は feature へ)

```go
package ui

// prettifyDebug は CaseResult.Debug の各 [DEBUG] 行のうち、ペイロードが
// 単独で valid JSON ({ or [ 始まり) のものを 2-space インデントに整形して返す。
// 整形対象外の行・空文字列はそのまま返す純関数。verdict や保存値は変えない。
//
//   入力:  "[DEBUG] {\"n\":5}\n[DEBUG] dp = {...}"
//   出力:  "[DEBUG] {\n  \"n\": 5\n}\n[DEBUG] dp = {...}"  // 2 行目は非 JSON なので素通し
func prettifyDebug(debug string) string
```

- `internal/ui` 内に閉じる。`testexec` は import しない (層境界維持)。`DebugPrefix` 定数は `testexec.DebugPrefix` を参照するか、UI 側でローカル定数を持つ (既存の `[DEBUG]` 振り分けと一貫させる)。

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `--pp` を `-d` 無しで指定 | stderr に `note: --pp has no effect without -d/--debug` を 1 行。exit 0 (整形対象なし) |
| ペイロードが valid JSON でない | エラーにせず原文の行をそのまま表示 (整形は best-effort) |
| `json.Indent` が失敗 (理論上 `json.Valid` 通過後は起きない) | 原文の行をそのまま表示 (フォールバック)。panic させない |
| `--json` と `--pp` の併用 | エラーにしない。`--pp` を無視 (人間向け表示自体が出ない) |

- 引数誤り (未知フラグ等) は標準 `flag` の既存規約どおり exit 2。pp 固有の新しいエラー条件・新 exit code は**設けない** (整形は常に best-effort で、失敗しても素通しするだけ)。

## 非機能要件

- **既存非破壊**: `--pp`/`:pp` 既定 off。未指定時の出力・verdict・`--json`・exit code は完全不変。
- **判定への非干渉**: pp は純粋な表示整形。`splitDebug` の比較除外や verdict には一切関与しない。
- **`--json` 不可侵**: 機械向け `debug` フィールドは常に生。pp は人間向け表示専用 ([042](042-test-json-output.md) の「人間向け表 / 機械向け JSON を出し分ける」流儀を維持)。
- **言語非依存維持**: `encoding/json` のみ。言語別パーサ・外部依存を増やさない。Python repr を整形したくなったら別要件として切り出す。
- **キー順・数値保存**: `json.Indent` を使い `Unmarshal`+`Marshal` を避ける (キー順シャッフル・数値桁落ちを防ぐ)。
- **層境界**: 整形は `internal/ui` に閉じ、`testexec` を汚さない。

## 将来の拡張ポイント

- **watch ペイン詳細 ([036](036-start-watch-detail-view.md)) への波及**: `:pp` を watch の `debug:` 表示にも反映 ([034](034-start-debug-watch-sync.md) が `:debug` をペインに波及させた流儀)。pp は verdict を変えないため同期は任意 (cosmetic のみ)。
- **既定 on / config 化**: 利用が定着したら `config` キー (`pretty_debug = true`) や `ATCODER_PP` で恒久化。
- **JSONL 風の複数値整形**: 1 行に複数 JSON を空白区切りで並べたケースの分割整形 (当面は単独 JSON のみ)。
- **言語別整形の別要件化**: Python `repr` を JSON5 的に正規化してから整形する経路 (`'`→`"`、`True/False/None`→`true/false/null`)。曖昧性が高いので独立要件で慎重に設計する。

## 用語

- **pretty print (pp)**: `[DEBUG]` 行のうち valid JSON ペイロードを 2-space インデントに整形する表示処理。判定・保存値・`--json` は変えない。
- **ペイロード**: `[DEBUG]` 行から `[DEBUG]` プレフィックスと前後空白を除いた本文。これが単独で valid JSON のときだけ整形する。
- **debug パイプライン**: `-d` で `[DEBUG]` 行を比較対象から外し `Debug` フィールドに集約する既存機構 ([030](030-chat-debug-cheat-commands.md)/[034](034-start-debug-watch-sync.md))。
- (`contest_id`/`contest_num`/`task_id`/`letter` は [002](002-exercise-abc-layout.md)/[003](003-exercise-abc-contest-meta.md) に準拠)

## 関連ドキュメント

- `docs/tools/requirements/030-chat-debug-cheat-commands.md` (chat `:debug` トグル。`:pp` はこの隣に追加)
- `docs/tools/requirements/034-start-debug-watch-sync.md` (`:debug` の watch ペイン波及。pp の将来波及の前例)
- `docs/tools/requirements/042-test-json-output.md` (`--json` の `debug` フィールド。pp が侵さない機械向け出力)
- `docs/tools/requirements/044-submit-precheck-confirm.md` (`DebugSeen` ゲート。pp は触れない)
- `docs/tools/requirements/031-command-mode-completion.md` (command 補完。`:pp`/`:set pp|nopp` を追加)
- `docs/tools/todo.md` (上位ロードマップ。本要件は §AL)
