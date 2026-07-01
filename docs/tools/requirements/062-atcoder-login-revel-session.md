# `atcoder login` / `logout` (REVEL_SESSION cookie 取り込み認証) 要件定義

## 概要

ブラウザで AtCoder にログイン済みの利用者が持つ **`REVEL_SESSION` cookie を手で取り込む**ことで、`atcoder` CLI に認証済みセッションを持たせる。`atcoder login` で cookie を受け取り・検証し・永続化し、`atcoder logout` で破棄し、`atcoder login --status` で現在のログイン状態を確認する。

本要件は **認証の入口 (login / セッション管理) だけ**を対象にする。取り込んだセッションを消費する機能 (実提出 POST・提出 verdict 取得) は**スコープ外**とし、将来の要件が使えるよう `internal/atcoder` にセッション取得の公開 API だけを用意する。

方針の決定記録は [ADR 0009](../decisions/0009-atcoder-login-revel-session-cookie.md)。

## 背景・目的

- AtCoder は 2025 年初頭にログインページへ **Cloudflare Turnstile** を導入し、**username/password の programmatic ログインは全滅**した。oj / atcoder-cli / AtCoder Tools いずれも正攻法ログインは不可で、**唯一の生存策はブラウザの `REVEL_SESSION` cookie 取り込み**に収束している (詳細・出典: [`docs/knowledge/atcoder-auth-state.md`](../../knowledge/atcoder-auth-state.md))。
- このリポジトリでも過去に `login` / `status` を実装したが、上記の理由と「毎回 cookie を手で取り込む UX が重い」判断で撤去した ([todo.md K](../todo.md))。今回は **その UX を受け入れた上で**、cookie 取り込み方式に一本化して login を再設計する。**自動ログイン (Turnstile 突破) は一切しない**ため、K の第一の却下理由 (programmatic ログイン不可) には抵触しない。
- login はそれ自体が目的ではなく、**将来の認証付き機能 (実提出・verdict 取得) の土台**になる。[ADR 0006](../decisions/0006-fold-submit-into-test.md) が「認証が安定したら `test --submit` を実 POST へ格上げする (案 A)」を将来余地として残しており、本要件のセッション API がその前提を用意する (実提出の設計は別要件)。

## スコープ

| 項目 | 当面のスコープ (この要件) | 将来の拡張余地 (別要件) |
|---|---|---|
| cookie 取り込み | `REVEL_SESSION` を **手貼り** (`--session-cookie` フラグ / stdin) | ブラウザ cookie DB からの自動抽出 (`--from-browser`)、`--cookie-file` |
| セッション操作 | `login` (取り込み・検証・保存) / `logout` (破棄) / `login --status` (状態表示) | — |
| 検証 | login-gated ページを 1 回 GET しログイン状態 + ユーザ名を判定 | 定期的な自動再検証・期限の事前通知 |
| 消費側 | セッション取得の**公開 API** (`internal/atcoder`) を用意するだけ | 実提出 (submit POST・csrf)、提出 verdict 取得 (status) |
| 認証方式 | 取り込んだ cookie の再利用のみ | (自動ログイン・password・CAPTCHA 突破は**恒久的に対象外**) |

### 境界

- **実提出 (submit POST) は本要件では作らない。** 取り込んだセッションを使う最初の消費側だが、csrf 取得・LanguageId 選択・誤提出防止・ToS 配慮など固有の設計判断が要るため別要件に切る。本要件は `internal/atcoder` に「認証済みリクエストを作る」API を置くところまで。
- **verdict 取得 (status) も作らない。** AtCoder Problems API は約 5 分遅延で live 判定に不適 ([knowledge doc](../../knowledge/atcoder-auth-state.md))、`/submissions/me` 取得は submit 設計とセットで検討する。
- **自動ログイン・ブラウザ自動化は恒久的に対象外。** 本ツールは利用者が既に持つ cookie を再利用するだけで、Turnstile を突破しない (業界標準の aclogin 方式と同じ立場)。
- **解答ファイル・キャッシュ・設定には触れない。** 保存先はセッション専用ファイル 1 つ。`--refresh` 系の対象にもしない。

