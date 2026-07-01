# `atcoder test` のテスト戦略

ツール本体 (`cmd/atcoder` + `internal/runner` / `internal/testexec` / `internal/ui`) の振る舞いをローカルで検証する方法をまとめる。

仕様・利用方法・内部設計は別ドキュメント:

- 要件定義: [001-exercise-test.md](./requirements/001-exercise-test.md)
- 利用手引: [docs/tools/usage/test.md](usage/test.md)
- アーキテクチャ: [atcoder-test-architecture.md](./atcoder-test-architecture.md)

## 方針

ユニットテストではなく、CLI を実際に呼び出す **スモークテスト** によって主要な実行パス (PASS / FAIL / RE / TLE / DEBUG フィルタ) が動いていることを保証する。

理由:

- ツールの本質は「サブプロセス起動 + I/O 比較 + 表示」で、内部関数を単体テストしても価値が薄い。
- 表示・終了コード・全体フローが実機で機能していることを確認したい。
- 解答コード = Python という外部依存があるため、現実のプロセス境界を通すほうが信頼できる。

スモークテストは `fixtures/` ディレクトリにある 5 種類のサンプルプログラムを使い、`fixtures/run.sh` が一括で実行する。

## 実行

```sh
./fixtures/run.sh
```

期待動作:

1. ツールを `go build` (一時ディレクトリへ)
2. 別の一時ディレクトリに `exercise/YYYY/MM/DD/` を掘り、`fixtures/fixture_*` を全件コピー
3. その一時ディレクトリに `cd` してから ツール本体を呼び出し
4. 各 fixture について `--task <name>` で起動、exit code を assert
5. 最後に `All fixtures behaved as expected.` または `N case(s) failed`

ツール本体には「テスト用パス上書き」のような専用機能を入れていない。スクリプトが当日の `exercise/YYYY/MM/DD/` 構造を一時ディレクトリ内に複製し `cd` することで、通常のユーザ操作と同じ呼び出し経路を辿る。

## fixture 一覧と検証する経路

| fixture | 入力 | 期待出力 | 期待挙動 | 検証する経路 |
|---|---|---|---|---|
| `fixture_pass` | `5` | `10` | PASS, exit 0 | 正常実行・出力一致 |
| `fixture_fail` | `5` | `10` | FAIL, exit 1 | 出力ミスマッチ・diff 表示 |
| `fixture_re` | `5` | `10` | RE, exit 1 | 子プロセス異常終了・stderr 表示 |
| `fixture_tle` | `5` | `10` | TLE, exit 1 | タイムアウト発火 (`time_limit=200ms` で `sleep(2)`) |
| `fixture_debug` (`-d` 無し) | `5` | `10` | FAIL, exit 1 | `[DEBUG]` 行が比較で汚染 |
| `fixture_debug` (`-d` 付き) | `5` | `10` | PASS, exit 0 | DEBUG=1 env 受け渡し + `[DEBUG]` フィルタ |
| `fixture_debug` (`--submit`) | `5` | `10` | exit 0 (提出準備へ) | 無条件 `[DEBUG]` print がコメントアウト後ソース実行で消える → クリーン (要件 049) |
| `fixture_debugjson` (`-d --pp`) | `5` | `10` | PASS, exit 0 | valid JSON の `[DEBUG]` が `debug:` で 2-space 整形される (`--pp` 単体は stderr に note)。要件 047 |
| `fixture_extra` | `5` / x01 `7` / x02 `3` | `10` / `14` / `999` | suite exit 1 (x02 FAIL) | `tests-extra/` 連結消費・表示 id `x01`/`x02`・`-c x01`/`-c 01` フィルタ |
| `fixture_okdebug` | `5` | `10` | 通常 PASS exit 0 / `--submit` exit 1 | `sys.stderr.write` で `[DEBUG]` (コメントアウトをすり抜ける)。判定は stdout のみで PASS だが `--submit` はコメントアウト後ソース実行でも `[DEBUG]` が残り検出 → 非 TTY 中止 (要件 044 / 049 安全網) |

詳細は [fixtures/README.md](../../fixtures/README.md)。

> フラグ/サブコマンド単位の経路 (引数順序非依存・`config`・補完・`usage` テレメトリ等) も同じ `run.sh` で smoke する。とくに利用テレメトリ (要件 037) は `XDG_DATA_HOME` を一時 dir に固定し、各ケースの実行が `events.jsonl` に記録されること・`atcoder usage` が `exit 0`・`ATCODER_NO_USAGE=1` で記録しないことを確認する (専用 `.py` fixture は不要)。

> `atcoder meta` (要件 046) の `show`/`set` と引数誤り (exit 2)・未キャッシュ (exit 1) も `run.sh` で smoke する。プリポピュレートされた `fixture_pass` のキャッシュ (書き込み可能な一時 `XDG_CACHE_HOME` にコピー済み) を再利用するので専用 fixture は不要。`fetch` はネットワークに触れるため回さない。

> `atcoder gen` (要件 060) も `run.sh` で smoke する。プリポピュレートされた `fixture/fixture_gen/gen.toml` (小さい制約) を解析して生成する経路 — `--show-spec` の内容 (`scalar : N M` / `coverage: full`)・`--seed` 生成・`--size max|min`・`-n 2 -o <dir>` の `NN.in`・`--save` の `tests-extra/` 追加、および引数誤り (`--task` 欠落 / `--show-spec` × `--seed` / 不正 `--size`) の exit 2 — を固定する。`fetch` はネットワークに触れるため回さない (生成は入力のみで judge しないため `.py` fixture は不要)。

