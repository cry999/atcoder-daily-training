# ADR 0006: `submit` を `test --submit` に畳む (実提出は auth 安定まで保留)

- ステータス: Accepted
- 日付: 2026-06-09
- 要件: [requirements/015-fold-submit-into-test.md](../requirements/015-fold-submit-into-test.md)
- 関連: [0005](0005-unify-test-run-into-test.md) (run→test の前例)

> **追記 (後日):** ここで参照していた `login`/`status` の認証基盤は、AtCoder ログインが Cloudflare Turnstile 保護で programmatic ログイン不可と判明したため**撤去された** (todo.md「K」)。submit を `test --submit` に畳む本決定自体は有効で、実提出 (認証 POST) への格上げ案 (案 A) は実現不可として打ち切り。

## コンテキスト

`atcoder submit` は「サンプル全通過を確認 → 解答をクリップボードへコピー → 提出ページをブラウザで開く」だけの薄い前準備で、実提出 (POST) はしていなかった (認証を持たない設計のため)。独立コマンドとしての価値が薄く、実体は「test して緑なら提出準備」。

その後 `login`/`status` で認証基盤 (`internal/atcoder` のセッション + CSRF) は入ったが、**まだ安定していない**。submit を本物の認証付き提出へ格上げする道もある (案 A) が、不安定な認証に依存させるのは時期尚早。

## 決定

`submit` サブコマンドを**削除**し、提出準備を **`atcoder test --submit`** フラグに畳む。

- `--submit` は「サンプルが全通過したら、続けてコピー + ブラウザ起動」を行うサンプルモードの修飾フラグ。`--no-open` は維持。
- **実提出 (認証 POST) はしない**。認証が安定するまではブラウザ起動に委ねる現行方針を保つ。
- `openBrowser` は `test --submit` の提出ページ起動に使う共有関数として残す (submit.go から移設)。

## 代替案 (却下)

- **案 A: submit を本物の認証付き提出へ格上げ (独立コマンド維持)**: `internal/atcoder` のセッションで実 POST し `status` に繋ぐ。理想だが**認証がまだ不安定**で、誤提出・ToS・レート等のリスクを不安定な土台の上に載せたくない。auth 安定後に再検討する将来案として保留。
- **submit を現状のまま (browser-defer) 独立コマンドで残す**: ユーザが「意味が薄い」と感じている現状維持で、フリクションが減らない。
- **`--submit` ではなく `--copy`/`--open` に分割**: 粒度は上がるが面の数が増える。提出準備は 1 まとまりの行為なので単一フラグ `--submit` (+ 修飾 `--no-open`) が素直。

## 結果

- コマンドが 1 つ減り、「test して緑なら提出準備」が `test --submit` で表現される (run 統合と同じ筋)。
- 破壊的変更: `atcoder submit <c> --task d [--no-open]` → `atcoder test <c> --task d --submit [--no-open]`。
- 実提出は依然ブラウザ任せ。認証が安定したら案 A (test --submit を実 POST へ) を ADR で更新する余地を残す。
- `--submit` はサンプルモード専用で、ad-hoc (`--in/--out/--interactive`)・`--watch` とは併用不可 (exit 2)。
