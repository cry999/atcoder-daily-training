# `atcoder start` 画面の AOJ v2.0 風レイアウト刷新 (判定一覧 + ケース詳細の横 2 カラム) 要件定義

> **この要件は [023](023-start-split-screen.md) (上下分割) と [036](036-start-watch-detail-view.md) (`Ctrl+G` トグルの詳細表示) の**レイアウトを supersede する**。判定要約 (per-case verdict, [028](028-start-watch-per-case.md)) と失敗ケースの diff/stderr データ (`CaseVerdict` の I/O, 036) はそのまま流用し、**並べ方**だけを AOJ v2.0 の問題ページに倣った構成に作り替える。判定・実行・chat・fetch のロジックは一切増やさない。

## 概要

`atcoder start` が開く画面を、Aizu Online Judge (AOJ) v2.0 の問題ページに倣った構成に刷新する。現状の「上=判定要約 3 行 / 下=chat、`Ctrl+G` で上ペインを下に伸ばして詳細 diff を出す」縦積みを廃し、**上部を横 2 カラム**(左=**判定一覧**・右=**ケース詳細**)、**下部を chat / コマンド**とする 3 領域構成にする。詳細 (失敗ケースの diff/stderr) は `Ctrl+G` のトグルではなく**右カラムに常時表示**し、左カラムで選択したケースの中身を追従表示する。**問題文・制約は取得も表示もしない**(AOJ の問題文エリアは作らない)。この画面が `start` の唯一の画面で、旧レイアウトは残さない (全面置換)。

## 背景・目的

- 現状の start 画面は、判定要約が 3 行のコンパクト表示に押し込まれ、失敗ケースの中身を見るには `Ctrl+G` でトグルする必要がある ([036](036-start-watch-detail-view.md))。「今どのケースがどう落ちているか」を**編集ループ中に常に一覧+中身で見たい**が、トグル方式だと開閉の一手間があり、判定一覧と詳細を同時に俯瞰しづらい。
- AOJ v2.0 の問題ページは「判定結果 (ステータスビュー) と各ケースの結果 (テストケースビュー) を並べて見せる」構成で、競プロの編集ループと相性が良い。start の TUI をこの情報構成に寄せると、**判定一覧 (左) → 気になるケースを選ぶ → 中身 (右) を見る**が 1 画面で完結する。
- start は既に TTY 必須で bubbletea 前提 ([023](023-start-split-screen.md))。横分割 (lipgloss `JoinHorizontal`) の導入だけで実現でき、既存の判定捕捉 (`SummaryReporter` / `CaseVerdict`) を並べ替えるだけで済む。

### AOJ v2.0 問題ページ ⇄ 本要件のマッピング

AOJ の問題ページは 5 部構成 (①問題文エリア ②コーディングフォーム ③ステータスビュー ④テストケースビュー ⑤フッタ)。本要件は端末 TUI にこう写す:

