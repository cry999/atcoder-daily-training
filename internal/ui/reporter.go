package ui

import (
	"fmt"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/runexec"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

type TestReporter struct {
	verbose bool
}

func NewTestReporter(verbose bool) *TestReporter { return &TestReporter{verbose: verbose} }

func (r *TestReporter) Fetching(contest, task string) {
	fmt.Println(infoStyle.Render(fmt.Sprintf("Fetching %s/%s from AtCoder...", contest, task)))
}

func (r *TestReporter) Header(task, contest string, timeLimitMs, timeoutMs, ntests int) {
	parts := []string{
		headerTitleStyle.Render(task),
		keyStyle.Render("contest=") + valueStyle.Render(contest),
		keyStyle.Render("time_limit=") + valueStyle.Render(fmt.Sprintf("%dms", timeLimitMs)),
	}
	if timeoutMs != timeLimitMs {
		parts = append(parts, overrideStyle.Render(fmt.Sprintf("timeout=%dms", timeoutMs)))
	}
	parts = append(parts, keyStyle.Render("tests=")+valueStyle.Render(fmt.Sprintf("%d", ntests)))
	fmt.Println(strings.Join(parts, "  "))
	fmt.Println()
}

func (r *TestReporter) Case(cr testexec.CaseResult) {
	elapsedText := elapsedStyle.Render(fmt.Sprintf("%d ms", cr.Elapsed.Milliseconds()))
	if cr.Status == testexec.Pass && cr.OriginalLimitMs > 0 &&
		cr.Elapsed > time.Duration(cr.OriginalLimitMs)*time.Millisecond {
		elapsedText += "  " + overLimitStyle.Render(fmt.Sprintf("(over original %dms)", cr.OriginalLimitMs))
	}
	fmt.Printf("%s %s  %s\n",
		caseLabelStyle.Render("["+cr.Name+"]"),
		statusBadge(cr.Status),
		elapsedText,
	)
	if r.verbose {
		printContent("input:", cr.Input)
		printContent("output:", cr.Actual)
	}
	if cr.Debug != "" {
		printContent("debug:", cr.Debug)
	}
	switch cr.Status {
	case testexec.Fail:
		printDiff(cr.Expected, cr.Actual)
	case testexec.RE:
		printStderr(cr.Stderr)
	}
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

func printDiff(expected, got string) {
	fmt.Println("       " + sectionLabel.Render("diff:"))
	fmt.Print(renderDiff(expected, got))
}

const (
	stderrFullDisplayLines = 50
	stderrHeadLines        = 10
	stderrTailLines        = 10
)

// ----- runexec.Reporter implementation -----

type RunReporter struct {
	verbose bool
}

func NewRunReporter(verbose bool) *RunReporter { return &RunReporter{verbose: verbose} }

func (r *RunReporter) Header(task, contest string, timeLimitMs, timeoutMs int, interactive bool) {
	parts := []string{
		headerTitleStyle.Render(task),
		keyStyle.Render("contest=") + valueStyle.Render(contest),
		keyStyle.Render("time_limit=") + valueStyle.Render(fmt.Sprintf("%dms", timeLimitMs)),
	}
	if timeoutMs != timeLimitMs {
		parts = append(parts, overrideStyle.Render(fmt.Sprintf("timeout=%dms", timeoutMs)))
	}
	mode := "(ad-hoc stdin)"
	if interactive {
		mode = "(interactive)"
	}
	parts = append(parts, infoStyle.Render(mode))
	fmt.Println(strings.Join(parts, "  "))
	fmt.Println()
}

func (r *RunReporter) Result(res runexec.Result) {
	fmt.Printf("%s  %s\n",
		runStatusBadge(res.Status),
		elapsedStyle.Render(fmt.Sprintf("%d ms", res.Elapsed.Milliseconds())),
	)
	if r.verbose {
		printContent("input:", res.Input)
	}
	printContent("output:", res.Stdout)
	if res.Debug != "" {
		printContent("debug:", res.Debug)
	}
	if res.Status == runexec.Crashed {
		printStderr(res.Stderr)
	}
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
