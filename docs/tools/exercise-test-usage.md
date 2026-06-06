# `exercise test` 利用手引

`exercise` ツールの `test` サブコマンドの使い方をまとめる。

仕様の詳細は [exercise-test-requirements.md](./exercise-test-requirements.md) を参照。

## 前提

- リポジトリルートで操作することを想定する。
- Python の実行には `<repo_root>/.venv/bin/python` を使う。Poetry で `.venv` を作成済みであること。

```sh
poetry install        # 初回のみ
```

- ツール本体は Go 製。実行は `go run ./cmd/exercise` または事前ビルド (`go build -o exercise ./cmd/exercise`)。

## クイックスタート

ABC325 の問題 D を当日の演習として書いたあとに、サンプルケースでテストする。

```sh
# 1. 当日の演習ディレクトリを用意 (まだ無ければ)
go run ./cmd/exercise new

# 2. 解答を exercise/YYYY/MM/DD/abc325_d.py として書く

# 3. テストを実行
go run ./cmd/exercise test abc325 --task abc325_d
```

初回実行時に AtCoder の問題ページからサンプル入出力と Time Limit を取得し、以下に保存する。

```
exercise/YYYY/MM/DD/
  abc325_d.py
  abc325_d/
    meta.toml
    tests/
      01.in
      01.out
      02.in
      02.out
```

2 回目以降は保存済みのテストを使うため、ネットワークアクセスは発生しない。

## コマンド

```
exercise test <contest> --task <task> [-v] [-d] [--case <N[,M,...]>] [--refresh] [--timeout <dur>]
```

### 引数

| 引数 | 必須 | 説明 |
|---|---|---|
| `<contest>` | ✔ | AtCoder のコンテスト ID (例: `abc325`)。URL の `/contests/<contest>/` に対応 |
| `--task <task>` | ✔ | AtCoder のタスク ID (例: `abc325_d`)。URL の `/tasks/<task>` に対応。**短縮形**: `_` を含まない値は `<contest>_<task>` に自動展開 (例: `--task d` + `<contest>=abc325` → `abc325_d`) |
| `-v` / `--verbose` | | 各ケースで入力 (`input:`) と実際の出力 (`output:`) を表示 |
| `-d` / `--debug` | | 子プロセスに `DEBUG=1` を渡し、stdout のうち `[DEBUG]` で始まる行を比較対象から除外。除外行は `debug:` セクションに表示 |
| `--case <N>` | | 指定したケース番号のみ実行。カンマ区切りで複数可 (`--case 1,3`)。数値は `01`, `03` のように 2 桁ゼロ埋めへ正規化。該当無しはエラー終了 |
| `--refresh` | | テストキャッシュを無視して AtCoder から再取得 |
| `--timeout <dur>` | | 1 ケースあたりの実行制限時間を上書き。Go の duration 記法 (例: `5s`, `500ms`)。未指定なら `meta.toml.time_limit_ms` の値を使う |

### 解答ファイルの特定

ツールは **当日 (ローカル時刻) の `exercise/YYYY/MM/DD/<task>.py`** を解答ファイルとして使う。指定された日付の解答だけをテストする想定であり、過去日の解答は (現時点では) テストできない。

## 動作

1. `exercise/YYYY/MM/DD/<task>.py` の存在を確認 (無ければエラー)。
2. `exercise/YYYY/MM/DD/<task>/tests/` を確認:
   - 存在し `--refresh` も無ければそれを使う。
   - 無ければ AtCoder からサンプル入出力と Time Limit を取得して保存。
3. 各サンプルケースに対して `<repo_root>/.venv/bin/python <task>.py < NN.in` を実行。
4. 標準出力を `NN.out` と比較し、結果をケースごとに表示。

## 判定種別

| ラベル | 意味 |
|---|---|
| `PASS` | 期待出力と一致 (末尾改行の差は無視) |
| `FAIL` | 期待出力と一致しない |
| `TLE` | 制限時間 (デフォルトは `meta.toml.time_limit_ms`、`--timeout` で上書き可) を超過 |
| `RE` | Python プロセスが非ゼロ終了 |

## 出力例

```
abc325_d  contest=abc325  time_limit=2000ms  tests=3

[01] PASS  12 ms
[02] FAIL  18 ms
       expected:
         3
         1 2 3
       got:
         3
         1 3 2
       diff:
         - 1 2 3
         + 1 3 2
[03] PASS  10 ms

Result: 2/3 PASS
```

### exit code

