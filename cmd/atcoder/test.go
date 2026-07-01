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

	"github.com/cry999/atcoder-daily-training/internal/cliargs"
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
	// 位置引数 (contest) とフラグを任意順で受けられるよう、flag.Parse の前に分離する。
	flagArgs, positionals := cliargs.Split(args)
	if len(positionals) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := positionals[0]

	// ユーザ設定を読み、フラグのデフォルトに反映する (優先順位: flag > config > default)。
	// 設定が無いのは正常 (全デフォルト)。パース失敗だけ exit 2。
	cfg, err := config.Load()
	if err != nil {
		return 2, err
	}

	flags := flag.NewFlagSet("test", flag.ContinueOnError)
	taskFlag := addTaskFlag(flags)
	refresh := flags.Bool("refresh", false, "Force refetch sample cases")
	timeoutFlag := flags.Duration("timeout", 0, "Override time limit (e.g. 5s, 500ms). Defaults to the problem's time limit (2s if unknown).")
	var verbose bool
	flags.BoolVar(&verbose, "v", false, "Show the input fed to the solution (and per-case I/O in sample mode)")
	flags.BoolVar(&verbose, "verbose", false, "Show the input fed to the solution (and per-case I/O in sample mode)")
	var debug bool
	flags.BoolVar(&debug, "d", false, "Run with DEBUG=1 and special-case [DEBUG]-prefixed output lines")
	flags.BoolVar(&debug, "debug", false, "Run with DEBUG=1 and special-case [DEBUG]-prefixed output lines")
	var pp bool
	flags.BoolVar(&pp, "pp", false, "Pretty-print valid-JSON [DEBUG] payloads in the debug: section (2-space indent). Orthogonal to -d; no effect without it.")
	var caseStr string
	flags.StringVar(&caseStr, "case", "", `Run only the specified case(s); comma-separated (e.g. "01" or "1,3")`)
	flags.StringVar(&caseStr, "c", "", `Run only the specified case(s); comma-separated (e.g. "01" or "1,3")`)
	tolFlag := flags.Float64("tolerance", 0, "Float token comparison tolerance for sample judging or --out (e.g. 1e-9). 0 or unset → default 1e-6.")
	// side-by-side のデフォルトは config から取る (flag > config > default)。
	// 設定で true でも `--side-by-side=false` でその回だけ unified に戻せる。
	var sideBySide bool
	flags.BoolVar(&sideBySide, "s", cfg.Test.SideBySide, "Show diff side-by-side (expected on left, actual on right)")
	flags.BoolVar(&sideBySide, "side-by-side", cfg.Test.SideBySide, "Show diff side-by-side (expected on left, actual on right)")
	layoutFlag := addLayoutFlag(flags)
	// ad-hoc / 対話モード (旧 run コマンド)。これらを明示したときだけ、サンプル判定
	// (testexec) ではなく ad-hoc 実行 (runexec) に振り分ける。明示しなければ既定は
	// サンプル判定で、stdin がパイプされていてもモードは変わらない (魔法なし)。
	var inFile string
	flags.StringVar(&inFile, "in", "", "Ad-hoc input file ('-' = stdin). Switches to ad-hoc run mode (no sample judging).")
	flags.StringVar(&inFile, "i", "", "Ad-hoc input file ('-' = stdin). Switches to ad-hoc run mode (no sample judging).")
	var outFile string
	flags.StringVar(&outFile, "out", "", "Judge a single ad-hoc run against this expected output (ad-hoc mode; reads stdin if no --in).")
	flags.StringVar(&outFile, "o", "", "Judge a single ad-hoc run against this expected output (ad-hoc mode; reads stdin if no --in).")
	var interactive bool
	flags.BoolVar(&interactive, "interactive", false, "Interactive mode: wire the solution's stdin/stdout to the parent (live). chat TUI on a TTY.")
	flags.BoolVar(&interactive, "I", false, "Interactive mode: wire the solution's stdin/stdout to the parent (live). chat TUI on a TTY.")
	var autoRestart bool
	flags.BoolVar(&autoRestart, "auto-restart", false, "With --interactive (TTY): re-run the solution each time the child exits (Ctrl+D to stop, Ctrl+C to abort).")
	flags.BoolVar(&autoRestart, "R", false, "With --interactive (TTY): re-run the solution each time the child exits (Ctrl+D to stop, Ctrl+C to abort).")
	var jobs int
	flags.IntVar(&jobs, "jobs", 0, "Number of test cases to run in parallel. 0 → number of CPUs (capped at the case count).")
	flags.IntVar(&jobs, "j", 0, "Number of test cases to run in parallel. 0 → number of CPUs (capped at the case count).")
	var watchMode bool
	flags.BoolVar(&watchMode, "watch", false, "Re-run the tests whenever the solution file changes. Ctrl+C to quit. Requires a terminal.")
	flags.BoolVar(&watchMode, "w", false, "Re-run the tests whenever the solution file changes. Ctrl+C to quit. Requires a terminal.")
	// 提出準備 (旧 submit コマンド)。サンプル全通過時にコピー + 提出ページ起動。
	var submit bool
	flags.BoolVar(&submit, "submit", false, "After all samples pass, copy the solution to the clipboard and open the submit page.")
	noOpen := flags.Bool("no-open", false, "With --submit, do not open the browser (just print the submit URL).")
	keepDebug := flags.Bool("keep-debug", false, "With --submit, copy the solution as-is without commenting out [DEBUG] print lines.")
	var asJSON bool
	flags.BoolVar(&asJSON, "json", false, "Print the sample-judging result as a single JSON object to stdout (sample mode only).")
	flags.SetOutput(os.Stderr)

	if err := flags.Parse(flagArgs); err != nil {
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

	// --pp は debug 表示の整形だけを司る (要件 047)。-d 無しでは debug: セクションが
	// 空なので --pp は無表示になる。「効かない」誤認を避けるため note を 1 行出す
	// (exit code は変えない。--pp が -d を含意する隠れ結合は入れない)。
	if pp && !debug {
		fmt.Fprintln(os.Stderr, "note: --pp has no effect without -d/--debug")
	}

	lay, err := resolveLayout(*layoutFlag, contest)
	if err != nil {
		return 2, err
	}

	// モード判定: --in/--out/--interactive を明示したら ad-hoc / 対話 (runexec)、
	// それ以外は既定のサンプル判定 (testexec)。判定は「明示指定されたフラグ」基準で
	// 行う (--side-by-side は config 既定で true になりうるため値では判定しない)。
	set := map[string]bool{}
	flags.Visit(func(f *flag.Flag) { set[f.Name] = true })
	setAny := func(names ...string) bool {
		for _, n := range names {
			if set[n] {
				return true
			}
		}
		return false
	}
	// --auto-restart は対話モード (chat TUI) 専用。--interactive 無しでの指定はフラグ誤り。
	if autoRestart && !interactive {
		return 2, errors.New("--auto-restart requires --interactive")
	}
	// --json はサンプル判定モード専用 (要件 042)。単発の機械出力なので、ad-hoc/対話・
	// ライブ再描画 (--watch)・副作用を伴う --submit とは併用できない。
	if asJSON && (interactive || inFile != "" || outFile != "" || watchMode || submit) {
		return 2, errors.New("--json is a sample-mode flag and cannot be combined with --in/--out/--interactive/--watch/--submit")
	}
	if interactive || inFile != "" || outFile != "" {
		if setAny("refresh", "case", "c", "jobs", "j", "watch", "w", "s", "side-by-side", "submit", "no-open", "keep-debug") {
			return 2, errors.New("--refresh/--case/--jobs/--watch/--side-by-side/--submit are sample-mode flags and cannot be combined with --in/--out/--interactive")
		}
		return runAdHoc(contest, task, lay, inFile, outFile, interactive, autoRestart, debug, verbose, pp, *timeoutFlag, *tolFlag, cfg.Editor, cfg.EditorNvimRemote)
	}

	// --submit は一回限りの提出準備なので、常駐する --watch とは併用不可。
	if submit && watchMode {
		return 2, errors.New("--submit cannot be combined with --watch")
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
			Reporter:    ui.NewTestReporter(verbose, sideBySide, pp),
		}
	}

	if watchMode {
		return runTestWatch(contest, task, lay, *refresh, buildOpts, false)
	}

	// --json: 判定を SummaryReporter で回し、結果を JSON で stdout に出す (要件 042)。
	if asJSON {
		return runTestJSON(contest, task, buildOpts(*refresh))
	}

	// --submit: サンプルを実行し提出前チェック (全通過・実行可否・DEBUG 検出) を経て、
	// クリーンなら提出準備、リスクがあれば確認を取る (要件 044)。
	if submit {
		return runSubmitPrep(contest, task, lay, buildOpts(*refresh), *noOpen, *keepDebug)
	}

	code, err := testexec.Run(buildOpts(*refresh))
	if err != nil {
		return code, err
	}
	return code, err
}

// runTestWatch は解答ファイルの保存を監視し、変更のたびにテストを再実行する。
// Ctrl+C で抜けて exit 0。判定結果 (FAIL/RE/TLE) ではループを止めない。
// untilPass が true なら、サンプルが全通過した回 (testexec.Run が 0) で抜けて exit 0
// にする (`atcoder start --until-pass` 用)。
func runTestWatch(contest, task string, lay layout.Layout, refresh bool, buildOpts func(refresh bool) testexec.Options, untilPass bool) (int, error) {
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
		code, err := testexec.Run(buildOpts(refresh && firstRun))
		if err != nil {
			fmt.Fprintln(os.Stderr, "atcoder test:", err)
		}
		firstRun = false

		// --until-pass: 全サンプル通過 (code==0) でループを抜けて終了する。
		if untilPass && err == nil && code == 0 {
			fmt.Println()
			return 0, nil
		}

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
