# start watch ペインの詳細表示 (失敗ケースの diff) 要件定義

> **表示方式の刷新 ([072](072-start-aoj-layout.md)):** 本要件の `Ctrl+G` **トグルで上ペインを拡張して詳細を出す方式は [072](072-start-aoj-layout.md) が supersede** する (詳細を**右カラムに常時表示**し、左カラムで選択したケースを追従)。詳細に要るデータ (`CaseVerdict` の `Input`/`Expected`/`Actual`/`Stderr`/`Elapsed`) と `renderDiff` の再利用は不変で、`Ctrl+G` は「詳細開閉」から「判定ペインのフォーカス開閉」に役割が移り、`↑`/`↓` が全失敗ケース連結のスクロールから**単一ケースの選択**に変わる。072 では AC ケースにも I/O を載せる (本要件では AC を空にしていた点を緩める)。

## 概要

`atcoder start` の分割画面で、**専用キー `Ctrl+G`** を押すと、上ペイン (watch) のサンプル判定結果の**詳細 = 失敗ケース (WA/TLE/RE) の diff** を表示する。現状の上ペインは per-case verdict (`01 AC  02 WA  03 TLE`) を 3 行で出すだけで「**どこがどう違って落ちたか**」が分からない。`Ctrl+G` で失敗ケースの期待出力と実際出力の差分 (RE なら stderr) を `test` の FAIL 表示と同じ `renderDiff` で見られるようにする。もう一度 `Ctrl+G` か `Esc` で閉じて通常の分割画面に戻る。判定の入力/期待/実際/stderr は既に `SummaryReporter` が `CaseResult` として捕捉しているので、UI 層へ運んで描画するだけ。

**表示方式は「watch ペイン拡張」**: 詳細表示中は上ペイン (watch) が下方向に伸びて詳細 diff を専有し、**下ペイン chat は縮んで残る** (全画面で隠さない)。編集中の chat と詳細を同時に見ながら直せる。`Ctrl+G`/`Esc` で元の 3 行 watch ペインに戻る。

> **設計判断 (2026-06)**: 当初は詳細を**全画面オーバーレイ**で出していた (chat を一時的に隠す)。「編集しながら失敗箇所を見たい」用途では chat が消えるのが不便なため、**上下分割を保ったまま上ペインを拡張**する方式へ変更した。モーダル (中央ボックス重畳) も候補だったが、`lipgloss.Place` 合成の複雑さに対し上下分割の延長で済むペイン拡張を採った。

## 背景・目的

- 分割画面 ([023](023-start-split-screen.md)) の上ペインは per-case verdict (W) まで出るが、WA の中身 (期待と実際の差) は見えない。落ちたら一度 `start` を抜けて `atcoder test` を別途叩くか、`:case` でケースを作るしかない。
- `test` の判定は `CaseResult` に **`Input` / `Expected` / `Actual` / `Stderr`** を全て持っており、`SummaryReporter.Result()` が `[]CaseResult` をそのまま返す。**詳細表示に要るデータは既に揃っている** — UI に運んで `renderDiff` で出すだけで「編集 → 保存 → 失敗箇所を即確認」が 1 画面で回る。
- 編集ループ中に「どのサンプルで落ちているか」を確認するのが主目的なので、AC のケースは省き**失敗ケースだけ**を出す。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| トリガ | 専用キー `Ctrl+G` (split が chat より先に横取り)。詳細表示中は `Ctrl+G`/`Esc` で閉じる | キー設定の config 化 |
| 中身 | **失敗ケース (WA/TLE/RE) のみ**。WA/TLE は `renderDiff` (期待 vs 実際)、RE は stderr。AC は省略 | AC も含める切替・1 ケース選択・side-by-side |
| 出し方 | **watch ペイン拡張** (上ペインが下方向に伸び、chat は縮んで残る)。`PageUp`/`PageDown`/`↑`/`↓` でスクロール | モーダル (中央ボックス重畳)・全画面切替 |
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

1. 分割画面で `Ctrl+G` 押下 → `m.detail = true`。現在の `summary.Cases` の**失敗ケース**から詳細文字列を組み (`buildDetailContent`)、詳細用 `viewport` (高さ = `detailBodyHeight()`) に流す。`detail` 切替で chat の割当高さが変わるので、chat に新しい高さの `WindowSizeMsg` を送り直す (`resizeChat`)。
2. `View()` は `m.detail` のとき、**watch ペイン (3 行) + 詳細 viewport + 区切り線 + 縮んだ chat ペイン + ヘルプ行**を縦結合する。watch のタイトル/要約 (per-case verdict) はそのまま残るので、どのケースが落ちたかの文脈を保ったまま中身を見られる。
3. 詳細表示中のキー: `Ctrl+G`/`Esc` → 閉じる (`m.detail = false` → `resizeChat` で chat を元の高さに戻す)。`PageUp`/`PageDown`/`↑`/`↓` → 詳細 viewport をスクロール。他は無視 (chat に渡さない)。
4. 詳細表示中に新しい `splitSampleMsg` (保存→再判定) が来たら、`summary` 更新後に詳細内容を作り直す (スクロール位置は最下部 or 維持は実装裁量)。

