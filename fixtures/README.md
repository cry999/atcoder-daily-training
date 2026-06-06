# Test fixtures for `exercise test`

`exercise test` コマンド自身の挙動をスモークテストするための fixture 一式と、それを走らせるスクリプト。

ツール本体には「テスト用パス上書き」のような専用機能は持たせていない。代わりに `run.sh` が一時ディレクトリ内に当日の `exercise/YYYY/MM/DD/` 構造を作り、そこに fixtures を複製してから `cd` 経由でツールを呼び出す (= 普段のユースケースと同じ呼び出し方になる)。

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
| `fixture_multi` | `1`/`2`/`3` | `2`/`4`/`6` | 3 ケース持ちで `--case` フィルタの動作確認用 (`fixture_pass` と同じ N\*2 ロジック)。指定無しなら 3 ケース全 PASS、`--case 02` で 1 ケース、`--case 99` で「該当無し」エラー exit 1 |

## ディレクトリ構造

各 fixture は `exercise/YYYY/MM/DD/<task>.py` + `exercise/YYYY/MM/DD/<task>/{meta.toml,tests/NN.in NN.out}` という規約 (要件定義書参照) に従う。

```
fixtures/
  README.md
  run.sh
  fixture_pass.py
  fixture_pass/
    meta.toml
    tests/
      01.in
      01.out
  fixture_fail.py
  fixture_fail/
    ...
```
