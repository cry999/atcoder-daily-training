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

// 再ターゲット後 (epoch 進行) は、旧ターゲットの遅延サンプル結果 (古い epoch) を破棄し、
// 現世代の結果だけを反映する (要件 027 の target epoch)。
func TestStartSplitStaleSampleDiscarded(t *testing.T) {
	m := &startSplitModel{epoch: 1, sampleInFlight: true}

	// 旧世代 (epoch 0) の結果は破棄される。
	m.Update(splitSampleMsg{summary: SampleSummary{Passed: 9, Total: 9, AllPassed: true}, epoch: 0})
	if m.haveSummary {
		t.Errorf("stale sample (epoch 0) should be discarded, but summary was applied: %+v", m.summary)
	}
	if !m.sampleInFlight {
		t.Errorf("stale sample should not clear sampleInFlight")
	}

	// 現世代 (epoch 1) の結果は反映される。
	m.Update(splitSampleMsg{summary: SampleSummary{Passed: 2, Total: 2, AllPassed: true}, epoch: 1})
	if !m.haveSummary || m.summary.Passed != 2 || m.summary.Total != 2 {
		t.Errorf("fresh sample should be applied, got haveSummary=%v summary=%+v", m.haveSummary, m.summary)
	}
	if m.sampleInFlight {
		t.Errorf("fresh sample should clear sampleInFlight")
	}
}

// DebugMsg は live Debug を更新し、新 Debug で watch を即再判定する (要件 033)。
// epoch を進めて in-flight の旧判定を破棄し、runSamples には新しい Debug 値が渡る。
func TestStartSplitDebugMsgRejudges(t *testing.T) {
	var gotDebug []bool
	m := &startSplitModel{
		debug: false,
		epoch: 0,
		runSamples: func(debug bool) SampleSummary {
			gotDebug = append(gotDebug, debug)
			return SampleSummary{Passed: 1, Total: 1, AllPassed: true}
		},
	}

	// :debug on 相当。live Debug が true になり、再判定 Cmd が返る。
	_, cmd := m.Update(DebugMsg{On: true})
	if !m.debug {
		t.Errorf("DebugMsg{On:true} should set m.debug=true")
	}
	if m.epoch != 1 {
		t.Errorf("debug change should bump epoch to discard stale in-flight judge, got epoch=%d", m.epoch)
	}
	if !m.sampleInFlight {
		t.Errorf("debug change should mark a re-judge in flight")
	}
	if cmd == nil {
		t.Fatal("DebugMsg should trigger a re-judge Cmd")
	}
	// Cmd を駆動すると runSamples が新 Debug=true で呼ばれ、現世代 epoch を載せた結果が返る。
	msg, ok := cmd().(splitSampleMsg)
	if !ok {
		t.Fatalf("re-judge Cmd should produce splitSampleMsg, got %#v", cmd())
	}
	if msg.epoch != 1 {
		t.Errorf("re-judge result should carry the new epoch 1, got %d", msg.epoch)
	}
	if len(gotDebug) != 1 || gotDebug[0] != true {
		t.Errorf("runSamples should be called once with debug=true, got %v", gotDebug)
	}

	// 同値の DebugMsg は再判定しない (epoch も据え置き)。
	_, cmd = m.Update(DebugMsg{On: true})
	if cmd != nil || m.epoch != 1 {
		t.Errorf("DebugMsg with unchanged value should be a no-op, got cmd=%v epoch=%d", cmd, m.epoch)
	}
}

// watch ペインのタイトルは live Debug on のときだけ [debug] バッジを出す (要件 033)。
func TestRenderWatchPaneDebugBadge(t *testing.T) {
	m := &startSplitModel{width: 60, solutionPath: "exercise/2026/06/11/abc999_a.py", haveSummary: true,
		summary: SampleSummary{Passed: 1, Total: 1, AllPassed: true}}

	if got := m.renderWatchPane(); strings.Contains(got, "[debug]") {
		t.Errorf("debug off: watch pane should not show [debug] badge; got %q", got)
	}
	m.debug = true
	if got := m.renderWatchPane(); !strings.Contains(got, "[debug]") {
		t.Errorf("debug on: watch pane should show [debug] badge; got %q", got)
	}
}
