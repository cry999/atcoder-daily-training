// Package stats は日々の練習ツリー (exercise/YYYY/MM/DD/*.py) を集計して、
// 解答数・アクティブ日数・ストリーク・カテゴリ別内訳・時系列を求める。
//
// I/O (Scan) と集計ロジック (Compute) を分離し、Compute は純粋関数にして
// ある。Now を注入できるので「今週/今月/今年」の相対集計も決定的にテスト
// できる (internal/layout の Detect / Letter と同じ流儀)。
//
// 要件詳細: docs/tools/requirements/005-exercise-stats.md
package stats

import (
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"
)

// Period は集計窓。
type Period int

const (
	AllTime Period = iota
	ThisWeek
	ThisMonth
	ThisYear
)

// Solve は 1 ファイル = 1 問の集計単位。
type Solve struct {
	Date     time.Time // パス由来の解答日 (ローカル 0 時)
	File     string    // ベース名 (例 "abc457_d.py")
	Category string    // コンテスト種別 ("abc"/"arc"/…/"other")
	Letter   string    // 問題レター ("a".."g") / 不明は "?"
}

// Options は集計条件。Now がゼロ値なら time.Now().Local() を使う。
type Options struct {
	Period Period
	Now    time.Time
}

// Count は key ごとの件数 (カテゴリ別 / レター別)。
type Count struct {
	Key string
	N   int
}

// Bucket は時系列の 1 区切り (日 or 週)。
type Bucket struct {
	Label string
	N     int
}

// Report は表示に必要な集計済みデータ。
type Report struct {
	Label         string
	Total         int
	ActiveDays    int
	CurrentStreak int
	LongestStreak int
	Categories    []Count
	Letters       []Count
	Series        []Bucket
	SeriesKind    string // "day" / "week"
	SeriesOmitted int    // 週別で切り捨てた古い週数
}

// maxWeekBuckets は週別時系列で表示する最大週数。超過分は SeriesOmitted に回す。
const maxWeekBuckets = 16

// leadingAlphaRE はファイル名先頭の連続英字 (= コンテスト種別) を捕捉する。
var leadingAlphaRE = regexp.MustCompile(`^[a-zA-Z]+`)

// Scan は root (通常 "exercise") 配下の YYYY/MM/DD/*.py を列挙して Solve にする。
// root が無ければ空スライスを返す (エラーにしない)。
func Scan(root string) ([]Solve, error) {
	matches, err := filepath.Glob(filepath.Join(root, "*", "*", "*", "*.py"))
	if err != nil {
		return nil, err
	}
	var solves []Solve
	for _, m := range matches {
		rel, err := filepath.Rel(root, m)
		if err != nil {
			continue
		}
		parts := strings.Split(rel, string(filepath.Separator))
		if len(parts) != 4 {
			continue
		}
		date, ok := parseDate(parts[0], parts[1], parts[2])
		if !ok {
			continue
		}
		base := parts[3]
		cat, letter := classify(base)
		solves = append(solves, Solve{Date: date, File: base, Category: cat, Letter: letter})
	}
	return solves, nil
}

// parseDate は YYYY/MM/DD の各文字列を検証してローカル 0 時の time に変換する。
func parseDate(ys, ms, ds string) (time.Time, bool) {
	y, err1 := strconv.Atoi(ys)
	mo, err2 := strconv.Atoi(ms)
	d, err3 := strconv.Atoi(ds)
	if err1 != nil || err2 != nil || err3 != nil {
		return time.Time{}, false
	}
	if mo < 1 || mo > 12 || d < 1 || d > 31 {
		return time.Time{}, false
	}
	t := time.Date(y, time.Month(mo), d, 0, 0, 0, 0, time.Local)
	// 正規化後にずれていれば不正な日付 (例: 02/31)。
	if t.Year() != y || int(t.Month()) != mo || t.Day() != d {
		return time.Time{}, false
	}
	return t, true
}

