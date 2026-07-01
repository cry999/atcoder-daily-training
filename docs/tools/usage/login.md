# `atcoder login` / `logout` 利用手引

ブラウザで AtCoder にログイン済みのときに持っている **`REVEL_SESSION` cookie を手で取り込む**ことで、`atcoder` CLI に認証済みセッションを持たせる。取り込んだセッションは `$XDG_DATA_HOME/atcoder-tools/session.toml` (パーミッション `0600`) に保存され、`atcoder logout` で破棄できる。

> 設計の背景・スコープは [要件 062](../requirements/062-atcoder-login-revel-session.md)、方針の決定記録は [ADR 0009](../decisions/0009-atcoder-login-revel-session-cookie.md)、認証の技術背景は [`docs/knowledge/atcoder-auth-state.md`](../../knowledge/atcoder-auth-state.md)。

## なぜ cookie 手貼りなのか

AtCoder は 2025 年初頭にログインページへ Cloudflare Turnstile を導入し、username/password による programmatic ログインは全ツールで使えなくなった。生存策はブラウザで既にログイン済みのセッション cookie (`REVEL_SESSION`) を再利用することだけで、oj / atcoder-cli / AtCoder Tools も同じ方式に収束している。本ツールも **Turnstile を突破せず、利用者が既に持つ cookie を取り込むだけ**。

このコマンドは **認証の入口 (login / セッション管理) だけ**を担う。取り込んだセッションを使う実提出 (submit POST) や提出 verdict 取得はまだ実装されておらず、将来の別要件に切ってある。

## REVEL_SESSION cookie の取り出し方 (ブラウザ)

1. ブラウザで [atcoder.jp](https://atcoder.jp) にログインする。
2. 開発者ツール → Application (Chrome) / Storage (Firefox) → Cookies → `https://atcoder.jp`。
3. `REVEL_SESSION` の値をコピーする。

この値は**秘匿情報**。他人と共有せず、取り込んだ後は CLI 側で `0600` のファイルに保存され、表示・ログには一切出さない。

## `atcoder login`

```
atcoder login [--session-cookie <value>]
atcoder login --status [--check]
```

| フラグ | 説明 |
|---|---|
| `--session-cookie <value>` | 取り込む `REVEL_SESSION` の値。省略時は stdin から読む |
| `--status` | 取り込みをせず、保存済みセッションの状態を表示する (cookie 不要) |
| `--check` | `--status` と併用。ネットワークで現在の有効性を再検証する |

### cookie の取り込み (既定動作)

`--status` 無しで実行すると cookie を取り込む。cookie の入力は次の順で決まる:

1. `--session-cookie <value>` があればそれを使う。
2. 無ければ **stdin** から読む:
   - TTY のときは `REVEL_SESSION: ` とプロンプトし、**エコーせず**に 1 行読む (秘匿入力)。
   - パイプ (非 TTY) のときはそのまま 1 行読む (`pbpaste | atcoder login` を許容)。
3. 前後の空白・改行は除去する。`REVEL_SESSION=<value>` の形で貼っても `REVEL_SESSION=` 接頭辞は自動で剥がす。

取り込んだ cookie で login-gated ページ (`https://atcoder.jp/settings`) を 1 回だけ GET して検証し、ログイン状態とユーザ名を判定する。成功したら `session.toml` に保存する。**cookie の生値は出力しない。**

```
$ atcoder login
REVEL_SESSION: (入力はエコーされない)
logged in as cry999

$ pbpaste | atcoder login          # クリップボードの cookie 値を流し込む
logged in as cry999

$ atcoder login --session-cookie 'bad-value'
atcoder login: cookie is invalid or expired (log in via browser and copy a fresh REVEL_SESSION)
# exit 1
```

### 状態表示 (`--status`)

ネットワーク無しで保存済みセッションを読み、状態を表示する。`--check` を付けると検証 GET を 1 回行い、現在も有効かを併記する。

```
$ atcoder login --status
logged in as cry999 (since 2026-07-01T12:34:56+09:00)

$ atcoder login --status --check
logged in as cry999 (since 2026-07-01T12:34:56+09:00) — valid

$ atcoder login --status      # 未ログインなら
not logged in
```

`--status` と `--session-cookie` は併用できない (引数エラー)。

## `atcoder logout`

```
atcoder logout
```

保存済み `session.toml` を削除する。無い場合も `not logged in` を出して正常終了する (冪等)。ネットワーク不要・フラグ無し。

```
$ atcoder logout
logged out

$ atcoder logout      # もう何も無いとき
not logged in
```

## 保存先

| パス | 内容 |
|---|---|
| `$XDG_DATA_HOME/atcoder-tools/session.toml` | 取り込んだ cookie (秘匿) + ユーザ名 + login 時刻。パーミッション `0600` |

`XDG_DATA_HOME` 未設定時は `~/.local/share` を使う (利用統計 `usage/`・chat 履歴 `chat-history/` と同居)。cookie は秘匿情報なので**平文 + `0600`** で保存する (at-rest 暗号化は入れていない — threat model 上 `0600` と等価で移植性を壊すため。詳細は [要件 062 の非機能要件](../requirements/062-atcoder-login-revel-session.md#非機能要件))。

## exit code

| code | 意味 |
|---|---|
| `0` | 成功 (`--status` の `not logged in` 表示・冪等な `logout` を含む) |
| `1` | cookie が無効・期限切れ、Cloudflare チャレンジ検出、検証 GET のネットワーク失敗、I/O 失敗、`--status --check` で期限切れ |
| `2` | 引数・フラグ誤り (空 cookie、`--status` と `--session-cookie` の併用、`--check` 単独指定、余分な位置引数など) |

## セッションが切れたら

保存した cookie は時間が経つと失効する。失効すると、消費側 (将来の submit など) は「再ログインしてください」を促す。`atcoder login --status --check` で事前に有効性を確認でき、切れていたらブラウザで新しい `REVEL_SESSION` をコピーして `atcoder login` し直す。

```
$ atcoder login --status --check
logged in as cry999 (since 2026-07-01T12:34:56+09:00) — expired (please re-login)
# exit 1
```

## 注意

- **自動ログイン (Turnstile 突破) はしない。** 利用者が既に持つ cookie を再利用するだけ。cookie が取れない・失効したときはブラウザ側でログインし直してから取り込む。
- cookie は秘匿情報。`--session-cookie` でシェル履歴に残したくないなら、stdin 経由 (`pbpaste | atcoder login` やプロンプト入力) を使う。
- 検証 GET は 1 回だけ。ポーリング・連投はしない (rate limit 配慮)。
