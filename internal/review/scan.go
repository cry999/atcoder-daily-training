package review

import (
	"path/filepath"
	"regexp"
	"strings"

	"github.com/cry999/atcoder-daily-training/internal/stats"
)

// catDirRE は contest dir 名がコンテストらしいか (数字を含むか) を判定する。
// "447" / "0001-beta" は通すが、"templates" のような数字なし dir は弾く。
var catDirRE = regexp.MustCompile(`[0-9]`)

// catLetterRE はカテゴリツリーで letter として許すファイル名 stem (1〜2 文字の英小文字)。
// "d" / "ex" は通すが、"generate_d_testcase" のような補助スクリプトは弾く。
var catLetterRE = regexp.MustCompile(`^[a-z]{1,2}$`)

// ScanCategoryTree は <category>/<num>/<letter>.py を **日付なし** solve として列挙する。
// contest_id = <category> + <num>。<num> が数字でない dir、letter 形でないファイルは無視。
// <category> dir が無ければ空スライスを返す (エラーにしない)。Date はゼロ値 (日付なし)。
func ScanCategoryTree(category string) ([]stats.Solve, error) {
	matches, err := filepath.Glob(filepath.Join(category, "*", "*.py"))
	if err != nil {
		return nil, err
	}
	var solves []stats.Solve
	for _, m := range matches {
		rel, err := filepath.Rel(category, m)
		if err != nil {
			continue
		}
		parts := strings.Split(rel, string(filepath.Separator))
		if len(parts) != 2 {
			continue
		}
		num := parts[0]
		if !catDirRE.MatchString(num) {
			continue
		}
		letter := strings.ToLower(strings.TrimSuffix(parts[1], filepath.Ext(parts[1])))
		if !catLetterRE.MatchString(letter) {
			continue
		}
		solves = append(solves, stats.Solve{
			File:     parts[1],
			Category: category,
			Contest:  category + num,
			Letter:   letter,
			// Date: ゼロ値 = 日付なし
		})
	}
	return solves, nil
}
