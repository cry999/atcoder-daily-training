# `atcoder meta` 利用手引

`atcoder meta` は、サンプル入出力と Time Limit を保持するキャッシュ
(`$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/`) を、**問題ページの URL を貼るだけ**で
用意・点検・補正するためのサブコマンドです (要件 [046](requirements/046-meta-command.md))。

- `fetch` — task URL (または contest + `--task`) を渡してサンプル + Time Limit をダウンロードする。
- `show` — キャッシュ済みメタの内容を表示する。
- `set` — キャッシュ済みメタのフィールド (現状 Time Limit) を手で上書きする。

judge は行いません (それは [`atcoder test`](atcoder-test-usage.md))。`meta` はキャッシュ層だけを
操作し、解答ファイルや `tests-extra/` (ユーザ追加ケース) には一切触れません。

## ターゲット指定 (3 サブコマンド共通)

対象タスクは次のどちらかで指定します。

| 指定方法 | 例 |
|---|---|
| **task URL を位置引数で** (`--task` 不要) | `atcoder meta fetch https://atcoder.jp/contests/abc457/tasks/abc457_d` |
| **contest + `--task`** (`test` と同じ短縮形) | `atcoder meta fetch abc457 --task d` |

- URL は `https://` / `http://` / スキーム省略 (`atcoder.jp/...`) を許容し、`?lang=ja` 等の
  クエリやフラグメントが付いていても構いません。
- URL とみなした位置引数から `/contests/<contest>/tasks/<task>` を取り出せなければフラグ誤り (exit 2)。
- `--task` の短縮形は `d` → `<contest>_d` に展開します (`test` と同規約)。

## `atcoder meta fetch`

```sh
# URL を直接貼ってダウンロード
atcoder meta fetch https://atcoder.jp/contests/abc457/tasks/abc457_d

# contest + task でも可
atcoder meta fetch abc457 --task d
```

AtCoder からサンプル入出力と Time Limit を取得し、`meta.toml` + `tests/NN.in|out` を
キャッシュに書き込みます。`test --refresh` と同じ**強制再取得**で、既存キャッシュは
上書きします (`tests-extra/` には触れません)。解答ファイルの有無は問いません。

```console
$ atcoder meta fetch https://atcoder.jp/contests/abc457/tasks/abc457_d
Fetching abc457/abc457_d from AtCoder...
fetched abc457_d
  url:         https://atcoder.jp/contests/abc457/tasks/abc457_d
  time limit:  2000 ms
  samples:     3
  cached at:   /Users/you/.cache/atcoder-tools/abc457/abc457_d
```

ここで温めたキャッシュは、その後の `atcoder test abc457 --task d` / `atcoder start` が
そのまま再利用します (キャッシュキー・スキーマは共通)。

## `atcoder meta show`

```sh
atcoder meta show abc457 --task d
atcoder meta show https://atcoder.jp/contests/abc457/tasks/abc457_d
```

キャッシュ済み `meta.toml` を読んで表示します (fetch はしません)。未キャッシュなら
exit 1 で「先に `fetch` せよ」と案内します。

```console
$ atcoder meta show abc457 --task d
abc457_d
  url:         https://atcoder.jp/contests/abc457/tasks/abc457_d
  time limit:  2000 ms
  samples:     3
  fetched at:  2026-06-24T12:00:00+09:00
```

## `atcoder meta set`

```sh
# Time Limit を手で 5 秒に上書き
atcoder meta set abc457 --task d --time-limit 5s
```

キャッシュ済み `meta.toml` の指定フィールドを上書きして保存します。AtCoder の HTML 変更
などで Time Limit が取れなかった / ずれたときの補正に使います。

| フラグ | 説明 |
|---|---|
| `--time-limit <dur>` | Time Limit を上書き (`5s` / `1500ms` 等)。`> 0` のみ許容。`time_limit_ms` に変換して保存 |

- フィールド指定が 1 つも無ければフラグ誤り (exit 2)。
- 未キャッシュなら exit 1 (先に `fetch` してください)。
- 指定したフィールドだけ上書きし、他のフィールド (`url` / `fetched_at` / サンプル) は保持します。

```console
$ atcoder meta set abc457 --task d --time-limit 5s
updated abc457_d
  time limit:  2000 ms -> 5000 ms
```

## exit code

| code | 意味 |
|---|---|
| 0 | 成功 |
| 1 | 実行時失敗 (fetch 失敗 / 未キャッシュ) |
| 2 | 引数・フラグ誤り (サブコマンド無し・未知サブコマンド・ターゲット未指定・URL 解釈不可・`--task` 欠落・`set` のフィールド無し / duration 不正) |

## 制約事項 (現時点)

- `set` で上書きできるのは Time Limit (`--time-limit`) のみ。`url` 等の他フィールドは未対応 (要件 046 の将来拡張)。
- `fetch` はネットワークに触れるため、fixture スモークテスト (`fixtures/run.sh`) では `show`/`set` と
  引数誤りのみを固定し、`fetch` 本体は回しません。

## 関連

- 要件定義: [046-meta-command.md](./requirements/046-meta-command.md)
- サンプル取得・キャッシュの元仕様: [001-exercise-test.md](./requirements/001-exercise-test.md)
- テスト実行: [atcoder-test-usage.md](./atcoder-test-usage.md)
- アーキテクチャ: [atcoder-test-architecture.md](./atcoder-test-architecture.md)
- ツール本体: [`cmd/atcoder/meta.go`](../../cmd/atcoder/meta.go)
