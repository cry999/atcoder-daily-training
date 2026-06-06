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

// DebugPrefix で始まる行は、--debug 指定時の比較対象から除外される。
const DebugPrefix = "[DEBUG]"

type CaseResult struct {
	Name            string
	Status          CaseStatus
	Elapsed         time.Duration
	Input           string // 常にセット (テストケースの標準入力)
	Expected        string // 常にセット (normalize 済みの期待出力)
	Actual          string // 常にセット (normalize 済みの実際の stdout, debug 時は [DEBUG] 行を除外したもの)
	Debug           string // --debug 時にのみセット。[DEBUG] で始まる行の集合
	Stderr          string // RE のみ
	OriginalLimitMs int    // problem の本来の制限時間 (ms)。Status==Pass で Elapsed が超えていたら本来 TLE。
}

func judge(name, input, expected string, pr *runner.ProcessResult, debug bool) CaseResult {
	stdout := pr.Stdout
	var debugOut string
	if debug {
		stdout, debugOut = splitDebug(stdout)
	}
	cr := CaseResult{
		Name:     name,
		Elapsed:  pr.Elapsed,
		Input:    strings.TrimRight(input, "\n"),
		Expected: normalizeOutput(expected),
		Actual:   normalizeOutput(stdout),
		Debug:    debugOut,
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

// splitDebug は stdout を「[DEBUG] で始まらない行」と「[DEBUG] で始まる行」に分割する。
func splitDebug(stdout string) (filtered, debug string) {
	var filteredLines, debugLines []string
	for _, line := range strings.Split(stdout, "\n") {
		if strings.HasPrefix(line, DebugPrefix) {
			debugLines = append(debugLines, line)
		} else {
			filteredLines = append(filteredLines, line)
		}
	}
	return strings.Join(filteredLines, "\n"), strings.Join(debugLines, "\n")
}

func normalizeOutput(s string) string {
	s = strings.ReplaceAll(s, "\r\n", "\n")
	return strings.TrimRight(s, "\n")
}
