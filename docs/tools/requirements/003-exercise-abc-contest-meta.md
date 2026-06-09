# `atcoder` コンテストメタ一括準備 要件定義

## 概要

ABC 本番開始直後に、コンテスト 1 つ分のサンプル取得・キャッシュ・解答スケルトン生成を **1 コマンド** で済ませられるようにする。あわせて、コンテスト単位の情報 (タスクリスト・開始 / 終了時刻・URL) を **コンテストメタ** として 1 か所に保存し、Phase 2 の E (本番モード判定) / G (タイマー) の前提を整える。

`docs/tools/abc-todo.md` の MVP "B. コンテストメタの取り扱い" の要件詳細。MVP "A" (`docs/tools/requirements/002-exercise-abc-layout.md`) で導入した ABC レイアウトと、既存の fetch / cache 基盤 (`internal/testexec`) の上に乗せる。

## 背景・目的

- 本番では A〜G が一斉に必要になる。現状は問題ごとに `atcoder test abc457 --task d` を叩いて都度 fetch するため、開始直後の準備が **問題数 × fetch + ファイル作成** の手作業になる。
- MVP A により解答パスは `abc/<contest_num>/<letter>.py` に解決できるようになったが、**そのファイルを置く** 作業と **サンプルを取りに行く** 作業は依然として問題ごとに発生する。これを 1 コマンドにまとめる。
- コンテストの開始 / 終了時刻・タスクリストを 1 つの場所 (`contest.toml`) に保存しておけば、E (本番モード判定) や G (タイマー) が後から参照できる。MVP B の時点でこのメタを揃えておく。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象コマンド | `atcoder new abc <contest>` (既存 `new` を拡張) | `arc`/`agc`/`ahc` モード、`atcoder contest status` (E/G で別途) |
| 対象 contest プレフィックス | `abc` のみ | ABC レイアウトを共有できる `arc`/`agc`/`ahc` |
| 取得物 | タスクリスト・各タスクのサンプル + meta・コンテストメタ (時刻含む) | standings / 順位 / penalty (G 後段) |
| 解答スケルトン | `abc/<contest_num>/<letter>.py` を **空ファイル**で生成 | 言語別テンプレート流し込み (別管理の H) |
| 提出・認証 | 対象外 (`oj` で代替、後回し C/D) | — |

### スケルトン生成の方針 (H との境界)

テンプレート連携 (H) は ABC 専用ではないため `docs/tools/todo.md` に移管済み。MVP B では **中身のない空の `.py` ファイル**だけを生成し、本格的なテンプレート流し込みは H 実装時に差し替える。これにより:

- `atcoder test` / `atcoder run` の「解答ファイルが見つかりません」エラーが本番開始直後から出なくなる (MVP A の解答パス解決がそのまま通る)。
- H が入ったら、空ファイル生成箇所を「テンプレート書き込み」に置き換えるだけで済む (生成のフックは MVP B で確保しておく)。

## ディレクトリ構造

```
# 解答コード (MVP A と同じ位置。new abc が空ファイルを生成)
abc/<contest_num>/
  a.py   ← 空ファイル
  b.py
  ...
  g.py

# タスク単位キャッシュ (既存のまま。各タスクで ensureTests を流用)
$XDG_CACHE_HOME/atcoder-tools/<contest_id>/<task_id>/
  meta.toml
  tests/
    01.in
    01.out
    ...

# コンテスト単位メタ (新規)
$XDG_CACHE_HOME/atcoder-tools/<contest_id>/contest.toml
```

- タスク単位の `meta.toml` (`internal/testexec/meta.go`) と、コンテスト単位の `contest.toml` は **別ファイル**として同じ contest dir 直下に並べる。前者はタスクごとのサブ dir 内、後者は contest dir 直下。
- キャッシュキー・URL に使う ID は MVP A の用語に従う: `contest_id` = `abc457`、`contest_num` = `457`、`task_id` = `abc457_d`、`letter` = `d`。

## コンテストメタのスキーマ

`contest.toml` (`github.com/BurntSushi/toml` で encode/decode、タスク meta と同じ流儀):

```toml
contest      = "abc457"
url          = "https://atcoder.jp/contests/abc457"
title        = "AtCoder Beginner Contest 457"
start_at     = 2026-06-14T21:00:00+09:00
end_at       = 2026-06-14T22:40:00+09:00
duration_ms  = 6000000
tasks        = ["abc457_a", "abc457_b", "abc457_c", "abc457_d", "abc457_e", "abc457_f", "abc457_g"]
fetched_at   = 2026-06-09T12:34:56+09:00
```

