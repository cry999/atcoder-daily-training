package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/cry999/atcoder-daily-training/internal/runner"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
	"github.com/cry999/atcoder-daily-training/internal/ui"
)

func cmdTest(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := args[0]

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
	exerciseDir := flags.String("exercise-dir", "", "Override solution directory (default: today's exercise/YYYY/MM/DD)")
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

	return testexec.Run(testexec.Options{
		Contest:     contest,
		Task:        task,
		Refresh:     *refresh,
		Timeout:     *timeoutFlag,
		Debug:       debug,
		ExerciseDir: *exerciseDir,
		ExecutorFor: selectExecutor,
		Reporter:    ui.NewTestReporter(verbose),
	})
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
