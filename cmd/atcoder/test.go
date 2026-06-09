package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/config"
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/runner"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
	"github.com/cry999/atcoder-daily-training/internal/ui"
	"github.com/cry999/atcoder-daily-training/internal/watch"
)

const (
	// watch モードのポーリング間隔とデバウンス待機。
	watchPollInterval = 200 * time.Millisecond
	watchDebounce     = 120 * time.Millisecond
)

func cmdTest(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := args[0]

	// ユーザ設定を読み、フラグのデフォルトに反映する (優先順位: flag > config > default)。
	// 設定が無いのは正常 (全デフォルト)。パース失敗だけ exit 2。
	cfg, err := config.Load()
	if err != nil {
		return 2, err
	}

	flags := flag.NewFlagSet("test", flag.ContinueOnError)
	taskFlag := flags.String("task", "", `AtCoder task ID, or short form (e.g. "d" expands to "<contest>_d")`)
	refresh := flags.Bool("refresh", false, "Force refetch sample cases")
	timeoutFlag := flags.Duration("timeout", 0, "Override time limit (e.g. 5s, 500ms). Defaults to the problem's time limit.")
	var verbose bool
	flags.BoolVar(&verbose, "v", false, "Show input/output content for each case")
	flags.BoolVar(&verbose, "verbose", false, "Show input/output content for each case")
	var debug bool
	flags.BoolVar(&debug, "d", false, "Run with DEBUG=1 and filter [DEBUG]-prefixed lines from comparison")
	flags.BoolVar(&debug, "debug", false, "Run with DEBUG=1 and filter [DEBUG]-prefixed lines from comparison")
	var caseStr string
	flags.StringVar(&caseStr, "case", "", `Run only the specified case(s); comma-separated (e.g. "01" or "1,3")`)
	flags.StringVar(&caseStr, "c", "", `Run only the specified case(s); comma-separated (e.g. "01" or "1,3")`)
	tolFlag := flags.Float64("tolerance", 0, "Absolute/relative tolerance for float token comparison (e.g. 1e-9). 0 or unset → use default 1e-6.")
	// side-by-side のデフォルトは config から取る (flag > config > default)。
	// 設定で true でも `--side-by-side=false` でその回だけ unified に戻せる。
	var sideBySide bool
	flags.BoolVar(&sideBySide, "s", cfg.Test.SideBySide, "Show diff side-by-side (expected on left, actual on right)")
	flags.BoolVar(&sideBySide, "side-by-side", cfg.Test.SideBySide, "Show diff side-by-side (expected on left, actual on right)")
	layoutFlag := flags.String("layout", "auto", "Solution file layout (auto, abc, exercise). auto picks abc for abc<NNN>, exercise otherwise.")
	var jobs int
	flags.IntVar(&jobs, "jobs", 0, "Number of test cases to run in parallel. 0 → number of CPUs (capped at the case count).")
	flags.IntVar(&jobs, "j", 0, "Number of test cases to run in parallel. 0 → number of CPUs (capped at the case count).")
	var watchMode bool
	flags.BoolVar(&watchMode, "watch", false, "Re-run the tests whenever the solution file changes. Ctrl+C to quit. Requires a terminal.")
	flags.BoolVar(&watchMode, "w", false, "Re-run the tests whenever the solution file changes. Ctrl+C to quit. Requires a terminal.")
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

	lay, err := layout.Parse(*layoutFlag, contest)
	if err != nil {
		return 2, err
	}

	var cases []string
	if caseStr != "" {
		for _, p := range strings.Split(caseStr, ",") {
			if p = strings.TrimSpace(p); p != "" {
				cases = append(cases, p)
			}
		}
	}

	// buildOpts は 1 回分の実行オプションを作る。watch では毎回新しい Reporter を
	// 作り直し (ライブ表示のプログラムを使い回さない)、refresh は呼び出し側が制御する。
	buildOpts := func(refresh bool) testexec.Options {
		return testexec.Options{
			Contest:     contest,
			Task:        task,
			Layout:      lay,
			Refresh:     refresh,
			Timeout:     *timeoutFlag,
			Debug:       debug,
			Cases:       cases,
			Tolerance:   *tolFlag,
			Concurrency: jobs,
			ExecutorFor: selectExecutor,
			Reporter:    ui.NewTestReporter(verbose, sideBySide),
		}
	}

	if watchMode {
		return runTestWatch(contest, task, lay, *refresh, buildOpts)
	}

	code, err := testexec.Run(buildOpts(*refresh))
	return code, err
}

// runTestWatch は解答ファイルの保存を監視し、変更のたびにテストを再実行する。
// Ctrl+C で抜けて exit 0。判定結果 (FAIL/RE/TLE) ではループを止めない。
func runTestWatch(contest, task string, lay layout.Layout, refresh bool, buildOpts func(refresh bool) testexec.Options) (int, error) {
	if !ui.IsStdoutTerminal() {
		return 2, errors.New("--watch requires a terminal (stdout is not a TTY)")
	}
	solutionPath, err := lay.SolutionPath(contest, task)
	if err != nil {
		return 2, err
	}

	// Ctrl+C で監視ループを抜ける。各回の実行中 (bubbletea) でも SIGINT は届く。
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()

	w := watch.New(solutionPath, watchPollInterval, watchDebounce)
	firstRun := true
	for {
		ui.ClearScreen()
		ui.WatchHeader(solutionPath)

		// 初回だけ --refresh を効かせる (毎保存での再 fetch を避ける)。
		if _, err := testexec.Run(buildOpts(refresh && firstRun)); err != nil {
			fmt.Fprintln(os.Stderr, "atcoder test:", err)
		}
		firstRun = false

		ui.WatchFooter(solutionPath)

		if !w.WaitForChange(ctx) {
			// Ctrl+C: 改行して正常終了。
			fmt.Println()
			return 0, nil
		}
	}
}

func selectExecutor(sourcePath string) (testexec.Executor, error) {
	ext := filepath.Ext(sourcePath)
	switch ext {
	case ".py":
		return runner.NewPython()
	default:
		return nil, fmt.Errorf("unsupported extension: %s", ext)
	}
}
