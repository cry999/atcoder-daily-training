# `atcoder test` アーキテクチャ

要件 / 利用手引はそれぞれ以下を参照:

- 要件定義: [001-exercise-test.md](./requirements/001-exercise-test.md)
- 利用手引: [atcoder-test-usage.md](./atcoder-test-usage.md)

このドキュメントは `cmd/atcoder` ツールの内部設計、特に `test` サブコマンドのパッケージ構成・依存方向・型設計を扱う。

## パッケージ構成

```
cmd/atcoder/
  main.go        # サブコマンドの dispatch + usage
  new.go         # cmdNew: 当日の演習ディレクトリを作成
  test.go        # cmdTest: 引数パース + selectExecutor (composition root) + watch ループ

internal/runner/
  runner.go      # ProcessResult + ProcessStatus (実行結果の低レベル型)
  python.go      # Python 具象実装 (Python 型 + NewPython + Run)

internal/testexec/
  test.go        # Run(Options) + Executor interface + orchestration (ケースを並列実行)
  judge.go       # CaseResult + CaseStatus + judge() + normalizeOutput()
  reporter.go    # Reporter interface (UI 抽象。Begin/CaseStarted/CaseFinished/End のライフサイクル)
  meta.go        # meta 型 + load/save (meta.toml の I/O)
  fetch.go       # AtCoder fetch + HTML パース (xpath via htmlquery)

internal/ui/
  reporter.go    # TestReporter / RunReporter: Reporter 実装 (case/result 出力、stderr 表示、summary)
  progress.go    # bubbletea ライブ進捗 (ケース一覧のスピナー + プログレスバー。TTY 時)
  watch.go       # watch モードの画面クリア・ヘッダ/フッタ・TTY 判定ヘルパー
  diff.go        # delta 風 unified diff (LCS + intra-line token highlight)
  chat.go        # bubbletea ベース chat TUI (`atcoder test --interactive` の TTY モード)。
                 # 出力行ごとに直前イベント (入力送信 or 直前出力) からの経過時間を表示
                 # (lastEventAt を基準に、行を読み出した時刻との差分。要件 019)。
                 # WatchPath が渡るとファイルを mtime ポーリングし、保存検知で子を最新
                 # ファイルで再 spawn する (epoch=sessionN で旧 stream の残響を破棄。要件 022)
  chat_casebuilder.go # vim 風 command モード (`Esc`→`:`)・ケースビルダー (textarea 2 ペイン)・
                 # ライブ検証 (tokensMatch)。`:w` で extracase.Save、保存先は tests-extra (要件 024)
  style.go       # lipgloss スタイル定義

internal/runexec/
  runexec.go     # Run(Options) + Executor/Reporter/ChatRunner interface (ad-hoc 実行: 任意 stdin → 出力表示)

internal/watch/
  watch.go       # 単一ファイルの mtime ポーリング監視 (Watcher + WaitForChange)。test の watch モードが使う

internal/config/
  config.go      # ユーザ設定 config.toml の XDG パス解決 + Load。flag のデフォルトに流し込む
  keys.go        # 既知キーのレジストリ (fields) + Keys/Get/Set/All/ValueCandidates。config サブコマンドと補完が参照する単一情報源

internal/cachepath/
  cachepath.go   # キャッシュ配置 (XDG_CACHE_HOME / ~/.cache / atcoder-tools 配下) の解決

internal/extracase/
  extracase.go   # ユーザ追加ケース (tests-extra/) の場所解決・保存 (Save)・列挙 (List)。
                 # ui (chat の :w で保存) と testexec (判定で列挙) の両方から使う (要件 024)
```

> 補足: `internal/runexec` は `atcoder test` の **ad-hoc / 対話モード** の実装 (旧 `atcoder run` サブコマンド。[ADR 0005](./decisions/0005-unify-test-run-into-test.md) で `test` に統合・廃止)。`testexec` (サンプル判定) と並列の位置付けで、判定 suite を行わず単発実行に特化する。`cmd/atcoder/test.go` がフラグ (`--in`/`--out`/`--interactive`) を見て `testexec.Run` / `runexec.Run` のどちらに振り分けるかを決め、ad-hoc 結線は `cmd/atcoder/adhoc.go` が持つ。詳細は [atcoder-test-usage.md](./atcoder-test-usage.md) の「モード」節。