| フィールド | 型 | 取得元 | 用途 |
|---|---|---|---|
| `contest` | string | CLI 引数 | キー / 表示 |
| `url` | string | 組み立て (`https://atcoder.jp/contests/<contest>`) | 表示・リンク |
| `title` | string | コンテストトップページ | G の表示 |
| `start_at` | time | コンテストトップページの `<time class="fixtime">` | E の判定 / G の残り時間 |
| `end_at` | time | 同上 (2 つ目の fixtime) | E の判定 / G の残り時間 |
| `duration_ms` | int | `end_at - start_at` を ms 換算 | G の進捗バー等 |
| `tasks` | []string | タスク一覧ページ | 一括 fetch の対象、E の対象タスク判定 |
| `fetched_at` | time | 取得時刻 | キャッシュ鮮度確認 / `--refresh` 判断材料 |

- `start_at` / `end_at` は TOML のネイティブ datetime (オフセット付き) で保存する。タスク meta の `fetched_at` と同様、`time.Time` に decode できる。
- 時刻が取れなかった場合 (未公開コンテスト等) は `start_at` / `end_at` をゼロ値のまま保存し、`tasks` とサンプルの取得は継続する (時刻はあくまで Phase 2 用の付加情報で、サンプル取得を妨げない)。

## CLI 仕様

既存 `atcoder new` を **モード分岐**で拡張する。後方互換のため引数なしは従来挙動。

```
atcoder new                       # 既存: exercise/YYYY/MM/DD/ を作成 (変更なし)
atcoder new abc <contest> [flags] # 新規: ABC コンテスト一括準備
```

`abc` はモード名 (= レイアウト名)。将来 `new arc <contest>` 等に拡張できるよう、第 2 引数をモードとして扱う。

### `atcoder new abc <contest>`

| 引数 / フラグ | 説明 |
|---|---|
| `<contest>` | contest ID (`abc457` のフル形式。`abc<NNN>` でなければエラー) |
| `--refresh` | サンプル / コンテストメタを再取得して上書き (既存 `test --refresh` と同セマンティクス) |
| `--tasks <list>` | 対象タスクを限定 (`a,b,c` or `abc457_a,...`)。省略時はタスク一覧ページから全件 |
| `--no-skeleton` | 解答スケルトン (`abc/<num>/<letter>.py`) を生成しない (fetch とメタ保存のみ) |
| `--no-fetch` | サンプル取得をスキップし、コンテストメタ + スケルトンのみ (オフライン下準備用) |

`--tasks` と `--refresh` を組み合わせれば「A だけ後から取り直す」のような **部分更新**ができる (下記「動作仕様」参照)。

### 処理ステップ

`atcoder new abc abc457` 実行時:

1. **contest ID 検証**: `abc<NNN>` にマッチしなければ exit 2 (フラグ / 引数エラー)。
2. **コンテストメタ取得** (`--no-fetch` 時はスキップ):
   - `/contests/<contest>` トップページを fetch し `title` / `start_at` / `end_at` を抽出、`duration_ms` を算出。
   - `/contests/<contest>/tasks` を fetch しタスク ID リストを抽出。
   - `--tasks` 指定があればその集合に絞る。
3. **`contest.toml` を保存** (`$XDG_CACHE_HOME/atcoder-tools/<contest>/contest.toml`)。`--refresh` でなくても、メタが無ければ取得し、あれば再利用。
4. **各タスクのサンプル + meta を取得**: タスクごとに既存 `ensureTests` を呼び、`<contest>/<task_id>/tests/` と `meta.toml` を埋める。進捗を 1 行ずつ表示。
5. **解答スケルトン生成** (`--no-skeleton` 時はスキップ):
   - 各 task_id から MVP A の `layout.Letter` で letter を求め、`abc/<contest_num>/<letter>.py` を**存在しなければ**空ファイルで作成。
   - 既存ファイルは**上書きしない** (本番中に書いたコードを潰さない)。`--refresh` でも解答ファイルには触れない。

### 出力イメージ

```
$ atcoder new abc abc457
contest abc457 — AtCoder Beginner Contest 457
  21:00:00 – 22:40:00 (100m)
fetching tasks ... 7 found
  [1/7] abc457_a  ok (2 samples)
  [2/7] abc457_b  ok (3 samples)
  ...
  [7/7] abc457_g  ok (2 samples)
skeleton: abc/457/{a,b,c,d,e,f,g}.py (7 created)
ready. run: atcoder test abc457 --task a
```

## 動作仕様

### 一括 fetch とキャッシュ共有

