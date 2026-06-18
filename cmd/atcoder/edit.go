package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"

	"github.com/cry999/atcoder-daily-training/internal/ui"
)

// editAction は「解答ファイルをどう開くか」の決定 (純粋関数 planEdit が返す。要件 038)。
//   - remote=true:  既に動いている nvim へ送る (端末を奪わない)。argv は nvim --server …。
//   - remote=false: エディタを端末を奪って起動する (nvim 外)。argv はエディタ + パス。
type editAction struct {
	remote bool
	argv   []string
}

// planEdit は Ctrl+E のエディタ起動方法を決める純粋関数。
//   - nvimSock (= $NVIM) が非空 → 親 nvim に remote 送信 (ネスト回避が目的なので最優先)。
//     nvimRemote == "tab" なら --remote-tab (新規タブ。要件 038 の旧既定)、それ以外 (既定 "current")
//     なら --remote (現在のウィンドウで開く = タブ再利用。要件 041)。
//   - それ以外 → editorOverride (config) > editorEnv ($EDITOR) > "nvim" の順でエディタを起動。
//
// editorOverride / editorEnv は空白区切りで argv に展開する (例 "nvim -p")。
func planEdit(nvimSock, nvimRemote, editorOverride, editorEnv, path string) editAction {
	if strings.TrimSpace(nvimSock) != "" {
		remoteFlag := "--remote" // 既定 (current): 現在のウィンドウで開きタブを再利用する
		if strings.TrimSpace(nvimRemote) == "tab" {
			remoteFlag = "--remote-tab"
		}
		return editAction{remote: true, argv: []string{"nvim", "--server", nvimSock, remoteFlag, path}}
	}
	editor := strings.TrimSpace(editorOverride)
	if editor == "" {
		editor = strings.TrimSpace(editorEnv)
	}
	if editor == "" {
		editor = "nvim"
	}
	return editAction{remote: false, argv: append(strings.Fields(editor), path)}
}

// editFunc は chat の Ctrl+E に注入する ui.EditFunc を作る。editorOverride は config の
// editor キー、nvimRemote は config の editor_nvim_remote キー (current/tab。要件 041)。
// 実行時に $NVIM / $EDITOR を読み、planEdit で決めた方法で起動する。
//   - remote: exec.Command(...).Start() の best-effort (openBrowser と同じ。端末を奪わない)。
//   - exec:   *exec.Cmd を EditPlan.Exec に載せ、chat 側が tea.ExecProcess で前面起動する。
func editFunc(editorOverride, nvimRemote string) ui.EditFunc {
	return func(path string) ui.EditPlan {
		act := planEdit(os.Getenv("NVIM"), nvimRemote, editorOverride, os.Getenv("EDITOR"), path)
		if act.remote {
			c := exec.Command(act.argv[0], act.argv[1:]...)
			if err := c.Start(); err != nil {
				return ui.EditPlan{IsError: true, Message: "エディタ起動に失敗: " + err.Error()}
			}
			return ui.EditPlan{Message: fmt.Sprintf("nvim で開きました: %s (:terminal の親 nvim に送信)", path)}
		}
		return ui.EditPlan{Exec: exec.Command(act.argv[0], act.argv[1:]...)}
	}
}
