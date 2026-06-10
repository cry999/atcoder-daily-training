package main

import (
	"errors"
	"flag"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cachepath"
	"github.com/cry999/atcoder-daily-training/internal/config"
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/runner"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
	"github.com/cry999/atcoder-daily-training/internal/ui"
	"github.com/cry999/atcoder-daily-training/internal/watch"
)

// cmdStart は問題への着手をまとめる: レイアウトに応じた解答ファイルを (無ければ)
// 用意し、そのまま test --watch の編集ループに入る。`--until-pass` でサンプル全通過時に
// 終了する。新しい実行・判定ロジックは持たず、layout / testexec / watch を束ねるだけ。
func cmdStart(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := args[0]

	cfg, err := config.Load()
	if err != nil {
		return 2, err
	}

	flags := flag.NewFlagSet("start", flag.ContinueOnError)
	taskFlag := addTaskFlag(flags)
	untilPass := flags.Bool("until-pass", false, "Exit when all sample tests pass (otherwise watch until Ctrl+C).")
	refresh := flags.Bool("refresh", false, "Force refetch sample cases on the first run")
	timeoutFlag := flags.Duration("timeout", 0, "Override time limit (e.g. 5s, 500ms). Defaults to the problem's time limit (2s if unknown).")
	tolFlag := flags.Float64("tolerance", 0, "Float token comparison tolerance (e.g. 1e-9). 0 or unset → default 1e-6.")
	var debug bool
	flags.BoolVar(&debug, "d", false, "Run with DEBUG=1 and special-case [DEBUG]-prefixed output lines")
	flags.BoolVar(&debug, "debug", false, "Run with DEBUG=1 and special-case [DEBUG]-prefixed output lines")
	var sideBySide bool
	flags.BoolVar(&sideBySide, "s", cfg.Test.SideBySide, "Show diff side-by-side (expected on left, actual on right)")
	flags.BoolVar(&sideBySide, "side-by-side", cfg.Test.SideBySide, "Show diff side-by-side (expected on left, actual on right)")
	var jobs int
	flags.IntVar(&jobs, "jobs", 0, "Number of test cases to run in parallel. 0 → number of CPUs (capped at the case count).")
	flags.IntVar(&jobs, "j", 0, "Number of test cases to run in parallel. 0 → number of CPUs (capped at the case count).")
	layoutFlag := addLayoutFlag(flags)
	flags.SetOutput(os.Stderr)

	if err := flags.Parse(args[1:]); err != nil {
		return 2, err
	}
	task := *taskFlag
	if task == "" {
		return 2, errors.New("--task is required")
	}
	// Short form: `--task d` → `<contest>_d` when no underscore is present.
	if !strings.Contains(task, "_") {
		task = contest + "_" + task
	}

	lay, err := resolveLayout(*layoutFlag, contest)
	if err != nil {
		return 2, err
	}

	// 解答ファイルを用意 (無ければ空ファイル)。既存は温存する。
	path, created, err := ensureSolutionFile(lay, contest, task)
	if err != nil {
		return 1, err
	}
	if created {
		fmt.Printf("created: %s\n", path)
	} else {
		fmt.Printf("solution: %s (exists)\n", path)
	}

	buildOpts := func(refresh bool) testexec.Options {
		return testexec.Options{
			Contest:     contest,
			Task:        task,
			Layout:      lay,
			Refresh:     refresh,
			Timeout:     *timeoutFlag,
			Debug:       debug,
			Tolerance:   *tolFlag,
			Concurrency: jobs,
			ExecutorFor: selectExecutor,
			Reporter:    ui.NewTestReporter(false, sideBySide),
		}
	}

	return runStartWatch(contest, task, lay, *refresh, buildOpts, *untilPass, debug, *timeoutFlag, *tolFlag)
}