- 各タスクの取得は **既存 `ensureTests` をそのまま再利用**する。これにより、後日 `atcoder test abc457 --task d` を叩いたときに同じキャッシュがヒットし、二重取得が起きない (MVP A の「キャッシュキーは task_id 共有」と一貫)。
- `--refresh` 未指定時は、タスク dir に `tests/` と読める `meta.toml` があればそのタスクの fetch をスキップする (既存 `ensureTests` のキャッシュヒット判定を踏襲)。途中で中断・再実行しても、取得済みタスクは飛ばして残りだけ取りに行く (**冪等**)。

### 部分更新 / `--refresh`

| 操作 | 挙動 |
|---|---|
| `new abc abc457` (2 回目) | キャッシュヒットしたタスクは fetch スキップ。未取得タスクのみ取得。`contest.toml` は既存を再利用。スケルトンは既存ファイルを残し不足分のみ作成 |
| `new abc abc457 --refresh` | 全タスクのサンプル + meta と `contest.toml` を再取得して上書き。**解答ファイルは上書きしない** |
| `new abc abc457 --tasks a --refresh` | タスク `a` だけ再取得。`contest.toml` の `tasks` は再 fetch 結果でなく既存を尊重 (部分更新で全体リストを壊さない) |

- `--refresh` の作用範囲は**キャッシュ (サンプル / meta / contest.toml) のみ**。リポジトリ内の解答ファイルには一切触れない。誤って提出前コードを消さないための安全側設計。

### 進捗表示

- タスク数 × fetch でそれなりに時間が掛かる (7 問なら 7 回の HTTP)。`[i/N] <task_id>` 形式で 1 行ずつ進捗を出す (既存 `Reporter.Fetching` の延長で実現)。
- AtCoder への連続アクセスになるため、タスク間に短い間隔 (例: 200〜500ms) を入れて rate limit を避ける。間隔値は定数で持ち、将来フラグ化できる余地を残す。

### 既存 `atcoder new` との共存

- 引数なし `atcoder new` は従来通り当日 dir を作成 (regression なし)。
- `atcoder new abc <contest>` はサブモードであり、当日 dir は作らない。両者は独立。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/new.go` | `cmdNew(args []string)` にシグネチャ変更。`args[0] == "abc"` でモード分岐。既存無引数パスは温存 |
| `cmd/atcoder/main.go` | `case "new"` を `cmdNew(os.Args[2:])` 呼び出しに変更。usage 文字列更新 |
| 新規 `internal/contestmeta/` | `contest.toml` のスキーマ・load/save・コンテストメタ fetch (トップ / タスク一覧ページのパース) を集約 |
| `internal/cachepath/cachepath.go` | `Contest(contest) string` ヘルパー追加 (`<Base>/atcoder-tools/<contest>/`)。既存 `Task` はこれを基点に再構成可 |
| `internal/testexec/` | `ensureTests` を contest 準備からも呼べるよう公開・切り出し (現状は `Run` 内部から呼ぶ private)。fetch / meta 構造体は再利用 |
| `internal/layout/` | `Letter` / `ContestNum` 抽出ヘルパーを skeleton 生成から利用 (MVP A で導入済みの関数を流用、不足あれば `ContestNum(contestID)` を追加) |
| `fixtures/run.sh` | `new abc` の smoke を追加 (ネットワーク無しで回せるよう、fetch はモック / `--no-fetch` 経路でスケルトン生成だけ検証する案) |

### 新規 `internal/contestmeta/` パッケージの責務

タスク単位の `internal/testexec/meta.go` と対になる、**コンテスト単位**のメタ層。

```go
package contestmeta

// Meta は contest.toml のスキーマ。
type Meta struct {
    Contest    string    `toml:"contest"`
    URL        string    `toml:"url"`
    Title      string    `toml:"title"`
    StartAt    time.Time `toml:"start_at"`
    EndAt      time.Time `toml:"end_at"`
    DurationMs int       `toml:"duration_ms"`
    Tasks      []string  `toml:"tasks"`
    FetchedAt  time.Time `toml:"fetched_at"`
}

// Load / Save は contest.toml の読み書き (BurntSushi/toml)。
func Load(path string) (*Meta, error)
func Save(path string, m *Meta) error