## ディレクトリ構造 / スキーマ

セッションは**秘匿情報 (認証 cookie)** なので、設定 (`config.toml`) やキャッシュとは分離し、**データ領域**に専用ファイルとして `0600` で置く。usagelog / chatlog と同じ `$XDG_DATA_HOME/atcoder-tools/` 配下に置く。

```
$XDG_DATA_HOME/atcoder-tools/          # 既存 (usage/, chat-history/ と同居)
  session.toml                         # 新規。パーミッション 0600
```

### `session.toml` スキーマ

```toml
revel_session = "<REVEL_SESSION cookie 値>"   # 秘匿。表示・ログ出力しない
username      = "cry999"                       # login 時に解決したユーザ名
logged_in_at  = 2026-07-01T12:34:56+09:00
```

| フィールド | 型 | 取得元 | 用途 |
|---|---|---|---|
| `revel_session` | string | 利用者が貼った cookie 値 | 認証リクエストの `Cookie: REVEL_SESSION=...` |
| `username` | string | login 時の検証 GET で解決 | `--status` 表示・確認メッセージ |
| `logged_in_at` | time | login 実行時刻 | `--status` 表示・鮮度の目安 |

- `revel_session` は**秘匿値**。CLI 出力・usagelog・エラーメッセージのいずれにも生値を出さない (usagelog はフラグ**名**のみ記録する既存仕様と整合)。
- ファイルは `0600`、親ディレクトリは `0700` で作成する。
- ID 用語は既存要件に準拠 (`contest_id`=`abc457` / `task_id`=`abc457_d` / `letter`=`d`)。

## CLI 仕様

新サブコマンド **`login`** と **`logout`** を追加する。

### `atcoder login [--session-cookie <value>] [--status] [--check]`

| フラグ | 説明 |
|---|---|
| `--session-cookie <value>` | 取り込む `REVEL_SESSION` の値。省略時は stdin から読む |
| `--status` | 取り込みをせず、保存済みセッションの状態を表示する (cookie 不要) |
| `--check` | `--status` と併用。ネットワークで現在の有効性を再検証する |

**cookie の入力 (既定動作、`--status` 無し):**

1. `--session-cookie <value>` があればそれを使う。
2. 無ければ **stdin** から読む:
   - stdin が TTY のときは `REVEL_SESSION: ` とプロンプトし、**エコーせず** 1 行読む (秘匿入力)。
   - stdin が非 TTY (パイプ) のときはそのまま 1 行読む (`pbpaste | atcoder login` を許容)。
3. 前後の空白・改行を除去する。`REVEL_SESSION=<value>` 形式で貼られた場合は `REVEL_SESSION=` 接頭辞を剥がして値だけを取る。
4. 値が空なら**引数誤り (exit 2)**。

**処理ステップ (`atcoder login`):**

1. cookie 値を用意する (上記)。
2. **検証**: `internal/atcoder.Validate(cookie)` が login-gated ページ (例 `https://atcoder.jp/settings`) を cookie 付きで GET し、ログイン状態とユーザ名を判定する。未認証/期限切れは `ErrUnauthenticated` (exit 1)、Cloudflare チャレンジ検出は `ErrChallenge` (exit 1)、ネットワーク失敗は exit 1。
3. **保存**: 検証成功なら `session.toml` (0600) に `revel_session` / `username` / `logged_in_at` を書く (既存があれば上書き)。
4. `logged in as <username>` を出力して exit 0。**cookie 値は出力しない。**

**`atcoder login --status`:** ネットワーク無しで保存済みセッションを読み、`logged in as <username> (since <logged_in_at>)` または `not logged in` を表示する。`--check` を付けると検証 GET を 1 回行い、`valid` / `expired (please re-login)` を併記する。`--status` と `--session-cookie` の併用は**引数誤り (exit 2)**。

### `atcoder logout`

保存済み `session.toml` を削除する。無い場合も `not logged in` を出して exit 0 (冪等)。ネットワーク不要。フラグ無し。

