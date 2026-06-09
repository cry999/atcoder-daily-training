# `atcoder test` watch モード 要件定義

## 概要

`atcoder test` に **watch モード** (`--watch` / `-w`) を足し、起動したまま解答ファイルの保存を検知して**自動でテストを再実行**できるようにする。「コードを書く → ターミナルに戻って `atcoder test ...` を叩く」の往復をなくし、エディタで保存するだけでサンプル判定が回る編集ループを作る。

`docs/tools/todo.md` の「I. `test` watch モード」の要件詳細。既存の `atcoder test` (サンプル fetch / cache / judge) と、並列実行 + ライブ進捗表示 (`internal/ui` の bubbletea Reporter) の上に薄く乗せる。

## 背景・目的

- 競技中・練習中は「1 行直して保存 → サンプルを流す」を何十回も繰り返す。現状は毎回ターミナルにフォーカスを移して同じコマンドを叩く必要があり、編集リズムが切れる。
- サンプルは初回 fetch 後はキャッシュにあるため、2 回目以降の再実行はネットワーク不要で速い。再実行の起動コストはほぼプロセス起動だけで、watch ループに向いている。
- ライブ進捗表示 (ケース一覧 + プログレスバー) を既に持っているので、「保存するたびに最新結果だけが綺麗に出る」体験を低コストで作れる。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象コマンド | `atcoder test <contest> --task <task> --watch` | `atcoder run --watch` (対話/judge モードの再実行) |
| 監視対象 | **解答ファイル 1 つ** (`layout` が解決する `.py`) | サンプル (`tests/`)・include する自作ライブラリ・複数ファイル |
| 検知方式 | **mtime ポーリング** (200ms 間隔, 外部依存なし) | fsnotify 等のイベント駆動 |
| 動作環境 | **TTY 必須** (画面クリアして再描画するため) | 非 TTY 向けの追記モード |
| 再実行の表示 | 毎回画面をクリアして最新結果のみ | 実行履歴の保持・サマリの集計表示 |
| 終了 | `Ctrl+C` | `q` キー / ファイル削除検知での自動終了 |

### 監視対象を「解答ファイルのみ」にする理由

- 競プロの編集ループで変わるのはほぼ解答コードだけ。サンプルはほとんど触らない。
- サンプル (`tests/`) まで監視すると、`--refresh` や別タスクの fetch がキャッシュ dir を書き換えたときに予期しない再実行が走りうる。監視を解答ファイル 1 つに絞ると「保存 = 再実行」が直感的で誤爆しない。
- サンプルを手で直したいケースは将来の拡張余地として残す (監視パスのリスト化)。

### 検知方式を mtime ポーリングにする理由

- 見るのは単一ファイルなので、200ms 間隔の `os.Stat` 比較で十分。CPU 負荷は無視できる。
- `fsnotify` 等を足すと外部依存が増える。この repo は最小依存方針 (`go.mod` の direct dep は数個) で、単一ファイル監視のためにイベント駆動ライブラリを抱えるのは過剰。
- ポーリングはプラットフォーム差 (inotify / kqueue / ReadDirectoryChangesW) を踏まないぶん堅牢。エディタの「保存時に一旦削除して書き直す」挙動 (atomic save) でも、ファイルが再出現したタイミングで mtime 変化として拾える。

## CLI 仕様

既存 `atcoder test` にフラグを 1 つ足すだけ。他のフラグ (`-v` / `-d` / `-s` / `-c` / `--timeout` / `--tolerance` / `--layout` / `-j`) は watch 中の各実行にそのまま適用される。

```
atcoder test <contest> --task <task> [既存フラグ...] [--watch|-w]
```

| フラグ | 説明 |
|---|---|
| `--watch`, `-w` | 解答ファイルの保存を監視し、変更のたびにテストを再実行する。`Ctrl+C` で終了。TTY 必須 |

### フラグの相互作用

