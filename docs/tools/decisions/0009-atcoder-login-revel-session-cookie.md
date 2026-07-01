# ADR 0009: AtCoder 認証はブラウザの REVEL_SESSION cookie 取り込みで行う (自動ログインはしない)

- ステータス: Accepted
- 日付: 2026-07-01
- 要件: [requirements/062-atcoder-login-revel-session.md](../requirements/062-atcoder-login-revel-session.md)
- 関連: [0006](0006-fold-submit-into-test.md) (submit を browser-defer に畳み、認証安定後の実 POST を将来余地に) / 背景調査 [`docs/knowledge/atcoder-auth-state.md`](../../knowledge/atcoder-auth-state.md)

## コンテキスト

AtCoder は 2025 年初頭にログインページへ **Cloudflare Turnstile** を導入し、username/password の programmatic ログインが全滅した。oj / atcoder-cli / AtCoder Tools いずれも正攻法ログインは不可となり、**唯一の生存策はブラウザの `REVEL_SESSION` cookie を取り込む方式**に収束している (aclogin が事実上の標準)。submit POST 自体は有効 cookie があれば従来どおり通る。

このリポジトリでも過去に `login`/`logout`/`status` を実装したが、(a) programmatic ログインが Turnstile で不可、(b) cookie 取り込みは動くが毎回ブラウザから手でコピーする UX が重い、という理由で**撤去した** (todo.md「K」)。

その後、認証済みセッションを再び持ちたい要求が出た (将来の実提出・verdict 取得の土台として)。実現手段は cookie 取り込み一択で、争点は「UX の重さを受け入れるか」と「どこまで作るか」。

## 決定

**認証は利用者がブラウザで得た `REVEL_SESSION` cookie を手で取り込む方式に一本化する。自動ログイン (Turnstile 突破) は恒久的に実装しない。**

- `atcoder login` が cookie を **手貼り** (`--session-cookie` フラグ / stdin の秘匿読み) で受け取り、login-gated ページを 1 回 GET して検証し、`$XDG_DATA_HOME/atcoder-tools/session.toml` (0600) に保存する。`logout` で破棄、`login --status` で状態表示。
- セッションの消費 (認証付きリクエスト生成) は新パッケージ **`internal/atcoder`** の公開 API に一本化する。**本決定のスコープは login / セッション管理まで**で、実提出 (submit POST) と verdict 取得 (status) は API の消費側として別要件に切る。
- cookie は**秘匿情報**として扱う: 生値を出力・ログ・エラーに出さず、ファイルは 0600。設定 (`config.toml`) やキャッシュとは分離してデータ領域に置く。

## 結果

- 過去に「再着手しない」とした K の判断を、**cookie 取り込み方式・login スコープに限って覆す**。K の第一の却下理由 (programmatic ログイン不可) には抵触しない — 本ツールは利用者が既に持つ cookie を再利用するだけで Turnstile を突破しないため。第二の理由 (手貼り UX の重さ) は、利用者判断で**受け入れる**。
- [ADR 0006](0006-fold-submit-into-test.md) が将来余地に残した「認証安定後に `test --submit` を実 POST へ格上げ (案 A)」の前提となる認証基盤が、`internal/atcoder` のセッション API として用意される。ただし実 POST の設計・実装は本 ADR のスコープ外 (別要件)。
- セッションは 1 ファイル (`session.toml`) に閉じ、既存の fetch / test / submit-prep・キャッシュ・設定を無改修に保つ。

## 却下した代替案

- **programmatic な username/password ログイン (自動化)**: Turnstile で全ツールが全滅済み。実現不可。ブラウザ自動化 (Selenium 等) での突破も、脆く ToS 上も踏み込まない。→ 恒久的に不採用。
- **ブラウザ cookie DB からの自動抽出 (`--from-browser`, aclogin 流)**: 手貼りより便利だが、OS/ブラウザ依存が強く Chrome は OS キーチェーンでの cookie 暗号化解除が要り実装が重い。手貼りで動く最小形を先に固め、**将来の拡張余地**として保留。
- **cookie を `config.toml` に保存**: 認証 cookie は秘匿情報で、共有・可視性の高い設定ファイルに混ぜたくない。データ領域の専用ファイル (0600) に分離する。
- **login スコープを飛ばして submit まで一気に設計**: 実提出は csrf・LanguageId・誤提出防止・ToS 配慮など固有判断が多く、認証基盤とは分けて設計するほうが安全。まず login / セッション管理を確定し、submit は別要件へ。
- **現状維持 (browser-defer のみ)**: `test --submit` でブラウザに委ねる最小フリクションのままにする案。認証済みセッションを前提とする将来機能の土台が得られない。
