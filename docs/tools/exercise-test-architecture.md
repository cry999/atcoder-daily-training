# `exercise test` アーキテクチャ

要件 / 利用手引はそれぞれ以下を参照:

- 要件定義: [exercise-test-requirements.md](./exercise-test-requirements.md)
- 利用手引: [exercise-test-usage.md](./exercise-test-usage.md)

このドキュメントは `cmd/exercise` ツールの内部設計、特に `test` サブコマンドのパッケージ構成・依存方向・型設計を扱う。

## パッケージ構成

```
cmd/exercise/
  main.go        # サブコマンドの dispatch + usage
  new.go         # cmdNew: 当日の演習ディレクトリを作成
  test.go        # cmdTest: 引数パース + selectExecutor (composition root)

internal/runner/
  runner.go      # ProcessResult + ProcessStatus (実行結果の低レベル型)
  python.go      # Python 具象実装 (Python 型 + NewPython + Run)

internal/testexec/
  test.go        # Run(Options) + Executor interface + orchestration
  judge.go       # CaseResult + CaseStatus + judge() + report() + diff/stderr 表示
  meta.go        # meta 型 + load/save (meta.toml の I/O)
  fetch.go       # AtCoder fetch + HTML パース (xpath via htmlquery)
```

## 依存方向

```
cmd/exercise  ──▶  internal/testexec  ──▶  internal/runner
        └────────────────────────────────▶  internal/runner
```

- 矢印は import 方向。
- `cmd/exercise` (composition root) のみが両者を import し、`testexec` と `runner` を結線する。
- `testexec` は `runner` の `ProcessResult` を import するが、具象実装 (Python, …) は import しない。
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

役割: 解答ファイルを特定し、テストキャッシュを用意 (必要なら fetch) し、各ケースを Executor で実行して判定・表示する。

主な型と関数:

```go
// Consumer-side interface: testexec が必要とする最小契約のみを宣言。
type Executor interface {
    Run(ctx context.Context, source string, input []byte, timeout time.Duration) (*runner.ProcessResult, error)
}

// 拡張子 → Executor のファクトリ。実装は composition root が注入する。
type ExecutorFor func(sourcePath string) (Executor, error)

type Options struct {
    Contest     string
    Task        string
    Refresh     bool
    ExecutorFor ExecutorFor
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

type CaseResult struct {
    Name     string
    Status   CaseStatus
    Elapsed  time.Duration
    Expected string  // Fail のとき
    Actual   string  // Fail のとき
    Stderr   string  // RE のとき
}

func judge(name, expected string, pr *runner.ProcessResult) CaseResult
```

設計上のポイント:

- **`Executor` interface は testexec で定義** (Go のイディオム: インタフェースは consumer 側)。
- **`ExecutorFor` を関数値として注入**することで、testexec は「どの拡張子をサポートするか」を知らない。新言語追加は composition root の変更のみで済む。
- **`ProcessResult` と `CaseResult` は別の型**:
  - `ProcessResult`: 実行という事実 (低レベル、runner 側)
  - `CaseResult`: 判定という解釈 (高レベル、testexec 側)
  - `judge()` が両者を橋渡しする純粋関数。
- `meta`/`fetch` は testexec の内部実装 (テストキャッシュの取得・永続化) であり外部に公開しない。

### Layer 3: `cmd/exercise` — composition root

役割: コマンドの dispatch、引数のパース、ファクトリの定義 (拡張子 → 具象 runner)、`testexec.Run` への注入。

```go
func cmdTest(args []string) (int, error) {
    // ... 引数パース ...
    return testexec.Run(testexec.Options{
        Contest:     contest,
        Task:        task,
        Refresh:     *refresh,
        ExecutorFor: selectExecutor, // ← ここで注入
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

- main パッケージは **「どの言語をサポートするか」を唯一知っているレイヤー**。
- `testexec` も `runner` も特定の言語選択ロジックには関与しない。

## 拡張: 新しい言語を追加するには

例: Go (`.go`) を対応する場合。

1. `internal/runner/golang.go` を新規作成し、`Golang` 型と `NewGolang() (*Golang, error)`、`Run(...)` を実装する。
2. `cmd/exercise/test.go` の `selectExecutor` に `case ".go": return runner.NewGolang()` を追加する。

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
  │   └─ それ以外 → fetchProblem(contest, task) → meta.toml + tests/NN.{in,out} を書き出し
  │
  ├─ selectExecutor(solutionPath) → Executor を取得
  │
  └─ 各ケース:
      ├─ executor.Run(ctx, solutionPath, input, timeout) → *runner.ProcessResult
      ├─ judge(name, expected, pr) → CaseResult
      └─ report(cr) で表示
```

## なぜこの設計か

| 判断 | 理由 |
|---|---|
| testexec を `cmd/exercise` から切り離した | 言語ファクトリの注入点 (composition root) を main に集中させ、test 実行ロジック自体を pure に保つため。テスト可能性も向上 (モック Executor を渡せる)。 |
| `Executor` を testexec 側で定義 | Go のイディオム: interface は consumer 側。runner は自分が誰に使われるか知らない。 |
| `ProcessResult` を runner 側に置いた | import 方向の制約。具象 runner の戻り値型なので runner に置く。testexec は import する側に回る。 |
| TLE を `ProcessStatus` enum で表現 | sentinel error より明示的な状態遷移。RE (非ゼロ終了) との性質の違い (殺された vs 自走で失敗) を型で区別できる。 |
| `judge()` を純粋関数で分離 | I/O も実行も含まない純粋な「ProcessResult + 期待値 → CaseResult」の翻訳。単体テスト容易。 |
| `meta`/`fetch` を testexec 内に閉じた | テストキャッシュの取得・永続化は test コマンドのみの関心事。他コマンドからの再利用が発生したら別パッケージへ昇格する。 |
