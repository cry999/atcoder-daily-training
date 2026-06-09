# Test fixtures for `atcoder test` (samples + ad-hoc/interactive modes)

ツール自身の挙動をスモークテストするための fixture 一式と、それを走らせるスクリプト。

ツール本体は **解答 (`exercise/YYYY/MM/DD/<task>.py`)** と **キャッシュ (`$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/`)** を別の場所に保存する設計のため、`run.sh` は両者を 2 つの一時ディレクトリに振り分け、後者を `XDG_CACHE_HOME` 経由でツールに渡す。

## 実行

```sh
./fixtures/run.sh
```

ツールを `go build` し、各 fixture について実行・exit code を assert。最後にまとめを出力する。

## fixture 一覧

| fixture | 入力 | 期待出力 | 期待挙動 |
|---|---|---|---|
| `fixture_pass` | `5` | `10` | 正答 (N\*2)。PASS、exit 0 |
| `fixture_fail` | `5` | `10` | 誤答 (N\*2+1)。FAIL、exit 1 |
| `fixture_re` | `5` | `10` | `RuntimeError` を raise。RE、exit 1 |
| `fixture_tle` | `5` | `10` | `time.sleep(2)`、`time_limit=200ms` のため TLE、exit 1 |
| `fixture_debug` (`-d` 無し) | `5` | `10` | `[DEBUG]` 行で汚染 → FAIL、exit 1 |
| `fixture_debug` (`-d` 付き) | `5` | `10` | `[DEBUG]` がフィルタされ PASS、exit 0 |
| `fixture_multi` | `1`/`2`/`3` | `2`/`4`/`6` | 3 ケース持ちで `--case` フィルタの動作確認用 |
| `fixture_interactive` | 任意 | 任意 | 簡易インタラクティブ (query/response loop) — `test --interactive` 用 |
| `fixture_diff` | `1` | 3 行 (`1 2 3 4 5` / `hello world` / `last line`) | 複数行 + 行内 1 token 違いの誤答。`delta` 風の intra-line token highlight を視覚確認するため |

> フラグ単位の経路も `run.sh` で smoke する。例: `fixture_pass --watch` は run.sh の出力が非 TTY のため `exit 2` で拒否されることを確認 (watch ループ本体は常駐してブロックするため fixture では回さない)。
>
> ユーザ設定 (`config.toml`) も smoke する。`run.sh` は `XDG_CONFIG_HOME` を空 dir に固定して既存テストを config 非依存にしたうえで、専用 dir に `[test] side_by_side = true` を置いて (1) 既定で side-by-side diff になる (出力に `side-by-side` が出る) (2) `--side-by-side=false` でその回だけ unified に戻る (3) 壊れた `config.toml` は `exit 2` を確認する。`side_by_side` は終了コードを変えないため、出力文字列で検証する (`check_output` ヘルパー)。
>
> `atcoder config` サブコマンドも smoke する。`config show`/`path` の出力検証、未知サブコマンド・未知キー・型不一致・引数不足の `exit 2`、書き込み専用 dir での `set` → `get` 往復、および `set` した値が `atcoder test` の diff に波及する (出力に `side-by-side` が出る) 経路を確認する。
>
> `atcoder status` / `login` / `logout` も**ネットワーク非依存**で smoke する。`XDG_CONFIG_HOME` が空隔離 dir のため `session.json` が無く、`status` は「未ログイン」で `exit 1` (HTTP を一切叩かない)。引数誤りは `exit 2` (`status` の contest 欠落、`--watch` に `--task` 無し)。`login` は cookie 取り込み式 (AtCoder ログインは Cloudflare Turnstile 保護のため username/password では不可)。`run_piped` (非 TTY) で (1) `--session-cookie`/`--session-stdin` 無しは対話不可で `exit 2` (2) `--session-stdin` への空入力は cookie 空で `exit 2` を確認する。実ログイン・実ジャッジ取得は認証が要るため fixture では回さない。

## ディレクトリ構造

解答ファイルとキャッシュは別軸に分かれる:

```
fixtures/
  README.md
  run.sh
  fixture_pass.py            # 解答 (.py)
  fixture_fail.py
  ...
  cache/                     # XDG_CACHE_HOME に丸ごとマウントされる前提のレイアウト
    atcoder-tools/
      fixture/               # contest 名 = "fixture"
        fixture_pass/
          meta.toml
          tests/
            01.in
            01.out
        fixture_fail/
        ...
```

スクリプトは:

1. `fixtures/*.py` を `$STAGE/exercise/YYYY/MM/DD/` に複製する
2. `fixtures/cache/` の中身を `$CACHE_HOME` に複製し `XDG_CACHE_HOME=$CACHE_HOME` を export する
3. `$STAGE` に `cd` してからツールを呼び出す

これでツールは「解答は当日 dir、キャッシュは XDG」という通常運用と同じ経路でファイルを参照する。