| code | 意味 |
|---|---|
| `0` | 全ケース PASS |
| `1` | 実行できたが 1 ケース以上 FAIL/TLE/RE、または実行時エラー |
| `2` | 引数エラー (`--task` 未指定など) |

## ユースケース別の使い方

### 通常の演習チェック

```sh
# 短縮形 (ABC 系は contest + task で abcXXX 部分が重複するので便利)
go run ./cmd/exercise test abc325 --task d

# 等価。フル ID で書いてもよい
go run ./cmd/exercise test abc325 --task abc325_d
```

ADT のように contest ID と task ID が独立しているケースは、フル ID (`--task abc325_d` 等) で指定する。

### サンプルケースを最新化したい

問題ページが訂正されたり、自分で `tests/` を壊してしまったときに使う。

```sh
go run ./cmd/exercise test abc325 --task abc325_d --refresh
```

### 解答コードを修正してリトライ

`tests/` はキャッシュされているので 2 回目以降のテストは高速。

```sh
# 解答を編集して保存後
go run ./cmd/exercise test abc325 --task abc325_d
```

### 解答コードにデバッグ出力を仕込みたい

`-d` 指定で子プロセスに `DEBUG=1` が渡る。Python 側で `os.environ.get("DEBUG")` を分岐すれば、デバッグ実行時のみログを出せる。出力行のうち先頭が `[DEBUG]` のものは比較対象から自動除外される。

```python
import os
DEBUG = bool(os.environ.get("DEBUG"))
def dprint(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

N = int(input())
dprint("N =", N)        # `-d` 時のみ [DEBUG] N = ... が出る
# ...
print(answer)
```

```sh
# 通常実行: DEBUG 未設定、デバッグ出力なし、判定通り
go run ./cmd/exercise test abc325 --task d

# デバッグ実行: [DEBUG] 行を debug: セクションで確認しつつ判定もそのまま
go run ./cmd/exercise test abc325 --task d -d

# 入力・出力もまとめて見たい
go run ./cmd/exercise test abc325 --task d -d -v
```

### 制限時間を上書きしたい

問題ページの制限時間を超えても挙動を見たい / より厳しい制限で TLE をローカル検出したい、などのケース:

```sh
# AtCoder の値を無視して 5 秒で TLE 判定
go run ./cmd/exercise test abc325 --task abc325_d --timeout 5s

# 自前の高速性検証で 200ms 以内に収まるか確認
go run ./cmd/exercise test abc325 --task abc325_d --timeout 200ms
```

## トラブルシューティング

### `解答ファイルが見つかりません: exercise/YYYY/MM/DD/<task>.py`

- 当日の日付ディレクトリに `<task>.py` を作成しているか確認する。
- 日付ディレクトリが無い場合は `go run ./cmd/exercise new` で作成する。
- 過去日の解答をテストしたいユースケースは現時点では未対応。

### `AtCoder から取得できませんでした (HTTP 4xx)`

- `<contest>` と `<task>` の綴りを確認する (例: `abc325` / `abc325_d`)。
- 一部の限定公開コンテストは未対応 (公開サンプルがある問題のみ対象)。

### サンプルの抽出に失敗

- AtCoder の HTML 構造が変わった可能性。`--refresh` でリトライしても直らなければ実装側で対応が必要。
- 一時しのぎとして `<task>/tests/NN.in` `NN.out` を手で書いてもテスト自体は通る。

### `python が見つかりません`

- `<repo_root>/.venv/bin/python` の存在を確認 (`poetry install`)。
- `.venv` を作りたくない環境では、`PATH` 上に `python` を通しておけばフォールバックされる。

### `TLE` が頻発する

- 解答自体の計算量を見直す。
- `meta.toml` の `time_limit_ms` が問題ページから誤って小さく取得された疑いがあれば、`--refresh` を試す、または手で書き換える。

## 制約事項 (現時点)

- 対応言語は Python のみ。
- 対象ディレクトリは `exercise/YYYY/MM/DD/` 配下のみ (`abc/`, `arc/`, `adt/`, `dp/` などは未対応)。
- 解答ファイルは当日のディレクトリにあるものに限る。
- 認証が必要な限定公開コンテストは未対応。

## 関連

- 要件定義: [exercise-test-requirements.md](./exercise-test-requirements.md)
- アーキテクチャ: [exercise-test-architecture.md](./exercise-test-architecture.md)
- テスト戦略: [exercise-test-testing.md](./exercise-test-testing.md)
- ad-hoc 実行コマンド: [exercise-run-usage.md](./exercise-run-usage.md)
- ツール本体: [`cmd/exercise/main.go`](../../cmd/exercise/main.go)
