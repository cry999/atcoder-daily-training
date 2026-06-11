package ui

import (
	"testing"

	tea "github.com/charmbracelet/bubbletea"
)

// 直前と同じ内容の入力は履歴に積まない (連続重複の抑制)。
func TestHistorySkipsConsecutiveDuplicate(t *testing.T) {
	m, _ := runningModel()
	var cmds []tea.Cmd
	m.submitLines([]string{"a"}, &cmds)
	m.submitLines([]string{"a"}, &cmds) // 直前と同じ → 積まれない
	m.submitLines([]string{"b"}, &cmds)
	m.submitLines([]string{"a"}, &cmds) // 非連続の重複は許容

	got := m.history
	want := []string{"a", "b", "a"}
	if len(got) != len(want) {
		t.Fatalf("history = %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("history = %v, want %v", got, want)
		}
	}
}

// 複数行ペースト内での連続同一行も連続重複として抑制する。
func TestHistorySkipsConsecutiveDuplicateWithinPaste(t *testing.T) {
	m, _ := runningModel()
	var cmds []tea.Cmd
	m.submitLines([]string{"x", "x", "y"}, &cmds)

	got := m.history
	want := []string{"x", "y"}
	if len(got) != len(want) {
		t.Fatalf("history = %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("history = %v, want %v", got, want)
		}
	}
}
