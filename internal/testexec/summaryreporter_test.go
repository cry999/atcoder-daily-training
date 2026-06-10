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
	r.CaseFinished(CaseResult{Name: "03", Status: RE})
	r.CaseFinished(CaseResult{Name: "02", Status: Fail})
	r.Summary(1, 3)

	passed, total, failing := r.Result()
	if passed != 1 || total != 3 {
		t.Errorf("passed/total = %d/%d, want 1/3", passed, total)
	}
	// 失敗ケースは昇順 (Pass は含まない)。
	if !reflect.DeepEqual(failing, []string{"02", "03"}) {
		t.Errorf("failing = %v, want [02 03]", failing)
	}
}