> `atcoder record` (solve-stat 記録, 要件 061) も `run.sh` で smoke する。ネットワーク不要・非 TTY では対話プロンプトを出さないので、非対話フラグ経路だけで決定論的に検証する。`config set/get/show target.<category>.<letter>` (目標実装時間) と不正値の `exit 2` / `record start` が解答ファイルを作り `started_at` を刻む (冪等な再 start) / `record stop --no-ac --time 25m` が `solved_at`・`duration_ms`・(目標があれば) `target_ms` を刻む / `record --score`・個別軸 (`--impl`)・`--ac`/`--no-editorial` の部分更新と既存 duration の温存 / エラー系 (`--task` 欠落・`--score` の値数/範囲・`--ac`+`--no-ac` 併用・不正 `--time`・`record edit` 未実装・解答ファイル不在) の `exit 2`/`1` / solve-stat を書いた後 `stats` に `recorded (`・`score (avg` セクションが出ること、を確認する。record は `record start` が作る解答ファイル先頭のコメントブロックを読み書きするだけで judge しないため、専用 `.py` fixture は不要。

## 実行すべきタイミング

リファクタリングや機能追加で以下を触ったときに走らせる:

- `cmd/atcoder/` — 引数パース・dispatch・factory
- `internal/runner/` — プロセス実行
- `internal/testexec/` — `test` の orchestration・judge・meta・fetch
- `internal/runexec/` — `run` の orchestration
- `internal/cachepath/` — キャッシュ配置の解決
- `internal/ui/` — Reporter 実装・スタイル
- `internal/usagelog/` — 利用テレメトリの記録・集計 (要件 037)

逆に、`docs/` や `exercise/`/`abc/`/`adt/`/`dp/` 等の練習問題のみの変更では走らせる必要はない。

## fixture を追加するには

新しい振る舞い (例: 新フラグや新言語サポート) を追加したら、対応する fixture をひと組追加する:

1. `fixtures/fixture_<name>.py` を作成
2. `fixtures/fixture_<name>/meta.toml` を作成 (`contest = "fixture"`, `task = "fixture_<name>"`, `time_limit_ms`, `fetched_at` を埋める)
3. `fixtures/fixture_<name>/tests/01.in` / `01.out` を作成
4. `fixtures/run.sh` の `run_case` 行を追加 (expected exit code を含めて)
5. `fixtures/README.md` と本ドキュメントの fixture 一覧に追記

`meta.toml` の `url` は空文字でよい (フィクスチャは AtCoder にアクセスしない)。

## fetch (HTTP 取得) のオフラインテスト

サンプル・時間制限・コンテストメタの取得 (`internal/testexec/fetch.go` の `fetchProblem`、`internal/contestmeta/fetch.go` の `Fetch` / `fetchDoc`) は実 AtCoder を叩くコードなので、スモークテスト (`fixtures/run.sh`) では回さない。代わりに **実ページ相当の HTML を `testdata/` に保存し、`httptest.Server` から配って** 取得〜HTML 解析の結線をユニットテストで固定する。実ネットワークには一切触れない。

- `internal/testexec/testdata/problem_abc457_a.html` — 問題ページ。`fetch_network_test.go` が `fetchProblem` に食わせ、`?lang=ja` 付与・HTTP ステータス判定・時間制限/サンプル/入力形式/制約の抽出を検証する。
- `internal/contestmeta/testdata/contest_top.html` / `contest_tasks.html` — コンテストトップ + タスク一覧。`fetch_test.go` が `baseURL` を httptest サーバへ向け替えて `Fetch` を丸ごと検証する (タイトル・タスク列・開始/終了時刻・所要時間、および空タスク/非 200 のエラー化)。

`fetchProblem` / `fetchDoc` は URL を引数で受け取るため直接 httptest に向けられる。`contestmeta.Fetch` だけは取得元オリジンをハードコードしていたので、テストが差し替えられるよう `var baseURL` の seam を 1 つ設けている (本番は AtCoder 固定)。解析ロジック単体 (`extractSamples` 等) のテストは従来どおり in-memory HTML で継続する。

AtCoder の DOM が変わって testdata が古くなったら、実ページを 1 度取得して該当 HTML を差し替える (以後は再びオフライン)。

## 制約と非対象

- 表示の見た目 (色や配置) はスモークテストで検証できない。`CLICOLOR_FORCE=1` で手動目視を推奨。
- `atcoder test --interactive` の **chat TUI** は TTY を要するため `fixtures/run.sh` ではカバーされない (スクリプト内の interactive ケースは非TTY passthrough のみ試験する)。手動確認は端末から `atcoder test fixture --task interactive --interactive` を直接叩く。
- スモークテスト (`fixtures/run.sh`) は事前生成済みキャッシュを使い、HTTP fetch は踏まない。fetch そのものは上記「fetch (HTTP 取得) のオフラインテスト」で `httptest` + `testdata` により別途固定する。並列実行の挙動は対象外。
- Python 以外の言語の Runner はまだ存在しないので未対象。追加されたら言語ごとの fixture を増やす。