## 依存方向

```
cmd/atcoder  ──▶  internal/testexec  ──▶  internal/runner
        ├──────▶  internal/runner
        ├──────▶  internal/watch   (test --watch: 解答ファイルの変更検知)
        ├──────▶  internal/config  (test: ユーザ設定の既定値読み込み)
        └──────▶  internal/ui  ──▶  internal/testexec  (CaseResult/CaseStatus 参照)
```

> `internal/watch` は `testexec` / `ui` に依存しない単一ファイル監視の小さな層。watch ループ自体 (実行 → 待機 → 再実行) は composition root の `cmd/atcoder/test.go` が持ち、`testexec.Run` を反復呼び出しする。
>
> `internal/config` は `internal/cachepath` (キャッシュ配置) と対をなすユーザ設定の層。`config.Load()` の結果を composition root が flag のデフォルト値に流し込むことで `flag > config > default` の優先順位を実現する。`testexec` 等のドメイン層は config を知らない。
>
> `atcoder config` サブコマンド (`cmd/atcoder/config.go`) は `internal/config` の**キーレジストリ** (`keys.go` の `fields`) を介して設定を閲覧・編集する。既知キー・型・値候補をこのレジストリ 1 か所に集約し、`config get/set/show` とシェル補完 (`internal/complete`) が同じ表を参照する (キー追加 = `fields` に 1 行)。`set` は未知キー保全のため struct ではなく汎用 `map[string]any` で読み書きする。

- 矢印は import 方向。
- `cmd/atcoder` (composition root) のみが全 internal パッケージを import し、結線する。
- `testexec` は `runner.ProcessResult` を import するが、具象実装 (Python, …) は import しない。
- `ui` は `testexec` を import (CaseResult や CaseStatus を扱うため) するが、`testexec` 側は `ui` を import しない (consumer-side interface)。
- `runner` はどこにも依存しない (末端)。

## レイヤー設計

### Layer 1: `internal/runner` — 実行の低レベル

役割: 言語ごとに「ソースファイル + 入力 + タイムアウト」を渡されて、プロセスを起動し結果を返す。判定は行わない。

主な型:

```go
type ProcessStatus int
const (
    Exited   ProcessStatus = iota  // プロセスが終了 (ExitCode で正常/異常を判別)
    TimedOut                       // タイムアウトで強制終了
)

type ProcessResult struct {
    Status   ProcessStatus
    Stdout   string
    Stderr   string
    Elapsed  time.Duration
    ExitCode int            // Status == Exited のときのみ有効
}

type Python struct { /* ... */ }
func NewPython() (*Python, error)
func (p *Python) Run(ctx, source, input, timeout) (*ProcessResult, error)
```

設計上のポイント:

- **`ProcessStatus` は enum**。TLE を sentinel error にせず、状態として表現する。これによりタイムアウトは「異常ではなく外部要因で打ち切られた事実」として扱える。
- **`Run` の `error` 戻り値はセットアップ失敗のみ** (例: Python が見つからない、ソースファイルが開けない)。プロセスが起動できた以上、TLE も非ゼロ終了も `ProcessResult` の中で表現する。
- 具象型 (`Python`) は consumer (testexec) のインタフェースを **知らない**。Go の interface satisfaction は structural なので、シグネチャさえ合えば `testexec.Executor` を満たす。

### Layer 2: `internal/testexec` — テスト実行の orchestration

役割: 解答ファイルを特定し、テストキャッシュを用意 (必要なら fetch) し、各ケースを Executor で実行して判定する。**表示は行わず Reporter に委譲する**。

主な型と関数:

```go
// Consumer-side interface: testexec が必要とする実行の最小契約。
type Executor interface {
    Run(ctx context.Context, source string, input []byte, timeout time.Duration, extraEnv []string) (*runner.ProcessResult, error)
}

// Consumer-side interface: testexec が必要とする表示の最小契約。
type Reporter interface {
    Fetching(contest, task string)
    Header(task, contest string, timeLimitMs, timeoutMs, ntests int)
    Case(cr CaseResult)
    Summary(passed, total int)
}

type ExecutorFor func(sourcePath string) (Executor, error)

type Options struct {
    Contest     string
    Task        string
    Refresh     bool
    Timeout     time.Duration
    Debug       bool
    ExecutorFor ExecutorFor
    Reporter    Reporter
}

func Run(opts Options) (exitCode int, err error)
```

```go
// judge は「ProcessResult + 期待値 → 論理的な CaseResult」への翻訳。純粋関数。
type CaseStatus int
const (
    Pass CaseStatus = iota
    Fail
    TLE
    RE
)

const DebugPrefix = "[DEBUG]"

type CaseResult struct {
    Name            string
    Status          CaseStatus
    Elapsed         time.Duration
    Input           string  // 常時
    Expected        string  // 常時
    Actual          string  // 常時 (debug 時は [DEBUG] 行を除外したもの)
    Debug           string  // debug 時に [DEBUG] 行を集約
    Stderr          string  // RE のとき
    OriginalLimitMs int     // 本来の time_limit との比較用
}

func judge(name, input, expected string, pr *runner.ProcessResult, debug bool) CaseResult
```

設計上のポイント:

- **`Executor` も `Reporter` も testexec で定義** (Go のイディオム: インタフェースは consumer 側)。
- **`ExecutorFor` を関数値として注入**することで、testexec は「どの拡張子をサポートするか」を知らない。新言語追加は composition root の変更のみで済む。
- **`Reporter` を注入**することで、testexec は表示形式に依存しない。色付き表示・プレーン表示・テスト用の nop reporter などを差し替え可能。
- **`ProcessResult` と `CaseResult` は別の型**:
  - `ProcessResult`: 実行という事実 (低レベル、runner 側)
  - `CaseResult`: 判定という解釈 (高レベル、testexec 側)
  - `judge()` が両者を橋渡しする純粋関数。
- `meta`/`fetch` は testexec の内部実装 (テストキャッシュの取得・永続化) であり外部に公開しない。

### Layer 3: `internal/ui` — 表示

役割: `testexec.Reporter` の具象実装。lipgloss でステータスバッジ・色付き diff・サマリ等をターミナルに描画する。`testexec` のフックポイントから呼び出されるのみで、orchestration ロジックは持たない。

```go
type TestReporter struct{}

func NewTestReporter() *TestReporter

// testexec.Reporter を満たすメソッド
func (r *TestReporter) Fetching(contest, task string)
func (r *TestReporter) Header(task, contest string, timeLimitMs, ntests int)
func (r *TestReporter) Case(cr testexec.CaseResult)
func (r *TestReporter) Summary(passed, total int)
```

設計上のポイント:

- **`ui` は `testexec` を import するが逆は無い**。testexec は ui の存在を知らず、structural typing で `*ui.TestReporter` が `testexec.Reporter` を満たす。
- **lipgloss は `ui` 内に閉じ込められている**。スタイリングを差し替えたい (別ライブラリ、HTML 出力、JSON 出力など) ときは ui の置き換えで完結する。
- 非 TTY 環境では lipgloss が自動でエスケープを除去するため、CI やパイプ経由でも素直なテキストが流れる。

### Layer 4: `cmd/atcoder` — composition root

役割: コマンドの dispatch、引数のパース、ファクトリの定義 (拡張子 → 具象 runner)、Reporter の生成、`testexec.Run` への注入。

```go
func cmdTest(args []string) (int, error) {
    // ... 引数パース ...
    return testexec.Run(testexec.Options{
        Contest:     contest,
        Task:        task,
        Refresh:     *refresh,
        ExecutorFor: selectExecutor,        // ← runner の注入
        Reporter:    ui.NewTestReporter(),  // ← UI の注入
    })
}

func selectExecutor(sourcePath string) (testexec.Executor, error) {
    switch filepath.Ext(sourcePath) {
    case ".py":
        return runner.NewPython()
    default:
        return nil, fmt.Errorf("unsupported extension: %s", filepath.Ext(sourcePath))
    }
}
```