| AOJ の部品 | 中身 | 本要件での対応 |
|---|---|---|
| ①問題文エリア | 制約・本文・入出力形式・入出力例 | **作らない** (問題文・制約は取得しない。下記「却下した案」参照) |
| ②コーディングフォーム | 言語選択・エディタ・Submit | 下部 chat / コマンド (編集は既存の外部エディタ `Ctrl+E` [038](038-start-edit-in-editor.md)、提出準備は `Ctrl+S` [026](026-chat-submit.md)) |
| ③ステータスビュー | 提出進捗・全体結果 | 左カラム **判定一覧** の要約行 (`✓ 2/4` / 判定時刻) |
| ④テストケースビュー | 各ケースの判定 + 展開で I/O | 左カラム per-case verdict 一覧 + 右カラム **ケース詳細** (選択ケースの I/O・diff・stderr) |
| ⑤フッタ | リンク集 | 最下部ヘルプ行 (キー操作) |

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 | `atcoder start` の TTY 経路のみ (start は元々 TTY 必須) | `test --interactive` 単体は対象外 (判定ペインが無い) |
| レイアウト | **上部を横 2 カラム** (左=判定一覧・右=ケース詳細) + **下部 chat** + 最下部ヘルプ行 | ペイン比率の調整キー・カラム数の増減 |
| 左カラム | 全体要約 (`✓ 2/4` + 判定時刻) + per-case verdict 一覧 (`01 AC` …) + **選択カーソル** | AC/失敗のフィルタ・ソート |
| 右カラム | 左で選択中のケースの**詳細**を常時表示 (WA/TLE=diff、RE=stderr、AC=入力/期待) | side-by-side (`-s` 連動)・複数ケース並置 |
| ケース選択 | `Ctrl+G` で判定ペインにフォーカス→ `↑`/`↓` で選択→ 右が追従。`Esc`/`Ctrl+G` で chat に戻る。既定選択=最初の失敗ケース (無ければ先頭) | マウス・数字キーで直接選択 |
| 下カラム | 既存 chat (auto-restart・ナビ・提出・record 等) を**無改修で**再利用 | — |
| 狭い端末 | 横幅が 2 カラムに満たなければ**縦積みにフォールバック** (判定一覧→ケース詳細→chat) | 折り返し閾値の config 化 |
| 問題文・制約 | **取得も表示もしない** (fetch 拡張なし) | 別要件で問題文ペインを足す余地は残す |
| 切替 | **全面置換** (旧 023/036 レイアウトは廃止・フラグで戻せない) | — |
| 副作用 | 解答・キャッシュ・git・判定ロジック・exit code を壊さない (表示のみの変更) | — |

### 境界 (他機能との分担)

- **判定の捕捉は不変**: サンプル判定は既存の `testexec.Run` + `SummaryReporter` ([023](023-start-split-screen.md))。per-case の Name/Status/I/O は `CaseVerdict` ([036](036-start-watch-detail-view.md)) がそのまま運ぶ。本要件は**運ばれた結果の並べ方 (View) と選択状態 (Update) だけ**を変える。
- **chat ペインは無改修**: 下カラムは `chatModel` をそのまま内包 ([023](023-start-split-screen.md))。ナビ ([027](027-start-problem-navigation.md)/[032](032-nav-direct-target.md))・提出 ([026](026-chat-submit.md)/[044](044-submit-precheck-confirm.md))・meta ([055](055-chat-meta-edit.md)/[057](057-chat-meta-fetch.md))・gen ([060](060-gen-random-input.md))・record ([064](064-chat-record.md))・scroll ([071](071-chat-scroll-mode.md)) 等の chat 機能は不変。
- **fetch は不変**: `internal/testexec/fetch.go` は問題文本文を取らない。本要件でも取らない (fetch は制限時間・サンプル・gen 用の制約/入力形式だけを扱うまま)。
- **`test --watch` / `test --interactive` 単体・他サブコマンドは不変**。変わるのは `atcoder start` の TTY 画面のみ。

## CLI 仕様

```
atcoder start <contest> --task <task> [--until-pass] [--refresh] [-d] [-s] [-j <n>] [--timeout <dur>] [--tolerance <eps>] [--layout <...>]
```

- **フラグは不変** (新フラグを足さない)。挙動だけ「AOJ 風 2 カラム画面」に変わる。旧レイアウトへ戻すフラグは設けない (全面置換)。
- `--until-pass`・`--refresh`・`-d` (debug)・`-s` (side-by-side)・`--timeout`・`--tolerance`・`--layout` の意味は現状どおり (配置規約フラグは [070](070-contest-exercise-mode.md) で `--mode` へ改名予定だが、本要件はそれと独立)。

### 画面イメージ (通常時: 横 2 カラム)

```
┌ 判定 ─ exercise/2026/07/10/abc457_d.py ─┬ ケース詳細 ─ 02 WA ──────────────┐
│ ✗ 2/4          judged 12:34:56          │ [02] WA  31ms                     │
│  01 AC                                  │   expected        actual          │
│  02 WA  ◀                               │   1 2 3 4 5       1 2 3 4 6        │
│  03 TLE                                 │   hello           hallo           │
│  04 AC                                  │                                   │
├─────────────────────────────────────────┴───────────────────────────────────┤
│ interactive (auto-restart)                                                    │
│ > 5                                                                           │
│ 10                                                                            │
│ > _                                                                           │
└───────────────────────────────────────────────────────────────────────────────┘
 Ctrl+G 判定を選択 · Enter 送信 · Ctrl+E 編集 · Ctrl+S 提出 · Ctrl+Z サスペンド · 保存で再判定
```

