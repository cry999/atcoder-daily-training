# `layout` を `mode` (contest / exercise) に再設計する 要件定義

## 概要

解答ファイルの配置規約を選ぶ仕組みを、現行の **`layout` (`auto` / `abc` / `exercise`)** から
**`mode` (`contest` / `exercise`)** に作り直す。両モードとも **contest ID を指定して実行**でき、
違いは「解答ファイルをどこに置くか」と「stats 集計に載るか」だけになる。

- `contest` モード: `<prefix>/<contest_num>/<letter>.py` (例 `abc457 --task d` → `abc/457/d.py`、
  `arc212 --task c` → `arc/212/c.py`)。現行 `abc` レイアウトを **prefix 汎用**に一般化する。
- `exercise` モード: `exercise/YYYY/MM/DD/<task_id>.py` (現行 `exercise` レイアウトのまま)。

`auto` は廃止する。両モードとも contest ID を受け取る以上、prefix からモードを一意に決められない
(同じ `abc457` が両モードの正当な入力)。既定は **config の `mode` キー**に固定し、未設定時は
`exercise` にフォールバックする。あわせて **record / stats の集計母体を両モード横断**に広げ、
contest モードで解いた問題も solve-stat を持てば stats に載るようにする。

これは要件 [002](002-exercise-abc-layout.md) (ABC レイアウト) / [017](017-config-layout-default.md)
(既定レイアウト) を **置き換える** 破壊的リネーム。決定記録は
[ADR 0010](../decisions/0010-mode-rename-contest-exercise.md)、stats 母体の変更は
[ADR 0002 の追補](../decisions/0002-stats-readonly-exercise-tree.md)。

## 背景・目的

- 現行 `--layout` の値 `abc` は「ABC コンテストのディレクトリ配置」を指すが、名前が **特定 prefix**
  と癒着していて概念が伝わりづらい。`arc` / `agc` を置くつもりでも `--layout abc` と打つことになり、
  「これは配置規約なのか prefix なのか」が曖昧。実際 `abc` レイアウトは `abc<NNN>` 以外を弾く
  (`internal/layout` の `ABC` 実装) ため、arc/agc は現状 contest 配置に載せられない。
- `auto` は prefix でモードを推測するが、練習も本番も同じ contest ID を入力にするようになった今、
  prefix はモードの手掛かりにならない。「ある期間ずっと exercise で練習」「本番中はずっと contest」
  という**運用単位でモードは固定**したいので、都度の自動推測より config 既定が素直。
- 「配置規約」という抽象は本質的に **contest ツリー vs 練習ツリー**の 2 択。これを `mode`
  (`contest`/`exercise`) と名付け直せば、CLI 表面も内部語彙も一貫する。
- 記録 (record) は既にモード解決経由で解答パスを引くので、contest モードの解答にも solve-stat を
  書ける。ところが stats は `exercise/` ツリーしか見ない (ADR 0002) ため、本番/コンテスト配置で
  練習した分が集計に載らない。両モードで record できるなら stats も両モードを数えたい。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 概念 | `layout {auto,abc,exercise}` → `mode {contest,exercise}` に**リネーム + 一般化** | `adt` 等の別配置を第 3 の mode として追加 |
| contest モードの対象 prefix | contest ID の prefix から汎用導出 (`abc`/`arc`/`agc`/… → `<prefix>/<num>/`) | 不規則命名ツリー (`awc/NNNN-beta`) の吸収 |
| 既定/自動判定 | config `mode` キー + `$ATCODER_MODE` + `--mode` フラグ。`auto` は**廃止** | リポジトリローカル設定・プロファイル |
| 対象コマンド | `test` (=run 統合済) / `start` / `record`(+サブ) / `new` / chat `:record` の配置解決 | — |
| record | 両モードの解答ファイルに solve-stat 読み書き (現行踏襲、モード名だけ変更) | — |
| stats 集計母体 | `exercise/` (存在=1問) + **contest ツリーの solve-stat 保有ファイル** | contest ツリーの全解答を無条件カウント |
| 後方互換 | **clean break** (`--layout`/`abc`/`auto`/`ATCODER_LAYOUT`/config `layout` は廃止) | — |
| 対象言語 | Python (`.py`、solve-stat は `#` コメント) | 他言語 |

### 境界: 本命 abc-todo E の `live/practice` と混同しない

