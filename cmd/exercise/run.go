package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/cry999/atcoder-daily-training/internal/layout"
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
	var inFile string
	flags.StringVar(&inFile, "in", "", "Input file (use '-' or omit for parent stdin)")
	flags.StringVar(&inFile, "i", "", "Input file (use '-' or omit for parent stdin)")
	var outFile string
	flags.StringVar(&outFile, "out", "", "Expected output file. When set, stdout is judged against this file.")
	flags.StringVar(&outFile, "o", "", "Expected output file. When set, stdout is judged against this file.")
	timeoutFlag := flags.Duration("timeout", 0, "Override time limit (e.g. 5s, 500ms). Defaults to the problem's time limit or 2s if no meta.toml.")
	tolFlag := flags.Float64("tolerance", 0, "Absolute/relative tolerance for float token comparison in --out judge mode (e.g. 1e-9). 0 or unset → use default 1e-6.")
	var verbose bool
	flags.BoolVar(&verbose, "v", false, "Show the input that was fed in as well")
	flags.BoolVar(&verbose, "verbose", false, "Show the input that was fed in as well")
	var debug bool
	flags.BoolVar(&debug, "d", false, "Run with DEBUG=1 and split [DEBUG]-prefixed lines into a separate section")
	flags.BoolVar(&debug, "debug", false, "Run with DEBUG=1 and split [DEBUG]-prefixed lines into a separate section")
	layoutFlag := flags.String("layout", "auto", "Solution file layout (auto, abc, exercise). auto picks abc for abc<NNN>, exercise otherwise.")
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

	lay, err := layout.Parse(*layoutFlag, contest)
	if err != nil {
		return 2, err
	}

	return runexec.Run(runexec.Options{
		Contest:     contest,
		Task:        task,
		Layout:      lay,
		InFile:      inFile,
		OutFile:     outFile,
		Timeout:     *timeoutFlag,
		Tolerance:   *tolFlag,
		Debug:       debug,
		ExecutorFor: selectRunExecutor,
		Reporter:    ui.NewRunReporter(verbose),
		ChatRunner:  runChat,
	})
}

func runChat(spawn runexec.ChatSpawner, header runexec.ChatHeader) (*runner.ProcessResult, error) {
	return ui.RunChat(ui.Spawner(spawn), ui.ChatHeader{
		Task:        header.Task,
		Contest:     header.Contest,
		TimeLimitMs: header.TimeLimitMs,
		Debug:       header.Debug,
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