(枠は概念図。実装は lipgloss で軽く装飾。左カラムはケース名幅に合わせた固定幅、右カラムが残り幅。`◀` は選択中ケースのカーソル。)

### 画面イメージ (狭い端末: 縦積みフォールバック)

```
判定  abc457_d.py            ✗ 2/4
 01 AC   02 WA ◀   03 TLE   04 AC
─────────────────────────────────
ケース詳細  02 WA  31ms
 expected: 1 2 3 4 5
 actual:   1 2 3 4 6
─────────────────────────────────
interactive (auto-restart)
> _
 Ctrl+G 選択 · Enter 送信 · 保存で再判定
```

### 処理ステップ

1. `start` の解答ファイル用意・layout 解決・着手刻印・ナビ注入は現状どおり (`cmd/atcoder/start.go`)。`ui.RunStartSplit(...)` に渡す構成 (`StartTarget` / `SampleSummary` / `CaseVerdict`) も不変。
2. bubbletea モデル `startSplitModel` は:
   - 下カラムに chat サブモデルを保持・駆動 (既存)。
   - 起動時に 1 回サンプル判定を走らせ、`summary.Cases` を左カラムに一覧表示。既定の選択ケース = 最初の失敗ケース (無ければ先頭)。
   - `tea.Tick` で mtime をポーリングし、保存検知でサンプル再判定 → 一覧・選択ケースの詳細を更新。
3. `View()` は端末幅で分岐:
   - **2 カラムに足る幅**: `JoinHorizontal(左カラム, 縦区切り, 右カラム)` を上部に、`JoinVertical(上部, 横区切り, chat, ヘルプ行)` で全体を合成。
   - **足りない幅**: `JoinVertical(判定一覧, 区切り, ケース詳細, 区切り, chat, ヘルプ行)` の縦積み。
4. キー処理:
   - **chat フォーカス時 (既定)**: `Ctrl+G` で判定ペインにフォーカスを移す。それ以外は従来どおり chat に委譲。
   - **判定ペインフォーカス時**: `↑`/`↓` で選択ケースを移動 (右カラムが追従)。右カラムが 1 画面に収まらなければ `PageUp`/`PageDown` でスクロール。`Esc`/`Ctrl+G` で chat フォーカスに戻す。他キーは無視 (chat に渡さない)。
5. `Ctrl+C`/`Ctrl+D` で全体終了 (既存)。`--until-pass` で全通過なら exit 0 (既存)。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| start 起動 (TTY) | 上部 2 カラム (左=判定一覧・右=選択ケース詳細) + 下部 chat。起動時に 1 回判定 |
| 解答ファイル保存 | サンプル再判定 → 左カラム一覧を更新。選択中ケースがまだ存在すれば選択を維持、消えたら既定 (最初の失敗/先頭) に寄せる。右カラムを作り直す。chat も最新コードで reload (既存) |
| `Ctrl+G` (chat フォーカス中) | 判定ペインにフォーカス。`↑`/`↓` で選択、右が追従 |
| `↑`/`↓` (判定ペインフォーカス中) | 選択ケースを上下移動 (端で止まる)。右カラム詳細を差し替え |
| `Esc`/`Ctrl+G` (判定ペインフォーカス中) | chat フォーカスに戻る |
| 選択ケースが AC | 右カラムに入力・期待出力を表示 (diff は無い。`AC · 12ms` の見出し付き) |
| 選択ケースが WA/TLE | 右カラムに `renderDiff(expected, actual, full=true)` (RE は下記) |
| 選択ケースが RE | 右カラムに stderr を表示 |
| 失敗ケースが 0 (全 AC) | 既定選択は先頭 (AC)。右カラムはその AC ケースの I/O を表示 |
| 判定がまだ 1 度も走っていない | 左カラムに「(まだ判定結果がありません)」、右カラムは空 |
| 判定自体が失敗 (テスト無し等, `summary.Err`) | 左カラムに「(判定できません: …)」、右カラムにも同旨。chat は動く |
| 横幅が 2 カラムに満たない | 縦積みフォールバック (判定一覧→ケース詳細→chat) |
| 端末リサイズ | 幅で 2 カラム ⇔ 縦積みを切替。高さは上部を確保し chat に残りを割り当て直す (chat 最低行数を保証) |
| キー入力 (chat フォーカス中の通常キー) | 従来どおり chat に委譲 (Enter 送信・履歴・コマンドモード等すべて不変) |
| `Ctrl+C` / `Ctrl+D` / `--until-pass` 全通過 | 正常終了 (exit 0) |
| 非 TTY | start は元々 exit 2 (TTY 必須) |

