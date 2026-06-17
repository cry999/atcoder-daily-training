package ui

import (
	"io"
	"strings"
	"testing"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/chatlog"
	"github.com/cry999/atcoder-daily-training/internal/runner"
)

func discardSpawn() Spawner {
	return func() (*runner.ChatHandle, error) {
		return &runner.ChatHandle{
			Stdin:  nopWriteCloser{io.Discard},
			Stdout: io.NopCloser(strings.NewReader("")),
			Stderr: io.NopCloser(strings.NewReader("")),
		}, nil
	}
}

// 配線どおり (composition root の sid 生成 + LoadLastSession 先読み + RecordInput 注入) に
// 2 回の chat 起動を再現し、2 回目で前回入力がリプレイ対象になることを確認する。
func TestReplayAcrossRuns(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", t.TempDir())
	t.Setenv(chatlog.DisableEnv, "")
	const contest, task = "abc199", "abc199_d"

	// --- 1 回目の起動: 入力を 2 行送る ---
	sid1 := chatlog.NewSessionID()
	prev1, _ := chatlog.LoadLastSession(contest, task)
	if len(prev1) != 0 {
		t.Fatalf("run 1 PrevInputs should be empty, got %v", prev1)
	}
	m1 := &chatModel{spawn: discardSpawn(), header: ChatHeader{
		PrevInputs:  prev1,
		RecordInput: func(line string) { _ = chatlog.Record(contest, task, sid1, line) },
	}}
	var cmds []tea.Cmd
	m1.submitLines([]string{"3 3", "1 2"}, &cmds, true)

	// --- 2 回目の起動: 別 session。前回入力を先読みできるはず ---
	_ = chatlog.NewSessionID()
	prev2, _ := chatlog.LoadLastSession(contest, task)
	if want := []string{"3 3", "1 2"}; !equalStrings(prev2, want) {
		t.Fatalf("run 2 PrevInputs = %v, want %v (cross-run replay broken)", prev2, want)
	}
}
