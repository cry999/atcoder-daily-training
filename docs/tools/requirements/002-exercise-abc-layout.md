# `atcoder` ABC レイアウト対応 要件定義

## 概要

`atcoder test` / `atcoder run` の対象パスを、現在の `exercise/YYYY/MM/DD/<task>.py` だけでなく、AtCoder Beginner Contest 用の既存規約 **`abc/<contest_num>/<letter>.py`** にも拡張する。これにより本番中も同じツールで sample fetch・テスト・run 判定が回せるようになる。

`docs/tools/abc-todo.md` の MVP "A. ディレクトリ / 命名規約" の要件詳細。

## 背景・目的

- リポジトリには既に `abc/<3桁数字>/<letter>.py` (例: `abc/457/d.py`) のレイアウトで蓄積した解答が 30+ コンテスト分ある。新規ツールはこの既存資産にそのまま乗せたい。
- ABC 本番中は問題ファイルを `abc/<contest_num>/` に置き、`atcoder test` 等で素早くサンプル検証できる状態にしたい。
- 練習用 `exercise/YYYY/MM/DD/` レイアウトは引き続き使うので、両レイアウトを **同居** で扱える設計が必要。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 対象 subcommand | `atcoder test`, `atcoder run` | `atcoder commit`, `atcoder new` (B "contest prepare" で別途扱う) |
| 対象 contest プレフィックス | `abc` のみ | `arc`, `agc`, `ahc` ほか (同じレイアウトを共有できそう) |
| 対象言語 | Python のみ (`.py`) | 拡張子で判定する仕組みは既にあるので、将来の言語追加に直交 |
| 解答ファイル名 | `<letter>.py` (a〜g) | A〜Z 等の長コンテスト形式は当面想定外 |

## ディレクトリ構造

```
# 解答コード (既存資産と同じ位置)
abc/<contest_num>/
  a.py
  b.py
  c.py
  ...
  g.py

# キャッシュ (既存仕様のまま、コンテストレイアウトに依存しない)
$XDG_CACHE_HOME/atcoder-tools/<contest_id>/<task_id>/
  meta.toml
  tests/
    01.in
    01.out
    ...
```

- `<contest_num>` は **数字のみ** (例: `457`)。ディレクトリ名にも CLI 引数にも数字部分だけが現れる、というわけではなく、CLI ではフル形式 (`abc457`) を受け取る (後述)。
- キャッシュキーは引き続き AtCoder の **task ID 全体** (`abc457_d`) を使う。`abc/<contest_num>/` 配下の解答 / 練習 `exercise/YYYY/MM/DD/` 配下の解答どちらから fetch しても、同じキャッシュを共有する。

### 命名規約

| 種別 | 規約 | 例 |
|---|---|---|
| 解答ファイル (ABC) | `abc/<contest_num>/<letter>.py` | `abc/457/d.py` |
| 解答ファイル (練習) | `exercise/YYYY/MM/DD/<task_id>.py` | `exercise/2026/06/15/abc457_d.py` |
| AtCoder contest ID | `<prefix><contest_num>` | `abc457` |
| AtCoder task ID | `<contest_id>_<letter>` | `abc457_d` |
| キャッシュベース | `$XDG_CACHE_HOME/atcoder-tools/<contest_id>/<task_id>/` | `~/.cache/atcoder-tools/abc457/abc457_d/` |

`<letter>` は **小文字** で統一する (`a`〜`g`)。CLI 入力は大文字を受け付けてもよいが、内部で小文字に正規化する。

## CLI 仕様

### 共通

`atcoder test` / `atcoder run` 双方に **`--layout`** フラグを追加する。

| 値 | 解答ファイルの解決規則 |
|---|---|
| `auto` (default) | contest 引数のプレフィックスから自動判定: `abc<NNN>` なら `abc` レイアウト、それ以外は `exercise` レイアウト (= 当日 dir) |
| `abc` | `abc/<contest_num>/<letter>.py` を解答ファイルとする |
| `exercise` | 現状と同じ: `exercise/YYYY/MM/DD/<task_id>.py` |

省略時 = `auto`。これにより `atcoder test abc457 --task d` だけで `abc/457/d.py` を解決でき、明示的な `--layout` が必要なケースは「contest プレフィックスが abc だが当日 dir に置きたい」のような例外時に限る。

### `atcoder test`

```
atcoder test <contest_id> --task <letter|task_id> [--layout <auto|abc|exercise>] [-v] [-d] [-s] [-c <N[,...]>] [--refresh] [--timeout <dur>] [--tolerance <eps>]
```

