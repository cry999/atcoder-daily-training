package ui

import (
	"testing"
	"time"
)

// classifyTraceback の単体テスト。統合ストリーム上で Python traceback ブロックを
// 行内容から復元できること (連鎖例外・空行・例外メッセージ行での終端を含む)。
func TestClassifyTraceback(t *testing.T) {
	// 1 本のシーケンスを順に流し、各行の (isErr, next) を検証する。
	type step struct {
		line     string
		wantErr  bool
		wantNext bool
	}
	steps := []step{
		{"hello", false, false},                               // 通常の stdout
		{"Traceback (most recent call last):", true, true},    // traceback 開始
		{`  File "main.py", line 3, in <module>`, true, true}, // フレーム (インデント)
		{"    x = 1 / 0", true, true},                         // フレーム本体
		{"", true, true},                                      // 空行はブロック継続
		{"ZeroDivisionError: division by zero", true, false},  // 例外メッセージ行で終端
		{"after", false, false},                               // 終端後は通常 stdout に戻る
		{"During handling of the above exception, another exception occurred:", true, true}, // 連鎖ブリッジ
		{"Traceback (most recent call last):", true, true},
		{"ValueError: boom", true, false},
		{"tail", false, false},
	}
	inTB := false
	for i, s := range steps {
		isErr, next := classifyTraceback(inTB, s.line)
		if isErr != s.wantErr || next != s.wantNext {
			t.Errorf("step %d %q: got (isErr=%v, next=%v), want (%v, %v)", i, s.line, isErr, next, s.wantErr, s.wantNext)
		}
		inTB = next
	}
}

// 統合ストリーム (DEBUG=stdout と traceback=stderr が 1 本に束ねられて届く) を
// Update に順に流したとき、DEBUG 行は kindDebug、traceback 行は kindErr に分類され、
// **出力順がそのまま保たれる** こと。バグ (互い違い表示) はこの順序が崩れる症状だった。
func TestChatMergedStreamPreservesOrderAndColors(t *testing.T) {
	m := &chatModel{header: ChatHeader{Debug: true}, lastEventAt: time.Now()}

	// StartChat が stdout/stderr を 1 本に束ねるので、すべて kindOut として届く。
	lines := []string{
		"[DEBUG] before crash",
		"Traceback (most recent call last):",
		`  File "main.py", line 1, in <module>`,
		"    raise RuntimeError('x')",
		"RuntimeError: x",
		"done",
	}
	for _, ln := range lines {
		m.Update(chatLineMsg{kind: kindOut, text: ln})
	}

	want := []struct {
		kind string
		text string
	}{
		{kindDebug, "before crash"},
		{kindErr, "Traceback (most recent call last):"},
		{kindErr, `  File "main.py", line 1, in <module>`},
		{kindErr, "    raise RuntimeError('x')"},
		{kindErr, "RuntimeError: x"},
		{kindOut, "done"},
	}
	if len(m.msgs) != len(want) {
		t.Fatalf("got %d msgs, want %d: %+v", len(m.msgs), len(want), m.msgs)
	}
	for i, w := range want {
		got := m.msgs[i]
		if got.kind != w.kind || got.text != w.text {
			t.Errorf("msg %d = {kind:%q text:%q}, want {kind:%q text:%q}", i, got.kind, got.text, w.kind, w.text)
		}
	}
}
