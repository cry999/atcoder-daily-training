# `atcoder` タスク URL のタスク一覧ページ解決 要件定義

## 概要

`atcoder test` / `atcoder gen` がタスクページを fetch するときの取得元 URL を、`contest_id` と `letter` からの機械生成だけに頼らず、**タスク一覧ページ (`/contests/<contest>/tasks`) から該当タスクの実 URL を引いて解決する**フォールバックを足す。機械生成 URL が 404 のとき (task_id が contest と食い違う共催問題など) に自動で正しい URL に辿り着き、解決結果を meta.toml に記録して次回以降の再解決を省く。

## 背景・目的

現状、取得元 URL は `internal/testexec/fetch.go` の以下で決まる:

- `DefaultTaskURL(contest, task)` = `https://atcoder.jp/contests/<contest>/tasks/<task>`。ここで `task` は `cmd/atcoder/test.go` が `--task d` を `<contest>_<letter>` (= `abc111_d`) に正規化した**推定 task_id**。
- `resolveFetchURL(contest, task, override)` = override (meta.toml の `url`) があればそれ、無ければ `DefaultTaskURL`。

これは「task_id が contest と一致する」前提の機械生成で、**過去回との共催などで task_id が contest と食い違う問題**では破綻する。例:

- `abc111` の D 問題の task_id は `arc103_b`。`atcoder test abc111 --task d` は推定 task_id `abc111_d` から `.../contests/abc111/tasks/abc111_d` を生成するが、これは **404**。
- 現状の唯一の逃げ道は `atcoder meta set abc111 --task d --url <arc103_b の URL>` を**人手で**打って override を入れること。URL を人が調べて貼る必要があり摩擦が高い。

一方、`internal/contestmeta` は既に `/contests/<contest>/tasks` を fetch してタスク一覧 (出現順の task_id 配列) を取り出す機構 (`extractTasks`) を持っている。一覧ページのリンクは `/contests/<contest>/tasks/<実 task_id>` であり、共催問題でも**実 task_id がそのまま載っている** (abc111 のページには `/contests/abc111/tasks/arc103_b` が並ぶ)。

そこで、機械生成 URL が 404 のときに一覧ページを引いて実 URL を解決するフォールバックを入れ、人手の override 設定を不要にする。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 解決の起点 | 機械生成 URL (`DefaultTaskURL`) の fetch が **HTTP 404** のときのみフォールバック発火 | 常時一覧ページ優先に切り替える設定 (`config`) |
| 解決経路 | 一覧ページの**出現順 = letter 順**として、`letter` の位置 (index) で実 task_id を引く | letter 列テキストとの厳密突き合わせ |
| 対象コマンド | `atcoder test` / `atcoder gen` (共通ヘルパー経由の両方) | `meta fetch` 等も同ヘルパー経由なので自動的に恩恵 |
| 解決結果の永続化 | 解決できたら meta.toml の `url` に実 URL を記録し、次回は override 経路で直行 | — |
| override が有るとき | フォールバックしない (人が明示した URL の 404 は実エラーとして表面化) | — |

**境界**: 一覧ページの fetch とパースは `internal/contestmeta` の既存ロジックを再利用する (新しいパーサは作らない)。URL の機械生成 (`DefaultTaskURL`) と override 優先 (`resolveFetchURL`) の既存挙動は変えない — フォールバックは 404 の後段にだけ足す。

## 取得元 URL 解決のスキーマ

`atcoder test abc111 --task d` を例に、解決の優先順位:

| 優先 | 経路 | URL | 条件 |
|---|---|---|---|
| 1 | override | meta.toml の `url` | `url` が非空 (`atcoder meta set --url` 済み、または過去のフォールバック解決済み) |
| 2 | 機械生成 | `DefaultTaskURL(contest, task)` = `.../contests/abc111/tasks/abc111_d` | override 無し。**まずこれを試す** |
| 3 | 一覧ページ解決 (新規) | `DefaultTaskURL(contest, realTaskID)` = `.../contests/abc111/tasks/arc103_b` | override 無し **かつ** 2 が HTTP 404 |

一覧ページ解決の手順:

