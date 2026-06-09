package main

import (
	"errors"
	"flag"
	"os"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/review"
	"github.com/cry999/atcoder-daily-training/internal/stats"
	"golang.org/x/term"
)

// cmdReview は exercise/ を「コンテスト単位」で一覧する。<category> 必須の位置引数で
// 絞り、contest × letter のテーブルに各回の最終解答日を添える。読み取り専用。
func cmdReview(args []string) (int, error) {
	// 位置引数 <category> は先頭。フラグより前に来る (status と同じ規約)。
	if len(args) < 1 || strings.HasPrefix(args[0], "-") {
		return 2, errors.New("category is required (e.g. atcoder review abc)")
	}
	category := strings.ToLower(args[0])

	flags := flag.NewFlagSet("review", flag.ContinueOnError)
	var week, month, year bool
	var last string
	flags.BoolVar(&week, "week", false, "Limit to this week (Monday start, including today)")
	flags.BoolVar(&week, "w", false, "Limit to this week (Monday start, including today)")
	flags.BoolVar(&month, "month", false, "Limit to this month")
	flags.BoolVar(&month, "m", false, "Limit to this month")
	flags.BoolVar(&year, "year", false, "Limit to this year")
	flags.BoolVar(&year, "y", false, "Limit to this year")
	flags.StringVar(&last, "last", "", "Rolling window from today: 7d, 2w, 1m, 1y (bare d/w/m/y = 1)")
	flags.StringVar(&last, "l", "", "Rolling window from today: 7d, 2w, 1m, 1y (bare d/w/m/y = 1)")
	flags.SetOutput(os.Stderr)
	if err := flags.Parse(args[1:]); err != nil {
		return 2, err
	}

	// 期間フラグの解決は stats と共有 (排他違反・不正 --last は exit 2)。
	sopts, err := resolveStatsOptions(week, month, year, last)
	if err != nil {
		return 2, err
	}

	// 日付あり (exercise/) と日付なし (<category>/ ツリー) を結合して横断集計する。
	solves, err := stats.Scan("exercise")
	if err != nil {
		return 1, err
	}
	catSolves, err := review.ScanCategoryTree(category)
	if err != nil {
		return 1, err
	}
	solves = append(solves, catSolves...)

	rep := review.Build(solves, review.Options{
		Category: category,
		Period:   sopts.Period,
		Rolling:  sopts.Rolling,
		Now:      time.Now().Local(),
	})

	// TTY かつ 1 件以上ならページに収まるスクロール TUI。非 TTY (パイプ/リダイレクト)
	// や 0 件は従来どおり一括テキスト出力 (スクリプト・テストはこちらを踏む)。
	if rep.Contests > 0 && term.IsTerminal(int(os.Stdout.Fd())) {
		if err := review.RunTUI(rep); err != nil {
			return 1, err
		}
		return 0, nil
	}
	if err := review.Render(os.Stdout, rep); err != nil {
		return 1, err
	}
	return 0, nil
}
