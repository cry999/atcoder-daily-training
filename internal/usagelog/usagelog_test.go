package usagelog

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestFlagsFromArgs(t *testing.T) {
	cases := []struct {
		args []string
		want []string
	}{
		{[]string{"--task", "d", "e.py"}, []string{"task"}},                // 値・位置引数は捨てる
		{[]string{"abc457", "--debug"}, []string{"debug"}},                 // 位置引数は捨てる
		{[]string{"--last=3d"}, []string{"last"}},                          // =value は手前まで
		{[]string{"-c", "1,2", "-j", "4"}, []string{"c", "j"}},             // 短縮フラグ
		{[]string{"--in", "-"}, []string{"in"}},                            // 単独 "-" は空 → 捨てる
		{[]string{"--refresh", "--refresh"}, []string{"refresh"}},          // 重複除去
		{[]string{"--no-open", "--submit"}, []string{"no-open", "submit"}}, // ハイフン入りフラグ名
		{nil, nil},
	}
	for _, c := range cases {
		got := FlagsFromArgs(c.args)
		if strings.Join(got, "|") != strings.Join(c.want, "|") {
			t.Errorf("FlagsFromArgs(%v) = %v, want %v", c.args, got, c.want)
		}
	}
}

func TestRecordAndAggregateRoundtrip(t *testing.T) {
	dir := t.TempDir()
	t.Setenv("XDG_DATA_HOME", dir)
	t.Setenv(DisableEnv, "") // 念のため有効化

	base := time.Date(2026, 6, 12, 14, 0, 0, 0, time.UTC)
	evs := []Event{
		{TS: base, Cmd: "test", Flags: []string{"task"}, DurMs: 1000, Exit: 0},
		{TS: base.Add(time.Minute), Cmd: "test", Flags: []string{"task", "refresh"}, DurMs: 3000, Exit: 1},
		{TS: base.Add(2 * time.Minute), Cmd: "start", Flags: nil, DurMs: 5000, Exit: 0},
	}
	for _, ev := range evs {
		if err := Record(ev); err != nil {
			t.Fatalf("Record: %v", err)
		}
	}

	// ファイルが期待パスにできている。
	if _, err := os.Stat(Path()); err != nil {
		t.Fatalf("log file not created at %s: %v", Path(), err)
	}

	f, err := os.Open(Path())
	if err != nil {
		t.Fatal(err)
	}
	defer f.Close()
	stats, err := Aggregate(f)
	if err != nil {
		t.Fatalf("Aggregate: %v", err)
	}
	if len(stats) != 2 {
		t.Fatalf("want 2 commands, got %d (%+v)", len(stats), stats)
	}
	// count 降順: test(2) が先。
	if stats[0].Cmd != "test" || stats[0].Count != 2 {
		t.Errorf("stats[0] = %+v, want test count 2", stats[0])
	}
	if stats[0].TotalMs != 4000 || stats[0].AvgMs() != 2000 {
		t.Errorf("test total/avg = %d/%d, want 4000/2000", stats[0].TotalMs, stats[0].AvgMs())
	}
	if !stats[0].Last.Equal(base.Add(time.Minute)) {
		t.Errorf("test last = %v, want %v", stats[0].Last, base.Add(time.Minute))
	}
	if stats[0].Flags["task"] != 2 || stats[0].Flags["refresh"] != 1 {
		t.Errorf("test flags = %v, want task:2 refresh:1", stats[0].Flags)
	}
	if stats[1].Cmd != "start" || stats[1].Count != 1 {
		t.Errorf("stats[1] = %+v, want start count 1", stats[1])
	}
}

func TestRecordDisabled(t *testing.T) {
	dir := t.TempDir()
	t.Setenv("XDG_DATA_HOME", dir)
	t.Setenv(DisableEnv, "1")

	if !Disabled() {
		t.Fatal("Disabled() should be true when ATCODER_NO_USAGE is set")
	}
	if err := Record(Event{Cmd: "test"}); err != nil {
		t.Fatalf("Record while disabled should be a no-op nil, got %v", err)
	}
	if _, err := os.Stat(Path()); !os.IsNotExist(err) {
		t.Fatalf("disabled Record must not create the log file (err=%v)", err)
	}
}

func TestAggregateSkipsCorruptLines(t *testing.T) {
	content := strings.Join([]string{
		`{"ts":"2026-06-12T14:00:00Z","cmd":"test","dur_ms":100,"exit":0}`,
		`not json at all`,
		``,                      // 空行
		`{"cmd":"","dur_ms":1}`, // cmd 空 → 無視
		`{"ts":"2026-06-12T14:01:00Z","cmd":"test","dur_ms":200,"exit":0}`,
	}, "\n")
	stats, err := Aggregate(strings.NewReader(content))
	if err != nil {
		t.Fatalf("Aggregate: %v", err)
	}
	if len(stats) != 1 || stats[0].Cmd != "test" || stats[0].Count != 2 {
		t.Fatalf("want test count 2 (corrupt lines skipped), got %+v", stats)
	}
	if stats[0].TotalMs != 300 {
		t.Errorf("total = %d, want 300", stats[0].TotalMs)
	}
}

func TestPathUnderDataHome(t *testing.T) {
	dir := t.TempDir()
	t.Setenv("XDG_DATA_HOME", dir)
	want := filepath.Join(dir, AppName, "usage", "events.jsonl")
	if Path() != want {
		t.Errorf("Path() = %s, want %s", Path(), want)
	}
}
