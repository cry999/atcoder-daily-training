# Test fixtures for `exercise test` / `exercise run`

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
| `fixture_interactive` | 任意 | 任意 | 簡易インタラクティブ (query/response loop) — `run --stdin -` 用 |
| `fixture_diff` | `1` | 3 行 (`1 2 3 4 5` / `hello world` / `last line`) | 複数行 + 行内 1 token 違いの誤答。`delta` 風の intra-line token highlight を視覚確認するため |

> フラグ単位の経路も `run.sh` で smoke する。例: `fixture_pass --watch` は run.sh の出力が非 TTY のため `exit 2` で拒否されることを確認 (watch ループ本体は常駐してブロックするため fixture では回さない)。

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
