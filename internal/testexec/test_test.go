package testexec

import (
	"context"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cachepath"
	"github.com/cry999/atcoder-daily-training/internal/runner"
)

// fixedLayout は SolutionPath を固定パスに解決する最小 Layout (テスト用)。
type fixedLayout struct{ path string }

func (l fixedLayout) Name() string                                      { return "fixed" }
func (l fixedLayout) SolutionPath(contest, task string) (string, error) { return l.path, nil }

// recordingExecutor は Run に渡された source パスを記録し、PASS する固定出力を返す。
type recordingExecutor struct {
	got    string
	stdout string
}

func (e *recordingExecutor) Run(ctx context.Context, source string, input []byte, timeout time.Duration, extraEnv []string) (*runner.ProcessResult, error) {
	e.got = source
	return &runner.ProcessResult{Status: runner.Exited, ExitCode: 0, Stdout: e.stdout}, nil
}

// TestRunSolutionPathOverride は Options.SolutionPathOverride (要件 049) を検証する:
// 非空ならその値が実行対象になり、空なら Layout.SolutionPath の解決結果が使われる。
func TestRunSolutionPathOverride(t *testing.T) {
	// キャッシュ (tests/ + meta.toml) を一時 XDG_CACHE_HOME に用意し、fetch を回避する。
	t.Setenv("XDG_CACHE_HOME", t.TempDir())
	const contest, task = "fixture", "ovr"
	taskDir := cachepath.Task(contest, task)
	testsDir := filepath.Join(taskDir, "tests")
	if err := os.MkdirAll(testsDir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(testsDir, "01.in"), []byte("x\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(testsDir, "01.out"), []byte("ok\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := saveMeta(filepath.Join(taskDir, "meta.toml"), &Meta{Contest: contest, Task: task, TimeLimitMs: 2000, FetchedAt: time.Unix(0, 0)}); err != nil {
		t.Fatal(err)
	}

	// 解答パス (Layout 解決先) と override 先。Run は os.Stat するので両方実体を置く。
	dir := t.TempDir()
	layPath := filepath.Join(dir, "sol.py")
	ovrPath := filepath.Join(dir, "override.py")
	for _, p := range []string{layPath, ovrPath} {
		if err := os.WriteFile(p, []byte("print('ok')\n"), 0o644); err != nil {
			t.Fatal(err)
		}
	}

	run := func(override string) string {
		exec := &recordingExecutor{stdout: "ok\n"}
		opts := Options{
			Contest:              contest,
			Task:                 task,
			Layout:               fixedLayout{layPath},
			ExecutorFor:          func(string) (Executor, error) { return exec, nil },
			Reporter:             NewSummaryReporter(),
			SolutionPathOverride: override,
		}
		if code, err := Run(opts); err != nil || code != 0 {
			t.Fatalf("Run(override=%q) = (code %d, err %v), want (0, nil)", override, code, err)
		}
		return exec.got
	}

	if got := run(""); got != layPath {
		t.Errorf("override 空: 実行対象 = %q, want Layout 解決の %q", got, layPath)
	}
	if got := run(ovrPath); got != ovrPath {
		t.Errorf("override 指定: 実行対象 = %q, want override の %q", got, ovrPath)
	}
}
