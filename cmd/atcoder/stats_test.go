package main

import (
	"testing"

	"github.com/cry999/atcoder-daily-training/internal/stats"
)

func TestParseDur(t *testing.T) {
	ok := []struct {
		in   string
		want stats.Rolling
	}{
		{"d", stats.Rolling{N: 1, Unit: stats.UnitDay}},
		{"7d", stats.Rolling{N: 7, Unit: stats.UnitDay}},
		{"w", stats.Rolling{N: 1, Unit: stats.UnitWeek}},
		{"2w", stats.Rolling{N: 2, Unit: stats.UnitWeek}},
		{"m", stats.Rolling{N: 1, Unit: stats.UnitMonth}},
		{"3m", stats.Rolling{N: 3, Unit: stats.UnitMonth}},
		{"y", stats.Rolling{N: 1, Unit: stats.UnitYear}},
		{"1y", stats.Rolling{N: 1, Unit: stats.UnitYear}},
		{"Y", stats.Rolling{N: 1, Unit: stats.UnitYear}}, // 大文字も受ける
	}
	for _, c := range ok {
		got, err := parseDur(c.in)
		if err != nil {
			t.Errorf("parseDur(%q) error: %v", c.in, err)
			continue
		}
		if got != c.want {
			t.Errorf("parseDur(%q) = %+v, want %+v", c.in, got, c.want)
		}
	}

	bad := []string{"", "0d", "1x", "abc", "7", "d7", "-1d", "1.5d", "7dd"}
	for _, in := range bad {
		if _, err := parseDur(in); err == nil {
			t.Errorf("parseDur(%q) = nil error, want error", in)
		}
	}
}

func TestResolveStatsOptionsExclusive(t *testing.T) {
	// 2 つ以上の期間指定はエラー (exit 2 相当)。
	if _, err := resolveStatsOptions(true, false, false, "7d"); err == nil {
		t.Error("--week --last 7d should be rejected")
	}
	if _, err := resolveStatsOptions(true, true, false, ""); err == nil {
		t.Error("--week --month should be rejected")
	}
	// 単独の --last は Rolling になる。
	opts, err := resolveStatsOptions(false, false, false, "1m")
	if err != nil {
		t.Fatalf("--last 1m error: %v", err)
	}
	if opts.Rolling == nil || opts.Rolling.Unit != stats.UnitMonth || opts.Rolling.N != 1 {
		t.Errorf("opts.Rolling = %+v, want {1 month}", opts.Rolling)
	}
	// 無指定は AllTime。
	opts, err = resolveStatsOptions(false, false, false, "")
	if err != nil || opts.Rolling != nil || opts.Period != stats.AllTime {
		t.Errorf("no flags = %+v (err %v), want AllTime", opts, err)
	}
}