// runStartWatch は start の TTY 体験を上下分割画面で駆動する。下ペイン = 対話 chat
// (auto-restart)、上ペイン = watch 要約 (保存検知でサンプルを自動再判定)。両方を 1 つの
// bubbletea プログラム (ui.RunStartSplit) に合成し、同時に動かし続ける。untilPass なら
// サンプル全通過で終了。runTestWatch (test --watch 用) は別系統で不変。
func runStartWatch(contest, task string, lay layout.Layout, refresh bool,
	buildOpts func(refresh bool) testexec.Options, untilPass, debug bool,
	timeout time.Duration, tolerance float64) (int, error) {
	if !ui.IsStdoutTerminal() {
		return 2, errors.New("start requires a terminal (stdout is not a TTY)")
	}
	solutionPath, err := lay.SolutionPath(contest, task)
	if err != nil {
		return 2, err
	}

	// 下ペイン: chat の子プロセス起動 (auto-restart)。
	ex, err := selectRunExecutor(solutionPath)
	if err != nil {
		return 1, err
	}
	var extraEnv []string
	if debug {
		extraEnv = []string{"DEBUG=1"}
	}
	spawn := func() (*runner.ChatHandle, error) {
		return ex.StartChat(solutionPath, extraEnv)
	}

	// 上ペイン: 保存検知でサンプルを再判定する。判定は stdout に書かず捕捉 Reporter で
	// 結果だけ集めて要約にする (bubbletea 描画と衝突させない)。初回のみ refresh を効かせる。
	w := watch.New(solutionPath, watchPollInterval, watchDebounce)
	firstRefresh := refresh
	runSamples := func() ui.SampleSummary {
		rep := testexec.NewSummaryReporter()
		opts := buildOpts(firstRefresh)
		firstRefresh = false
		opts.Reporter = rep
		code, runErr := testexec.Run(opts)
		passed, total, cases := rep.Result()
		verdicts := make([]ui.CaseVerdict, 0, len(cases))
		for _, c := range cases {
			verdicts = append(verdicts, ui.CaseVerdict{Name: c.Name, Label: caseLabel(c.Status), OK: c.Status == testexec.Pass})
		}
		s := ui.SampleSummary{Passed: passed, Total: total, Cases: verdicts, At: time.Now()}
		if runErr != nil {
			s.Err = runErr
		} else {
			s.AllPassed = code == 0 && total > 0
		}
		return s
	}

	timeLimitMs := 2000
	if timeout > 0 {
		timeLimitMs = int(timeout / time.Millisecond)
	}
	// WatchPath を渡すと、保存検知で下ペインの chat も最新コードで reload する
	// (test --interactive と同じ挙動)。上ペインの再判定 (Changed) と合わせ、
	// 保存で対話・サンプルの両方が新コードを反映する。
	return ui.RunStartSplit(ui.StartSplitConfig{
		SolutionPath: solutionPath,
		Spawn:        ui.Spawner(spawn),
		Header:       ui.ChatHeader{Task: task, Contest: contest, TimeLimitMs: timeLimitMs, Debug: debug, AutoRestart: true, WatchPath: solutionPath, Submit: chatSubmitFunc(contest, task, lay), TaskDir: cachepath.Task(contest, task), Tolerance: tolerance},
		RunSamples:   runSamples,
		Changed:      w.Changed,
		UntilPass:    untilPass,
		Poll:         watchPollInterval,
	})
}

// caseLabel は per-case の判定結果を AtCoder 流の verdict 表記にする
// (watch ペインの per-case 表示用)。Pass=AC・Fail=WA・TLE・RE。
func caseLabel(s testexec.CaseStatus) string {
	switch s {
	case testexec.Pass:
		return "AC"
	case testexec.TLE:
		return "TLE"
	case testexec.RE:
		return "RE"
	default: // Fail
		return "WA"
	}
}

// ensureSolutionFile は lay/contest/task の解答パスを返し、無ければ親 dir を作って
// 空ファイルを生成する (既存ファイルは温存)。created はこの呼び出しで作ったか。
func ensureSolutionFile(lay layout.Layout, contest, task string) (path string, created bool, err error) {
	path, err = lay.SolutionPath(contest, task)
	if err != nil {
		return "", false, err
	}
	if _, err := os.Stat(path); err == nil {
		return path, false, nil // 既存は温存
	} else if !errors.Is(err, fs.ErrNotExist) {
		return "", false, err
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return "", false, err
	}
	if err := os.WriteFile(path, nil, 0o644); err != nil {
		return "", false, err
	}
	return path, true, nil
}
