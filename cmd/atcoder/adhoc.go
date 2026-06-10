package main

import (
	"errors"
	"fmt"
	"path/filepath"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/runexec"
	"github.com/cry999/atcoder-daily-training/internal/runner"
	"github.com/cry999/atcoder-daily-training/internal/ui"
)

// runAdHoc は `atcoder test` の ad-hoc / 対話モード。自前の stdin/ファイルで解答を
// 1 回実行し、出力を見る (--out 指定時は判定する)。判定 (PASS/FAIL の suite) は
// サンプルモード側 (testexec) が担い、こちらは runexec.Run へ結線する。
//
// 旧 `atcoder run` サブコマンドの中身を移設したもの。対話モードは親 stdin に直結し
// 出力もキャプチャしないため、judge (--out) ともファイル入力 (--in <path>) とも
// 併用できない (引数エラー = exit 2)。
func runAdHoc(contest, task string, lay layout.Layout, inFile, outFile string,
	interactive, autoRestart, debug, verbose bool, timeout time.Duration, tolerance float64) (int, error) {
	if interactive {
		if outFile != "" {
			return 2, errors.New("--interactive cannot be combined with --out (judging needs batch-captured output)")
		}
		if inFile != "" && inFile != "-" {
			return 2, errors.New("--interactive reads from the parent stdin; do not pass a file with --in (pipe the file instead)")
		}
	}

	return runexec.Run(runexec.Options{
		Contest:     contest,
		Task:        task,
		Layout:      lay,
		InFile:      inFile,
		OutFile:     outFile,
		Interactive: interactive,
		AutoRestart: autoRestart,
		Timeout:     timeout,
		Tolerance:   tolerance,
		Debug:       debug,
		ExecutorFor: selectRunExecutor,
		Reporter:    ui.NewRunReporter(verbose),
		ChatRunner:  runChat,
	})
}

func runChat(spawn runexec.ChatSpawner, header runexec.ChatHeader) (*runner.ProcessResult, error) {
	return ui.RunChat(ui.Spawner(spawn), ui.ChatHeader{
		Task:        header.Task,
		Contest:     header.Contest,
		TimeLimitMs: header.TimeLimitMs,
		Debug:       header.Debug,
		AutoRestart: header.AutoRestart,
	})
}

func selectRunExecutor(sourcePath string) (runexec.Executor, error) {
	ext := filepath.Ext(sourcePath)
	switch ext {
	case ".py":
		return runner.NewPython()
	default:
		return nil, fmt.Errorf("unsupported extension: %s", ext)
	}
}
