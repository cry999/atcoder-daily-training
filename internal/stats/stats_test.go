package stats

import (
	"os"
	"path/filepath"
	"testing"
	"time"
)

// d は YYYY-MM-DD のローカル 0 時を作るヘルパー。
func d(y, m, day int) time.Time {
	return time.Date(y, time.Month(m), day, 0, 0, 0, 0, time.Local)
}

func solve(date time.Time, file string) Solve {
	cat, letter := classify(file)
	return Solve{Date: date, File: file, Category: cat, Letter: letter}
}

func TestClassify(t *testing.T) {
	cases := []struct {
		file     string
		category string
		letter   string
	}{
		{"abc457_d.py", "abc", "d"},
		{"arc180_c.py", "arc", "c"},
		{"ABC457_D.py", "abc", "d"}, // 大文字も正規化
		{"scratch.py", "scratch", "?"},
		{"123.py", "other", "?"},
		{"abc457_xy.py", "abc", "xy"},
	}
	for _, c := range cases {
		cat, letter := classify(c.file)
		if cat != c.category || letter != c.letter {
			t.Errorf("classify(%q) = (%q,%q), want (%q,%q)", c.file, cat, letter, c.category, c.letter)
		}
	}
}

func TestContestID(t *testing.T) {
	cases := []struct {
		file string
		want string
	}{
		{"abc457_d.py", "abc457"},
		{"ABC457_D.py", "abc457"}, // 小文字化
		{"arc180_c.py", "arc180"},
		{"scratch.py", "scratch"}, // 数字無し → 先頭英字
		{"123.py", "other"},       // 先頭英字なし
	}
	for _, c := range cases {
		if got := contestID(c.file); got != c.want {
			t.Errorf("contestID(%q) = %q, want %q", c.file, got, c.want)
		}
	}
}

func TestComputeAllTime(t *testing.T) {
	now := d(2026, 6, 9) // 火曜
	solves := []Solve{
		solve(d(2026, 6, 7), "abc457_d.py"),
		solve(d(2026, 6, 8), "abc457_e.py"),
		solve(d(2026, 6, 8), "arc180_c.py"),
		solve(d(2026, 6, 9), "abc458_a.py"),
		solve(d(2025, 12, 31), "abc400_b.py"), // 前年
	}
	rep := Compute(solves, Options{Period: AllTime, Now: now})

	if rep.Total != 5 {
		t.Errorf("Total = %d, want 5", rep.Total)
	}
	if rep.ActiveDays != 4 {
		t.Errorf("ActiveDays = %d, want 4", rep.ActiveDays)
	}
	// 6/7,6/8,6/9 の 3 連続。今日 6/9 を含むので current = 3。
	if rep.CurrentStreak != 3 {
		t.Errorf("CurrentStreak = %d, want 3", rep.CurrentStreak)
	}
	if rep.LongestStreak != 3 {
		t.Errorf("LongestStreak = %d, want 3", rep.LongestStreak)
	}
	if rep.SeriesKind != "week" {
		t.Errorf("SeriesKind = %q, want week", rep.SeriesKind)
	}
	// カテゴリ: abc=3, arc=1, abc400=abc なので abc=4? 確認: abc457_d, abc457_e, abc458_a, abc400_b → abc=4, arc=1
	if len(rep.Categories) != 2 || rep.Categories[0].Key != "abc" || rep.Categories[0].N != 4 {
		t.Errorf("Categories = %+v, want abc=4 first", rep.Categories)
	}
}

func TestComputeThisMonth(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []Solve{
		solve(d(2026, 6, 7), "abc457_d.py"),
		solve(d(2026, 6, 9), "abc458_a.py"),
		solve(d(2026, 5, 31), "abc450_a.py"), // 先月 → 除外
		solve(d(2025, 6, 9), "abc300_a.py"),  // 前年同月 → 除外
	}
	rep := Compute(solves, Options{Period: ThisMonth, Now: now})
	if rep.Total != 2 {
		t.Errorf("Total = %d, want 2 (this month only)", rep.Total)
	}
	if rep.SeriesKind != "day" {
		t.Errorf("SeriesKind = %q, want day", rep.SeriesKind)
	}
	// 日別は 6/1〜6/9 の 9 日分 (0 件含む)。
	if len(rep.Series) != 9 {
		t.Errorf("len(Series) = %d, want 9", len(rep.Series))
	}
	// current streak: 6/9 のみが連続末尾 (6/8 は無い) → 1。
	if rep.CurrentStreak != 1 {
		t.Errorf("CurrentStreak = %d, want 1", rep.CurrentStreak)
	}
}

