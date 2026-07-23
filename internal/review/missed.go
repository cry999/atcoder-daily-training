package review

import (
	"fmt"
	"io"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/charmbracelet/lipgloss"

	"github.com/cry999/atcoder-daily-training/internal/solvestat"
	"github.com/cry999/atcoder-daily-training/internal/stats"
)

// MissedItem は 1 件の復習対象。
type MissedItem struct {
	ID        string
	Path      string
	Contest   string
	Letter    string
	AC        *bool
	Editorial *bool
	Reviewed  time.Time
}

// MissedReport は前日復習キューの表示データ。
type MissedReport struct {
	Date  time.Time
	Items []MissedItem
}

// BuildMissed は target の練習問題から ac=false または editorial=true のものを抽出する。
func BuildMissed(solves []stats.Solve, target time.Time) MissedReport {
	target = dayOf(target)
	rep := MissedReport{Date: target}
	for _, s := range solves {
		if !dayOf(s.Date).Equal(target) || !s.HasStat {
			continue
		}
		if !isMissed(s.Stat) {
			continue
		}
		rep.Items = append(rep.Items, MissedItem{
			ID:        strings.TrimSuffix(s.File, filepath.Ext(s.File)),
			Path:      s.Path,
			Contest:   s.Contest,
			Letter:    s.Letter,
			AC:        s.Stat.AC,
			Editorial: s.Stat.Editorial,
			Reviewed:  s.Stat.ReviewedAt,
		})
	}
	sort.Slice(rep.Items, func(i, j int) bool { return rep.Items[i].ID < rep.Items[j].ID })
	return rep
}

func isMissed(st solvestat.Stat) bool {
	if st.AC != nil && !*st.AC {
		return true
	}
	return st.Editorial != nil && *st.Editorial
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
		return MissedItem{}, fmt.Errorf("missed item %q not found for %s", id, r.Date.Format("2006-01-02"))
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
	b.WriteString(revTitleStyle.Render("missed practice — "+r.Date.Format("2006-01-02")) + "\n\n")
	if len(r.Items) == 0 {
		b.WriteString(revInfoStyle.Render("no missed practice found") + "\n")
		_, err := io.WriteString(w, b.String())
		return err
	}
	reviewed := 0
	for _, it := range r.Items {
		check := "[ ]"
		reviewedAt := ""
		if !it.Reviewed.IsZero() {
			check = "[x]"
			reviewed++
			reviewedAt = "   " + revInfoStyle.Render("reviewed "+it.Reviewed.Format("2006-01-02 15:04"))
		}
		fmt.Fprintf(&b, "  %s %-12s  ac=%-5s  editorial=%-5s  %s%s\n",
			check, it.ID, boolText(it.AC), boolText(it.Editorial), it.Path, reviewedAt)
	}
	fmt.Fprintf(&b, "\n  %s\n", revInfoStyle.Render(fmt.Sprintf("%d missed, %d reviewed", len(r.Items), reviewed)))
	_, err := io.WriteString(w, lipgloss.NewStyle().Render(b.String()))
	return err
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
