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
	if !m.scrolled {
		t.Fatal("PageUp should set scrolled")
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

// PageDown で最下部に戻ると追従 (scrolled=false) を再開する。
func TestCmdScroll_PageDownResumesFollow(t *testing.T) {
	m := scrollableCommandModel()
	m.updateCommand(tea.KeyMsg{Type: tea.KeyPgUp})
	if !m.scrolled {
		t.Fatal("armed after PageUp")
	}
	for i := 0; i < 10 && !m.viewport.AtBottom(); i++ {
		m.updateCommand(tea.KeyMsg{Type: tea.KeyPgDown})
	}
	if !m.viewport.AtBottom() {
		t.Fatal("PageDown should reach the bottom")
	}
	if m.scrolled {
		t.Fatal("reaching the bottom with PageDown should clear scrolled (resume follow)")
	}
}

// Esc は上スクロールを解除し、最下部 (最新) に戻して insert モードへ。
func TestCmdScroll_EscReturnsToBottom(t *testing.T) {
	m := scrollableCommandModel()
	m.updateCommand(tea.KeyMsg{Type: tea.KeyPgUp})
	if !m.scrolled || m.viewport.AtBottom() {
		t.Fatal("should be scrolled up after PageUp")
	}

	m.updateCommand(tea.KeyMsg{Type: tea.KeyEsc})
	if m.scrolled {
		t.Fatal("Esc should clear scrolled")
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
	if !m.scrolled {
		t.Fatal("armed after PageUp")
	}
	m.cmdInput.SetValue("") // 空コマンド → command モードを抜ける
	m.updateCommand(tea.KeyMsg{Type: tea.KeyEnter})
	if m.scrolled {
		t.Fatal("executing a command should clear scrolled")
	}
	if !m.viewport.AtBottom() {
		t.Fatal("after a command the viewport should be back at the bottom")
	}
}

// 要件 067: command モードの Ctrl+P (1 行) / Ctrl+U (半ページ) で上にスクロールし、
// 出力到着でも最下部に引き戻さない。Ctrl+N / Ctrl+D で最下部に戻ると追従を再開する。
func TestCmdScroll_LineAndHalfPage(t *testing.T) {
	cases := []struct {
		name     string
		up, down tea.KeyType
	}{
		{"line", tea.KeyCtrlP, tea.KeyCtrlN},
		{"half", tea.KeyCtrlU, tea.KeyCtrlD},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			m := scrollableCommandModel()
			if !m.viewport.AtBottom() {
				t.Fatal("freshly refreshed viewport should follow (be at the bottom)")
			}

			m.updateCommand(tea.KeyMsg{Type: tc.up})
			if !m.scrolled {
				t.Fatalf("%v should set scrolled", tc.up)
			}
			if m.viewport.AtBottom() {
				t.Fatalf("%v should scroll up (no longer at bottom)", tc.up)
			}
			off := m.viewport.YOffset

			// 出力が届いて refresh されても最下部に引き戻さない。
			m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "new output"})
			m.refreshViewport()
			if m.viewport.AtBottom() || m.viewport.YOffset != off {
				t.Fatalf("output must not yank back to bottom while scrolled (off=%d got=%d)", off, m.viewport.YOffset)
			}

			// Ctrl+N / Ctrl+D で最下部に戻ると追従再開。
			for i := 0; i < 40 && !m.viewport.AtBottom(); i++ {
				m.updateCommand(tea.KeyMsg{Type: tc.down})
			}
			if !m.viewport.AtBottom() {
				t.Fatalf("%v should reach the bottom", tc.down)
			}
			if m.scrolled {
				t.Fatalf("reaching the bottom with %v should clear scrolled (resume follow)", tc.down)
			}
		})
	}
}

// overflow する履歴を積んだ insert モードの model (要件 040 のスクロール検証用)。
func scrollableInsertModel() *chatModel {
	m := initialChatModel(ChatHeader{}, nil)
	m.width, m.height, m.ready = 40, 8, true
	m.viewport = viewport.New(40, 3)
	for i := 0; i < 30; i++ {
		m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "line"})
	}
	m.refreshViewport()
	return m
}

// 要件 040: insert モードの PageUp (と Ctrl+B) で上にスクロールし、出力到着でも
// 最下部に引き戻さない。PageDown/Ctrl+F で最下部に戻ると追従を再開する。
func TestInsertScroll_PageUpHoldsThenResumes(t *testing.T) {
	for _, up := range []tea.KeyType{tea.KeyPgUp, tea.KeyCtrlB} {
		m := scrollableInsertModel()
		if !m.viewport.AtBottom() {
			t.Fatal("freshly refreshed insert viewport should follow the bottom")
		}
		m.Update(tea.KeyMsg{Type: up})
		if !m.scrolled {
			t.Fatalf("%v should set scrolled in insert mode", up)
		}
		if m.viewport.AtBottom() {
			t.Fatalf("%v should scroll up (no longer at bottom)", up)
		}
		off := m.viewport.YOffset

		// 出力が届いて refresh されても最下部に引き戻さない。
		m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "new output"})
		m.refreshViewport()
		if m.viewport.AtBottom() || m.viewport.YOffset != off {
			t.Fatalf("output must not yank back to bottom while scrolled (off=%d got=%d)", off, m.viewport.YOffset)
		}

		// PageDown/Ctrl+F で最下部に戻ると追従再開。
		down := tea.KeyPgDown
		if up == tea.KeyCtrlB {
			down = tea.KeyCtrlF
		}
		for i := 0; i < 20 && !m.viewport.AtBottom(); i++ {
			m.Update(tea.KeyMsg{Type: down})
		}
		if !m.viewport.AtBottom() {
			t.Fatalf("%v should reach the bottom", down)
		}
		if m.scrolled {
			t.Fatalf("reaching bottom with %v should clear scrolled (resume follow)", down)
		}
	}
}

// 送信 (Enter) は上スクロールを解除し最下部 (live view) に戻す。
func TestInsertScroll_EnterReturnsToBottom(t *testing.T) {
	// 起動済み (running) モデルにして submitLines が restart せず実送信する経路にする。
	m, _ := runningModel()
	m.viewport = viewport.New(40, 3)
	for i := 0; i < 30; i++ {
		m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "line"})
	}
	m.refreshViewport()

	m.Update(tea.KeyMsg{Type: tea.KeyPgUp})
	if !m.scrolled || m.viewport.AtBottom() {
		t.Fatal("should be scrolled up after PageUp")
	}
	var cmds []tea.Cmd
	m.submitLines([]string{"x"}, &cmds, false)
	if m.scrolled {
		t.Fatal("submitting should clear scrolled (return to live view)")
	}
}

// 入力履歴 (↑/↓) は従来どおりで、スクロールには使わない (非破壊)。
func TestInsertScroll_ArrowsStillNavigateHistory(t *testing.T) {
	m := scrollableInsertModel()
	m.history = []string{"first", "second"}
	m.historyPos = len(m.history)
	m.Update(tea.KeyMsg{Type: tea.KeyUp})
	if m.scrolled {
		t.Fatal("Up must not trigger scroll (it navigates history)")
	}
	if got := m.input.Value(); got != "second" {
		t.Fatalf("Up should recall last history entry, got %q", got)
	}
}
