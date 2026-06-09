package main

import (
	"fmt"
	"os"

	"github.com/atotto/clipboard"
	"github.com/cry999/atcoder-daily-training/internal/layout"
)

// prepareSubmission は `test --submit` のサンプル全通過後に呼ばれる提出準備。
// 解答をクリップボードへコピーし、提出ページをブラウザで開く (best-effort)。
// 実提出 (認証付き POST) はしない — 認証が安定するまではブラウザに委ねる (ADR 0006)。
//
// 旧 `atcoder submit` の後半 (サンプルゲート後の処理) を移設したもの。
func prepareSubmission(contest, task string, lay layout.Layout, noOpen bool) (int, error) {
	solutionPath, err := lay.SolutionPath(contest, task)
	if err != nil {
		return 2, err
	}

	src, err := os.ReadFile(solutionPath)
	if err != nil {
		return 1, fmt.Errorf("解答ファイルの読み込みに失敗しました: %w", err)
	}
	if err := clipboard.WriteAll(string(src)); err != nil {
		return 1, fmt.Errorf("クリップボードへのコピーに失敗しました: %w", err)
	}
	fmt.Printf("クリップボードにコピーしました: %s\n", solutionPath)

	submitURL := fmt.Sprintf("https://atcoder.jp/contests/%s/submit?taskScreenName=%s", contest, task)
	if noOpen {
		fmt.Printf("提出ページ: %s\n", submitURL)
		return 0, nil
	}
	if err := openBrowser(submitURL); err != nil {
		// ブラウザを開けなくてもコピーは済んでいるので致命的ではない。
		fmt.Fprintf(os.Stderr, "ブラウザを開けませんでした (%v)。手動で開いてください: %s\n", err, submitURL)
		return 0, nil
	}
	fmt.Printf("提出ページを開きました: %s\n", submitURL)
	return 0, nil
}
