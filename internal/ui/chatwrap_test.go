package ui

import (
	"strings"
	"testing"
	"time"

	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/x/ansi"
)

func TestHardWrap(t *testing.T) {
	cases := []struct {
		s     string
		width int
		want  []string
	}{
		{"abcdef", 3, []string{"abc", "def"}},
		{"abcdefg", 3, []string{"abc", "def", "g"}},
		{"ab", 5, []string{"ab"}},
		{"", 5, []string{""}},               // 空文字でも 1 行確保
		{"abc", 0, []string{"a", "b", "c"}}, // 幅 0 は 1 にクランプ
	}
	for _, c := range cases {
		got := hardWrap(c.s, c.width)
		if strings.Join(got, "|") != strings.Join(c.want, "|") {
			t.Errorf("hardWrap(%q, %d) = %v, want %v", c.s, c.width, got, c.want)
		}
	}
}

// 全角は 2 桁として数える。
func TestHardWrapWide(t *testing.T) {
	got := hardWrap("あいう", 4) // 各 2 桁 → 4 桁に 2 文字ずつ
	if strings.Join(got, "|") != "あい|う" {
		t.Errorf("hardWrap wide = %v, want [あい う]", got)
	}
}

// 長い出力行は折り返され、継続行は揃ったインデント + マーカー (↪) を持つ。
func TestRenderMsgBlockWrapsAligned(t *testing.T) {
	const width = 30
	// avail = 30 - (leadColW+2) = 30 - 9 = 21。21 桁を超える本文で折り返す。
	text := strings.Repeat("x", 50)
	msg := chatLine{kind: kindOut, text: text, hasDur: true, dur: 5 * time.Millisecond}

	block := renderMsgBlock(msg, width)
	lines := strings.Split(block, "\n")
	if len(lines) < 2 {
		t.Fatalf("long output should wrap into multiple lines, got %d", len(lines))
	}

	// 各行は viewport 幅に収まる (クリップされない)。
	for i, ln := range lines {
		if w := lipgloss.Width(ln); w > width {
			t.Errorf("line %d width %d > %d: %q", i, w, width, ansi.Strip(ln))
		}
	}

	// 1 行目は「経過時間カラム + 矢印」。leadColW(7) 幅の "   5ms " + "← "。
	first := ansi.Strip(lines[0])
	if !strings.HasPrefix(first, "   5ms ← ") {
		t.Errorf("first line prefix = %q, want '   5ms ← '", first)
	}

	// 継続行は leadColW(7) 空白 + マーカー (↪) + スペースで、本文カラムが 1 行目と揃う。
	contPrefix := strings.Repeat(" ", leadColW) + wrapMarker + " "
	for i := 1; i < len(lines); i++ {
		cont := ansi.Strip(lines[i])
		if !strings.HasPrefix(cont, contPrefix) {
			t.Errorf("continuation line %d = %q, want prefix %q (aligned + ↪ marker)", i, cont, contPrefix)
		}
	}

	// 本文を連結すると元に戻る (折り返しで欠落しない)。
	var joined strings.Builder
	joined.WriteString(strings.TrimPrefix(first, "   5ms ← "))
	for i := 1; i < len(lines); i++ {
		joined.WriteString(strings.TrimPrefix(ansi.Strip(lines[i]), contPrefix))
	}
	if joined.String() != text {
		t.Errorf("reassembled text = %q, want %q (no characters dropped)", joined.String(), text)
	}
}

// debug 行は角丸ピル ( DEBUG ) を行頭に置き、本文・継続行が幅に収まり揃う。
func TestRenderMsgBlockDebugPill(t *testing.T) {
	const width = 40
	text := strings.Repeat("z", 60) // 折り返すだけの長さ
	msg := chatLine{kind: kindDebug, text: text, hasDur: true, dur: 2 * time.Millisecond}

	block := renderMsgBlock(msg, width)
	lines := strings.Split(block, "\n")
	if len(lines) < 2 {
		t.Fatalf("long debug line should wrap, got %d lines", len(lines))
	}

	// 各行は viewport 幅に収まる。
	for i, ln := range lines {
		if w := lipgloss.Width(ln); w > width {
			t.Errorf("line %d width %d > %d: %q", i, w, width, ansi.Strip(ln))
		}
	}

	// 1 行目には角丸キャップで挟んだ DEBUG ピルが含まれる。
	first := ansi.Strip(lines[0])
	if !strings.Contains(first, plRoundLeft+"DEBUG"+plRoundRight) {
		t.Errorf("first line missing rounded DEBUG pill: %q", first)
	}

	// 継続行は leadColW + (debugPillWidth-1) 空白 + マーカーで、本文カラムが 1 行目と揃う。
	contPrefix := strings.Repeat(" ", leadColW+debugPillWidth-1) + wrapMarker + " "
	for i := 1; i < len(lines); i++ {
		if cont := ansi.Strip(lines[i]); !strings.HasPrefix(cont, contPrefix) {
			t.Errorf("continuation line %d = %q, want prefix %q", i, cont, contPrefix)
		}
	}

	// 本文を連結すると元に戻る (折り返しで欠落しない)。
	pillPrefix := plRoundLeft + "DEBUG" + plRoundRight + " "
	var joined strings.Builder
	joined.WriteString(strings.TrimPrefix(first[leadColW:], pillPrefix))
	for i := 1; i < len(lines); i++ {
		joined.WriteString(strings.TrimPrefix(ansi.Strip(lines[i]), contPrefix))
	}
	if joined.String() != text {
		t.Errorf("reassembled text = %q, want %q", joined.String(), text)
	}
}

// 入力行と出力行のインデント (矢印カラム) が揃う。
func TestRenderMsgBlockInOutAligned(t *testing.T) {
	in := ansi.Strip(renderMsgBlock(chatLine{kind: kindIn, text: "hi"}, 40))
	out := ansi.Strip(renderMsgBlock(chatLine{kind: kindOut, text: "yo", hasDur: true, dur: time.Millisecond}, 40))
	// どちらも矢印は leadColW(7) 桁の直後に来る (leadColW までは ASCII なのでバイト境界と一致)。
	if !strings.HasPrefix(in[leadColW:], "→") {
		t.Errorf("input arrow not at column %d: %q", leadColW, in)
	}
	if !strings.HasPrefix(out[leadColW:], "←") {
		t.Errorf("output arrow not at column %d: %q", leadColW, out)
	}
}