1. `task` (= `abc111_d`) の末尾 `_` 以降を `letter` とする → `d`。単一の英小文字 (`a`–`z`) でなければ解決不能としてフォールバック中止 (2 の 404 をそのまま返す)。
2. `letter` の序数を index とする → `d` = 3 (0 始まり)。
3. 一覧ページ (`/contests/<contest>/tasks`) を fetch し、出現順の task_id 配列 `tasks` を得る。
4. `index < len(tasks)` なら `realTaskID = tasks[index]`。そうでなければ解決不能 (404 をそのまま返す)。
5. `realTaskID == task` (推定と同じ) なら別 URL にならないので解決失敗扱い (404 をそのまま返す)。
6. `DefaultTaskURL(contest, realTaskID)` を fetch。成功したら、その `problem.URL` を meta.toml の `url` に記録する。

## CLI 仕様

**新しいフラグ・サブコマンドは追加しない。** 既存の `atcoder test <contest> --task <letter>` / `atcoder gen <contest> --task <letter>` の挙動が、404 時に自動で正しい URL に辿り着くようになるだけ。

### 出力イメージ

`abc111` の D (= `arc103_b`) を、override 未設定で初めて取得する場合:

```
$ atcoder test abc111 --task d
Fetching abc111 d ...
# 内部: abc111_d の URL が 404 → 一覧ページから arc103_b を解決 → 取得成功
=== abc111 d (arc103_b) ===
...
```

失敗経路 (letter が解決不能・一覧にも無い) では、従来どおり機械生成 URL の 404 を実エラーとして表面化する:

```
$ atcoder test somecontest --task z
Fetching somecontest z ...
error: AtCoder から取得できませんでした: HTTP 404 for https://atcoder.jp/contests/somecontest/tasks/somecontest_z
```

## 動作仕様

| 観点 | 動作 |
|---|---|
| 発火条件 | override 無し **かつ** 機械生成 URL の fetch が HTTP 404。それ以外 (200 成功・override 有り・ネットワークエラー等) はフォールバックしない |
| 404 の判定 | `fetchProblem` が返すエラーから **HTTP ステータス 404 だけ**を型付きエラーで識別する。他ステータス (403 rate limit・5xx) はフォールバックせず実エラー扱い |
| override 有りの 404 | フォールバックしない。人が明示した URL の 404 はそのまま表面化する (誤設定を隠さない) |
| 冪等性 | フォールバックで解決した URL を meta.toml の `url` に保存するので、次回以降は優先度 1 (override 経路) で直行し、一覧ページ fetch は 1 回きり |
| 一覧ページ取得失敗 | 一覧ページ自体が引けない / タスクが 0 件なら解決不能。元の 404 エラーをそのまま返す (フォールバックの失敗で元のエラーを覆い隠さない) |
| rate limit 配慮 | フォールバックは 404 の後段でのみ発火し、追加リクエストは高々 1 回 (一覧ページ)。成功後は永続化されるので常態的な追加負荷にはならない |
| 既存挙動の非破壊 | 機械生成 URL が 200 で通る通常問題は一切追加 fetch しない。`resolveFetchURL` / `DefaultTaskURL` の戻り値も不変 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/testexec/fetch.go` | ① 取得元オリジンを差し替え可能にする `baseURL` 変数を導入し `DefaultTaskURL` がそれを使う (httptest で結線検証するため。既定 `https://atcoder.jp` で挙動不変)。② `fetchProblem` の非 200 エラーを HTTP ステータスを持つ型付きエラー (`httpStatusError`) にし、呼び出し側が 404 を識別できるようにする。③ フォールバックを閉じ込めた共通ヘルパー `resolveAndFetch(contest, task, override)` を追加 |
| `internal/testexec/test.go` | `ensureTests` の override 読み → `resolveFetchURL` → `fetchProblem` の三段を `resolveAndFetch` 呼び出しに置換。返った `problem.URL` (解決後の実 URL) を meta.toml に保存 (既存どおり `mta.URL = prob.URL`) |
| `internal/testexec/gensource.go` | `EnsureGenSource` も同様に `resolveAndFetch` へ置換 |
| `internal/contestmeta/fetch.go` | 一覧ページ DOM から出現順 task_id を取り出す既存 `extractTasks` の公開ラッパー `ExtractTaskIDs(doc, contest) []string` を追加 (一覧ページのリンク書式を 1 箇所に集約したまま testexec から再利用させる。挙動不変)。HTTP は testexec 側で行うため contestmeta に新しい fetch 関数は足さない |
| `internal/testexec/fetch_network_test.go` | httptest で「機械生成 URL は 404、一覧ページと実 task ページは 200」を配り、`resolveAndFetch` が実 URL に辿り着くことを固定。404 型付きエラーの識別も検証 |
| `internal/contestmeta/fetch_test.go` | `FetchTasks` 単体の回帰テストを追加 (既存 testdata を流用) |
| `docs/tools/atcoder-test-architecture.md` | URL 解決の優先順位 (override → 機械生成 → 一覧ページ解決) と 404 フォールバックの節を追記 |
| `docs/tools/usage/test.md` (該当あれば) | 共催問題で `meta set --url` 無しでも取得できる旨を追記 |
| `docs/tools/todo.md` | 本項目を DONE でマーク + 本要件へ相互リンク |

