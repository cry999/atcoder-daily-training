package main

import (
	"bytes"
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/BurntSushi/toml"
)

type meta struct {
	Contest     string    `toml:"contest"`
	Task        string    `toml:"task"`
	URL         string    `toml:"url"`
	TimeLimitMs int       `toml:"time_limit_ms"`
	FetchedAt   time.Time `toml:"fetched_at"`
}

func cmdTest(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := args[0]

	fs := flag.NewFlagSet("test", flag.ContinueOnError)
	taskFlag := fs.String("task", "", "AtCoder task ID (required)")
	refresh := fs.Bool("refresh", false, "Force refetch sample cases")
	fs.SetOutput(os.Stderr)

	if err := fs.Parse(args[1:]); err != nil {
		return 2, err
	}
	task := *taskFlag
	if task == "" {
		return 2, errors.New("--task is required")
	}

	// 1. Locate solution file (today's exercise directory).
	y, m, d := time.Now().Local().Date()
	dateDir := filepath.Join("exercise",
		fmt.Sprintf("%04d", y),
		fmt.Sprintf("%02d", m),
		fmt.Sprintf("%02d", d),
	)
	solutionPath := filepath.Join(dateDir, task+".py")
	if _, err := os.Stat(solutionPath); err != nil {
		return 1, fmt.Errorf("解答ファイルが見つかりません: %s", solutionPath)
	}

	// 2. Prepare cache paths.
	taskDir := filepath.Join(dateDir, task)
	testsDir := filepath.Join(taskDir, "tests")
	metaPath := filepath.Join(taskDir, "meta.toml")

	// 3. Use cache or fetch.
	mta, err := ensureTests(contest, task, taskDir, testsDir, metaPath, *refresh)
	if err != nil {
		return 1, err
	}

	// 4. Resolve Python interpreter.
	python := findPython()
	if python == "" {
		return 1, errors.New("python が見つかりません (.venv/bin/python も PATH の python も見つかりません)")
	}

	// 5. Enumerate cases.
	names, err := listCases(testsDir)
	if err != nil {
		return 1, err
	}
	if len(names) == 0 {
		return 1, errors.New("テストケースが見つかりません")
	}

	// 6. Run.
	fmt.Printf("%s  contest=%s  time_limit=%dms  tests=%d\n\n",
		task, contest, mta.TimeLimitMs, len(names))

	timeout := time.Duration(mta.TimeLimitMs) * time.Millisecond
	passed := 0
	for _, name := range names {
		ok, err := runCase(python, solutionPath, testsDir, name, timeout)
		if err != nil {
			return 1, err
		}
		if ok {
			passed++
		}
	}

	fmt.Printf("\nResult: %d/%d PASS\n", passed, len(names))
	if passed != len(names) {
		return 1, nil
	}
	return 0, nil
}

