package testexec

import (
	"context"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cachepath"
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
	ExecutorFor ExecutorFor
	Reporter    Reporter
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
	if _, err := os.Stat(solutionPath); err != nil {
		return 1, fmt.Errorf("解答ファイルが見つかりません: %s", solutionPath)
	}

	// キャッシュ (meta.toml + tests/) は XDG_CACHE_HOME/atcoder-tools 配下に置く。
	// 解答ファイル自体は per-day の exercise/YYYY/MM/DD のまま。
	taskDir := cachepath.Task(opts.Contest, opts.Task)
	testsDir := filepath.Join(taskDir, "tests")
	metaPath := filepath.Join(taskDir, "meta.toml")

	mta, err := ensureTests(opts.Reporter, opts.Contest, opts.Task, taskDir, testsDir, metaPath, opts.Refresh)
	if err != nil {
		return 1, err
	}

	executor, err := opts.ExecutorFor(solutionPath)
	if err != nil {
		return 1, err
	}

	names, err := listCases(testsDir)
	if err != nil {
		return 1, err
	}
	if len(names) == 0 {
		return 1, errors.New("テストケースが見つかりません")
	}
	if len(opts.Cases) > 0 {
		names, err = filterCases(names, opts.Cases)
		if err != nil {
			return 1, err
		}
	}

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

	passed := 0
	for _, name := range names {
		cr, err := runCase(executor, extraEnv, opts.Debug, tolerance, solutionPath, testsDir, name, timeout)
		if err != nil {
			return 1, err
		}
		cr.OriginalLimitMs = mta.TimeLimitMs
		opts.Reporter.Case(cr)
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

func runCase(executor Executor, extraEnv []string, debug bool, tolerance float64, solutionPath, testsDir, name string, timeout time.Duration) (CaseResult, error) {
	inPath := filepath.Join(testsDir, name+".in")
	outPath := filepath.Join(testsDir, name+".out")

	input, err := os.ReadFile(inPath)
	if err != nil {
		return CaseResult{}, err
	}
	expected, err := os.ReadFile(outPath)
	if err != nil {
		return CaseResult{}, err
	}

	pr, err := executor.Run(context.Background(), solutionPath, input, timeout, extraEnv)
	if err != nil {
		return CaseResult{}, err
	}
	return judge(name, string(input), string(expected), pr, debug, tolerance), nil
}

func ensureTests(reporter Reporter, contest, task, taskDir, testsDir, metaPath string, refresh bool) (*meta, error) {
	if !refresh {
		_, errTests := os.Stat(testsDir)
		if errTests == nil {
			if m, err := loadMeta(metaPath); err == nil {
				return m, nil
			}
		}
	}

	reporter.Fetching(contest, task)
	prob, err := fetchProblem(contest, task)
	if err != nil {
		return nil, fmt.Errorf("AtCoder から取得できませんでした: %w", err)
	}

	if err := os.MkdirAll(testsDir, 0o755); err != nil {
		return nil, err
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
			return nil, err
		}
		if err := os.WriteFile(outPath, []byte(s.Output), 0o644); err != nil {
			return nil, err
		}
	}

	mta := &meta{
		Contest:     contest,
		Task:        task,
		URL:         prob.URL,
		TimeLimitMs: prob.TimeLimitMs,
		FetchedAt:   time.Now(),
	}
	if err := saveMeta(metaPath, mta); err != nil {
		return nil, err
	}
	return mta, nil
}

// filterCases は要求されたケース名 (例: "1", "01", "03") の和集合に含まれる
// ケースだけを並びを保って返す。数値のみの指定は 2 桁ゼロ埋めに正規化する。
// 該当するケースが 1 つも無ければエラー。
func filterCases(all, requested []string) ([]string, error) {
	want := make(map[string]bool, len(requested))
	for _, r := range requested {
		want[normalizeCaseName(r)] = true
	}
	var out []string
	for _, name := range all {
		if want[name] {
			out = append(out, name)
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