### 出力イメージ

```
$ atcoder login
REVEL_SESSION: (入力はエコーされない)
logged in as cry999

$ atcoder login --status
logged in as cry999 (since 2026-07-01T12:34:56+09:00)

$ atcoder login --status --check
logged in as cry999 (since 2026-07-01T12:34:56+09:00) — valid

$ pbpaste | atcoder login          # クリップボードの cookie 値を流し込む
logged in as cry999

$ atcoder logout
logged out
```

```
$ atcoder login --session-cookie 'bad-value'
error: cookie is invalid or expired (log in via browser and copy a fresh REVEL_SESSION)
# exit 1
```

## 動作仕様

| 観点 | 仕様 |
|---|---|
| 冪等性 | `login` は成功のたびに `session.toml` を上書き。`logout` は無セッションでも exit 0 |
| 秘匿性 | `revel_session` の生値は CLI 出力・usagelog・エラーに一切出さない。ファイルは `0600` |
| 非 TTY | `login` の cookie は非 TTY stdin から読める (パイプ)。`--status`/`logout` は TTY 非依存 |
| 再ログイン | 保存 cookie が後で期限切れになったら、消費側は `ErrUnauthenticated` を受け「再 `login` してください」を促す。`login --status --check` で事前に気づける |
| 既存非破壊 | `test`/`start`/`gen`/`meta` 等の既存挙動・キャッシュ・設定に影響しない。問題ページ fetch は従来どおり cookie 無し (認証不要) |
| ネットワーク | 検証 GET は **1 回のみ**。ポーリング・連投はしない (rate limit 配慮) |
| 消費側 API | 実提出・status は本要件では未実装。`internal/atcoder` の公開 API 経由でのみ将来接続する |

## 影響範囲

| ファイル / パッケージ | 変更内容 |
|---|---|
| 新規 `internal/atcoder/` | セッションの型・永続化・検証・認証リクエスト生成。下記 API 素描を参照 |
| 新規 `cmd/atcoder/login.go` | `cmdLogin(args)` — フラグパース、cookie 入力 (flag/stdin・秘匿読み)、検証、保存、`--status` 表示 |
| 新規 `cmd/atcoder/logout.go` | `cmdLogout(args)` — `session.toml` 削除 (冪等) |
| `cmd/atcoder/main.go` | `builtins` に `login`/`logout` 追加、`dispatch` に `case` 追加、`usage` 文字列更新 |
| `internal/complete/complete.go` | `login`/`logout` サブコマンド候補、`login` の `--session-cookie`/`--status`/`--check` フラグ補完 |
| `internal/cliargs/cliargs.go` | `--session-cookie` を値フラグ (value-flag) として登録 |
| 秘匿入力 | TTY 非エコー読みのため `golang.org/x/term` (`term.ReadPassword`) を追加検討。導入是非は実装 (feature) で確定 |

### 新規 `internal/atcoder/` パッケージの責務 (API 素描)

```go
// Package atcoder は AtCoder の認証セッション (REVEL_SESSION cookie) を
// 取り込み・検証・永続化し、認証付きリクエストを組み立てる。
// login / logout / 将来の submit・status がここを経由する。
package atcoder

// Session はログイン済みセッション (cookie + メタ)。
type Session struct {
    RevelSession string    // REVEL_SESSION cookie 値 (秘匿)
    Username     string    // login 時に解決したユーザ名
    LoggedInAt   time.Time
}

// Path は session.toml の保存先 ($XDG_DATA_HOME/atcoder-tools/session.toml)。
func Path() (string, error)

// Load は保存済みセッションを読む。無ければ (nil, ErrNoSession)。
func Load() (*Session, error)

// Save は 0600 で session.toml に書く (親 dir は 0700)。
func Save(s *Session) error

// Clear は session.toml を削除する (無ければ no-op)。
func Clear() error

// Validate は cookie で login-gated ページを GET し、ログイン状態とユーザ名を返す。
// 未認証/期限切れは ErrUnauthenticated、Cloudflare チャレンジは ErrChallenge。
func Validate(revelSession string) (username string, err error)

// NewRequest は保存済み cookie と標準 User-Agent を付けた *http.Request を作る。
// 将来の submit/status など認証付き経路の唯一の入口 (層境界)。
func (s *Session) NewRequest(ctx context.Context, method, url string, body io.Reader) (*http.Request, error)

var (
    ErrNoSession       = errors.New("no session")               // 未ログイン
    ErrUnauthenticated = errors.New("cookie invalid or expired")
    ErrChallenge       = errors.New("cloudflare challenge")
)
```

