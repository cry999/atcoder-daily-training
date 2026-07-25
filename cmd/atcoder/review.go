package main

import (
	"errors"
	"flag"
	"os"
	"strings"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/cliargs"
	"github.com/cry999/atcoder-daily-training/internal/config"
	"github.com/cry999/atcoder-daily-training/internal/review"
	"github.com/cry999/atcoder-daily-training/internal/reviewrule"
	"github.com/cry999/atcoder-daily-training/internal/solvestat"
	"github.com/cry999/atcoder-daily-training/internal/stats"
	"golang.org/x/term"
)

// cmdReview は exercise/ を「コンテスト単位」で一覧する。<category> 必須の位置引数で
// 絞り、contest × letter のテーブルに各回の最終解答日を添える。読み取り専用。
func cmdReview(args []string) (int, error) {
	// 位置引数 <category> はフラグと任意順で混在できる (cliargs.Split で分離)。
	flagArgs, positionals := cliargs.Split(args)
	if len(positionals) < 1 {
		return 2, errors.New("category is required (e.g. atcoder review abc)")
	}
	if strings.ToLower(positionals[0]) == "missed" {
		if len(positionals) > 1 {
			return 2, errors.New("review missed does not accept positional arguments")
		}
		return cmdReviewMissed(flagArgs)
	}
	category := strings.ToLower(positionals[0])

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
	if err := flags.Parse(flagArgs); err != nil {
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

func cmdReviewMissed(flagArgs []string) (int, error) {
	flags := flag.NewFlagSet("review missed", flag.ContinueOnError)
	var dateText, check string
	flags.StringVar(&dateText, "date", "", "Practice date to review (YYYY-MM-DD); default is yesterday")
	flags.StringVar(&check, "check", "", "Mark one missed item as reviewed (e.g. abc357_d or abc357/d)")
	flags.SetOutput(os.Stderr)
	if err := flags.Parse(flagArgs); err != nil {
		return 2, err
	}
	if flags.NArg() != 0 {
		return 2, errors.New("review missed does not accept positional arguments")
	}

	now := time.Now().Local()
	target := dayOnly(now.AddDate(0, 0, -1))
	if strings.TrimSpace(dateText) != "" {
		d, err := time.ParseInLocation("2006-01-02", dateText, time.Local)
		if err != nil {
			return 2, errors.New("--date must be YYYY-MM-DD")
		}
		target = d
	}

	cfg, err := config.Load()
	if err != nil {
		return 2, err
	}
	rule, err := reviewrule.Parse(cfg.Review.Missed.Mode, cfg.Review.Missed.Conditions)
	if err != nil {
		return 2, err
	}

	solves, err := stats.Scan("exercise")
	if err != nil {
		return 1, err
	}
	rep := review.BuildMissedWithRule(solves, target, rule)
	if strings.TrimSpace(check) != "" {
		item, err := rep.FindMissed(check)
		if err != nil {
			return 1, err
		}
		patch := solvestat.Empty()
		patch.ReviewedAt = now
		if err := solvestat.Update(item.Path, patch); err != nil {
			return 1, err
		}
		_, _ = os.Stdout.WriteString("reviewed " + item.ID + " (" + item.Path + ")\n")
		return 0, nil
	}
	if err := review.RenderMissed(os.Stdout, rep); err != nil {
		return 1, err
	}
	return 0, nil
}

func dayOnly(t time.Time) time.Time {
	y, m, d := t.Date()
	return time.Date(y, m, d, 0, 0, 0, 0, t.Location())
}
