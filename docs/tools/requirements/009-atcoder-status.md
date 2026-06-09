# `atcoder status` / `atcoder login` 要件定義

> **更新 (実装後に判明): AtCoder ログインは Cloudflare Turnstile 保護に変わった。**
> 当初は `atcoder login` を username / password の programmatic ログインで設計したが、
> AtCoder のログインページは Cloudflare Turnstile (ボット対策) を導入しており、ブラウザが
> JS で生成する検証トークン無しでは正しい資格情報でも拒否される。よって **`atcoder login`
> はブラウザの `REVEL_SESSION` cookie を取り込む方式に変更**した (`--session-cookie` /
> `--session-stdin` / 対話プロンプト)。Turnstile はログイン**ページ**のみで、ログイン後の
> `/submissions/me` 等は cookie だけでアクセスできるため、`status` の設計は不変。以降の
> username / password に関する記述は歴史的経緯として残す。利用手引は
> `docs/tools/atcoder-status-usage.md` を参照。

## 概要

提出したコードの**ジャッジ結果 (verdict)** をターミナルから確認できる `atcoder status` サブコマンドを追加する。AtCoder の提出一覧 (`/submissions/me`) は**ログイン必須**のため、併せて **`atcoder login` / `atcoder logout`** を追加し、セッション cookie を保存して認証付きで提出一覧を取得する。`atcoder status <contest> --task <task>` で当該タスクの**自分の最新提出の verdict** (AC / WA / TLE / WJ 等) を即時に表示する。

`docs/tools/todo.md` の「K. 提出ジャッジ状況の確認」の要件詳細。調査の結果、認証なし経路 (公開個別ページ + kenkoooo API) は **提出一覧が AtCoder 直では列挙不可**・**kenkoooo は反映まで約 5 分の遅延**のため即時性が出ず、本要件では**認証あり経路を採用**する。認証なし経路は将来の no-auth fallback として `Source` 抽象の別実装に残す。

## 背景・目的

- `atcoder submit` は提出ページをブラウザで開くだけで、提出後の verdict はブラウザに切り替えて自分で確認している。「今出したコードの結果」を端末から確認できれば編集ループから目を離さずに済む。
- 調査で判明した制約 (これが認証ありを選ぶ根拠):
  - **個別提出ページ `/contests/<c>/submissions/<id>` は公開** (200) だが、**提出一覧 `/submissions` および `?f.User=&f.Task=` はログイン必須** (302 → `/login`)。よって認証なしでは「自分の提出 ID を列挙」できない。
  - 認証なしで列挙可能な唯一の経路 **kenkoooo AtCoder Problems API** は公式 FAQ で**新規提出の反映に約 5 分**・コンテスト中の非公開提出は非対応・第三者依存。即時フィードバック用途に合わない。
  - 認証あり (`/submissions/me`) なら**即時・コンテスト中も・AtCoder 公式データ**で取得できる。
- 一度 `atcoder login` すればセッション cookie が保存され、以降 `atcoder status` は再ログイン不要 (cookie 失効まで)。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 認証 | username/password で `/login` → セッション cookie 保存 | OAuth 的なものは AtCoder に無し。`--password-stdin` での非対話ログイン |
| 取得経路 | 認証付き `/contests/<contest>/submissions/me` の HTML スクレイプ | no-auth fallback (kenkoooo API) を `Source` 別実装で追加 |
| 表示単位 | `--task` 指定で当該タスクの**最新 1 件**。未指定は contest の最新数件 | `--all` で全件、結果別フィルタ |
| ライブ更新 | `--watch` で verdict 確定 (WJ → AC/WA 等) までポーリング | `submit` 完了からの自動 watch 連携 |
| セッション保存 | `$XDG_CONFIG_HOME/atcoder-daily-training/session.json` (0600) | 複数アカウント、keyring 連携 |
| user 指定 | `config.toml` の `user_id` / `--user` は**将来の no-auth 用に予約**。認証経路では session の user を使う | no-auth source で必須化 |

### 認証なし経路を今回採らない理由 (記録)

- 提出一覧が AtCoder 直で列挙不可 → kenkoooo 依存が不可避。
- kenkoooo は**約 5 分の反映遅延** (公式 FAQ) で「提出直後に確認」に向かない・コンテスト中非対応・第三者の可用性に依存 (過去に長期停止例あり)。
- ただし `Source` インターフェースを切っておき、認証不要の手軽さが欲しくなったら kenkoooo 実装を**追加**できる前方互換を残す (本要件の `internal/atcoder` 設計で担保)。

