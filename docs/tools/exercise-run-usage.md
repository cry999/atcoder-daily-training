# `exercise run` 利用手引

`test` がサンプルケースとの突合せ判定を行うのに対し、`run` は **任意の標準入力で解答を走らせて、出てきた出力をそのまま見る** ための ad-hoc 実行コマンド。判定 (PASS/FAIL) は行わない。

仕様の詳細は [exercise-test-requirements.md](./exercise-test-requirements.md) (test 側) と本ドキュメントを参照。アーキテクチャは [exercise-test-architecture.md](./exercise-test-architecture.md) (runexec パッケージのセクション)。

## 用途

- 自分で考えたエッジケースで解答の挙動を確認したい
- AtCoder にまだ問題が無い (キャッシュも無い) 状態でとりあえず動かしたい
- `[DEBUG]` 行を見ながらインタラクティブにデバッグしたい

## 前提

当日の `exercise/YYYY/MM/DD/<task>.py` が存在すること。`<task>/meta.toml` が存在すればその `time_limit_ms` を使い、無ければ 2 秒をデフォルトにする (`--timeout` で常に上書き可)。

## コマンド

```
exercise run <contest> --task <task> [-v] [-d] [--stdin <path>|-] [--timeout <dur>]
```

### 引数

| 引数 | 必須 | 説明 |
|---|---|---|
| `<contest>` | ✔ | AtCoder のコンテスト ID (例: `abc325`) |
| `--task <task>` | ✔ | AtCoder のタスク ID (例: `abc325_d`)。`_` を含まない短縮形は `<contest>_<task>` に展開される |
| `--stdin <path>` | | 標準入力として渡すファイル。`-` または省略時は親プロセスの stdin (パイプ / リダイレクト) |
| `-v` / `--verbose` | | 渡した入力 (`input:` セクション) も合わせて表示 |
| `-d` / `--debug` | | 子プロセスに `DEBUG=1` を渡し、stdout から `[DEBUG]` で始まる行を `debug:` セクションに切り出す (`test` と同じ規約) |
| `--timeout <dur>` | | 制限時間の上書き (`5s`, `500ms` 等)。未指定なら meta.toml の値、無ければ 2 秒 |

## 出力例

```
abc325_d  contest=abc325  time_limit=3000ms  (ad-hoc stdin)

  OK    27 ms
       output:
         14
```

ステータス:

| ラベル | 意味 |
|---|---|
| `OK` | 正常終了 (ExitCode == 0) |
| `TLE` | タイムアウト |
| `RE` | 非ゼロ終了 (`stderr:` を続けて表示) |

### exit code

- `0`: 正常終了
- `1`: TLE / RE / セットアップ失敗
- `2`: 引数エラー

## 例

```sh
# stdin リダイレクトで実行
exercise run abc325 --task d < my_case.txt

# パイプで渡す
echo "5\n1 2 3 4 5" | exercise run abc325 --task d

# ファイルを明示
exercise run abc325 --task d --stdin my_case.txt

# 入力と一緒に出力を確認
exercise run abc325 --task d --stdin my_case.txt -v

# DEBUG=1 を有効にしつつ ad-hoc 実行
exercise run abc325 --task d --stdin my_case.txt -d -v

# 制限時間を 10 秒に緩める (重い解法を観察)
exercise run abc325 --task d --stdin my_case.txt --timeout 10s
```

## test との比較

| | `exercise test` | `exercise run` |
|---|---|---|
| 入力 | `<task>/tests/NN.in` (複数) | `--stdin` / pipe (単一) |
| 期待出力 | `<task>/tests/NN.out` と突合 | 突合せ無し |
| 判定 | PASS / FAIL / TLE / RE | OK / TLE / RE |
| AtCoder fetch | 必要に応じて自動 | 行わない |

## 関連

- 仕様 (test): [exercise-test-requirements.md](./exercise-test-requirements.md)
- 利用 (test): [exercise-test-usage.md](./exercise-test-usage.md)
- アーキテクチャ: [exercise-test-architecture.md](./exercise-test-architecture.md)
- テスト戦略: [exercise-test-testing.md](./exercise-test-testing.md)