`docs/tools/abc-todo.md` の Phase 2 「E. 本番 vs 練習モード判定」は、**コンテスト時刻範囲による
本番 (live) / 練習 (practice) の挙動ガード**を `--mode=live/practice` として構想していた。本要件の
`mode` (`contest`/`exercise`) は **解答ファイルの配置**という別軸で、時刻判定とは無関係。用語衝突を
避けるため、**`mode` は配置軸に確定**し、E の live/practice 軸は別名 (例 `--phase live|practice`
または `--live`) にリネームする (abc-todo E を更新)。2 つの軸は直交する: 「exercise モードで本番中」
「contest モードで後追い練習」もあり得る。

### 他コマンドとの分担

- 配置解決は `internal/mode` (本要件でリネーム)。ディレクトリ作成・空ファイル生成は `new` /
  `start` のスケルトン方針 (既存温存) のまま。
- サンプル fetch・判定・watch は `test` (001/004)。本要件は配置解決層のみ差し替える。
- solve-stat の読み書きは `internal/solvestat` (061)。本要件はモード名の変更に追従するのみで、
  書き込みロジックは変えない。

## ディレクトリ構造 / 命名規約

| mode | 解答ファイル | 例 |
|---|---|---|
| `contest` | `<prefix>/<contest_num>/<letter>.py` | `abc/457/d.py`, `arc/212/c.py` |
| `exercise` | `exercise/YYYY/MM/DD/<task_id>.py` | `exercise/2026/07/06/abc457_d.py` |

- **contest_num は contest ID の数字部分をそのまま使う** (再ゼロ埋め・ゼロ除去をしない)。
  `abc457`→`457`、`abc099`→`099`。既存 repo の `abc/457/`・`arc/212/` はこの規則で一致する。
- **prefix 汎用導出**: contest ID を `<英字 1 文字以上><数字 1 文字以上>` に分割し、英字部を
  ツリー名、数字部をコンテスト番号ディレクトリにする。`abc`/`arc`/`agc`/`ahc` を同じ規則でカバー。
- **不規則命名は対象外**: `awc/` は既存 dir が `0001-beta` 等 (ゼロ埋め + サフィックス) で汎用導出
  では一致しない。`adt/` も日付バケツで別配置。これらは contest モードの自動導出から外れる
  (exercise モードで置くか、手動配置)。将来 mode を足して吸収する余地は残す。
- キャッシュキー (`<contest_id>/<task_id>`) と task_id 展開はモード非依存で不変 (002 と同じ)。
  同じ `abc457_d` を contest / exercise どちらから fetch しても同一キャッシュを共有する。

### 用語

- **mode**: 解答ファイルの配置規約。`contest` / `exercise` の 2 値。
- **contest_id** (`abc457`) / **contest_num** (`457`) / **task_id** (`abc457_d`) / **letter** (`d`)
  は既存要件 (002) に準拠。
- **prefix**: contest_id の英字部分 (`abc457`→`abc`)。contest モードのツリー名。record の category と同一。

## CLI 仕様

### `--mode` フラグ (共通)

`test` / `start` / `record`(+サブ) が `--mode <contest|exercise>` を受け取る (旧 `--layout` を置換)。

| 値 | 解答ファイルの解決規則 |
|---|---|
| `contest` | `<prefix>/<contest_num>/<letter>.py` |
| `exercise` | `exercise/YYYY/MM/DD/<task_id>.py` |
| (省略) | env → config → `exercise` の順で既定を引く (下記 precedence) |

`auto` は受け付けない (廃止)。不正値はどの出所でも "unknown mode" で **exit 2**。

### 既定の解決順 (precedence)

| 優先 | 出所 | 値の例 |
|---|---|---|
| 1 | `--mode` フラグ (指定時) | `--mode contest` |
| 2 | 環境変数 `$ATCODER_MODE` (空でなければ) | `ATCODER_MODE=contest` |
| 3 | 設定ファイル `config.toml` の `mode` | `mode = "contest"` |
| 4 | 既定 (`exercise`) | — |

- 旧 `auto` の prefix 検出 (`layout.Detect`) は**削除**する。段 4 のハード既定は `exercise`。
- 純粋関数 `mode.Resolve(flag, env, cfg)` に集約する (旧 `layout.Resolve` から contestID 引数と
  auto 分岐を落とす)。

### config

```
$ atcoder config set mode contest
set mode = contest  (/home/user/.config/atcoder-daily-training/config.toml)

$ atcoder config get mode
contest              # 未設定時は既定の "exercise" を表示

$ atcoder config show
mode = contest
test.side_by_side = false
```

- `config.toml` はトップレベル `mode` キー (旧 `layout` を置換)。enum 候補は `contest`/`exercise`。
- 不正値は "invalid config value" で **exit 2** (書き込まない)。

```toml
# $XDG_CONFIG_HOME/atcoder-daily-training/config.toml
mode = "contest"      # ← 旧 layout キーを置換 (test/start/record 横断の既定)

[test]
side_by_side = true
```

