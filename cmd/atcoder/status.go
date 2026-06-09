package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/atcoder"
	"golang.org/x/term"
)

// cmdStatus は認証付きで /submissions/me を取得し、指定タスクの最新提出の
// verdict を表示する。--watch で確定までポーリングする。
func cmdStatus(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := args[0]

	flags := flag.NewFlagSet("status", flag.ContinueOnError)
	taskFlag := flags.String("task", "", `task ID、または短縮形 (例 "d" → "<contest>_d")`)
	watch := flags.Bool("watch", false, "verdict が確定するまでポーリング表示する")
	flags.BoolVar(watch, "w", false, "--watch の短縮形")
	interval := flags.Duration("interval", 3*time.Second, "--watch のポーリング間隔 (下限 2s)")
	open := flags.Bool("open", false, "表示した提出の個別ページをブラウザで開く")
	flags.SetOutput(os.Stderr)
	if err := flags.Parse(args[1:]); err != nil {
		return 2, err
	}

	task := *taskFlag
	if task != "" && !strings.Contains(task, "_") {
		task = contest + "_" + task
	}
	if *interval < 2*time.Second {
		*interval = 2 * time.Second
	}

	sess, err := atcoder.LoadSession()
	if err != nil {
		if errors.Is(err, atcoder.ErrNoSession) {
			return 1, errors.New("ログインしていません。atcoder login を実行してください")
		}
		return 1, err
	}
	src := atcoder.AuthedSource(sess)

	if *watch {
		return watchStatus(src, contest, task, *interval, *open)
	}
	return showStatus(src, contest, task, *open)
}

// fetchTarget は contest の提出を取得し、task 指定があれば該当の最新 1 件、
// 無ければ最新 1 件を返す。見つからなければ (nil, nil)。
func fetchTarget(src atcoder.Source, contest, task string) (*atcoder.Submission, []atcoder.Submission, error) {
	subs, err := src.Submissions(contest)
	if err != nil {
		return nil, nil, err
	}
	if task == "" {
		if len(subs) == 0 {
			return nil, subs, nil
		}
		return &subs[0], subs, nil
	}
	for i := range subs {
		if subs[i].Task == task {
			return &subs[i], subs, nil
		}
	}
	return nil, subs, nil
}

func showStatus(src atcoder.Source, contest, task string, open bool) (int, error) {
	target, subs, err := fetchTarget(src, contest, task)
	if err != nil {
		return statusErrCode(err), friendlyErr(err)
	}
	if task == "" {
		if len(subs) == 0 {
			return 1, errors.New("提出が見つかりません")
		}
		// task 未指定: 最新数件を一覧。
		n := len(subs)
		if n > 10 {
			n = 10
		}
		for i := 0; i < n; i++ {
			printSubmission(&subs[i])
		}
		return 0, nil
	}
	if target == nil {
		return 1, errors.New("提出が見つかりません")
	}
	printSubmission(target)
	if open {
		_ = openBrowser(target.URL)
	}
	return 0, nil
}

func watchStatus(src atcoder.Source, contest, task string, interval time.Duration, open bool) (int, error) {
	if task == "" {
		return 2, errors.New("--watch には --task が必要です")
	}
	// Ctrl+C で 0 終了 (test --watch と同じ)。
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)
	defer signal.Stop(sigCh)

	isTTY := isTerminalStdout()
	for {
		target, _, err := fetchTarget(src, contest, task)
		if err != nil {
			return statusErrCode(err), friendlyErr(err)
		}
		if target == nil {
			// まだ反映されていない可能性。待って再取得。
			fmt.Fprintf(os.Stderr, "提出待ち... %s\n", task)
		} else if atcoder.IsFinal(target.Verdict) {
			if isTTY {
				fmt.Print("\r\033[K")
			}
			printSubmission(target)
			if open {
				_ = openBrowser(target.URL)
			}
			return 0, nil
		} else {
			line := fmt.Sprintf("%s  %s", target.Task, target.Verdict)
			if isTTY {
				fmt.Printf("\r\033[K%s", line)
			} else {
				fmt.Println(line)
			}
		}

		select {
		case <-sigCh:
			if isTTY {
				fmt.Println()
			}
			return 0, nil
		case <-time.After(interval):
		}
	}
}

func printSubmission(s *atcoder.Submission) {
	title := s.TaskTitle
	if title == "" {
		title = s.Task
	}
	fmt.Printf("%s  %s\n", s.Task, title)

	parts := []string{s.Verdict}
	if s.Language != "" {
		parts = append(parts, s.Language)
	}
	if s.ExecTimeMs > 0 {
		parts = append(parts, fmt.Sprintf("%d ms", s.ExecTimeMs))
	}
	if s.MemoryKiB > 0 {
		parts = append(parts, fmt.Sprintf("%d KiB", s.MemoryKiB))
	}
	if !s.SubmittedAt.IsZero() {
		parts = append(parts, "("+s.SubmittedAt.Format("2006-01-02 15:04")+")")
	}
	fmt.Printf("  %s\n", strings.Join(parts, "   "))
	if s.URL != "" {
		fmt.Printf("  %s\n", s.URL)
	}
}

// statusErrCode はソース取得エラーを exit code に写す。失効は再ログインを促す
// メッセージに差し替えたいので、呼び出し側は friendlyErr も使う。
func statusErrCode(err error) int { return 1 }

// friendlyErr は失効エラーを利用者向けの案内に差し替える。
func friendlyErr(err error) error {
	if errors.Is(err, atcoder.ErrSessionExpired) {
		return errors.New("セッションが失効しました。atcoder login を実行してください")
	}
	return err
}

func isTerminalStdout() bool {
	return term.IsTerminal(int(os.Stdout.Fd()))
}
