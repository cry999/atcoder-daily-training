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

// ChatHandle は対話型 (chat-style) UI 用の子プロセスハンドル。
// 呼び出し側が pipes に対して読み書きを行い、終了時に Wait() を呼ぶ。
type ChatHandle struct {
	cmd    *exec.Cmd
	start  time.Time
	Stdin  io.WriteCloser
	Stdout io.ReadCloser
	Stderr io.ReadCloser
	out    io.Closer // 統合 pipe の read 端 (Wait で閉じて fd を返す)。nil 可
}

// Wait は子プロセスの終了を待ち、ProcessResult を返す。タイムアウトの概念は
// chat モードでは設けない (利用者がリアルタイムで操作するため)。
// cmd が無い (実プロセスを持たない) handle では即 Exited を返す (防御的)。
func (h *ChatHandle) Wait() *ProcessResult {
	if h.cmd == nil {
		return &ProcessResult{Status: Exited}
	}
	err := h.cmd.Wait()
	elapsed := time.Since(h.start)
	if h.out != nil {
		_ = h.out.Close() // 統合 pipe の read 端を返す
	}

	exitCode := 0
	if err != nil {
		var exitErr *exec.ExitError
		if errors.As(err, &exitErr) {
			exitCode = exitErr.ExitCode()
		}
	}
	return &ProcessResult{
		Status:   Exited,
		Elapsed:  elapsed,
		ExitCode: exitCode,
	}
}

// Kill は子プロセスを強制終了する。cmd / Process が無ければ no-op (防御的)。
func (h *ChatHandle) Kill() error {
	if h.cmd != nil && h.cmd.Process != nil {
		return h.cmd.Process.Kill()
	}
	return nil
}

// StartChat は子プロセスを起動し、stdin と (統合した) 出力ストリームを返す。
// 制限時間は使わない (chat UI 側で必要に応じて Kill する)。
//
// 出力は stdout と stderr を **同じ 1 本の pipe** に束ねて返す (Stdout に統合ストリーム、
// Stderr は空)。別々の pipe を 2 本の scanner で並行に読むと、子が stdout と stderr を
// ほぼ同時に出した瞬間 (例: デバッグ print の直後に traceback) にどちらが先に読み出されるか
// 非決定的になり、chat 画面で DEBUG 行と Runtime Error が互い違いに並ぶ。1 本に束ねれば
// カーネルが write 順を保つので子が出した順がそのまま残る (stderr 由来の赤色付けは chat 側で
// traceback を行内容から検出して復元する)。
func (p *Python) StartChat(source string, extraEnv []string) (*ChatHandle, error) {
	cmd := exec.Command(p.binPath, source)
	cmd.Env = append(os.Environ(), "PYTHONUNBUFFERED=1")
	if len(extraEnv) > 0 {
		cmd.Env = append(cmd.Env, extraEnv...)
	}

	stdin, err := cmd.StdinPipe()
	if err != nil {
		return nil, err
	}
	// stdout/stderr を同一 pipe に向ける。子の fd1/fd2 が同じ write 端を指すので write 順が保たれる。
	pr, pw, err := os.Pipe()
	if err != nil {
		return nil, err
	}
	cmd.Stdout = pw
	cmd.Stderr = pw

	if err := cmd.Start(); err != nil {
		_ = pr.Close()
		_ = pw.Close()
		return nil, err
	}
	// 親側の write 端は閉じる。子が終了して fd を閉じたとき pr が EOF を返すように。
	_ = pw.Close()
	return &ChatHandle{
		cmd:    cmd,
		start:  time.Now(),
		Stdin:  stdin,
		Stdout: pr,                                // stdout/stderr を統合した単一ストリーム (順序保持)
		Stderr: io.NopCloser(bytes.NewReader(nil)), // 統合済みなので別 stderr は無い (即 EOF)
		out:    pr,
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
