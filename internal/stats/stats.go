// Package stats は日々の練習ツリー (exercise/YYYY/MM/DD/*.py) を集計して、
// 解答数・アクティブ日数・ストリーク・カテゴリ別内訳・時系列を求める。
//
// I/O (Scan) と集計ロジック (Compute) を分離し、Compute は純粋関数にして
// ある。Now を注入できるので「今週/今月/今年」の暦窓も「今日から N 単位分」の
// ローリング窓も決定的にテストできる (internal/layout の Detect / Letter と
// 同じ流儀)。
//
// 要件詳細: docs/tools/requirements/005-exercise-stats.md (基本),
// docs/tools/requirements/010-stats-rolling-window.md (ローリング期間)。
package stats

import (
	"fmt"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"
)

// Period は暦ベースの集計窓。
type Period int

const (
	AllTime Period = iota
	ThisWeek
	ThisMonth
	ThisYear
)

// Unit はローリング窓 (Rolling) の単位。
type Unit int

const (
	UnitDay Unit = iota
	UnitWeek
	UnitMonth
	UnitYear
)

// Rolling は「今日から N 単位分」のローリング窓指定 (半開区間 (start, now])。
type Rolling struct {
	N    int
	Unit Unit
}

// Solve は 1 ファイル = 1 問の集計単位。
type Solve struct {
	Date     time.Time // パス由来の解答日 (ローカル 0 時)
	File     string    // ベース名 (例 "abc457_d.py")
	Category string    // コンテスト種別 ("abc"/"arc"/…/"other")
	Contest  string    // contest_id ("abc457")。先頭英字 + 数字。数字無しは先頭英字
	Letter   string    // 問題レター ("a".."g") / 不明は "?"
}