func TestComputeThisWeek(t *testing.T) {
	now := d(2026, 6, 10) // 水曜。週は 6/8(月)〜6/14(日)
	solves := []Solve{
		solve(d(2026, 6, 8), "abc457_a.py"),
		solve(d(2026, 6, 9), "abc457_b.py"),
		solve(d(2026, 6, 7), "abc456_a.py"), // 前週日曜 → 除外
	}
	rep := Compute(solves, Options{Period: ThisWeek, Now: now})
	if rep.Total != 2 {
		t.Errorf("Total = %d, want 2", rep.Total)
	}
	// 6/8(月)〜6/10(今日) の 3 日。
	if len(rep.Series) != 3 {
		t.Errorf("len(Series) = %d, want 3", len(rep.Series))
	}
}

func TestCurrentStreakGraceYesterday(t *testing.T) {
	now := d(2026, 6, 9) // 今日は未着手
	solves := []Solve{
		solve(d(2026, 6, 7), "abc457_a.py"),
		solve(d(2026, 6, 8), "abc457_b.py"),
	}
	rep := Compute(solves, Options{Period: AllTime, Now: now})
	// 今日未着手でも前日まで 2 連続 → current = 2。
	if rep.CurrentStreak != 2 {
		t.Errorf("CurrentStreak = %d, want 2 (grace to yesterday)", rep.CurrentStreak)
	}
}

func TestCurrentStreakBroken(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []Solve{
		solve(d(2026, 6, 5), "abc457_a.py"),
		solve(d(2026, 6, 6), "abc457_b.py"),
	}
	rep := Compute(solves, Options{Period: AllTime, Now: now})
	// 直近が 6/6、今日/前日に無い → current = 0、longest = 2。
	if rep.CurrentStreak != 0 {
		t.Errorf("CurrentStreak = %d, want 0", rep.CurrentStreak)
	}
	if rep.LongestStreak != 2 {
		t.Errorf("LongestStreak = %d, want 2", rep.LongestStreak)
	}
}

func TestComputeRollingDays(t *testing.T) {
	now := d(2026, 6, 9) // 火曜
	solves := []Solve{
		solve(d(2026, 6, 9), "abc458_a.py"), // 今日 → 含む
		solve(d(2026, 6, 3), "abc457_d.py"), // 7d 窓のちょうど最初の日 (now-6) → 含む
		solve(d(2026, 6, 2), "abc456_a.py"), // now-7 → 半開区間の下端 → 除外
	}
	// --last 7d: 半開区間 (6/2, 6/9] = 6/3〜6/9 の 7 日。
	rep := Compute(solves, Options{Rolling: &Rolling{N: 7, Unit: UnitDay}, Now: now})
	if rep.Total != 2 {
		t.Errorf("Total = %d, want 2 (6/3 and 6/9 in window, 6/2 excluded)", rep.Total)
	}
	if rep.SeriesKind != "day" {
		t.Errorf("SeriesKind = %q, want day", rep.SeriesKind)
	}
	if len(rep.Series) != 7 { // 6/3..6/9
		t.Errorf("len(Series) = %d, want 7", len(rep.Series))
	}
	if got := rep.Label; got != "last 7 days (2026-06-03–06-09)" {
		t.Errorf("Label = %q", got)
	}
}

func TestComputeRollingWeekEqualsSevenDays(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []Solve{
		solve(d(2026, 6, 3), "abc457_d.py"), // now-6 → 含む
		solve(d(2026, 6, 2), "abc456_a.py"), // now-7 → 除外
	}
	rep := Compute(solves, Options{Rolling: &Rolling{N: 1, Unit: UnitWeek}, Now: now})
	if rep.Total != 1 {
		t.Errorf("Total = %d, want 1 (1w == last 7 days)", rep.Total)
	}
	if len(rep.Series) != 7 {
		t.Errorf("len(Series) = %d, want 7", len(rep.Series))
	}
}

func TestComputeRollingDefaultCount(t *testing.T) {
	now := d(2026, 6, 9)
	// N 省略 (bare "d") は 1 扱い: 窓は今日のみ。
	solves := []Solve{
		solve(d(2026, 6, 9), "abc458_a.py"), // 今日 → 含む
		solve(d(2026, 6, 8), "abc457_e.py"), // 昨日 → 1d の半開区間 (6/8, 6/9] からは除外
	}
	rep := Compute(solves, Options{Rolling: &Rolling{N: 1, Unit: UnitDay}, Now: now})
	if rep.Total != 1 {
		t.Errorf("Total = %d, want 1 (1d window = today only)", rep.Total)
	}
	if len(rep.Series) != 1 {
		t.Errorf("len(Series) = %d, want 1", len(rep.Series))
	}
}

