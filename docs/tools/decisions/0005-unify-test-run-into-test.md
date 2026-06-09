# ADR 0005: `test` / `run` を `test` 1 コマンドに統一する

- ステータス: Accepted
- 日付: 2026-06-09
- 要件: [requirements/013-unify-test-run.md](../requirements/013-unify-test-run.md)
- 関連: [0001](0001-test-watch-mtime-polling.md) (watch) / [atcoder-test-usage.md](../atcoder-test-usage.md)

## コンテキスト

`atcoder test` (サンプル群との突合せ判定) と `atcoder run` (任意入力での ad-hoc 実行 / 対話) は、本質的には **入力ソースの違い** でしかない。にもかかわらず「どっちのコマンドだったか」を毎回選ばされるのが摩擦になっていた。境界も既に曖昧で (`test --case 01` は実質 1 件、`run --out` は実質 1 件判定)、共通フラグ (`--task`/`--layout`/`-d`/`-v`/`--timeout`/`--tolerance`) も多い。

## 決定

入口を **`atcoder test` 1 つに統一**し、`atcoder run` を削除する。

- **既定はサンプル判定** (従来 `test`)。`--in` / `--out` / `--interactive` を**明示したときだけ** ad-hoc / 対話モード (従来 `run`) に切り替わる。
- **stdin の有無でモードを変えない (魔法なし)**。stdin から ad-hoc 入力したいときは `--in -` を明示する。既定が常にサンプル判定になり、挙動が予測可能。
- **内部エンジンは 2 本のまま** (`internal/testexec` = 判定、`internal/runexec` = ad-hoc/対話)。`cmd/atcoder/test.go` の入口でフラグを見て振り分けるだけ。各モードの実行ロジック・表示・exit code は従来と同一。
- サンプル専用フラグ (`--refresh`/`-c`/`-j`/`-w`/`-s`) と ad-hoc トリガ (`--in`/`--out`/`--interactive`) の**併用は exit 2** (モードの曖昧化を禁止)。判定は `flag.Visit` による「明示指定されたフラグ」基準 (`-s` は config 既定 true になりうるため)。

## 代替案 (却下)

- **`run` を正にする**: 「走らせる」の一般動詞で名前の据わりは良いが、見出し価値は「サンプルに通ったか=判定」なので `test` を正にした。
- **両名を対等エイリアスにする**: 「どっち?」は消えるが名前が 2 つ残り、補完・docs も二重。1 つに絞る方が学習面が単純。
- **`run` を deprecated エイリアスで一定期間残す**: 移行は穏やかだが、利用者は事実上 1 人で乗り換えが速いため、即削除を選択 (履歴・複雑さを残さない)。
- **stdin パイプを検知して自動 ad-hoc**: タイプ量は減るが、パイプの有無で挙動が変わる暗黙性が事故の元。明示フラグに倒した。
- **`testexec` / `runexec` を内部統合**: CLI 統一に内部統合は不要。分離は健全なので据え置き、表面だけ 1 つにした。

## 結果

- 「どっちのコマンド?」という選択が消え、内部の良い分離は保てる。
- 破壊的変更が 2 点: (1) `atcoder run` 削除 → `atcoder test --in/--out/--interactive`。(2) 「`run` で `--in` 省略=stdin」→ `test` では `--in -` を明示 (省略時はサンプル判定)。利用者が少なく移行容易なため許容。
- `atcoder test` の `--help` がモード分の情報を持つため厚くなる。usage にモード表を置いて緩和。
