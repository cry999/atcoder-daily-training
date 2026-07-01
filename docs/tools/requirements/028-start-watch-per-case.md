# `atcoder start` watch ペインの per-case verdict 表示 要件定義

## 概要

`atcoder start` の分割画面 watch ペインを、現状の集計要約 (`✗ FAIL 3/4  fail: 02`) から、**各サンプルケースが AC か WA か (per-case の verdict)** が分かるレベルに拡張する。`01 AC  02 WA  03 AC  04 AC` のようにケースごとの合否を一目で見せ、「どのケースで落ちているか」を即把握できるようにする。

## 背景・目的

- 現状の watch ペインは「PASS/FAIL 件数 + 失敗ケース番号」だけで、各ケースが AC なのか WA/TLE/RE なのかは分からない (失敗ケース名は出るが verdict の種類が出ない)。
- 編集 → 保存しながら「2 番が WA、3 番は TLE」と即分かれば、どのケースを潰すかの判断が速い。
- 既存の `SummaryReporter` は per-case の結果 (`End(results)`) を受け取れるのに、失敗ケース名しか拾っていない。ここを per-case verdict まで拾って watch ペインに出す。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | `atcoder start` の分割画面 watch ペイン (上ペイン) | `test --watch` 等の他表示 |
| 表示 | 各ケースの **id + verdict** (`01 AC` / `02 WA` / `03 TLE` / `04 RE`) を横並び | per-case の経過時間・diff トグル |
| verdict 語彙 | **AC / WA / TLE / RE** (AtCoder 流のコンパクト表記。AC=Pass・WA=Fail・TLE・RE) | — |
| 色 | AC=緑、WA/TLE/RE=赤 | TLE は黄など細分化 |
| 幅超過 | ペイン幅 (端末幅) に収まらなければ末尾を `…` で切り詰め (ペインの行数は increase させない) | per-case を折り返して複数行表示 |
| 副作用 | 無し (表示のみ。判定は従来どおり捕捉 Reporter 経由で stdout に出さない) | — |

### 境界

- 判定ロジック・exit code・サンプル取得は不変。**watch ペインの表示内容だけ**を richer にする。
- `start` の分割画面 (要件 023) の上ペイン専用。chat ペイン・非 TTY・`test` 各モードには影響しない。

## CLI 仕様

- **新フラグは無し**。`atcoder start` の watch ペインの表示として常時有効。

### 画面イメージ (watch ペイン)

全 AC:

```
watch  exercise/2026/06/11/abc999_a.py
  ✓ 4/4   01 AC  02 AC  03 AC  04 AC   · 12:34:56
──────────────────────────────────────────────────
```

一部 WA / TLE:

```
watch  exercise/2026/06/11/abc999_a.py
  ✗ 2/4   01 AC  02 WA  03 TLE  04 AC   · 12:35:10
──────────────────────────────────────────────────
```

- 先頭に全体グリフ + `passed/total` (✓=全 AC・緑 / ✗=未達・赤)、続けて per-case verdict、末尾に判定時刻。
- ケースが多くペイン幅を超える場合は末尾を `…` で切り詰め (上ペインは 3 行のまま、chat ペインの高さ計算を崩さない)。
- 判定不可 (テスト無し等) は従来どおり `判定不可: <理由>`。判定前は `judging…`。

### 処理ステップ

1. 保存検知でサンプル再判定 (`testexec.Run` + `SummaryReporter`)。
2. `SummaryReporter.End(results)` で **ケース名順の全 CaseResult** を捕捉する。
3. `runSamples` (cmd/start.go) が CaseResult を `ui.CaseVerdict{Name, Label, OK}` に写す (Label は `AC`/`WA`/`TLE`/`RE`、OK は Status==Pass)。
4. watch ペインが per-case verdict を横並びで描画し、幅を超えたら切り詰める。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| 全ケース AC | `✓ N/N` (緑) + `01 AC …` (各緑) |
| 一部 WA/TLE/RE | `✗ p/N` (赤) + 落ちたケースだけ赤 verdict |
| ケースが幅を超える | 末尾を `…` で切り詰め (ペイン 3 行を維持) |
| テスト無し / 判定失敗 | `判定不可: <理由>` (従来どおり) |
| 判定前 | `judging…` |

