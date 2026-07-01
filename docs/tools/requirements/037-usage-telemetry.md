# コマンド利用テレメトリ (ローカル集計) 要件定義

## 概要

`atcoder` の各サブコマンドの**利用頻度・所要時間**をローカルに記録し、`atcoder usage` で集計表示する。実行のたびに「サブコマンド名・使われたフラグ名・所要時間・exit code・時刻」を 1 行 JSON (JSONL) で追記し、`atcoder usage` がそれを読んでコマンド別の回数・合計/平均所要時間・最終利用日時を出す。目的は**実利用データに基づくコマンド設計の判断** (どのコマンド/フラグがよく使われ、どれが使われていないか) であり、ネットワークには一切出さない (ローカル完結)。記録は **non-fatal** — ログ書き込みに失敗してもコマンド本体の挙動・exit code には一切影響しない。

## 背景・目的

- どのサブコマンド・フラグが実際に使われているかの定量データが無く、コマンド設計 (新フラグの要否・廃止候補・既定値の調整) が勘になっている。
- 「`test` を 1 日に何回・1 回あたり何秒回しているか」「`start` の滞在時間」「`--graph` や `--submit` が実際に使われているか」をローカルで可視化したい。
- 既存 [`stats`](005-exercise-stats.md) は **exercise ツリー (練習解答) の集計専用**で、CLI そのものの利用統計とは責務が別。混ぜると stats の責務が「練習 + ツール利用」に膨らむため、**新サブコマンド `usage` に分ける**。

## スコープ

| 項目 | 当面のスコープ | 将来の拡張余地 |
|---|---|---|
| 記録トリガ | `main()` の dispatch を 1 箇所でラップし、全組み込みサブコマンド実行のたびに 1 イベント追記 | — |
| 記録項目 | 時刻 (ts) / サブコマンド名 (cmd) / 使われたフラグ名 (flags) / 所要時間 (dur_ms) / exit code (exit) / バージョン (version) | 端末種別・cwd 種別・OS など |
| 引数の粒度 | **サブコマンド名 + フラグ名のみ**。フラグの値・位置引数 (パス・contest_id 等) は記録しない (プライバシー/ノイズ低減) | フラグ値のカテゴリ化 (任意 opt-in) |
| 形式 | **JSONL** (append-only)。1 実行 = 1 行 | 圧縮・ローテーション |
| 集計コマンド | `atcoder usage`: コマンド別の count / total / avg / last を表で。`--flags` でフラグ別内訳 | 期間窓 (`-l/--last`)・`--graph`・`--json` 出力 |
| 保存先 | `$XDG_DATA_HOME/atcoder-tools/usage/events.jsonl` (キャッシュではなく**データ**領域 = `--refresh` 等で消えない) | — |
| 無効化 | 環境変数 `ATCODER_NO_USAGE` が非空なら記録しない | config `[usage] enabled` |
| 除外コマンド | `__complete` (補完ヘルパ。シェルが tab ごとに呼ぶためノイズ) と未知コマンド (typo) は記録しない | — |

### 既存 stats との責務分担

| | 集計対象 | データ源 | コマンド |
|---|---|---|---|
| `stats` | 練習解答 (何問解いたか) | `exercise/YYYY/MM/DD/*.py` | `atcoder stats` |
| `usage` (本件) | CLI 利用 (どのコマンドを何回/何秒) | `usage/events.jsonl` | `atcoder usage` |

両者は入力もコマンドも独立。`usage` は `stats` のコードに触らない。

## ディレクトリ構造 / スキーマ

### 保存先

```
$XDG_DATA_HOME/atcoder-tools/usage/events.jsonl   # XDG_DATA_HOME 未設定なら ~/.local/share、最終 fallback ./.local/share
```

キャッシュ (`internal/cachepath` = `$XDG_CACHE_HOME/atcoder-tools/`) とは別に**データ領域**へ置く。利用履歴は集計の材料として蓄積したいので、キャッシュ削除 (`--refresh` やユーザの掃除) で消えてはならない。AppName は cachepath と同じ `atcoder-tools`。

### イベント (JSONL 1 行) スキーマ

| フィールド | 型 | 内容 |
|---|---|---|
| `ts` | string (RFC3339) | 実行開始時刻 |
| `cmd` | string | サブコマンド名 (alias 展開後の組み込み名。例 `test`) |
| `flags` | []string | 使われたフラグ名 (先頭の `-`/`--` を除き、`=value` の手前まで。重複は除く。例 `["task","refresh"]`) |
| `dur_ms` | int64 | 所要時間 (ミリ秒) |
| `exit` | int | exit code |
| `version` | string | 実行バイナリのバージョン (`selfupdate.ReadCurrent()` 相当。空可) |

