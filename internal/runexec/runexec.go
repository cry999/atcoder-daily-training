// Package runexec implements the `exercise run` subcommand: execute a solution
// against an arbitrary stdin (file or pipe) without any expected-output
// comparison. Use this when you want to feed a custom input to a solution and
// just see what comes back (for debugging or manual exploration).
package runexec

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/cry999/atcoder-daily-training/internal/cachepath"
	"github.com/cry999/atcoder-daily-training/internal/runner"
)

type Executor interface {
	Run(ctx context.Context, source string, input []byte, timeout time.Duration, extraEnv []string) (*runner.ProcessResult, error)
	RunInteractive(ctx context.Context, source string, stdin io.Reader, stdout, stderr io.Writer, timeout time.Duration, extraEnv []string) (*runner.ProcessResult, error)
}

type ExecutorFor func(sourcePath string) (Executor, error)

type Reporter interface {
	Header(task, contest string, timeLimitMs, timeoutMs int, interactive bool)
	Result(r Result)
}

type Options struct {
	Contest     string
	Task        string
	StdinFile   string        // "" / "-" → 親プロセスの stdin、それ以外はそのファイルを読む
	Timeout     time.Duration // 0 → meta.toml.time_limit_ms か 2 秒のデフォルト
	Debug       bool          // DEBUG=1 と [DEBUG] フィルタ (test と同じ規約)
	ExecutorFor ExecutorFor
	Reporter    Reporter
}

type Status int

const (
	Ok      Status = iota // 正常終了 (ExitCode == 0)
	Timeout               // 制限時間超過
	Crashed               // 非ゼロ終了
)

type Result struct {
	Status   Status
	Input    string
	Stdout   string
	Stderr   string
	Debug    string
	Elapsed  time.Duration
	ExitCode int
}

const defaultTimeLimitMs = 2000

func Run(opts Options) (int, error) {
	y, m, d := time.Now().Local().Date()
	dateDir := filepath.Join("exercise",
		fmt.Sprintf("%04d", y),
		fmt.Sprintf("%02d", m),
		fmt.Sprintf("%02d", d),
	)
	solutionPath := filepath.Join(dateDir, opts.Task+".py")
	if _, err := os.Stat(solutionPath); err != nil {
		return 1, fmt.Errorf("解答ファイルが見つかりません: %s", solutionPath)
	}

	timeLimitMs := defaultTimeLimitMs
	metaPath := filepath.Join(cachepath.Task(opts.Contest, opts.Task), "meta.toml")
	if m, err := loadMeta(metaPath); err == nil {
		timeLimitMs = m.TimeLimitMs
	}
	timeout := time.Duration(timeLimitMs) * time.Millisecond
	if opts.Timeout > 0 {
		timeout = opts.Timeout
	}

	executor, err := opts.ExecutorFor(solutionPath)
	if err != nil {
		return 1, err
	}

	var extraEnv []string
	if opts.Debug {
		extraEnv = []string{"DEBUG=1"}
	}

	interactive := opts.StdinFile == "-"
	opts.Reporter.Header(opts.Task, opts.Contest, timeLimitMs, int(timeout/time.Millisecond), interactive)

	if interactive {
		return runInteractive(opts, executor, solutionPath, timeout, extraEnv)
	}
	return runBatch(opts, executor, solutionPath, timeout, extraEnv)
}

func runBatch(opts Options, executor Executor, solutionPath string, timeout time.Duration, extraEnv []string) (int, error) {
	input, err := readStdin(opts.StdinFile)
	if err != nil {
		return 1, err
	}

	pr, err := executor.Run(context.Background(), solutionPath, input, timeout, extraEnv)
	if err != nil {
		return 1, err
	}

	stdout := pr.Stdout
	var debugOut string
	if opts.Debug {
		stdout, debugOut = splitDebug(stdout)
	}

	res := Result{
		Input:    strings.TrimRight(string(input), "\n"),
		Stdout:   strings.TrimRight(stdout, "\n"),
		Stderr:   pr.Stderr,
		Debug:    debugOut,
		Elapsed:  pr.Elapsed,
		ExitCode: pr.ExitCode,
	}
	res.Status = classify(pr)

	opts.Reporter.Result(res)
	if res.Status != Ok {
		return 1, nil
	}
	return 0, nil
}

