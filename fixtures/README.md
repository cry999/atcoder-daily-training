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
| `fixture_debug` (`--submit`) | `5` | `10` | 無条件 `[DEBUG]` print はコメントアウト後ソース実行で消える → クリーン → 提出準備 (exit 0)。要件 049 |
| `fixture_debugjson` | `5` | `10` | `[DEBUG] {"grid": [[0,1],[2,3]], "n": n}` を吐く。`-d` 無しは行が混ざり FAIL (exit 1)、`-d` で PASS (exit 0)。`-d --pp` で `debug:` の JSON が 2-space 整形される (`--pp` を単体で渡すと stderr に note)。要件 047 |
| `fixture_multi` | `1`/`2`/`3` | `2`/`4`/`6` | 3 ケース持ちで `--case` フィルタの動作確認用 |
| `fixture_interactive` | 任意 | 任意 | 簡易インタラクティブ (query/response loop) — `test --interactive` 用 |
| `fixture_diff` | `1` | 3 行 (`1 2 3 4 5` / `hello world` / `last line`) | 複数行 + 行内 1 token 違いの誤答。`delta` 風の intra-line token highlight を視覚確認するため |
| `fixture_extra` | 公式 `5`→`10` / 追加 x01 `7`→`14` / 追加 x02 `3`→`999` | — | 解答は N\*2。`tests-extra/` のユーザ追加ケースを公式の後ろに連結して判定する経路 (表示 id `x01`/`x02`)。x02 が FAIL するので suite は exit 1、`-c x01`/`-c 01` で個別指定は exit 0 |
| `fixture_okdebug` | `5` | `10` | stdout は正答 (N\*2) だが `sys.stderr.write` で `[DEBUG]` を吐く (debugstrip の regex に拾われずコメントアウトをすり抜ける)。通常実行は PASS (exit 0)、`--submit` はコメントアウト後ソース実行でも `[DEBUG]` が残り検出 → 確認 → 非 TTY 中止 (exit 1)。要件 044 / 049 (安全網) |

> フラグ単位の経路も `run.sh` で smoke する。例: `fixture_pass --watch` は run.sh の出力が非 TTY のため `exit 2` で拒否されることを確認 (watch ループ本体は常駐してブロックするため fixture では回さない)。
>
> **引数順序の非依存** (`internal/cliargs`) も smoke する。`test --task pass fixture` (フラグ先頭)・`--task=pass`・フラグの間に位置引数・`-c 02` の後に contest、を `exit 0` で確認 (いずれも `test fixture --task pass` と等価)。位置引数先頭の従来ケースも全て不変。
>
> `atcoder gen` (要件 060) も smoke する。プリポピュレートされた `fixture/fixture_gen/gen.toml` (小さい制約 `N M` / 配列 / 辺リスト) を解析して生成する経路を、`--show-spec` の内容 (`scalar : N M` / `coverage: full`)・`--seed` 付き生成の `exit 0`・`--size max|min`・`-n 2 -o <dir>` の `NN.in` 生成・`--save` の `tests-extra/` 追加、および引数誤り (`--task` 欠落 / `--show-spec` と `--seed` の併用 / 不正な `--size`) の `exit 2` で固定する。`fetch` はネットワークに触れるため回さない (専用 `.py` は不要 — 生成は入力のみで judge しない)。
>
> ユーザ設定 (`config.toml`) も smoke する。`run.sh` は `XDG_CONFIG_HOME` を空 dir に固定して既存テストを config 非依存にしたうえで、専用 dir に `[test] side_by_side = true` を置いて (1) 既定で side-by-side diff になる (出力に `side-by-side` が出る) (2) `--side-by-side=false` でその回だけ unified に戻る (3) 壊れた `config.toml` は `exit 2` を確認する。`side_by_side` は終了コードを変えないため、出力文字列で検証する (`check_output` ヘルパー)。
>
> `atcoder config` サブコマンドも smoke する。`config show`/`path` の出力検証、未知サブコマンド・未知キー・型不一致・引数不足の `exit 2`、書き込み専用 dir での `set` → `get` 往復、および `set` した値が `atcoder test` の diff に波及する (出力に `side-by-side` が出る) 経路を確認する。
>
> 利用テレメトリ (`atcoder usage`, 要件 037) も smoke する。`run.sh` は `XDG_DATA_HOME` を一時 dir に固定して実ユーザの `~/.local/share/atcoder-tools/usage/` を汚さず、(1) 上の各ケースの実行が `events.jsonl` に記録されること (`test` イベントを grep) (2) `atcoder usage` / `--flags` / `--json` が `exit 0` (3) `ATCODER_NO_USAGE=1` でログを書かないこと、を確認する。記録は dispatch のラップで全コマンドに透過挿入されるため、専用 fixture (`.py`) は不要。
>
> `atcoder record` (solve-stat 記録, 要件 061) も smoke する。ネットワーク不要で、stdin が非 TTY のとき record は対話プロンプトを出さないため、非対話フラグ経路だけで決定論的に検証できる。`config set/get/show target.<category>.<letter>` (目標実装時間, 例 `target.fixture.d 30m`) と不正値 (duration でない / letter が 2 文字) の `exit 2` / `record start` が解答ファイルを作り `started_at` を刻む (冪等な再 start) / `record stop --no-ac --time 25m` が `solved_at`・`duration_ms`・(config に目標があるとき) `target_ms` を刻む / `record --score --ac --no-editorial` が 5 軸スコアと ac/editorial を部分更新し既存 duration を温存 / 個別軸フラグ `--impl` が `--score` を上書き / エラー系 (`--task` 欠落・`--score` の値数/範囲・`--ac`+`--no-ac` 併用・不正 `--time`・`record edit` 未実装・`record stop` で解答ファイル不在) の `exit 2`/`1` / solve-stat を書いた後 `stats` に `recorded (` と `score (avg` セクションが出ること、を確認する。record は既存の解答ファイル (ここでは `record start` が作る `exercise/YYYY/MM/DD/fixture_d.py`) の先頭コメントブロックを読み書きするだけで judge しないため、専用 `.py` fixture は不要。

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