### `atcoder new`

`new` のコンテスト一括準備 (003) も mode リネームに合わせる。`abc` というモード語を捨て、
**contest ID を直接受ける**形にする (contest モードは prefix を ID から導出できるため語が不要)。

```
atcoder new                         # 既存: exercise/YYYY/MM/DD/ を作成 (変更なし)
atcoder new <contest> [flags]       # 変更: コンテスト一括準備 (旧 `new abc <contest>`)
```

- `<contest>` は `<prefix><num>` 形 (`abc457`/`arc212`)。数字部を持たない引数 (`abc` 単体等) は
  contest ID として不正で **exit 2**。
- スケルトン生成先は contest モードのパス (`<prefix>/<num>/<letter>.py`) を汎用導出。abc 固定で
  なくなり、`new arc212` で `arc/212/{a..}.py` を生成できる。
- `--refresh` / `--tasks` / `--no-skeleton` / `--no-fetch` は 003 のまま。

### 処理ステップ (`atcoder test` 側の例)

1. `--mode` をパース (デフォルト `""` = 未指定)。
2. `resolveMode(flag)` が `$ATCODER_MODE` → `config.toml` の `mode` → `exercise` の順で解決
   (`mode.Resolve`)。
3. `mode.Parse(value)` で `Mode` を得る。不正値は exit 2。
4. `m.SolutionPath(contest, task)` で解答パスを算出。contest ID が `<prefix><num>` 形でない
   (contest モード時) は exit 2。パス不在は既存どおり exit 1。

## 動作仕様

| 状況 | 挙動 |
|---|---|
| `--mode contest` 明示 | env / config を無視して contest (段 1) |
| `--mode` 省略 + `ATCODER_MODE=contest` | contest (段 2) |
| `--mode` 省略 + env 未設定 + config `mode="contest"` | contest (段 3) |
| すべて未設定 | `exercise` (段 4) |
| `ATCODER_MODE=""` (空) | 未設定扱い、段 3 へ |
| 不正な mode 値 (どの出所でも) | "unknown mode …" で exit 2 |
| contest モードで contest ID が `<prefix><num>` 形でない | "contest id must be <prefix><num>" で exit 2 |
| `config set mode <不正値>` | "invalid config value" で exit 2 (書き込まない) |

- **配置解決だけを差し替える**。fetch・判定・watch・キャッシュの挙動は不変。
- **解答ファイル非破壊**: `--refresh` はキャッシュのみ。既存解答は上書きしない (start/new)。
- 旧 `auto` の「存在すれば contest、無ければ exercise」といったフォールバックは**しない**。
  モードが決まった後の解答ファイル不在は素直にエラー (誤配置の検知を優先、002 と同方針)。

### record / stats の両モード横断

record は `resolveMode` 経由で解答パスを引くので、contest モードの解答ファイル
(`abc/457/d.py`) にも solve-stat を読み書きできる (現行 `recordTargetFor` がモード非依存に働く。
リネーム追従のみ)。これに合わせて **stats の集計母体を拡張**する:

| ツリー | カウント条件 | 日付の出所 |
|---|---|---|
| `exercise/YYYY/MM/DD/*.py` | 存在すれば 1 問 (従来どおり) | パス (`YYYY/MM/DD`) |
| contest ツリー (`abc/`/`arc/`/`agc/`/…) の `*.py` | **solve-stat ブロックを持つファイルのみ** | solve-stat の `solved_at` (無ければ `started_at`) |

- **contest ツリーは「記録した問題」だけ数える**。無条件に `abc/**/*.py` を数えると過去 30+
  コンテスト分の未記録解答が一気に混入して集計が壊れるため、solve-stat の有無をカウント境界にする。
  これにより「contest モードで record した練習」は stats に載り、レガシー解答は載らない。
- **contest ツリーの日付はパスに無い**ので solve-stat の `solved_at` を使う。solve-stat が無い/
  日付が空の contest ツリーファイルは**日付ベース統計 (ストリーク・時系列・`--week/month/year`)
  から除外**する (集計母体に入らない = カウント境界そのもの)。
- exercise ツリーは従来どおりファイル存在で数え、solve-stat があれば duration/ac/5 軸を上乗せする
  (061 のまま)。この非対称 (exercise=存在で数える / contest=記録で数える) は仕様として明記する。
