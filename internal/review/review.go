// Package review は練習ツリー (exercise/YYYY/MM/DD/*.py) を「コンテスト単位」で
// 列挙する。stats が集計値 (総数・ストリーク・カテゴリ別・草) を出すのに対し、
// review は contest × letter のテーブルを並べ、各マスを recency (最近解いたか /
// 古いか) で着色し、各コンテストの最終解答日を添える。
//
// データ層 (Scan/Solve/Period/Rolling) と期間窓判定・色ランプは internal/stats を
// 流用する。Build / recencyLevel は純粋関数で、Now 注入により決定的にテストできる。
//
// 要件詳細: docs/tools/requirements/014-exercise-review.md
package review

import (
	"regexp"
	"sort"
	"strconv"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/stats"
)

// Options は一覧条件。Category は必須。Period/Rolling/Now は stats と共通の期間窓。
type Options struct {
	Category string
	Period   stats.Period
	Rolling  *stats.Rolling
	Now      time.Time
}

// Row は 1 コンテスト分の行。
type Row struct {
	Contest    string               // contest_id (例 "abc457")
	Solved     map[string]time.Time // letter → その letter を最後に解いた日。未解の letter は不在
	Editorial  map[string]bool      // letter → その letter を解説 (editorial=true) 込みで解いたか。true のマスは赤で描く
	LastSolved time.Time            // その回を最後に解いた日 (= Solved の最大値)
}

// Report は表示に必要な集計済みデータ。
type Report struct {
	Label    string    // 期間ラベル ("all time" / "this month (2026-06)" など)
	Category string    // 対象カテゴリ
	AllTime  bool      // 期間フィルタ無し (全期間) なら true。ヘッダの出し分けに使う
	Now      time.Time // recency 判定の基準日 (ローカル 0 時)。Render が各マスの色を引くのに使う
	Columns  []string  // 表示する letter 列 (abc は a–g 固定 + 範囲外 letter を末尾、他は和集合昇順、"?" 末尾)
	Rows     []Row     // contest 番号降順
	Contests int       // 行数
	Solves   int       // 対象 solve 総数
}

// abcLetters は ABC の固定列 (a–g)。解いていない letter も列として出し、穴を見せる。
var abcLetters = []string{"a", "b", "c", "d", "e", "f", "g"}

// contestNumRE は contest_id 中の最初の数字列 (contest_num) を捕捉する。
// "abc447" → 447、"awc0001-beta" → 1 (先頭の数字列)。
var contestNumRE = regexp.MustCompile(`[0-9]+`)

// statsOptions は review.Options から stats の期間窓判定に渡す Options を作る。
func (o Options) statsOptions() stats.Options {
	return stats.Options{Period: o.Period, Rolling: o.Rolling, Now: o.Now}
}

