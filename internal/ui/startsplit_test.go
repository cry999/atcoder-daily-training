package ui

import (
	"errors"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/x/ansi"

	"github.com/cry999/atcoder-daily-training/internal/solvestat"
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

// DebugMsg は live Debug を更新し、新 Debug で watch を即再判定する (要件 034)。
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

// :meta fetch (要件 057) の成功は watch ペインを即再判定する。fetch でキャッシュの
// サンプル / Time Limit が更新されるので、保存検知を待たずに新しい結果へ追従させる。
// chat にも委譲され、結果行とヘッダ Time Limit が反映される。epoch を進めて in-flight の
// 旧判定を破棄する (DebugMsg と同型)。
func TestStartSplitMetaFetchDoneRejudges(t *testing.T) {
	var calls int
	m := &startSplitModel{
		chat:  &chatModel{header: ChatHeader{TimeLimitMs: 2000}},
		epoch: 0,
		runSamples: func(debug bool) SampleSummary {
			calls++
			return SampleSummary{Passed: 1, Total: 1, AllPassed: true}
		},
	}

	_, cmd := m.Update(metaFetchDoneMsg{
		lines:          []string{"fetched abc111_d", "time limit:  5000 ms", "samples:     2"},
		newTimeLimitMs: 5000,
	})
	if m.epoch != 1 {
		t.Errorf("成功した :meta fetch は epoch を進めて旧判定を破棄すべき, got epoch=%d", m.epoch)
	}
	if !m.sampleInFlight {
		t.Errorf("成功した :meta fetch は再判定を in-flight にすべき")
	}
	if cmd == nil {
		t.Fatal("成功した :meta fetch は watch 再判定の Cmd を返すべき (nil だった)")
	}
	// chat へも委譲され、ヘッダ Time Limit が新値へ追従する。
	if m.chat.header.TimeLimitMs != 5000 {
		t.Errorf("chat ヘッダ TimeLimitMs=%d, want 5000 (:meta fetch を chat に委譲)", m.chat.header.TimeLimitMs)
	}
	// Cmd を駆動すると runSamples が呼ばれ、現世代 epoch を載せた結果が返る。
	if msg, ok := cmd().(splitSampleMsg); !ok || msg.epoch != 1 {
		t.Fatalf("再判定 Cmd は epoch 1 の splitSampleMsg を返すべき, got %#v", cmd())
	}
	if calls != 1 {
		t.Errorf("runSamples は 1 回呼ばれるべき, got %d", calls)
	}

	// 失敗した :meta fetch は再判定しない (epoch 据え置き・Cmd なし)。chat には err 行が積まれる。
	prevEpoch := m.epoch
	_, cmd = m.Update(metaFetchDoneMsg{err: errors.New("再取得に失敗しました: network")})
	if m.epoch != prevEpoch {
		t.Errorf("失敗した :meta fetch は epoch を進めないべき, got epoch=%d want %d", m.epoch, prevEpoch)
	}
	if cmd != nil {
		t.Errorf("失敗した :meta fetch は再判定 Cmd を返さないべき, got %v", cmd)
	}
	if last := m.chat.msgs[len(m.chat.msgs)-1]; last.kind != kindErr || !strings.Contains(last.text, "失敗") {
		t.Errorf("失敗した :meta fetch は chat に err 行を積むべき, got {%q %q}", last.kind, last.text)
	}
}

// watch ペインのタイトルは live Debug on のときだけ [debug] バッジを出す (要件 034)。
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

// navTarget は指定 solve-stat を返す RecordEditLoad を積んだナビ先ターゲットを組む test helper。
func navTarget(contest, task string, st solvestat.Stat, found bool) StartTarget {
	return StartTarget{
		ContestID: contest,
		Task:      task,
		Header: ChatHeader{
			Contest: contest, Task: task, TimeLimitMs: 2000, NavEnabled: true,
			RecordEditLoad: func() (solvestat.Stat, int64, bool, error) { return st, 0, found, nil },
		},
	}
}

// ナビ移動 (retarget) 後、移動先タスクが計測中 (started_at あり・solved_at 空) なら
// ● REC を復元し (started_at 基準)、tick を再開する。計測中でない移動先では REC を消す。
// バグ: retarget が chat を作り直す際に recording 状態を落とし、REC が消えていた。
func TestRetargetRestoresRecordingFromStat(t *testing.T) {
	started := time.Now().Add(-3 * time.Minute)
	// 起点: contest A で計測中 (REC 点灯相当)。
	m := &startSplitModel{
		chat:      initialChatModel(ChatHeader{Contest: "abc100", Task: "a", TimeLimitMs: 2000}, nil),
		contestID: "abc100", task: "a",
		navigate: func(curID, curTask string, req NavRequest) (StartTarget, error) {
			// 移動先 B は計測中の記録を持つ (started_at あり・solved_at 空)。
			return navTarget("abc101", "a", solvestat.Stat{StartedAt: started}, true), nil
		},
	}
	m.chat.recording = true
	m.chat.recordStart = started

	// :contest next 相当 → 計測中タスクへ移動。REC は点灯を保ち、tick Cmd が返る。
	_, cmd := m.Update(NavMsg{Req: NavRequest{Kind: NavContestNext}})
	if !m.chat.recording {
		t.Fatal("計測中タスクへ移動したら REC は点灯を保つべき")
	}
	if !m.chat.recordStart.Equal(started) {
		t.Errorf("recordStart は移動先の started_at 基準にすべき: got %v want %v", m.chat.recordStart, started)
	}
	if h := m.chat.renderHeader(); !strings.Contains(h, "● REC") {
		t.Fatalf("移動後ヘッダに ● REC が無い: %q", h)
	}
	if cmd == nil {
		t.Fatal("計測中タスクへの retarget は tick Cmd を返すべき")
	}

	// 次に未計測タスクへ移動 → ● REC は消灯し、未計測マーク ○ REC が出る。
	m.navigate = func(curID, curTask string, req NavRequest) (StartTarget, error) {
		return navTarget("abc102", "a", solvestat.Empty(), false), nil
	}
	m.Update(NavMsg{Req: NavRequest{Kind: NavContestNext}})
	if m.chat.recording {
		t.Fatal("未計測タスクへ移動したら計測は消灯すべき")
	}
	if h := m.chat.renderHeader(); strings.Contains(h, "● REC") {
		t.Fatalf("未計測タスクへ移動後もヘッダに ● REC が残る: %q", h)
	}
	if h := m.chat.renderHeader(); !strings.Contains(h, "○ REC") {
		t.Fatalf("未計測タスクへ移動後は未計測マーク ○ REC を出すべき: %q", h)
	}
}

// 計測中タスク間を連続で retarget しても record tick の世代 (recordGen) は単調増加し、
// 旧 chat の迷子 recordTickMsg (キャンセル不可の tea.Tick 遅延到達) が新 chat の tick と
// 世代衝突して二重 tick を張らない。retarget が旧 gen を引き継ぐことを固定する。
func TestRetargetRecordGenMonotonic(t *testing.T) {
	started := time.Now().Add(-time.Minute)
	rec := func() (solvestat.Stat, int64, bool, error) { return solvestat.Stat{StartedAt: started}, 0, true, nil }
	m := &startSplitModel{
		chat:      initialChatModel(ChatHeader{Contest: "abc100", Task: "a", TimeLimitMs: 2000, RecordEditLoad: rec}, nil),
		contestID: "abc100", task: "a",
	}
	// 起点も計測中 (:record start 相当で gen を 1 に進めておく)。
	m.chat.recording = true
	m.chat.recordStart = started
	m.chat.recordGen = 1

	prevGen := m.chat.recordGen
	for i := 0; i < 3; i++ {
		m.navigate = func(curID, curTask string, req NavRequest) (StartTarget, error) {
			return navTarget("abc101", "a", solvestat.Stat{StartedAt: started}, true), nil
		}
		m.Update(NavMsg{Req: NavRequest{Kind: NavContestNext}})
		if !m.chat.recording {
			t.Fatalf("retarget %d: 計測中タスクなら REC 点灯を保つべき", i)
		}
		if m.chat.recordGen <= prevGen {
			t.Fatalf("retarget %d: recordGen は単調増加すべき (旧 gen 引き継ぎ), got %d prev %d", i, m.chat.recordGen, prevGen)
		}
		prevGen = m.chat.recordGen
	}
}
