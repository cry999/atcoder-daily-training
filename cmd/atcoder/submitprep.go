package main

import (
	"fmt"
	"os"

	"github.com/atotto/clipboard"
	"github.com/cry999/atcoder-daily-training/internal/layout"
)

// submitURLFor は提出ページの URL を組む。
func submitURLFor(contest, task string) string {
	return fmt.Sprintf("https://atcoder.jp/contests/%s/submit?taskScreenName=%s", contest, task)
}

// submitOutcome は提出準備の結果。印字しない core (submitPrepCore) が返し、
// 呼び出し側 (CLI 経路 = 印字 / chat 経路 = 行描画) が好きに表示する。
type submitOutcome struct {
	CopiedPath string // クリップボードにコピーした解答パス
	URL        string // 提出ページ URL
	Opened     bool   // ブラウザを開けたか (noOpen 時や失敗時は false)
	OpenErr    error  // ブラウザ起動に失敗したときのエラー (noOpen / 成功時は nil)
}

// submitPrepCore は印字せずに提出準備の副作用 (解答コピー + 提出ページ起動) を行い
// 結果を返す。chat TUI からも呼べるよう stdout には一切書かない。
//
// 解答読込・クリップボード書込の失敗は error。ブラウザ起動失敗はコピーが済んで
// いるので致命的でなく、OpenErr に載せて error にはしない。
func submitPrepCore(contest, task string, lay layout.Layout, noOpen bool) (submitOutcome, error) {
	solutionPath, err := lay.SolutionPath(contest, task)
	if err != nil {
		return submitOutcome{}, err
	}
	src, err := os.ReadFile(solutionPath)
	if err != nil {
		return submitOutcome{}, fmt.Errorf("解答ファイルの読み込みに失敗しました: %w", err)
	}
	if err := clipboard.WriteAll(string(src)); err != nil {
		return submitOutcome{}, fmt.Errorf("クリップボードへのコピーに失敗しました: %w", err)
	}
	out := submitOutcome{CopiedPath: solutionPath, URL: submitURLFor(contest, task)}
	if noOpen {
		return out, nil
	}
	if err := openBrowser(out.URL); err != nil {
		out.OpenErr = err // コピーは済んでいるので致命的でない。
		return out, nil
	}
	out.Opened = true
	return out, nil
}

// prepareSubmission は `test --submit` のサンプル全通過後に呼ばれる提出準備 (CLI 経路)。
// 解答をクリップボードへコピーし、提出ページをブラウザで開く (best-effort)。
// 実提出 (認証付き POST) はしない — 認証は Turnstile 保護で不可、ブラウザに委ねる (ADR 0006)。
//
// 旧 `atcoder submit` の後半 (サンプルゲート後の処理) を移設したもの。
func prepareSubmission(contest, task string, lay layout.Layout, noOpen bool) (int, error) {
	// task/layout の解決失敗は引数誤り (exit 2)。実体処理の失敗は実行時失敗 (exit 1)。
	if _, err := lay.SolutionPath(contest, task); err != nil {
		return 2, err
	}
	out, err := submitPrepCore(contest, task, lay, noOpen)
	if err != nil {
		return 1, err
	}

	fmt.Printf("クリップボードにコピーしました: %s\n", out.CopiedPath)
	if noOpen {
		fmt.Printf("提出ページ: %s\n", out.URL)
		return 0, nil
	}
	if out.Opened {
		fmt.Printf("提出ページを開きました: %s\n", out.URL)
	} else {
		fmt.Fprintf(os.Stderr, "ブラウザを開けませんでした (%v)。手動で開いてください: %s\n", out.OpenErr, out.URL)
	}
	return 0, nil
}