// Fetch はトップページ + タスク一覧ページを取得し Meta を組む。
// 時刻が取れなくても tasks が取れていれば成功扱い (時刻はゼロ値)。
func Fetch(contest string) (*Meta, error)
```

- HTTP クライアント・User-Agent・XPath パースは `internal/testexec/fetch.go` と同じ流儀 (`http.DefaultClient` + `antchfx/htmlquery`)。重複が気になるなら fetch の HTTP 下回りを共通ヘルパーに括り出す余地があるが、MVP B では `contestmeta` 内に閉じて持って良い。
- タスク一覧の抽出 XPath は `/contests/<contest>/tasks` テーブル行の `<a href="/contests/<contest>/tasks/<task_id>">` から task_id を拾う。
- 時刻は トップページの `.contest-duration` 内 `<time class="fixtime fixtime-full">` 2 要素 (開始 / 終了) をパースする。フォーマットは `2006-01-02 15:04:05-0700` 系。

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| contest ID が `abc<NNN>` でない | "contest ID must match abc<NNN>" で exit 2 |
| `new` の第 2 引数が未知モード (`abc` 以外) | usage を出して exit 2 |
| タスク一覧ページ取得失敗 (ネットワーク / 404) | エラー表示で exit 1。`contest.toml` もサンプルも書かない |
| 一部タスクの fetch だけ失敗 | そのタスクを warning 表示して継続。最後に「N/M succeeded」を出し、1 件でも失敗なら exit 1 (成功分のキャッシュは残す) |
| 時刻が取れない (未公開等) | warning のみ。`start_at`/`end_at` ゼロ値で `contest.toml` を保存し、サンプル取得は継続 |
| 解答ファイルが既に存在 | 上書きせずスキップ (info 表示)。エラーではない |
| `contest.toml` 保存失敗 (権限等) | エラー表示で exit 1 |

## 非機能要件

- **冪等性**: 同じコマンドの再実行で副作用が積み上がらない。取得済みタスクはスキップ、既存解答ファイルは温存。途中中断 → 再実行で残りだけ取得できる。
- **既存ワークフロー非破壊**: 引数なし `atcoder new` と既存 `test` / `run` のキャッシュ挙動は不変。`new abc` は同じ task キャッシュを共有するだけ。
- **オフライン下準備**: `--no-fetch` でネットワーク無しでもスケルトンと (取得済みなら) メタを揃えられる。
- **Phase 2 への前方互換**: `contest.toml` のスキーマが E (時刻範囲判定) / G (残り時間表示) の入力として十分。スキーマ追加はあっても破壊的変更を避ける。
- **rate limit 配慮**: 一括 fetch は逐次 + 短い間隔。並列 fetch はしない (AtCoder への負荷と BAN 回避)。

## 将来の拡張ポイント

- **`new arc <contest>` 等**: ABC レイアウトを共有する arc/agc/ahc へモードを追加。`internal/contestmeta` の fetch は contest プレフィックス非依存にできる。
- **`atcoder contest status <contest>`** (E/G): `contest.toml` を読んで残り時間・本番判定・対象タスクを表示する診断コマンド。MVP B のメタがそのまま入力になる。
- **テンプレート流し込み (H)**: 空ファイル生成箇所を、言語別テンプレート書き込みに差し替え。`--no-skeleton` / 既存ファイル温存のルールはそのまま活かせる。
- **fetch HTTP 下回りの共通化**: `internal/testexec/fetch.go` と `internal/contestmeta` で User-Agent / クライアントを共有ヘルパーに括り出す。
- **並列 fetch + キャッシュ TTL**: rate limit を見つつ将来検討 (当面は逐次で十分)。

## 用語

- **コンテストメタ**: コンテスト単位の情報 (タスクリスト・開始 / 終了時刻・タイトル・URL)。`contest.toml` に保存。タスク単位の `meta.toml` とは別。
- **タスクメタ**: タスク単位の情報 (`time_limit_ms`・URL・fetched_at)。既存 `internal/testexec/meta.go` の `meta`。
- **一括準備 (prepare)**: `new abc <contest>` が行う、タスク一覧取得 → サンプル一括 fetch → スケルトン生成 → コンテストメタ保存の一連の処理。
- **スケルトン**: 解答ファイルの初期状態。MVP B では空 `.py`。H 実装後はテンプレート入り。
- (その他 `contest_id` / `contest_num` / `task_id` / `letter` / `layout` は MVP A 要件定義に準拠)

## 関連ドキュメント

- `docs/tools/abc-todo.md` (上位ロードマップ。MVP "B" の要件詳細が本書)
- `docs/tools/requirements/002-exercise-abc-layout.md` (MVP "A" ABC レイアウト要件。ID 用語・レイアウト Strategy の定義元)
- `docs/tools/requirements/001-exercise-test.md` (既存 test サブコマンド要件。fetch / cache / meta の基盤)
- `docs/tools/todo.md` (テンプレート連携 H の移管先)
