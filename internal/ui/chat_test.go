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
	_, cmd := m.Update(streamEndMsg{kind: kindOut, epoch: m.sessionN})
	if !isQuit(cmd) {
		t.Error("child exit without --auto-restart should quit (no restart prompt)")
	}
	if !hasInfo(m, "child process exited") {
		t.Errorf("expected '(child process exited)'; msgs=%v", m.msgs)
	}
}

// Ctrl+C = プログラム中断・再起動 (要件 025): 子を kill して新しいプロセスで
// やり直す。quit せず chat に留まり、sessionN++ と中断 info 行が出る。
// restart の Kill/Wait は fake handle (cmd=nil) で panic するため m.handle を外す。
func TestCtrlCInterruptRestarts(t *testing.T) {
	m := initialChatModel(fakeHandle(), ChatHeader{}, fakeSpawn())
	m.handle = nil // restart 内の Kill/Wait を踏ませない
	before := m.sessionN
	_, cmd := m.Update(tea.KeyMsg{Type: tea.KeyCtrlC})
	if isQuit(cmd) {
		t.Error("Ctrl+C should interrupt+restart, not quit")
	}
	if m.sessionN != before+1 {
		t.Errorf("Ctrl+C should restart: sessionN %d → %d, want %d", before, m.sessionN, before+1)
	}
	if !hasInfo(m, "中断") {
		t.Errorf("expected interrupt message; msgs=%v", m.msgs)
	}
}

// Ctrl+D = chat 終了 (要件 022 のまま): 子を kill して quit する。
func TestCtrlDQuits(t *testing.T) {
	m := initialChatModel(fakeHandle(), ChatHeader{}, fakeSpawn())
	m.handle = nil // Kill を踏ませない (nil ガード経由)
	_, cmd := m.Update(tea.KeyMsg{Type: tea.KeyCtrlD})
	if !isQuit(cmd) {
		t.Error("Ctrl+D should quit the chat")
	}
}

// spawn が無い (再起動不可) 経路では Ctrl+C は従来どおり quit にフォールバックする。
func TestCtrlCWithoutSpawnerQuits(t *testing.T) {
	m := initialChatModel(fakeHandle(), ChatHeader{}, nil)
	m.handle = nil
	_, cmd := m.Update(tea.KeyMsg{Type: tea.KeyCtrlC})
	if !isQuit(cmd) {
		t.Error("Ctrl+C without a spawner should fall back to quit")
	}
}

// リロードで差し替えた旧セッションの streamEndMsg (epoch 不一致) は破棄され、
// 新セッションの状態 (endedOut) を汚さない。
func TestStaleStreamEndDropped(t *testing.T) {
	m := initialChatModel(fakeHandle(), ChatHeader{}, fakeSpawn())
	m.endedErr = true
	_, cmd := m.Update(streamEndMsg{kind: kindOut, epoch: m.sessionN + 99}) // 旧 epoch
	if m.endedOut {
		t.Error("stale streamEndMsg should be dropped, not set endedOut")
	}
	if isQuit(cmd) {
		t.Error("stale streamEndMsg should not trigger quit")
	}
}

// 保存検知 (fileChangedMsg{changed}) で info メッセージを出して再 spawn (sessionN++) する。
// restart の Kill/Wait は fake handle (cmd=nil) で panic するため、旧 handle を外して回避する。
func TestFileChangedReloads(t *testing.T) {
	m := initialChatModel(fakeHandle(), ChatHeader{}, fakeSpawn())
	m.handle = nil // restart 内の Kill/Wait を踏ませない (spawn される新 handle は触らない)
	before := m.sessionN
	m.Update(fileChangedMsg{changed: true})
	if m.sessionN != before+1 {
		t.Errorf("file change should restart: sessionN %d → %d, want %d", before, m.sessionN, before+1)
	}
	if !hasInfo(m, "解答ファイルが更新されました") {
		t.Errorf("expected file-updated message; msgs=%v", m.msgs)
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
