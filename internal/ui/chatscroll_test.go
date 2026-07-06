package ui

import (
	"testing"

	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
)

// スクロールモードの素キー (j/k/d/u/f/b/g/G/:) は recordedit_test.go の runeKey を流用する。

// overflow する履歴を積んだ insert モードの model (スクロール検証用)。height を小さくして
// maxViewportHeight を絞り、scrollback がスクロール可能な状態にする。
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

// overflow する履歴を積んだスクロールモードの model (要件 071)。
func scrollableScrollModel() *chatModel {
	m := scrollableInsertModel()
	m.enterScrollMode()
	return m
}

// overflow する履歴を積んだ command モードの model (:scroll 突入検証用)。
func scrollableCommandModel() *chatModel {
	m := &chatModel{width: 40, height: 8, ready: true, mode: modeCommand}
	m.cmdInput = newCommandInput()
	m.viewport = viewport.New(40, 3)
	for i := 0; i < 30; i++ {
		m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "line"})
	}
	m.refreshViewport()
	return m
}

// 要件 071: insert モードの PageUp はスクロール専用モードへ入り、1 ページ上へスクロール
// する。以降の出力到着でも最下部に引き戻さない。
func TestInsertScroll_PageUpEntersScrollMode(t *testing.T) {
	m := scrollableInsertModel()
	if !m.viewport.AtBottom() {
		t.Fatal("freshly refreshed insert viewport should follow the bottom")
	}
	m.Update(tea.KeyMsg{Type: tea.KeyPgUp})
	if m.mode != modeScroll {
		t.Fatalf("PageUp from insert should enter scroll mode, got mode=%d", m.mode)
	}
	if !m.scrolled {
		t.Fatal("PageUp should set scrolled")
	}
	if m.viewport.AtBottom() {
		t.Fatal("PageUp should scroll up (no longer at bottom)")
	}
	off := m.viewport.YOffset

	// 出力が届いて refresh されても最下部に引き戻さない。
	m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "new output"})
	m.refreshViewport()
	if m.viewport.AtBottom() || m.viewport.YOffset != off {
		t.Fatalf("output must not yank back to bottom while scrolled (off=%d got=%d)", off, m.viewport.YOffset)
	}
}

// PageDown from insert も同様にスクロールモードへ入る (最下部なら位置は動かない)。
func TestInsertScroll_PageDownEntersScrollMode(t *testing.T) {
	m := scrollableInsertModel()
	m.Update(tea.KeyMsg{Type: tea.KeyPgDown})
	if m.mode != modeScroll {
		t.Fatalf("PageDown from insert should enter scroll mode, got mode=%d", m.mode)
	}
}

// Ctrl+B / Ctrl+F は insert から撤去した (スクロールしない・textinput の既定へ戻す)。
func TestInsertScroll_CtrlBFNoLongerScroll(t *testing.T) {
	for _, k := range []tea.KeyType{tea.KeyCtrlB, tea.KeyCtrlF} {
		m := scrollableInsertModel()
		m.Update(tea.KeyMsg{Type: k})
		if m.mode != modeInsert {
			t.Fatalf("%v must not change mode (stays insert), got %d", k, m.mode)
		}
		if m.scrolled {
			t.Fatalf("%v must not scroll (scrolled stays false)", k)
		}
	}
}

// 要件 071: スクロールモードの上方向キー (k=行 / u=半ページ / b=ページ / g=先頭) は
// 上へスクロールし scrolled を立てる。出力到着でも最下部に引き戻さない。
func TestScrollMode_UpKeysHoldPosition(t *testing.T) {
	for _, r := range []rune{'k', 'u', 'b', 'g'} {
		m := scrollableScrollModel()
		if !m.viewport.AtBottom() {
			t.Fatalf("[%c] fresh scroll model should be at bottom", r)
		}
		m.Update(runeKey(r))
		if !m.scrolled {
			t.Fatalf("[%c] up key should set scrolled", r)
		}
		if m.viewport.AtBottom() {
			t.Fatalf("[%c] up key should scroll up (no longer at bottom)", r)
		}
		off := m.viewport.YOffset
		m.msgs = append(m.msgs, chatLine{kind: kindOut, text: "new output"})
		m.refreshViewport()
		if m.viewport.AtBottom() || m.viewport.YOffset != off {
			t.Fatalf("[%c] output must not yank back to bottom (off=%d got=%d)", r, off, m.viewport.YOffset)
		}
	}
}

// 要件 071: スクロールモードの下方向キー (j=行 / d=半ページ / f=ページ) で最下部に戻ると
// 追従 (scrolled=false) を再開する。矢印 (↓) と Space (ページ下) も同じ。
func TestScrollMode_DownKeysResumeFollow(t *testing.T) {
	downs := []tea.KeyMsg{runeKey('j'), runeKey('d'), runeKey('f'), {Type: tea.KeyDown}, {Type: tea.KeySpace}}
	for _, down := range downs {
		m := scrollableScrollModel()
		m.scrollTop() // まず先頭まで上げてから下方向で戻す
		if !m.scrolled {
			t.Fatalf("[%s] should be scrolled after GotoTop", down.String())
		}
		for i := 0; i < 40 && !m.viewport.AtBottom(); i++ {
			m.Update(down)
		}
		if !m.viewport.AtBottom() {
			t.Fatalf("[%s] should reach the bottom", down.String())
		}
		if m.scrolled {
			t.Fatalf("[%s] reaching the bottom should clear scrolled (resume follow)", down.String())
		}
	}
}