- ADR 0002 の「`exercise/` ツリーのみ」の割り切りを本要件で見直す ([ADR 0002 追補](../decisions/0002-stats-readonly-exercise-tree.md))。

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/layout/` → **`internal/mode/`** | パッケージ名を `mode` にリネーム。`Layout` interface → `Mode`、`ABC` struct → `Contest` (prefix 汎用化)、`Exercise` 据え置き。`Detect` 削除、`Parse`/`Resolve`/`Names`/`Known` を mode 用に改修 |
| `internal/mode/mode_test.go` | contest 汎用導出 (abc/arc)・`Resolve` precedence (auto 無し)・不正 contest ID のテスト |
| `internal/config/config.go` | `Config.Layout` → `Config.Mode` (toml `mode`)。package doc の env 記述を `ATCODER_MODE` に |
| `internal/config/keys.go` | `fields` の `layout` エントリ → `mode` (enum `contest`/`exercise`)。候補は `mode.Names()` |
| `internal/config/keys_test.go` | `mode` の get/set/不正値/候補テストへ差し替え |
| `cmd/atcoder/flags.go` | `addLayoutFlag`→`addModeFlag` (`--mode`)、`ATCODER_LAYOUT`→`ATCODER_MODE`、`resolveLayout`→`resolveMode(flag)` (contestID 引数を落とす) |
| `cmd/atcoder/test.go` | `resolveLayout`→`resolveMode`、`lay.SolutionPath`→`m.SolutionPath` |
| `cmd/atcoder/start.go` | 同上 + ナビゲーション helper (`ShiftLetter`/`ShiftContest`/`WithContestNum`) の import パス追従 |
| `cmd/atcoder/record.go` | `buildRecordTarget`/`recordTargetFor` のモード解決追従。category 抽出は不変 |
| `cmd/atcoder/new.go` | `new abc <contest>` → `new <contest>`。固定 `layout.ABC{}` を contest モード汎用導出に。ABC 固定判定を prefix 汎用へ |
| `cmd/atcoder/adhoc.go` / chat `:record` | `SolutionPath` 呼び出しのモード追従 (層境界は不変) |
| `cmd/atcoder/gen.go` / `meta.go` | `TaskID`/`ParseTaskURL` 等の import パス追従のみ (モード非依存) |
| `internal/stats/` | 集計母体に contest ツリー走査を追加。solve-stat 保有ファイルを `solved_at` で日付付与し集計に合流。母体境界 (contest=記録のみ) を `Compute` に実装 |
| `internal/stats/*_test.go` | contest ツリー混在・solve-stat 日付・母体境界のテスト |
| `internal/complete/complete.go` | `--layout`→`--mode`、値候補 `contest`/`exercise`。`new` の位置引数 (contest) 追従 |
| `internal/complete/complete_test.go` | 期待値更新 |
| `cmd/atcoder/main.go` | usage 文字列を `--mode <contest\|exercise>` / `new <contest>` に更新 |
| `fixtures/run.sh` | `--mode` 経路・config set/get mode・precedence・contest 汎用パス (arc)・`new <contest>` スケルトンの smoke |
| `docs/tools/usage/*.md` | `test.md`/`start.md`/`record.md`/`config.md`/`new` 手引の `--layout`→`--mode` 追従 (feature フェーズで) |

### `internal/mode` パッケージの素描

```go
package mode

// Mode は解答ファイル配置規約。test/start/record はこの interface 越しに使う。
type Mode interface {
    Name() string                                        // "contest" / "exercise"
    SolutionPath(contestID, task string) (string, error) // リポジトリルートからの相対 path
}

// Contest は <prefix>/<contest_num>/<letter>.py 配置 (旧 ABC を prefix 汎用化)。
type Contest struct{}

// Exercise は exercise/YYYY/MM/DD/<task_id>.py 配置 (練習用、現行)。
type Exercise struct {
    Today time.Time // ゼロ値なら time.Now().Local()
}

// SplitContestID は contest_id を prefix + contest_num に分割する (旧 ContestNum の汎用版)。
// "abc457" → ("abc", "457", true) / "adt_2026_..." → ("", "", false)。
func SplitContestID(contestID string) (prefix, num string, ok bool)

// Parse は CLI 値 ("contest"/"exercise"/"") を Mode にする。"" は既定 (exercise) 扱い。
func Parse(name string) (Mode, error)

// Resolve は precedence (flag > env > config > exercise) で Mode を解決する。
// 返り値: (Mode, 採用値, 出所 "flag"/"env"/"config"/"default", err)。auto は無い。
func Resolve(flag, env, cfg string) (m Mode, value, source string, err error)

// Names は既知 mode 名を正規順 (contest, exercise) で返す (補完・検証の単一情報源)。
func Names() []string

// Known は mode 名が既知かを返す (config set の検証用)。
func Known(name string) bool
```

- モード非依存 helper (`TaskID` / `Letter` / `ParseTaskURL` / `IsTaskURL` / `ShiftLetter` /
  `ShiftContest` / `WithContestNum`) はそのまま `internal/mode` に残す。`ContestNum` は
  `SplitContestID` に一般化 (呼び出し側は prefix も得られる)。

## エラーハンドリング

| 状況 | 動作 | exit |
|---|---|---|
| `--mode` / env / config の不正値 (実行時) | "unknown mode …" | 2 |
| `config set mode <不正値>` | "invalid config value" | 2 |
| contest モードで contest ID が `<prefix><num>` 形でない | "contest id must be <prefix><num>" | 2 |
| `new` の引数が contest ID として不正 | usage / "contest id must be …" | 2 |
| 解答ファイル不在 (モード解決後) | 「解答ファイルが見つかりません」 | 1 |
| `config.toml` 読み取り I/O・文法エラー | "config parse error" | 2 |
| `config.toml` 書き込み失敗 | エラー表示 | 1 |

## 移行 (breaking change)

clean break を採る。後方互換の alias は設けない。

- `--layout` フラグ・`ATCODER_LAYOUT` 環境変数は**廃止** (未知フラグ扱い → exit 2)。`--mode` /
  `ATCODER_MODE` に置換する。
- config の旧 `layout` キーは**読まれなくなる** (未知キーとして無視され温存はされる)。ユーザは
  一度 `atcoder config set mode <contest|exercise>` を実行して新キーを書く。旧 `layout` キーは
  害が無いので放置でも良い (手で消してもよい)。
- 旧 `--layout abc` は `--mode contest` に、`--layout exercise` は `--mode exercise` に対応する。
  `--layout auto` に相当する自動判定は無くなるため、運用に応じて config `mode` を 1 度設定する。
- `new abc <contest>` は `new <contest>` に変わる。旧構文は「`abc` = 不正な contest ID」で exit 2。

## 非機能要件

- **既存キャッシュ非破壊**: `<contest_id>/<task_id>` 階層・meta・tests・contest.toml は不変。
  モードは配置解決のみを変える。
- **解答ファイル非破壊**: 既存解答は上書きしない (`--refresh` はキャッシュのみ)。
- **決定的・テスト可能**: precedence は `mode.Resolve` 純粋関数、contest 汎用導出は
  `SplitContestID`、stats 母体境界は `Compute` に閉じ、いずれもユニットテスト。
- **単一情報源**: 既知 mode 名は `mode.Names()` に集約し、config 検証・補完候補も参照する。
- **前方互換**: 将来 `adt` 等を第 3 の mode として `Names()`/`Parse` に足せば env/config/補完が
  そのまま受け付ける。live/practice 軸 (abc-todo E) は別フラグとして直交に足せる。

## 将来の拡張ポイント

- **第 3 の mode**: `adt` (`adt/<YYYY>/<MM>/<DD>/<HHMM>/<LETTER>/main.py`) や `dp` を mode として
  追加。`SplitContestID` で導出できない配置は個別 `Mode` 実装を足す (open-closed)。
- **contest ツリー全走査の stats**: 記録の有無に関わらず contest ツリーを数えるオプト
  (`stats --all-trees` 等)。日付は git log / mtime に頼るため別設計 (ADR 0002 の却下案)。
- **live/practice 判定 (abc-todo E)**: `contest.toml` の時刻範囲で本番ガードを効かせる軸。
  `mode` とは別フラグ (`--phase` 等) で直交に実装する。
- **不規則ツリーの吸収**: `awc/NNNN-beta` のような命名を contest モードで解決するマッピング表。

## 関連ドキュメント

- [ADR 0010](../decisions/0010-mode-rename-contest-exercise.md) (本再設計の決定記録。002/017 を Supersede)
- [ADR 0002 追補](../decisions/0002-stats-readonly-exercise-tree.md) (stats 母体を両モードへ拡張)
- [002-exercise-abc-layout.md](002-exercise-abc-layout.md) / [017-config-layout-default.md](017-config-layout-default.md) (本要件が置き換える旧レイアウト仕様)
- [003-exercise-abc-contest-meta.md](003-exercise-abc-contest-meta.md) (`new <contest>` 一括準備の基盤)
- [005-exercise-stats.md](005-exercise-stats.md) / [061-solve-record-stats.md](061-solve-record-stats.md) (stats / record の基盤)
- [018-start-command.md](018-start-command.md) (start の配置解決) / [064](064-chat-record.md) / [066](066-record-edit.md) (chat `:record`)
- `docs/tools/abc-todo.md` の E (live/practice 軸。用語衝突回避のためリネーム)
