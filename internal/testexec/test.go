package testexec

import (
	"context"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

type Executor interface {
	Run(ctx context.Context, source string, input []byte, timeout time.Duration) (*runner.ProcessResult, error)
}

type ExecutorFor func(sourcePath string) (Executor, error)

type Options struct {
	Contest     string
	Task        string
	Refresh     bool
	Timeout     time.Duration // 0 → use the problem's time_limit_ms from meta.toml
	ExecutorFor ExecutorFor
	Reporter    Reporter
}

func Run(opts Options) (int, error) {
	y, m, d := time.Now().Local().Date()
	dateDir := filepath.Join("exercise",
		fmt.Sprintf("%04d", y),
		fmt.Sprintf("%02d", m),
		fmt.Sprintf("%02d", d),
	)
	solutionPath := filepath.Join(dateDir, opts.Task+".py")
	if _, err := os.Stat(solutionPath); err != nil {
		return 1, fmt.Errorf("解答ファイルが見つかりません: %s", solutionPath)
	}

	taskDir := filepath.Join(dateDir, opts.Task)
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

	timeout := time.Duration(mta.TimeLimitMs) * time.Millisecond
	if opts.Timeout > 0 {
		timeout = opts.Timeout
	}
	opts.Reporter.Header(opts.Task, opts.Contest, mta.TimeLimitMs, int(timeout/time.Millisecond), len(names))
	passed := 0
	for _, name := range names {
		cr, err := runCase(executor, solutionPath, testsDir, name, timeout)
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

func runCase(executor Executor, solutionPath, testsDir, name string, timeout time.Duration) (CaseResult, error) {
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

	pr, err := executor.Run(context.Background(), solutionPath, input, timeout)
	if err != nil {
		return CaseResult{}, err
	}
	return judge(name, string(input), string(expected), pr), nil
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
