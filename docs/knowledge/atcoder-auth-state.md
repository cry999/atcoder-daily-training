# AtCoder の認証・提出の現状 (2025–2026 / 類似ツール横断調査)

## TL;DR

- AtCoder は **2025 年初頭に Cloudflare Turnstile (CAPTCHA)** をログインに導入し、**username/password の programmatic ログインは全滅**した (HTTP POST 直叩きも、`online-judge-tools` の Selenium 自動化も両方壊れた)。
- **今も生き残っている唯一の認証手段は「ブラウザの `REVEL_SESSION` cookie を取り込む」方式**。oj / atcoder-cli (acc) / AtCoder Tools いずれもこの形に収束。`aclogin` がブラウザ cookie を oj・acc の cookie ストアへコピーするのが事実上の標準回避策。
- **提出 (submit) 自体は壊れていない**。有効な cookie があれば従来どおり `csrf_token` + session cookie で `/contests/<contest>/submit` へ数値 `LanguageId` 付き POST が通る。壊れたのは「cookie を得る入口 (ログイン)」であって submit ではない。Cloudflare チャレンジに当たった応答では失敗する。
- **このリポジトリの判断 (todo.md「K」で login/status を撤去) は業界全体の現状と一致**。再導入するなら cookie 取り込み方式一択で、UX が重い (毎回ブラウザから cookie を手で取り込む) という K の却下理由はそのまま有効。

## 経緯 (Turnstile タイムライン)

- AtCoder がログインページに **Cloudflare Turnstile** を導入。ブラウザが JS で生成する検証トークン (`cf-turnstile-response`) が無いと、正しい資格情報でも拒否される。
- **`online-judge-tools` issue #934 (2025-03-17)** がこれを記録し、「Turnstile が Selenium ログインをブロックする」と明言。回避策として `aclogin` (cookie 取り込み) を推奨。
- ⚠️ **正確な導入日は未確定** (調査で特定できず)。「2025 年初頭まで」が確度高。

## ツール横断比較

### 認証 (ログイン)

| ツール | 元の方式 | Turnstile 後の現状 |
|---|---|---|
| online-judge-tools (oj) | username/password POST、または Selenium (GUI ブラウザ)。`--use-browser-cookie`/`LOGIN_WITH_COOKIES` は **yukicoder 専用で AtCoder 非対応** | Selenium ログインは **不可**。**既存/取り込み済み cookie があれば認証は通る**。oj 自身「認証まわりは非常に複雑かつ壊れやすい」と自認 |
| atcoder-cli (acc) | ログインは **oj に委譲** (acc 単体は認証を持たない) | `acc login` は **失敗** (acc #67)。oj 側に cookie があれば動く。acc 固有のサンプル取得・テストは無認証で従来どおり |
| AtCoder Tools | **v2.16.0 (2025-11-14)** で **手動取り込み cookie 認証** (PR 310) | cookie 取り込みで維持。提出前に Cloudflare チャレンジを検出すると `CaptchaError` で中止 (PR 311) |
| aclogin (key-moon) | — (補助ツール) | ブラウザの `REVEL_SESSION` cookie を oj・acc の cookie ストアへコピー。oj メンテナ推奨の標準回避策 |

### 提出 (submit)

| 項目 | 実態 |
|---|---|
| 仕組み | 従来どおり: session cookie + hidden `csrf_token` を付けて `/contests/<contest>/submit` へ POST。フォーム項目は `TaskScreenName` / **数値 `LanguageId`** / `sourceCode` (oj-api `atcoder.py` で確認) |
| Turnstile の影響 | **提出ページ自体は Turnstile 保護されていない**。有効 cookie があれば submit POST は通る |
| 失敗検出 | AtCoder Tools は応答が Cloudflare チャレンジホストなら中止。oj/acc の検出有無は未確認 |

### コンテスト中・代替手段

- **AtCoder Problems API はリアルタイムでない**: 通常 **約 5 分の遅延**、コンテスト後はさらに遅れ、bulk データセットは **週 1 更新**。アクセスは **1 秒以上の間隔**が礼儀 (`doc/api.md` / `faq_ja.md`)。→ **ライブコンテストの verdict 取得には使えない**。
- ToS / 自動化の是非はルールページ参照 (下記)。本調査では「自動化を明示禁止」等の**具体条文は検証済み主張として抽出できず** — URL は提示するが断定しない。

## このリポジトリへの含意

- **正攻法の自動ログインは再実装しない** (Turnstile で全ツールが諦めた)。
- 提出を再導入する現実解は **cookie 取り込み方式** (ユーザがブラウザの `REVEL_SESSION` を貼る) + submit POST。技術的には動くが、毎回 cookie を手で取り込む運用の重さが難点 (= K の却下理由)。
- 当面は **browser-defer** (`test --submit` で提出ページをブラウザで開く) が最小フリクションで合理的。cookie 取り込みは「やれば動くが UX が重い将来オプション」として温存。

## 出典

- oj Turnstile 記録: <https://github.com/online-judge-tools/oj/issues/934>
- aclogin (cookie 取り込み): <https://github.com/key-moon/aclogin>
- acc ログイン不可: <https://github.com/Tatamo/atcoder-cli/issues/67>
- oj-api 提出実装: <https://github.com/online-judge-tools/api-client/blob/master/onlinejudge/service/atcoder.py>
- AtCoder Tools CHANGELOG (v2.16.0 cookie 認証・CaptchaError): <https://github.com/kyuridenamida/atcoder-tools/blob/stable/CHANGELOG.md>
- AtCoder Problems API 制約: <https://github.com/kenkoooo/AtCoderProblems/blob/master/doc/api.md> / `faq_ja.md`
- AtCoder ルール: <https://info.atcoder.jp/overview/contest/rules> / LLM ルール <https://info.atcoder.jp/entry/llm-rules-ja>

## 確度・留保

- **高確度**: cookie 取り込みが唯一の生存ログイン手段 / submit POST は cookie で通る / AtCoder Problems の遅延・礼儀制限。
- **未確定**: Turnstile の正確な導入日、submit の連投レート制限値、oj・acc のチャレンジ検出有無。
- **棄却した主張 (採用しない)**: 「oj メンテナが『同じ Turnstile 破綻が login を要する全ツールに及び修正不能』と確認した」は 3 票中 2 票で否定 → 過度な一般化はしない。

## 関連

- ロードマップ: `docs/tools/todo.md` の **K. 提出ジャッジ状況の確認 (撤去)**。
- 調査日: 2026-06-16 (deep-research、18 ソース・25 主張を 3 票検証)。
