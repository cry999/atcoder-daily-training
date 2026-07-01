package testexec

import (
	"context"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cachepath"
	"github.com/cry999/atcoder-daily-training/internal/extracase"
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/runner"
)

type Executor interface {
	Run(ctx context.Context, source string, input []byte, timeout time.Duration, extraEnv []string) (*runner.ProcessResult, error)
}

type ExecutorFor func(sourcePath string) (Executor, error)

type Options struct {
	Contest     string
	Task        string
	Layout      layout.Layout // nil なら layout.Exercise{} 相当 (旧挙動)
	Refresh     bool
	Timeout     time.Duration // 0 → use the problem's time_limit_ms from meta.toml
	Debug       bool          // true → DEBUG=1 を子プロセスに渡し、stdout から [DEBUG] 行を除外して比較
	Cases       []string      // 非空ならこの名前 (例: "01", "03") のケースだけ実行。数値のみは 2 桁ゼロ埋めに正規化
	Tolerance   float64       // float トークン比較の絶対 / 相対誤差。0 以下なら DefaultTolerance を使う
	Concurrency int           // 同時に実行するケース数。0 以下なら runtime.NumCPU() (ケース数で頭打ち)
	ExecutorFor ExecutorFor
	Reporter    Reporter

	// SolutionPathOverride は実行対象の解答パスを上書きする (要件 049)。非空なら
	// Layout.SolutionPath の解決結果ではなくこのパスを実行する。提出ゲートが
	// 「コメントアウト後ソースを書き出した一時ファイル」を走らせるために使う。
	// 拡張子は ExecutorFor の言語選択に効くので、原本と同じ拡張子で渡すこと。
	SolutionPathOverride string
}

func Run(opts Options) (int, error) {
	lay := opts.Layout
	if lay == nil {
		lay = layout.Exercise{}
	}
	solutionPath, err := lay.SolutionPath(opts.Contest, opts.Task)
	if err != nil {
		return 1, err
	}
	// 提出ゲートはコメントアウト後ソースを書き出した一時ファイルを実行対象にする (要件 049)。
	if opts.SolutionPathOverride != "" {
		solutionPath = opts.SolutionPathOverride
	}
	if _, err := os.Stat(solutionPath); err != nil {
		return 1, fmt.Errorf("解答ファイルが見つかりません: %s", solutionPath)
	}

	// キャッシュ (meta.toml + tests/) は XDG_CACHE_HOME/atcoder-tools 配下に置く。
	// 解答ファイル自体は per-day の exercise/YYYY/MM/DD のまま。
	taskDir := cachepath.Task(opts.Contest, opts.Task)
	testsDir := filepath.Join(taskDir, "tests")
	metaPath := filepath.Join(taskDir, "meta.toml")

	mta, _, err := ensureTests(opts.Reporter, opts.Contest, opts.Task, taskDir, testsDir, metaPath, opts.Refresh)
	if err != nil {
		return 1, err
	}

	executor, err := opts.ExecutorFor(solutionPath)
	if err != nil {
		return 1, err
	}

	refs, err := collectCases(testsDir, taskDir)
	if err != nil {
		return 1, err
	}
	if len(refs) == 0 {
		return 1, errors.New("テストケースが見つかりません")
	}
	if len(opts.Cases) > 0 {
		refs, err = filterRefs(refs, opts.Cases)
		if err != nil {
			return 1, err
		}
	}
	names := caseIDs(refs) // 表示 id (公式=01… / 追加=x01…)。Reporter とサマリで使う

	timeout := time.Duration(mta.TimeLimitMs) * time.Millisecond
	if opts.Timeout > 0 {
		timeout = opts.Timeout
	}
	tolerance := opts.Tolerance
	if tolerance <= 0 {
		tolerance = DefaultTolerance
	}
	opts.Reporter.Header(opts.Task, opts.Contest, mta.TimeLimitMs, int(timeout/time.Millisecond), len(names), tolerance)

	var extraEnv []string
	if opts.Debug {
		extraEnv = []string{"DEBUG=1"}
	}

	// 各ケースは独立 (共有状態なし、Executor.Run は毎回別プロセスを起動) なので、
	// 上限付きワーカープールで並列に実行する。結果は元の並び (names 順) を保つ。
	concurrency := opts.Concurrency
	if concurrency <= 0 {
		concurrency = runtime.NumCPU()
	}
	if concurrency > len(names) {
		concurrency = len(names)
	}

	opts.Reporter.Begin(names, concurrency)

	results := make([]CaseResult, len(refs))
	var (
		wg       sync.WaitGroup
		mu       sync.Mutex // firstErr を保護する
		firstErr error
		sem      = make(chan struct{}, concurrency)
	)
	for i, ref := range refs {
		wg.Add(1)
		go func(i int, ref caseRef) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()

			opts.Reporter.CaseStarted(ref.id)
			cr, err := runCase(executor, extraEnv, opts.Debug, tolerance, solutionPath, ref, timeout)
			if err != nil {
				mu.Lock()
				if firstErr == nil {
					firstErr = err
				}
				mu.Unlock()
				return
			}
			cr.OriginalLimitMs = mta.TimeLimitMs
			results[i] = cr
			opts.Reporter.CaseFinished(cr)
		}(i, ref)
	}
	wg.Wait()

	opts.Reporter.End(results)
	if firstErr != nil {
		return 1, firstErr
	}

	passed := 0
	for _, cr := range results {
		if cr.Status == Pass {
			passed++
		}
	}
	opts.Reporter.Summary(passed, len(names))
	if passed != len(names) {
		return 1, nil
	}
	return 0, nil
}