## ディレクトリ構造 / 保存物

```
# セッション (新規・機械管理・手編集しない・秘匿)
$XDG_CONFIG_HOME/atcoder-daily-training/session.json   (perm 0600, 親 dir 0700)
  └ fallback: ~/.config/atcoder-daily-training/session.json
```

- 既存 `config.toml` (手編集する設定) と同じ app dir に置くが、`session.json` は**機械が書く秘匿ファイル**。XDG ベース解決は `internal/config` の既存ロジックを再利用する (`config.SessionPath()` を追加)。
- リポジトリ外 (XDG home) なので `.gitignore` 対象外。万一リポジトリ内に出力されても拾わないようパスは XDG 固定。

### session.json スキーマ

```json
{
  "user": "takeharak999",
  "session_cookie": "REVEL_SESSION=...",
  "saved_at": "2026-06-09T21:00:00+09:00"
}
```

| キー | 型 | 用途 |
|---|---|---|
| `user` | string | ログインしたユーザ名。`status` の表示・整合チェック用 |
| `session_cookie` | string | `REVEL_SESSION=<value>` 1 本。これだけで認証付き GET が成立する |
| `saved_at` | string (RFC3339) | 保存時刻。失効診断・表示用 |

- **パスワードは保存しない**。ログイン時のみ使い、cookie 取得後は破棄する。

## CLI 仕様

### `atcoder login`

```
atcoder login [--user <name>] [--password-stdin]
```

| 引数/フラグ | 必須 | 用途 |
|---|---|---|
| `--user <name>` | no | ユーザ名。省略時は対話プロンプトで尋ねる |
| `--password-stdin` | no | パスワードを stdin から読む (CI/自動化)。省略時は端末から**非表示入力** |

処理ステップ:

1. ユーザ名を確定 (`--user` or プロンプト)。
2. パスワードを取得 (`--password-stdin` なら stdin 1 行、そうでなければ `term.ReadPassword` で非表示入力)。
3. `GET https://atcoder.jp/login` → cookiejar に pre-auth `REVEL_SESSION` を受け、フォームの隠し `csrf_token` を抽出。
4. `POST https://atcoder.jp/login` に `username` / `password` / `csrf_token` を form-encoded 送信 (同 jar)。
5. ログイン成否を判定: 認証後の jar で**ログイン必須ページに 302 されないか**を確認 (例: 任意 contest の `/submissions/me` が 200 か、`/login` へ戻されないか)。失敗なら exit 1。
6. 成功なら jar の `REVEL_SESSION` と user を `session.json` (0600) に保存。パスワードは破棄。
7. `ログインしました: <user>` を表示し exit 0。

### `atcoder logout`

```
atcoder logout
```

- `session.json` を削除 (無ければ no-op で 0)。`ログアウトしました` を表示。

### `atcoder status`

```
atcoder status <contest> [--task <task>] [--watch] [--interval <dur>] [--open]
```

| 引数/フラグ | 必須 | 既定 | 用途 |
|---|---|---|---|
| `<contest>` | yes | — | contest_id (例 `abc258`) |
| `--task <task>` | no | — | task。短縮形 `d` は `<contest>_d` に展開。指定時は当該タスクの最新 1 件、未指定は contest の最新数件 |
| `--watch` / `-w` | no | false | verdict が確定するまでポーリング表示。`Ctrl+C` で終了 |
| `--interval <dur>` | no | `3s` | `--watch` のポーリング間隔。**下限 2s** (rate limit 配慮) |
| `--open` | no | false | 表示した提出の個別ページをブラウザで開く |

処理ステップ (`atcoder status abc258 --task d`):

1. `session.json` を読む。無ければ exit 1 (`atcoder login を実行してください`)。
2. 認証付き `Source` を構築 (cookie を載せた HTTP client)。
3. `Source.Submissions(contest)` → `GET /contests/<contest>/submissions/me` を取得・パース。**302 → /login** (cookie 失効) は exit 1 (`セッションが失効しました。atcoder login を実行してください`)。
4. `--task` 指定時は task で絞り、提出日時の最新 1 件を選ぶ。該当なしは exit 1 (`提出が見つかりません`)。未指定は最新数件を一覧表示。
5. verdict と実行時間・メモリ・個別ページ URL を表示。`--watch` かつ verdict が未確定 (WJ/Judging) なら `--interval` ごとに再取得し、確定したら最終表示して exit 0。
6. `--open` なら個別提出ページをブラウザで開く。