func ensureTests(contest, task, taskDir, testsDir, metaPath string, refresh bool) (*meta, error) {
	if !refresh {
		_, errTests := os.Stat(testsDir)
		var mta meta
		_, errMeta := toml.DecodeFile(metaPath, &mta)
		if errTests == nil && errMeta == nil {
			return &mta, nil
		}
	}

	fmt.Printf("Fetching %s/%s from AtCoder...\n", contest, task)
	prob, err := fetchProblem(contest, task)
	if err != nil {
		return nil, fmt.Errorf("AtCoder から取得できませんでした: %w", err)
	}

	if err := os.MkdirAll(testsDir, 0o755); err != nil {
		return nil, err
	}
	// Wipe stale test files so removed cases don't linger.
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
	f, err := os.Create(metaPath)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	if err := toml.NewEncoder(f).Encode(mta); err != nil {
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

func runCase(python, solutionPath, testsDir, name string, timeout time.Duration) (bool, error) {
	inPath := filepath.Join(testsDir, name+".in")
	outPath := filepath.Join(testsDir, name+".out")

	input, err := os.ReadFile(inPath)
	if err != nil {
		return false, err
	}
	expected, err := os.ReadFile(outPath)
	if err != nil {
		return false, err
	}

	got, stderrOut, elapsed, runErr := executePython(python, solutionPath, input, timeout)
	ms := elapsed.Milliseconds()

	switch {
	case errors.Is(runErr, errTLE):
		fmt.Printf("[%s] TLE   %d ms\n", name, ms)
		return false, nil
	case runErr != nil:
		fmt.Printf("[%s] RE    %d ms\n", name, ms)
		printRE(runErr, stderrOut)
		return false, nil
	}

	expNorm := normalizeOutput(string(expected))
	gotNorm := normalizeOutput(got)
	if expNorm == gotNorm {
		fmt.Printf("[%s] PASS  %d ms\n", name, ms)
		return true, nil
	}

	fmt.Printf("[%s] FAIL  %d ms\n", name, ms)
	printDiff(expNorm, gotNorm)
	return false, nil
}

var errTLE = errors.New("time limit exceeded")

func executePython(python, solutionPath string, input []byte, timeout time.Duration) (stdout, stderr string, elapsed time.Duration, err error) {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	cmd := exec.CommandContext(ctx, python, solutionPath)
	cmd.Stdin = bytes.NewReader(input)
	var outBuf, errBuf bytes.Buffer
	cmd.Stdout = &outBuf
	cmd.Stderr = &errBuf

	start := time.Now()
	runErr := cmd.Run()
	elapsed = time.Since(start)

	if errors.Is(ctx.Err(), context.DeadlineExceeded) {
		return outBuf.String(), errBuf.String(), elapsed, errTLE
	}
	return outBuf.String(), errBuf.String(), elapsed, runErr
}

func normalizeOutput(s string) string {
	s = strings.ReplaceAll(s, "\r\n", "\n")
	return strings.TrimRight(s, "\n")
}

func printRE(err error, stderrOut string) {
	fmt.Printf("       %s\n", err)
	stderrOut = strings.TrimRight(stderrOut, "\n")
	if stderrOut == "" {
		return
	}
	if len(stderrOut) > 1000 {
		stderrOut = stderrOut[:1000] + "... (truncated)"
	}
	fmt.Printf("       stderr:\n")
	for _, line := range strings.Split(stderrOut, "\n") {
		fmt.Printf("         %s\n", line)
	}
}

func printDiff(expected, got string) {
	fmt.Printf("       expected:\n")
	for _, l := range strings.Split(expected, "\n") {
		fmt.Printf("         %s\n", l)
	}
	fmt.Printf("       got:\n")
	for _, l := range strings.Split(got, "\n") {
		fmt.Printf("         %s\n", l)
	}
	fmt.Printf("       diff:\n")
	expLines := strings.Split(expected, "\n")
	gotLines := strings.Split(got, "\n")
	maxL := len(expLines)
	if len(gotLines) > maxL {
		maxL = len(gotLines)
	}
	for i := 0; i < maxL; i++ {
		var e, g string
		hasE := i < len(expLines)
		hasG := i < len(gotLines)
		if hasE {
			e = expLines[i]
		}
		if hasG {
			g = gotLines[i]
		}
		if hasE && hasG && e == g {
			continue
		}
		if hasE {
			fmt.Printf("         - %s\n", e)
		}
		if hasG {
			fmt.Printf("         + %s\n", g)
		}
	}
}

func findPython() string {
	if root, err := findRepoRoot(); err == nil {
		candidate := filepath.Join(root, ".venv", "bin", "python")
		if _, err := os.Stat(candidate); err == nil {
			return candidate
		}
	}
	if p, err := exec.LookPath("python"); err == nil {
		return p
	}
	if p, err := exec.LookPath("python3"); err == nil {
		return p
	}
	return ""
}

func findRepoRoot() (string, error) {
	dir, err := os.Getwd()
	if err != nil {
		return "", err
	}
	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "", errors.New("go.mod not found in any parent")
		}
		dir = parent
	}
}