| 組み合わせ | 挙動 |
|---|---|
| `--watch` + `--refresh` | **初回実行のみ** `--refresh` を適用 (再 fetch)。2 回目以降はキャッシュを使う (毎保存で再 fetch して rate limit を踏むのを防ぐ) |
| `--watch` + `-c <cases>` | 監視中の各実行で指定ケースのみ流す (絞り込みを保ったまま回せる) |
| `--watch` + `-j <n>` | 各実行を n 並列で流す (既存の並列実行と同じ) |
| `--watch` (非 TTY: パイプ/リダイレクト) | exit 2。"--watch requires a terminal" |

### 処理ステップ

`atcoder test abc457 --task d --watch` 実行時:

1. **TTY 検証**: stdout が端末でなければ exit 2 (フラグ誤用)。画面クリア前提のため。
2. **監視パス解決**: `layout` で解答パス (`abc/457/d.py` 等) を求める。解決できなければ exit 2。
3. **シグナル待受**: `SIGINT` (`Ctrl+C`) を捕捉する context を張る。
4. **編集ループ** (context が生きている間くり返す):
   1. 画面をクリアし、watch ヘッダ (監視パス) を出す。
   2. `atcoder test` の 1 回分を実行する (既存 `testexec.Run`)。FAIL/RE/TLE でもループは止めない。実行時エラー (解答ファイル無し等) は表示して継続。
   3. 初回の `--refresh` は消費済みにする (以降の実行は refresh=false)。
   4. フッタ (「保存で再実行 / Ctrl+C で終了」) を出す。
   5. 解答ファイルの mtime が変わるまで待つ。`Ctrl+C` が来たら待機を抜けてループ終了。
5. **終了**: `Ctrl+C` でループを抜け、exit 0。

### 出力イメージ

```
$ atcoder test abc457 --task d --watch
▸ watch  abc/457/d.py

abc457_d  contest=abc457  time_limit=2000ms  tolerance=1e-6  tests=3

[01]  PASS   31 ms
[02]  FAIL   28 ms
       diff:
           1 - │ 42
           1 + │ 41

Result: 1/2 PASS

watching abc/457/d.py — save to re-run, Ctrl+C to quit
```

(端末では実行中はケース一覧のスピナー + プログレスバーがライブ表示され、保存するたびに画面がクリアされて上記が描き直される。)

## 動作仕様

| 項目 | 挙動 |
|---|---|
| 再実行トリガ | 解答ファイルの mtime 変化のみ。内容が同じでも mtime が変われば再実行する (保存=再実行の単純さを優先) |
| デバウンス | mtime 変化検知後、短い待機を入れて連続書き込み (エディタの複数回 write) を 1 回の再実行にまとめる |
| atomic save 対応 | 保存時にファイルが一瞬消えても、再出現時の mtime 変化で拾う。消えている瞬間に再実行はしない |
| FAIL/RE/TLE | 結果を表示してループ継続 (終了コードでは抜けない)。watch は「常駐して回し続ける」のが役割 |
| 解答ファイルが無い | その回はエラー表示 (exit はしない)。作成・保存されれば次の変化で実行される |
| 初回 `--refresh` | 1 回目だけ再 fetch。2 回目以降はキャッシュ。`--refresh` 無し時は全回キャッシュ |
| `Ctrl+C` | 実行中ならその実行を中断しつつループ終了、待機中なら即終了。どちらも exit 0 |
| 非 watch 時 | 既存挙動と完全に同一 (1 回実行して終了)。`--watch` を付けたときだけループ化 |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/test.go` | `--watch` / `-w` フラグ追加。watch 指定時は TTY 検証 → 監視パス解決 → 編集ループ (`testexec.Run` を反復呼び出し) に分岐。非 watch は従来パス |
| `cmd/atcoder/main.go` | usage 文字列に `[--watch]` を追記 |
| 新規 `internal/watch/` | 単一ファイルの mtime ポーリング監視。`Ctrl+C` (context) で抜けられる `WaitForChange` を提供 |
| `internal/ui/` | 画面クリア・watch ヘッダ / フッタの描画ヘルパーを追加 (既存 style に合わせる) |
| `fixtures/run.sh` | 非 TTY での `--watch` 拒否 (exit 2) を smoke。watch ループ自体はブロックするため fixture では回さない (下記) |
| `docs/tools/atcoder-test-usage.md` | `--watch` の説明・サンプル出力を追記 |
| `docs/tools/atcoder-test-architecture.md` | watch ループと `internal/watch` の位置づけを追記 |
| `docs/tools/todo.md` | 「I. `test` watch モード」を `✅ DONE` でマーク |

### 新規 `internal/watch/` パッケージの責務

単一ファイルの変更検知に閉じた小さな層。`testexec` / `ui` には依存しない (再利用可能に保つ)。

```go
package watch