// 要件 071: G は末尾 (最新) へジャンプして追従を再開する。
func TestScrollMode_GJumpsToBottom(t *testing.T) {
	m := scrollableScrollModel()
	m.scrollTop()
	if m.viewport.AtBottom() {
		t.Fatal("GotoTop should move off the bottom")
	}
	m.Update(runeKey('G'))
	if !m.viewport.AtBottom() {
		t.Fatal("G should jump to the bottom (latest)")
	}
	if m.scrolled {
		t.Fatal("G should resume follow (clear scrolled)")
	}
}

// 要件 071: 未定義キーは no-op でスクロールモードから抜けない。
func TestScrollMode_UnknownKeyIsNoop(t *testing.T) {
	m := scrollableScrollModel()
	m.Update(runeKey('x'))
	if m.mode != modeScroll {
		t.Fatal("unknown key must not leave scroll mode")
	}
	if m.scrolled {
		t.Fatal("unknown key must not scroll")
	}
}

// 要件 071: ":" プロンプトで :q / :quit を打つと insert へ退出し最下部 (最新) へ戻る。
func TestScrollMode_QuitExitsToInsert(t *testing.T) {
	for _, arg := range []string{"q", "quit"} {
		m := scrollableScrollModel()
		m.scrollTop() // 上にスクロールしておく
		m.Update(runeKey(':'))
		if !m.scrollPrompt {
			t.Fatal(": should open the scroll command prompt")
		}
		m.cmdInput.SetValue(arg)
		m.Update(tea.KeyMsg{Type: tea.KeyEnter})
		if m.mode != modeInsert {
			t.Fatalf(":%s should return to insert mode", arg)
		}
		if m.scrolled {
			t.Fatalf(":%s should clear scrolled (return to live view)", arg)
		}
		if !m.viewport.AtBottom() {
			t.Fatalf(":%s should return the viewport to the bottom", arg)
		}
	}
}

// 要件 071: ":" プロンプトの Esc はプロンプトのみキャンセルし、スクロールモードは抜けない
// (単発 Esc での誤爆退出を防ぐ設計)。
func TestScrollMode_PromptEscCancelsPromptOnly(t *testing.T) {
	m := scrollableScrollModel()
	m.Update(runeKey(':'))
	if !m.scrollPrompt {
		t.Fatal(": should open the prompt")
	}
	m.Update(tea.KeyMsg{Type: tea.KeyEsc})
	if m.scrollPrompt {
		t.Fatal("Esc should close the prompt")
	}
	if m.mode != modeScroll {
		t.Fatal("Esc in the prompt must NOT leave scroll mode")
	}
}

// 要件 071: ":" プロンプトで空 Enter はプロンプトを閉じるだけ (退出しない)。未知コマンドは
// E492 を出してプロンプトを閉じ、スクロールモードに留まる。
func TestScrollMode_PromptEmptyAndUnknown(t *testing.T) {
	// 空 Enter。
	m := scrollableScrollModel()
	m.Update(runeKey(':'))
	m.cmdInput.SetValue("")
	m.Update(tea.KeyMsg{Type: tea.KeyEnter})
	if m.scrollPrompt {
		t.Fatal("empty Enter should close the prompt")
	}
	if m.mode != modeScroll {
		t.Fatal("empty Enter must stay in scroll mode")
	}

	// 未知コマンド。
	m = scrollableScrollModel()
	before := len(m.msgs)
	m.Update(runeKey(':'))
	m.cmdInput.SetValue("bogus")
	m.Update(tea.KeyMsg{Type: tea.KeyEnter})
	if m.mode != modeScroll {
		t.Fatal("unknown scroll command must stay in scroll mode")
	}
	if len(m.msgs) != before+1 {
		t.Fatalf("unknown scroll command should append one info line, got %d new", len(m.msgs)-before)
	}
}

// 要件 071: command モードの :scroll でスクロールモードへ入る。
func TestCommandMode_ScrollCommandEntersScrollMode(t *testing.T) {
	m := scrollableCommandModel()
	m.cmdInput.SetValue("scroll")
	m.updateCommand(tea.KeyMsg{Type: tea.KeyEnter})
	if m.mode != modeScroll {
		t.Fatalf(":scroll should enter scroll mode, got mode=%d", m.mode)
	}
}

// 要件 071: command モードからスクロールは撤去した (PageUp / Ctrl+P 等でスクロールしない)。
func TestCommandMode_NoLongerScrolls(t *testing.T) {
	for _, k := range []tea.KeyType{tea.KeyPgUp, tea.KeyPgDown, tea.KeyCtrlP, tea.KeyCtrlN, tea.KeyCtrlU} {
		m := scrollableCommandModel()
		m.updateCommand(tea.KeyMsg{Type: k})
		if m.scrolled {
			t.Fatalf("%v must not scroll in command mode anymore", k)
		}
		if m.mode != modeCommand {
			t.Fatalf("%v must keep command mode, got %d", k, m.mode)
		}
	}
}

// 入力履歴 (↑/↓) は insert モードで従来どおりで、スクロールには使わない (非破壊)。
func TestInsertScroll_ArrowsStillNavigateHistory(t *testing.T) {
	m := scrollableInsertModel()
	m.history = []string{"first", "second"}
	m.historyPos = len(m.history)
	m.Update(tea.KeyMsg{Type: tea.KeyUp})
	if m.mode != modeInsert {
		t.Fatal("Up must not change mode (it navigates history)")
	}
	if got := m.input.Value(); got != "second" {
		t.Fatalf("Up should recall last history entry, got %q", got)
	}
}
