package ui

import (
	"bytes"
	"io"
	"strings"
	"testing"
	"time"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

type nopWriteCloser struct{ io.Writer }

func (nopWriteCloser) Close() error { return nil }

func TestWaitStatus(t *testing.T) {
	// frame はコマ配列 index、経過は formatDur 表記 (出力行の経過カラムと揃える)。
	if got := waitStatus(0, 400*time.Millisecond); got != "⠋ 400ms" {
		t.Errorf("waitStatus(0, 400ms) = %q, want '⠋ 400ms'", got)
	}
	if got := waitStatus(2, 5*time.Second); got != "⠹ 5000ms" {
		t.Errorf("waitStatus(2, 5s) = %q, want '⠹ 5000ms'", got)
	}
	// frame はコマ数で巡回する (10 → 0)。
	if waitStatus(len(spinnerFrames), time.Second) != waitStatus(0, time.Second) {
		t.Errorf("frame index should wrap around modulo %d", len(spinnerFrames))
	}
}

func TestSpinnerTickAdvancesAndStops(t *testing.T) {
	m := &chatModel{}
	m.startAwaiting()
	if !m.awaiting {
		t.Fatal("startAwaiting should set awaiting=true")
	}
	gen := m.spinGen

	// 正しい世代の tick はコマを進めて再アームする。
	before := m.spinnerFrame
	_, cmd := m.Update(spinnerTickMsg{gen: gen})
	if m.spinnerFrame != before+1 {
		t.Errorf("tick should advance the spinner frame")
	}
	if cmd == nil {
		t.Errorf("tick should re-arm while awaiting (non-nil cmd)")
	}

	// 古い世代の tick は無視 (コマも進めない)。
	f := m.spinnerFrame
	m.Update(spinnerTickMsg{gen: gen - 1})
	if m.spinnerFrame != f {
		t.Errorf("stale-gen tick must be ignored")
	}

	// 待機解除後の tick は止まる (再アームしない)。
	m.stopAwaiting()
	_, cmd2 := m.Update(spinnerTickMsg{gen: gen})
	if cmd2 != nil {
		t.Errorf("tick after stopAwaiting should not re-arm")
	}
}

func TestEnterStartsAwaiting(t *testing.T) {
	ti := textinput.New()
	ti.SetValue("5")
	m := &chatModel{
		handle: &runner.ChatHandle{Stdin: nopWriteCloser{&bytes.Buffer{}}},
		input:  ti,
	}
	gen0 := m.spinGen
	m.Update(tea.KeyMsg{Type: tea.KeyEnter})
	if !m.awaiting {
		t.Error("Enter (send success) should start awaiting (spinner)")
	}
	if m.spinGen != gen0+1 {
		t.Errorf("Enter should bump spinGen to start a fresh tick loop")
	}
}

func TestOutputStopsAwaiting(t *testing.T) {
	m := &chatModel{} // sessionN=0
	m.startAwaiting()
	// 出力行が届くと待機解除。epoch は現行 sessionN に合わせる。
	m.Update(chatLineMsg{kind: kindOut, text: "10", epoch: m.sessionN})
	if m.awaiting {
		t.Error("an output line should stop awaiting (hide the spinner)")
	}
}

func TestBottomRuleShowsSpinnerWhileAwaiting(t *testing.T) {
	m := &chatModel{width: 40}
	// 非待機: 通常の罫線 (スピナー無し)。
	if strings.ContainsAny(m.renderBottomRule(40), strings.Join(spinnerFrames, "")) {
		t.Error("bottom rule should be plain when not awaiting")
	}
	// 待機: スピナーのコマを含む。
	m.startAwaiting()
	got := m.renderBottomRule(40)
	if !strings.Contains(got, spinnerFrames[m.spinnerFrame%len(spinnerFrames)]) {
		t.Errorf("bottom rule while awaiting should contain the spinner frame: %q", got)
	}
}