func runCase(executor Executor, extraEnv []string, debug bool, tolerance float64, solutionPath string, ref caseRef, timeout time.Duration) (CaseResult, error) {
	input, err := os.ReadFile(ref.in)
	if err != nil {
		return CaseResult{}, err
	}
	expected, err := os.ReadFile(ref.out)
	if err != nil {
		return CaseResult{}, err
	}

	pr, err := executor.Run(context.Background(), solutionPath, input, timeout, extraEnv)
	if err != nil {
		return CaseResult{}, err
	}
	return judge(ref.id, string(input), string(expected), pr, debug, tolerance), nil
}

// EnsureResult は EnsureTests の結果サマリ。コンテスト一括準備の進捗表示に使う。
type EnsureResult struct {
	Fetched     bool // true ならネットワークから取得、false ならキャッシュヒット
	NumSamples  int  // 現在キャッシュされているサンプルケース数
	TimeLimitMs int
}

// EnsureTests は単一タスクのサンプル + meta をキャッシュに揃える。
// キャッシュ済みなら何もせず、未取得 (または refresh) なら AtCoder から取得する。
// `atcoder new abc` のような一括準備から呼ぶための公開ラッパー。
func EnsureTests(reporter Reporter, contest, task string, refresh bool) (EnsureResult, error) {
	taskDir := cachepath.Task(contest, task)
	testsDir := filepath.Join(taskDir, "tests")
	metaPath := filepath.Join(taskDir, "meta.toml")

	mta, fetched, err := ensureTests(reporter, contest, task, taskDir, testsDir, metaPath, refresh)
	if err != nil {
		return EnsureResult{}, err
	}
	names, err := listCases(testsDir)
	if err != nil {
		return EnsureResult{}, err
	}
	return EnsureResult{
		Fetched:     fetched,
		NumSamples:  len(names),
		TimeLimitMs: mta.TimeLimitMs,
	}, nil
}