| 引数 / フラグ | 新規 / 変更 | 説明 |
|---|---|---|
| `<contest_id>` | 既存 | AtCoder の contest ID。`abc457` のフル形式で受け取る (数字のみは不可) |
| `--task <letter\|task_id>` | 既存 | 短縮形 `d` は `abc457_d` に展開済み (既存仕様)。ABC レイアウト時は letter 部分 (`d`) を解答ファイル名に使う |
| `--layout <auto\|abc\|exercise>` | **新規** | 解答ファイルの解決方式 (上表参照) |
| 既存フラグ | 変更なし | `-v`, `-d`, `-s`, `-c`, `--refresh`, `--timeout`, `--tolerance` はそのまま |

### `atcoder run`

```
atcoder run <contest_id> --task <letter|task_id> [--layout <auto|abc|exercise>] [-v] [-d] [--in <path>|-] [--out <path>] [--tolerance <eps>] [--timeout <dur>]
```

`--layout` を同じセマンティクスで追加。それ以外のフラグは現状維持。

### 短縮形 `--task d` の展開

ABC レイアウトでも展開ルールは現行 (`internal/testexec/test.go` の `task = contest + "_" + task`) と同じ。展開後の `task_id` は **AtCoder への問い合わせとキャッシュキー** に使い、**解答ファイル名の決定** はレイアウトに応じて分岐する。

- 入力 `--task d` (ABC レイアウト):
  - キャッシュキー: `abc457_d`
  - 解答ファイル: `abc/457/d.py`
- 入力 `--task abc457_d` (ABC レイアウト):
  - 末尾の letter (`d`) を切り出して `abc/457/d.py` を解答ファイルとする
- 入力 `--task d` (exercise レイアウト):
  - キャッシュキー: `abc457_d`
  - 解答ファイル: `exercise/YYYY/MM/DD/abc457_d.py`

## 動作仕様

### 解答ファイル解決アルゴリズム

1. `--layout` を決定:
   - `--layout` が明示されていればそれを使う
   - されていなければ `<contest_id>` を見る:
     - `abc<NNN>` (NNN は数字 1 文字以上) にマッチ → `abc`
     - それ以外 → `exercise`
2. `letter` を抽出:
   - `--task` が letter 単体 (1 文字、a〜g) → そのまま
   - `--task` が `<contest_id>_<letter>` 形式 → `_` の右側を letter として使う
   - どちらにも当てはまらない (例: ADT のような独立 task ID) → ABC レイアウト下ではエラー
3. 解答ファイルパス算出:
   - `abc` レイアウト: `abc/<contest_num>/<letter>.py` (contest_num は `<contest_id>` から数字部分を抽出)
   - `exercise` レイアウト: 当日 dir + `<task_id>.py` (現状通り)
4. パスが存在しなければエラー終了 (現状通り)。

### キャッシュ周りは現状維持

- meta / tests の取得・保存先は **`<contest_id>/<task_id>`** 階層のまま
- `--refresh` の挙動・ TOML 形式・ tests の番号付けは変更なし
- これにより、同じ `abc457_d` を後日 `exercise/` 配下から取り直しても、ABC 本番中に `abc/` 配下で fetch したサンプルがそのまま使える

### 既存 exercise レイアウトとの共存

- `--layout exercise` を明示すれば、ABC コンテスト ID であっても当日 dir を見る
- `--layout auto` のままでも、`abc/<contest_num>/<letter>.py` が **存在しない** ときに当日 dir にフォールバックするか? → **しない**。layout が決まった後の解答ファイル不在は素直にエラーとし、ユーザに明示してもらう (誤った dir 配置を検知しやすくするため)

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/testexec/test.go` | `Options` に `Layout` フィールドを追加。`solutionPath` 計算を layout 依存に切替 |
| `internal/runexec/runexec.go` | 同上 (`Options.Layout` を追加し、解答パス解決を layout に応じて切替) |
| `cmd/atcoder/test.go` | `--layout` フラグの追加、Options への伝搬 |
| `cmd/atcoder/run.go` | 同上 |
| 新規 `internal/layout/` | レイアウト規約を **Strategy パターン** で集約。test と run で共有 |
| `cmd/atcoder/main.go` | usage 文字列の更新 |
| `fixtures/run.sh` | 既存 fixture は exercise レイアウト前提のまま。ABC レイアウトの smoke を 1〜2 ケース追加する |

### `internal/layout/` パッケージ (新規) の責務

#### Strategy パターン

レイアウトを **インターフェース + 各実装** で表現する。test/run はインターフェース越しに `SolutionPath` を呼ぶだけで、レイアウト固有の振る舞いを知らない。ARC/AGC を将来追加するときも、既存の test/run コードに触らず実装を 1 つ加えるだけで済む (open-closed)。

```go
package layout

