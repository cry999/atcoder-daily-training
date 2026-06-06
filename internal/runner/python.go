package runner

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

type Python struct {
	binPath string
}

func NewPython() (*Python, error) {
	if root, err := findRepoRoot(); err == nil {
		candidate := filepath.Join(root, ".venv", "bin", "python")
		if _, err := os.Stat(candidate); err == nil {
			return &Python{binPath: candidate}, nil
		}
	}
	if p, err := exec.LookPath("python"); err == nil {
		return &Python{binPath: p}, nil
	}
	if p, err := exec.LookPath("python3"); err == nil {
		return &Python{binPath: p}, nil
	}
	return nil, errors.New("python が見つかりません (.venv/bin/python も PATH の python も見つかりません)")
}

func (p *Python) Run(ctx context.Context, source string, input []byte, timeout time.Duration, extraEnv []string) (*ProcessResult, error) {
	cctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	cmd := exec.CommandContext(cctx, p.binPath, source)
	cmd.Stdin = bytes.NewReader(input)
	if len(extraEnv) > 0 {
		cmd.Env = append(os.Environ(), extraEnv...)
	}
	var outBuf, errBuf bytes.Buffer
	cmd.Stdout = &outBuf
	cmd.Stderr = &errBuf

	start := time.Now()
	runErr := cmd.Run()
	elapsed := time.Since(start)

	if errors.Is(cctx.Err(), context.DeadlineExceeded) {
		return &ProcessResult{
			Status:  TimedOut,
			Stdout:  outBuf.String(),
			Stderr:  errBuf.String(),
			Elapsed: elapsed,
		}, nil
	}

	exitCode := 0
	if runErr != nil {
		var exitErr *exec.ExitError
		if errors.As(runErr, &exitErr) {
			exitCode = exitErr.ExitCode()
		} else {
			return nil, fmt.Errorf("python execution failed: %w", runErr)
		}
	}
	return &ProcessResult{
		Status:   Exited,
		Stdout:   outBuf.String(),
		Stderr:   errBuf.String(),
		Elapsed:  elapsed,
		ExitCode: exitCode,
	}, nil
}

// RunInteractive はインタラクティブ問題向けに、子プロセスの stdin/stdout/stderr を
// 呼び出し側から渡された Reader/Writer に直接接続して実行する。
// 出力は捕捉されず、そのまま渡された Writer に流れる (= ProcessResult の Stdout/Stderr は空)。
func (p *Python) RunInteractive(ctx context.Context, source string, stdin io.Reader, stdout, stderr io.Writer, timeout time.Duration, extraEnv []string) (*ProcessResult, error) {
	cctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	cmd := exec.CommandContext(cctx, p.binPath, source)
	cmd.Stdin = stdin
	cmd.Stdout = stdout
	cmd.Stderr = stderr
	// インタラクティブ問題では Python の line-buffer/full-buffer 化により
	// stdout が滞留すると判定機 (or 利用者) との応答が成立しない。常に unbuffered で起動する。
	cmd.Env = append(os.Environ(), "PYTHONUNBUFFERED=1")
	if len(extraEnv) > 0 {
		cmd.Env = append(cmd.Env, extraEnv...)
	}

	start := time.Now()
	runErr := cmd.Run()
	elapsed := time.Since(start)

	if errors.Is(cctx.Err(), context.DeadlineExceeded) {
		return &ProcessResult{
			Status:  TimedOut,
			Elapsed: elapsed,
		}, nil
	}

	exitCode := 0
	if runErr != nil {
		var exitErr *exec.ExitError
		if errors.As(runErr, &exitErr) {
			exitCode = exitErr.ExitCode()
		} else {
			return nil, fmt.Errorf("python execution failed: %w", runErr)
		}
	}
	return &ProcessResult{
		Status:   Exited,
		Elapsed:  elapsed,
		ExitCode: exitCode,
	}, nil
}

func findRepoRoot() (string, error) {
	dir, err := os.Getwd()
	if err != nil {
		return "", err
	}
	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "", errors.New("go.mod not found in any parent")
		}
		dir = parent
	}
}