### 新規/変更する公開・非公開 API シグネチャ (Go 素描)

```go
// internal/contestmeta/fetch.go — 一覧ページ DOM から出現順 task_id を取り出す
// 既存 extractTasks の公開ラッパー (パーサのみ。HTTP は testexec 側)。
func ExtractTaskIDs(doc *html.Node, contest string) []string

// internal/testexec/fetch.go
var baseURL = "https://atcoder.jp" // テストで httptest へ差し替え可能に

// タスク一覧ページを baseURL から取得し ExtractTaskIDs でパースする。
func fetchTaskIDs(contest string) (tasks []string, err error)

// 非 200 を表す型付きエラー。呼び出し側が errors.As で 404 を識別する。
type httpStatusError struct {
    Code int
    URL  string
}
func (e *httpStatusError) Error() string

// override → 機械生成 → (404 なら) 一覧ページ解決、の順で problem を取得する。
// 返す problem.URL は実際に取得できた URL (解決後の実 URL)。
func resolveAndFetch(contest, task, override string) (*problem, error)
```

## エラーハンドリング

| 状況 | 動作 | exit code |
|---|---|---|
| 機械生成 URL が 200 | そのまま成功。フォールバックしない | 0 |
| 機械生成 URL が 404・一覧ページから実 URL を解決でき取得成功 | 成功。実 URL を meta.toml に保存 | 0 |
| 機械生成 URL が 404・letter が単一英小文字でない | 解決中止。元の 404 を返す | 1 (実行時失敗) |
| 機械生成 URL が 404・一覧ページ取得失敗 / index 範囲外 / 実 task_id が推定と同一 | 解決中止。元の 404 を返す | 1 |
| override 設定済みでその URL が 404 | フォールバックしない。404 を表面化 | 1 |
| 機械生成 URL が 403/5xx 等 (404 以外) | フォールバックしない。そのエラーを表面化 | 1 |

引数・フラグの誤りは従来どおり exit 2 (本要件では新フラグが無いため追加なし)。

## 非機能要件

- **冪等性**: フォールバック解決した URL を永続化し、追加の一覧ページ fetch は 1 回きり。
- **既存非破壊**: 通常問題 (機械生成 URL が 200) は挙動・追加 fetch ともに一切変わらない。`resolveFetchURL` / `DefaultTaskURL` の戻り値も不変。
- **前方互換**: meta.toml のスキーマは変えない (既存 `url` フィールドに解決結果を書くだけ)。
- **rate limit 配慮**: 追加リクエストは 404 後段の 1 回のみ。403/5xx ではフォールバックせず、無駄打ちしない。
- **依存方向**: `internal/testexec → internal/contestmeta` の新規 import を足す (循環なし。contestmeta は testexec に依存しない)。

## 将来の拡張ポイント

- 常時一覧ページ優先に切り替える `config` オプション (現状は 404 フォールバックのみ)。
- letter → index の位置解決を、一覧ページの letter 列テキストとの厳密突き合わせに強化 (現状は出現順 = letter 順の前提)。
- 解決した実 task_id を `atcoder meta show` で可視化する。

## 用語

| 用語 | 意味 | 例 |
|---|---|---|
| `contest_id` (contest) | コンテスト識別子 | `abc111` |
| `letter` | 1 文字のタスク識別子 | `d` |
| 推定 task_id | `<contest>_<letter>` で機械生成した task_id (共催問題では実 task_id と食い違う) | `abc111_d` |
| 実 task_id | 一覧ページに載る本来の task_id | `arc103_b` |

## 関連ドキュメント

- 要件 003 (`003-exercise-abc-contest-meta.md`) — `new abc` の一覧ページ一括 fetch。`contestmeta` の初出。
- ADR 0008 (`decisions/0008-gen-best-effort-raw-cache.md`) — fetch のベストエフォート / キャッシュ方針。
- `docs/tools/atcoder-test-architecture.md` — test の fetch / meta / キャッシュ構造。
