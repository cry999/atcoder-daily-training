# `atcoder login` / `atcoder logout` / `atcoder status` 利用手引

提出したコードの**ジャッジ結果 (verdict)** を端末から確認する。AtCoder の提出一覧 (`/contests/<contest>/submissions/me`) は**ログイン必須**のため、一度 `atcoder login` してセッション cookie を保存しておき、以降 `atcoder status` で当該タスクの**自分の最新提出**の verdict (AC / WA / TLE / WJ 等)・実行時間・メモリ・個別ページ URL を即時に表示する。ブラウザに切り替えずに編集ループから結果を確認できる。

> 要件詳細: `docs/tools/requirements/009-atcoder-status.md`

## はじめに (ログイン)

```
atcoder login [--user <name>] [--password-stdin]
atcoder logout
```

| フラグ | 用途 |
|---|---|
| `--user <name>` | AtCoder のユーザ名。省略時は対話プロンプト (`Username:`) で尋ねる |
| `--password-stdin` | パスワードを stdin から読む (CI / 自動化)。省略時は端末から**非表示入力** (`Password:`) |

`atcoder login` は username / password で AtCoder にログインし、得られたセッション cookie を保存する。対話時はパスワードを**非表示入力**で受け取る。`--password-stdin` を使う場合は `--user` が必須。

**パスワードは保存しない。** ログイン時に cookie を取得するためだけに使い、取得後は破棄する。保存されるのはセッション cookie (`REVEL_SESSION`) と user 名のみで、次の `session.json` に置かれる。

```
$XDG_CONFIG_HOME/atcoder-daily-training/session.json   (パーミッション 0600, 親 dir 0700)
  └ fallback: ~/.config/atcoder-daily-training/session.json
```

`session.json` は `config.toml` と同じ app dir 配下に置くが、**機械が書く秘匿ファイル**で手編集しない。`atcoder logout` で削除できる (無ければ no-op で成功扱い)。

## 使い方 (`atcoder status`)

```
atcoder status <contest> [--task <task>] [-w|--watch] [--interval <dur>] [--open]
```

| 引数 / フラグ | 既定 | 用途 |
|---|---|---|
| `<contest>` | — | contest_id (例 `abc258`)。必須 |
| `--task <task>` | — | task ID。短縮形 `d` は `<contest>_d` に展開される (`_` を含めば指定をそのまま使う)。指定時は当該タスクの**最新 1 件**、未指定は contest の最新数件 (最大 10 件) を一覧表示 |
| `--watch` / `-w` | `false` | verdict が確定 (WJ → AC/WA 等) するまでポーリング表示する。`Ctrl+C` で終了 |
| `--interval <dur>` | `3s` | `--watch` のポーリング間隔。**下限 2s** (これより短く指定しても 2s に切り上げ) |
| `--open` | `false` | 表示した提出の個別ページをブラウザで開く |

- セッションを読み、認証付きで `/contests/<contest>/submissions/me` を取得して提出一覧をパースする。
- 指定タスクの**自分の最新提出**の verdict・実行時間・メモリ・個別ページ URL を表示する。
- `--watch` は verdict が確定するまで `--interval` ごとに再取得し、確定したら最終表示して終了する。`--watch` は対象を 1 件に絞る必要があるため **`--task` が必須** (無いと exit 2)。
- `--open` を付けると、表示した提出の個別ページをブラウザで開く。

## サンプル出力

ログイン:

```
$ atcoder login --user takeharak999
Password: (非表示入力)
ログインしました: takeharak999
```

status (one-shot、`--task` 指定):

```
$ atcoder status abc258 --task d
abc258_d  D - Trophy
  AC   Python (PyPy 3.11-v7.3.20)   91 ms   108556 KiB   (2022-07-09 21:34)
  https://atcoder.jp/contests/abc258/submissions/76544704
```

1 件は最大 3 行で、`<task>  <title>` / `  <verdict>   <言語>   <実行時間>   <メモリ>   (提出日時)` / `  <URL>` の順。言語・実行時間・メモリ・日時はジャッジ中などで欠ける場合は省かれる。`--task` 未指定では最新数件 (最大 10) を同じ形式で並べる。

status (`--watch`、確定までポーリング):

```
$ atcoder status abc258 --task d --watch
abc258_d  WJ            # interval ごとに同じ行を上書き更新 (TTY)
abc258_d  Judging 3/21
abc258_d  D - Trophy    # 確定したら最終表示して終了
  AC   Python (PyPy 3.11-v7.3.20)   91 ms   108556 KiB   (2022-07-09 21:34)
  https://atcoder.jp/contests/abc258/submissions/76544704
```

提出がまだ反映されていない間は `提出待ち... <task>` を出して待機する。

## exit code

| code | 意味 |
|---|---|
| `0` | verdict 取得・表示に成功 (verdict が WA / TLE / RE / CE 等でも、`--watch` でも 0)。`Ctrl+C` での `--watch` 中断も 0 |
| `1` | 未ログイン (`atcoder login を実行してください`) / セッション失効 (`セッションが失効しました。...`) / 該当提出なし (`提出が見つかりません`) / ネットワーク・パース失敗 / login 失敗 |
| `2` | 引数不足・不正フラグ / `--watch` に `--task` 無し / 非 TTY で `login` を `--password-stdin` 無しに実行 (非表示入力できないため) |

`status` は照会コマンドなので、verdict が AC 以外でも成功扱い (verdict は判定結果ではなく取得したデータ)。

## 制約と注意

- **認証必須。** 提出一覧はログインしないと取得できない。一度ログインすれば cookie 失効まで再ログイン不要。コンテスト中でも**自分の提出**は確認できる。
- セッション失効 (302 → /login) 時は再ログインを促すだけで `session.json` は消さない (誤削除回避)。`atcoder logout` で明示的に削除する。
- `session.json` は AtCoder アカウントへのアクセス権を持つ**秘匿情報**。共有・コミットしない (XDG home 配下なのでリポジトリ外)。
- `status` は完全に読み取り専用。解答ファイル・キャッシュ・提出に一切書き込まない。
- 将来の no-auth fallback (kenkoooo AtCoder Problems API 経由、新規提出の反映に約 5 分の遅延) は**未実装で予定**。即時性が要るため当面は認証あり経路のみ。

## 関連

- 要件定義: [009-atcoder-status.md](./requirements/009-atcoder-status.md)
- config / XDG 解決: [007-atcoder-config.md](./requirements/007-atcoder-config.md)
- 提出コマンド: [atcoder-test-usage.md](./atcoder-test-usage.md)
- ツール本体: [`cmd/atcoder/login.go`](../../cmd/atcoder/login.go) / [`cmd/atcoder/status.go`](../../cmd/atcoder/status.go)
