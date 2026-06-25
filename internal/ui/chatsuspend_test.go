package ui

import (
	"strings"
	"testing"

	tea "github.com/charmbracelet/bubbletea"
)

// isSuspend は cmd を実行して tea.SuspendMsg を返すか確かめる。tea.Suspend は
// func() Msg { return SuspendMsg{} } なので、Cmd として実行すると SuspendMsg が出る。
func isSuspend(t *testing.T, cmd tea.Cmd) bool {
	t.Helper()
	if cmd == nil {
		return false
	}
	_, ok := cmd().(tea.SuspendMsg)
	return ok
}

// 要件 058: chat の insert モードで Ctrl+Z はサスペンド (tea.Suspend) を返す。
func TestChatCtrlZ_Suspends(t *testing.T) {
	m := initialChatModel(ChatHeader{}, nil)
	_, cmd := m.Update(tea.KeyMsg{Type: tea.KeyCtrlZ})
	if !isSuspend(t, cmd) {
		t.Fatal("Ctrl+Z should return tea.Suspend in insert mode")
	}
}

// 要件 058: command (`:`) モードでも Ctrl+Z はサスペンドする (モード分岐より前で捕捉)。
func TestChatCtrlZ_SuspendsInCommandMode(t *testing.T) {
	m := initialChatModel(ChatHeader{}, nil)
	m.mode = modeCommand
	_, cmd := m.Update(tea.KeyMsg{Type: tea.KeyCtrlZ})
	if !isSuspend(t, cmd) {
		t.Fatal("Ctrl+Z should return tea.Suspend in command mode")
	}
}

// 要件 058: Ctrl+Z はヘルプ (placeholder) に出る。
func TestChatCtrlZ_PlaceholderMentionsIt(t *testing.T) {
	m := initialChatModel(ChatHeader{}, nil)
	if !strings.Contains(m.input.Placeholder, "Ctrl+Z") {
		t.Fatalf("placeholder should mention Ctrl+Z: %q", m.input.Placeholder)
	}
}

// 要件 058: 分割画面 (start) も通常表示・詳細表示中の両方で Ctrl+Z はサスペンドする。
func TestStartSplitCtrlZ_Suspends(t *testing.T) {
	m := detailModel(nil)
	_, cmd := m.Update(tea.KeyMsg{Type: tea.KeyCtrlZ})
	if !isSuspend(t, cmd) {
		t.Fatal("Ctrl+Z should return tea.Suspend in split view")
	}

	m2 := detailModel(nil)
	m2.detail = true // 詳細表示中でも有効
	_, cmd2 := m2.Update(tea.KeyMsg{Type: tea.KeyCtrlZ})
	if !isSuspend(t, cmd2) {
		t.Fatal("Ctrl+Z should return tea.Suspend even while the detail overlay is open")
	}
}
