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
	"github.com/cry999/atcoder-daily-training/internal/cliargs"
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
	flagArgs, positionals := cliargs.Split(args)
	if len(positionals) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := positionals[0]

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

	sc := &startConfig{
		layoutFlag: *layoutFlag,
		debug:      debug,
		timeout:    *timeoutFlag,
		tolerance:  *tolFlag,
		jobs:       jobs,
		sideBySide: sideBySide,
	}

	// 初期ターゲットを構築 (resolveLayout / 着手 はここで)。
	t0, created, code, err := sc.buildTarget(contest, task, *refresh)
	if err != nil {
		return code, err
	}
	if created {
		fmt.Printf("created: %s\n", t0.SolutionPath)
	} else {
		fmt.Printf("solution: %s (exists)\n", t0.SolutionPath)
	}

	if !ui.IsStdoutTerminal() {
		return 2, errors.New("start requires a terminal (stdout is not a TTY)")
	}

	// ナビゲーション解決を注入する: 移動先 ID を算出 (純粋) → buildTarget で再ターゲット
	// 用ターゲットを組む。境界・非対応・不正 spec は error として返り、TUI 内 1 行で示す。
	navigate := func(curID, curTask string, req ui.NavRequest) (ui.StartTarget, error) {
		newID, newTask, err := nextTarget(curID, curTask, req)
		if err != nil {
			return ui.StartTarget{}, err
		}
		t, created, _, err := sc.buildTarget(newID, newTask, false)
		if err != nil {
			return ui.StartTarget{}, err
		}
		t.InfoLines = navInfoLines(t.Task, t.SolutionPath, created)
		return t, nil
	}

	return ui.RunStartSplit(ui.StartSplitConfig{
		Initial:   t0,
		Navigate:  navigate,
		UntilPass: *untilPass,
		Poll:      watchPollInterval,
	})
}

// startConfig は start 起動フラグのうち、ターゲット構築 (初回 + ナビ) で共通に使う値。
type startConfig struct {
	layoutFlag string
	debug      bool
	timeout    time.Duration
	tolerance  float64
	jobs       int
	sideBySide bool
}

// buildTarget は (contestID, task) に対する分割画面ターゲットを構築する。レイアウト解決
// (auto は contestID で再判定) → 着手 (無ければ空ファイル) → runner spawn・サンプル判定
// closure・watcher・ChatHeader を組む。初回起動とナビゲーション解決の両方から呼ぶ薄い
// orchestration で、新しい実行・判定ロジックは持たない。code は err 時の exit code。
func (c *startConfig) buildTarget(contestID, task string, refresh bool) (t ui.StartTarget, created bool, code int, err error) {
	lay, err := resolveLayout(c.layoutFlag, contestID)
	if err != nil {
		return ui.StartTarget{}, false, 2, err
	}
	// 解答ファイルを用意 (無ければ空ファイル)。既存は温存する。
	path, created, err := ensureSolutionFile(lay, contestID, task)
	if err != nil {
		return ui.StartTarget{}, false, 1, err
	}

	// 下ペイン: chat の子プロセス起動 (auto-restart)。
	ex, err := selectRunExecutor(path)
	if err != nil {
		return ui.StartTarget{}, false, 1, err
	}
	var extraEnv []string
	if c.debug {
		extraEnv = []string{"DEBUG=1"}
	}
	spawn := func() (*runner.ChatHandle, error) {
		return ex.StartChat(path, extraEnv)
	}

	buildOpts := func(refresh bool) testexec.Options {
		return testexec.Options{
			Contest:     contestID,
			Task:        task,
			Layout:      lay,
			Refresh:     refresh,
			Timeout:     c.timeout,
			Debug:       c.debug,
			Tolerance:   c.tolerance,
			Concurrency: c.jobs,
			ExecutorFor: selectExecutor,
			Reporter:    ui.NewTestReporter(false, c.sideBySide),
		}
	}

	// 上ペイン: 保存検知でサンプルを再判定する。判定は stdout に書かず捕捉 Reporter で
	// 結果だけ集めて要約にする。初回のみ refresh を効かせる (ナビ時は refresh=false)。
	firstRefresh := refresh
	runSamples := func() ui.SampleSummary {
		rep := testexec.NewSummaryReporter()
		opts := buildOpts(firstRefresh)
		firstRefresh = false
		opts.Reporter = rep
		runCode, runErr := testexec.Run(opts)
		passed, total, cases := rep.Result()
		verdicts := make([]ui.CaseVerdict, 0, len(cases))
		for _, cs := range cases {
			verdicts = append(verdicts, ui.CaseVerdict{Name: cs.Name, Label: caseLabel(cs.Status), OK: cs.Status == testexec.Pass})
		}
		s := ui.SampleSummary{Passed: passed, Total: total, Cases: verdicts, At: time.Now()}
		if runErr != nil {
			s.Err = runErr
		} else {
			s.AllPassed = runCode == 0 && total > 0
		}
		return s
	}

	timeLimitMs := 2000
	if c.timeout > 0 {
		timeLimitMs = int(c.timeout / time.Millisecond)
	}
	// WatchPath を渡すと、保存検知で下ペインの chat も最新コードで reload する。
	header := ui.ChatHeader{
		Task:        task,
		Contest:     contestID,
		TimeLimitMs: timeLimitMs,
		Debug:       c.debug,
		AutoRestart: true,
		WatchPath:   path,
		Submit:      chatSubmitFunc(contestID, task, lay),
		TaskDir:     cachepath.Task(contestID, task),
		Tolerance:   c.tolerance,
		NavEnabled:  true,
	}
	return ui.StartTarget{
		ContestID:    contestID,
		Task:         task,
		SolutionPath: path,
		Spawn:        ui.Spawner(spawn),
		Header:       header,
		RunSamples:   runSamples,
		Watcher:      watch.New(path, watchPollInterval, watchDebounce),
	}, created, 0, nil
}

