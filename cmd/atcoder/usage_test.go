package main

import (
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/cry999/atcoder-daily-training/internal/usagelog"
)

// captureStdout は fn 実行中の os.Stdout を文字列として捕捉する。
func captureStdout(t *testing.T, fn func()) string {
	t.Helper()
	old := os.Stdout
	r, w, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	os.Stdout = w
	fn()
	w.Close()
	os.Stdout = old
	out, _ := io.ReadAll(r)
	return string(out)
}

func writeEvents(t *testing.T, lines ...string) {
	t.Helper()
	dir := usagelog.Dir()
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "events.jsonl"), []byte(strings.Join(lines, "\n")+"\n"), 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestCmdUsageEmpty(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", t.TempDir())
	out := captureStdout(t, func() {
		code, err := cmdUsage(nil)
		if code != 0 || err != nil {
			t.Fatalf("cmdUsage empty = (%d, %v), want (0, nil)", code, err)
		}
	})
	if !strings.Contains(out, "まだ利用記録がありません") {
		t.Errorf("empty usage should print the no-records message, got %q", out)
	}
}

func TestCmdUsageTable(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", t.TempDir())
	writeEvents(t,
		`{"ts":"2026-06-12T14:00:00Z","cmd":"test","flags":["task"],"dur_ms":1000,"exit":0}`,
		`{"ts":"2026-06-12T14:01:00Z","cmd":"test","flags":["task","refresh"],"dur_ms":3000,"exit":1}`,
		`{"ts":"2026-06-12T14:02:00Z","cmd":"start","dur_ms":5000,"exit":0}`,
	)
	out := captureStdout(t, func() {
		code, err := cmdUsage(nil)
		if code != 0 || err != nil {
			t.Fatalf("cmdUsage = (%d, %v), want (0, nil)", code, err)
		}
	})
	if !strings.Contains(out, "test") || !strings.Contains(out, "start") {
		t.Errorf("table should list test and start: %q", out)
	}
	if !strings.Contains(out, "合計 3 回 / 2 コマンド") {
		t.Errorf("table should show totals: %q", out)
	}
	// test(2) は count 降順で start(1) より前。
	if strings.Index(out, "test") > strings.Index(out, "start") {
		t.Errorf("test (count 2) should appear before start (count 1): %q", out)
	}
}

func TestCmdUsageFlagsBreakdown(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", t.TempDir())
	writeEvents(t,
		`{"ts":"2026-06-12T14:00:00Z","cmd":"test","flags":["task"],"dur_ms":1000,"exit":0}`,
		`{"ts":"2026-06-12T14:01:00Z","cmd":"test","flags":["task","refresh"],"dur_ms":3000,"exit":0}`,
	)
	out := captureStdout(t, func() {
		if code, err := cmdUsage([]string{"--flags"}); code != 0 || err != nil {
			t.Fatalf("cmdUsage --flags = (%d, %v)", code, err)
		}
	})
	if !strings.Contains(out, "task") || !strings.Contains(out, "refresh") {
		t.Errorf("--flags should show per-flag breakdown: %q", out)
	}
}

func TestCmdUsageBadFlag(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", t.TempDir())
	code, err := cmdUsage([]string{"--nope"})
	if code != 2 || err != nil {
		t.Fatalf("unknown flag should exit 2 with nil err, got (%d, %v)", code, err)
	}
}