### 出力イメージ

```
$ atcoder login --user takeharak999
Password: (非表示入力)
ログインしました: takeharak999

$ atcoder status abc258 --task d
abc258_d  D - Trophy
  AC   PyPy3   91 ms   108556 KiB   (2022-07-09 21:34)
  https://atcoder.jp/contests/abc258/submissions/76544704

$ atcoder status abc258 --task d --watch
abc258_d  D - Trophy
  WJ ...        # 2 秒ごとに更新
  Judging 3/21
  AC   91 ms   108556 KiB     # 確定したら最終表示して終了
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| 未ログインで `status` | exit 1、`atcoder login を実行してください` |
| cookie 失効 (302→/login) | exit 1、再ログインを促す。session.json は残す (誤削除回避) |
| `--task` 該当提出なし | exit 1、`提出が見つかりません` |
| verdict が AC 以外 (WA/TLE/RE/CE…) | **exit 0** (status は照会コマンド。verdict は判定結果ではなくデータ) |
| `--watch` で確定 | 最終 verdict を表示し exit 0 (AC/WA いずれでも 0) |
| `--watch` 中の `Ctrl+C` | exit 0 (test --watch と同じ) |
| `--interval` が 2s 未満 | 2s に切り上げ (rate limit 配慮) |
| login 失敗 (資格情報誤り) | exit 1、`ログインに失敗しました` (パスワードは出力しない) |
| 非 TTY で `login` (`--password-stdin` 無し) | exit 2 (非表示入力できないため) |
| 冪等性 | `status` は読み取りのみ。解答ファイル・キャッシュ・提出に一切書かない |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| 新規 `internal/atcoder/` | 認証 client・セッション保存/読込・`/submissions/me` パーサ・`Source` 抽象・verdict 確定判定 |
| 新規 `cmd/atcoder/login.go` | `atcoder login` / `atcoder logout` 本体 |
| 新規 `cmd/atcoder/status.go` | `atcoder status` 本体 (one-shot + `--watch`) |
| `cmd/atcoder/main.go` | `login`/`logout`/`status` の dispatch + `usage()` 更新 |
| `internal/config/config.go` | `SessionPath()` 追加 (app dir 配下の session.json パス)。`user_id` は将来 no-auth 用に予約コメント |
| `fixtures/run.sh` | 認証なしでも回せる smoke (未ログイン status=1 / login 非 TTY=2 / 引数誤り=2)。AtCoder には触らない |
| `docs/tools/atcoder-status-usage.md` | 新規利用手引 (login → status、watch、session の所在と削除) |
| `docs/tools/todo.md` | 「K」を `✅ DONE` でマークし「決まったこと」を引用追記 |

### 新規 `internal/atcoder/` パッケージの責務

```go
package atcoder

// Submission は提出 1 件分。Source 実装間で共通の形。
type Submission struct {
    ID          int       // 提出 ID (個別ページ URL の末尾)
    Task        string    // task screen name 例 "abc258_d"
    TaskTitle   string    // 例 "D - Trophy"
    Verdict     string    // "AC" / "WA" / "WJ" / "Judging 3/21" など生の結果文字列
    Language    string
    Score       int
    ExecTimeMs  int       // 未確定時は 0
    MemoryKiB   int       // 未確定時は 0
    SubmittedAt time.Time
    URL         string    // 個別提出ページ
}

// Source は提出一覧の取得元。認証あり (/submissions/me) を当面実装し、
// 将来 no-auth (kenkoooo) を別実装として足せるようにする前方互換の seam。
type Source interface {
    // Submissions は呼び出し元ユーザの contest 内提出を新しい順で返す。
    Submissions(contest string) ([]Submission, error)
}

// Session は保存された認証情報 (cookie + user)。
type Session struct {
    User          string
    SessionCookie string // "REVEL_SESSION=..."
    SavedAt       time.Time
}

// Login は username/password で AtCoder にログインし Session を返す。
func Login(user, password string) (*Session, error)

// SaveSession / LoadSession / DeleteSession は session.json を 0600 で永続化する。
func SaveSession(s *Session) error
func LoadSession() (*Session, error) // 無ければ (nil, ErrNoSession)
func DeleteSession() error

