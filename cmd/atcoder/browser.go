package main

import (
	"os/exec"
	"runtime"
)

// openBrowser は OS 既定のブラウザで URL を開く (best-effort)。
// `test --submit` の提出ページ起動と `status --open` の提出ページ起動が共有する。
// macOS の `open` は既存ウィンドウを前面化しつつ URL を開く (同一 URL のタブ再利用は保証されない)。
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
