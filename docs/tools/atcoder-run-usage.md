# `atcoder run` 利用手引

`test` がサンプルケースとの突合せ判定を行うのに対し、`run` は **任意の標準入力で解答を走らせて、出てきた出力をそのまま見る** ための ad-hoc 実行コマンド。判定 (PASS/FAIL) は行わない。

仕様の詳細は [001-exercise-test.md](./requirements/001-exercise-test.md) (test 側) と本ドキュメントを参照。アーキテクチャは [atcoder-test-architecture.md](./atcoder-test-architecture.md) (runexec パッケージのセクション)。

## 用途

- 自分で考えたエッジケースで解答の挙動を確認したい
- AtCoder にまだ問題が無い (キャッシュも無い) 状態でとりあえず動かしたい
- `[DEBUG]` 行を見ながらインタラクティブにデバッグしたい

## 前提

当日の `exercise/YYYY/MM/DD/<task>.py` が存在すること。`<task>/meta.toml` が存在すればその `time_limit_ms` を使い、無ければ 2 秒をデフォルトにする (`--timeout` で常に上書き可)。

## コマンド

```
atcoder run <contest> --task <task> [-v] [-d] [--in <path>|-] [--out <path>] [--interactive] [--timeout <dur>] [--tolerance <eps>] [--layout <auto|abc|exercise>]
```

### 引数

| 引数 | 必須 | 説明 |
|---|---|---|
| `<contest>` | ✔ | AtCoder のコンテスト ID (例: `abc325`) |
| `--task <task>` | ✔ | AtCoder のタスク ID (例: `abc325_d`)。`_` を含まない短縮形は `<contest>_<task>` に展開される |
| `--in <path>` / `-i` | | 入力ソース。**`-` を指定または省略するとどちらも親プロセスの stdin を read-all する batch モード** (両者は等価)。ファイルパスを渡すとそのファイルを read する batch モード |
| `--out <path>` / `-o` | | 期待出力ファイル。指定すると stdout をこのファイルと突合せ判定する (judge モード、常に batch) |
| `--interactive` / `-I` | | **インタラクティブモード**。子の stdin/stdout/stderr を親に直結し live で対話する。TTY なら chat TUI を起動。入力は親 stdin から読むので、`--out` やファイル指定の `--in <path>` とは併用不可 (引数エラー) |
| `-v` / `--verbose` | | 渡した入力 (`input:` セクション) も合わせて表示 |
| `-d` / `--debug` | | 子プロセスに `DEBUG=1` を渡し、stdout から `[DEBUG]` で始まる行を `debug:` セクションに切り出す (`test` と同じ規約) |
| `--timeout <dur>` | | 制限時間の上書き (`5s`, `500ms` 等)。未指定なら meta.toml の値、無ければ 2 秒 |
| `--tolerance <eps>` | | `--out` judge モードでの float トークン比較の許容誤差 (例: `1e-9`)。未指定または `0` は既定の `1e-6` |
| `--layout <auto\|abc\|exercise>` | | 解答ファイルの配置規約 (`test` と同じ)。`auto` (既定) は `abc<NNN>` なら `abc`、それ以外は `exercise` |

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
# stdin リダイレクトで実行 (--in 省略 = --in - と等価な batch)
atcoder run abc325 --task d < my_case.txt

# パイプで渡す (--in 省略 = --in - と等価な batch)
echo "5\n1 2 3 4 5" | atcoder run abc325 --task d

# ファイルを明示 (batch)
atcoder run abc325 --task d --in my_case.txt

# 入力と一緒に出力を確認
atcoder run abc325 --task d --in my_case.txt -v

# DEBUG=1 を有効にしつつ ad-hoc 実行
atcoder run abc325 --task d --in my_case.txt -d -v

# 制限時間を 10 秒に緩める (重い解法を観察)
atcoder run abc325 --task d --in my_case.txt --timeout 10s

# インタラクティブモード (--interactive)。端末から直接なら chat UI が起動する
atcoder run abc999 --task a --interactive
```

## インタラクティブモード

`--interactive` (`-I`) を指定するとインタラクティブモードに入る。入力は親 stdin から読むため、`--out` (judge は常に batch) やファイル指定の `--in <path>` とは併用できない (引数エラー)。`--in` / `--in -` の有無はインタラクティブ判定に影響しない (どちらも batch 用の指定)。入力ソースによって 2 通りの挙動になる。

### TTY 入力 (端末から直接): **chat TUI**

bubbletea ベースの簡易チャット UI を起動する。

- 画面下部の入力ボックスに 1 行入力 → `Enter` で子プロセスに 1 行送信、scrollback に `→ <input>` が追加される
- 子プロセスの出力は届き次第 `← <output>` として scrollback に追加される (改行単位、live)
- `↑` / `↓` で入力履歴を辿れる (セッション中のみ)
- `Ctrl+D`: 子の stdin を閉じる (EOF 通知)。子が `input()` を呼んで終了することがある
- `Ctrl+C`: 子を kill して TUI 終了

子プロセスは `PYTHONUNBUFFERED=1` を付けて起動するので、`sys.stdout.flush()` を呼ばなくても各 `print()` が即座に届く。

子が exit すると TUI は `(child process exited; press any key to close)` を表示する。任意のキーで TUI を抜けると、`OK` / `RE` ステータスと経過時間が画面に残る。

```sh
# インタラクティブ問題を chat UI で解く
atcoder run abc999 --task a --interactive
```

### 非TTY 入力 (パイプ / リダイレクト): **passthrough + tee**

CI やスクリプトから応答を仕込みたいときの batch-friendly モード。

- 子の stdout / stderr を親 fd に直結 (live streaming)
- stdin は `io.TeeReader` で経由させ、各行を `> <input>` と echo してから子に転送 — スクリプト経由でも「何が送られたか」が見える
- TUI は使わない (キーボード入力ループが成立しないため)

```sh
printf "3\nok\nok\nok\n" | atcoder run abc999 --task a --interactive
```

> 注意: 非TTY での入出力 interleave は厳密には保証されない。pipe バッファ (~64KB) より小さい入力は子の読み込みより先にすべて echo され、その後に解答の出力が現れる。**真にチャットらしい交互表示が必要なら TTY (chat UI)** を使うか、`expect`(1) 等の外部ツールで応答を協調させる。

### batch モード (`--interactive` 無し: デフォルト)

`--interactive` を付けない限りこちらがデフォルト。親の stdin (`--in` 省略 / `--in -`) またはファイル (`--in <path>`) を read-all してから子に渡し、出力をキャプチャしてから `output:` セクションに表示する。リダイレクトやパイプで「全入力を先に決めて流す」一括処理や、`--out` での judge に適する。

## test との比較

| | `atcoder test` | `atcoder run` |
|---|---|---|
| 入力 | `<task>/tests/NN.in` (複数) | `--in` / pipe (単一) |
| 期待出力 | `<task>/tests/NN.out` と突合 | 突合せ無し |
| 判定 | PASS / FAIL / TLE / RE | OK / TLE / RE |
| AtCoder fetch | 必要に応じて自動 | 行わない |

## 関連

- 仕様 (test): [001-exercise-test.md](./requirements/001-exercise-test.md)
- 利用 (test): [atcoder-test-usage.md](./atcoder-test-usage.md)
- アーキテクチャ: [atcoder-test-architecture.md](./atcoder-test-architecture.md)
- テスト戦略: [atcoder-test-testing.md](./atcoder-test-testing.md)
- コミット: [atcoder-commit-usage.md](./atcoder-commit-usage.md)
