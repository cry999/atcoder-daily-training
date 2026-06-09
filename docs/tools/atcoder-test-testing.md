# `atcoder test` のテスト戦略

ツール本体 (`cmd/atcoder` + `internal/runner` / `internal/testexec` / `internal/ui`) の振る舞いをローカルで検証する方法をまとめる。

仕様・利用方法・内部設計は別ドキュメント:

- 要件定義: [001-exercise-test.md](./requirements/001-exercise-test.md)
- 利用手引: [atcoder-test-usage.md](./atcoder-test-usage.md)
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

詳細は [fixtures/README.md](../../fixtures/README.md)。

## 実行すべきタイミング

リファクタリングや機能追加で以下を触ったときに走らせる:

- `cmd/atcoder/` — 引数パース・dispatch・factory
- `internal/runner/` — プロセス実行
- `internal/testexec/` — `test` の orchestration・judge・meta・fetch
- `internal/runexec/` — `run` の orchestration
- `internal/cachepath/` — キャッシュ配置の解決
- `internal/ui/` — Reporter 実装・スタイル

逆に、`docs/` や `exercise/`/`abc/`/`adt/`/`dp/` 等の練習問題のみの変更では走らせる必要はない。

## fixture を追加するには

新しい振る舞い (例: 新フラグや新言語サポート) を追加したら、対応する fixture をひと組追加する:

1. `fixtures/fixture_<name>.py` を作成
2. `fixtures/fixture_<name>/meta.toml` を作成 (`contest = "fixture"`, `task = "fixture_<name>"`, `time_limit_ms`, `fetched_at` を埋める)
3. `fixtures/fixture_<name>/tests/01.in` / `01.out` を作成
4. `fixtures/run.sh` の `run_case` 行を追加 (expected exit code を含めて)
5. `fixtures/README.md` と本ドキュメントの fixture 一覧に追記

`meta.toml` の `url` は空文字でよい (フィクスチャは AtCoder にアクセスしない)。

## 制約と非対象

- 表示の見た目 (色や配置) はスモークテストで検証できない。`CLICOLOR_FORCE=1` で手動目視を推奨。
- `atcoder run --stdin -` の **chat TUI** は TTY を要するため `fixtures/run.sh` ではカバーされない (スクリプト内の interactive ケースは非TTY passthrough のみ試験する)。手動確認は端末から `atcoder run fixture --task interactive --stdin -` を直接叩く。
- 並列実行や HTTP fetch の挙動は対象外 (fixtures は事前生成済みのキャッシュを使う想定)。
- Python 以外の言語の Runner はまだ存在しないので未対象。追加されたら言語ごとの fixture を増やす。
