package testexec

import (
	"fmt"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

type CaseStatus int

const (
	Pass CaseStatus = iota
	Fail
	TLE
	RE
)

type CaseResult struct {
	Name     string
	Status   CaseStatus
	Elapsed  time.Duration
	Expected string
	Actual   string
	Stderr   string
}

func judge(name, expected string, pr *runner.ProcessResult) CaseResult {
	cr := CaseResult{Name: name, Elapsed: pr.Elapsed}
	switch pr.Status {
	case runner.TimedOut:
		cr.Status = TLE
	case runner.Exited:
		if pr.ExitCode != 0 {
			cr.Status = RE
			cr.Stderr = pr.Stderr
			break
		}
		exp := normalizeOutput(expected)
		got := normalizeOutput(pr.Stdout)
		if exp == got {
			cr.Status = Pass
			break
		}
		cr.Status = Fail
		cr.Expected = exp
		cr.Actual = got
	}
	return cr
}

func normalizeOutput(s string) string {
	s = strings.ReplaceAll(s, "\r\n", "\n")
	return strings.TrimRight(s, "\n")
}

func report(cr CaseResult) {
	ms := cr.Elapsed.Milliseconds()
	switch cr.Status {
	case Pass:
		fmt.Printf("[%s] PASS  %d ms\n", cr.Name, ms)
	case Fail:
		fmt.Printf("[%s] FAIL  %d ms\n", cr.Name, ms)
		printDiff(cr.Expected, cr.Actual)
	case TLE:
		fmt.Printf("[%s] TLE   %d ms\n", cr.Name, ms)
	case RE:
		fmt.Printf("[%s] RE    %d ms\n", cr.Name, ms)
		printStderr(cr.Stderr)
	}
}

func printStderr(stderrOut string) {
	stderrOut = strings.TrimRight(stderrOut, "\n")
	if stderrOut == "" {
		return
	}
	if len(stderrOut) > 1000 {
		stderrOut = stderrOut[:1000] + "... (truncated)"
	}
	fmt.Printf("       stderr:\n")
	for _, line := range strings.Split(stderrOut, "\n") {
		fmt.Printf("         %s\n", line)
	}
}

func printDiff(expected, got string) {
	fmt.Printf("       expected:\n")
	for _, l := range strings.Split(expected, "\n") {
		fmt.Printf("         %s\n", l)
	}
	fmt.Printf("       got:\n")
	for _, l := range strings.Split(got, "\n") {
		fmt.Printf("         %s\n", l)
	}
	fmt.Printf("       diff:\n")
	expLines := strings.Split(expected, "\n")
	gotLines := strings.Split(got, "\n")
	maxL := len(expLines)
	if len(gotLines) > maxL {
		maxL = len(gotLines)
	}
	for i := 0; i < maxL; i++ {
		var e, g string
		hasE := i < len(expLines)
		hasG := i < len(gotLines)
		if hasE {
			e = expLines[i]
		}
		if hasG {
			g = gotLines[i]
		}
		if hasE && hasG && e == g {
			continue
		}
		if hasE {
			fmt.Printf("         - %s\n", e)
		}
		if hasG {
			fmt.Printf("         + %s\n", g)
		}
	}
}