func TestComputeRollingMonth(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []Solve{
		solve(d(2026, 6, 9), "abc458_a.py"),  // 今日 → 含む
		solve(d(2026, 5, 10), "abc450_a.py"), // 半開区間 (5/9, 6/9] の最初の日 → 含む
		solve(d(2026, 5, 9), "abc449_a.py"),  // ちょうど 1 ヶ月前 = 下端 → 除外
	}
	rep := Compute(solves, Options{Rolling: &Rolling{N: 1, Unit: UnitMonth}, Now: now})
	if rep.Total != 2 {
		t.Errorf("Total = %d, want 2 (5/10 and 6/9; 5/9 excluded)", rep.Total)
	}
	if rep.SeriesKind != "day" { // 1 ヶ月 (≤31 日) は日別。
		t.Errorf("SeriesKind = %q, want day", rep.SeriesKind)
	}
	if got := rep.Label; got != "last 1 month (2026-05-10–06-09)" {
		t.Errorf("Label = %q", got)
	}
}

func TestComputeRollingYearWeekly(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []Solve{
		solve(d(2026, 6, 9), "abc458_a.py"),  // 今日 → 含む
		solve(d(2025, 6, 10), "abc300_a.py"), // 半開区間 (2025-06-09, now] の最初 → 含む
		solve(d(2025, 6, 9), "abc299_a.py"),  // ちょうど 1 年前 = 下端 → 除外
	}
	rep := Compute(solves, Options{Rolling: &Rolling{N: 1, Unit: UnitYear}, Now: now})
	if rep.Total != 2 {
		t.Errorf("Total = %d, want 2", rep.Total)
	}
	if rep.SeriesKind != "week" { // 1 年 (>31 日) は週別。
		t.Errorf("SeriesKind = %q, want week", rep.SeriesKind)
	}
}

func TestComputeEmpty(t *testing.T) {
	rep := Compute(nil, Options{Period: AllTime, Now: d(2026, 6, 9)})
	if rep.Total != 0 || rep.ActiveDays != 0 || rep.CurrentStreak != 0 || rep.LongestStreak != 0 {
		t.Errorf("empty Compute = %+v, want all zero", rep)
	}
}

func TestLetterBucketing(t *testing.T) {
	now := d(2026, 6, 9)
	solves := []Solve{
		solve(now, "abc457_a.py"),
		solve(now, "abc457_d.py"),
		solve(now, "scratch.py"), // letter 不明 → "?"
	}
	rep := Compute(solves, Options{Period: AllTime, Now: now})
	// "?" は末尾。
	if last := rep.Letters[len(rep.Letters)-1]; last.Key != "?" {
		t.Errorf("last letter = %q, want ?", last.Key)
	}
}

func TestScan(t *testing.T) {
	root := t.TempDir()
	mustWrite(t, filepath.Join(root, "2026", "06", "09", "abc457_d.py"))
	mustWrite(t, filepath.Join(root, "2026", "06", "08", "arc180_c.py"))
	mustWrite(t, filepath.Join(root, "2026", "06", "09", "notes.txt")) // 非 .py → 無視
	mustWrite(t, filepath.Join(root, "2026", "13", "09", "bad.py"))    // 不正月 → 無視

	solves, err := Scan(root)
	if err != nil {
		t.Fatalf("Scan: %v", err)
	}
	if len(solves) != 2 {
		t.Fatalf("len(solves) = %d, want 2; got %+v", len(solves), solves)
	}
}

func TestScanMissingRoot(t *testing.T) {
	solves, err := Scan(filepath.Join(t.TempDir(), "does-not-exist"))
	if err != nil {
		t.Fatalf("Scan missing root should not error: %v", err)
	}
	if len(solves) != 0 {
		t.Errorf("len(solves) = %d, want 0", len(solves))
	}
}

