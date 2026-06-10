package ui

import (
	"errors"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/x/ansi"
)

func TestFormatSampleSummaryAllPassed(t *testing.T) {
	s := SampleSummary{
		Passed: 2, Total: 2, AllPassed: true,
		Cases: []CaseVerdict{{Name: "01", Label: "AC", OK: true}, {Name: "02", Label: "AC", OK: true}},
		At:    time.Date(2026, 6, 11, 12, 34, 56, 0, time.UTC),
	}
	got := formatSampleSummary(s) // 非 TTY テストでは lipgloss が色を剥がす
	if !strings.Contains(got, "✓ 2/2") {
		t.Errorf("got %q, want it to contain '✓ 2/2'", got)
	}
	if !strings.Contains(got, "01 AC") || !strings.Contains(got, "02 AC") {
		t.Errorf("got %q, want per-case '01 AC' '02 AC'", got)
	}
	if !strings.Contains(got, "12:34:56") {
		t.Errorf("got %q, want it to contain the judged time", got)
	}
}

func TestFormatSampleSummaryPerCase(t *testing.T) {
	s := SampleSummary{
		Passed: 2, Total: 4, AllPassed: false,
		Cases: []CaseVerdict{
			{Name: "01", Label: "AC", OK: true},
			{Name: "02", Label: "WA", OK: false},
			{Name: "03", Label: "TLE", OK: false},
			{Name: "04", Label: "AC", OK: true},
		},
	}
	got := formatSampleSummary(s)
	if !strings.Contains(got, "✗ 2/4") {
		t.Errorf("got %q, want '✗ 2/4'", got)
	}
	for _, want := range []string{"01 AC", "02 WA", "03 TLE", "04 AC"} {
		if !strings.Contains(got, want) {
			t.Errorf("got %q, want per-case %q", got, want)
		}
	}
}

func TestFormatSampleSummaryError(t *testing.T) {
	got := formatSampleSummary(SampleSummary{Err: errors.New("テストケースが見つかりません")})
	if !strings.Contains(got, "判定不可") {
		t.Errorf("got %q, want it to report '判定不可'", got)
	}
}

// 多数のケースでペイン幅を超えても、renderSummaryLine は 1 行に収める (… で切り詰め)。
func TestRenderSummaryLineTruncates(t *testing.T) {
	cases := make([]CaseVerdict, 20)
	for i := range cases {
		cases[i] = CaseVerdict{Name: fmt.Sprintf("%02d", i+1), Label: "AC", OK: true}
	}
	m := &startSplitModel{width: 30, haveSummary: true, summary: SampleSummary{Passed: 20, Total: 20, AllPassed: true, Cases: cases}}
	line := m.renderSummaryLine()
	if w := lipgloss.Width(line); w > 30 {
		t.Errorf("summary line width %d > pane width 30 (should be truncated): %q", w, ansi.Strip(line))
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
