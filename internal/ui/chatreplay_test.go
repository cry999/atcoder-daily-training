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

// 子セッションを複数またいでも :replay は **直前の (child) セッション** の入力だけを流す。
// 起動を通した手入力すべてを累積して流してはいけない (要件 039 / バグ報告)。
func TestReplayScopedToPreviousSession(t *testing.T) {
	var stdin bytes.Buffer
	spawn := func() (*runner.ChatHandle, error) {
		return &runner.ChatHandle{
			Stdin:  nopWriteCloser{&stdin},
			Stdout: io.NopCloser(strings.NewReader("")),
			Stderr: io.NopCloser(strings.NewReader("")),
		}, nil
	}
	m := &chatModel{spawn: spawn} // 遅延起動
	var cmds []tea.Cmd

	// セッション 1: A, B を手入力
	m.submitLines([]string{"A", "B"}, &cmds, true)
	m.restart() // 子セッション境界 (watch reload / Ctrl+D リセット相当)

	// セッション 2: C, D を手入力
	m.submitLines([]string{"C", "D"}, &cmds, true)
	m.restart()

	// :replay は直前のセッション (= セッション 2 の C, D) だけを流すべき。
	// バグ時は A, B, C, D 全部が流れる。
	stdin.Reset()
	m.execReplay()
	if got, want := stdin.String(), "C\nD\n"; got != want {
		t.Errorf("replay stdin = %q, want %q (only the previous session, not all run inputs)", got, want)
	}
}

// 今回分も前回分も無ければ :replay は info 行のみで子を起動しない。
func TestExecReplayNoInputs(t *testing.T) {
	spawnCalls := 0
	spawn := func() (*runner.ChatHandle, error) { spawnCalls++; return fakeHandle(), nil }
	m := &chatModel{spawn: spawn, header: ChatHeader{}} // sessionInputs/prevSessionInputs/PrevInputs すべて nil

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

// 現セッションで入力を送っていれば、:replay は (PrevInputs ではなく) その現セッション分を再生する。
// コード修正後に同じ入力を流し直す主用途。
func TestExecReplayPrefersCurrentSessionInputs(t *testing.T) {
	var stdin bytes.Buffer
	spawn := func() (*runner.ChatHandle, error) {
		return &runner.ChatHandle{
			Stdin:  nopWriteCloser{&stdin},
			Stdout: io.NopCloser(strings.NewReader("")),
			Stderr: io.NopCloser(strings.NewReader("")),
		}, nil
	}
	// 現セッションの入力 (sessionInputs) があり、前回起動入力 (PrevInputs) とは別物。
	m := &chatModel{spawn: spawn,
		sessionInputs: []string{"now 1", "now 2"},
		header:        ChatHeader{PrevInputs: []string{"old 1"}},
	}

	m.execReplay()

	if got, want := stdin.String(), "now 1\nnow 2\n"; got != want {
		t.Errorf("replay should re-send the current session inputs: stdin = %q, want %q", got, want)
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
	m.submitLines([]string{"a", "b"}, &cmds, true)

	if want := []string{"a", "b"}; !equalStrings(recorded, want) {
		t.Errorf("RecordInput got %v, want %v", recorded, want)
	}
}

// :replay の再送は RecordInput を呼ばない (record=false) — 再生行を永続化すると
// 次回起動の前回入力 (PrevInputs) が再生値で膨らむため (要件 039)。
func TestReplayDoesNotRecord(t *testing.T) {
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
		PrevInputs:  []string{"4", "1 1"},
		RecordInput: func(line string) { recorded = append(recorded, line) },
	}}

	m.execReplay() // 前回フォールバックを再送

	if len(recorded) != 0 {
		t.Errorf("replay must not persist replayed lines, recorded %v", recorded)
	}
	if len(m.sessionInputs) != 0 {
		t.Errorf("replay must not add to sessionInputs (replay source), got %v", m.sessionInputs)
	}
}

// バグ再現: 起動直後に :replay (前回フォールバック) してから手入力すると、次の :replay の
// 対象 (sessionInputs) は手入力した行だけになるべき。フォールバック/再生で流れた過去の
// テストケース値が現セッションに積もって次回の再生に巻き込まれてはいけない (要件 039)。
func TestReplayDoesNotAccumulatePreviousValues(t *testing.T) {
	var stdin bytes.Buffer
	spawn := func() (*runner.ChatHandle, error) {
		return &runner.ChatHandle{
			Stdin:  nopWriteCloser{&stdin},
			Stdout: io.NopCloser(strings.NewReader("")),
			Stderr: io.NopCloser(strings.NewReader("")),
		}, nil
	}
	// 今セッションは未入力。前回セッションにサンプル/テストケース値がある状態 (遅延起動)。
	m := &chatModel{spawn: spawn, header: ChatHeader{PrevInputs: []string{"4", "1 1", "2 2"}}}

	// 1) 起動直後の :replay → 前回フォールバックでサンプル値を流す (が sessionInputs には残さない)
	m.execReplay()
	if len(m.sessionInputs) != 0 {
		t.Fatalf("fallback replay must not enter sessionInputs, got %v", m.sessionInputs)
	}

	// 2) 今セッションで手入力 → :replay 対象は手入力分だけ。前回フォールバックの 3 行は混ざらない。
	var cmds []tea.Cmd
	m.submitLines([]string{"6"}, &cmds, true)
	if want := []string{"6"}; !equalStrings(m.replayLines(), want) {
		t.Errorf("replayLines = %v, want %v — previous-session/test-case values must not leak into the next replay", m.replayLines(), want)
	}
}

// beginNewSession は直前セッションの (手入力) 入力を prevSessionInputs に退避し、空セッションでは
// 上書きしない。replayLines は現セッション→直前セッション→前回起動 の順で 1 セッション分を返す。
func TestSessionRotationAndReplayLines(t *testing.T) {
	m := &chatModel{sessionInputs: []string{"A", "B"}, header: ChatHeader{PrevInputs: []string{"old"}}}
	m.beginNewSession() // prev=[A,B], session=[]
	if want := []string{"A", "B"}; !equalStrings(m.prevSessionInputs, want) {
		t.Fatalf("prevSessionInputs = %v, want %v", m.prevSessionInputs, want)
	}
	// 現セッション空 → 直前セッションを返す (前回起動 PrevInputs より優先)
	if want := []string{"A", "B"}; !equalStrings(m.replayLines(), want) {
		t.Errorf("replayLines (empty current) = %v, want %v", m.replayLines(), want)
	}
	// 空セッションの回転は prevSessionInputs を上書きしない
	m.beginNewSession()
	if want := []string{"A", "B"}; !equalStrings(m.prevSessionInputs, want) {
		t.Errorf("empty rotation overwrote prevSessionInputs: got %v, want %v", m.prevSessionInputs, want)
	}
	// 次のセッションで入力 → 現セッションが優先
	m.sessionInputs = []string{"C", "D"}
	if want := []string{"C", "D"}; !equalStrings(m.replayLines(), want) {
		t.Errorf("replayLines (current present) = %v, want %v", m.replayLines(), want)
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
