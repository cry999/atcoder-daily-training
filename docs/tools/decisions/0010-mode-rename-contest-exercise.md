# ADR 0010: 配置規約を `layout {auto,abc,exercise}` から `mode {contest,exercise}` に再設計する

- ステータス: Accepted
- 日付: 2026-07-06
- 実装: 設計のみ ([requirements/070-contest-exercise-mode.md](../requirements/070-contest-exercise-mode.md))
- Supersedes: [ADR (相当) の 002](../requirements/002-exercise-abc-layout.md) / [017](../requirements/017-config-layout-default.md) のレイアウト概念
- 関連: [ADR 0002 追補](0002-stats-readonly-exercise-tree.md) (stats 母体の拡張) / [ADR 0003](0003-user-config-xdg-toml.md) (config)

## コンテキスト

解答ファイルの配置は `--layout {auto,abc,exercise}` (要件 002/017) で選んでいた。運用してみると:

- 値 `abc` が「ABC のディレクトリ配置」という**特定 prefix と癒着**しており、配置規約なのか
  コンテスト種別なのか曖昧。実装 (`internal/layout` の `ABC`) は `abc<NNN>` 以外を弾くので、
  同形の `arc/<num>/<letter>.py` すら contest 配置に載せられなかった。
- `auto` は contest ID の prefix でレイアウトを推測するが、練習も本番も**同じ contest ID** を
  入力にするため prefix はモードの手掛かりにならない (同じ `abc457` が両配置の正当な入力)。
- 「配置規約」の本質は **contest ツリー vs 練習ツリー**の 2 択で、`abc`/`exercise`/`auto` の 3 値は
  その本質を覆い隠していた。

## 決定

配置規約を **`mode` (`contest` / `exercise`)** に作り直す (要件 070)。

- **contest モードを prefix 汎用化**: 解答パスを `<prefix>/<contest_num>/<letter>.py` とし、
  contest ID を `<英字><数字>` に分割して導出する (`abc457`→`abc/457/`, `arc212`→`arc/212/`)。
  旧 `ABC` struct を `Contest` struct に一般化。
- **`auto` を廃止**: 既定は `--mode` > `$ATCODER_MODE` > config `mode` > `exercise` の precedence で
  決める。prefix 自動判定 (`Detect`) は削除。運用単位でモードを固定する使い方に合わせる。
- **clean break**: `--layout`/`ATCODER_LAYOUT`/config `layout`/`new abc <contest>` は廃止し、
  `--mode`/`ATCODER_MODE`/config `mode`/`new <contest>` に置換。個人リポジトリのため alias は
  設けず、一度 `config set mode …` すれば済む。
- **record / stats を両モード横断**に (ADR 0002 追補)。contest モードで record した問題も stats に
  載る。ただし contest ツリーは無条件走査すると過去解答が混入するため、**solve-stat 保有ファイル
  のみ**を母体境界とし、日付は `solved_at` から取る。
- パッケージ `internal/layout` → `internal/mode` にリネーム。モード非依存 helper (`TaskID` /
  `Letter` / `ShiftLetter` / `ShiftContest` / `WithContestNum` 等) は据え置き、`ContestNum` は
  `SplitContestID` に一般化。

## 結果

- CLI 表面と内部語彙が「配置 = contest / exercise」で一貫する。arc/agc も contest モードに載る。
- 自動判定が無くなり、モード決定が config 1 か所に集約されて予測しやすくなる。
- 既存のフラグ/env/config/`new abc` を使うスクリプトは壊れる (clean break、既知の割り切り)。
- `awc/NNNN-beta` のような不規則命名ツリーは汎用導出から外れる (将来 mode 追加で吸収)。
- live/practice 判定 (abc-todo E) は `mode` とは別軸として直交させる (用語衝突を回避)。

## 却下した代替案

- **`--layout` 名を残し値だけ `contest`/`exercise` に**: フラグ名が概念とずれ続ける。CLI 表面の
  分かりにくさが主因なので、名前ごと `mode` に刷新した。
- **`abc`/`auto` を deprecated alias として残す**: 個人リポジトリで利用者が 1 人のため、二重の
  語彙を保守する価値が低い。clean break で語彙を 1 つにした。
- **`auto` を「ファイル存在で contest/exercise を判定」に作り替え**: 曖昧さが残り、誤配置の検知が
  鈍る。運用単位で固定する config 既定の方が意図に合う。
- **stats で contest ツリーを無条件カウント**: 過去 30+ コンテスト分の未記録解答が一気に混入して
  集計が壊れる。solve-stat 保有を母体境界にして「記録した練習」だけ載せた。
