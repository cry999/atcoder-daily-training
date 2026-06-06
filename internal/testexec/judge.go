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
	Input           string // 常にセット (テストケースの標準入力)
	Expected        string // 常にセット (normalize 済みの期待出力)
	Actual          string // 常にセット (normalize 済みの実際の stdout)
	Stderr          string // RE のみ
	OriginalLimitMs int    // problem の本来の制限時間 (ms)。Status==Pass で Elapsed が超えていたら本来 TLE。
}

func judge(name, input, expected string, pr *runner.ProcessResult) CaseResult {
	cr := CaseResult{
		Name:     name,
		Elapsed:  pr.Elapsed,
		Input:    strings.TrimRight(input, "\n"),
		Expected: normalizeOutput(expected),
		Actual:   normalizeOutput(pr.Stdout),
	}
	switch pr.Status {
	case runner.TimedOut:
		cr.Status = TLE
	case runner.Exited:
		if pr.ExitCode != 0 {
			cr.Status = RE
			cr.Stderr = pr.Stderr
			break
		}
		if cr.Expected == cr.Actual {
			cr.Status = Pass
			break
		}
		cr.Status = Fail
	}
	return cr
}

func normalizeOutput(s string) string {
	s = strings.ReplaceAll(s, "\r\n", "\n")
	return strings.TrimRight(s, "\n")
}
