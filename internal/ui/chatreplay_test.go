package ui

import (
	"bytes"
	"io"
	"strings"
	"testing"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

// :replay は parseCommand で name="replay" になる (要件 039)。
func TestParseCommandReplay(t *testing.T) {
	if got := parseCommand("replay"); got.name != "replay" {
		t.Errorf("parseCommand(replay).name = %q, want replay", got.name)
	}
}

// 今回分も前回分も無ければ :replay は info 行のみで子を起動しない。
func TestExecReplayNoInputs(t *testing.T) {
	spawnCalls := 0
	spawn := func() (*runner.ChatHandle, error) { spawnCalls++; return fakeHandle(), nil }
	m := &chatModel{spawn: spawn, header: ChatHeader{}} // runInputs=nil, PrevInputs=nil

	m.execReplay()

	if spawnCalls != 0 {
		t.Errorf("no inputs must not spawn, got %d", spawnCalls)
	}
	if m.running {
		t.Error("no inputs: child must not be running")
	}
	if !hasInfo(m, "再生できる入力がありません") {
		t.Error("expected the empty-history info line")
	}
}

// 今回の起動で入力を送っていれば、:replay は (PrevInputs ではなく) 今回分を再生する。
// コード修正後に同じ入力を流し直す主用途。
func TestExecReplayPrefersCurrentRunInputs(t *testing.T) {
	var stdin bytes.Buffer
	spawn := func() (*runner.ChatHandle, error) {
		return &runner.ChatHandle{
			Stdin:  nopWriteCloser{&stdin},
			Stdout: io.NopCloser(strings.NewReader("")),
			Stderr: io.NopCloser(strings.NewReader("")),
		}, nil
	}
	// 今回の入力 (runInputs) があり、前回入力 (PrevInputs) とは別物。
	m := &chatModel{spawn: spawn,
		runInputs: []string{"now 1", "now 2"},
		header:    ChatHeader{PrevInputs: []string{"old 1"}},
	}

	m.execReplay()

	if got, want := stdin.String(), "now 1\nnow 2\n"; got != want {
		t.Errorf("replay should re-send current-run inputs: stdin = %q, want %q", got, want)
	}
	// 二重化防止: 再生後 runInputs は再生分そのものに揃う (倍にならない)。
	if want := []string{"now 1", "now 2"}; !equalStrings(m.runInputs, want) {
		t.Errorf("runInputs after replay = %v, want %v (must not double)", m.runInputs, want)
	}
}

// 今回まだ何も送っていなければ :replay は前回セッションの入力にフォールバックする。
func TestExecReplaySendsPrevInputs(t *testing.T) {
	var stdin bytes.Buffer
	spawnCalls := 0
	spawn := func() (*runner.ChatHandle, error) {
		spawnCalls++
		return &runner.ChatHandle{
			Stdin:  nopWriteCloser{&stdin},
			Stdout: io.NopCloser(strings.NewReader("")),
			Stderr: io.NopCloser(strings.NewReader("")),
		}, nil
	}
	// 遅延状態 (running=false, handle=nil) から開始 — restart は既存子を Kill しない。
	m := &chatModel{spawn: spawn, header: ChatHeader{PrevInputs: []string{"5 3", "go", ""}}}

	m.execReplay()

	if spawnCalls != 1 {
		t.Fatalf("replay should restart (spawn) exactly once, got %d", spawnCalls)
	}
	if !m.running {
		t.Error("child should be running after replay")
	}
	// 空行を含め、前回入力を順に改行付きで送る (空 Enter も再現対象)。
	if got, want := stdin.String(), "5 3\ngo\n\n"; got != want {
		t.Errorf("stdin = %q, want %q", got, want)
	}
	// 送信行は kindIn として echo され、現セッションの history にも積まれる。
	if !hasInfo(m, "5 3") {
		t.Error("expected replayed line echoed in chat")
	}
	if len(m.history) == 0 {
		t.Error("replayed lines should be recorded in session history")
	}
}

// RecordInput フックが注入されていれば、送信した各行で呼ばれる (永続化経路)。
func TestSubmitLinesCallsRecordInput(t *testing.T) {
	var recorded []string
	var stdin bytes.Buffer
	spawn := func() (*runner.ChatHandle, error) {
		return &runner.ChatHandle{
			Stdin:  nopWriteCloser{&stdin},
			Stdout: io.NopCloser(strings.NewReader("")),
			Stderr: io.NopCloser(strings.NewReader("")),
		}, nil
	}
	m := &chatModel{spawn: spawn, header: ChatHeader{
		RecordInput: func(line string) { recorded = append(recorded, line) },
	}}

	var cmds []tea.Cmd
	m.submitLines([]string{"a", "b"}, &cmds)

	if want := []string{"a", "b"}; !equalStrings(recorded, want) {
		t.Errorf("RecordInput got %v, want %v", recorded, want)
	}
}

func equalStrings(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}
