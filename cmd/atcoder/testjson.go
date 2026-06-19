package main

import (
	"encoding/json"
	"os"

	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

// testJSON は `atcoder test --json` のトップレベル出力スキーマ (要件 042)。
// 外部ツール (nvim フロント等) が atcoder を判定エンジンとして消費するための
// 機械可読コントラクト。キーは欠落させず、空でも値を出す。
type testJSON struct {
	Contest     string         `json:"contest"`
	Task        string         `json:"task"`
	TimeLimitMs int            `json:"time_limit_ms"`
	TimeoutMs   int            `json:"timeout_ms"`
	Tolerance   float64        `json:"tolerance"`
	Passed      int            `json:"passed"`
	Total       int            `json:"total"`
	AllPassed   bool           `json:"all_passed"`
	Cases       []testCaseJSON `json:"cases"`
}

// testCaseJSON は cases[] の 1 要素 (testexec.CaseResult の機械可読版)。
type testCaseJSON struct {
	Name      string `json:"name"`
	Status    string `json:"status"`
	ElapsedMs int64  `json:"elapsed_ms"`
	Input     string `json:"input"`
	Expected  string `json:"expected"`
	Actual    string `json:"actual"`
	Stderr    string `json:"stderr"`
	Debug     string `json:"debug"`
}

// caseStatusString は testexec.CaseStatus を安定した文字列に写す純粋関数。
// internal/testexec の表示語彙に依存させず、JSON コントラクトを cmd 側で固定する。
func caseStatusString(s testexec.CaseStatus) string {
	switch s {
	case testexec.Pass:
		return "AC"
	case testexec.Fail:
		return "WA"
	case testexec.TLE:
		return "TLE"
	case testexec.RE:
		return "RE"
	default:
		return "UNKNOWN"
	}
}

// runTestJSON はサンプル判定を SummaryReporter (stdout 非汚染) で回し、結果を
// JSON オブジェクト 1 個として stdout に出力する。exit code は通常の test と同じ
// セマンティクス (全通過=0 / 不通過=1 / fetch・実行失敗=1)。
func runTestJSON(contest, task string, opts testexec.Options) (int, error) {
	rep := testexec.NewSummaryReporter()
	opts.Reporter = rep
	code, err := testexec.Run(opts)
	if err != nil {
		// fetch 失敗・ケース無し等。JSON は出さず従来どおりエラーを返す。
		return code, err
	}

	passed, total, cases := rep.Result()
	timeLimitMs, timeoutMs, _, tolerance := rep.Meta()
	out := buildTestJSON(contest, task, timeLimitMs, timeoutMs, tolerance, passed, total, cases)

	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(out); err != nil {
		return 1, err
	}
	return code, nil
}

// buildTestJSON は捕捉した判定結果を出力スキーマに組み立てる純粋関数。
func buildTestJSON(contest, task string, timeLimitMs, timeoutMs int, tolerance float64, passed, total int, cases []testexec.CaseResult) testJSON {
	out := testJSON{
		Contest:     contest,
		Task:        task,
		TimeLimitMs: timeLimitMs,
		TimeoutMs:   timeoutMs,
		Tolerance:   tolerance,
		Passed:      passed,
		Total:       total,
		AllPassed:   total > 0 && passed == total,
		Cases:       make([]testCaseJSON, 0, len(cases)),
	}
	for _, c := range cases {
		out.Cases = append(out.Cases, testCaseJSON{
			Name:      c.Name,
			Status:    caseStatusString(c.Status),
			ElapsedMs: c.Elapsed.Milliseconds(),
			Input:     c.Input,
			Expected:  c.Expected,
			Actual:    c.Actual,
			Stderr:    c.Stderr,
			Debug:     c.Debug,
		})
	}
	return out
}
