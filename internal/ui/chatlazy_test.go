package ui

import (
	"testing"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

// バグ: auto-restart 時に子終了で即再 spawn し、入力を読まず即終了する解答だと
// 無限ループになる。修正後は子終了で即再 spawn せず、入力を機に再実行する。
func TestNoAutoRespawnOnChildExit(t *testing.T) {
	spawnCalls := 0
	spawn := func() (*runner.ChatHandle, error) { spawnCalls++; return fakeHandle(), nil }
	m := &chatModel{spawn: spawn, autoRestart: true, running: true, handle: fakeHandle(), endedErr: true}

	// out 側も EOF で両ストリーム終了 = 子プロセス終了。
	_, cmd := m.Update(streamEndMsg{kind: kindOut, epoch: m.sessionN})

	if m.running {
		t.Error("child exit should clear running")
	}
	if spawnCalls != 0 {
		t.Errorf("must NOT auto-respawn on exit (infinite loop), spawn called %d times", spawnCalls)
	}
	if isQuit(cmd) {
		t.Error("auto-restart: child exit should wait for input, not quit")
	}
}

// auto-restart 無しでは従来どおり子終了で quit (1 回実行)。
func TestExitQuitsWithoutAutoRestart(t *testing.T) {
	m := &chatModel{running: true, handle: fakeHandle(), endedErr: true}
	_, cmd := m.Update(streamEndMsg{kind: kindOut, epoch: m.sessionN})
	if !isQuit(cmd) {
		t.Error("without --auto-restart, child exit should quit")
	}
}

// 遅延起動: 開いた時点では子なし。最初の Enter で初めて spawn する。
func TestLazyStartSpawnsOnFirstInput(t *testing.T) {
	spawnCalls := 0
	spawn := func() (*runner.ChatHandle, error) { spawnCalls++; return fakeHandle(), nil }
	ti := textinput.New()
	ti.SetValue("5")
	m := &chatModel{spawn: spawn, input: ti} // running=false, handle=nil (lazy)

	if m.running || m.handle != nil {
		t.Fatal("model should start with no child (lazy start)")
	}
	m.Update(tea.KeyMsg{Type: tea.KeyEnter})
	if spawnCalls != 1 {
		t.Errorf("first Enter should spawn the child, got %d spawn calls", spawnCalls)
	}
	if !m.running {
		t.Error("child should be running after the first input")
	}
}

// 子終了後 (待機中) に入力を送ると再実行する (入力で再起動)。
func TestRespawnOnInputAfterExit(t *testing.T) {
	spawnCalls := 0
	spawn := func() (*runner.ChatHandle, error) { spawnCalls++; return fakeHandle(), nil }
	ti := textinput.New()
	ti.SetValue("next")
	// 直前に子が終了して running=false の状態。
	m := &chatModel{spawn: spawn, autoRestart: true, input: ti, running: false, endedOut: true, endedErr: true}

	m.Update(tea.KeyMsg{Type: tea.KeyEnter})
	if spawnCalls != 1 {
		t.Errorf("input after exit should respawn once, got %d", spawnCalls)
	}
	if !m.running {
		t.Error("child should be running again after input")
	}
}
