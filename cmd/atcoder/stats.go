package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/stats"
)

// cmdStats は exercise/YYYY/MM/DD/*.py を集計して練習統計をテーブル表示する。
// 読み取り専用で、リポジトリには一切書き込まない。
func cmdStats(args []string) (int, error) {
	flags := flag.NewFlagSet("stats", flag.ContinueOnError)
	var week, month, year, graph bool
	var last string
	flags.BoolVar(&week, "week", false, "Limit to this week (Monday start, including today)")
	flags.BoolVar(&week, "w", false, "Limit to this week (Monday start, including today)")
	flags.BoolVar(&month, "month", false, "Limit to this month")
	flags.BoolVar(&month, "m", false, "Limit to this month")
	flags.BoolVar(&year, "year", false, "Limit to this year")
	flags.BoolVar(&year, "y", false, "Limit to this year")
	flags.StringVar(&last, "last", "", "Rolling window from today: 7d, 2w, 1m, 1y (bare d/w/m/y = 1)")
	flags.StringVar(&last, "l", "", "Rolling window from today: 7d, 2w, 1m, 1y (bare d/w/m/y = 1)")
	flags.BoolVar(&graph, "graph", false, "Render the time series as a GitHub-style contribution graph")
	flags.BoolVar(&graph, "g", false, "Render the time series as a GitHub-style contribution graph")
	flags.SetOutput(os.Stderr)
	if err := flags.Parse(args); err != nil {
		return 2, err
	}

	opts, err := resolveStatsOptions(week, month, year, last)
	if err != nil {
		return 2, err
	}
	opts.Now = time.Now().Local()
	opts.Graph = graph

	solves, err := stats.Scan("exercise")
	if err != nil {
		return 1, err
	}

	rep := stats.Compute(solves, opts)
	if err := stats.Render(os.Stdout, rep); err != nil {
		return 1, err
	}
	return 0, nil
}

// resolveStatsOptions は排他フラグ --week/--month/--year/--last を Options に変換する。
// 2 つ以上指定、または --last の値が不正なときはエラー (exit 2)。
func resolveStatsOptions(week, month, year bool, last string) (stats.Options, error) {
	n := 0
	for _, b := range []bool{week, month, year, last != ""} {
		if b {
			n++
		}
	}
	if n > 1 {
		return stats.Options{}, errors.New("only one of --week/--month/--year/--last may be set")
	}
	switch {
	case last != "":
		r, err := parseDur(last)
		if err != nil {
			return stats.Options{}, err
		}
		return stats.Options{Rolling: &r}, nil
	case week:
		return stats.Options{Period: stats.ThisWeek}, nil
	case month:
		return stats.Options{Period: stats.ThisMonth}, nil
	case year:
		return stats.Options{Period: stats.ThisYear}, nil
	default:
		return stats.Options{Period: stats.AllTime}, nil
	}
}

// durRE は --last の値 "<N><unit>" を捕捉する。N 省略は 1、単位は d/w/m/y。
var durRE = regexp.MustCompile(`^([0-9]*)([dwmyDWMY])$`)

// parseDur は "7d" / "2w" / "1m" / "y" 等を stats.Rolling に変換する。
// 数値を省くと 1 扱い。文法外・0 以下はエラー (exit 2)。
func parseDur(s string) (stats.Rolling, error) {
	m := durRE.FindStringSubmatch(s)
	if m == nil {
		return stats.Rolling{}, fmt.Errorf("invalid --last value %q (expected like 7d, 2w, 1m, 1y)", s)
	}
	n := 1
	if m[1] != "" {
		var err error
		n, err = strconv.Atoi(m[1])
		if err != nil || n <= 0 {
			return stats.Rolling{}, fmt.Errorf("invalid --last value %q (count must be a positive integer)", s)
		}
	}
	var unit stats.Unit
	switch m[2] {
	case "d", "D":
		unit = stats.UnitDay
	case "w", "W":
		unit = stats.UnitWeek
	case "m", "M":
		unit = stats.UnitMonth
	case "y", "Y":
		unit = stats.UnitYear
	}
	return stats.Rolling{N: n, Unit: unit}, nil
}
