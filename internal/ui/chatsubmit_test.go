package ui

import (
	"strings"
	"testing"

	tea "github.com/charmbracelet/bubbletea"
)

func ctrlS(m *chatModel) (*chatModel, tea.Cmd) {
	model, cmd := m.Update(tea.KeyMsg{Type: tea.KeyCtrlS})
	return model.(*chatModel), cmd
}

// Ctrl+S は注入された Submit フックを呼び、結果を info 行に積む。
func TestChatCtrlS_Success(t *testing.T) {
	called := 0
	m := initialChatModel(ChatHeader{Submit: func() SubmitResult {
		called++
		return SubmitResult{Message: "クリップボードにコピー abc457/d.py / 提出ページを開きました"}
	}}, nil)
	before := len(m.msgs)

	m, cmd := ctrlS(m)

	if called != 1 {
		t.Fatalf("Submit called %d times, want 1", called)
	}
	if cmd != nil {
		t.Fatalf("Ctrl+S returned a non-nil cmd; chat should stay (no quit)")
	}
	if len(m.msgs) != before+1 {
		t.Fatalf("added %d lines, want 1", len(m.msgs)-before)
	}
	last := m.msgs[len(m.msgs)-1]
	if last.kind != kindInfo {
		t.Fatalf("kind=%q, want %q", last.kind, kindInfo)
	}
	if !strings.Contains(last.text, "提出準備:") || !strings.Contains(last.text, "abc457/d.py") {
		t.Fatalf("text=%q", last.text)
	}
}

// IsError な結果は err 行で表示する。
func TestChatCtrlS_Error(t *testing.T) {
	m := initialChatModel(ChatHeader{Submit: func() SubmitResult {
		return SubmitResult{Message: "失敗: 解答ファイルの読み込みに失敗しました", IsError: true}
	}}, nil)

	m, _ = ctrlS(m)

	last := m.msgs[len(m.msgs)-1]
	if last.kind != kindErr {
		t.Fatalf("kind=%q, want %q", last.kind, kindErr)
	}
}

// Submit 未注入 (nil) のとき Ctrl+S は「利用できません」を出すだけ (パニックしない)。
func TestChatCtrlS_Unavailable(t *testing.T) {
	m := initialChatModel(ChatHeader{}, nil) // Submit == nil

	m, cmd := ctrlS(m)

	if cmd != nil {
		t.Fatalf("Ctrl+S returned a non-nil cmd")
	}
	last := m.msgs[len(m.msgs)-1]
	if !strings.Contains(last.text, "利用できません") {
		t.Fatalf("text=%q, want 利用できません", last.text)
	}
}

// Submit が注入されているとヘルプ文言に Ctrl+S が出る。未注入なら出ない。
func TestChatSubmitHint(t *testing.T) {
	with := initialChatModel(ChatHeader{Submit: func() SubmitResult { return SubmitResult{} }}, nil)
	if !strings.Contains(with.input.Placeholder, "Ctrl+S") {
		t.Fatalf("placeholder should mention Ctrl+S: %q", with.input.Placeholder)
	}
	without := initialChatModel(ChatHeader{}, nil)
	if strings.Contains(without.input.Placeholder, "Ctrl+S") {
		t.Fatalf("placeholder should not mention Ctrl+S when Submit is nil: %q", without.input.Placeholder)
	}
}
