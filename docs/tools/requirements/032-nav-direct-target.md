# chat ナビ `:contest` / `:task` に直指定 (絶対ジャンプ) を追加 要件定義

## 概要

`atcoder start` 分割画面の chat command モードのナビ ([027](027-start-problem-navigation.md)) で、`:contest` / `:task` を `next`/`prev` (相対移動) だけでなく **直指定 (絶対ジャンプ)** にも対応させる。`:contest 123` で現シリーズの 123 番 (例 `abc457` から `abc123`) へ、`:task f` で現コンテストの問題記号 `f` へ、その場で移動する。種別固定の直指定なので、自由形式の `:e <spec>` とは役割を分ける。

## 背景・目的

- 現状 `:contest` / `:task` は `next`/`prev` (別名 `n`/`p`) の**相対移動だけ**で、離れた番号・記号へ一気に飛べない。`:e abc500_d` の自由形式ジャンプはあるが、「今のコンテストで D 問題へ」「123 回へ」のような**種別を固定した直指定**は冗長 (`:e abc123_<現letter>` を手で組む必要がある)。
- 相対移動と同じコマンド語彙のまま第 2 トークンに番号/記号を置けると、`next/prev` で寄せるか直接飛ぶかを 1 系統で選べて素直。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| `:task <letter>` | 現コンテストの問題記号 `letter` (単一 a–z) へ。例 `:task f` | 記号範囲外の検証メッセージ細分化 |
| `:contest <num>` | 現シリーズ (プレフィックス・桁数保持) の `num` 回へ、**現 letter を保持**。例 `:contest 123` → `abc123` | シリーズ跨ぎの相対移動 |
| `:contest <id>` | 完全なコンテスト ID 直指定も許容 (`:contest arc100`)、現 letter を保持 | — |
| 相対移動 | `:contest`/`:task` の `next`/`prev` (`n`/`p`) は不変 | — |

### 境界

- 既存の `:e <spec>` (自由形式: `f` / `abc500_d`) は不変。**役割分担**: `:task`=記号のみ・`:contest`=コンテストのみ (letter 保持)・`:e`=任意。
- `NavEnabled` が偽 (`test --interactive` 単体) では従来どおり**未知コマンド扱い** (`E492`)。ナビは start 分割画面限定 ([027])。
- レイアウト解決・着手・再ターゲット・判定・exit code は [027] のまま。本要件は**移動先の決め方**に直指定を足すだけ。

## CLI / TUI 仕様

新フラグ無し。command モード (insert で `Esc` → `:`) の `:contest` / `:task` の第 2 トークン解釈を拡張する。

| コマンド | 第 2 トークン | 動作 |
|---|---|---|
| `:task next` / `:task n` | — | 記号 +1 (既存) |
| `:task prev` / `:task p` | — | 記号 −1 (既存) |
| **`:task <letter>`** | 単一 a–z | 現コンテストの記号 `letter` へ直接移動 (例 `:task f`) |
| `:contest next` / `n` | — | 番号 +1・letter 保持 (既存) |
| `:contest prev` / `p` | — | 番号 −1・letter 保持 (既存) |
| **`:contest <num>`** | 数字のみ | 現シリーズの番号 `num` へ・letter 保持 (例 `:contest 123` → `abc123`) |
| **`:contest <id>`** | コンテスト ID | そのコンテストへ・letter 保持 (例 `:contest arc100`) |

### 処理ステップ

1. `navRequestFor` (純粋関数) が第 2 トークンを見る: `next`/`prev`/`n`/`p` は従来の相対 `NavRequest`。それ以外で**非空**なら直指定として **`NavLetterExplicit`**(`:task`)/ **`NavContestExplicit`**(`:contest`) を `Spec` 付きで返す。空なら `ok=false` (利用法案内)。
2. `execNav` が `NavEnabled` のとき `NavMsg` を親へ発火 (既存経路。直指定でも同じ)。
3. 親 `nextTarget` (resolver) が新 Kind を解決:
   - `NavLetterExplicit`: `Spec` を小文字化し単一 a–z を検証 → `(現 contestID, TaskID(現 contestID, letter))`。
   - `NavContestExplicit`: `Spec` が数字のみ → `layout.WithContestNum(現 contestID, num)` (プレフィックス・桁数保持) / コンテスト ID 形 → そのまま採用。現 letter を `layout.Letter` で保ち `TaskID(newID, letter)`。
4. 不正値はエラー文字列を返し、再ターゲットせず **TUI 内 1 行で案内** ([027] と同じ。chat は継続)。

### 出力イメージ