// Layout は解答ファイル配置規約。test/run はこの interface 越しに使う。
type Layout interface {
    Name() string                                        // "abc" / "exercise"
    SolutionPath(contestID, task string) (string, error) // リポジトリルートからの相対 path
}

// ABC は abc/<contest_num>/<letter>.py 配置。
type ABC struct{}

// Exercise は exercise/YYYY/MM/DD/<task_id>.py 配置 (練習用、現行)。
type Exercise struct {
    Today time.Time // ゼロ値なら time.Now().Local()
}

// Parse は CLI フラグ値 ("auto"/"abc"/"exercise"/"") と contest_id から Layout を選ぶ。
// "" or "auto" の場合は contest_id (例: "abc<NNN>") を見て自動判定する。
func Parse(name, contestID string) (Layout, error)

// Detect は contest_id から layout を自動選択する純粋関数。
func Detect(contestID string) Layout
```

#### Layout 非依存のヘルパー

task_id 計算 (cache key・AtCoder URL 用) はレイアウトに依存しないので、package トップレベルの関数として分離して持つ:

```go
// TaskID は短縮形 task ("d") を AtCoder task ID ("abc457_d") に展開する。
func TaskID(contestID, task string) string

// Letter は task ("d" or "abc457_d") から末尾の letter を取り出す (ABC 用)。
func Letter(task string) (string, error)
```

#### test / run からの呼び出しイメージ

```go
lay, err := layout.Parse(opts.LayoutName, opts.Contest)
if err != nil { return ... }
solutionPath, err := lay.SolutionPath(opts.Contest, opts.Task)
taskID := layout.TaskID(opts.Contest, opts.Task) // cache / AtCoder URL に使う
```

CLI 層 (`cmd/atcoder`) が文字列フラグを `Layout` に変換して `testexec.Options` / `runexec.Options` に詰める。test/run 内部は `Layout.SolutionPath` を呼ぶだけで、レイアウト判定はしない。

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| ABC レイアウト下で task が letter 単体でも `<contest>_<letter>` でもない | "ABC layout requires task as a single letter (a-g) or '<contest>_<letter>'" のようなメッセージで exit 1 |
| contest ID が `abc<NNN>` でないのに `--layout abc` 指定 | "contest ID does not match abc<NNN> format" で exit 1 (ARC 等の拡張は別途) |
| `abc/<contest_num>/<letter>.py` が存在しない | 既存と同じく「解答ファイルが見つかりません: ...」で exit 1 |
| 解答ファイルパスが算出できない (`--task` の形式異常) | 既存と同じく exit 2 (フラグエラー扱い) |

## 非機能要件

- 既存 `exercise/YYYY/MM/DD/` ワークフローは無修正で従来通り動くこと (regression なし)。`--layout` の default は実質 exercise レイアウトを変えない。
- `--layout=auto` の挙動が文書化されており、ユーザが「なぜ ABC dir が見られたのか」を後から把握できること。
- 新パッケージ `internal/layout/` の責務が明確で、test と run の重複実装を防げること。

## 将来の拡張ポイント

- ARC / AGC / AHC のレイアウト追加
  - 既存ディレクトリ `arc/<contest_num>/<letter>.py` も同じ形なので、`--layout arc` を足す or `--layout auto` の判定に `arc<NNN>` を追加するだけ
- ADT (`adt/<YYYY>/<MM>/<DD>/<HHMM>/<LETTER>/main.py`) は別レイアウト
  - 階層が深く letter は **大文字 + ディレクトリ** なので、`--layout adt` として別途設計
  - 当面 ABC 対応のみのため、ADT は将来課題に残す
- contest prefix から URL を組み立てる helper (今は `https://atcoder.jp/contests/<contest>/...` でハードコード) を `internal/layout/` 側に寄せる選択肢

## 用語

- **contest_id**: AtCoder の URL `/contests/<contest_id>/` に現れる ID 全体 (例: `abc457`)。
- **contest_num**: `contest_id` の数字部分 (例: `abc457` なら `457`)。ABC レイアウトのディレクトリ名に使う。
- **task_id**: AtCoder の URL `/tasks/<task_id>` に現れる ID 全体 (例: `abc457_d`)。
- **letter**: task_id の末尾 1 文字 (`a`〜`g`)。ABC レイアウトの解答ファイル名に使う。
- **layout**: 解答ファイルの配置規約。`abc` / `exercise` / `auto` の 3 値。

## 関連ドキュメント

- `docs/tools/abc-todo.md` (上位ロードマップ。MVP "A" の要件詳細が本書)
- `docs/tools/requirements/001-exercise-test.md` (既存の test サブコマンド要件)
- `docs/tools/usage/test.md` (ad-hoc 実行の使用例。旧 run-usage は 013 で test-usage に統合)
