package ui

import (
	"bytes"
	"io"
	"path/filepath"
	"strings"
	"testing"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

// :test / :t は parseCommand で name="test" になり、引数 (ケース ID) は arg に載る (要件 045)。
func TestParseCommandTest(t *testing.T) {
	cases := []struct {
		in       string
		wantName string
		wantArg  string
	}{
		{"test 01", "test", "01"},
		{"test", "test", ""},
		{"t 1", "test", "1"},
		{"t x01", "test", "x01"},
	}
	for _, c := range cases {
		got := parseCommand(c.in)
		if got.name != c.wantName || got.arg != c.wantArg {
			t.Errorf("parseCommand(%q) = {name:%q arg:%q}, want {name:%q arg:%q}", c.in, got.name, got.arg, c.wantName, c.wantArg)
		}
	}
}

// spawnToBuf は stdin を buf に集める fake spawner と呼び出し回数を返す。
func spawnToBuf(buf *bytes.Buffer, calls *int) Spawner {
	return func() (*runner.ChatHandle, error) {
		*calls++
		return &runner.ChatHandle{
			Stdin:  nopWriteCloser{buf},
			Stdout: io.NopCloser(strings.NewReader("")),
			Stderr: io.NopCloser(strings.NewReader("")),
		}, nil
	}
}

// :test <case> は子をリスタートしてケースの .in を順送し、.out でライブ検証を有効化する。
func TestExecTestRunsCase(t *testing.T) {
	taskDir := t.TempDir()
	writeCase(t, filepath.Join(taskDir, "tests"), "01", "5 3\n1 2 3\n", "6\n")

	var stdin bytes.Buffer
	calls := 0
	m := &chatModel{spawn: spawnToBuf(&stdin, &calls), header: ChatHeader{TaskDir: taskDir}}

	m.execTest("01")

	if calls != 1 {
		t.Fatalf(":test should restart (spawn) exactly once, got %d", calls)
	}
	if !m.running {
		t.Error("child should be running after :test")
	}
	if got, want := stdin.String(), "5 3\n1 2 3\n"; got != want {
		t.Errorf(":test stdin = %q, want %q", got, want)
	}
	// expected があるのでライブ検証が有効化され、:set verify の対象も更新される。
	if m.verify == nil {
		t.Error(":test with expected should enable live verify")
	}
	if !equalStrings(m.lastExpected, []string{"6"}) {
		t.Errorf("lastExpected = %v, want [6]", m.lastExpected)
	}
	if !hasInfo(m, "case 01 を実行") {
		t.Error("expected the run info line")
	}
}

// 短縮形 :t と bare 数字 (1→01) でも公式ケースを実行できる。
func TestExecTestNumericAlias(t *testing.T) {
	taskDir := t.TempDir()
	writeCase(t, filepath.Join(taskDir, "tests"), "01", "hi\n", "ok\n")

	var stdin bytes.Buffer
	calls := 0
	m := &chatModel{spawn: spawnToBuf(&stdin, &calls), header: ChatHeader{TaskDir: taskDir}}

	m.execTest("1") // :t 1

	if got, want := stdin.String(), "hi\n"; got != want {
		t.Errorf("stdin = %q, want %q", got, want)
	}
}

// 追加ケース (x プレフィックス) は tests-extra から実行する。
func TestExecTestExtraCase(t *testing.T) {
	taskDir := t.TempDir()
	writeCase(t, filepath.Join(taskDir, "tests-extra"), "01", "9 9\n", "18\n")

	var stdin bytes.Buffer
	calls := 0
	m := &chatModel{spawn: spawnToBuf(&stdin, &calls), header: ChatHeader{TaskDir: taskDir}}

	m.execTest("x01")

	if got, want := stdin.String(), "9 9\n"; got != want {
		t.Errorf("extra case stdin = %q, want %q", got, want)
	}
	if !hasInfo(m, "case x01 を実行") {
		t.Error("expected the extra-case run info line")
	}
}

// 順送は record=false: :test の入力は sessionInputs / chatlog に積まない (:replay を膨らませない)。
func TestExecTestDoesNotRecord(t *testing.T) {
	taskDir := t.TempDir()
	writeCase(t, filepath.Join(taskDir, "tests"), "01", "a\nb\n", "x\n")

	var stdin bytes.Buffer
	calls := 0
	var recorded []string
	m := &chatModel{spawn: spawnToBuf(&stdin, &calls), header: ChatHeader{
		TaskDir:     taskDir,
		RecordInput: func(line string) { recorded = append(recorded, line) },
	}}

	m.execTest("01")

	if len(recorded) != 0 {
		t.Errorf(":test must not persist case input, recorded %v", recorded)
	}
	if len(m.sessionInputs) != 0 {
		t.Errorf(":test must not add to sessionInputs (replay source), got %v", m.sessionInputs)
	}
}

// 引数省略 :test は利用可能なケース一覧を表示し、子は起動しない。
func TestExecTestListsCases(t *testing.T) {
	taskDir := t.TempDir()
	writeCase(t, filepath.Join(taskDir, "tests"), "01", "a", "b")
	writeCase(t, filepath.Join(taskDir, "tests-extra"), "01", "c", "d")

	var stdin bytes.Buffer
	calls := 0
	m := &chatModel{spawn: spawnToBuf(&stdin, &calls), header: ChatHeader{TaskDir: taskDir}}

	m.execTest("")

	if calls != 0 {
		t.Errorf("listing must not spawn, got %d", calls)
	}
	if !hasInfo(m, "利用可能なケース: 01 x01") {
		t.Error("expected the case-list info line")
	}
}

// ケースが 1 つも無ければ取得方法を案内する。
func TestExecTestListsEmpty(t *testing.T) {
	var stdin bytes.Buffer
	calls := 0
	m := &chatModel{spawn: spawnToBuf(&stdin, &calls), header: ChatHeader{TaskDir: t.TempDir()}}

	m.execTest("")

	if calls != 0 {
		t.Errorf("empty listing must not spawn, got %d", calls)
	}
	if !hasInfo(m, "利用可能なサンプルがありません") {
		t.Error("expected the empty-samples info line")
	}
}

// 該当しないケース ID は子を起動せず info 行のみ。
func TestExecTestUnknownCase(t *testing.T) {
	taskDir := t.TempDir()
	writeCase(t, filepath.Join(taskDir, "tests"), "01", "a", "b")

	var stdin bytes.Buffer
	calls := 0
	m := &chatModel{spawn: spawnToBuf(&stdin, &calls), header: ChatHeader{TaskDir: taskDir}}

	m.execTest("99")

	if calls != 0 {
		t.Errorf("unknown case must not spawn, got %d", calls)
	}
	if m.running {
		t.Error("unknown case: child must not be running")
	}
	if !hasInfo(m, "が見つかりません") {
		t.Error("expected the not-found info line")
	}
}

// TaskDir 未注入なら :test は場所不明として実行も一覧もしない。
func TestExecTestNoTaskDir(t *testing.T) {
	var stdin bytes.Buffer
	calls := 0
	m := &chatModel{spawn: spawnToBuf(&stdin, &calls), header: ChatHeader{}} // TaskDir 空

	m.execTest("01")

	if calls != 0 {
		t.Errorf("no TaskDir must not spawn, got %d", calls)
	}
	if !hasInfo(m, "ケースの場所が不明") {
		t.Error("expected the unknown-location info line")
	}
}

// .out が空のケースは入力を流すがライブ検証は付けない。
func TestExecTestEmptyExpected(t *testing.T) {
	taskDir := t.TempDir()
	writeCase(t, filepath.Join(taskDir, "tests"), "01", "5\n", "") // 空 expected

	var stdin bytes.Buffer
	calls := 0
	m := &chatModel{spawn: spawnToBuf(&stdin, &calls), header: ChatHeader{TaskDir: taskDir}}

	m.execTest("01")

	if got, want := stdin.String(), "5\n"; got != want {
		t.Errorf("stdin = %q, want %q", got, want)
	}
	if m.verify != nil {
		t.Error("empty expected should not enable live verify")
	}
}