- **既存非破壊**: 判定・exit code・chat ペイン・非 TTY は不変。`SummaryReporter.Result` の戻りを richer にするが、唯一の利用者は start の `runSamples`。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/testexec/summaryreporter.go` | `End(results)` で per-case の `[]CaseResult` (名前順) を捕捉。`Result()` を `(passed, total int, cases []CaseResult)` に拡張 (失敗名は呼び側で導出) |
| `internal/ui/startsplit.go` | `SampleSummary` に `Cases []CaseVerdict` を追加 (`CaseVerdict{Name, Label string, OK bool}`)。`formatSampleSummary` を per-case verdict 表示に変更。幅超過は `ansi.Truncate` で `…` 切り詰め。純粋関数で組む |
| `cmd/atcoder/start.go` | `runSamples` で `Result()` の `cases` を `ui.CaseVerdict` に写す (Label は `caseLabel(status)` で `AC/WA/TLE/RE`)。`Failing` は per-case から導出 |
| `internal/testexec/summaryreporter_test.go` | `End`→`Result` で per-case を順序付きで返すテストに更新 |
| `internal/ui/startsplit_test.go` | `formatSampleSummary` が per-case verdict を出す/幅で切り詰めるテストを追加 |
| `docs/tools/usage/start.md` | watch ペインの説明・画面イメージを per-case verdict に更新 |
| `docs/tools/requirements/023-start-split-screen.md` | watch ペインを per-case verdict 表示に更新した旨を追記 (相互リンク) |
| `docs/tools/todo.md` | 本項目を記載し本要件へ相互リンク |

### 型の素描

```go
// internal/ui (startsplit.go)
type CaseVerdict struct {
    Name  string // ケース名 (例 "01")
    Label string // "AC" / "WA" / "TLE" / "RE"
    OK    bool   // AC (Pass) なら true。色分けに使う
}
// SampleSummary に追加: Cases []CaseVerdict  // ケース名順

// internal/testexec (summaryreporter.go)
// End(results []CaseResult) で results を保持し、
func (r *SummaryReporter) Result() (passed, total int, cases []CaseResult)
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| テストケースが無い / 判定失敗 | `SampleSummary.Err` をセット → ペインに `判定不可: …` |
| per-case が幅を超える | `…` 切り詰め (エラーにしない) |

- exit code への影響なし (表示のみ)。

## 非機能要件

- **既存非破壊**: 判定・exit code・chat ペイン・非 TTY・`test` 各モードは不変。
- **ペイン高さ不変**: 幅超過は切り詰めて上ペイン 3 行を維持し、`start` 分割画面の chat 高さ計算 (`splitTopLines`) を崩さない。
- **stdout を汚さない**: 判定は捕捉 Reporter のみ。直接 print しない。
- **決定的にテスト可能**: `formatSampleSummary` / `SummaryReporter.Result` を純粋関数的に保ち、per-case の並び・色・切り詰めをユニットテストで固定する。

## 将来の拡張ポイント

- per-case の経過時間 (`01 AC 12ms`) や、ペイン内 diff トグル。
- TLE を黄、RE を別色に細分化。
- ケースが多いときの折り返し複数行表示。

## 用語

- **per-case verdict**: 各サンプルケースの判定結果 (AC/WA/TLE/RE)。AC=Pass・WA=Fail。
- **watch ペイン**: `start` 分割画面の上ペイン。保存検知でサンプルを再判定して要約を出す。

## 関連ドキュメント

- `docs/tools/requirements/023-start-split-screen.md` (分割画面 watch ペインの定義元)
- `docs/tools/usage/start.md` (利用手引)
