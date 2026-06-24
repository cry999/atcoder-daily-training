# `atcoder meta` コマンド (task URL 直指定の DL / 表示 / 編集) 要件定義

## 概要

task URL (例: `https://atcoder.jp/contests/abc457/tasks/abc457_d`) を 1 引数で渡すだけで、その問題のサンプル入出力と Time Limit をキャッシュへダウンロードできるようにする。あわせて、キャッシュ済みメタ (`meta.toml`) の内容を確認 (`show`) し、特定フィールド (Time Limit) を手で上書き (`set`) できる `atcoder meta` サブコマンドを新設する。

## 背景・目的

現状、サンプルのダウンロードは `atcoder test <contest> --task <task>` に従属しており、

- 解答ファイル (`exercise/.../<task>.py` 等) が存在しないと `test` は走らず、ダウンロードもされない。
- contest ID と task ID を `--task` の短縮形ルールに合わせて分けて渡す必要がある。問題ページの URL をそのまま貼れない。
- キャッシュした Time Limit が AtCoder の HTML 変更等で取れなかった/ずれた場合に、手で直す経路がない (`meta.toml` を直接編集するしかない)。

「問題ページの URL をコピペ → データだけ先に落とす」「キャッシュの中身を見る」「Time Limit を手で直す」を 1 コマンドで賄えるようにし、`test`/`start` のサンプル取得経路 (`testexec.EnsureTests` / `fetchProblem`) を再利用する。

## スコープ

| 区分 | 内容 |
|---|---|
| 当面のスコープ | `atcoder meta fetch <url\|contest --task>` (DL)、`atcoder meta show <url\|contest --task>` (表示)、`atcoder meta set <url\|contest --task> [--url <url>] [--time-limit <dur>]` (URL override / Time Limit 上書き) |
| 当面のスコープ | task URL のパース (`https://atcoder.jp/contests/<contest>/tasks/<task>` → contest_id / task_id)。`http`/`https`/スキームなし (`atcoder.jp/...`) を許容 |
| 当面のスコープ | **URL override**: `set --url <url>` で解答スロット (contest/task) に取得元 URL を記録し、`fetch`/`test`/`start` の取得経路 (`ensureTests`) がそれを尊重する。task_id が contest と食い違う問題 (例: abc111 の D = `arc103_b`) を、スロットを保ったまま正しいページから取得するため |
| 当面のスコープ | `fetch` は既存 `testexec.EnsureTests(..., refresh=true)` を呼ぶ強制再取得。キャッシュのみを書き換え、解答ファイルには一切触れない |
| 将来の拡張余地 | `set` の対象フィールド拡張 (canonical url 以外)、`meta` を介したコンテスト一括 fetch、`meta path` (キャッシュパス表示)、JSON 出力 |
| 境界 (他項目との分担) | judge は行わない (それは `test`)。解答スケルトン生成も行わない (それは `new`)。`meta` はキャッシュ層 (`~/.cache/atcoder-tools/<contest>/<task>/`) の準備・点検・補正に専念する |

## ディレクトリ構造 / キャッシュ

`meta` が読み書きするのは既存のキャッシュ階層 (新規ディレクトリは作らない):

```
$XDG_CACHE_HOME/atcoder-tools/<contest>/<task>/
  meta.toml          # contest / task / url / time_limit_ms / fetched_at
  tests/
    01.in  01.out
    02.in  02.out
    ...
```

`meta.toml` スキーマ (既存 `internal/testexec/meta.go` の構造体。変更なし):

| フィールド | 型 | 説明 |
|---|---|---|
| `contest` | string | contest_id (例 `abc457`) |
| `task` | string | task_id (例 `abc457_d`) |
| `url` | string | 問題ページ URL。`fetch` が記録するほか、`set --url` で override 可。取得経路 (`ensureTests`) は空でなければこの url を優先する |
| `time_limit_ms` | int | Time Limit (ミリ秒)。`set --time-limit` の上書き対象 |
| `fetched_at` | time | 取得時刻 |

## CLI 仕様

### 共通: ターゲット指定 (URL or contest + --task)

3 サブコマンド共通で、対象タスクを次のどちらかで指定する:

