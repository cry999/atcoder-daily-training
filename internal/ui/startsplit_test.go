package ui

import (
	"errors"
	"strings"
	"testing"
	"time"
)

func TestFormatSampleSummaryAllPassed(t *testing.T) {
	s := SampleSummary{Passed: 3, Total: 3, AllPassed: true, At: time.Date(2026, 6, 11, 12, 34, 56, 0, time.UTC)}
	got := formatSampleSummary(s) // 非 TTY テストでは lipgloss が色を剥がす
	if !strings.Contains(got, "✓ PASS  3/3") {
		t.Errorf("got %q, want it to contain '✓ PASS  3/3'", got)
	}
	if !strings.Contains(got, "12:34:56") {
		t.Errorf("got %q, want it to contain the judged time", got)
	}
	if strings.Contains(got, "fail:") {
		t.Errorf("all-passed summary should not list failing cases: %q", got)
	}
}

func TestFormatSampleSummaryFailing(t *testing.T) {
	s := SampleSummary{Passed: 1, Total: 3, AllPassed: false, Failing: []string{"02", "03"}}
	got := formatSampleSummary(s)
	if !strings.Contains(got, "✗ FAIL  1/3") {
		t.Errorf("got %q, want '✗ FAIL  1/3'", got)
	}
	if !strings.Contains(got, "fail: 02 03") {
		t.Errorf("got %q, want 'fail: 02 03'", got)
	}
}

func TestFormatSampleSummaryError(t *testing.T) {
	got := formatSampleSummary(SampleSummary{Err: errors.New("テストケースが見つかりません")})
	if !strings.Contains(got, "判定不可") {
		t.Errorf("got %q, want it to report '判定不可'", got)
	}
}

func TestStartSplitChatHeight(t *testing.T) {
	cases := []struct {
		height int
		want   int
	}{
		{24, 24 - splitTopLines - splitHelpLines}, // 通常
		{splitTopLines + splitHelpLines, 1},       // 余地ゼロ → 1 にクランプ
		{2, 1},                                    // 端末が極端に低い → 1
	}
	for _, c := range cases {
		m := &startSplitModel{height: c.height}
		if got := m.chatHeight(); got != c.want {
			t.Errorf("chatHeight(height=%d) = %d, want %d", c.height, got, c.want)
		}
	}
}
