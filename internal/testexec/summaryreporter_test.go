package testexec

import (
	"reflect"
	"testing"
)

func TestSummaryReporterCaptures(t *testing.T) {
	r := NewSummaryReporter()
	// 表示系 no-op は呼んでも安全。
	r.Header("abc999_a", "abc999", 2000, 2000, 3, 1e-6)
	r.Begin([]string{"01", "02", "03"}, 1)
	r.CaseFinished(CaseResult{Name: "01", Status: Pass})
	// End はケース名順の全結果を渡す (per-case verdict はここで捕捉する)。
	r.End([]CaseResult{
		{Name: "01", Status: Pass},
		{Name: "02", Status: Fail},
		{Name: "03", Status: RE},
	})
	r.Summary(1, 3)

	passed, total, cases := r.Result()
	if passed != 1 || total != 3 {
		t.Errorf("passed/total = %d/%d, want 1/3", passed, total)
	}
	// per-case は名前順・status 付きで返る。
	want := []CaseResult{
		{Name: "01", Status: Pass},
		{Name: "02", Status: Fail},
		{Name: "03", Status: RE},
	}
	if !reflect.DeepEqual(cases, want) {
		t.Errorf("cases = %v, want %v", cases, want)
	}
}
