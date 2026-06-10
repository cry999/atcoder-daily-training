// Package runexec implements the `atcoder run` subcommand: execute a solution
// against an arbitrary stdin (file or pipe), optionally comparing the stdout
// against an expected-output file (--out). Without --out, this is purely a
// "feed a custom input and see what comes back" tool for debugging or manual
// exploration; with --out, it acts as an ad-hoc judge for one input/output pair.
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
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/runner"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

type Executor interface {
	Run(ctx context.Context, source string, input []byte, timeout time.Duration, extraEnv []string) (*runner.ProcessResult, error)
	RunInteractive(ctx context.Context, source string, stdin io.Reader, stdout, stderr io.Writer, timeout time.Duration, extraEnv []string) (*runner.ProcessResult, error)
	StartChat(source string, extraEnv []string) (*runner.ChatHandle, error)
}

type ExecutorFor func(sourcePath string) (Executor, error)

type Reporter interface {
	Header(task, contest string, timeLimitMs, timeoutMs int, mode string)
	Result(r Result)
}

// ChatHeader は chat TUI に渡すメタ情報。runexec は ui には依存しないため、
// 同等の型をここで再宣言し、ChatRunner の引数として渡す。
type ChatHeader struct {
	Task        string
	Contest     string
	TimeLimitMs int
	Debug       bool // true なら chat TUI は子の stdout から [DEBUG] 行を別カテゴリに振り分ける
	AutoRestart bool // true なら chat TUI は起動時から sticky auto-restart
}

// ChatSpawner は chat TUI 内で子プロセスを (再) 起動するためのファクトリ。
// 連続テスト機能 (TUI 内で「もう一回」) のために、TUI 側がライフサイクルを所有して
// 必要な回数だけ呼び出せるよう関数値で渡す。
type ChatSpawner func() (*runner.ChatHandle, error)

// ChatRunner は chat-style TUI を駆動するコールバック。
// composition root (cmd/atcoder) が ui.RunChat を注入する。
// 最終的に最後のセッションの ProcessResult を返す。
type ChatRunner func(spawn ChatSpawner, header ChatHeader) (*runner.ProcessResult, error)

type Options struct {
	Contest     string
	Task        string
	InFile      string        // "" / "-" → 親プロセスの stdin を read-all (batch)、それ以外はそのファイルを batch で読む
	OutFile     string        // 非空のとき、stdout をこのファイルの内容と比較 (judge モード)
	Interactive bool          // true なら子の stdin/stdout/stderr を親に直結する対話モード (TTY なら chat TUI)
	Layout      layout.Layout // nil なら layout.Exercise{} 相当 (旧挙動)
	Timeout     time.Duration // 0 → meta.toml.time_limit_ms か 2 秒のデフォルト
	Tolerance   float64       // float トークン比較の誤差。0 以下なら testexec.DefaultTolerance
	Debug       bool          // DEBUG=1 と [DEBUG] フィルタ (test と同じ規約)
	AutoRestart bool          // true なら対話モードの chat TUI を起動時から sticky auto-restart にする (TTY のみ有効)
	ExecutorFor ExecutorFor
	Reporter    Reporter
	ChatRunner  ChatRunner // 非 nil かつ stdin が TTY のとき chat TUI を起動する
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
	// 以下は --out 指定時 (judge モード) のみ意味を持つ。
	Compared    bool   // 判定を行ったか
	Expected    string // 正規化済みの期待出力
	OutputMatch bool   // 期待出力と一致したか
}

const defaultTimeLimitMs = 2000

func Run(opts Options) (int, error) {
	lay := opts.Layout
	if lay == nil {
		lay = layout.Exercise{}
	}
	solutionPath, err := lay.SolutionPath(opts.Contest, opts.Task)
	if err != nil {
		return 1, err
	}
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

	// インタラクティブモードは --interactive を明示したときだけ。
	// -in と -in - は等価 (どちらも親 stdin を read-all する batch)。
	interactive := opts.Interactive

	// chat モード: --interactive かつ TTY、かつ ChatRunner が注入されているとき。
	// バブルティーの TUI を起動するため、ヘッダは TUI 側で描画する (ここでは何も
	// 出さない — リポータの Header を呼ぶと TUI 起動前に行が漏れて混乱する)。
	if interactive && opts.ChatRunner != nil && stdinIsTTY() {
		return runChatMode(opts, executor, solutionPath, timeLimitMs, extraEnv)
	}

	mode := "(ad-hoc stdin)"
	if interactive {
		mode = "(interactive)"
	} else if opts.OutFile != "" {
		mode = fmt.Sprintf("(judging vs %s)", opts.OutFile)
	}
	opts.Reporter.Header(opts.Task, opts.Contest, timeLimitMs, int(timeout/time.Millisecond), mode)
	if interactive {
		return runInteractive(opts, executor, solutionPath, timeout, extraEnv)
	}
	return runBatch(opts, executor, solutionPath, timeout, extraEnv)
}

func runChatMode(opts Options, executor Executor, solutionPath string, timeLimitMs int, extraEnv []string) (int, error) {
	spawner := func() (*runner.ChatHandle, error) {
		return executor.StartChat(solutionPath, extraEnv)
	}
	pr, err := opts.ChatRunner(spawner, ChatHeader{
		Task:        opts.Task,
		Contest:     opts.Contest,
		TimeLimitMs: timeLimitMs,
		Debug:       opts.Debug,
		AutoRestart: opts.AutoRestart,
	})
	if err != nil {
		return 1, err
	}
	// chat 終了後にステータスを 1 行だけ出して締める (TUI 内ですべての yarn は流したので Result の本文は不要)。
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

func runBatch(opts Options, executor Executor, solutionPath string, timeout time.Duration, extraEnv []string) (int, error) {
	input, err := readStdin(opts.InFile)
	if err != nil {
		return 1, err
	}

	pr, err := executor.Run(context.Background(), solutionPath, input, timeout, extraEnv)
	if err != nil {
		return 1, err
	}

	res := Result{
		Input:    strings.TrimRight(string(input), "\n"),
		Stderr:   pr.Stderr,
		Elapsed:  pr.Elapsed,
		ExitCode: pr.ExitCode,
	}
	res.Status = classify(pr)

	// --out 指定時は judge を回し、Stdout / Debug / Expected を judge 側の
	// 正規化結果で埋める。--out 未指定なら従来通り stdout を見せるだけ。
	if opts.OutFile != "" {
		expected, err := os.ReadFile(opts.OutFile)
		if err != nil {
			return 1, fmt.Errorf("--out のファイルを読み込めませんでした: %w", err)
		}
		pass, expN, actN, debugOut := testexec.Judge(string(expected), pr.Stdout, opts.Debug, opts.Tolerance)
		res.Compared = true
		res.Expected = expN
		res.Stdout = actN
		res.Debug = debugOut
		res.OutputMatch = pass
	} else {
		stdout := pr.Stdout
		var debugOut string
		if opts.Debug {
			stdout, debugOut = splitDebug(stdout)
		}
		res.Stdout = strings.TrimRight(stdout, "\n")
		res.Debug = debugOut
	}

	opts.Reporter.Result(res)
	if res.Status != Ok || (res.Compared && !res.OutputMatch) {
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

func readStdin(inFile string) ([]byte, error) {
	if inFile == "" || inFile == "-" {
		return io.ReadAll(os.Stdin)
	}
	return os.ReadFile(inFile)
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
