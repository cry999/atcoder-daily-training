package ui

import (
	"testing"

	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
)

// overflow する履歴を積んだ command モードの model を作る (height を小さくして
// maxViewportHeight を絞り、scrollback がスクロール可能な状態にする)。
func scrollableCommandModel() *chatModel {
	m := &chatModel{width: 40, height: 8, ready: true, mode: modeCommand}
	m.viewport = viewport.New(40, 3)
	for i := 0; i < 30; i++ {
		m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "line"})
	}
	m.refreshViewport()
	return m
}

// 要件 032: command モードの PageUp で上にスクロールし、以降の出力到着でも
// 最下部に引き戻さない (上スクロール位置を維持)。
func TestCmdScroll_PageUpHoldsPosition(t *testing.T) {
	m := scrollableCommandModel()
	if !m.viewport.AtBottom() {
		t.Fatal("freshly refreshed viewport should follow (be at the bottom)")
	}

	m.updateCommand(tea.KeyMsg{Type: tea.KeyPgUp})
	if !m.cmdScrolled {
		t.Fatal("PageUp should set cmdScrolled")
	}
	if m.viewport.AtBottom() {
		t.Fatal("PageUp should scroll up (no longer at bottom)")
	}
	off := m.viewport.YOffset

	// 子の出力が届いて refresh されても最下部に引き戻さない。
	m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "new output"})
	m.refreshViewport()
	if m.viewport.AtBottom() {
		t.Fatal("output arrival must NOT yank back to bottom while scrolled up")
	}
	if m.viewport.YOffset != off {
		t.Fatalf("YOffset should be preserved (%d), got %d", off, m.viewport.YOffset)
	}
}

// PageDown で最下部に戻ると追従 (cmdScrolled=false) を再開する。
func TestCmdScroll_PageDownResumesFollow(t *testing.T) {
	m := scrollableCommandModel()
	m.updateCommand(tea.KeyMsg{Type: tea.KeyPgUp})
	if !m.cmdScrolled {
		t.Fatal("armed after PageUp")
	}
	for i := 0; i < 10 && !m.viewport.AtBottom(); i++ {
		m.updateCommand(tea.KeyMsg{Type: tea.KeyPgDown})
	}
	if !m.viewport.AtBottom() {
		t.Fatal("PageDown should reach the bottom")
	}
	if m.cmdScrolled {
		t.Fatal("reaching the bottom with PageDown should clear cmdScrolled (resume follow)")
	}
}

// Esc は上スクロールを解除し、最下部 (最新) に戻して insert モードへ。
func TestCmdScroll_EscReturnsToBottom(t *testing.T) {
	m := scrollableCommandModel()
	m.updateCommand(tea.KeyMsg{Type: tea.KeyPgUp})
	if !m.cmdScrolled || m.viewport.AtBottom() {
		t.Fatal("should be scrolled up after PageUp")
	}

	m.updateCommand(tea.KeyMsg{Type: tea.KeyEsc})
	if m.cmdScrolled {
		t.Fatal("Esc should clear cmdScrolled")
	}
	if !m.viewport.AtBottom() {
		t.Fatal("Esc should return the viewport to the bottom (latest)")
	}
	if m.mode != modeInsert {
		t.Fatal("Esc from command mode should return to insert mode")
	}
}

// コマンド実行 (Enter) は上スクロールを解除する (実行後は最下部の live view)。
func TestCmdScroll_ExecResets(t *testing.T) {
	m := scrollableCommandModel()
	m.updateCommand(tea.KeyMsg{Type: tea.KeyPgUp})
	if !m.cmdScrolled {
		t.Fatal("armed after PageUp")
	}
	m.cmdInput.SetValue("") // 空コマンド → command モードを抜ける
	m.updateCommand(tea.KeyMsg{Type: tea.KeyEnter})
	if m.cmdScrolled {
		t.Fatal("executing a command should clear cmdScrolled")
	}
	if !m.viewport.AtBottom() {
		t.Fatal("after a command the viewport should be back at the bottom")
	}
}

// insert モードでは cmdScrolled が立たず、常に最下部追従 (非破壊)。
func TestCmdScroll_InsertModeAlwaysFollows(t *testing.T) {
	m := scrollableCommandModel()
	m.mode = modeInsert
	m.cmdScrolled = false
	m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "more"})
	m.refreshViewport()
	if !m.viewport.AtBottom() {
		t.Fatal("insert mode (no scroll keys) should always follow the bottom")
	}
}
