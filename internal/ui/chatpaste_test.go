package ui

import (
	"bytes"
	"io"
	"strings"
	"testing"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

func TestSplitPasteLines(t *testing.T) {
	cases := []struct {
		name          string
		current       string
		pasted        string
		wantSend      []string
		wantRemainder string
	}{
		{"trailing newline", "", "5\n1 2 3\n", []string{"5", "1 2 3"}, ""},
		{"no trailing newline", "", "5\n1 2 3", []string{"5"}, "1 2 3"},
		{"with current value", "ab", "c\nd\n", []string{"abc", "d"}, ""},
		{"empty lines kept", "", "a\n\nb\n", []string{"a", "", "b"}, ""},
		{"crlf normalized", "", "a\r\nb\r\n", []string{"a", "b"}, ""},
		{"cr only normalized", "", "a\rb\r", []string{"a", "b"}, ""},
		{"no newline", "x", "yz", nil, "xyz"},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			send, rem := splitPasteLines(c.current, c.pasted)
			if rem != c.wantRemainder {
				t.Errorf("remainder = %q, want %q", rem, c.wantRemainder)
			}
			if strings.Join(send, "|") != strings.Join(c.wantSend, "|") {
				t.Errorf("send = %q, want %q", send, c.wantSend)
			}
		})
	}
}

// runningModel は buffer を stdin に持つ起動済み (running) の chat モデルを返す。
func runningModel() (*chatModel, *bytes.Buffer) {
	var buf bytes.Buffer
	m := initialChatModel(ChatHeader{}, fakeSpawn())
	m.Update(tea.WindowSizeMsg{Width: 80, Height: 24})
	m.handle = &runner.ChatHandle{
		Stdin:  nopWriteCloser{&buf},
		Stdout: io.NopCloser(strings.NewReader("")),
		Stderr: io.NopCloser(strings.NewReader("")),
	}
	m.running = true
	m.sessionN = 1
	return m, &buf
}

func countKind(m *chatModel, kind string) int {
	n := 0
	for _, l := range m.msgs {
		if l.kind == kind {
			n++
		}
	}
	return n
}

// submitLines は各行を子へ Fprintln し、空行も 1 行として送る。履歴には非空行のみ積む。
func TestSubmitLinesSendsEach(t *testing.T) {
	m, buf := runningModel()
	var cmds []tea.Cmd
	m.submitLines([]string{"a", "b", ""}, &cmds)

	if buf.String() != "a\nb\n\n" {
		t.Errorf("stdin = %q, want \"a\\nb\\n\\n\"", buf.String())
	}
	if n := countKind(m, kindIn); n != 3 {
		t.Errorf("kindIn lines = %d, want 3 (a, b, empty)", n)
	}
	if len(m.history) != 2 {
		t.Errorf("history = %v, want [a b] (empty line not recorded)", m.history)
	}
	if len(cmds) == 0 {
		t.Error("expected a startAwaiting cmd after sending")
	}
}

// 複数行ペーストは完全な行を逐次送信し、末尾の未改行行を入力欄に残す。
func TestPasteSendsCompleteLinesKeepsRemainder(t *testing.T) {
	m, buf := runningModel()
	m.Update(tea.KeyMsg{Type: tea.KeyRunes, Paste: true, Runes: []rune("3\n1 2 3\nq")})

	if buf.String() != "3\n1 2 3\n" {
		t.Errorf("stdin = %q, want \"3\\n1 2 3\\n\"", buf.String())
	}
	if m.input.Value() != "q" {
		t.Errorf("input remainder = %q, want \"q\"", m.input.Value())
	}
	if n := countKind(m, kindIn); n != 2 {
		t.Errorf("kindIn lines = %d, want 2", n)
	}
}

// 末尾が改行のペーストは全行送信し入力欄は空になる (CRLF も正規化)。
func TestPasteTrailingNewlineClearsInput(t *testing.T) {
	m, buf := runningModel()
	m.Update(tea.KeyMsg{Type: tea.KeyRunes, Paste: true, Runes: []rune("a\r\nb\r\n")})

	if buf.String() != "a\nb\n" {
		t.Errorf("stdin = %q, want \"a\\nb\\n\"", buf.String())
	}
	if m.input.Value() != "" {
		t.Errorf("input = %q, want empty", m.input.Value())
	}
}

// 改行を含まないペーストは送信せず、通常入力として textinput に流れる (1 行扱い)。
func TestPasteWithoutNewlineDoesNotSend(t *testing.T) {
	m, buf := runningModel()
	m.Update(tea.KeyMsg{Type: tea.KeyRunes, Paste: true, Runes: []rune("hello")})
	if buf.Len() != 0 {
		t.Errorf("single-line paste should not send to child; stdin = %q", buf.String())
	}
}