// Options は集計条件。Now がゼロ値なら time.Now().Local() を使う。
// Rolling が非 nil なら Period より優先してローリング窓で集計する。
type Options struct {
	Period  Period
	Rolling *Rolling
	Now     time.Time
	Graph   bool // true で時系列をバーではなく草グリッド (contribution graph) として構築する
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

// GraphCell は草グリッドの 1 マス (1 日)。
type GraphCell struct {
	Date    time.Time // そのマスの日。範囲外パディングは IsZero
	Score   int       // Σ letterWeight。範囲外/0 件は 0
	Level   int       // 0..4 の濃淡レベル
	InRange bool      // グリッド対象範囲 (期間窓内かつ今日以前) なら true。範囲外は空白パディング
}

// GraphColumn は週 (月曜始まり) 1 列。Cells[0]=Mon … Cells[6]=Sun。
type GraphColumn struct {
	Monday time.Time
	Cells  [7]GraphCell
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
	SeriesKind    string        // "day" / "week"
	SeriesOmitted int           // 週別で切り捨てた古い週数
	Graph         []GraphColumn // Options.Graph 指定時のみ。空なら従来の Series を使う
	GraphOmitted  int           // 53 週上限で切り捨てた古い週数
}

// maxWeekBuckets は週別時系列で表示する最大週数。超過分は SeriesOmitted に回す。
const maxWeekBuckets = 16

// maxGraphWeeks は草グリッドの最大列 (週) 数。超過分は古い週から GraphOmitted に回す。
const maxGraphWeeks = 53

// leadingAlphaRE はファイル名先頭の連続英字 (= コンテスト種別) を捕捉する。
var leadingAlphaRE = regexp.MustCompile(`^[a-zA-Z]+`)

// contestIDRE はファイル名先頭の「英字 + 数字」(= contest_id) を捕捉する。
var contestIDRE = regexp.MustCompile(`^[a-zA-Z]+[0-9]+`)

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
		solves = append(solves, Solve{Date: date, File: base, Category: cat, Contest: contestID(base), Letter: letter})
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

// contestID はファイル名から contest_id を導く。
//   - "abc457_d.py" → "abc457"  (先頭英字 + 数字)
//   - "scratch.py"  → "scratch" (数字が無ければ先頭英字)
//   - "123.py"      → "other"   (先頭英字なし)
func contestID(file string) string {
	base := strings.TrimSuffix(file, filepath.Ext(file))
	if m := contestIDRE.FindString(base); m != "" {
		return strings.ToLower(m)
	}
	if m := leadingAlphaRE.FindString(base); m != "" {
		return strings.ToLower(m)
	}
	return "other"
}

// Compute は Solve 群を Options に従って集計する純粋関数。
func Compute(solves []Solve, opts Options) Report {
	now := opts.Now
	if now.IsZero() {
		now = time.Now().Local()
	}
	now = dayOf(now)

	win := resolveWindow(opts, now)

	// 期間窓で絞る。
	var in []Solve
	for _, s := range solves {
		if inWin(s.Date, win) {
			in = append(in, s)
		}
	}

	rep := Report{Label: win.label}
	rep.Total = len(in)

	// カテゴリ別・レター別・日別件数・日別スコア (レター重み合計) を集計。
	catN := map[string]int{}
	letN := map[string]int{}
	dayN := map[time.Time]int{}     // 0 時 time → 件数
	dayScore := map[time.Time]int{} // 0 時 time → Σ letterWeight (草の濃淡用)
	for _, s := range in {
		catN[s.Category]++
		letN[s.Letter]++
		day := dayOf(s.Date)
		dayN[day]++
		dayScore[day] += letterWeight(s.Letter)
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

	// 時系列。--graph 指定時は草グリッドに差し替え、バー Series は構築しない。
	// グリッド範囲は窓 (Period でも Rolling でも) の開始日に追従する。
	if opts.Graph {
		rep.Graph, rep.GraphOmitted = buildGraph(dayScore, win.start, now)
	} else if win.daily {
		rep.SeriesKind = "day"
		rep.Series = dailySeries(dayN, win.start, now)
	} else {
		rep.SeriesKind = "week"
		rep.Series, rep.SeriesOmitted = weeklySeries(in)
	}
	return rep
}

// window は集計に使う日付窓。start/end は inclusive 日境界 (ローカル 0 時)。
// start.IsZero() なら下端なし、end.IsZero() なら上端なし (= 全期間)。
type window struct {
	start, end time.Time
	daily      bool   // 時系列粒度: true=日別 / false=週別
	label      string // Report.Label
}

// resolveWindow は Options から window を組み立てる。
// Rolling が非 nil ならローリング窓、そうでなければ Period の暦窓。
func resolveWindow(opts Options, now time.Time) window {
	if r := opts.Rolling; r != nil {
		return rollingWindow(*r, now)
	}
	switch opts.Period {
	case ThisWeek:
		s := weekStart(now)
		e := s.AddDate(0, 0, 6)
		return window{start: s, end: e, daily: true,
			label: "this week (" + s.Format("2006-01-02") + "–" + e.Format("01-02") + ")"}
	case ThisMonth:
		s := time.Date(now.Year(), now.Month(), 1, 0, 0, 0, 0, now.Location())
		e := s.AddDate(0, 1, -1)
		return window{start: s, end: e, daily: true,
			label: "this month (" + now.Format("2006-01") + ")"}
	case ThisYear:
		s := time.Date(now.Year(), 1, 1, 0, 0, 0, 0, now.Location())
		e := time.Date(now.Year(), 12, 31, 0, 0, 0, 0, now.Location())
		return window{start: s, end: e, daily: false,
			label: "this year (" + now.Format("2006") + ")"}
	default: // AllTime
		return window{daily: false, label: "all time"}
	}
}

// rollingWindow は「今日から N 単位分」の半開区間 (startExcl, now] を window にする。
// 含まれる最初の日 first を start に、now を end に置き、粒度は窓日数 (≤31 で日別) で決める。
func rollingWindow(r Rolling, now time.Time) window {
	var startExcl time.Time
	var unit string
	switch r.Unit {
	case UnitWeek:
		startExcl = now.AddDate(0, 0, -7*r.N)
		unit = "week"
	case UnitMonth:
		startExcl = now.AddDate(0, -r.N, 0)
		unit = "month"
	case UnitYear:
		startExcl = now.AddDate(-r.N, 0, 0)
		unit = "year"
	default: // UnitDay
		startExcl = now.AddDate(0, 0, -r.N)
		unit = "day"
	}
	first := startExcl.AddDate(0, 0, 1) // 半開区間なので開始の翌日が最初の含む日
	plural := ""
	if r.N != 1 {
		plural = "s"
	}
	label := fmt.Sprintf("last %d %s%s (%s–%s)", r.N, unit, plural,
		first.Format("2006-01-02"), now.Format("01-02"))
	return window{start: first, end: now, daily: daysBetween(first, now) <= 31, label: label}
}

// daysBetween は a..b (inclusive) の日数を DST 非依存に数える。
func daysBetween(a, b time.Time) int {
	a, b = dayOf(a), dayOf(b)
	n := 0
	for d := a; !d.After(b); d = d.AddDate(0, 0, 1) {
		n++
	}
	return n
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

// inWin は d (日に丸めて) が window の inclusive 境界に入るか判定する。
func inWin(d time.Time, w window) bool {
	d = dayOf(d)
	if !w.start.IsZero() && d.Before(w.start) {
		return false
	}
	if !w.end.IsZero() && d.After(w.end) {
		return false
	}
	return true
}

// InWindow は date が opts の集計窓 (Period / Rolling) に入るか判定する公開ヘルパ。
// review など stats 以外のコマンドが同じ窓定義を共有するために使う。Now が
// ゼロ値なら time.Now().Local() を使う。
func InWindow(date time.Time, opts Options) bool {
	now := opts.Now
	if now.IsZero() {
		now = time.Now().Local()
	}
	return inWin(date, resolveWindow(opts, dayOf(now)))
}

// WindowLabel は opts の集計窓のラベルを返す
// ("all time" / "this month (2026-06)" / "last 2 weeks (…)" など)。
func WindowLabel(opts Options) string {
	now := opts.Now
	if now.IsZero() {
		now = time.Now().Local()
	}
	return resolveWindow(opts, dayOf(now)).label
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

// dailySeries は start〜now の各日を 0 件含めて並べる (日別粒度の窓用)。
func dailySeries(dayN map[time.Time]int, start, now time.Time) []Bucket {
	if start.IsZero() {
		start = now
	}
	var out []Bucket
	for d := dayOf(start); !d.After(now); d = d.AddDate(0, 0, 1) {
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

// letterWeight はレターを難易度の代理重みに変換する。
//   - "?" (レター不明) は 1。
//   - 先頭が英小文字なら a=1, b=2, … z=26 (大文字は classify で小文字化済み)。
//   - それ以外 (数字始まり等) は 1。
//
// 複数文字レター ("ex" 等、稀) は先頭文字のみ採用する。
func letterWeight(letter string) int {
	if letter == "" || letter == "?" {
		return 1
	}
	c := letter[0]
	if c >= 'a' && c <= 'z' {
		return int(c-'a') + 1
	}
	return 1
}

// shadeLevel は日次スコア (Σ letterWeight) を濃淡レベル 0..4 に分類する。
// しきい値は固定で、データに依存せず決定的。
//
//	score 0    → 0 (空マス)
//	      1–3  → 1
//	      4–7  → 2
//	      8–12 → 3
//	      13+  → 4
func shadeLevel(score int) int {
	switch {
	case score <= 0:
		return 0
	case score <= 3:
		return 1
	case score <= 7:
		return 2
	case score <= 12:
		return 3
	default:
		return 4
	}
}

// buildGraph は日次スコアから集計窓に追従した草グリッドを構築する。
// winStart は窓の開始日 (Period でも Rolling でも resolveWindow が決めた値)。
// winStart.IsZero() (= 全期間で下端なし) のときは最初に解いた日を基点にする。
// 列は月曜始まりの週、各列 7 マス (Mon..Sun)。範囲の先頭/末尾で週の途中に
// かかる曜日は InRange=false の空白パディングにする。列が maxGraphWeeks を
// 超える場合は新しい側を残し、切り捨てた古い週数を omitted で返す。
func buildGraph(dayScore map[time.Time]int, winStart, now time.Time) (cols []GraphColumn, omitted int) {
	now = dayOf(now)

	// グリッドが覆う [rangeStart, rangeEnd] を決める。rangeEnd は常に今日。
	rangeEnd := now
	var rangeStart time.Time
	if !winStart.IsZero() {
		rangeStart = dayOf(winStart)
	} else {
		// 下端なし (全期間): 最初に解いた日が基点。無ければ今日。
		rangeStart = now
		first := true
		for d := range dayScore {
			d = dayOf(d)
			if first || d.Before(rangeStart) {
				rangeStart = d
				first = false
			}
		}
	}
	if rangeStart.After(rangeEnd) {
		rangeStart = rangeEnd
	}

	// 列は週境界 (月曜) に整列。範囲外の曜日はパディング。
	firstMon := weekStart(rangeStart)
	lastMon := weekStart(rangeEnd)
	for mon := firstMon; !mon.After(lastMon); mon = mon.AddDate(0, 0, 7) {
		col := GraphColumn{Monday: mon}
		for wd := 0; wd < 7; wd++ {
			day := mon.AddDate(0, 0, wd)
			inRange := !day.Before(rangeStart) && !day.After(rangeEnd)
			cell := GraphCell{InRange: inRange}
			if inRange {
				cell.Date = day
				cell.Score = dayScore[day]
				cell.Level = shadeLevel(cell.Score)
			}
			col.Cells[wd] = cell
		}
		cols = append(cols, col)
	}

	// 上限超過 (主に全期間) は新しい側を残す。
	if len(cols) > maxGraphWeeks {
		omitted = len(cols) - maxGraphWeeks
		cols = cols[len(cols)-maxGraphWeeks:]
	}
	return cols, omitted
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