// Build は Solve 群を Options に従ってカテゴリ絞り・グルーピングする純粋関数。
// 列の決定 (abc は a–g 固定) もここで行う。
func Build(solves []stats.Solve, opts Options) Report {
	now := opts.Now
	if now.IsZero() {
		now = time.Now().Local()
	}
	opts.Now = now // stats の窓判定と recency で同じ now を使う
	sopts := opts.statsOptions()

	rep := Report{
		Label:    stats.WindowLabel(sopts),
		Category: opts.Category,
		AllTime:  opts.Period == stats.AllTime && opts.Rolling == nil,
		Now:      dayOf(now),
	}

	// カテゴリ + 期間窓で絞り、contest_id でグルーピング。
	byContest := map[string]*Row{}
	letterSeen := map[string]bool{}
	for _, s := range solves {
		if s.Category != opts.Category {
			continue
		}
		if !stats.InWindow(s.Date, sopts) {
			continue
		}
		rep.Solves++
		letterSeen[s.Letter] = true
		row := byContest[s.Contest]
		if row == nil {
			row = &Row{Contest: s.Contest, Solved: map[string]time.Time{}, Editorial: map[string]bool{}}
			byContest[s.Contest] = row
		}
		// 解説を見て解いた (editorial=true) 記録が 1 件でもあればそのマスを赤で描く。
		// 日付の代表値選びとは独立に OR で拾う (どれか 1 回でも解説込みなら「解説を見た」)。
		if s.Stat.Editorial != nil && *s.Stat.Editorial {
			row.Editorial[s.Letter] = true
		}
		// (contest, letter) ごとに最良の日付を採る。日付あり (exercise) を優先し、
		// 日付なし (カテゴリツリー) では既存を上書きしない。複数日付なら最大。
		cur, ok := row.Solved[s.Letter]
		switch {
		case !ok:
			row.Solved[s.Letter] = s.Date
		case s.Date.IsZero():
			// 日付なしは既存 (dated/undated 問わず) を上書きしない。
		case cur.IsZero() || s.Date.After(cur):
			row.Solved[s.Letter] = s.Date
		}
		// LastSolved は dated のみで決める (全部 undated ならゼロ → "—")。
		if !s.Date.IsZero() && s.Date.After(row.LastSolved) {
			row.LastSolved = s.Date
		}
	}

	rep.Columns = buildColumns(opts.Category, letterSeen)

	rep.Rows = make([]Row, 0, len(byContest))
	for _, row := range byContest {
		rep.Rows = append(rep.Rows, *row)
	}
	sort.Slice(rep.Rows, func(i, j int) bool {
		ni, nj := contestNum(rep.Rows[i].Contest), contestNum(rep.Rows[j].Contest)
		if ni != nj {
			return ni > nj // contest 番号降順 (新しい回が上)
		}
		return rep.Rows[i].Contest > rep.Rows[j].Contest
	})
	rep.Contests = len(rep.Rows)
	return rep
}

// buildColumns は表示する letter 列を決める。
// abc は a–g を固定列にし、a–g 外で解いた letter があれば末尾に足す。
// その他のカテゴリは実際に解いた letter の和集合 (昇順、"?" 末尾)。
func buildColumns(category string, seen map[string]bool) []string {
	var cols []string
	inBase := map[string]bool{}
	if category == "abc" {
		cols = append(cols, abcLetters...)
		for _, l := range abcLetters {
			inBase[l] = true
		}
	}
	// 固定列に無い letter を昇順 ("?" 末尾) で末尾追加。
	var extra []string
	for l := range seen {
		if !inBase[l] {
			extra = append(extra, l)
		}
	}
	sortLetters(extra)
	return append(cols, extra...)
}

// sortLetters は letter を昇順に並べる ("?" は末尾)。
func sortLetters(ls []string) {
	sort.Slice(ls, func(i, j int) bool {
		ai, bi := ls[i] == "?", ls[j] == "?"
		if ai != bi {
			return bi // "?" を後ろへ
		}
		return ls[i] < ls[j]
	})
}

// dayOf は時刻を捨ててローカル 0 時に丸める。
func dayOf(t time.Time) time.Time {
	y, m, d := t.Date()
	return time.Date(y, m, d, 0, 0, 0, 0, t.Location())
}

// contestNum は contest_id の末尾数字を返す。数字が無ければ -1 (末尾に並ぶ)。
func contestNum(id string) int {
	if m := contestNumRE.FindString(id); m != "" {
		if n, err := strconv.Atoi(m); err == nil {
			return n
		}
	}
	return -1
}

// recencyLevel は解答日 solved と now の経過日数を 1..4 のレベルに分類する。
// しきい値は固定で決定的: ≤7 日=4 (最も新しい), ≤30 日=3, ≤90 日=2, それ超=1 (最も古い)。
// 未解のマスはこの関数を呼ばず、レベル 0 (薄灰 ·) で描く。
func recencyLevel(solved, now time.Time) int {
	switch {
	case !solved.Before(now.AddDate(0, 0, -7)):
		return 4
	case !solved.Before(now.AddDate(0, 0, -30)):
		return 3
	case !solved.Before(now.AddDate(0, 0, -90)):
		return 2
	default:
		return 1
	}
}