例:

```json
{"ts":"2026-06-12T14:01:09+09:00","cmd":"test","flags":["task"],"dur_ms":7600,"exit":0,"version":"a1b2c3d (2026-06-10T..)"}
{"ts":"2026-06-12T14:05:33+09:00","cmd":"start","flags":["debug"],"dur_ms":210000,"exit":0,"version":"a1b2c3d (..)"}
```

## CLI 仕様

### 記録 (全コマンド共通・暗黙)

新フラグは増やさない。`main()` が dispatch をラップして自動記録する。記録は表に出ない副作用で、**失敗しても無視** (stderr にも出さない)。

### `atcoder usage` (新サブコマンド)

| 引数/フラグ | 説明 |
|---|---|
| (なし) | コマンド別集計表を count 降順で表示 |
| `--flags` | コマンド別表に加え、フラグ別の利用回数内訳を表示 |
| `--json` | 集計結果を JSON で出力 (機械可読。将来の分析用) |

処理ステップ:

1. `usagelog.Path()` の JSONL を 1 行ずつ読む (無ければ「記録がありません」と出して exit 0)。
2. 壊れた行 (パース失敗) はスキップ (集計は best-effort)。
3. `cmd` ごとに count / total dur / last ts を集計し、count 降順 (同数は cmd 名昇順) に整列。
4. 表で出力 (TTY なら整形)。`--flags` 指定時はコマンド配下にフラグ別 count を出す。

出力イメージ:

```
$ atcoder usage
Command   Count   Total     Avg     Last
test        142   18m02s    7.6s    2026-06-12 14:01
start        37   2h11m     3.5m    2026-06-11 22:40
new          21    4.2s     0.2s    2026-06-12 09:00
stats         9    1.1s     0.1s    2026-06-10 23:12

合計 209 回 / 4 コマンド
```

```
$ atcoder usage --flags
test        142   18m02s    7.6s    2026-06-12 14:01
    task     130
    refresh   12
    submit     4
...
```

記録が無いとき:

```
$ atcoder usage
(まだ利用記録がありません)
```

## 動作仕様

| 項目 | 挙動 |
|---|---|
| 記録の non-fatal 性 | ログのディレクトリ作成/書き込みに失敗しても、コマンド本体の stdout/stderr/exit code は不変。エラーは握りつぶす (stderr にも出さない) |
| 除外 | `__complete` (補完ヘルパ) と未知コマンド (usage 表示 → exit 2) は記録しない |
| alias | alias は展開後の組み込み名で記録 (例 `upd-lo` → `update`)。alias 名自体は残さない |
| フラグ抽出 | `-`/`--` で始まるトークンのみ。`=value` は手前まで。値 (次トークン) や位置引数は記録しない。単独 `-` (stdin) は空になるので捨てる |
| 無効化 | `ATCODER_NO_USAGE` が非空なら記録を完全スキップ (ファイルも作らない) |
| 冪等性 | 記録は追記のみ。`usage` は読み取り専用で副作用ゼロ |
| 並行実行 | 追記は `O_APPEND` で開く。複数プロセス同時実行でも行は壊れにくい (1 行ずつ Write) |
| 保存先 | キャッシュではなくデータ領域。`--refresh` 等のキャッシュ操作で消えない |

## 影響範囲

| ファイル | 変更内容 |
|---|---|
| `internal/usagelog/usagelog.go` (新規) | 記録機構 + 集計。`Event` 型、`Path() string`、`Record(Event) error` (append-only, non-fatal は呼び出し側)、`FlagsFromArgs([]string) []string`、`Aggregate(io.Reader) ([]Stat, error)` / `Load()`、`Stat` 型。`ATCODER_NO_USAGE` 判定 |
| `cmd/atcoder/main.go` | dispatch を `dispatch(name, rest) int` に切り出し、`__complete`/未知以外を実行前後で時刻計測 → `usagelog.Record` (non-fatal)。`builtins` に `usage` を追加し `usage()` 文字列も更新 |
| `cmd/atcoder/usage.go` (新規) | `cmdUsage(args []string) (int, error)`。JSONL を読み集計し表 (or `--flags`/`--json`) を出力 |
| `internal/usagelog/usagelog_test.go` (新規) | record→load の roundtrip、`FlagsFromArgs` の正規化 (`--task`→`task`, `--last=3d`→`last`, `-`→除外, 重複除去)、`Aggregate` の count/total/last、壊れ行スキップ、`ATCODER_NO_USAGE` で書かない |
| `cmd/atcoder/usage_test.go` (新規) | 一時 `XDG_DATA_HOME` にイベントを置き `cmdUsage` が exit 0 で集計を出す・空時のメッセージ・`--flags` 内訳 |
| `fixtures/run.sh` | `usage` のオフライン smoke を 1 ケース (一時 XDG_DATA_HOME で記録 → `atcoder usage` exit 0)。既存 `test` ケースには `ATCODER_NO_USAGE=1` を効かせ実ユーザのデータ領域を汚さない |
| `docs/tools/usage/usage.md` (新規) | `atcoder usage` の利用手引 (集計の見方・保存先・無効化・プライバシー) |
| `docs/tools/todo.md` | 本項目を追加し ✅ DONE。要件 037 と相互リンク |

