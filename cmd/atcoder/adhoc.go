package main

import (
	"errors"
	"fmt"
	"path/filepath"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cachepath"
	"github.com/cry999/atcoder-daily-training/internal/chatlog"
	"github.com/cry999/atcoder-daily-training/internal/layout"
	"github.com/cry999/atcoder-daily-training/internal/runexec"
	"github.com/cry999/atcoder-daily-training/internal/runner"
	"github.com/cry999/atcoder-daily-training/internal/testexec"
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
	interactive, autoRestart, debug, verbose bool, timeout time.Duration, tolerance float64, editorOverride, nvimRemote string) (int, error) {
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
		ChatRunner:  makeChatRunner(contest, task, lay, tolerance, editorOverride, nvimRemote),
	})
}

// makeChatRunner は ChatRunner クロージャを作る。chat に Ctrl+S の提出準備フックや
// ケース保存先 (tests-extra) を注入するため、contest/task/lay/tolerance を捕捉する
// (これらは runexec.ChatHeader には乗らない)。
func makeChatRunner(contest, task string, lay layout.Layout, tolerance float64, editorOverride, nvimRemote string) func(runexec.ChatSpawner, runexec.ChatHeader) (*runner.ProcessResult, error) {
	return func(spawn runexec.ChatSpawner, header runexec.ChatHeader) (*runner.ProcessResult, error) {
		// :replay (要件 039): 同じ問題の前回入力を先読みし、今回の入力を session ごとに記録する。
		sid := chatlog.NewSessionID()
		prev, _ := chatlog.LoadLastSession(contest, task) // best-effort: 失敗時は前回入力なし
		return ui.RunChat(ui.Spawner(spawn), ui.ChatHeader{
			Task:        header.Task,
			Contest:     header.Contest,
			TimeLimitMs: header.TimeLimitMs,
			Debug:       header.Debug,
			AutoRestart: header.AutoRestart,
			WatchPath:   header.WatchPath,
			Submit:      chatSubmitFunc(contest, task, lay),
			SubmitCheck: chatSubmitCheckFunc(contest, task, lay, tolerance), // Ctrl+S の提出前チェック (要件 044)
			TaskDir:     cachepath.Task(contest, task),                      // :case/:w の保存先 (tests-extra)
			Tolerance:   tolerance,
			Edit:        editFunc(editorOverride, nvimRemote), // Ctrl+E でエディタ起動 (要件 038/041)
			PrevInputs:  prev,
			RecordInput: func(line string) { _ = chatlog.Record(contest, task, sid, line) },
			MetaShow:    chatMetaShowFunc(contest, task), // :meta の表示 (要件 050)
			MetaSet:     chatMetaSetFunc(contest, task),  // :meta の編集 (要件 050)
		})
	}
}

// chatSubmitFunc は chat の Ctrl+S で呼ばれる提出準備フック。submitPrepCore (印字なし) を
// 呼んで結果文を組む。chat は常にブラウザを開く (noOpen=false)。
func chatSubmitFunc(contest, task string, lay layout.Layout) ui.SubmitFunc {
	return func() ui.SubmitResult {
		// chat は常に [DEBUG] 出力行をコメントアウトしてコピーする (keepDebug=false)。
		src, err := buildSubmitSource(contest, task, lay, false)
		if err != nil {
			return ui.SubmitResult{Message: "失敗: " + err.Error(), IsError: true}
		}
		out, err := submitPrepCore(src, contest, task, false)
		if err != nil {
			return ui.SubmitResult{Message: "失敗: " + err.Error(), IsError: true}
		}
		msg := "クリップボードにコピー " + out.CopiedPath
		if out.DebugCommented > 0 {
			msg += fmt.Sprintf(" (DEBUG %d 行コメントアウト)", out.DebugCommented)
		}
		if out.Opened {
			msg += " / 提出ページを開きました"
		} else {
			msg += " / 提出ページ: " + out.URL + " (ブラウザを開けませんでした、手動で開いてください)"
		}
		return ui.SubmitResult{Message: msg}
	}
}

// chatSubmitCheckFunc は chat の Ctrl+S 提出前チェック (要件 044 / 049)。提出される中身
// (= [DEBUG] print をコメントアウトしたソース。chat は常にコメントアウト) を一時ファイルに
// 書き出し、それをサンプル判定の実行対象にして SummaryReporter (stdout 非汚染) で 1 度実行し、
// 提出ゲート (全通過・実行可否・DEBUG 検出) を評価して SubmitCheck を返す。TUI を汚さないよう
// 表示はせず、結果だけ返す (chat 側が行に整形する)。
func chatSubmitCheckFunc(contest, task string, lay layout.Layout, tolerance float64) ui.SubmitCheckFunc {
	return func() ui.SubmitCheck {
		// 提出される中身 (コメントアウト後ソース) を構築し、それを実行対象にして判定する。
		src, err := buildSubmitSource(contest, task, lay, false)
		if err != nil {
			return ui.SubmitCheck{Clean: false, Reasons: []string{"提出前チェックを実行できませんでした: " + err.Error()}}
		}
		tmp, cleanup, err := writeTempSource(src.Path, src.Body)
		if err != nil {
			return ui.SubmitCheck{Clean: false, Reasons: []string{"提出前チェックを実行できませんでした: " + err.Error()}}
		}
		defer cleanup()

		gate := &submitGateReporter{Reporter: testexec.NewSummaryReporter()}
		code, runErr := testexec.Run(testexec.Options{
			Contest:              contest,
			Task:                 task,
			Layout:               lay,
			Tolerance:            tolerance,
			ExecutorFor:          selectExecutor,
			Reporter:             gate,
			SolutionPathOverride: tmp, // コメントアウト後ソースを実行する (要件 049)。
		})
		reasons := submitGateReasons(code, runErr, gate.DebugSeen())
		return ui.SubmitCheck{Clean: len(reasons) == 0, Reasons: reasons}
	}
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