### 検証の中身 (ベストエフォート)

- login-gated な安定ページ (第一候補 `https://atcoder.jp/settings`) を cookie 付きで GET する。未認証だと `/login?continue=...` へリダイレクトされるので、**最終 URL が `/login` を含むなら未認証**と判定する。
- ログイン時はページ内にユーザ本人のリンク (`a[href="/users/<name>"]`) が出るので、そこから `username` を取る (正確なセレクタは実装 feature で確定)。
- 応答が Cloudflare チャレンジ (challenge ホスト・`cf-` マーカー) なら `ErrChallenge`。
- HTTP クライアントは既存 fetch (`internal/testexec/fetch.go`) と同じ User-Agent 規約を踏襲する (共有定数化を検討)。

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| cookie 値が空 (flag 空・stdin 空) | `error: empty cookie` で exit 2 |
| `--status` と `--session-cookie` 併用 / 未知フラグ | usage を出して exit 2 |
| cookie が無効・期限切れ (login ページへリダイレクト) | `error: cookie is invalid or expired` で exit 1。`session.toml` は書かない |
| Cloudflare チャレンジ検出 | `error: hit Cloudflare challenge; open the browser, refresh, and copy a new REVEL_SESSION` で exit 1 |
| 検証 GET のネットワーク失敗 | エラー表示で exit 1 |
| `login --status` で未ログイン | `not logged in` を出して exit 0 (エラーではない) |
| `login --status --check` で期限切れ | `... — expired (please re-login)` を出して exit 1 |
| `logout` で無セッション | `not logged in` を出して exit 0 (冪等) |
| `session.toml` 読み書き失敗 (権限等) | エラー表示で exit 1 |

## 非機能要件

- **秘匿情報の扱い**: `revel_session` の生値を出力・ログ・エラーに出さない。`session.toml` は `0600`、親 dir は `0700`。usagelog はフラグ名のみ記録する既存仕様に依拠し cookie 値を残さない。
- **at-rest 暗号化はしない (方針)**: `session.toml` は平文 + `0600` で保存し、アプリ層での暗号化は本要件では入れない。理由は 3 点:
  1. **threat model 上 `0600` と等価**: 復号鍵を同じマシンに置けば「ファイルが読めれば鍵も読める」ので難読化にしかならない。`0600` + 親 dir `0700` が守るべき現実的な脅威 (同一マシンの別ユーザからの読み取り) をちょうどカバーし、ディスク盗難・root 奪取はフルディスク暗号化 (FileVault 等) の領分でアプリ層の責務ではない。
  2. **移植性を壊す**: 本物の at-rest 暗号化は OS キーチェーン連携 (macOS Keychain / Linux Secret Service / Windows DPAPI) が要り、「cookie は手貼りで OS・ブラウザ非依存」「移植性」という本要件の非機能目標や、CI・ヘッドレス・cron 実行と矛盾する。パスフレーズ方式は「毎回入力が重い」を受け入れた本要件の UX 方針とさらに衝突する。
  3. **業界標準が平文 + 制限パーミッション**: 範に取る aclogin (online-judge-tools) は cookie を平文の cookie.jar に置き、atcoder-cli・AtCoder Tools も同様。REVEL_SESSION 取り込み方式を採る既存ツール群が揃ってこの立場。
  - 保存側の at-rest 暗号化を検討するとしても、同じく OS キーチェーンに触る `--from-browser` (ブラウザ cookie 自動抽出) を入れる将来要件とセットで扱う (下記「将来の拡張ポイント」)。