```
:task f
(→ abc457_f に移動しました)
solution: exercise/2026/06/11/abc457_f.py (exists)
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `:task f` | 現コンテストの記号 f へ。`f` は小文字化・単一 a–z 検証 |
| `:task 5` / `:task xx` | 記号として不正 → `E492` (記号は単一英字。`:e <task_id>` を促す)。再ターゲットせず継続 |
| `:contest 123` | 現プレフィックス+桁数で 123 回へ (`abc457`→`abc123`)、letter 保持 |
| `:contest 5` | 桁数保持でゼロ埋め (`abc457`→`abc005`) |
| `:contest arc100` | コンテスト ID 直指定、letter 保持 |
| `:contest 0` / 負 | 範囲外 → `E492` (1 以上)。継続 |
| `:task` / `:contest` (引数なし) | 利用法案内 (`next|prev|<直指定>`)。再ターゲットなし |
| `NavEnabled` 偽 (`test --interactive`) | 直指定も従来どおり未知コマンド扱い (`E492`) |

- **既存非破壊**: `next`/`prev`・`:e`・他コマンド・キー・判定・exit code は不変。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/ui/nav.go` | `NavKind` に `NavLetterExplicit` / `NavContestExplicit` を追加。`navRequestFor` の `:task`/`:contest` で、`next`/`prev` 以外の非空トークンを直指定 `NavRequest{Kind, Spec}` に写す。`Spec` は第 1 トークン |
| `internal/layout/layout.go` | `WithContestNum(contestID string, n int) (string, error)` を追加 (プレフィックス・桁数を保持して番号を絶対設定。`splitContestID` 流用、`n<1` は `ErrContestBound`、形不正は `ErrContestShape`) |
| `cmd/atcoder/start.go` | `nextTarget` に `NavLetterExplicit` / `NavContestExplicit` の解決を追加 (letter 検証は `ShiftLetter(letter,0)` 再利用、contest は数字→`WithContestNum` / ID 形→`ContestNum` 検証して採用、現 letter 保持) |
| `internal/ui/chat_casebuilder.go` | `execNav` の利用法案内文を「`next|prev` (n|p) または直指定」に更新。`showCheat` の `:task`/`:contest` 行を直指定対応の表記に更新 |
| `internal/ui/nav_test.go` | `navRequestFor` が `:task f`→`NavLetterExplicit{Spec:"f"}`、`:contest 123`→`NavContestExplicit{Spec:"123"}`、引数なし→`ok=false` を返すテスト |
| `cmd/atcoder/start_test.go` | `nextTarget` が直指定を解決 (`:task f`/`:contest 123`/桁数保持/不正値エラー) するテスト。`layout` 側に `WithContestNum` の単体テスト |
| `docs/tools/usage/start.md` / `docs/tools/usage/test.md` | command 表のナビ説明に直指定を追記 |

### 型の素描

```go
// internal/ui/nav.go
const (
    // … 既存 NavLetterNext/Prev, NavContestNext/Prev, NavExplicit …
    NavLetterExplicit  // :task <letter>   — Spec=letter (現コンテスト)
    NavContestExplicit // :contest <num|id> — Spec=コンテスト指定 (letter 保持)
)

// internal/layout/layout.go
// WithContestNum は contestID のプレフィックス・桁数を保ったまま番号を n に置く。
func WithContestNum(contestID string, n int) (string, error)
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `:task <非英字/複数文字>` | `E492` (記号は単一英字。`:e` を促す)。再ターゲットなし・継続 |
| `:contest <番号 < 1>` | `E492` (1 以上)。継続 |
| `:contest <形不正>` (数字も ID 形でもない) | `E492` (`:contest <番号>` か `:contest <id>` を促す)。継続 |
| 移動先に letter が無い (task に記号なし) | `E492` (記号移動に対応していません)。継続 |
| exit code | 影響なし (TUI 内案内のみ。引数誤り=2 / 実行時失敗=1 は不変) |

## 非機能要件

- **既存非破壊**: 相対 `next`/`prev`・`:e`・他コマンド・判定・chat 描画は不変。解答ファイルは [027] と同じく「無ければ空ファイル生成・既存温存」。
- **stdout 非汚染**: 案内は chat 内 info 行のみ。
- **前方互換**: 直指定は新 `NavKind` で表すので、相対移動の表現を壊さない。`WithContestNum` は他のナビ拡張からも使える純粋関数。
- **決定的にテスト可能**: `navRequestFor` / `nextTarget` / `WithContestNum` を純粋に保ち、直指定の写像・解決・桁数保持・不正値をユニットテストで固定する。

## 将来の拡張ポイント

- `:task` の範囲チェックを「そのコンテストに存在する記号」まで踏み込む (現状は形のみ)。
- `:contest` のシリーズ跨ぎ相対移動 (`:contest arc next`)。

## 用語

- `contest_id`=`abc457` / `contest_num`=`457` / `task_id`=`abc457_d` / `letter`=`d` (既存要件準拠)。
- **直指定 (絶対ジャンプ)**: `next`/`prev` の相対移動に対し、番号・記号を直接与えて移動すること。
- **相対移動**: 現在地から ±1 する `next`/`prev`。

## 関連ドキュメント

- ナビ基盤: [027](027-start-problem-navigation.md) / command モード: [024](024-interactive-case-builder.md)
- 分割画面: [023](023-start-split-screen.md)
- 利用手引: `docs/tools/usage/start.md` / `docs/tools/usage/test.md`