設計上のポイント:

- main パッケージは **「どの言語をサポートするか」「どう表示するか」を唯一知っているレイヤー**。
- `testexec` も `runner` も `ui` も、特定の言語選択や具体的な描画ライブラリには関与しない。

## 拡張: 新しい言語を追加するには

例: Go (`.go`) を対応する場合。

1. `internal/runner/golang.go` を新規作成し、`Golang` 型と `NewGolang() (*Golang, error)`、`Run(...)` を実装する。
2. `cmd/atcoder/test.go` の `selectExecutor` に `case ".go": return runner.NewGolang()` を追加する。

`internal/testexec` は無改修。`Executor` interface のシグネチャを満たす型を runner 側に1つ追加し、composition root の switch に 1 行追加するだけで完了する。

コンパイル工程が必要な言語 (C++ 等) の場合は、`Run` の内部でビルド成果物をキャッシュするか、将来的に `Executor` interface に `Prepare(ctx, source) error` を追加して二段階に分割する余地を残す。現状の interface は最小契約 (`Run` のみ) なので後方互換に注意しつつ拡張可能。

## テストキャッシュのフロー

```
testexec.Run
  │
  ├─ 解答ファイル特定: exercise/YYYY/MM/DD/<task>.py
  │
  ├─ ensureTests
  │   ├─ <task>/tests/ と <task>/meta.toml が両方ある & !refresh → 使う
  │   └─ それ以外 → reporter.Fetching() → fetchProblem(contest, task) → meta.toml + tests/NN.{in,out} を書き出し
  │       (ensureTests / --refresh は tests/ のみ対象。tests-extra/ には触れない)
  │
  ├─ selectExecutor(solutionPath) → Executor を取得
  │
  ├─ collectCases: 公式 tests/NN (id=NN) + extracase.List → tests-extra/NN (id=x+NN) を連結
  │
  ├─ reporter.Header(...)
  │
  ├─ 各ケース (caseRef = id + in/out パス):
  │   ├─ executor.Run(ctx, solutionPath, input, timeout) → *runner.ProcessResult
  │   ├─ judge(id, expected, pr) → CaseResult
  │   └─ reporter.Case(cr)
  │
  └─ reporter.Summary(passed, total)
```

> ユーザ追加ケース (`tests-extra/`) は chat のケースビルダー (`:w`) が `extracase.Save` で書き、判定時は `collectCases` が公式サンプルの後ろに連結する (表示 id は接頭辞 `x`)。`--refresh` は公式サンプル (`tests/`) だけを取り直すので追加ケースは消えない (要件 024)。

## なぜこの設計か

| 判断 | 理由 |
|---|---|
| testexec を `cmd/atcoder` から切り離した | 言語ファクトリの注入点 (composition root) を main に集中させ、test 実行ロジック自体を pure に保つため。テスト可能性も向上 (モック Executor を渡せる)。 |
| `Executor` を testexec 側で定義 | Go のイディオム: interface は consumer 側。runner は自分が誰に使われるか知らない。 |
| `ProcessResult` を runner 側に置いた | import 方向の制約。具象 runner の戻り値型なので runner に置く。testexec は import する側に回る。 |
| TLE を `ProcessStatus` enum で表現 | sentinel error より明示的な状態遷移。RE (非ゼロ終了) との性質の違い (殺された vs 自走で失敗) を型で区別できる。 |
| `judge()` を純粋関数で分離 | I/O も実行も含まない純粋な「ProcessResult + 期待値 → CaseResult」の翻訳。単体テスト容易。 |
| `meta`/`fetch` を testexec 内に閉じた | テストキャッシュの取得・永続化は test コマンドのみの関心事。他コマンドからの再利用が発生したら別パッケージへ昇格する。 |
| 表示を `internal/ui` に分離した | lipgloss / 色付けなどの presentation 詳細を testexec から切り離し、testexec を pure な orchestration に保つため。表示形式の差し替え (プレーン出力、JSON 出力、TUI) も ui の入れ替えで完結する。 |
