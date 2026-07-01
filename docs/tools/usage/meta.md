# `atcoder meta` 利用手引

`atcoder meta` は、サンプル入出力と Time Limit を保持するキャッシュ
(`$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/`) を、**問題ページの URL を貼るだけ**で
用意・点検・補正するためのサブコマンドです (要件 [046](../requirements/046-meta-command.md))。

- `fetch` — task URL (または contest + `--task`) を渡してサンプル + Time Limit をダウンロードする。
- `show` — キャッシュ済みメタの内容を表示する。
- `set` — キャッシュ済みメタのフィールド (現状 Time Limit) を手で上書きする。

judge は行いません (それは [`atcoder test`](test.md))。`meta` はキャッシュ層だけを
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
# 取得元 URL を手で設定（task_id が contest と食い違う問題用）
atcoder meta set abc111 --task d --url https://atcoder.jp/contests/abc111/tasks/arc103_b

# Time Limit を手で 5 秒に上書き
atcoder meta set abc457 --task d --time-limit 5s
```

`meta.toml` の指定フィールドを上書きして保存します。

| フラグ | 説明 |
|---|---|
| `--url <url>` | **取得元 URL の override**。下記「URL が contest と食い違う問題」を参照。AtCoder の URL のみ。スロット未キャッシュでも記録可 |
| `--time-limit <dur>` | Time Limit を上書き (`5s` / `1500ms` 等)。`> 0` のみ許容。`time_limit_ms` に変換して保存。キャッシュ済みが前提 |

- フィールド指定 (`--url` / `--time-limit`) が 1 つも無ければフラグ誤り (exit 2)。
- `--time-limit` のみの上書きは未キャッシュなら exit 1 (先に `fetch` してください)。
- 指定したフィールドだけ上書きし、他のフィールドは保持します。

```console
$ atcoder meta set abc457 --task d --time-limit 5s
updated abc457_d
  time limit:  2000 ms -> 5000 ms
```

### URL が contest と食い違う問題（例: abc111 の D = arc103_b）

ABC のいくつかの問題は、コンテストページの URL とタスク ID の接頭辞が一致しません。
たとえば **abc111 の D 問題**のページは
`https://atcoder.jp/contests/abc111/tasks/arc103_b` で、タスク ID は `arc103_b` です。
この場合、既定の取得は `.../tasks/abc111_d` を組み立てて **404** になります。

**多くの場合これは自動で解決されます** (要件 065): `test` / `gen` / `meta fetch` は機械生成 URL が
404 になると、**タスク一覧ページ (`/contests/<contest>/tasks`) から該当 letter の実 task_id
(`arc103_b`) を引いて取得し直し**、解決できた URL をこのスロットの `url` に記録します。以降は
その URL で直行するので、`meta set --url` を手打ちしなくても `atcoder test abc111 --task d` が
そのまま通ります。

`set --url` は、この自動フォールバックが効かないとき (letter が単一英小文字でない・一覧ページ
から辿れない等) や、取得元を明示的に固定したいときの手段です。スロット `abc111/d`（= キャッシュ
キー `abc111_d`、解答ファイル `abc111_d.py` / `abc/111/d.py`）に正しい URL を記録すれば、
**スロットはそのまま**で取得元だけ差し替えられます。記録した URL は `meta fetch` だけでなく
`test` / `start` の取得経路でも尊重されます (override があるときは自動フォールバックしません)。

```console
$ atcoder meta set abc111 --task d --url https://atcoder.jp/contests/abc111/tasks/arc103_b
updated abc111_d
  url:         (none) -> https://atcoder.jp/contests/abc111/tasks/arc103_b

# 以降はこのスロットの取得がすべて arc103_b のページを引く
$ atcoder meta fetch abc111 --task d      # または atcoder test abc111 --task d
fetched abc111_d
  url:         https://atcoder.jp/contests/abc111/tasks/arc103_b
  time limit:  2000 ms
  samples:     4
  cached at:   /Users/you/.cache/atcoder-tools/abc111/abc111_d
```

`set --url` はスロット未キャッシュでも記録できます（空の `meta.toml` を作って URL だけ書き、
取得は後続の `fetch` / `test` に任せる）。記録後・取得前の `show` では `fetched at` が
`(not fetched yet)` と表示されます。

## chat 内からの編集 (`:meta`)

インタラクティブ chat (`test --interactive` / `start` 分割画面の下ペイン) では、command モード
(`Esc` → `:`) の **`:meta`** で `show`/`set` 相当を chat を抜けずに行えます。`:meta` で url /
time limit / samples を表示、`:meta url <url>` で URL override、`:meta time_limit 5s` で Time Limit
を上書きします。編集対象・検証規則・未キャッシュ時の扱いは本コマンドの `set` と同一です
(要件 [055](../requirements/055-chat-meta-edit.md))。さらに **`:meta fetch`** で本コマンドの `fetch`
相当 (url からサンプル + Time Limit を再取得) を chat 内から実行できます。`:meta url <url>` で
取得元を直した後に `:meta fetch` と続ければ、新しい url の問題内容へ差し替えられます
(取得は非同期。要件 [057](../requirements/057-chat-meta-fetch.md))。詳細は
[docs/tools/usage/test.md](test.md) / [docs/tools/usage/start.md](start.md)
の command モードのコマンド表を参照してください。

## exit code

| code | 意味 |
|---|---|
| 0 | 成功 |
| 1 | 実行時失敗 (fetch 失敗 / 未キャッシュ) |
| 2 | 引数・フラグ誤り (サブコマンド無し・未知サブコマンド・ターゲット未指定・URL 解釈不可・`--task` 欠落・`set` のフィールド無し・`--time-limit` の duration 不正・`--url` が AtCoder の URL でない) |

## 制約事項 (現時点)

- `set` で上書きできるのは取得元 URL (`--url`) と Time Limit (`--time-limit`)。その他のフィールドは未対応 (要件 046 の将来拡張)。
- `fetch` はネットワークに触れるため、fixture スモークテスト (`fixtures/run.sh`) では `show`/`set` (url override の記録を含む) と
  引数誤りのみを固定し、`fetch` 本体は回しません。

## 関連

- 要件定義: [046-meta-command.md](../requirements/046-meta-command.md)
- chat からの編集 (`:meta`): [055-chat-meta-edit.md](../requirements/055-chat-meta-edit.md)
- chat からの再取得 (`:meta fetch`): [057-chat-meta-fetch.md](../requirements/057-chat-meta-fetch.md)
- サンプル取得・キャッシュの元仕様: [001-exercise-test.md](../requirements/001-exercise-test.md)
- テスト実行: [docs/tools/usage/test.md](test.md)
- アーキテクチャ: [atcoder-test-architecture.md](../atcoder-test-architecture.md)
- ツール本体: [`cmd/atcoder/meta.go`](../../../cmd/atcoder/meta.go)
