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
| `fixture_extra` | 公式 `5`→`10` / 追加 x01 `7`→`14` / 追加 x02 `3`→`999` | — | 解答は N\*2。`tests-extra/` のユーザ追加ケースを公式の後ろに連結して判定する経路 (表示 id `x01`/`x02`)。x02 が FAIL するので suite は exit 1、`-c x01`/`-c 01` で個別指定は exit 0 |

> フラグ単位の経路も `run.sh` で smoke する。例: `fixture_pass --watch` は run.sh の出力が非 TTY のため `exit 2` で拒否されることを確認 (watch ループ本体は常駐してブロックするため fixture では回さない)。
>
> **引数順序の非依存** (`internal/cliargs`) も smoke する。`test --task pass fixture` (フラグ先頭)・`--task=pass`・フラグの間に位置引数・`-c 02` の後に contest、を `exit 0` で確認 (いずれも `test fixture --task pass` と等価)。位置引数先頭の従来ケースも全て不変。
>
> ユーザ設定 (`config.toml`) も smoke する。`run.sh` は `XDG_CONFIG_HOME` を空 dir に固定して既存テストを config 非依存にしたうえで、専用 dir に `[test] side_by_side = true` を置いて (1) 既定で side-by-side diff になる (出力に `side-by-side` が出る) (2) `--side-by-side=false` でその回だけ unified に戻る (3) 壊れた `config.toml` は `exit 2` を確認する。`side_by_side` は終了コードを変えないため、出力文字列で検証する (`check_output` ヘルパー)。
>
> `atcoder config` サブコマンドも smoke する。`config show`/`path` の出力検証、未知サブコマンド・未知キー・型不一致・引数不足の `exit 2`、書き込み専用 dir での `set` → `get` 往復、および `set` した値が `atcoder test` の diff に波及する (出力に `side-by-side` が出る) 経路を確認する。
>
> 利用テレメトリ (`atcoder usage`, 要件 037) も smoke する。`run.sh` は `XDG_DATA_HOME` を一時 dir に固定して実ユーザの `~/.local/share/atcoder-tools/usage/` を汚さず、(1) 上の各ケースの実行が `events.jsonl` に記録されること (`test` イベントを grep) (2) `atcoder usage` / `--flags` / `--json` が `exit 0` (3) `ATCODER_NO_USAGE=1` でログを書かないこと、を確認する。記録は dispatch のラップで全コマンドに透過挿入されるため、専用 fixture (`.py`) は不要。

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
