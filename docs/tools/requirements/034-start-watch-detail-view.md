# start watch ペインの詳細表示 (失敗ケースの diff) 要件定義

## 概要

`atcoder start` の分割画面で、**専用キー `Ctrl+G`** を押すと、上ペイン (watch) のサンプル判定結果の**詳細 = 失敗ケース (WA/TLE/RE) の diff** をオーバーレイ表示する。現状の上ペインは per-case verdict (`01 AC  02 WA  03 TLE`) を 3 行で出すだけで「**どこがどう違って落ちたか**」が分からない。`Ctrl+G` で失敗ケースの期待出力と実際出力の差分 (RE なら stderr) を `test` の FAIL 表示と同じ `renderDiff` で見られるようにする。もう一度 `Ctrl+G` か `Esc` で閉じて分割画面に戻る。判定の入力/期待/実際/stderr は既に `SummaryReporter` が `CaseResult` として捕捉しているので、UI 層へ運んで描画するだけ。

## 背景・目的

- 分割画面 ([023](023-start-split-screen.md)) の上ペインは per-case verdict (W) まで出るが、WA の中身 (期待と実際の差) は見えない。落ちたら一度 `start` を抜けて `atcoder test` を別途叩くか、`:case` でケースを作るしかない。
- `test` の判定は `CaseResult` に **`Input` / `Expected` / `Actual` / `Stderr`** を全て持っており、`SummaryReporter.Result()` が `[]CaseResult` をそのまま返す。**詳細表示に要るデータは既に揃っている** — UI に運んで `renderDiff` で出すだけで「編集 → 保存 → 失敗箇所を即確認」が 1 画面で回る。
- 編集ループ中に「どのサンプルで落ちているか」を確認するのが主目的なので、AC のケースは省き**失敗ケースだけ**を出す。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| トリガ | 専用キー `Ctrl+G` (split が chat より先に横取り)。詳細表示中は `Ctrl+G`/`Esc` で閉じる | キー設定の config 化 |
| 中身 | **失敗ケース (WA/TLE/RE) のみ**。WA/TLE は `renderDiff` (期待 vs 実際)、RE は stderr。AC は省略 | AC も含める切替・1 ケース選択・side-by-side |
| 出し方 | 全画面オーバーレイ (split を一時的に隠す)。`PageUp`/`PageDown`/`↑`/`↓` でスクロール | 上ペイン展開方式 |
| ライブ更新 | 詳細表示中に保存→再判定 (新 `splitSampleMsg`) が来たら詳細内容を作り直す | — |
| 対象 | `start` 分割画面のみ (TTY)。`test --interactive` 単体は対象外 (watch ペインが無い) | — |

### 失敗ケースだけにする理由

編集ループの主目的は「落ちた原因を見る」こと。AC のケースの I/O は通常不要で、出すと縦に長くなり目的のケースが埋もれる。AC を省くことで詳細を**失敗箇所に集中**させる。全ケース表示は将来の切替オプションに回す。

## CLI 仕様

新フラグ・新サブコマンドは**増やさない**。`start` 分割画面のキーが 1 つ増える。

### キー (追加分・`start` 分割画面)

| キー | 動作 |
|---|---|
| `Ctrl+G` | 詳細オーバーレイを開く (失敗ケースの diff)。表示中にもう一度押すと閉じる |
| `Esc` (詳細表示中) | 詳細を閉じて分割画面へ戻る |
| `PageUp`/`PageDown`/`↑`/`↓` (詳細表示中) | 詳細内容をスクロール (失敗ケースが多く画面に収まらないとき) |
| (詳細表示中のその他キー) | 無視 (chat には渡さない) |
| (分割画面のその他キー) | 従来どおり下ペイン chat に委譲 (不変) |

### 処理ステップ

1. 分割画面で `Ctrl+G` 押下 → `m.detail = true`。現在の `summary.Cases` の**失敗ケース**から詳細文字列を組み (`buildDetail`)、詳細用 `viewport` に流す。
2. `View()` は `m.detail` のとき、分割画面の代わりに**詳細オーバーレイ** (ヘッダ + 詳細 viewport + フッタヒント) を描画する。
3. 詳細表示中のキー: `Ctrl+G`/`Esc` → 閉じる (`m.detail = false`)。`PageUp`/`PageDown`/`↑`/`↓` → 詳細 viewport をスクロール。他は無視。
4. 詳細表示中に新しい `splitSampleMsg` (保存→再判定) が来たら、`summary` 更新後に詳細内容を作り直す (スクロール位置は最下部 or 維持は実装裁量)。

### 出力イメージ (詳細オーバーレイ)

```
── 詳細 (失敗ケース)  abc457_d ───────────────────────
[02] WA   31 ms
  expected ┊ actual
  1 2 3 4 5 ┊ 1 2 3 4 6
  hello     ┊ hallo

[03] RE   12 ms
  stderr: IndexError: list index out of range
──  Ctrl+G/Esc で戻る  ·  PageUp/PageDown でスクロール ──
```

失敗ケースが無いとき:

