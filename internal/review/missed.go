package review

import (
	"fmt"
	"io"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/charmbracelet/lipgloss"

	"github.com/cry999/atcoder-daily-training/internal/reviewrule"
	"github.com/cry999/atcoder-daily-training/internal/stats"
)

// MissedItem は 1 件の復習対象。
type MissedItem struct {
	Date      time.Time
	ID        string
	Path      string
	Contest   string
	Letter    string
	AC        *bool
	Editorial *bool
	Reviewed  time.Time
}

// MissedReport は復習キューの表示データ。
type MissedReport struct {
	Date  time.Time // 互換用。単日なら Start と同じ。
	Start time.Time
	End   time.Time
	Items []MissedItem
}

// BuildMissed は target の練習問題から既定条件 (ac=false or editorial=true) に
// 合うものを抽出する。
func BuildMissed(solves []stats.Solve, target time.Time) MissedReport {
	rule, _ := reviewrule.Parse("", nil)
	return BuildMissedWithRule(solves, target, rule)
}

// BuildMissedWithRule は target の練習問題から rule に合うものを抽出する。
func BuildMissedWithRule(solves []stats.Solve, target time.Time, rule reviewrule.Rule) MissedReport {
	return BuildMissedInRangeWithRule(solves, target, target, rule)
}

// BuildMissedInRangeWithRule は start から end まで (両端を含む) の練習問題から
// rule に合うものを抽出する。
func BuildMissedInRangeWithRule(solves []stats.Solve, start, end time.Time, rule reviewrule.Rule) MissedReport {
	start, end = dayOf(start), dayOf(end)
	rep := MissedReport{Date: start, Start: start, End: end}
	for _, s := range solves {
		date := dayOf(s.Date)
		if date.Before(start) || date.After(end) || !s.HasStat {
			continue
		}
		if !rule.Match(s.Stat) {
			continue
		}
		rep.Items = append(rep.Items, MissedItem{
			Date:      date,
			ID:        strings.TrimSuffix(s.File, filepath.Ext(s.File)),
			Path:      s.Path,
			Contest:   s.Contest,
			Letter:    s.Letter,
			AC:        s.Stat.AC,
			Editorial: s.Stat.Editorial,
			Reviewed:  s.Stat.ReviewedAt,
		})
	}
	sort.Slice(rep.Items, func(i, j int) bool {
		if !rep.Items[i].Date.Equal(rep.Items[j].Date) {
			return rep.Items[i].Date.Before(rep.Items[j].Date)
		}
		return rep.Items[i].ID < rep.Items[j].ID
	})
	return rep
}

// FindMissed は check ID に一致する復習対象を 1 件だけ返す。
func (r MissedReport) FindMissed(id string) (MissedItem, error) {
	id = normalizeMissedID(id)
	var matches []MissedItem
	for _, it := range r.Items {
		if normalizeMissedID(it.ID) == id || normalizeMissedID(it.Contest+"/"+it.Letter) == id {
			matches = append(matches, it)
		}
	}
	if len(matches) == 0 {
		return MissedItem{}, fmt.Errorf("missed item %q not found for %s", id, r.periodLabel())
	}
	if len(matches) > 1 {
		return MissedItem{}, fmt.Errorf("missed item %q is ambiguous", id)
	}
	if strings.TrimSpace(matches[0].Path) == "" {
		return MissedItem{}, fmt.Errorf("missed item %q has no source path", id)
	}
	return matches[0], nil
}

func normalizeMissedID(id string) string {
	id = strings.ToLower(strings.TrimSpace(id))
	id = strings.TrimSuffix(id, ".py")
	id = strings.ReplaceAll(id, "\\", "/")
	id = strings.ReplaceAll(id, "/", "_")
	return id
}

// RenderMissed は復習キューを人間向けテキストとして出力する。
func RenderMissed(w io.Writer, r MissedReport) error {
	var b strings.Builder
	b.WriteString(revTitleStyle.Render("missed practice — "+r.periodLabel()) + "\n\n")
	if len(r.Items) == 0 {
		b.WriteString(revInfoStyle.Render("no missed practice found") + "\n")
		_, err := io.WriteString(w, b.String())
		return err
	}
	reviewed := 0
	showDate := !dayOf(r.Start).Equal(dayOf(r.End))
	for _, it := range r.Items {
		check := "[ ]"
		reviewedAt := ""
		if !it.Reviewed.IsZero() {
			check = "[x]"
			reviewed++
			reviewedAt = "   " + revInfoStyle.Render("reviewed "+it.Reviewed.Format("2006-01-02 15:04"))
		}
		if showDate {
			fmt.Fprintf(&b, "  %s %s  %-12s  ac=%-5s  editorial=%-5s  %s%s\n",
				check, it.Date.Format("2006-01-02"), it.ID, boolText(it.AC), boolText(it.Editorial), it.Path, reviewedAt)
		} else {
			fmt.Fprintf(&b, "  %s %-12s  ac=%-5s  editorial=%-5s  %s%s\n",
				check, it.ID, boolText(it.AC), boolText(it.Editorial), it.Path, reviewedAt)
		}
	}
	fmt.Fprintf(&b, "\n  %s\n", revInfoStyle.Render(fmt.Sprintf("%d missed, %d reviewed", len(r.Items), reviewed)))
	_, err := io.WriteString(w, lipgloss.NewStyle().Render(b.String()))
	return err
}

func (r MissedReport) periodLabel() string {
	start, end := r.Start, r.End
	if start.IsZero() {
		start = r.Date
	}
	if end.IsZero() {
		end = start
	}
	if dayOf(start).Equal(dayOf(end)) {
		return start.Format("2006-01-02")
	}
	return start.Format("2006-01-02") + " through " + end.Format("2006-01-02")
}

func boolText(b *bool) string {
	if b == nil {
		return "unset"
	}
	if *b {
		return "true"
	}
	return "false"
}