// ensureTests は contest/task のサンプル + meta をキャッシュに揃え、その meta と
// 「実際にネットワークから取得したか (fetched)」を返す。
func ensureTests(reporter Reporter, contest, task, taskDir, testsDir, metaPath string, refresh bool) (*Meta, bool, error) {
	if !refresh {
		_, errTests := os.Stat(testsDir)
		if errTests == nil {
			if m, err := loadMeta(metaPath); err == nil {
				return m, false, nil
			}
		}
	}

	// 取得元 URL を決める。meta.toml に url override が記録されていれば (例:
	// `atcoder meta set abc111 --task d --url <arc103_b の URL>`) それを優先する。
	// task_id が contest と食い違う問題で、解答スロット (contest/task) を保ったまま
	// 正しいページから取得するための仕掛け。override が無ければ contest/task から導出。
	override := ""
	if m, err := loadMeta(metaPath); err == nil {
		override = m.URL
	}
	url := resolveFetchURL(contest, task, override)

	reporter.Fetching(contest, task)
	prob, err := fetchProblem(url)
	if err != nil {
		return nil, false, fmt.Errorf("AtCoder から取得できませんでした: %w", err)
	}

	if err := os.MkdirAll(testsDir, 0o755); err != nil {
		return nil, false, err
	}
	if entries, err := os.ReadDir(testsDir); err == nil {
		for _, e := range entries {
			os.Remove(filepath.Join(testsDir, e.Name()))
		}
	}
	for i, s := range prob.Samples {
		n := i + 1
		inPath := filepath.Join(testsDir, fmt.Sprintf("%02d.in", n))
		outPath := filepath.Join(testsDir, fmt.Sprintf("%02d.out", n))
		if err := os.WriteFile(inPath, []byte(s.Input), 0o644); err != nil {
			return nil, false, err
		}
		if err := os.WriteFile(outPath, []byte(s.Output), 0o644); err != nil {
			return nil, false, err
		}
	}

	mta := &Meta{
		Contest:     contest,
		Task:        task,
		URL:         prob.URL,
		TimeLimitMs: prob.TimeLimitMs,
		FetchedAt:   time.Now(),
	}
	if err := saveMeta(metaPath, mta); err != nil {
		return nil, false, err
	}
	// 入力生成 (要件 060) 用の生セクションも同じ HTML から拾って保存する
	// (ベストエフォート。失敗してもサンプル取得は成功扱い)。
	saveGenSource(taskDir, prob)
	return mta, true, nil
}

// caseRef は判定 1 件分の参照。id は表示 id (公式=01… / 追加=x01…)、in/out は
// 実ファイルの絶対パス (公式は tests/、追加は tests-extra/ を指す)。
type caseRef struct {
	id  string
	in  string
	out string
}

// collectCases は公式サンプル (tests/) の後ろにユーザ追加ケース (tests-extra/) を
// 連結した判定対象の並びを返す。追加ケースは表示 id に接頭辞 `x` を付け、公式と
// 区別する (x は ASCII で数字の後にソートされ、公式の後に並ぶ)。tests-extra が
// 無いのは正常 (公式だけを返す)。
func collectCases(testsDir, taskDir string) ([]caseRef, error) {
	official, err := listCases(testsDir)
	if err != nil {
		return nil, err
	}
	refs := make([]caseRef, 0, len(official))
	for _, n := range official {
		refs = append(refs, caseRef{
			id:  n,
			in:  filepath.Join(testsDir, n+".in"),
			out: filepath.Join(testsDir, n+".out"),
		})
	}
	extra, err := extracase.List(taskDir)
	if err != nil {
		return nil, err
	}
	extraDir := extracase.Dir(taskDir)
	for _, n := range extra {
		refs = append(refs, caseRef{
			id:  "x" + n,
			in:  filepath.Join(extraDir, n+".in"),
			out: filepath.Join(extraDir, n+".out"),
		})
	}
	return refs, nil
}

// caseIDs は refs の表示 id を順番どおりに取り出す。
func caseIDs(refs []caseRef) []string {
	ids := make([]string, len(refs))
	for i, r := range refs {
		ids[i] = r.id
	}
	return ids
}

// filterRefs は要求されたケース id (例: "1", "01", "x01") の和集合に含まれる
// ケースだけを並びを保って返す。数値のみの指定は 2 桁ゼロ埋めに正規化する
// (追加ケースは `x01` のように接頭辞付きで明示指定する)。該当無しはエラー。
func filterRefs(all []caseRef, requested []string) ([]caseRef, error) {
	want := make(map[string]bool, len(requested))
	for _, r := range requested {
		want[normalizeCaseName(r)] = true
	}
	var out []caseRef
	for _, ref := range all {
		if want[ref.id] {
			out = append(out, ref)
		}
	}
	if len(out) == 0 {
		return nil, fmt.Errorf("該当するテストケースがありません: %v", requested)
	}
	return out, nil
}

func normalizeCaseName(s string) string {
	if n, err := strconv.Atoi(s); err == nil && n >= 0 && n < 100 {
		return fmt.Sprintf("%02d", n)
	}
	return s
}

func listCases(testsDir string) ([]string, error) {
	entries, err := os.ReadDir(testsDir)
	if err != nil {
		return nil, err
	}
	var names []string
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		if !strings.HasSuffix(e.Name(), ".in") {
			continue
		}
		names = append(names, strings.TrimSuffix(e.Name(), ".in"))
	}
	sort.Strings(names)
	return names, nil
}