// nextTarget は現 (contestID, task) とナビ要求から移動先の (contestID, task) を算出する
// 純粋関数 (要件 027)。境界・非対応・不正 spec は日本語の UI 文言エラーを返す
// (TUI 内 1 行表示に使う)。layout の sentinel error を文言に写像する。
func nextTarget(contestID, task string, req ui.NavRequest) (newID, newTask string, err error) {
	switch req.Kind {
	case ui.NavLetterNext, ui.NavLetterPrev:
		letter, lerr := layout.Letter(task)
		if lerr != nil {
			return "", "", errors.New("この問題は記号移動に対応していません")
		}
		delta := 1
		if req.Kind == ui.NavLetterPrev {
			delta = -1
		}
		nl, serr := layout.ShiftLetter(letter, delta)
		if serr != nil {
			if errors.Is(serr, layout.ErrLetterShape) {
				return "", "", errors.New("この問題は記号移動に対応していません")
			}
			if delta < 0 {
				return "", "", errors.New("これより前の問題はありません")
			}
			return "", "", errors.New("これより先の問題はありません")
		}
		return contestID, contestID + "_" + nl, nil

	case ui.NavContestNext, ui.NavContestPrev:
		letter, lerr := layout.Letter(task)
		if lerr != nil {
			return "", "", errors.New("この問題は番号移動に対応していません")
		}
		delta := 1
		if req.Kind == ui.NavContestPrev {
			delta = -1
		}
		nid, serr := layout.ShiftContest(contestID, delta)
		if serr != nil {
			if errors.Is(serr, layout.ErrContestShape) {
				return "", "", errors.New("このコンテストは番号移動に対応していません")
			}
			if delta < 0 {
				return "", "", errors.New("これより前のコンテストはありません")
			}
			return "", "", errors.New("これより先のコンテストはありません")
		}
		return nid, nid + "_" + letter, nil

	case ui.NavExplicit:
		return parseExplicitSpec(req.Spec, contestID)

	default:
		return "", "", errors.New("不明なナビゲーション要求です")
	}
}

// parseExplicitSpec は :e <spec> を移動先 (contestID, task) に解決する純粋関数。
//   - ""                    → error (E492。問題指定なし)
//   - "<contest>_<letter>"  → (<contest>, <contest>_<letter>)   例 "abc500_d"
//   - "<letter>" (英字のみ) → (現 contestID, 現contestID_<letter>) 例 "f"
//   - 数字を含み _ 無し      → error (contest 単体は不可。:e <contest>_<letter> を促す)
func parseExplicitSpec(spec, contestID string) (newID, newTask string, err error) {
	spec = strings.TrimSpace(spec)
	if spec == "" {
		return "", "", errors.New("E492: :e は問題を指定してください (例 :e f / :e abc500_d)")
	}
	if i := strings.LastIndex(spec, "_"); i >= 0 {
		cid := spec[:i]
		letter := spec[i+1:]
		if cid == "" || letter == "" {
			return "", "", errors.New("E492: 不正な問題指定です :e " + spec)
		}
		return cid, layout.TaskID(cid, letter), nil
	}
	if strings.ContainsAny(spec, "0123456789") {
		return "", "", errors.New("E492: コンテスト単体ではなく :e <contest>_<letter> の形式で指定してください (例 :e abc500_d)")
	}
	letter := strings.ToLower(spec)
	return contestID, layout.TaskID(contestID, letter), nil
}

// navInfoLines は再ターゲット時に chat へ出す案内行を組む (移動先 + 着手状況)。
func navInfoLines(task, path string, created bool) []string {
	lines := []string{fmt.Sprintf("(→ %s に移動しました)", task)}
	if created {
		lines = append(lines, "created: "+path)
	} else {
		lines = append(lines, "solution: "+path+" (exists)")
	}
	return lines
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
