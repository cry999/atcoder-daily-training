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
| `--stdin <path>` | | 標準入力として渡すファイル。省略時は親プロセスの stdin を **read-all** (batch モード)。`-` を明示した場合のみ **インタラクティブモード** に切り替わる (子の stdin/stdout/stderr を親の fd に直結し、live streaming) |
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

## インタラクティブモード

`--stdin -` を明示するとインタラクティブモードに入る:

- 子プロセスの **stdin / stdout / stderr** を親プロセスの fd に直結 (`exec.Cmd.Stdin = os.Stdin`, …)。
- 解答の出力はキャプチャされず、ターミナルへ即座に流れる (live streaming)。`output:` セクションは表示されない (既に見えているため)。
- Python は **自動で `PYTHONUNBUFFERED=1`** が渡される (行バッファ化を防ぎ、双方向の応答が成立するため)。明示的な `sys.stdout.flush()` は不要。
- `-d` (DEBUG=1) と併用可。`[DEBUG]` 行のフィルタはインタラクティブでは行わない (stream を後加工しないため、そのまま端末に出る)。

典型的な使用例:

```sh
# キーボード入力でインタラクティブに解く
exercise run abc999 --task a --stdin -

# テストハーネスで応答を仕込んで通す (CI 等で)
printf "3\nok\nok\nok\n" | exercise run abc999 --task a --stdin -
```

省略時 (`--stdin` を付けない場合) は **batch モード**: 親の stdin から read-all してから子に渡し、出力をキャプチャしてから `output:` セクションに表示する。リダイレクトやパイプで「全入力を先に決めて流す」一括処理に適する。

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