1. **task URL を位置引数で**: `https://atcoder.jp/contests/<contest>/tasks/<task>` を渡すと、URL から contest_id と task_id を抽出する (`--task` 不要)。スキームは `https://` / `http://` / 省略 (`atcoder.jp/...`) を許容。
2. **contest + `--task`** (既存 `test` と同じ): 位置引数に contest_id、`--task` に task_id または短縮形 (`d` → `<contest>_d`)。

URL とみなす判定: 位置引数が `://` を含むか `atcoder.jp/` を含む。URL なのに `/contests/.../tasks/...` を取り出せなければフラグ誤り (exit 2)。

### `atcoder meta fetch <url | contest --task <task>>`

サンプルと Time Limit を AtCoder から取得し、`meta.toml` + `tests/` をキャッシュへ書き込む。`test --refresh` と同じ強制再取得 (既存キャッシュは上書き)。解答ファイルの有無は問わない。

処理ステップ:

1. ターゲット指定をパースして contest_id / task_id を得る。
2. `testexec.EnsureTests(reporter, contest, task, refresh=true)` を呼ぶ (内部で `fetchProblem` → `tests/NN.in|out` + `meta.toml` 保存)。
3. 取得結果サマリ (URL / Time Limit / サンプル数 / 保存先) を表示する。

### `atcoder meta show <url | contest --task <task>>`

キャッシュ済み `meta.toml` を読み、内容を表示する。fetch はしない (未キャッシュならエラー)。

### `atcoder meta set <url | contest --task <task>> [--url <url>] [--time-limit <dur>]`

`meta.toml` の指定フィールドを上書きして保存する。フィールド指定が 1 つも無ければフラグ誤り (exit 2)。

- `--url <url>`: 取得元 URL の override。task_id が contest と食い違う問題 (例: abc111 の D = `arc103_b`) で、解答スロット (contest/task = `abc111_d`) を保ったまま正しいページを指す。値は AtCoder の URL (`atcoder.jp/...` か `://` を含む) でなければフラグ誤り (exit 2)。**スロット未キャッシュでも記録できる** — 空の `meta.toml` を作って url だけ書き、後続の `fetch`/`test` がそれを使って取得する。
- `--time-limit <dur>`: `5s` / `500ms` 等の duration を `time_limit_ms` に変換して書き込む。`> 0` のみ許容。こちらはキャッシュ済みが前提 (未キャッシュならエラー、先に `fetch` せよ)。

### フラグ表

| フラグ | 対象サブコマンド | 説明 |
|---|---|---|
| `--task <task>` | fetch / show / set | task_id または短縮形。位置引数が URL のときは不要 (指定されても URL 優先で無視) |
| `--url <url>` | set | 取得元 URL の override (上記)。AtCoder の URL のみ。スロット未キャッシュでも記録可 |
| `--time-limit <dur>` | set | 上書きする Time Limit (`5s` / `1500ms` 等)。`> 0` のみ許容。キャッシュ済みが前提 |

### 出力イメージ

```console
$ atcoder meta fetch https://atcoder.jp/contests/abc457/tasks/abc457_d
Fetching abc457/abc457_d from AtCoder...
fetched abc457_d
  url:         https://atcoder.jp/contests/abc457/tasks/abc457_d
  time limit:  2000 ms
  samples:     3
  cached at:   ~/.cache/atcoder-tools/abc457/abc457_d

$ atcoder meta show abc457 --task d
abc457_d
  url:         https://atcoder.jp/contests/abc457/tasks/abc457_d
  time limit:  2000 ms
  samples:     3
  fetched at:  2026-06-24T12:00:00+09:00

$ atcoder meta set abc457 --task d --time-limit 5s
updated abc457_d
  time limit:  2000 ms -> 5000 ms

# task_id が contest と食い違う問題 (abc111 の D = arc103_b)
$ atcoder meta set abc111 --task d --url https://atcoder.jp/contests/abc111/tasks/arc103_b
updated abc111_d
  url:         (none) -> https://atcoder.jp/contests/abc111/tasks/arc103_b
$ atcoder test abc111 --task d   # 以降はこの url から取得する
```

## 動作仕様