- **既存非破壊**: 判定ロジック・`CaseVerdict` の中身・chat の全機能・exit code・非 TTY 挙動・`test --*` 単体は不変。変わるのは `startSplitModel` の `View`/`Update` の**並べ方と選択状態**のみ。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/startsplit.go` | View を **横 2 カラム (幅十分) / 縦積み (狭い)** の分岐に作り替え。`startSplitModel` の `detail bool` を廃し、`focus`(chat/verdict) と `selected int` (選択ケース index) を導入。`Update` を「`Ctrl+G` でフォーカス切替」「フォーカス中 `↑`/`↓` で選択移動」「`Esc`/`Ctrl+G` で chat 復帰」に変更。左カラム描画 (`renderVerdictColumn`: 要約行 + per-case 一覧 + カーソル)・右カラム描画 (`renderCaseDetailColumn`: 選択ケースを `renderDiff`/stderr/AC 表示) を追加。カラム幅計算 (`columnWidths`)・上部/chat の高さ配分 (`topPaneHeight`/`chatHeight`)・幅による 2 カラム可否 (`canSplitHorizontally`) を純粋関数で。旧 `buildDetailContent`(全失敗ケース連結) は「選択 1 ケール描画」に置換。`resizeChat` はフォーカス/レイアウト変化時に chat 高さを再送 |
| `cmd/atcoder/start.go` | `runSamples` の `CaseResult → CaseVerdict` マッピングで、**AC ケースにも `Input`/`Expected`/`Elapsed` を載せる** (右カラムが任意ケースを表示できるように。036 は AC を空にしていたのを緩める。`Actual`/`Stderr` は失敗時のみで従来どおり) |
| `internal/ui/startsplit_test.go` | 純粋関数のユニットテスト: `columnWidths`/`canSplitHorizontally`/`topPaneHeight`/`chatHeight` の高さ・幅計算、選択移動 (端でクランプ・保存後の選択維持/寄せ)、左カラム一覧文字列にカーソルが出る、右カラムが選択ケースの diff/stderr/AC を出す、狭い端末で縦積みになる、を固定 |
| `docs/tools/usage/start.md` | 画面構成を「AOJ v2.0 風 2 カラム」に書き換え。キー表を `Ctrl+G`(判定フォーカス) / `↑`/`↓`(選択) / `Esc`(chat 復帰) に更新。旧「上ペイン 3 行 + Ctrl+G トグル詳細」の記述を差し替え |
| `docs/tools/atcoder-test-architecture.md` | start TUI 内部設計の該当節を 2 カラム構成に更新 (縦積み→横分割、detail トグル→常時右カラム) |
| `docs/tools/todo.md` | 新セクションを追加し本要件へ相互リンク。023/036 の該当記述に「レイアウトは 072 で刷新」と追記 |

### `startSplitModel` の状態 (素描)

```go
package ui

// フォーカス先: 通常は chat、Ctrl+G で verdict (判定ペイン) に移る。
type startFocus int

const (
    focusChat    startFocus = iota // 既定。キーは chat に委譲
    focusVerdict                   // ↑/↓ で選択ケース移動、Esc/Ctrl+G で chat に戻る
)

// startSplitModel は AOJ 風 3 領域 (上=判定一覧|ケース詳細, 下=chat) を描く。
// 023 の detail bool は廃止し、focus + selected に置き換える。
type startSplitModel struct {
    // ... 既存フィールド (chat, watcher, summary, ...) ...
    focus    startFocus
    selected int             // summary.Cases のうち右カラムに出すケース index
    detailVP viewport.Model  // 右カラム (選択ケースが 1 画面に収まらないとき用)
    width    int
    height   int
}

