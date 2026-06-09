package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

func cmdCommit(args []string) (int, error) {
	y, m, d := time.Now().Local().Date()
	dateDir := filepath.Join("exercise",
		fmt.Sprintf("%04d", y),
		fmt.Sprintf("%02d", m),
		fmt.Sprintf("%02d", d),
	)
	dateStr := fmt.Sprintf("%04d-%02d-%02d", y, m, d)

	if _, err := os.Stat(dateDir); err != nil {
		return 1, fmt.Errorf("本日の演習ディレクトリが見つかりません: %s", dateDir)
	}

	// 削除も含めて当日ディレクトリ配下を index に反映する。
	if code, err := runGit(os.Stdout, os.Stderr, "add", "-A", "--", dateDir); err != nil || code != 0 {
		if err != nil {
			return 1, fmt.Errorf("git add: %w", err)
		}
		return code, nil
	}

	// dateDir 配下に何もステージされなかったらエラー終了。
	if isClean, err := indexClean(dateDir); err != nil {
		return 1, err
	} else if isClean {
		return 1, fmt.Errorf("ステージ対象がありません (%s 配下に変更/新規ファイルなし)", dateDir)
	}

	// pathspec 付きの commit にすることで「dateDir 以外の staged 変更」は index に残す。
	msg := "exercise: " + dateStr
	if code, err := runGit(os.Stdout, os.Stderr, "commit", "-m", msg, "--", dateDir); err != nil || code != 0 {
		if err != nil {
			return 1, fmt.Errorf("git commit: %w", err)
		}
		return code, nil
	}
	return 0, nil
}

func runGit(stdout, stderr *os.File, args ...string) (int, error) {
	cmd := exec.Command("git", args...)
	cmd.Stdout = stdout
	cmd.Stderr = stderr
	err := cmd.Run()
	if err == nil {
		return 0, nil
	}
	if exitErr, ok := err.(*exec.ExitError); ok {
		return exitErr.ExitCode(), nil
	}
	return 1, err
}

// indexClean は指定 pathspec 配下に staged 変更が無いかを判定する (=「clean なら true」)。
func indexClean(pathspec string) (bool, error) {
	cmd := exec.Command("git", "diff", "--cached", "--quiet", "--", pathspec)
	err := cmd.Run()
	if err == nil {
		return true, nil // exit 0 = no diff
	}
	if exitErr, ok := err.(*exec.ExitError); ok && exitErr.ExitCode() == 1 {
		return false, nil // exit 1 = has diff
	}
	return false, fmt.Errorf("git diff --cached: %w", err)
}