// Watcher は 1 ファイルの mtime をポーリングして変更を検知する。
type Watcher struct { /* path, interval, debounce, last mtime */ }

// New は path を監視する Watcher を作る。基準 mtime は生成時点の値。
func New(path string, interval, debounce time.Duration) *Watcher

// WaitForChange は監視ファイルの mtime が基準から変わるまでブロックする。
// 変化を検知したら debounce 待機後に基準を更新して true を返す。
// ctx が先に done なら false を返す (Ctrl+C / 終了)。
func (w *Watcher) WaitForChange(ctx context.Context) bool
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| `--watch` だが stdout が非 TTY | "--watch requires a terminal" で exit 2 |
| 監視パスを `layout` で解決できない | exit 2 (フラグ / 引数エラー) |
| watch 中の 1 回が FAIL/RE/TLE | 結果表示のみ。ループ継続 (exit しない) |
| watch 中の 1 回が実行時エラー (解答無し等) | stderr に表示してループ継続 |
| `Ctrl+C` | ループを抜けて exit 0 (正常終了) |

- watch モードの **終了コードはループの結果に依存しない** (常駐ツールのため `Ctrl+C` = exit 0)。判定結果による exit 1 は非 watch の 1 回実行のときだけ意味を持つ。引数 / フラグ誤りの exit 2 は従来どおり。

## 非機能要件

- **既存ワークフロー非破壊**: `--watch` 無しの `atcoder test` は挙動・出力・終了コードとも一切変わらない。
- **低オーバーヘッド**: 監視は単一ファイルの 200ms ポーリング。常駐しても CPU・I/O 負荷は無視できる。
- **rate limit 配慮**: watch 中の再 fetch は初回 `--refresh` のみ。毎保存でネットワークを叩かない。
- **最小依存**: 監視に外部ライブラリを足さない (標準ライブラリの `os.Stat` ベース)。
- **解答ファイル非破壊**: watch は読むだけ。解答にも tests キャッシュにも書き込まない。

## 将来の拡張ポイント

- **監視パスのリスト化**: 解答に加えてサンプル (`tests/`) や include する自作ライブラリも監視対象にする (`Watcher` を複数パス対応に)。
- **`atcoder run --watch`**: 対話 / judge モードの再実行。watch ループを `run` 側にも展開。
- **イベント駆動への差し替え**: ポーリングがボトルネックになる規模になれば `fsnotify` に置き換え (`internal/watch` のインタフェースは維持)。
- **キー操作**: 待機中に `r` で手動再実行、`q` で終了などの簡易 TUI 操作。
- **実行履歴 / サマリ**: 直近 N 回の PASS/FAIL 推移を表示する。

## 用語

- **watch モード**: `--watch` で起動する常駐実行ループ。保存検知でテストを再実行する。
- **編集ループ**: 「実行 → 待機 → 変更検知 → 再実行」のくり返し。
- **デバウンス**: 連続した書き込みを 1 回の再実行にまとめるための短い待機。
- **atomic save**: エディタが保存時に一旦ファイルを削除 / リネームしてから書き直す挙動。
- (`contest_id` / `task_id` / `letter` / `layout` 等は 002 / 003 の要件定義に準拠)

## 関連ドキュメント

- `docs/tools/todo.md` (上位ロードマップ。「I. `test` watch モード」の要件詳細が本書)
- `docs/tools/requirements/001-exercise-test.md` (test サブコマンドの基盤要件)
- `docs/tools/atcoder-test-usage.md` (利用手引。`--watch` を追記)
- `docs/tools/atcoder-test-architecture.md` (内部設計。watch ループの位置づけを追記)
