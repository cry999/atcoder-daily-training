package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"runtime"
	"strings"

	"github.com/atotto/clipboard"
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
	"github.com/cry999/atcoder-daily-training/internal/ui"
)

// cmdSubmit は提出の前準備を行う。実際の提出は認証が必要なためブラウザ側に委ねる。
//  1. サンプルテストを全件実行し、全通過したときだけ次へ進む。
//  2. 解答ソースをクリップボードへコピーする。
//  3. AtCoder の提出ページをブラウザで開く（best-effort）。
func cmdSubmit(args []string) (int, error) {
	if len(args) < 1 {
		return 2, errors.New("contest is required")
	}
	contest := args[0]

	flags := flag.NewFlagSet("submit", flag.ContinueOnError)
	taskFlag := addTaskFlag(flags)
	refresh := flags.Bool("refresh", false, "Force refetch sample cases")
	tolFlag := flags.Float64("tolerance", 0, "Absolute/relative tolerance for float token comparison (e.g. 1e-9). 0 or unset → use default 1e-6.")
	layoutFlag := addLayoutFlag(flags)
	noOpen := flags.Bool("no-open", false, "Do not open the submit page in a browser")
	flags.SetOutput(os.Stderr)

	if err := flags.Parse(args[1:]); err != nil {
		return 2, err
	}
	task := *taskFlag
	if task == "" {
		return 2, errors.New("--task is required")
	}
	// Short form: `--task d` → `<contest>_d` when no underscore is present.
	if !strings.Contains(task, "_") {
		task = contest + "_" + task
	}

	lay, err := layout.Parse(*layoutFlag, contest)
	if err != nil {
		return 2, err
	}

	solutionPath, err := lay.SolutionPath(contest, task)
	if err != nil {
		return 2, err
	}

	// 1. サンプルテストを全件実行。全通過 (exit 0) でなければ提出準備を中止する。
	code, err := testexec.Run(testexec.Options{
		Contest:     contest,
		Task:        task,
		Layout:      lay,
		Refresh:     *refresh,
		Tolerance:   *tolFlag,
		ExecutorFor: selectExecutor,
		Reporter:    ui.NewTestReporter(false, false),
	})
	if err != nil {
		return code, err
	}
	if code != 0 {
		fmt.Fprintln(os.Stderr, "テストが全通過していないため提出準備を中止しました。")
		return code, nil
	}

	// 2. 解答ソースをクリップボードへコピー。
	src, err := os.ReadFile(solutionPath)
	if err != nil {
		return 1, fmt.Errorf("解答ファイルの読み込みに失敗しました: %w", err)
	}
	if err := clipboard.WriteAll(string(src)); err != nil {
		return 1, fmt.Errorf("クリップボードへのコピーに失敗しました: %w", err)
	}
	fmt.Printf("クリップボードにコピーしました: %s\n", solutionPath)

	// 3. 提出ページをブラウザで開く (best-effort)。
	submitURL := fmt.Sprintf("https://atcoder.jp/contests/%s/submit?taskScreenName=%s", contest, task)
	if *noOpen {
		fmt.Printf("提出ページ: %s\n", submitURL)
		return 0, nil
	}
	if err := openBrowser(submitURL); err != nil {
		// ブラウザを開けなくてもクリップボードへのコピーは済んでいるので致命的ではない。
		fmt.Fprintf(os.Stderr, "ブラウザを開けませんでした (%v)。手動で開いてください: %s\n", err, submitURL)
		return 0, nil
	}
	fmt.Printf("提出ページを開きました: %s\n", submitURL)
	return 0, nil
}

// openBrowser は OS 既定のブラウザで URL を開く。
// macOS の `open` は既存ウィンドウを前面化しつつ URL を開く（同一 URL のタブ再利用は保証されない）。
func openBrowser(url string) error {
	var name string
	var args []string
	switch runtime.GOOS {
	case "darwin":
		name, args = "open", []string{url}
	case "windows":
		name, args = "rundll32", []string{"url.dll,FileProtocolHandler", url}
	default: // linux など
		name, args = "xdg-open", []string{url}
	}
	return exec.Command(name, args...).Start()
}
