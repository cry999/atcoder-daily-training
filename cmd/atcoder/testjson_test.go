package main

import (
	"testing"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

func TestCaseStatusString(t *testing.T) {
	cases := []struct {
		in   testexec.CaseStatus
		want string
	}{
		{testexec.Pass, "AC"},
		{testexec.Fail, "WA"},
		{testexec.TLE, "TLE"},
		{testexec.RE, "RE"},
		{testexec.CaseStatus(999), "UNKNOWN"},
	}
	for _, c := range cases {
		if got := caseStatusString(c.in); got != c.want {
			t.Errorf("caseStatusString(%v) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestBuildTestJSON(t *testing.T) {
	cases := []testexec.CaseResult{
		{Name: "01", Status: testexec.Pass, Elapsed: 12 * time.Millisecond, Input: "5", Expected: "10", Actual: "10"},
		{Name: "02", Status: testexec.Fail, Elapsed: 14 * time.Millisecond, Input: "3", Expected: "6", Actual: "7"},
		{Name: "x01", Status: testexec.RE, Elapsed: 8 * time.Millisecond, Input: "1", Expected: "2", Actual: "", Stderr: "boom"},
	}
	out := buildTestJSON("abc457", "abc457_d", 2000, 5000, 1e-6, 1, 3, cases)

	if out.Contest != "abc457" || out.Task != "abc457_d" {
		t.Errorf("contest/task = %q/%q", out.Contest, out.Task)
	}
	if out.TimeLimitMs != 2000 || out.TimeoutMs != 5000 || out.Tolerance != 1e-6 {
		t.Errorf("meta = %d/%d/%g", out.TimeLimitMs, out.TimeoutMs, out.Tolerance)
	}
	if out.Passed != 1 || out.Total != 3 {
		t.Errorf("passed/total = %d/%d", out.Passed, out.Total)
	}
	if out.AllPassed {
		t.Errorf("all_passed should be false when passed != total")
	}
	if len(out.Cases) != 3 {
		t.Fatalf("len(cases) = %d, want 3", len(out.Cases))
	}
	if out.Cases[0].Status != "AC" || out.Cases[0].ElapsedMs != 12 {
		t.Errorf("case0 = %+v", out.Cases[0])
	}
	if out.Cases[2].Status != "RE" || out.Cases[2].Stderr != "boom" {
		t.Errorf("case2 = %+v", out.Cases[2])
	}
}

func TestBuildTestJSON_AllPassed(t *testing.T) {
	cases := []testexec.CaseResult{
		{Name: "01", Status: testexec.Pass},
		{Name: "02", Status: testexec.Pass},
	}
	out := buildTestJSON("fixture", "fixture_pass", 2000, 2000, 1e-6, 2, 2, cases)
	if !out.AllPassed {
		t.Errorf("all_passed should be true when passed == total > 0")
	}

	// total == 0 のときは all_passed=false (0 件成功を「全通過」と誤認しない)。
	empty := buildTestJSON("fixture", "fixture_pass", 2000, 2000, 1e-6, 0, 0, nil)
	if empty.AllPassed {
		t.Errorf("all_passed should be false when total == 0")
	}
}