```
── 詳細 (失敗ケース)  abc457_d ───────────────────────
  (失敗ケースはありません)
──  Ctrl+G/Esc で戻る ──
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| 失敗ケースの判定 | `CaseVerdict.OK == false` (= AC 以外: WA/TLE/RE)。AC は出さない |
| WA / TLE | `renderDiff(expected, actual, full=true)` で期待 vs 実際を強調表示 (`test` の FAIL と同じ) |
| RE | `stderr` を表示 (diff は無い) |
| 判定エラー (テスト無し等, `summary.Err`) | 詳細にも「(判定できません: …)」を出す |
| ライブ更新 | 詳細表示中に保存→再判定が走ると、新しい結果で詳細を作り直す |
| chat ペイン | 詳細表示中も裏で生きている (子は kill しない)。閉じると元の chat に戻る |
| 判定ロジック・exit code | 不変。詳細は**表示のみ**で子・解答・キャッシュに触れない |
| 非 TTY / `test --interactive` 単体 | 対象外 (分割画面が無い)。挙動不変 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/startsplit.go` | `CaseVerdict` に失敗ケース用の `Input`/`Expected`/`Actual`/`Stderr`/`Elapsed` を追加。`startSplitModel` に `detail bool` + 詳細用 `viewport.Model`。`Update` に `Ctrl+G` トグル + 詳細表示中のキールーティング (`Esc`/スクロール) を追加。`View` に詳細オーバーレイ分岐。`buildDetail` (失敗ケース → `renderDiff`/stderr で文字列化) を追加。`splitSampleMsg` 受信時、詳細表示中なら作り直す |
| `cmd/atcoder/start.go` | `runSamples` の `CaseResult → CaseVerdict` マッピングで、`Status != Pass` のとき `Input`/`Expected`/`Actual`/`Stderr`/`Elapsed` を載せる (AC は載せない) |
| `internal/ui/startsplit_test.go` | `Ctrl+G` で `detail` が開く・失敗ケースの diff が内容に出る・`Esc`/`Ctrl+G` で閉じる・失敗ゼロ時の文言・AC ケースが出ないこと、を固定 |
| `docs/tools/atcoder-start-usage.md` | 分割画面キー表に `Ctrl+G` (詳細表示) を追記 |
| `docs/tools/todo.md` | 本項目を追加し ✅ DONE。要件 023 / per-case verdict (W) と相互リンク |

### `CaseVerdict` の拡張 (`internal/ui`)

```go
type CaseVerdict struct {
    Name  string // ケース名 (例 "01")
    Label string // "AC" / "WA" / "TLE" / "RE"
    OK    bool   // AC (Pass) なら true
    // 詳細表示用 (失敗ケースのときだけ start.go がセットする。AC は空)。
    Input    string
    Expected string
    Actual   string
    Stderr   string        // RE のみ
    Elapsed  time.Duration // 実行時間
}
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| 失敗ケースが無い | 詳細に「(失敗ケースはありません)」と出す (エラーにしない) |
| `summary.Err` (判定自体が失敗) | 詳細に「(判定できません: <err>)」を出す |
| 判定がまだ 1 度も走っていない (`!haveSummary`) | 詳細に「(まだ判定結果がありません)」を出す |
| (注) chat はキー操作の TUI。exit code ではなく画面表示で表現する。詳細表示は終了コードに影響しない |

## 非機能要件

- **既存非破壊**: 下ペイン chat・per-case verdict (上ペイン)・判定ロジック・exit code・非 TTY・`test --interactive` 単体は不変。`Ctrl+G` は chat 未使用キーで、split が chat より先に横取りするだけ。
- **データ流用**: 詳細に要る I/O は `CaseResult` が既に保持し `SummaryReporter` が運ぶ。新たな捕捉経路は作らない (失敗ケースの I/O を `CaseVerdict` に載せるだけ)。
- **表示のみ**: 詳細は子・解答・キャッシュに触れない。`renderDiff` は既存の純粋関数を再利用。
- **前方互換**: `CaseVerdict` の追加フィールドは AC で空。将来 AC 表示・1 ケース選択・side-by-side を足せる。

## 将来の拡張ポイント

- AC ケースも見る切替・1 ケースを `↑`/`↓` で選んで展開・side-by-side diff (`-s` 相当)。
- `test --interactive` 単体でも直近のサンプル判定詳細を見られるようにする。
- 詳細表示中であることのインジケータ・件数 (`2 fails`) の表示。

## 用語

- **詳細表示**: 失敗ケースの期待 vs 実際の diff (RE は stderr) をオーバーレイで見る機能。
- **per-case verdict**: 上ペインの `01 AC  02 WA …` 表示 (todo「W」)。本機能はその「中身」を出す。
- **CaseResult**: `internal/testexec` の 1 ケース判定結果 (`Input`/`Expected`/`Actual`/`Stderr` 等)。

## 関連ドキュメント

- `docs/tools/requirements/023-start-split-screen.md` (分割画面。本機能はその上ペインに詳細を足す)
- `docs/tools/requirements/001-exercise-test.md` (`test` の判定・diff 表示。`renderDiff` の元)
- `docs/tools/atcoder-start-usage.md` (分割画面キーの説明の更新先)