### `internal/usagelog` の公開 API 素描

```go
package usagelog

type Event struct {
    TS      time.Time `json:"ts"`
    Cmd     string    `json:"cmd"`
    Flags   []string  `json:"flags"`
    DurMs   int64     `json:"dur_ms"`
    Exit    int       `json:"exit"`
    Version string    `json:"version"`
}

// Path は events.jsonl の絶対パス ($XDG_DATA_HOME/atcoder-tools/usage/events.jsonl)。
func Path() string

// Disabled は ATCODER_NO_USAGE が非空かを返す。
func Disabled() bool

// Record は 1 イベントを JSONL に追記する。Disabled なら何もしない。
// 失敗時は error を返すが、呼び出し側 (main) は無視する (non-fatal)。
func Record(ev Event) error

// FlagsFromArgs は引数列から使われたフラグ名 (正規化・重複除去) を抜く。
func FlagsFromArgs(args []string) []string

type Stat struct {
    Cmd      string
    Count    int
    TotalMs  int64
    Last     time.Time
    Flags    map[string]int // フラグ名 → 回数 (--flags 用)
}

// Aggregate は JSONL を読み、cmd 別に集計して count 降順で返す。壊れ行はスキップ。
func Aggregate(r io.Reader) ([]Stat, error)
```

## エラーハンドリング

| 状況 | 動作 |
|---|---|
| ログ書き込み失敗 (権限・ディスク等) | 記録を諦める。コマンド本体・exit code は不変 (non-fatal、stderr にも出さない) |
| `usage`: ログファイルが無い | 「(まだ利用記録がありません)」を出して exit 0 |
| `usage`: 壊れた JSON 行がある | その行だけスキップして集計続行 (exit 0) |
| `usage`: 未知フラグ | exit 2 (引数誤り) |
| `usage`: ログ読み取り I/O エラー | exit 1 |
| `ATCODER_NO_USAGE` 非空 | 記録を完全スキップ (ファイルも作らない)。`usage` は既存ログがあれば読める |

## 非機能要件

- **既存非破壊**: 記録は dispatch のラップで全コマンドに透過的に挿入されるが、stdout/stderr/exit code/挙動は一切変えない。記録失敗は握りつぶす。`__complete` は記録対象外で補完性能に影響しない。
- **プライバシー / ローカル完結**: フラグ**名**のみ記録し、値・位置引数 (パス・問題名) は残さない。ネットワークには出さない。`ATCODER_NO_USAGE` で完全無効化できる。
- **永続性**: キャッシュではなくデータ領域に置き、`--refresh` 等で消えない。
- **前方互換**: JSONL なので項目追加は後方互換 (古い行に欠ける項目はゼロ値)。将来 `usage -l/--last`・`--graph`・config opt-out を足せる。
- **軽量**: 追記 1 回 (O_APPEND + 1 行 Write) のみ。dispatch のオーバーヘッドは無視できる。

## 将来の拡張ポイント

- `usage -l/--last <dur>` で期間窓集計、`--graph` で時系列 (stats の期間窓・草グリッドの実装を流用)。
- フラグ値のカテゴリ化 (opt-in)、cwd 種別・端末種別の記録。
- config `[usage] enabled = false` での恒久 opt-out。
- ログのローテーション / 圧縮。

## 用語

- **利用イベント**: 1 回のサブコマンド実行の記録 (cmd/flags/dur/exit/ts/version)。
- **データ領域**: `$XDG_DATA_HOME/atcoder-tools/` (キャッシュとは別。消えてはいけない永続データ)。
- **フラグ名**: `--task` → `task` のように先頭ダッシュと `=value` を除いた識別子。

## 関連ドキュメント

- `docs/tools/requirements/005-exercise-stats.md` (`stats`。責務が別であることの対比)
- `docs/tools/usage/stats.md` (集計コマンドの利用手引の前例)
- `internal/cachepath` (XDG パス解決の前例。本件はデータ領域版を usagelog に持つ)
- `cmd/atcoder/main.go` (dispatch のフック箇所)
