package runner

import (
	"bytes"
	"context"
	"errors"
	"fmt"
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

func (p *Python) Run(ctx context.Context, source string, input []byte, timeout time.Duration) (*ProcessResult, error) {
	cctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	cmd := exec.CommandContext(cctx, p.binPath, source)
	cmd.Stdin = bytes.NewReader(input)
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
