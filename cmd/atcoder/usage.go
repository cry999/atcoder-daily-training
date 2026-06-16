package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"sort"
	"text/tabwriter"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/usagelog"
)

// cmdUsage はローカルに記録した CLI 利用イベント (usagelog) を読み、コマンド別に
// 集計して表示する。読み取り専用・オフライン・副作用なし。要件 037。
func cmdUsage(args []string) (int, error) {
	flags := flag.NewFlagSet("usage", flag.ContinueOnError)
	flags.SetOutput(os.Stderr)
	var withFlags bool
	var asJSON bool
	flags.BoolVar(&withFlags, "flags", false, "コマンド別にフラグ利用回数の内訳も表示する")
	flags.BoolVar(&asJSON, "json", false, "集計結果を JSON で出力する")
	if err := flags.Parse(args); err != nil {
		return 2, nil // フラグ誤り
	}

	path := usagelog.Path()
	f, err := os.Open(path)
	if err != nil {
		if os.IsNotExist(err) {
			fmt.Println("(まだ利用記録がありません)")
			return 0, nil
		}
		return 1, fmt.Errorf("利用ログを開けません: %w", err)
	}
	defer f.Close()

	stats, err := usagelog.Aggregate(f)
	if err != nil {
		return 1, fmt.Errorf("利用ログの集計に失敗しました: %w", err)
	}
	if len(stats) == 0 {
		fmt.Println("(まだ利用記録がありません)")
		return 0, nil
	}

	if asJSON {
		return usageJSON(stats)
	}
	usageTable(stats, withFlags)
	return 0, nil
}

// usageTable はコマンド別集計を整形した表で出力する。
func usageTable(stats []usagelog.Stat, withFlags bool) {
	w := tabwriter.NewWriter(os.Stdout, 0, 2, 2, ' ', 0)
	fmt.Fprintln(w, "Command\tCount\tTotal\tAvg\tLast")
	var total int
	for _, s := range stats {
		total += s.Count
		fmt.Fprintf(w, "%s\t%d\t%s\t%s\t%s\n",
			s.Cmd, s.Count,
			formatTotalDur(time.Duration(s.TotalMs)*time.Millisecond),
			formatTotalDur(time.Duration(s.AvgMs())*time.Millisecond),
			formatLast(s.Last),
		)
		if withFlags {
			for _, fl := range sortFlags(s.Flags) {
				fmt.Fprintf(w, "    %s\t%d\t\t\t\n", fl.name, fl.count)
			}
		}
	}
	w.Flush()
	fmt.Printf("\n合計 %d 回 / %d コマンド\n", total, len(stats))
}

// usageJSON は集計結果を機械可読な JSON で出力する。
func usageJSON(stats []usagelog.Stat) (int, error) {
	type flagCount struct {
		Flag  string `json:"flag"`
		Count int    `json:"count"`
	}
	type row struct {
		Cmd     string      `json:"cmd"`
		Count   int         `json:"count"`
		TotalMs int64       `json:"total_ms"`
		AvgMs   int64       `json:"avg_ms"`
		Last    time.Time   `json:"last"`
		Flags   []flagCount `json:"flags"`
	}
	rows := make([]row, 0, len(stats))
	for _, s := range stats {
		fc := make([]flagCount, 0, len(s.Flags))
		for _, fl := range sortFlags(s.Flags) {
			fc = append(fc, flagCount{Flag: fl.name, Count: fl.count})
		}
		rows = append(rows, row{
			Cmd: s.Cmd, Count: s.Count, TotalMs: s.TotalMs,
			AvgMs: s.AvgMs(), Last: s.Last, Flags: fc,
		})
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(rows); err != nil {
		return 1, err
	}
	return 0, nil
}

type flagStat struct {
	name  string
	count int
}

// sortFlags はフラグ別 count を回数降順 (同数は名前昇順) に整列する。
func sortFlags(m map[string]int) []flagStat {
	out := make([]flagStat, 0, len(m))
	for k, v := range m {
		out = append(out, flagStat{k, v})
	}
	sort.Slice(out, func(i, j int) bool {
		if out[i].count != out[j].count {
			return out[i].count > out[j].count
		}
		return out[i].name < out[j].name
	})
	return out
}

// formatTotalDur は所要時間を人間向けに整える。
//
//	>= 1h : "2h11m"
//	>= 1m : "18m02s"
//	>= 1s : "7.6s"
//	< 1s  : "120ms" / "0"
func formatTotalDur(d time.Duration) string {
	if d <= 0 {
		return "0"
	}
	switch {
	case d >= time.Hour:
		h := d / time.Hour
		m := (d % time.Hour) / time.Minute
		return fmt.Sprintf("%dh%02dm", h, m)
	case d >= time.Minute:
		m := d / time.Minute
		s := (d % time.Minute) / time.Second
		return fmt.Sprintf("%dm%02ds", m, s)
	case d >= time.Second:
		return fmt.Sprintf("%.1fs", d.Seconds())
	default:
		return fmt.Sprintf("%dms", d.Milliseconds())
	}
}

// formatLast は最終利用日時を "2006-01-02 15:04" で表す (ゼロ値は "-")。
func formatLast(t time.Time) string {
	if t.IsZero() {
		return "-"
	}
	return t.Local().Format("2006-01-02 15:04")
}