// AuthedSource は cookie を載せた client で /submissions/me を引く Source。
func AuthedSource(s *Session) Source

// IsFinal は verdict が確定 (再取得不要) かを返す。WJ/WR/Judging は false。
func IsFinal(verdict string) bool
```

- HTTP は `testexec/fetch.go` と同じ流儀 (明示 User-Agent・`net/http`)。cookie は `http.Client` に手で `Cookie` ヘッダを載せるか `cookiejar` を使う。
- パーサは `htmlquery` (既存依存) で提出テーブルの各行から上記フィールドを抽出。個別ページ URL から `ID` を取る。
- **seam の要点**: `status` は `Source` にのみ依存。認証あり/将来の no-auth は実装差し替えで、verdict 整形・watch ループは共通。

## エラーハンドリング

| 状況 | 動作 (exit) |
|---|---|
| 引数不足 / 不正フラグ | usage を出して **2** |
| `login` を非 TTY かつ `--password-stdin` 無し | **2** (非表示入力不可) |
| login 資格情報誤り・login 経路の HTTP 失敗 | **1**、`ログインに失敗しました` (秘密情報は出さない) |
| `status` 未ログイン (session 無し) | **1**、`atcoder login を実行してください` |
| `status` cookie 失効 (302→/login) | **1**、再ログインを促す |
| `status` ネットワーク/パース失敗 | **1** |
| `--task` 該当提出なし | **1**、`提出が見つかりません` |
| 正常 (verdict 取得・表示) | **0** (AC/WA いずれでも) |

## 非機能要件

- **セキュリティ (最重要)**:
  - パスワードは**保存しない・ログ出力しない**。`term.ReadPassword` で非表示入力、または `--password-stdin`。
  - 保存するのは `REVEL_SESSION` cookie + user のみ。`session.json` は **0600**、親 dir **0700**。
  - cookie は AtCoder アカウントへのアクセス権を持つ。`atcoder logout` で確実に削除できる。失効時は再ログインを促すのみ。
  - 通信は HTTPS 固定。明示的な User-Agent を付ける。
- **rate limit 配慮**: `--watch` の `--interval` 下限 2s。デフォルト 3s。AtCoder/`login` を不要に叩かない (status は 1 回 1 リクエスト)。
- **解答ファイル非破壊**: `status` は読み取りのみ。解答・キャッシュ・提出に書き込まない。
- **前方互換**: `Source` 抽象で no-auth (kenkoooo) 実装を後から追加可能。`config.toml` の `user_id` を no-auth 用に予約。session.json は未知キーを無視。
- **既存非破壊**: 既存サブコマンド (`test`/`run`/`submit`/`new`/`stats`/`commit`) に影響なし。

## 将来の拡張ポイント

- **no-auth fallback**: kenkoooo API を実装する `Source`。未ログイン時に `--user`/config の `user_id` で kenkoooo から取得 (約 5 分遅延を明示)。
- **`submit` 連携**: `atcoder submit` 後に自動で `status --watch` を起動し、提出から確定まで一気通貫。
- **複数アカウント / keyring**: session を keyring に格納、`--account` で切替。
- **`--all` / 結果フィルタ**: contest 全提出・WA のみ等。

## 用語

- **verdict (結果)**: AtCoder のジャッジ結果文字列。確定: AC/WA/TLE/RE/CE/MLE/OLE/QLE/IE。未確定: WJ/WR/Judging n/m。
- **session cookie**: `REVEL_SESSION`。これ 1 本で認証付き GET が成立する。
- **Source**: 提出一覧の取得元抽象。認証あり (`/submissions/me`) / 将来 no-auth (kenkoooo) を差し替える seam。
- (`contest_id` / `task_id` / `letter` は 002 / 003 の要件定義に準拠)

## 関連ドキュメント

- `docs/tools/todo.md` の「K. 提出ジャッジ状況の確認」(本要件の発端。認証必須の調査結論)
- `docs/tools/requirements/007-atcoder-config.md` (config.toml と XDG 解決。`SessionPath()` の置き場)
- `cmd/atcoder/submit.go` (認証を避けブラウザに委譲してきた既存設計。本機能で初めて認証を持つ)
- `docs/tools/atcoder-status-usage.md` (利用手引・新規)
