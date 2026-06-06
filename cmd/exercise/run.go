package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/cry999/atcoder-daily-training/internal/runexec"
	"github.com/cry999/atcoder-daily-training/internal/runner"
	"github.com/cry999/atcoder-daily-training/internal/ui"
)

func cmdRun(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := args[0]

	flags := flag.NewFlagSet("run", flag.ContinueOnError)
	taskFlag := flags.String("task", "", `AtCoder task ID, or short form (e.g. "d" expands to "<contest>_d")`)
	stdinFlag := flags.String("stdin", "", "Input file (use '-' or omit for parent stdin)")
	timeoutFlag := flags.Duration("timeout", 0, "Override time limit (e.g. 5s, 500ms). Defaults to the problem's time limit or 2s if no meta.toml.")
	var verbose bool
	flags.BoolVar(&verbose, "v", false, "Show the input that was fed in as well")
	flags.BoolVar(&verbose, "verbose", false, "Show the input that was fed in as well")
	var debug bool
	flags.BoolVar(&debug, "d", false, "Run with DEBUG=1 and split [DEBUG]-prefixed lines into a separate section")
	flags.BoolVar(&debug, "debug", false, "Run with DEBUG=1 and split [DEBUG]-prefixed lines into a separate section")
	flags.SetOutput(os.Stderr)

	if err := flags.Parse(args[1:]); err != nil {
		return 2, err
	}
	task := *taskFlag
	if task == "" {
		return 2, errors.New("--task is required")
	}
	if !strings.Contains(task, "_") {
		task = contest + "_" + task
	}

	return runexec.Run(runexec.Options{
		Contest:     contest,
		Task:        task,
		StdinFile:   *stdinFlag,
		Timeout:     *timeoutFlag,
		Debug:       debug,
		ExecutorFor: selectRunExecutor,
		Reporter:    ui.NewRunReporter(verbose),
	})
}

func selectRunExecutor(sourcePath string) (runexec.Executor, error) {
	ext := filepath.Ext(sourcePath)
	switch ext {
	case ".py":
		return runner.NewPython()
	default:
		return nil, fmt.Errorf("unsupported extension: %s", ext)
	}
}