### 高さ配分

詳細表示中の縦の割り当て (端末高 `H`):

| 領域 | 行数 |
|---|---|
| watch ペイン (タイトル + 要約 + 区切り線) | `splitTopLines` = 3 |
| 詳細 viewport | `detailBodyHeight()` (body の約 60%、chat に最低 `minDetailChatLines` を残す) |
| 区切り線 (詳細と chat の間) | `splitDetailRuleLines` = 1 |
| chat ペイン | 残り (`chatHeight()` が `detail` 時にこの控除を行う) |
| ヘルプ行 | `splitHelpLines` = 1 |

`body = H - splitTopLines - splitHelpLines - splitDetailRuleLines`。`chatHeight()` は `detail` のとき `detailBodyHeight() + splitDetailRuleLines` を追加で引く。

### 出力イメージ (ペイン拡張)

```
watch  abc457/d.py            [debug]
✗ 2/4  01 AC 02 WA 03 TLE 04 AC
─────────────────────────────────────
[02] WA  31ms
  1 2 3 4 5    1 2 3 4 6
  hello        hallo
[03] RE  12ms
  IndexError: list index out of range
─────────────────────────────────────
→ (chat はそのまま下に残る)
← …
Ctrl+G/Esc 閉じる · ↑/↓ PageUp/PageDown スクロール · 保存で再判定
```

失敗ケースが無いとき (詳細領域に):

```
  (失敗ケースはありません)
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| 失敗ケースの判定 | `CaseVerdict.OK == false` (= AC 以外: WA/TLE/RE)。AC は出さない |
| WA / TLE | `renderDiff(expected, actual, full=true)` で期待 vs 実際を強調表示 (`test` の FAIL と同じ) |
| RE | `stderr` を表示 (diff は無い) |
| 判定エラー (テスト無し等, `summary.Err`) | 詳細にも「(判定できません: …)」を出す |
| ライブ更新 | 詳細表示中に保存→再判定が走ると、新しい結果で詳細を作り直す |
| chat ペイン | 詳細表示中も**下に縮んで見えている** (子は kill しない)。閉じると元の高さに戻る |
| 判定ロジック・exit code | 不変。詳細は**表示のみ**で子・解答・キャッシュに触れない |
| 非 TTY / `test --interactive` 単体 | 対象外 (分割画面が無い)。挙動不変 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/startsplit.go` | `CaseVerdict` に失敗ケース用の `Input`/`Expected`/`Actual`/`Stderr`/`Elapsed` を追加。`startSplitModel` に `detail bool` + 詳細用 `viewport.Model`。`chatHeight()` を `detail` 時に詳細領域分を控除するよう拡張し、`detailBodyHeight()`/`resizeChat()` を追加。`Update` に `Ctrl+G` トグル (+ 開閉時の `resizeChat`) と詳細表示中のキールーティング (`Esc`/スクロール) を追加。`View` の `detail` 分岐を**ペイン拡張**レイアウト (watch + 詳細 viewport + 区切り線 + chat + ヘルプ) に。`buildDetailContent` (失敗ケース → `renderDiff`/stderr で文字列化) を追加。`splitSampleMsg` 受信時、詳細表示中なら作り直す |
| `cmd/atcoder/start.go` | `runSamples` の `CaseResult → CaseVerdict` マッピングで、`Status != Pass` のとき `Input`/`Expected`/`Actual`/`Stderr`/`Elapsed` を載せる (AC は載せない) |
| `internal/ui/startsplit_test.go` | `Ctrl+G` で `detail` が開く・失敗ケースの diff が内容に出る・`Esc`/`Ctrl+G` で閉じる・失敗ゼロ時の文言・AC ケースが出ないこと、を固定 |
| `docs/tools/usage/start.md` | 分割画面キー表に `Ctrl+G` (詳細表示) を追記 |
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

- **詳細表示**: 失敗ケースの期待 vs 実際の diff (RE は stderr) を、上ペイン (watch) を拡張して見る機能。
- **per-case verdict**: 上ペインの `01 AC  02 WA …` 表示 (todo「W」)。本機能はその「中身」を出す。
- **CaseResult**: `internal/testexec` の 1 ケース判定結果 (`Input`/`Expected`/`Actual`/`Stderr` 等)。

## 関連ドキュメント

- `docs/tools/requirements/023-start-split-screen.md` (分割画面。本機能はその上ペインに詳細を足す)
- `docs/tools/requirements/001-exercise-test.md` (`test` の判定・diff 表示。`renderDiff` の元)
- `docs/tools/usage/start.md` (分割画面キーの説明の更新先)
