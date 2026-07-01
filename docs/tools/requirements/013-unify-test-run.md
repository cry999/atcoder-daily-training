# `test` / `run` 統一 要件定義

## 概要

`atcoder test` (サンプル判定) と `atcoder run` (任意入力での ad-hoc 実行) の使い分けが摩擦になっているため、**入口を `atcoder test` 1 つに統一**する。既定はサンプル判定 (従来の `test`)、`--in` / `--out` / `--interactive` を**明示したときだけ** ad-hoc / 対話モード (従来の `run`) に切り替わる。`atcoder run` サブコマンドは**削除**する。

内部エンジン (`internal/testexec` = サンプル判定、`internal/runexec` = ad-hoc / 対話) は **2 本のまま据え置き**、`cmd/atcoder/test.go` の入口でフラグを見て振り分けるだけにする。CLI の表面だけを 1 つにまとめる変更で、各モードの実行ロジック・表示は従来と同一。

設計判断の記録は [ADR 0005](../decisions/0005-unify-test-run-into-test.md)。

## 背景・目的

- `test` と `run` の本質的な違いは名前 (テスト/実行) ではなく **入力ソース**: サンプル群 (キャッシュ, N 件, 必ず判定) か、自前の stdin/ファイル (1 件, `--out` 指定時のみ判定) か。「どっちのコマンドだったか」を毎回考えさせられるのが摩擦。
- 境界は既に曖昧 (`test --case 01` は実質 1 件、`run --out` は実質 1 件判定)。共通フラグ (`--task`/`--layout`/`-d`/`-v`/`--timeout`/`--tolerance`) も多い。
- 内部の `testexec` / `runexec` の分離はきれいなので残し、**変えるのは CLI の表面だけ**にする。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 入口コマンド | `atcoder test` に一本化 | — |
| `atcoder run` | **削除** (dispatch・usage から除去) | — |
| 既定モード | サンプル判定 (従来 test) | — |
| ad-hoc / 対話への切替 | `--in` / `--out` / `--interactive` を**明示**したとき | — |
| stdin 自動判定 | **しない** (暗黙切替は事故の元)。stdin から ad-hoc は `--in -` を明示 | パイプ検知の opt-in 化 |
| 内部エンジン | `testexec` / `runexec` 2 本維持 | 必要が出たら統合検討 |
| `--watch` | サンプルモードのみ (従来どおり) | ad-hoc モードの watch |

## モード判定

`atcoder test` 実行時、フラグから 1 つのモードに解決する。

| モード | トリガ | エンジン |
|---|---|---|
| **サンプル判定** (既定) | `--in` / `--out` / `--interactive` のいずれも無し | `testexec.Run` |
| **ad-hoc 実行** | `--in <path>` / `--in -` / `--out <path>` のいずれか (かつ `--interactive` 無し) | `runexec.Run` |
| **対話** | `--interactive` (`-I`) | `runexec.Run` (interactive) |

- 既定が常にサンプル判定なので、**stdin がパイプされていてもモードは変わらない**。stdin を ad-hoc 入力にしたいときは `--in -` を明示する (従来の `run` で `--in` 省略=stdin だった挙動からの変更点)。
- `--out` のみ指定 (=`--in` 無し) は ad-hoc 判定モードで、入力は stdin から読む (`runexec` の従来挙動と同じ)。

### フラグの所属と排他

| フラグ | 所属モード |
|---|---|
| `--refresh` / `--case`(`-c`) / `--jobs`(`-j`) / `--watch`(`-w`) / `--side-by-side`(`-s`) | サンプル判定のみ |
| `--in`(`-i`) / `--out`(`-o`) / `--interactive`(`-I`) | ad-hoc / 対話のみ |
| `--task` / `--layout` / `--timeout` / `--tolerance` / `-v` / `-d` | 共通 |

- **サンプル専用フラグと ad-hoc トリガフラグを同時に明示したら exit 2** (例: `--in foo -c 01`)。「どちらのモードか」が曖昧になるのを禁じる。
- 判定は**明示的に指定されたフラグ** (`flag.FlagSet.Visit`) を基準にする。`--side-by-side` は config で既定 true になりうるため、値ではなく「コマンドラインで明示したか」で排他を見る。
- 対話モードの内部排他は従来どおり: `--interactive` は `--out` とも、ファイル指定の `--in <path>` とも併用不可 (exit 2)。`--in -` は可。

## CLI 仕様

```
atcoder test <contest> --task <task>
    [サンプル判定: --refresh | -c <N[,M,...]> | -j <n> | -w | -s]
    [ad-hoc:       --in <path>|- | --out <path>]
    [対話:         --interactive]
    [共通:         -v | -d | --timeout <dur> | --tolerance <eps> | --layout <auto|abc|exercise>]
```

