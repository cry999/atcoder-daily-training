package ui

import (
	"strings"
	"testing"
	"time"

	tea "github.com/charmbracelet/bubbletea"
)

func detailModel(cases []CaseVerdict) *startSplitModel {
	return &startSplitModel{
		chat:        initialChatModel(ChatHeader{}, nil),
		task:        "abc457_d",
		width:       60,
		height:      20,
		ready:       true,
		haveSummary: true,
		summary:     SampleSummary{Passed: 1, Total: 2, Cases: cases},
	}
}

// 要件 034: Ctrl+G で詳細を開き、失敗ケースの diff (期待/実際) が出る。AC は省く。
func TestStartDetail_CtrlGOpensFailingDiff(t *testing.T) {
	cases := []CaseVerdict{
		{Name: "01", Label: "AC", OK: true, Expected: "RIGHTOUT", Actual: "RIGHTOUT"},
		{Name: "02", Label: "WA", OK: false, Input: "5", Expected: "RIGHTOUT", Actual: "WRONGOUT", Elapsed: 31 * time.Millisecond},
	}
	m := detailModel(cases)

	m.Update(tea.KeyMsg{Type: tea.KeyCtrlG})
	if !m.detail {
		t.Fatal("Ctrl+G should open the detail overlay")
	}
	content := m.buildDetailContent()
	if !strings.Contains(content, "[02]") || !strings.Contains(content, "WA") {
		t.Fatalf("detail should include the failing case header: %q", content)
	}
	if !strings.Contains(content, "WRONGOUT") {
		t.Fatalf("detail should show the actual (wrong) output via the diff: %q", content)
	}
	if strings.Contains(content, "[01]") {
		t.Fatalf("AC case should be omitted from the detail: %q", content)
	}
}

// Esc で閉じる。Ctrl+G は開閉トグル。
func TestStartDetail_EscAndToggleClose(t *testing.T) {
	m := detailModel([]CaseVerdict{{Name: "02", Label: "WA", OK: false, Expected: "a", Actual: "b"}})

	m.Update(tea.KeyMsg{Type: tea.KeyCtrlG})
	if !m.detail {
		t.Fatal("opened by Ctrl+G")
	}
	m.Update(tea.KeyMsg{Type: tea.KeyEsc})
	if m.detail {
		t.Fatal("Esc should close the detail overlay")
	}
	m.Update(tea.KeyMsg{Type: tea.KeyCtrlG}) // open
	m.Update(tea.KeyMsg{Type: tea.KeyCtrlG}) // toggle close
	if m.detail {
		t.Fatal("Ctrl+G should toggle the detail overlay closed")
	}
}

// 失敗ケースが無ければその旨を出す。
func TestStartDetail_NoFailsMessage(t *testing.T) {
	m := detailModel([]CaseVerdict{{Name: "01", Label: "AC", OK: true}})
	if c := m.buildDetailContent(); !strings.Contains(c, "失敗ケースはありません") {
		t.Fatalf("all-AC should show the no-fails message: %q", c)
	}
}

// RE は stderr を出す。
func TestStartDetail_REShowsStderr(t *testing.T) {
	m := detailModel([]CaseVerdict{{Name: "03", Label: "RE", OK: false, Stderr: "IndexError: boom"}})
	if c := m.buildDetailContent(); !strings.Contains(c, "IndexError: boom") {
		t.Fatalf("RE detail should show stderr: %q", c)
	}
}

// 詳細表示中は普通のキーが chat に渡らない (chat の入力欄が変わらない)。
func TestStartDetail_KeysNotForwardedWhileOpen(t *testing.T) {
	m := detailModel([]CaseVerdict{{Name: "02", Label: "WA", OK: false, Expected: "a", Actual: "b"}})
	m.Update(tea.KeyMsg{Type: tea.KeyCtrlG}) // open
	before := m.chat.input.Value()
	m.Update(tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune("x")})
	if m.chat.input.Value() != before {
		t.Fatalf("keys must not reach chat while detail is open; chat input became %q", m.chat.input.Value())
	}
}
