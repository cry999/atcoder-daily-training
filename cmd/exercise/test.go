package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"

	"github.com/cry999/atcoder-daily-training/internal/runner"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

func cmdTest(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := args[0]

	flags := flag.NewFlagSet("test", flag.ContinueOnError)
	taskFlag := flags.String("task", "", "AtCoder task ID (required)")
	refresh := flags.Bool("refresh", false, "Force refetch sample cases")
	flags.SetOutput(os.Stderr)

	if err := flags.Parse(args[1:]); err != nil {
		return 2, err
	}
	task := *taskFlag
	if task == "" {
		return 2, errors.New("--task is required")
	}

	return testexec.Run(testexec.Options{
		Contest:     contest,
		Task:        task,
		Refresh:     *refresh,
		ExecutorFor: selectExecutor,
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