| フラグ | モード | 説明 |
|---|---|---|
| `<contest>` / `--task` | 共通 | 従来どおり (短縮形 `--task d` → `<contest>_d`) |
| `--refresh` | サンプル | サンプルを再取得して上書き |
| `--case` / `-c` | サンプル | 指定ケースのみ実行 |
| `--jobs` / `-j` | サンプル | 並列ワーカー数 (0=CPU 数) |
| `--watch` / `-w` | サンプル | 保存検知で再実行 (TTY 必須) |
| `--side-by-side` / `-s` | サンプル | diff を左右 2 カラム表示 |
| `--in` / `-i` | ad-hoc | 入力ファイル。`-` で stdin。指定した時点で ad-hoc モード |
| `--out` / `-o` | ad-hoc | 期待出力ファイル。stdout を突合せ判定 |
| `--interactive` / `-I` | 対話 | 子の stdin/stdout を親に直結 (TTY なら chat TUI) |
| `--timeout` | 共通 | 制限時間の上書き |
| `--tolerance` | 共通 | float 比較の許容誤差 (サンプル判定 / `--out` 判定) |
| `-v` / `--verbose` | 共通 | 入力も表示 (サンプルでは各ケースの I/O) |
| `-d` / `--debug` | 共通 | `DEBUG=1` を渡し `[DEBUG]` 行を特別扱い |
| `--layout` | 共通 | 解答ファイル配置規約 |

### 処理ステップ

1. contest / `--task` を解決 (従来どおり)。
2. フラグをパースし、`Visit` で**明示指定されたフラグ集合**を得る。
3. `adHoc = --interactive || --in 指定 || --out 指定`。
4. `adHoc` かつサンプル専用フラグが明示されていれば exit 2。
5. `adHoc` なら: 対話の内部排他チェック → `runexec.Run(...)`。
6. そうでなければ: サンプル判定。`--watch` 指定時は watch ループ、それ以外は `testexec.Run(...)`。

### 出力イメージ

サンプル判定 (既定) ・ad-hoc・対話のいずれも**従来の `test` / `run` と同一の出力**。

```
# サンプル判定 (既定)
$ atcoder test abc325 --task d
abc325_d  contest=abc325  time_limit=3000ms  tolerance=1e-6  tests=3
[01]  PASS  27 ms
...
Result: 3/3 PASS

# ad-hoc (自前入力で実行、判定なし)
$ atcoder test abc325 --task d --in my_case.txt
abc325_d  contest=abc325  time_limit=3000ms  (ad-hoc stdin)
  OK    27 ms
       output:
         14

# stdin から ad-hoc (--in - を明示)
$ echo "5" | atcoder test abc325 --task d --in -

# 対話
$ atcoder test abc999 --task a --interactive
```

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `atcoder test <c> --task d` (ad-hoc フラグ無し) | サンプル判定 (従来 test と同一) |
| `atcoder test <c> --task d --in foo.txt` | ad-hoc 実行 (従来 `run --in foo.txt`) |
| `atcoder test <c> --task d --in -` (or パイプ) | stdin から ad-hoc batch |
| `atcoder test <c> --task d --out exp.txt` | stdin を読み exp.txt と判定 |
| `atcoder test <c> --task d --interactive` | 対話 (TTY=chat TUI / 非TTY=passthrough) |
| `atcoder test <c> --task d --in foo -c 01` | exit 2 (モード混在) |
| `atcoder test <c> --task d --interactive --out e` | exit 2 (対話と判定の併用不可) |
| `atcoder run ...` | **未知サブコマンド → usage → exit 2** (run は削除済み) |
| stdin をパイプ + ad-hoc フラグ無し | サンプル判定 (stdin は無視。暗黙 ad-hoc にしない) |

- **既存非破壊 (各モード内)**: サンプル判定・ad-hoc・対話の各挙動・出力・exit code は従来と同一。`testexec` / `runexec` は無改修。
- **後方互換の破壊点 (明示)**:
  1. `atcoder run` 削除 → `atcoder test --in/--out/--interactive` へ移行。
  2. 「`run` で `--in` 省略=stdin」→ `test` では `--in -` を明示 (省略時はサンプル判定)。
