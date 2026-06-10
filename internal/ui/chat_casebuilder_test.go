package ui

import (
	"os"
	"path/filepath"
	"testing"

	tea "github.com/charmbracelet/bubbletea"
)

func TestParseCommand(t *testing.T) {
	cases := []struct {
		in   string
		name string
		arg  string
	}{
		{"case", "case", ""},
		{"c", "case", ""},
		{"w", "w", ""},
		{"w edge", "w", "edge"},
		{"write foo", "w", "foo"},
		{"set verify", "set", "verify"},
		{"set noverify", "set", "noverify"},
		{"q", "q", ""},
		{"  case  ", "case", ""},
		{"", "", ""},
		{"bogus", "unknown", "bogus"}, // 未知コマンド名は arg に入れて E492 表示に使う
	}
	for _, c := range cases {
		got := parseCommand(c.in)
		if got.name != c.name || got.arg != c.arg {
			t.Errorf("parseCommand(%q) = {%q,%q}, want {%q,%q}", c.in, got.name, got.arg, c.name, c.arg)
		}
	}
}

func TestTokensMatch(t *testing.T) {
	cases := []struct {
		exp, act string
		tol      float64
		want     bool
	}{
		{"9", "9", 0, true},
		{"9", "8", 0, false},
		{"1 2 3", "1 2 3", 0, true},
		{"1 2", "1 2 3", 0, false},       // トークン数違い
		{"1.0000001", "1.0", 1e-6, true}, // 許容誤差内
		{"1.1", "1.0", 1e-6, false},      // 許容誤差外
		{"abc", "abc", 0, true},          // 非数値の文字列一致
		{"abc", "abd", 1e-6, false},      // 非数値の不一致
		{"hello world", "hello world", 0, true},
	}
	for _, c := range cases {
		if got := tokensMatch(c.exp, c.act, c.tol); got != c.want {
			t.Errorf("tokensMatch(%q,%q,%g) = %v, want %v", c.exp, c.act, c.tol, got, c.want)
		}
	}
}

// insert モードで Esc を押すと command モード (`:` 行) に入る。
func TestEscEntersCommandMode(t *testing.T) {
	m := initialChatModel(ChatHeader{}, fakeSpawn())
	m.Update(tea.WindowSizeMsg{Width: 80, Height: 24})
	if _, _ = m.Update(tea.KeyMsg{Type: tea.KeyEsc}); m.mode != modeCommand {
		t.Errorf("Esc should enter command mode, got mode=%d", m.mode)
	}
}

// :case で現セッションの送信入力を前埋めしたビルダーが開く。
func TestCaseCommandOpensBuilderWithPrefill(t *testing.T) {
	m := initialChatModel(ChatHeader{}, fakeSpawn())
	m.Update(tea.WindowSizeMsg{Width: 80, Height: 24})
	m.sessionInputs = []string{"5 3", "1 2 3 4 5"}
	m.execCommand(parseCommand("case"))
	if m.mode != modeBuilder || m.builder == nil {
		t.Fatalf("`:case` should open builder; mode=%d builder=%v", m.mode, m.builder)
	}
	if got := m.builder.in.Value(); got != "5 3\n1 2 3 4 5" {
		t.Errorf("builder input prefill = %q, want session inputs joined", got)
	}
}

// :w で builder の内容が tests-extra に保存され、builder が閉じてライブ検証が有効になる。
func TestWriteSavesAndEnablesVerify(t *testing.T) {
	taskDir := t.TempDir()
	m := initialChatModel(ChatHeader{TaskDir: taskDir}, fakeSpawn())
	m.Update(tea.WindowSizeMsg{Width: 80, Height: 24})
	m.execCommand(parseCommand("case"))
	m.builder.in.SetValue("7")
	m.builder.out.SetValue("14")
	m.execCommand(parseCommand("w"))

	if m.builder != nil {
		t.Error("builder should close after :w")
	}
	if m.verify == nil {
		t.Error(":w with non-empty expected should enable live verify")
	}
	in, err := os.ReadFile(filepath.Join(taskDir, "tests-extra", "01.in"))
	if err != nil || string(in) != "7\n" {
		t.Errorf("saved 01.in = %q err=%v", in, err)
	}
}

// 保存先 (TaskDir) が無いと :w はエラー行を出し、builder は開いたまま。
func TestWriteWithoutTaskDirErrors(t *testing.T) {
	m := initialChatModel(ChatHeader{}, fakeSpawn()) // TaskDir 空
	m.Update(tea.WindowSizeMsg{Width: 80, Height: 24})
	m.execCommand(parseCommand("case"))
	m.builder.out.SetValue("9")
	m.execCommand(parseCommand("w"))
	if m.builder == nil {
		t.Error("builder should stay open when save fails")
	}
	if !hasInfo(m, "保存できません") {
		t.Errorf("expected save-failure message; msgs=%v", m.msgs)
	}
}

// 未知コマンドはエラー行を出して insert へ戻る (副作用なし)。
func TestUnknownCommand(t *testing.T) {
	m := initialChatModel(ChatHeader{}, fakeSpawn())
	m.Update(tea.WindowSizeMsg{Width: 80, Height: 24})
	m.execCommand(parseCommand("bogus"))
	if m.mode != modeInsert {
		t.Error("unknown command should return to insert mode")
	}
	if !hasInfo(m, "E492") {
		t.Errorf("expected E492 message; msgs=%v", m.msgs)
	}
}

// ライブ検証: stdout 行を expected と順に突き合わせ、判定を行に付ける。
func TestApplyVerify(t *testing.T) {
	m := initialChatModel(ChatHeader{}, fakeSpawn())
	m.enableVerify([]string{"9", "8"})

	l1 := chatLine{kind: kindOut, text: "9"}
	m.applyVerify(&l1)
	if l1.verdict != verdictOK {
		t.Errorf("first line should match; verdict=%q", l1.verdict)
	}
	l2 := chatLine{kind: kindOut, text: "7"}
	m.applyVerify(&l2)
	if l2.verdict != verdictNG || l2.verdictExp != "8" {
		t.Errorf("second line should mismatch with expected 8; verdict=%q exp=%q", l2.verdict, l2.verdictExp)
	}
	// expected を使い切ったら以降は判定なし。
	l3 := chatLine{kind: kindOut, text: "5"}
	m.applyVerify(&l3)
	if l3.verdict != "" {
		t.Errorf("after expected exhausted, no verdict; got %q", l3.verdict)
	}
}

// :set verify は直近の expected が無いと有効化しない。
func TestSetVerifyNeedsExpected(t *testing.T) {
	m := initialChatModel(ChatHeader{}, fakeSpawn())
	m.applySet("verify")
	if m.verify != nil {
		t.Error(":set verify without prior expected should not enable verify")
	}
	if !hasInfo(m, "期待出力がありません") {
		t.Errorf("expected guidance message; msgs=%v", m.msgs)
	}
}
