package ui

import (
	"fmt"
	"os"

	"golang.org/x/term"
)

// ClearScreen は端末をクリアしてカーソルを左上に戻す。スクロールバック
// (\033[3J) も消し、watch の各再実行で画面を作り直す。
func ClearScreen() {
	fmt.Print("\033[H\033[2J\033[3J")
}

// WatchHeader は watch ループの各回の先頭に出すヘッダを stdout に書く。
// 監視中のファイルパスを示す。
func WatchHeader(path string) {
	fmt.Println(watchHeaderStyle.Render("▸ watch ") + valueStyle.Render(path))
	fmt.Println()
}

// WatchFooter は 1 回分のテスト結果の後に出す待機案内。
func WatchFooter(path string) {
	fmt.Println()
	fmt.Println(watchFooterStyle.Render(fmt.Sprintf("watching %s — save to re-run, Ctrl+C to quit", path)))
}

// StartWatchFooter は `atcoder start` の待機案内。保存での再実行に加え、待機中の
// キー操作 ([i] interactive / [q] quit) を示す。
func StartWatchFooter(path string) {
	fmt.Println()
	fmt.Println(watchFooterStyle.Render(fmt.Sprintf("watching %s — save to re-run, [i] interactive, [q]/Ctrl+C quit", path)))
}

// IsStdoutTerminal は stdout が端末かどうかを返す。watch の TTY 必須判定に使う。
func IsStdoutTerminal() bool {
	return isTerminal(os.Stdout)
}

// isTerminal は f が端末かどうかを返す。TestReporter のライブ判定と watch の
// TTY 必須判定で共用する。
func isTerminal(f *os.File) bool {
	return term.IsTerminal(int(f.Fd()))
}
