package ui

import (
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/runexec"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

type TestReporter struct {
	verbose    bool
	sideBySide bool
	pp         bool // true なら debug: セクションの valid JSON ペイロードを整形して表示する (要件 047)

	// live は stdout が端末のときだけ true。true ならテスト実行中に bubbletea で
	// ライブ表示 (ケース一覧 + プログレスバー) を出す。パイプ/CI のときは false で、
	// End() で結果をまとめてプレーン出力する。
	live    bool
	program *tea.Program
	done    chan struct{}
}

func NewTestReporter(verbose, sideBySide, pp bool) *TestReporter {
	return &TestReporter{
		verbose:    verbose,
		sideBySide: sideBySide,
		pp:         pp,
		live:       isTerminal(os.Stdout),
	}
}

func (r *TestReporter) Fetching(contest, task string) {
	fmt.Println(infoStyle.Render(fmt.Sprintf("Fetching %s/%s from AtCoder...", contest, task)))
}

func (r *TestReporter) Header(task, contest string, timeLimitMs, timeoutMs, ntests int, tolerance float64) {
	parts := []string{
		headerTitleStyle.Render(task),
		keyStyle.Render("contest=") + valueStyle.Render(contest),
		keyStyle.Render("time_limit=") + valueStyle.Render(fmt.Sprintf("%dms", timeLimitMs)),
	}
	if timeoutMs != timeLimitMs {
		parts = append(parts, overrideStyle.Render(fmt.Sprintf("timeout=%dms", timeoutMs)))
	}
	parts = append(parts,
		keyStyle.Render("tolerance=")+valueStyle.Render(formatTolerance(tolerance)),
		keyStyle.Render("tests=")+valueStyle.Render(fmt.Sprintf("%d", ntests)),
	)
	fmt.Println(strings.Join(parts, "  "))
	fmt.Println()
}

// formatTolerance は 1e-6 を "1e-6" のように表示する (Go の %g だと "1e-06" になるため、
// 指数部の leading zero を剥がして読みやすくする)。
func formatTolerance(t float64) string {
	s := strconv.FormatFloat(t, 'g', -1, 64)
	s = strings.ReplaceAll(s, "e-0", "e-")
	s = strings.ReplaceAll(s, "e+0", "e+")
	return s
}

// Begin はライブ表示を開始する (live のときのみ)。bubbletea プログラムを別
// goroutine で走らせ、CaseStarted / CaseFinished で送られるイベントを描画する。
func (r *TestReporter) Begin(names []string, jobs int) {
	if !r.live {
		return
	}
	r.program = tea.NewProgram(newProgressModel(names, jobs))
	r.done = make(chan struct{})
	go func() {
		_, _ = r.program.Run()
		close(r.done)
	}()
}

// CaseStarted / CaseFinished はワーカー goroutine から並列に呼ばれる。
// program.Send はスレッドセーフ。
func (r *TestReporter) CaseStarted(name string) {
	if !r.live {
		return
	}
	r.program.Send(caseStartedMsg{name: name})
}

func (r *TestReporter) CaseFinished(cr testexec.CaseResult) {
	if !r.live {
		return
	}
	r.program.Send(caseFinishedMsg{cr: cr})
}

// End はライブ表示を終了させ、各ケースの詳細 (verbose の入出力 / debug / diff /
// stderr) をケース名順に出力する。
//   - live のとき: ライブのグリッドに既に各ケースの 1 行サマリが残っているので、
//     ここでは「追加情報を持つケース」だけ [NN] 行 + 詳細を出す。
//   - 非 live のとき: 各ケースの 1 行サマリと詳細を順に出す (従来の挙動)。
//
// results にはエラーで実行できなかったケースの zero 値 (Name=="") が混じりうる
// ため、Name 空はスキップする。
func (r *TestReporter) End(results []testexec.CaseResult) {
	if r.live {
		r.program.Quit()
		<-r.done
	}
	wroteSeparator := false
	for _, cr := range results {
		if cr.Name == "" {
			continue
		}
		if r.live {
			if !r.caseHasDetail(cr) {
				continue
			}
			if !wroteSeparator {
				fmt.Println()
				wroteSeparator = true
			}
		}
		fmt.Println(caseLineString(cr))
		r.printCaseDetail(cr)
	}
}

// caseHasDetail はライブ表示後に追加で詳細を出す価値があるか (FAIL の diff、
// RE の stderr、verbose の入出力、debug 行) を返す。
func (r *TestReporter) caseHasDetail(cr testexec.CaseResult) bool {
	return r.verbose || cr.Debug != "" || cr.Status == testexec.Fail || cr.Status == testexec.RE
}

func (r *TestReporter) printCaseDetail(cr testexec.CaseResult) {
	if r.verbose {
		printContent("input:", cr.Input)
		printContent("output:", cr.Actual)
	}
	if cr.Debug != "" {
		debug := cr.Debug
		if r.pp {
			debug = prettifyDebug(debug)
		}
		printContent("debug:", debug)
	}
	switch cr.Status {
	case testexec.Fail:
		// -v のときは diff にマッチ行も context として含める。
		// -s のときは side-by-side レンダラに切り替える。
		printDiff(cr.Expected, cr.Actual, r.verbose, r.sideBySide)
	case testexec.RE:
		printStderr(cr.Stderr)
	}
}

// caseLineString は "[NN] BADGE  elapsed (over ...)" の 1 行を返す (改行なし)。
// ライブグリッドの完了行と End() のプレーン出力で共用する。
func caseLineString(cr testexec.CaseResult) string {
	elapsedText := elapsedStyle.Render(fmt.Sprintf("%d ms", cr.Elapsed.Milliseconds()))
	if cr.Status == testexec.Pass && cr.OriginalLimitMs > 0 &&
		cr.Elapsed > time.Duration(cr.OriginalLimitMs)*time.Millisecond {
		elapsedText += "  " + overLimitStyle.Render(fmt.Sprintf("(over original %dms)", cr.OriginalLimitMs))
	}
	return fmt.Sprintf("%s %s  %s",
		caseLabelStyle.Render("["+cr.Name+"]"),
		statusBadge(cr.Status),
		elapsedText,
	)
}

func printContent(label, body string) {
	body = strings.TrimRight(body, "\n")
	if body == "" {
		return
	}
	fmt.Println("       " + sectionLabel.Render(label))
	for _, line := range strings.Split(body, "\n") {
		fmt.Println("         " + line)
	}
}

func (r *TestReporter) Summary(passed, total int) {
	fmt.Println()
	text := fmt.Sprintf("Result: %d/%d PASS", passed, total)
	if passed == total {
		fmt.Println(summaryPassStyle.Render(text))
	} else {
		fmt.Println(summaryFailStyle.Render(text))
	}
}

func statusBadge(s testexec.CaseStatus) string {
	switch s {
	case testexec.Pass:
		return passBadge.Render("PASS")
	case testexec.Fail:
		return failBadge.Render("FAIL")
	case testexec.TLE:
		return tleBadge.Render("TLE")
	case testexec.RE:
		return reBadge.Render("RE")
	}
	return ""
}

func printDiff(expected, got string, full, sideBySide bool) {
	label := "diff:"
	if sideBySide {
		label = "diff (side-by-side):"
	}
	fmt.Println("       " + sectionLabel.Render(label))
	if sideBySide {
		fmt.Print(renderDiffSideBySide(expected, got, full))
	} else {
		fmt.Print(renderDiff(expected, got, full))
	}
}

const (
	stderrFullDisplayLines = 50
	stderrHeadLines        = 10
	stderrTailLines        = 10
)

// ----- runexec.Reporter implementation -----

type RunReporter struct {
	verbose bool
	pp      bool // true なら debug: セクションの valid JSON ペイロードを整形して表示する (要件 047)
}

func NewRunReporter(verbose, pp bool) *RunReporter { return &RunReporter{verbose: verbose, pp: pp} }

func (r *RunReporter) Header(task, contest string, timeLimitMs, timeoutMs int, mode string) {
	parts := []string{
		headerTitleStyle.Render(task),
		keyStyle.Render("contest=") + valueStyle.Render(contest),
		keyStyle.Render("time_limit=") + valueStyle.Render(fmt.Sprintf("%dms", timeLimitMs)),
	}
	if timeoutMs != timeLimitMs {
		parts = append(parts, overrideStyle.Render(fmt.Sprintf("timeout=%dms", timeoutMs)))
	}
	if mode != "" {
		parts = append(parts, infoStyle.Render(mode))
	}
	fmt.Println(strings.Join(parts, "  "))
	fmt.Println()
}

func (r *RunReporter) Result(res runexec.Result) {
	fmt.Printf("%s  %s\n",
		runResultBadge(res),
		elapsedStyle.Render(fmt.Sprintf("%d ms", res.Elapsed.Milliseconds())),
	)
	if r.verbose {
		printContent("input:", res.Input)
	}
	printContent("output:", res.Stdout)
	if res.Debug != "" {
		debug := res.Debug
		if r.pp {
			debug = prettifyDebug(debug)
		}
		printContent("debug:", debug)
	}
	// judge モード (--out 指定時) で不一致のとき、diff を出す。
	if res.Compared && !res.OutputMatch && res.Status == runexec.Ok {
		printDiff(res.Expected, res.Stdout, r.verbose, false)
	}
	if res.Status == runexec.Crashed {
		printStderr(res.Stderr)
	}
}

// runResultBadge は run の結果バッジを返す。judge モード (Compared) で正常
// 終了かつ不一致なら FAIL、一致なら PASS。それ以外は実行ステータス由来。
func runResultBadge(res runexec.Result) string {
	if res.Compared && res.Status == runexec.Ok {
		if res.OutputMatch {
			return passBadge.Render("PASS")
		}
		return failBadge.Render("FAIL")
	}
	return runStatusBadge(res.Status)
}

func runStatusBadge(s runexec.Status) string {
	switch s {
	case runexec.Ok:
		return passBadge.Render("OK")
	case runexec.Timeout:
		return tleBadge.Render("TLE")
	case runexec.Crashed:
		return reBadge.Render("RE")
	}
	return ""
}

// ----- shared helpers -----

func printStderr(stderrOut string) {
	stderrOut = strings.TrimRight(stderrOut, "\n")
	if stderrOut == "" {
		return
	}
	lines := strings.Split(stderrOut, "\n")
	fmt.Println("       " + sectionLabel.Render("stderr:"))
	if len(lines) <= stderrFullDisplayLines {
		for _, line := range lines {
			fmt.Println("         " + line)
		}
		return
	}
	for _, line := range lines[:stderrHeadLines] {
		fmt.Println("         " + line)
	}
	elided := len(lines) - stderrHeadLines - stderrTailLines
	fmt.Println("         " + sectionLabel.Render(fmt.Sprintf("... (%d more lines elided)", elided)))
	for _, line := range lines[len(lines)-stderrTailLines:] {
		fmt.Println("         " + line)
	}
}