// classify はファイル名 (拡張子込み) からカテゴリとレターを導く。
//   - "abc457_d.py" → ("abc", "d")
//   - "arc180_c.py" → ("arc", "c")
//   - "scratch.py"  → ("scratch", "?")  (レター不明)
//   - "123.py"      → ("other", "?")    (先頭英字なし)
func classify(file string) (category, letter string) {
	base := strings.TrimSuffix(file, filepath.Ext(file))
	category = "other"
	if m := leadingAlphaRE.FindString(base); m != "" {
		category = strings.ToLower(m)
	}
	letter = "?"
	if i := strings.LastIndex(base, "_"); i >= 0 && i+1 < len(base) {
		letter = strings.ToLower(base[i+1:])
	}
	return category, letter
}

// Compute は Solve 群を Options に従って集計する純粋関数。
func Compute(solves []Solve, opts Options) Report {
	now := opts.Now
	if now.IsZero() {
		now = time.Now().Local()
	}
	now = dayOf(now)

	// 期間窓で絞る。
	var in []Solve
	for _, s := range solves {
		if inWindow(s.Date, now, opts.Period) {
			in = append(in, s)
		}
	}

	rep := Report{Label: periodLabel(opts.Period, now)}
	rep.Total = len(in)

	// カテゴリ別・レター別・日別件数を集計。
	catN := map[string]int{}
	letN := map[string]int{}
	dayN := map[time.Time]int{} // 0 時 time → 件数
	for _, s := range in {
		catN[s.Category]++
		letN[s.Letter]++
		dayN[dayOf(s.Date)]++
	}
	rep.ActiveDays = len(dayN)
	rep.Categories = sortedByCountDesc(catN)
	rep.Letters = sortedByLetter(letN)

	// ストリーク (窓内のアクティブ日集合に対して)。
	days := make([]time.Time, 0, len(dayN))
	for d := range dayN {
		days = append(days, d)
	}
	rep.CurrentStreak = currentStreak(days, now)
	rep.LongestStreak = longestStreak(days)

	// 時系列。
	if opts.Period == ThisWeek || opts.Period == ThisMonth {
		rep.SeriesKind = "day"
		rep.Series = dailySeries(dayN, opts.Period, now)
	} else {
		rep.SeriesKind = "week"
		rep.Series, rep.SeriesOmitted = weeklySeries(in)
	}
	return rep
}

// dayOf は時刻を捨ててローカル 0 時に丸める。
func dayOf(t time.Time) time.Time {
	y, m, d := t.Date()
	return time.Date(y, m, d, 0, 0, 0, 0, t.Location())
}

// weekStart は t を含む週の月曜 0 時を返す。
func weekStart(t time.Time) time.Time {
	t = dayOf(t)
	delta := (int(t.Weekday()) + 6) % 7 // Sunday=0 を月曜起点に補正
	return t.AddDate(0, 0, -delta)
}

// inWindow は d が now 基準の期間窓に入るか判定する。
func inWindow(d, now time.Time, p Period) bool {
	d = dayOf(d)
	switch p {
	case ThisYear:
		return d.Year() == now.Year()
	case ThisMonth:
		return d.Year() == now.Year() && d.Month() == now.Month()
	case ThisWeek:
		start := weekStart(now)
		end := start.AddDate(0, 0, 6)
		return !d.Before(start) && !d.After(end)
	default: // AllTime
		return true
	}
}

func periodLabel(p Period, now time.Time) string {
	switch p {
	case ThisWeek:
		s := weekStart(now)
		e := s.AddDate(0, 0, 6)
		return "this week (" + s.Format("2006-01-02") + "–" + e.Format("01-02") + ")"
	case ThisMonth:
		return "this month (" + now.Format("2006-01") + ")"
	case ThisYear:
		return "this year (" + now.Format("2006") + ")"
	default:
		return "all time"
	}
}

