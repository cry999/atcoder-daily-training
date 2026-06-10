package ui

import (
	"io"
	"strings"
	"testing"
	"time"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

func TestFormatDur(t *testing.T) {
	cases := []struct {
		d    time.Duration
		want string
	}{
		{0, "0"},
		{-5 * time.Millisecond, "0"}, // 負値は 0 に丸める
		{830 * time.Nanosecond, "830ns"},
		{340 * time.Microsecond, "340µs"},
		{1 * time.Microsecond, "1µs"},
		{340600 * time.Nanosecond, "341µs"}, // µs に四捨五入
		{1500 * time.Microsecond, "2ms"},    // 1.5ms → 四捨五入で 2ms (最大単位のみ)
		{2500 * time.Microsecond, "3ms"},    // 2.5ms → 3ms (半数は切り上げ)
		{12 * time.Millisecond, "12ms"},
		{218 * time.Millisecond, "218ms"},
		{1100 * time.Millisecond, "1100ms"}, // 1.1s は ms 表示 (< 10s)
		{1500 * time.Millisecond, "1500ms"}, // 1.5s も ms 表示
		{9999 * time.Millisecond, "9999ms"}, // 10s 未満は ms
		{10 * time.Second, "10s"},           // 10s ちょうどは s
		{12345 * time.Millisecond, "12s"},   // 12.345s → 12s (秒に四捨五入)
		{12678 * time.Millisecond, "13s"},   // 12.678s → 13s (切り上げ)
	}
	for _, c := range cases {
		if got := formatDur(c.d); got != c.want {
			t.Errorf("formatDur(%v) = %q, want %q", c.d, got, c.want)
		}
	}
}

// 出力行に直前イベントからの経過時間が載ること。連続出力は直前の出力からの差分、
// 時刻の巻き戻りは 0 にクランプされること。
func TestChatOutputElapsed(t *testing.T) {
	base := time.Now()
	m := &chatModel{lastEventAt: base}

	m.Update(chatLineMsg{kind: kindOut, text: "first", at: base.Add(5 * time.Millisecond)})
	if last := m.msgs[len(m.msgs)-1]; !last.hasDur || last.dur != 5*time.Millisecond {
		t.Errorf("first out line dur = %v (hasDur=%v), want 5ms", last.dur, last.hasDur)
	}

	// 直前の出力 (base+5ms) からの差分 = 2ms。
	m.Update(chatLineMsg{kind: kindOut, text: "second", at: base.Add(7 * time.Millisecond)})
	if last := m.msgs[len(m.msgs)-1]; last.dur != 2*time.Millisecond {
		t.Errorf("second out line dur = %v, want 2ms", last.dur)
	}

	// 受信時刻が直前より前 (時計ズレ) なら 0 にクランプ。
	m.Update(chatLineMsg{kind: kindErr, text: "warn", at: base})
	if last := m.msgs[len(m.msgs)-1]; !last.hasDur || last.dur != 0 {
		t.Errorf("clamped dur = %v (hasDur=%v), want 0", last.dur, last.hasDur)
	}
}

// fakeHandle は initialChatModel が scanner を張れるだけの最小 ChatHandle (空 stream)。
func fakeHandle() *runner.ChatHandle {
	return &runner.ChatHandle{
		Stdout: io.NopCloser(strings.NewReader("")),
		Stderr: io.NopCloser(strings.NewReader("")),
	}
}

func fakeSpawn() Spawner {
	return func() (*runner.ChatHandle, error) { return fakeHandle(), nil }
}

func TestInitialChatModelAutoRestartOn(t *testing.T) {
	m := initialChatModel(fakeHandle(), ChatHeader{AutoRestart: true}, fakeSpawn())
	if !m.autoRestart {
		t.Error("autoRestart should be true when header.AutoRestart && spawn != nil")
	}
	if !m.autoHintShown || !hasInfo(m, "auto-restart on") {
		t.Errorf("expected the startup auto-restart hint; msgs=%v", m.msgs)
	}
}

func TestInitialChatModelAutoRestartOff(t *testing.T) {
	m := initialChatModel(fakeHandle(), ChatHeader{}, fakeSpawn())
	if m.autoRestart {
		t.Error("autoRestart should default to false")
	}
	if hasInfo(m, "auto-restart on") {
		t.Error("no hint expected without --auto-restart")
	}
}

func TestInitialChatModelAutoRestartNeedsSpawner(t *testing.T) {
	// spawn == nil では再起動できないので autoRestart は立てない。
	m := initialChatModel(fakeHandle(), ChatHeader{AutoRestart: true}, nil)
	if m.autoRestart {
		t.Error("autoRestart should be false when spawn == nil (cannot restart)")
	}
}

func TestStreamEndQuitsWhenNoAutoRestart(t *testing.T) {
	m := initialChatModel(fakeHandle(), ChatHeader{}, fakeSpawn())
	m.endedErr = true // err 側は既に EOF。out 側 EOF で「両ストリーム終了」になる。
	_, cmd := m.Update(streamEndMsg{kind: kindOut})
	if !isQuit(cmd) {
		t.Error("child exit without --auto-restart should quit (no restart prompt)")
	}
	if !hasInfo(m, "child process exited") {
		t.Errorf("expected '(child process exited)'; msgs=%v", m.msgs)
	}
}

func TestStreamEndQuitsWhenQuitOnChildExit(t *testing.T) {
	m := initialChatModel(fakeHandle(), ChatHeader{AutoRestart: true}, fakeSpawn())
	m.quitOnChildExit = true // Ctrl+D 後の状態
	m.endedErr = true
	_, cmd := m.Update(streamEndMsg{kind: kindOut})
	if !isQuit(cmd) {
		t.Error("quitOnChildExit should win over autoRestart and quit")
	}
}

func hasInfo(m *chatModel, substr string) bool {
	for _, l := range m.msgs {
		if strings.Contains(l.text, substr) {
			return true
		}
	}
	return false
}

func isQuit(cmd tea.Cmd) bool {
	if cmd == nil {
		return false
	}
	_, ok := cmd().(tea.QuitMsg)
	return ok
}

// Ctrl+D は子に EOF を送らず CLI 側の終了操作。auto-restart の有無で動作が分かれる。
func TestCtrlDActionFor(t *testing.T) {
	if got := ctrlDActionFor(false); got != ctrlDQuit {
		t.Errorf("ctrlDActionFor(false) = %d, want ctrlDQuit", got)
	}
	if got := ctrlDActionFor(true); got != ctrlDStopAfterSession {
		t.Errorf("ctrlDActionFor(true) = %d, want ctrlDStopAfterSession", got)
	}
}
