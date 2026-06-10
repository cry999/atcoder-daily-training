package ui

import (
	"bytes"
	"io"
	"strings"
	"testing"
	"time"

	"github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/bubbles/viewport"
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
		handle:  &runner.ChatHandle{Stdin: nopWriteCloser{&bytes.Buffer{}}},
		input:   ti,
		running: true, // 既に子が動いている状態 (送信のみ。再 spawn 経路は通らない)
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

func TestSpinnerShownInOutputTail(t *testing.T) {
	m := &chatModel{width: 40, height: 20, ready: true}
	m.viewport = viewport.New(40, 5)
	// 非待機: 出力末尾にスピナーは出ない。
	m.refreshViewport()
	if strings.ContainsAny(m.viewport.View(), strings.Join(spinnerFrames, "")) {
		t.Error("viewport should not contain a spinner when not awaiting")
	}
	// 待機: 出力の最後尾にスピナーのコマが出る。
	m.startAwaiting()
	m.refreshViewport()
	if !strings.Contains(m.viewport.View(), spinnerFrames[m.spinnerFrame%len(spinnerFrames)]) {
		t.Errorf("viewport tail should contain the spinner frame while awaiting: %q", m.viewport.View())
	}
}

func TestInputBoxBottomRulePlainWhileAwaiting(t *testing.T) {
	m := &chatModel{width: 40, input: textinput.New()}
	m.startAwaiting()
	// スピナーは入力ボックスの下罫線ではなく出力末尾に出すので、下罫線は素の罫線。
	bottom := lastLine(m.renderInputBox())
	if strings.ContainsAny(bottom, strings.Join(spinnerFrames, "")) {
		t.Errorf("input box bottom rule should be plain (no spinner): %q", bottom)
	}
}

func lastLine(s string) string {
	lines := strings.Split(s, "\n")
	return lines[len(lines)-1]
}