- **cookie を環境変数経由で渡さない**: `NewRequest` が組む `Cookie:` ヘッダの値が `/proc/<pid>/environ` や `ps` 出力に漏れないよう、cookie は環境変数ではなくメモリ内で受け渡す (実装 feature で確認する)。
- **既存非破壊**: `login`/`logout` は新サブコマンドで、既存コマンド・キャッシュ・設定・解答ファイルに触れない。問題ページ fetch は従来どおり無認証のまま。
- **ネットワーク礼儀**: 検証は 1 回の GET のみ。自動ポーリングや連投をしない。
- **exit code 規約**: 引数・フラグ誤り = 2 / 実行時失敗 (検証失敗・ネットワーク・I/O) = 1 / 成功 (未ログイン表示を含む) = 0。
- **前方互換**: セッションの消費は `internal/atcoder` の公開 API に一本化し、将来の submit/status がそこだけを経由する (層境界)。`session.toml` にユーザ名・時刻を持たせておき、後続機能が追加フィールドを足しても後方互換に読めるようにする。
- **標準 `flag` 維持**: 外部 CLI フレームワークは導入しない。
- **移植性**: cookie は手貼り (flag/stdin) で OS・ブラウザ非依存。秘匿入力の非エコーは TTY のときだけ (非 TTY はそのまま読む)。

## 将来の拡張ポイント

- **実提出 (submit POST)**: 取り込んだセッションで `test --submit` を実 POST へ格上げする ([ADR 0006](../decisions/0006-fold-submit-into-test.md) の案 A)。csrf 取得・数値 LanguageId 選択・提出前ゲート ([要件 044](044-submit-precheck-confirm.md)) との接続・誤提出防止・ToS 配慮を別要件で設計する。`internal/atcoder.NewRequest` を入口にする。
- **提出 verdict 取得 (status)**: submit と同じセッションで `/submissions/me` を取得。live 判定は AtCoder Problems API の遅延で不可なので、認証 cookie 経路とセットで検討。
- **ブラウザ cookie 自動抽出** (`--from-browser`): aclogin 流に手貼りの手間を消す。OS/ブラウザ依存・Chrome の OS キーチェーン暗号化解除が要るため後回し。保存側の **at-rest 暗号化** (session.toml を OS キーチェーンで保護) を検討するなら、同じくキーチェーンに触るこの要件とセットで扱う (単独では threat model 上 `0600` と等価で移植性を壊すため見送り。上記「非機能要件」参照)。
- **`--cookie-file <path>`**: スクリプト連携用にファイルからも読む。

## 用語

- **REVEL_SESSION**: AtCoder が使う Revel フレームワークのセッション cookie。ブラウザでログイン中ならこの 1 個で認証状態を持てる。手貼りの対象。
- **login-gated ページ**: ログインしていないと `/login` へリダイレクトされるページ (検証に使う。第一候補 `/settings`)。
- **Cloudflare チャレンジ**: cookie が失効・不正なとき等に返る Cloudflare のボット検証応答。検出したら `ErrChallenge` で中止する。
- **セッション API**: `internal/atcoder` が公開する、認証済みリクエスト生成の唯一の入口。submit/status など消費側はここだけを経由する。

## 関連ドキュメント

- 決定記録: [ADR 0009 — AtCoder 認証は REVEL_SESSION cookie 取り込みで行う](../decisions/0009-atcoder-login-revel-session-cookie.md)
- 認証の技術背景・出典: [`docs/knowledge/atcoder-auth-state.md`](../../knowledge/atcoder-auth-state.md)
- ロードマップ: [`todo.md`](../todo.md) の **K. 認証 (`atcoder login`)**
- submit を browser-defer に畳んだ決定 (案 A を将来余地に): [ADR 0006](../decisions/0006-fold-submit-into-test.md) / [要件 015](015-fold-submit-into-test.md)
- 提出前ゲート (将来の実提出が繋ぐ先): [要件 044](044-submit-precheck-confirm.md)
- 利用手引: `docs/tools/usage/login.md` (実装時に新規作成 — feature フェーズ)
