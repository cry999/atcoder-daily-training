package review

import (
	"reflect"
	"strings"
	"testing"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/stats"
)

// d は YYYY-MM-DD のローカル 0 時を作るヘルパー。
func d(y, m, day int) time.Time {
	return time.Date(y, time.Month(m), day, 0, 0, 0, 0, time.Local)
}

// sv は contest_id とレターから stats.Solve を作る (category は contest 先頭英字)。
func sv(date time.Time, contest, letter string) stats.Solve {
	cat := strings.TrimRight(contest, "0123456789")
	return stats.Solve{Date: date, File: contest + "_" + letter + ".py", Category: cat, Contest: contest, Letter: letter}
}

func TestBuildColumnsABCFixed(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []stats.Solve{sv(d(2026, 6, 1), "abc458", "d")}
	rep := Build(solves, Options{Category: "abc", Now: now})
	want := []string{"a", "b", "c", "d", "e", "f", "g"}
	if !reflect.DeepEqual(rep.Columns, want) {
		t.Errorf("Columns = %v, want fixed a–g %v", rep.Columns, want)
	}
}

func TestBuildColumnsABCExtraLetter(t *testing.T) {
	now := d(2026, 6, 9)
	// a–g 外の letter "ex" と "?" は末尾に追加される ("?" が最後)。
	solves := []stats.Solve{
		sv(now, "abc458", "d"),
		sv(now, "abc458", "ex"),
		sv(now, "abc457", "?"),
	}
	rep := Build(solves, Options{Category: "abc", Now: now})
	want := []string{"a", "b", "c", "d", "e", "f", "g", "ex", "?"}
	if !reflect.DeepEqual(rep.Columns, want) {
		t.Errorf("Columns = %v, want %v", rep.Columns, want)
	}
}

func TestBuildColumnsNonABCUnion(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []stats.Solve{
		sv(now, "arc180", "f"),
		sv(now, "arc179", "c"),
	}
	rep := Build(solves, Options{Category: "arc", Now: now})
	want := []string{"c", "f"} // 固定列なし、解いた letter の和集合 (昇順)
	if !reflect.DeepEqual(rep.Columns, want) {
		t.Errorf("Columns = %v, want %v", rep.Columns, want)
	}
}

func TestBuildGroupingAndLastSolved(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []stats.Solve{
		sv(d(2026, 6, 7), "abc457", "d"),
		sv(d(2026, 6, 8), "abc457", "e"), // 同一 contest の別 letter
	}
	rep := Build(solves, Options{Category: "abc", Now: now})
	if rep.Contests != 1 {
		t.Fatalf("Contests = %d, want 1 (grouped)", rep.Contests)
	}
	row := rep.Rows[0]
	if len(row.Solved) != 2 || row.Solved["d"].IsZero() || row.Solved["e"].IsZero() {
		t.Errorf("Solved = %v, want d and e", row.Solved)
	}
	if !row.LastSolved.Equal(d(2026, 6, 8)) {
		t.Errorf("LastSolved = %v, want 2026-06-08 (max)", row.LastSolved)
	}
}

func TestBuildSortContestDesc(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []stats.Solve{
		sv(now, "abc456", "d"),
		sv(now, "abc458", "d"),
		sv(now, "abc457", "d"),
	}
	rep := Build(solves, Options{Category: "abc", Now: now})
	got := []string{rep.Rows[0].Contest, rep.Rows[1].Contest, rep.Rows[2].Contest}
	want := []string{"abc458", "abc457", "abc456"}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("order = %v, want descending %v", got, want)
	}
}

func TestBuildPeriodFilter(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []stats.Solve{
		sv(d(2026, 6, 7), "abc457", "d"), // 今月
		sv(d(2026, 5, 31), "abc456", "d"), // 先月 → --month で除外
	}
	rep := Build(solves, Options{Category: "abc", Period: stats.ThisMonth, Now: now})
	if rep.Contests != 1 || rep.Rows[0].Contest != "abc457" {
		t.Errorf("ThisMonth Rows = %+v, want only abc457", rep.Rows)
	}
	if rep.AllTime {
		t.Errorf("AllTime = true, want false for ThisMonth")
	}
}

func TestBuildEmptyCategory(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []stats.Solve{sv(now, "abc458", "d")}
	rep := Build(solves, Options{Category: "arc", Now: now})
	if rep.Contests != 0 || rep.Solves != 0 {
		t.Errorf("arc filter on abc-only tree = %d contests / %d solves, want 0/0", rep.Contests, rep.Solves)
	}
	if !rep.AllTime {
		t.Errorf("AllTime = false, want true (no period flag)")
	}
}

func TestRecencyLevel(t *testing.T) {
	now := d(2026, 6, 9)
	cases := []struct {
		daysAgo int
		want    int
	}{
		{0, 4}, {7, 4}, // ≤7 → 4
		{8, 3}, {30, 3}, // ≤30 → 3
		{31, 2}, {90, 2}, // ≤90 → 2
		{91, 1}, {365, 1}, // それ超 → 1
	}
	for _, c := range cases {
		solved := now.AddDate(0, 0, -c.daysAgo)
		if got := recencyLevel(solved, now); got != c.want {
			t.Errorf("recencyLevel(%d days ago) = %d, want %d", c.daysAgo, got, c.want)
		}
	}
}