| 観点 | 動作 |
|---|---|
| URL パース | `https?://` 有無を問わず `atcoder.jp/contests/<c>/tasks/<t>` から `<c>`/`<t>` を抽出。クエリ (`?lang=ja`) / フラグメントは無視 |
| 取得元 URL の解決 | `ensureTests` は fetch 前に `meta.toml` を読み、`url` が空でなければそれを使う (override)。空なら `https://atcoder.jp/contests/<contest>/tasks/<task>` を導出。取得後も `url` (= 使った URL) を保存して override を保つ |
| URL override が効く範囲 | `set --url` した url は、`meta fetch` だけでなく `test` / `start` の取得経路 (共通 `ensureTests`) でも尊重される。スロット (contest/task) は `abc111_d` のまま、ページだけ `arc103_b` を引く |
| `fetch` の冪等性 | 常に再取得 (`refresh=true`)。`tests/` の既存ファイルはクリアして書き直す。`tests-extra/` (ユーザ追加ケース) には触れない |
| `show`/`set --time-limit` の前提 | `meta.toml` が無ければ「未キャッシュ」エラー (exit 1)。`fetch` を案内する |
| `set --url` の前提 | スロット未キャッシュでも可。空の `meta.toml` (contest/task/url のみ、time_limit_ms=0、fetched_at ゼロ値) を作る。`show` は未取得スロットの `fetched_at` を `(not fetched yet)` と表示 |
| `set` の部分更新 | 渡されたフィールドだけ上書きし、他フィールド (url / time_limit_ms / fetched_at / samples) は保持 |
| 解答非破壊 | `meta` はキャッシュ層のみ操作。解答ファイル・`tests-extra/` は読み書きしない |
| 既存ワークフロー共存 | `fetch` で温めたキャッシュは `test`/`start` がそのまま再利用する (キャッシュキー・スキーマ同一) |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/meta.go` (新規) | `cmdMeta(args) (int, error)`。`fetch`/`show`/`set` へディスパッチ。ターゲット解決 (URL or contest+--task)、`set --url`/`--time-limit`、出力整形 |
| `cmd/atcoder/main.go` | `builtins` に `meta` を追加、`dispatch` の switch に `case "meta"`、`usage()` に構文行を追加 |
| `internal/layout/layout.go` | task URL パーサを追加。`ParseTaskURL(s string) (contestID, taskID string, ok bool)` と `IsTaskURL(s string) bool` |
| `internal/testexec/meta.go` | 内部 `meta` 構造体を公開 (`Meta`) にリネーム。公開ラッパー `LoadMeta(contest, task) (*Meta, error)` / `SaveMeta(contest, task, *Meta) error` / `SampleCount(contest, task) (int, error)` を追加 |
| `internal/testexec/fetch.go` | `fetchProblem(contest, task)` を `fetchProblem(url)` 化。`DefaultTaskURL(contest, task)` と `resolveFetchURL(contest, task, override)` を追加 |
| `internal/testexec/test.go` | `meta` → `Meta` 参照更新に加え、`ensureTests` が fetch 前に `meta.toml` の `url` override を読み、`resolveFetchURL` で取得元 URL を決める |
| `internal/cliargs/cliargs.go` | `--time-limit` / `--url` を値フラグに登録 (位置引数と取り違えないため) |
| `internal/complete/complete.go` | `meta` のサブコマンド候補とフラグ (`--task`/`--url`/`--time-limit`) |
| `fixtures/run.sh` | `meta` の exit code を固定する run_case 群を追加 (ネットワーク非依存の show/set/url override/引数誤りのみ) |
| `docs/tools/atcoder-meta-usage.md` (新規) | `meta` の利用手引 |
| `docs/tools/todo.md` | ロードマップ項目を追記し本要件へ相互リンク |

### `internal/layout` に足す関数 (素描)

```go
// ParseTaskURL は AtCoder の task ページ URL から contest_id / task_id を抽出する。
// 例: "https://atcoder.jp/contests/abc457/tasks/abc457_d" -> ("abc457", "abc457_d", true)
// スキーム省略 ("atcoder.jp/...") とクエリ/フラグメント付きも許容する。
func ParseTaskURL(s string) (contestID, taskID string, ok bool)

