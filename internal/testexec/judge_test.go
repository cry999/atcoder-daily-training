package testexec

import (
	"testing"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

func TestContainsDebugLine(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want bool
	}{
		{"empty", "", false},
		{"plain", "10\n20\n", false},
		{"debug line", "[DEBUG] x=1\n10\n", true},
		{"debug mid (line prefix)", "10\n[DEBUG] done\n", true},
		{"debug not at line head", "result [DEBUG]\n", false},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := containsDebugLine(c.in); got != c.want {
				t.Errorf("containsDebugLine(%q) = %v, want %v", c.in, got, c.want)
			}
		})
	}
}

func TestJudgeDebugSeen(t *testing.T) {
	cases := []struct {
		name   string
		stdout string
		stderr string
		want   bool
	}{
		{"clean", "10\n", "", false},
		{"debug on stdout", "[DEBUG] n=5\n10\n", "", true},
		{"debug on stderr (stdout clean)", "10\n", "[DEBUG] n=5\n", true},
		{"no debug, noisy stderr", "10\n", "some warning\n", false},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			pr := &runner.ProcessResult{
				Status:   runner.Exited,
				ExitCode: 0,
				Stdout:   c.stdout,
				Stderr:   c.stderr,
				Elapsed:  time.Millisecond,
			}
			cr := judge("01", "5\n", "10\n", pr, false, DefaultTolerance)
			if cr.DebugSeen != c.want {
				t.Errorf("DebugSeen = %v, want %v", cr.DebugSeen, c.want)
			}
		})
	}
}