- 解答ファイルには触れない (`--refresh` はキャッシュのみ)。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `cmd/atcoder/test.go` | ad-hoc/対話フラグ (`--in`/`--out`/`--interactive`) を追加。`Visit` でモード判定 + 排他チェック。ad-hoc なら `runAdHoc` へ委譲 |
| `cmd/atcoder/run.go` | **削除**。`runChat` / `selectRunExecutor` と ad-hoc 呼び出しを `cmd/atcoder/adhoc.go` へ移設 |
| 新規 `cmd/atcoder/adhoc.go` | `runAdHoc(...)` (runexec.Run 結線) + `runChat` + `selectRunExecutor` |
| `cmd/atcoder/main.go` | `case "run"` と run の usage 行を削除。`test` の usage を統一版に更新 |
| `internal/complete/complete.go` | `subcommandCands` から `run` 削除。`subFlags["test"]` に `--in`/`--out`/`--interactive`(`-I`) を追加し `subFlags["run"]` を削除。`takesContest`/位置引数判定から `run` を除去 |
| `internal/complete/complete_test.go` | `run` を使うケースを `test` に書き換え |
| `fixtures/run.sh` | `run ...` ケースを `test ... --in/--out/--interactive` に変換。`run` 削除 (exit 2)・モード混在 (exit 2) の smoke 追加。「`--in` 省略=stdin」ケースは `--in -` に変更 |
| `docs/tools/usage/test.md` | ad-hoc / 対話 / モード表を追記 (run-usage の内容を統合)。run-usage への壊れリンクを修正 |
| `docs/tools/atcoder-run-usage.md` | **削除** (内容は test-usage に統合) |
| `docs/tools/atcoder-test-architecture.md` | `runexec` は「`test` の ad-hoc モードの実装」と書き換え。`run` サブコマンド記述を更新 |
| `docs/tools/requirements/002-*.md` 等の run-usage リンク | 壊れリンクを test-usage へ張り替え (本文の歴史記述は据え置き) |
| 新規 `docs/tools/decisions/0005-*.md` | 統一の決定記録 (ADR) |

### `runAdHoc` の素描 (cmd/atcoder/adhoc.go)

```go
// runAdHoc は test の ad-hoc / 対話モード。runexec.Run へ結線する (run コマンドの
// 中身を移設したもの)。対話と --out / ファイル --in の併用は exit 2。
func runAdHoc(contest, task string, lay layout.Layout, inFile, outFile string,
    interactive, debug, verbose bool, timeout time.Duration, tolerance float64) (int, error)
```

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `--task` 欠落 | "--task is required" | 2 |
| 不明フラグ / レイアウト不正 | usage / "unknown layout" | 2 |
| サンプル専用フラグ + ad-hoc トリガを併用 | "X cannot be combined with --in/--out/--interactive" | 2 |
| `--interactive` + `--out` / ファイル `--in` | 従来の run と同じメッセージ | 2 |
| `--watch` で非 TTY | "--watch requires a terminal" | 2 |
| サンプル FAIL/TLE/RE / ad-hoc TLE/RE / fetch 失敗 | 各エンジンの従来挙動 | 1 |
| 正常 (全 PASS / OK) | — | 0 |
| `atcoder run ...` | usage | 2 |

## 非機能要件

- **各モード内は完全な既存非破壊**: `testexec` / `runexec` / `ui` / `runner` は無改修。差し替えるのは入口の結線のみ。
- **明示優先・魔法なし**: モードは明示フラグで決まる。stdin の有無で挙動が変わらない (予測可能性)。
- **共通フラグの一貫**: 直近の共有化 (`addTaskFlag`/`addLayoutFlag`) をそのまま使う。
- **fixtures で固定**: モード判定・排他 (exit 2)・`run` 削除を smoke で assert。

## 将来の拡張ポイント

- ad-hoc モードの `--watch` (保存検知で再実行)。
- `--out` 判定での side-by-side diff 表示。
- `testexec` / `runexec` の内部統合 (現状は分離維持)。

## 用語

- **サンプル判定モード**: DL 済みサンプル群に対し PASS/FAIL を出す既定モード (従来 `test`)。
- **ad-hoc モード**: 自前の stdin/ファイルで 1 回実行し出力を見る (従来 `run`)。`--out` 指定時のみ判定。
- **対話モード**: 子プロセスと live 対話 (従来 `run --interactive`)。
- (`contest_id` / `task_id` / `letter` / `layout` は既存要件に準拠)

## 関連ドキュメント

- [ADR 0005](../decisions/0005-unify-test-run-into-test.md) (統一の決定記録)
- `docs/tools/usage/test.md` (統一後の利用手引)
- `docs/tools/atcoder-test-architecture.md` (testexec / runexec の内部設計)
- `docs/tools/requirements/001-exercise-test.md` (test の基盤要件)
- `docs/tools/requirements/004-exercise-test-watch.md` (watch モード)
