package main

import (
	"github.com/cry999/atcoder-daily-training/internal/testexec"
	"github.com/cry999/atcoder-daily-training/internal/ui"
)

// chatProblemURL は :open で開く問題ページ URL を決める。meta.toml に取得元 URL が
// 記録されていればそれを優先し、無ければ contest/task から標準 URL を組み立てる。
func chatProblemURL(contest, task string) string {
	if m, err := testexec.LoadMeta(contest, task); err == nil && m.URL != "" {
		return m.URL
	}
	return testexec.DefaultTaskURL(contest, task)
}

// chatOpenFunc は chat の :open フック。ブラウザ起動失敗は URL と一緒に UI へ返し、
// chat 自体は継続させる。
func chatOpenFunc(contest, task string) ui.OpenFunc {
	return func() ui.OpenResult {
		url := chatProblemURL(contest, task)
		err := openBrowser(url)
		return ui.OpenResult{URL: url, Opened: err == nil, Err: err}
	}
}
