package testexec

import (
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
	Name            string
	Status          CaseStatus
	Elapsed         time.Duration
	Expected        string
	Actual          string
	Stderr          string
	OriginalLimitMs int // problem の本来の制限時間 (ms)。Status==Pass で Elapsed が超えていたら本来 TLE。
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
