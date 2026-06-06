# `exercise test` コマンド 要件定義

## 概要

`cmd/exercise/` ツールに追加する `test` サブコマンドの要件を定義する。AtCoder の問題に対する Python 解答を、公開サンプル入出力でローカル検証するための CLI である。

## 背景・目的

- 日々の演習 (`exercise/YYYY/MM/DD/<task>.py`) で書いた解答を、AtCoder の公開サンプルケースに対してローカルで素早く検証したい。
- サンプル入出力を毎回手でコピー & ペーストするのは煩雑かつ間違いやすいため、AtCoder からの自動取得とキャッシュを行いたい。
- AtCoder の Time Limit を遵守したタイムアウト判定で、無限ループや TLE を早期に検出したい。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 言語 | Python のみ | Go, C++ 等 |
| 対象ディレクトリ | `exercise/YYYY/MM/DD/` 配下 | `abc/`, `arc/`, `adt/`, `dp/` など |
| 取得元 | AtCoder の問題ページ | online-judge-tools への切替 |

## ディレクトリ構造

解答ファイルと同階層に、同名サフィックス無しのディレクトリを置き、その配下にメタ情報とテストケースを保存する。

```
exercise/YYYY/MM/DD/
  abc325_d.py            # 解答コード (ユーザが書く)
  abc325_d/              # 問題コンテキスト (ツールが管理)
    meta.toml            # contest, task, time_limit_ms, url など
    tests/
      01.in              # サンプル入力 1
      01.out             # サンプル出力 1
      02.in
      02.out
      ...
```

### 命名規約

| 種別 | 規約 |
|---|---|
| 解答ファイル | `<task>.py` (例: `abc325_d.py`) |
| 問題コンテキスト ディレクトリ | `<task>/` (解答ファイルのベース名と一致) |
| メタファイル | `<task>/meta.toml` |
| サンプル入力 | `<task>/tests/NN.in` (NN は 2 桁ゼロ埋め、01 始まり) |
| サンプル出力 | `<task>/tests/NN.out` |

### `meta.toml` のスキーマ

```toml
contest        = "abc325"                                       # AtCoder のコンテスト ID
task           = "abc325_d"                                     # AtCoder のタスク ID
url            = "https://atcoder.jp/contests/abc325/tasks/abc325_d"
time_limit_ms  = 2000                                           # 問題ページから取得した制限時間 (ms)
fetched_at     = "2026-06-06T12:34:56+09:00"                    # 最終取得日時 (ISO 8601)
```

## CLI 仕様

```
exercise test <contest> --task <task> [--refresh] [--timeout <dur>]
```

| 引数 / フラグ | 必須 | 説明 |
|---|---|---|
| `<contest>` | ✔ | AtCoder のコンテスト ID (例: `abc325`)。URL の `/contests/<contest>/` 部分に対応 |
| `--task <task>` | ✔ | AtCoder のタスク ID (例: `abc325_d`)。URL の `/tasks/<task>` 部分に対応。`_` を含まない短縮形 (例: `d`) を渡した場合は `<contest>_<task>` に自動展開する |
| `-v` / `--verbose` | | 各ケースについて、入力 (`<task>/tests/NN.in` の中身) と解答の標準出力を追加表示する |
| `--refresh` | | テストキャッシュを無視して AtCoder から再取得する |
| `--timeout <dur>` | | 1 ケースあたりの制限時間を上書き (Go の `time.ParseDuration` 記法: `5s`, `500ms` 等)。未指定なら `meta.toml.time_limit_ms` を使う。`meta.toml` への永続化はしない |

省略時の動作:
- `--task` 未指定 → エラー (exit code 2 相当)。

## 動作仕様

1. **解答ファイルの特定**
   - 当日 (ローカル時刻) の `exercise/YYYY/MM/DD/<task>.py` をテスト対象とする。
   - 存在しなければエラー終了。
2. **テストキャッシュの確認**
   - `exercise/YYYY/MM/DD/<task>/tests/` が存在し、`--refresh` が指定されていなければそのまま使用する。
   - そうでない場合は AtCoder の問題ページ `https://atcoder.jp/contests/<contest>/tasks/<task>` を HTTP GET する。
