package ui

import (
	"testing"
	"time"
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
		{1500 * time.Microsecond, "1.5ms"}, // 1 桁台 ms は小数 1 桁
		{12 * time.Millisecond, "12ms"},
		{218 * time.Millisecond, "218ms"},
		{1500 * time.Millisecond, "1.50s"},
		{2340 * time.Millisecond, "2.34s"},
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