// IsTaskURL は s を task URL とみなすか (":// を含む or atcoder.jp/ を含む)。
func IsTaskURL(s string) bool
```

### `internal/testexec` に足す公開 API (素描)

```go
// Meta はキャッシュした meta.toml の内容 (旧内部 meta を公開化)。
type Meta struct {
    Contest     string
    Task        string
    URL         string
    TimeLimitMs int
    FetchedAt   time.Time
}

// LoadMeta は contest/task のキャッシュ済み meta.toml を読む。未取得なら error。
func LoadMeta(contest, task string) (*Meta, error)

// SaveMeta は contest/task の meta.toml を書き戻す (キャッシュディレクトリは作成)。
func SaveMeta(contest, task string, m *Meta) error

// SampleCount は tests/ のサンプルケース数を返す。
func SampleCount(contest, task string) (int, error)
```

## エラーハンドリング

| 状況 | 動作 (exit code) |
|---|---|
| `meta` にサブコマンド無し / 未知サブコマンド | usage 風メッセージ、exit 2 |
| ターゲット指定なし (位置引数も URL も無い) | エラー、exit 2 |
| URL らしいが `/contests/.../tasks/...` を抽出不可 | エラー、exit 2 |
| contest 指定だが `--task` 欠落 | エラー、exit 2 |
| `set` でフィールド指定が 1 つも無い (`--url`/`--time-limit` どちらも無) | エラー、exit 2 |
| `set --time-limit` の duration パース失敗 / `<= 0` | エラー、exit 2 |
| `set --url` が AtCoder の URL でない (`atcoder.jp/` も `://` も含まない) | エラー、exit 2 |
| `fetch` の取得失敗 (ネットワーク / HTML パース / override url が 404 等) | エラー、exit 1 |
| `show`/`set --time-limit` で未キャッシュ (`meta.toml` 無し) | エラー (「先に fetch せよ」)、exit 1 |
| `set --url` で未キャッシュ | エラーにせず空の `meta.toml` を作って url を記録、exit 0 |
| 成功 | exit 0 |

## 非機能要件

- **既存非破壊**: `test`/`start`/`new` の挙動を変えない。`meta` 構造体のリネームは internal に閉じ、外部 API シグネチャ (`EnsureTests` 等) は維持。
- **キャッシュのみ操作**: 解答ファイル・`tests-extra/` を読み書きしない (`--refresh` 系と同じ安全設計)。
- **rate limit 配慮**: `fetch` は 1 リクエスト/呼び出し。既存 `fetchProblem` の User-Agent / Accept-Language をそのまま使う。
- **前方互換**: `meta.toml` スキーマは不変。将来 `set` 対象や JSON 出力を足しても既存キャッシュを壊さない。
- **exit code 規約**: 引数/フラグ誤り = 2、実行時失敗 (fetch 失敗 / 未キャッシュ) = 1、成功 = 0。

## 将来の拡張ポイント

- `set` の上書き対象フィールドの追加 (`--url`/`--time-limit` 以外)。
- `meta path <url|contest --task>` でキャッシュパスのみ出力 (スクリプト連携)。
- `meta show --json` で機械可読出力 (要件 042 に倣う)。
- `meta fetch` をコンテスト URL (`/contests/<c>`) に拡張し、タスク一覧を一括 fetch (`new abc` と統合 / 要件 003 と接続)。

## 用語

| 用語 | 例 | 意味 |
|---|---|---|
| `contest_id` | `abc457` | コンテスト ID。URL の `/contests/<contest_id>/` |
| `task_id` | `abc457_d` | タスク ID。URL の `/tasks/<task_id>` |
| `letter` | `d` | task_id 末尾の問題記号 |
| task URL | `https://atcoder.jp/contests/abc457/tasks/abc457_d` | 問題ページの URL。`meta` の主入力 |

## 関連ドキュメント

- 元のサンプル取得・キャッシュ仕様: [`001-exercise-test.md`](001-exercise-test.md)
- コンテストメタ一括準備 (将来の統合先): [`003-exercise-abc-contest-meta.md`](003-exercise-abc-contest-meta.md)
- 利用手引: [`../atcoder-meta-usage.md`](../atcoder-meta-usage.md)
- アーキテクチャ: [`../atcoder-test-architecture.md`](../atcoder-test-architecture.md)
- ロードマップ: [`../todo.md`](../todo.md)
