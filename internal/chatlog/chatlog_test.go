package chatlog

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

// Record で 2 セッション分を追記し、LoadLastSession が直近 session の入力だけを
// 送信順 (空行込み) で返すことを確認する。
func TestRecordAndLoadLastSession(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", t.TempDir())
	t.Setenv(DisableEnv, "") // 無効化しない

	const contest, task = "abc457", "abc457_d"
	// 前回セッション s1
	mustRecord(t, contest, task, "s1", "old 1")
	mustRecord(t, contest, task, "s1", "old 2")
	// 今回セッション s2 (空行を含む)
	mustRecord(t, contest, task, "s2", "5 3")
	mustRecord(t, contest, task, "s2", "")
	mustRecord(t, contest, task, "s2", "go")

	got, err := LoadLastSession(contest, task)
	if err != nil {
		t.Fatalf("LoadLastSession: %v", err)
	}
	want := []string{"5 3", "", "go"}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("LoadLastSession = %#v, want %#v", got, want)
	}
}

// 別問題の履歴は混ざらない (キーは contest+task ごと)。
func TestLoadLastSessionPerProblem(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", t.TempDir())
	t.Setenv(DisableEnv, "")

	mustRecord(t, "abc457", "abc457_d", "s1", "for-d")
	mustRecord(t, "abc457", "abc457_e", "s1", "for-e")

	got, _ := LoadLastSession("abc457", "abc457_d")
	if want := []string{"for-d"}; !reflect.DeepEqual(got, want) {
		t.Errorf("per-problem isolation failed: got %#v, want %#v", got, want)
	}
}

// 無効化時 (ATCODER_NO_CHAT_HISTORY) は記録せず、ファイルも作らない。
func TestRecordDisabled(t *testing.T) {
	dir := t.TempDir()
	t.Setenv("XDG_DATA_HOME", dir)
	t.Setenv(DisableEnv, "1")

	if err := Record("abc457", "abc457_d", "s1", "x"); err != nil {
		t.Fatalf("Record (disabled) should be no-op, got err %v", err)
	}
	if _, err := os.Stat(Path("abc457", "abc457_d")); !os.IsNotExist(err) {
		t.Errorf("disabled Record must not create the file (stat err = %v)", err)
	}
	got, _ := LoadLastSession("abc457", "abc457_d")
	if got != nil {
		t.Errorf("LoadLastSession with no file = %#v, want nil", got)
	}
}

// 空 contest / task は記録・読込とも no-op (キーにできない)。
func TestEmptyKeyNoOp(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", t.TempDir())
	t.Setenv(DisableEnv, "")

	if err := Record("", "task", "s1", "x"); err != nil {
		t.Errorf("Record with empty contest: %v", err)
	}
	if err := Record("contest", "", "s1", "x"); err != nil {
		t.Errorf("Record with empty task: %v", err)
	}
	if got, _ := LoadLastSession("", "task"); got != nil {
		t.Errorf("LoadLastSession empty contest = %#v, want nil", got)
	}
}

// Path は XDG_DATA_HOME 配下に組み立てられる。
func TestPathUnderDataHome(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", "/tmp/xyz")
	got := Path("abc457", "abc457_d")
	want := filepath.Join("/tmp/xyz", AppName, "chat-history", "abc457", "abc457_d.jsonl")
	if got != want {
		t.Errorf("Path = %q, want %q", got, want)
	}
}

// 壊れた JSONL 行はスキップして読み進める (best-effort)。
func TestLoadSkipsMalformedLines(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", t.TempDir())
	t.Setenv(DisableEnv, "")

	path := Path("abc457", "abc457_d")
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	content := "not json\n" +
		`{"ts":"2026-06-17T10:00:00Z","session":"s1","text":"good"}` + "\n" +
		"{ broken\n"
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	got, err := LoadLastSession("abc457", "abc457_d")
	if err != nil {
		t.Fatalf("LoadLastSession: %v", err)
	}
	if want := []string{"good"}; !reflect.DeepEqual(got, want) {
		t.Errorf("malformed-skipping load = %#v, want %#v", got, want)
	}
}

func mustRecord(t *testing.T, contest, task, session, text string) {
	t.Helper()
	if err := Record(contest, task, session, text); err != nil {
		t.Fatalf("Record(%q,%q,%q,%q): %v", contest, task, session, text, err)
	}
}