3. **問題ページのパース**
   - レスポンスを `xmlquery` で HTML としてパースする。
   - 日本語版 (`lang-ja` クラスを持つセクション) を優先採用し、英語版との重複は排除する。
   - 抽出するもの:
     - サンプル入力 / 出力のペア (順序を保持)
     - Time Limit (例: "実行時間制限: 2 sec" を ms に換算)
4. **保存**
   - `exercise/YYYY/MM/DD/<task>/meta.toml` にメタ情報を書き出す。
   - `exercise/YYYY/MM/DD/<task>/tests/NN.in` `NN.out` を書き出す (`NN` は 01 始まりのゼロ埋め)。
5. **解答の実行**
   - 各テストケース `NN.in` を標準入力として `<repo_root>/.venv/bin/python <task>.py` を起動する。
   - `.venv/bin/python` が存在しない場合は `PATH` 上の `python` にフォールバックする。
   - タイムアウトは `--timeout` 指定があればその値、無ければ `meta.toml.time_limit_ms` を使う。
   - 実行時間を計測 (壁時計、ms 単位) する。
6. **判定**
   - 解答の標準出力を `NN.out` と比較する (完全一致、末尾改行は無視)。
   - タイムアウト超過は `TLE`。
   - Python 自体の異常終了は `RE` (Runtime Error)。
7. **結果表示**
   - 各ケースについて 1 行で `PASS`/`FAIL`/`TLE`/`RE` + 経過時間を表示する。
   - `FAIL` のケースには続けて `expected` と `got` の diff を表示する。
   - 全ケース PASS でも 1 行ずつ表示する (静かにしない方針)。
8. **exit code**
   - 全 PASS で `0`。
   - 1 ケースでも PASS 以外があれば `1`。
   - 引数エラーは `2` (要件外の異常は適宜 `1` か `2`)。

## 出力フォーマット (リファレンス)

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

## 技術仕様

| 項目 | 内容 |
|---|---|
| 実装言語 | Go (`cmd/exercise/main.go` に統合) |
| HTTP クライアント | 標準ライブラリ (`net/http`) |
| HTML パース | `github.com/antchfx/htmlquery` (xpath ベース、HTML5 lenient parser) |
| TOML | `github.com/BurntSushi/toml` |
| Python 実行 | `<repo_root>/.venv/bin/python` → フォールバック `python` |
| タイムアウト | `context.WithTimeout` + `exec.CommandContext` |
| 比較 | バイト列比較。末尾の `\n` を剥がしてから比較 |

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| 解答ファイル不在 | エラーメッセージを表示して exit 1 |
| AtCoder への HTTP 失敗 | URL と HTTP ステータスを表示して exit 1 |
| HTML パース失敗 / サンプルが見つからない | エラーメッセージを表示して exit 1 |
| `.venv` も `python` も無い | エラーメッセージを表示して exit 1 |
| 部分的に失敗したケースあり | 全ケース実行は試みた上で exit 1 |

## 非機能要件

- 単一のローカルユーザによる利用を前提とし、並列実行や排他制御は不要。
- AtCoder への HTTP リクエストは `--refresh` 時のみ発生する想定。短時間に連打しないユースケース。
- 認証は不要 (公開コンテストのサンプルのみを対象とする)。

## 将来の拡張ポイント

- 対象ディレクトリの拡張: `abc/`, `arc/`, `adt/`, `dp/` などへ広げる。`adt/` のように contest と task が独立するケースは `meta.toml` の `contest` が真の値を保持する。
- 言語サポート: 拡張子から実行コマンドを自動選択する仕組み。
- `--task` 省略時の挙動: コンテスト全タスクの一括テスト。
- 並列実行: ケースを並列に走らせて短縮。

## 用語

- **contest**: AtCoder の URL `/contests/<contest>/` に現れる ID (例: `abc325`)。
- **task**: AtCoder の URL `/tasks/<task>` に現れる ID (例: `abc325_d`)。多くの ABC では `<contest>_<letter>` 形式だが、ADT のように独立したものもある。
