package ui

import (
	"testing"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

// 要件 030: Ctrl+D 1 回目 = プログラムをリセット (restart で再 spawn) + 武装。終了しない。
// handle=nil で始めて restart の旧プロセス Kill を踏まない (fakeHandle.Kill はテストでは呼ばない)。
func TestCtrlD_FirstResetsAndArms(t *testing.T) {
	spawnCalls := 0
	spawn := func() (*runner.ChatHandle, error) { spawnCalls++; return fakeHandle(), nil }
	m := &chatModel{spawn: spawn} // handle=nil, running=false

	_, cmd := m.Update(tea.KeyMsg{Type: tea.KeyCtrlD})

	if isQuit(cmd) {
		t.Fatal("1st Ctrl+D should reset (restart), not quit")
	}
	if !m.ctrlDArmed {
		t.Fatal("1st Ctrl+D should arm (a 2nd Ctrl+D quits)")
	}
	if spawnCalls != 1 {
		t.Fatalf("1st Ctrl+D should restart the program (spawn=1), got %d", spawnCalls)
	}
	if !m.running {
		t.Fatal("after the reset the child should be running")
	}
}

// 1 回目 = 武装のみ (リセット不可なら)、2 回連続 = chat 終了。spawn=nil で Kill を踏まない。
func TestCtrlD_ArmsThenSecondQuits(t *testing.T) {
	m := &chatModel{spawn: nil} // 再起動不可。1 回目は武装のみ

	_, cmd1 := m.Update(tea.KeyMsg{Type: tea.KeyCtrlD})
	if isQuit(cmd1) {
		t.Fatal("1st Ctrl+D should arm, not quit")
	}
	if !m.ctrlDArmed {
		t.Fatal("1st Ctrl+D should arm")
	}

	_, cmd2 := m.Update(tea.KeyMsg{Type: tea.KeyCtrlD})
	if !isQuit(cmd2) {
		t.Fatal("2nd consecutive Ctrl+D should quit the chat")
	}
}

// 間に他のキー (履歴の ↑) が挟まると武装が解け、次の Ctrl+D は 1 回目に戻る。
// 解除は KeyMsg 先頭の一律クリアなので、どのキーでも効く (代表として ↑)。
func TestCtrlD_InterveningKeyDisarms(t *testing.T) {
	m := &chatModel{spawn: nil}

	m.Update(tea.KeyMsg{Type: tea.KeyCtrlD}) // 1st: arm
	if !m.ctrlDArmed {
		t.Fatal("armed after the 1st Ctrl+D")
	}
	m.Update(tea.KeyMsg{Type: tea.KeyUp}) // 他キー → 武装解除
	if m.ctrlDArmed {
		t.Fatal("an intervening key should disarm Ctrl+D")
	}
	_, cmd := m.Update(tea.KeyMsg{Type: tea.KeyCtrlD}) // 1st again, not quit
	if isQuit(cmd) {
		t.Fatal("Ctrl+D after an intervening key should reset (1st), not quit")
	}
}

// 非キー msg (子の出力到着) は武装を解かない: Ctrl+D → 出力 → Ctrl+D で終了できる。
func TestCtrlD_NonKeyMsgKeepsArmed(t *testing.T) {
	m := &chatModel{spawn: nil}

	m.Update(tea.KeyMsg{Type: tea.KeyCtrlD}) // arm
	// 子の出力が届く (非キー)。武装は維持されるべき。
	m.Update(chatLineMsg{kind: kindOut, text: "hello", epoch: m.sessionN})
	if !m.ctrlDArmed {
		t.Fatal("a non-key message (output) must NOT disarm Ctrl+D")
	}
	_, cmd := m.Update(tea.KeyMsg{Type: tea.KeyCtrlD})
	if !isQuit(cmd) {
		t.Fatal("2nd Ctrl+D after only output should still quit")
	}
}