func runInteractive(opts Options, executor Executor, solutionPath string, timeout time.Duration, extraEnv []string) (int, error) {
	var stdin io.Reader = os.Stdin
	var echo *linePrefixWriter
	if !stdinIsTTY() {
		// 非 TTY 入力 (pipe/redirect) では端末 echo が効かないので、TeeReader で
		// 各行を "> " プレフィックスを付けて os.Stdout にも流す。これでスクリプト
		// 経由でも「何が入力として送られたか」がプログラム出力と並んで見える。
		echo = &linePrefixWriter{w: os.Stdout, prefix: "> "}
		stdin = io.TeeReader(os.Stdin, echo)
	}

	pr, err := executor.RunInteractive(context.Background(), solutionPath, stdin, os.Stdout, os.Stderr, timeout, extraEnv)
	if echo != nil {
		echo.Flush()
	}
	if err != nil {
		return 1, err
	}

	// インタラクティブモードでは stdout/stderr は live で出ているため、Result の同フィールドは空のまま。
	res := Result{
		Elapsed:  pr.Elapsed,
		ExitCode: pr.ExitCode,
	}
	res.Status = classify(pr)

	opts.Reporter.Result(res)
	if res.Status != Ok {
		return 1, nil
	}
	return 0, nil
}

func stdinIsTTY() bool {
	stat, err := os.Stdin.Stat()
	if err != nil {
		return false
	}
	return (stat.Mode() & os.ModeCharDevice) != 0
}

// linePrefixWriter は書き込まれたバイト列を改行単位で区切り、各行にプレフィックスを
// 付けて下流の Writer に流すラッパー。改行で終わっていない末尾は次の Write まで
// バッファに保持される (Flush で強制吐き出し)。
type linePrefixWriter struct {
	w      io.Writer
	prefix string
	buf    []byte
}

func (l *linePrefixWriter) Write(b []byte) (int, error) {
	l.buf = append(l.buf, b...)
	for {
		i := bytes.IndexByte(l.buf, '\n')
		if i < 0 {
			break
		}
		if _, err := fmt.Fprintf(l.w, "%s%s\n", l.prefix, l.buf[:i]); err != nil {
			return 0, err
		}
		l.buf = l.buf[i+1:]
	}
	return len(b), nil
}

func (l *linePrefixWriter) Flush() {
	if len(l.buf) == 0 {
		return
	}
	fmt.Fprintf(l.w, "%s%s\n", l.prefix, l.buf)
	l.buf = nil
}

func classify(pr *runner.ProcessResult) Status {
	switch pr.Status {
	case runner.TimedOut:
		return Timeout
	case runner.Exited:
		if pr.ExitCode != 0 {
			return Crashed
		}
		return Ok
	}
	return Ok
}

func readStdin(stdinFile string) ([]byte, error) {
	if stdinFile == "" || stdinFile == "-" {
		return io.ReadAll(os.Stdin)
	}
	return os.ReadFile(stdinFile)
}

// runMeta は testexec の meta と同じ TOML 形式のサブセット。time_limit_ms だけ取り出せれば十分。
type runMeta struct {
	TimeLimitMs int `toml:"time_limit_ms"`
}

func loadMeta(path string) (*runMeta, error) {
	var m runMeta
	if _, err := toml.DecodeFile(path, &m); err != nil {
		return nil, err
	}
	if m.TimeLimitMs <= 0 {
		return nil, errors.New("time_limit_ms missing or non-positive in meta.toml")
	}
	return &m, nil
}

const debugPrefix = "[DEBUG]"

func splitDebug(stdout string) (filtered, debug string) {
	var filteredLines, debugLines []string
	for _, line := range strings.Split(stdout, "\n") {
		if strings.HasPrefix(line, debugPrefix) {
			debugLines = append(debugLines, line)
		} else {
			filteredLines = append(filteredLines, line)
		}
	}
	return strings.Join(filteredLines, "\n"), strings.Join(debugLines, "\n")
}