// currentStreak は今日 (無ければ前日) を起点に連続アクティブ日数を遡って数える。
func currentStreak(days []time.Time, now time.Time) int {
	set := dateSet(days)
	anchor := now
	if !set[anchor] {
		anchor = anchor.AddDate(0, 0, -1) // 今日未着手でも前日まで続いていれば継続中とみなす
	}
	if !set[anchor] {
		return 0
	}
	n := 0
	for set[anchor] {
		n++
		anchor = anchor.AddDate(0, 0, -1)
	}
	return n
}

// longestStreak は連続アクティブ日の最長を返す。
func longestStreak(days []time.Time) int {
	if len(days) == 0 {
		return 0
	}
	sorted := append([]time.Time(nil), days...)
	sort.Slice(sorted, func(i, j int) bool { return sorted[i].Before(sorted[j]) })
	best, cur := 1, 1
	for i := 1; i < len(sorted); i++ {
		if sorted[i].Equal(sorted[i-1].AddDate(0, 0, 1)) {
			cur++
		} else {
			cur = 1
		}
		if cur > best {
			best = cur
		}
	}
	return best
}

func dateSet(days []time.Time) map[time.Time]bool {
	s := make(map[time.Time]bool, len(days))
	for _, d := range days {
		s[dayOf(d)] = true
	}
	return s
}

// dailySeries は窓の開始日〜今日の各日を 0 件含めて並べる (week/month 用)。
func dailySeries(dayN map[time.Time]int, p Period, now time.Time) []Bucket {
	var start time.Time
	switch p {
	case ThisWeek:
		start = weekStart(now)
	case ThisMonth:
		start = time.Date(now.Year(), now.Month(), 1, 0, 0, 0, 0, now.Location())
	default:
		start = now
	}
	var out []Bucket
	for d := start; !d.After(now); d = d.AddDate(0, 0, 1) {
		out = append(out, Bucket{Label: d.Format("2006-01-02"), N: dayN[d]})
	}
	return out
}

// weeklySeries は解答のあった週 (月曜始まり) を新しい順に最大 maxWeekBuckets 件返す。
// 切り捨てた古い週数を omitted で返す。出力自体は古い順 (昇順) に並べる。
func weeklySeries(in []Solve) (buckets []Bucket, omitted int) {
	weekN := map[time.Time]int{}
	for _, s := range in {
		weekN[weekStart(s.Date)]++
	}
	weeks := make([]time.Time, 0, len(weekN))
	for w := range weekN {
		weeks = append(weeks, w)
	}
	sort.Slice(weeks, func(i, j int) bool { return weeks[i].Before(weeks[j]) })
	if len(weeks) > maxWeekBuckets {
		omitted = len(weeks) - maxWeekBuckets
		weeks = weeks[len(weeks)-maxWeekBuckets:]
	}
	for _, w := range weeks {
		buckets = append(buckets, Bucket{Label: w.Format("2006-01-02") + "+", N: weekN[w]})
	}
	return buckets, omitted
}

// sortedByCountDesc は件数の多い順、同数はキー名昇順で Count を並べる。
func sortedByCountDesc(m map[string]int) []Count {
	out := make([]Count, 0, len(m))
	for k, n := range m {
		out = append(out, Count{Key: k, N: n})
	}
	sort.Slice(out, func(i, j int) bool {
		if out[i].N != out[j].N {
			return out[i].N > out[j].N
		}
		return out[i].Key < out[j].Key
	})
	return out
}

// sortedByLetter はレター昇順で並べる ("?" は末尾)。
func sortedByLetter(m map[string]int) []Count {
	out := make([]Count, 0, len(m))
	for k, n := range m {
		out = append(out, Count{Key: k, N: n})
	}
	sort.Slice(out, func(i, j int) bool {
		ai, bi := out[i].Key == "?", out[j].Key == "?"
		if ai != bi {
			return bi // "?" を後ろへ
		}
		return out[i].Key < out[j].Key
	})
	return out
}