func mustWrite(t *testing.T, path string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte("print(1)\n"), 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestLetterWeight(t *testing.T) {
	cases := []struct {
		letter string
		want   int
	}{
		{"a", 1},
		{"d", 4},
		{"g", 7},
		{"z", 26},
		{"?", 1},  // 不明
		{"", 1},   // 空
		{"ex", 5}, // 先頭文字のみ ('e')
		{"1", 1},  // 英小文字でない
	}
	for _, c := range cases {
		if got := letterWeight(c.letter); got != c.want {
			t.Errorf("letterWeight(%q) = %d, want %d", c.letter, got, c.want)
		}
	}
}

func TestShadeLevel(t *testing.T) {
	cases := []struct {
		score int
		want  int
	}{
		{0, 0},
		{1, 1}, {3, 1},
		{4, 2}, {7, 2},
		{8, 3}, {12, 3},
		{13, 4}, {100, 4},
		{-5, 0}, // 負も 0 扱い
	}
	for _, c := range cases {
		if got := shadeLevel(c.score); got != c.want {
			t.Errorf("shadeLevel(%d) = %d, want %d", c.score, got, c.want)
		}
	}
}

// cellByDate はグリッドから指定日のセルを探す (見つからなければ ok=false)。
func cellByDate(cols []GraphColumn, day time.Time) (GraphCell, bool) {
	for _, col := range cols {
		for _, c := range col.Cells {
			if c.InRange && c.Date.Equal(day) {
				return c, true
			}
		}
	}
	return GraphCell{}, false
}

func TestBuildGraphWeek(t *testing.T) {
	now := d(2026, 6, 10) // 水曜。週は 6/8(月)〜6/14(日)
	// 6/8: a(1)+d(4)=5 → level 2、6/9: g(7) → level 2、6/10: なし → level 0。
	score := map[time.Time]int{
		d(2026, 6, 8): 5,
		d(2026, 6, 9): 7,
	}
	cols, omitted := buildGraph(score, weekStart(now), now) // ThisWeek の窓開始 = 今週月曜
	if omitted != 0 {
		t.Errorf("omitted = %d, want 0", omitted)
	}
	if len(cols) != 1 {
		t.Fatalf("len(cols) = %d, want 1 (single week column)", len(cols))
	}
	// Mon(6/8)=level2, Tue(6/9)=level2, Wed(6/10)=level0 in range。
	if c := cols[0].Cells[0]; !c.InRange || c.Level != 2 || c.Score != 5 {
		t.Errorf("Mon cell = %+v, want InRange level2 score5", c)
	}
	if c := cols[0].Cells[1]; !c.InRange || c.Level != 2 || c.Score != 7 {
		t.Errorf("Tue cell = %+v, want InRange level2 score7", c)
	}
	if c := cols[0].Cells[2]; !c.InRange || c.Level != 0 {
		t.Errorf("Wed cell = %+v, want InRange level0", c)
	}
	// Thu(6/11)〜Sun は今日より後 → 範囲外パディング。
	if c := cols[0].Cells[3]; c.InRange {
		t.Errorf("Thu cell should be padding (after today), got %+v", c)
	}
}

func TestBuildGraphMonthPadding(t *testing.T) {
	now := d(2026, 6, 10)                                                          // 6/1 は月曜。range = 6/1〜6/10
	cols, _ := buildGraph(map[time.Time]int{d(2026, 6, 1): 4}, d(2026, 6, 1), now) // ThisMonth の窓開始 = 月初
	// 6/1 は月曜なので列頭。6/1 セルは InRange level2。
	if c, ok := cellByDate(cols, d(2026, 6, 1)); !ok || c.Level != 2 {
		t.Errorf("6/1 cell = %+v ok=%v, want level2", c, ok)
	}
	// 6/11 以降 (今日より後) は範囲外。最終列 Sun(6/14) はパディング。
	last := cols[len(cols)-1]
	if last.Cells[6].InRange {
		t.Errorf("last Sun should be padding, got %+v", last.Cells[6])
	}
}

func TestBuildGraphAllTimeCap(t *testing.T) {
	now := d(2026, 6, 10)
	// 60 週前から今日まで毎週 1 件 → 列が maxGraphWeeks (53) を超える。
	score := map[time.Time]int{}
	oldest := weekStart(now).AddDate(0, 0, -7*60)
	for w := oldest; !w.After(now); w = w.AddDate(0, 0, 7) {
		score[w] = 4
	}
	cols, omitted := buildGraph(score, time.Time{}, now) // AllTime: 窓開始ゼロ → 最古の解答日にフォールバック
	if len(cols) != maxGraphWeeks {
		t.Errorf("len(cols) = %d, want %d", len(cols), maxGraphWeeks)
	}
	if omitted <= 0 {
		t.Errorf("omitted = %d, want > 0 (older weeks dropped)", omitted)
	}
	// 残るのは新しい側。最終列の月曜は今週の月曜。
	if last := cols[len(cols)-1].Monday; !last.Equal(weekStart(now)) {
		t.Errorf("last column Monday = %v, want this week's Monday %v", last, weekStart(now))
	}
}

func TestComputeGraphSkipsSeries(t *testing.T) {
	now := d(2026, 6, 10)
	solves := []Solve{solve(d(2026, 6, 8), "abc457_d.py")}
	rep := Compute(solves, Options{Period: ThisWeek, Now: now, Graph: true})
	if len(rep.Graph) == 0 {
		t.Errorf("Graph should be populated when Options.Graph is set")
	}
	if rep.Series != nil {
		t.Errorf("Series should be nil when Graph is set, got %+v", rep.Series)
	}
}
