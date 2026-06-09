package main

import (
	"errors"
	"flag"
	"os"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/stats"
)

// cmdStats は exercise/YYYY/MM/DD/*.py を集計して練習統計をテーブル表示する。
// 読み取り専用で、リポジトリには一切書き込まない。
func cmdStats(args []string) (int, error) {
	flags := flag.NewFlagSet("stats", flag.ContinueOnError)
	var week, month, year bool
	flags.BoolVar(&week, "week", false, "Limit to this week (Monday start, including today)")
	flags.BoolVar(&week, "w", false, "Limit to this week (Monday start, including today)")
	flags.BoolVar(&month, "month", false, "Limit to this month")
	flags.BoolVar(&month, "m", false, "Limit to this month")
	flags.BoolVar(&year, "year", false, "Limit to this year")
	flags.BoolVar(&year, "y", false, "Limit to this year")
	flags.SetOutput(os.Stderr)
	if err := flags.Parse(args); err != nil {
		return 2, err
	}

	period, err := resolvePeriod(week, month, year)
	if err != nil {
		return 2, err
	}

	solves, err := stats.Scan("exercise")
	if err != nil {
		return 1, err
	}

	rep := stats.Compute(solves, stats.Options{Period: period, Now: time.Now().Local()})
	if err := stats.Render(os.Stdout, rep); err != nil {
		return 1, err
	}
	return 0, nil
}

// resolvePeriod は排他フラグ --week/--month/--year を Period に変換する。
// 2 つ以上指定はエラー (exit 2)。
func resolvePeriod(week, month, year bool) (stats.Period, error) {
	n := 0
	for _, b := range []bool{week, month, year} {
		if b {
			n++
		}
	}
	if n > 1 {
		return stats.AllTime, errors.New("only one of --week/--month/--year may be set")
	}
	switch {
	case week:
		return stats.ThisWeek, nil
	case month:
		return stats.ThisMonth, nil
	case year:
		return stats.ThisYear, nil
	default:
		return stats.AllTime, nil
	}
}