// canSplitHorizontally は横 2 カラムに割れる幅かを判定する純粋関数。
// false なら縦積みフォールバック。
func canSplitHorizontally(width int) bool

// columnWidths は上部 2 カラムの (左幅, 右幅) を返す。左はケース名幅に合わせた
// 固定幅 (min/max でクランプ)、右は残り。
func columnWidths(width int, cases []CaseVerdict) (left, right int)

// defaultSelected は既定選択 index を返す (最初の失敗ケース。無ければ 0)。
func defaultSelected(cases []CaseVerdict) int
```

- **選択駆動の右カラム**: 036 の「失敗ケースを全部連結して viewport に流す」を「`selected` の 1 ケースだけ描く」に変える。右カラムは AC/WA/TLE/RE を問わず選択ケースを描き、WA/TLE は `renderDiff`、RE は stderr、AC は入力+期待を出す。
- **フォーカスモデル**: chat 入力が常にタイプを食うため、選択の `↑`/`↓` は「判定ペインにフォーカスを移してから」効かせる (`Ctrl+G` トグル)。036 の `Ctrl+G`(詳細開閉) の筋肉記憶を「判定フォーカス開閉」に引き継ぐ。
- **レイアウト**: `lipgloss.JoinHorizontal` で上部 2 カラム、`JoinVertical` で上部+chat+ヘルプ。狭い端末は全体を `JoinVertical` の縦積みに。区切り線・切り詰めは既存の `ansi`/`strings.Repeat` 流用。
- **stdout 非汚染**: 判定は捕捉 Reporter 経由のみ (既存)。描画は bubbletea が所有。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| 非 TTY | "start requires a terminal" (既存) | 2 |
| `--task` 無し / 引数誤り | 既存どおり | 2 |
| サンプルが取得できない (テスト無し等) | 左カラムに「(判定できません: …)」、右カラムにも同旨を出し続行 (chat は動く)。落とさない | (継続) |
| 判定が未実行 | 左「(まだ判定結果がありません)」・右空 (エラーにしない) | (継続) |
| 選択ケースが失敗ゼロ | 先頭 (AC) を選択し I/O 表示 (エラーにしない) | (継続) |
| chat の spawn 失敗 | 下カラムにエラー表示。上部は継続 (既存) | (継続) |
| `Ctrl+C` / `Ctrl+D` / `--until-pass` 全通過 | 正常終了 | 0 |

- 画面はキー操作の TUI。判定不能や選択の縁は exit code ではなく**画面表示**で表現する (判定・子・解答・キャッシュに触れない)。

## 非機能要件

- **表示層だけの変更**: 判定・実行・chat・fetch のロジックを増やさない。`View`/`Update` の並べ方と選択状態のみ変える。`CaseVerdict` に AC の I/O を載せる (`start.go`) 以外、データ経路は不変。
- **既存非破壊**: chat の全機能・判定ロジック・exit code・非 TTY・`test --*` 単体は不変。旧レイアウト固有の状態 (`detail bool` / `buildDetailContent`) は撤去するが、外部 API (`RunStartSplit` / `StartSplitConfig` / `StartTarget`) のシグネチャは保つ。
- **決定的にテストできる部分は純粋関数に**: 幅/高さ配分・2 カラム可否・既定選択・選択クランプ・要約/詳細の文字列化をユニットテスト。TUI 駆動・子プロセス I/O は TTY 必須で手動確認 (既存 start と同じ方針)。fixtures は従来どおり非 TTY=exit 2 の smoke のみ。
- **前方互換**: 右カラムは選択 1 ケース描画に集約したので、side-by-side (`-s` 連動)・AC/失敗フィルタ・複数ケース並置・問題文ペインの増設を後から足せる。カラム幅/高さ配分を純粋関数に切り出しておき、比率調整キーの導入余地を残す。
- **TTY 必須**: 非 TTY は exit 2 (既存維持)。

## 設計判断 (代替案・トレードオフ)

- **なぜ横 2 カラム + 常時右カラムか (却下: 縦積み拡張 / Ctrl+G トグル維持)**: AOJ v2.0 の「ステータス+テストケースを並置」を端末に写すと、判定一覧と選択ケースの中身を**同時に俯瞰**できる。036 の `Ctrl+G` トグル方式は開閉の一手間があり、一覧と詳細を並べて見られない。横分割は `JoinHorizontal` の導入だけで既存データを並べ替えられ、コストが小さい。縦積みは狭い端末のフォールバックとして残す (幅がある通常時は横 2 カラム)。
- **なぜ問題文エリアを作らないか (却下: 問題文/制約フェッチ)**: AOJ の問題ページの核は問題文エリアだが、(1) AtCoder の問題文は LaTeX を多用し、HTML→端末テキスト変換 (数式・表) が重く、readable にするコストが本要件の主眼 (判定の見せ方) から外れる。(2) 利用者は問題文をブラウザで読む運用で足りており、判定ループの TUI に本文は要らないと判断した。制約/入出力例の構造化表示も含め、**問題文系は本要件のスコープ外**とし、必要になれば別要件で問題文ペインを足す (前方互換として左カラム側に増設余地を残す)。
- **なぜ全面置換か (却下: opt-in フラグで旧レイアウト温存)**: start の画面は 1 つに保ちたい (023 も「常時分割画面」で `--no-split` を将来拡張に留めた)。二重メンテを避け、旧「縦積み + Ctrl+G トグル」は撤去する。挙動が気に入らない場合の逃げ道 (フラグ) は設けないが、レイアウト計算を純粋関数に切り出して調整余地を残す。
- **なぜフォーカスモデル (Ctrl+G) で選択するか (却下: 常時 `↑`/`↓` を選択に割当)**: chat 入力が常時 `↑`/`↓` (履歴・カーソル移動) を消費するため、選択専用にはできない。036 の `Ctrl+G` を「詳細開閉」から「判定ペインのフォーカス開閉」に引き継ぎ、フォーカス中だけ `↑`/`↓` を選択に使う。筋肉記憶を保ちつつ衝突を避ける。

## 将来の拡張ポイント

- 右カラムの side-by-side (`-s` 連動)・複数ケース並置・AC/失敗フィルタ・数字キーでのケース直接選択・マウス選択。
- カラム比率 / 上下比率の調整キー、閾値の config 化。
- (別要件) 左に問題文/制約ペインを増設して AOJ の問題文エリアに寄せる。fetch 側に問題文本文の抽出・キャッシュを足す設計が前提。
- `test --interactive` 単体でも直近サンプル判定の一覧+詳細を出す。

## 用語

- **判定一覧 (左カラム)**: 全体要約 (`✓ 2/4` + 判定時刻) と per-case verdict (`01 AC` …) の縦一覧。選択カーソルを持つ。旧「上ペイン (watch)」の後継。
- **ケース詳細 (右カラム)**: 左で選択中のケースの中身 (WA/TLE=diff、RE=stderr、AC=入力/期待)。036 の詳細表示を常時表示・選択駆動にしたもの。
- **フォーカス**: キー入力の宛先 (chat / 判定ペイン)。`Ctrl+G` で切り替える。
- **縦積みフォールバック**: 横幅が 2 カラムに満たないとき、判定一覧→ケース詳細→chat を縦に並べる代替レイアウト。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- `docs/tools/requirements/023-start-split-screen.md` (start 分割画面。本要件がレイアウトを supersede)
- `docs/tools/requirements/028-start-watch-per-case.md` (per-case verdict。左カラム一覧の元)
- `docs/tools/requirements/036-start-watch-detail-view.md` (Ctrl+G 詳細表示。右カラム常時表示に発展・supersede)
- `docs/tools/requirements/026-chat-submit.md` / `038-start-edit-in-editor.md` (下部 chat の提出準備 / エディタ起動)
- `docs/tools/usage/start.md` (利用手引・更新先)
- `docs/tools/atcoder-test-architecture.md` (start TUI 内部設計・更新先)
</content>
</invoke>
