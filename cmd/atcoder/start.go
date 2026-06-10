package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"io/fs"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"time"

	"golang.org/x/term"

	"github.com/cry999/atcoder-daily-training/internal/config"
	"github.com/cry999/atcoder-daily-training/internal/layout"
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

// startAction は watch 待機中のキー入力に対応する動作。
type startAction int

const (
	actNone startAction = iota
	actRerun
	actQuit
	actInteractive
)

// keyToAction は 1 バイトのキー入力をアクションに写す純粋関数。
// raw モードでは Ctrl+C はシグナルにならず 0x03 のバイトで届くため、ここで終了に倒す。
func keyToAction(b byte) startAction {
	switch b {
	case 'q', 'Q', 0x03: // 0x03 = Ctrl+C (raw モード)
		return actQuit
	case 'i', 'I':
		return actInteractive
	default:
		return actNone
	}
}

// runStartWatch は start 用の watch ループ。test --watch と同じく保存検知で再実行し、
// さらに待機中のキー (q=終了 / i=インタラクティブ) を mtime と多重化する。untilPass なら
// サンプル全通過で終了。runTestWatch (test --watch 用) はキー層を持たず別に温存する。
func runStartWatch(contest, task string, lay layout.Layout, refresh bool,
	buildOpts func(refresh bool) testexec.Options, untilPass, debug bool,
	timeout time.Duration, tolerance float64) (int, error) {
	if !ui.IsStdoutTerminal() {
		return 2, errors.New("start --watch requires a terminal (stdout is not a TTY)")
	}
	solutionPath, err := lay.SolutionPath(contest, task)
	if err != nil {
		return 2, err
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()

	w := watch.New(solutionPath, watchPollInterval, watchDebounce)
	firstRun := true
	for {
		ui.ClearScreen()
		ui.WatchHeader(solutionPath)

		code, runErr := testexec.Run(buildOpts(refresh && firstRun))
		if runErr != nil {
			fmt.Fprintln(os.Stderr, "atcoder start:", runErr)
		}
		firstRun = false

		// --until-pass: 全サンプル通過 (code==0) で終了。
		if untilPass && runErr == nil && code == 0 {
			fmt.Println()
			return 0, nil
		}

		ui.StartWatchFooter(solutionPath)

		switch waitForAction(ctx, w) {
		case actQuit:
			fmt.Println()
			return 0, nil
		case actInteractive:
			// 通常モードで既存の chat を起動 (bubbletea が端末を自前管理)。抜けたら再実行。
			// start は自前の watch ループで回すので chat 側の auto-restart は使わない。
			if _, err := runAdHoc(contest, task, lay, "", "", true, false, debug, false, timeout, tolerance); err != nil {
				fmt.Fprintln(os.Stderr, "atcoder start:", err)
			}
		case actRerun:
			// ループ先頭へ (再実行)。
		}
	}
}

// waitForAction は watch の待機フェーズ。/dev/tty を raw にして 1 キーを拾い、mtime の
// 変化と多重化する。q/Ctrl+C → 終了、i → インタラクティブ、保存 → 再実行。raw 化に
// 失敗したらキー無効で mtime のみの待機にフォールバックする (機能低下のみ)。
func waitForAction(ctx context.Context, w *watch.Watcher) startAction {
	tty, err := os.OpenFile("/dev/tty", os.O_RDONLY, 0)
	if err != nil {
		return waitMtimeOnly(ctx, w)
	}
	defer tty.Close()
	old, err := term.MakeRaw(int(tty.Fd()))
	if err != nil {
		return waitMtimeOnly(ctx, w)
	}
	defer term.Restore(int(tty.Fd()), old)

	keyCh := make(chan byte, 4)
	done := make(chan struct{})
	defer close(done) // goroutine を止める合図。tty.Close (defer) が Read を解く。
	go func() {
		buf := make([]byte, 1)
		for {
			n, err := tty.Read(buf)
			if n > 0 {
				select {
				case keyCh <- buf[0]:
				case <-done:
					return
				}
			}
			if err != nil {
				return
			}
		}
	}()

	ticker := time.NewTicker(watchPollInterval)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return actQuit
		case <-ticker.C:
			if w.Changed() {
				return actRerun
			}
		case b := <-keyCh:
			if a := keyToAction(b); a != actNone {
				return a
			}
		}
	}
}

// waitMtimeOnly は raw 化できない環境向けのフォールバック。キー無効で mtime のみ待つ。
func waitMtimeOnly(ctx context.Context, w *watch.Watcher) startAction {
	if w.WaitForChange(ctx) {
		return actRerun
	}
	return actQuit
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
