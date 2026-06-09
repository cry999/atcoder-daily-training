package review

import (
	"os"
	"path/filepath"
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

// svU は日付なし (カテゴリツリー由来) の stats.Solve を作る。
func svU(contest, letter string) stats.Solve {
	cat := strings.TrimRight(contest, "0123456789")
	return stats.Solve{File: letter + ".py", Category: cat, Contest: contest, Letter: letter}
}

func TestBuildMergeDatedPreference(t *testing.T) {
	now := d(2026, 6, 9)
	// exercise: abc457 の d を 6/7 に (日付あり)。category: abc457 の a と d (日付なし)。
	solves := []stats.Solve{
		sv(d(2026, 6, 7), "abc457", "d"),
		svU("abc457", "a"),
		svU("abc457", "d"), // d は dated と重複 → dated 優先
	}
	rep := Build(solves, Options{Category: "abc", Now: now})
	if rep.Contests != 1 {
		t.Fatalf("Contests = %d, want 1", rep.Contests)
	}
	row := rep.Rows[0]
	if got := row.Solved["d"]; !got.Equal(d(2026, 6, 7)) {
		t.Errorf("Solved[d] = %v, want dated 2026-06-07 (dated preferred over undated)", got)
	}
	if got, ok := row.Solved["a"]; !ok || !got.IsZero() {
		t.Errorf("Solved[a] = (%v,%v), want zero (undated)", got, ok)
	}
	if !row.LastSolved.Equal(d(2026, 6, 7)) {
		t.Errorf("LastSolved = %v, want 2026-06-07 (dated only)", row.LastSolved)
	}
}

func TestBuildAllUndatedNoLastSolved(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []stats.Solve{svU("abc461", "a"), svU("abc461", "b")}
	rep := Build(solves, Options{Category: "abc", Now: now})
	if rep.Contests != 1 {
		t.Fatalf("Contests = %d, want 1", rep.Contests)
	}
	if !rep.Rows[0].LastSolved.IsZero() {
		t.Errorf("LastSolved = %v, want zero (all undated → '—')", rep.Rows[0].LastSolved)
	}
}

func TestBuildUndatedExcludedByPeriod(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []stats.Solve{
		sv(d(2026, 6, 7), "abc457", "d"), // 今月 dated
		svU("abc461", "a"),               // 日付なし → 期間フィルタで除外
	}
	rep := Build(solves, Options{Category: "abc", Period: stats.ThisMonth, Now: now})
	if rep.Contests != 1 || rep.Rows[0].Contest != "abc457" {
		t.Errorf("ThisMonth Rows = %+v, want only abc457 (undated excluded)", rep.Rows)
	}
}

func TestScanCategoryTree(t *testing.T) {
	t.Chdir(t.TempDir())
	mk := func(parts ...string) {
		rel := filepath.Join(parts...)
		if err := os.MkdirAll(filepath.Dir(rel), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(rel, []byte("print(1)\n"), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	mk("abc", "447", "d.py")
	mk("abc", "447", "e.py")
	mk("abc", "424", "generate_d_testcase.py") // letter 形でない → 無視
	mk("abc", "templates", "x.py")             // 数字なし dir → 無視
	mk("awc", "0001-beta", "a.py")             // 非数字 contest dir も可

	solves, err := ScanCategoryTree("abc")
	if err != nil {
		t.Fatalf("ScanCategoryTree: %v", err)
	}
	if len(solves) != 2 {
		t.Fatalf("len(solves) = %d, want 2 (d,e); got %+v", len(solves), solves)
	}
	for _, s := range solves {
		if s.Contest != "abc447" || s.Category != "abc" || !s.Date.IsZero() {
			t.Errorf("solve = %+v, want contest abc447 / category abc / zero date", s)
		}
	}

	awc, _ := ScanCategoryTree("awc")
	if len(awc) != 1 || awc[0].Contest != "awc0001-beta" {
		t.Errorf("awc solves = %+v, want one awc0001-beta", awc)
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
