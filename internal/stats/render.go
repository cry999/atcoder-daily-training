package stats

import (
	"fmt"
	"io"
	"strings"

	"github.com/charmbracelet/lipgloss"
)

// Catppuccin Mocha から最小限の配色。非 TTY では lipgloss が自動で素のテキストに落とす。
var (
	statTitleStyle = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#74c7ec"))
	statLabelStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#7f849c"))
	statValueStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#89b4fa"))
	statSectStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#7f849c"))
	statBarStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color("#a6e3a1"))
	statInfoStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#7f849c")).Italic(true)
)

// Render は Report を人間向けテーブルとして w に書き出す。
func Render(w io.Writer, r Report) error {
	var b strings.Builder

	b.WriteString(statTitleStyle.Render("practice stats — "+r.Label) + "\n\n")

	if r.Total == 0 {
		b.WriteString(statInfoStyle.Render("no solves found in exercise/ for "+r.Label) + "\n")
		_, err := io.WriteString(w, b.String())
		return err
	}

	// サマリ。ラベル幅を揃える。
	summary := []struct {
		label string
		value string
	}{
		{"total solves", fmt.Sprintf("%d", r.Total)},
		{"active days", fmt.Sprintf("%d", r.ActiveDays)},
		{"current streak", fmt.Sprintf("%d days", r.CurrentStreak)},
		{"longest streak", fmt.Sprintf("%d days", r.LongestStreak)},
	}
	for _, s := range summary {
		b.WriteString("  " + statLabelStyle.Render(fmt.Sprintf("%-15s", s.label)) +
			statValueStyle.Render(s.value) + "\n")
	}

	// by category。
	if len(r.Categories) > 0 {
		b.WriteString("\n" + statSectStyle.Render("by category") + "\n")
		writeCounts(&b, r.Categories)
	}

	// by letter。
	if len(r.Letters) > 0 {
		b.WriteString("\n" + statSectStyle.Render("by letter") + "\n")
		writeCounts(&b, r.Letters)
	}

	// 時系列 (簡易バー付き)。
	if len(r.Series) > 0 {
		title := "by day"
		if r.SeriesKind == "week" {
			title = "by week"
		}
		b.WriteString("\n" + statSectStyle.Render(title) + "\n")
		writeSeries(&b, r.Series)
		if r.SeriesOmitted > 0 {
			b.WriteString("  " + statInfoStyle.Render(fmt.Sprintf("…and %d more week(s)", r.SeriesOmitted)) + "\n")
		}
	}

	_, err := io.WriteString(w, b.String())
	return err
}

// writeCounts は Count 群を "  key  N" 形式で揃えて書く。
func writeCounts(b *strings.Builder, counts []Count) {
	width := 0
	for _, c := range counts {
		if len(c.Key) > width {
			width = len(c.Key)
		}
	}
	for _, c := range counts {
		b.WriteString("  " + statValueStyle.Render(fmt.Sprintf("%-*s", width, c.Key)) +
			fmt.Sprintf("  %d\n", c.N))
	}
}

// writeSeries は各バケットを "  label  bar N" 形式で書く。バーは最大件数に合わせて伸縮。
func writeSeries(b *strings.Builder, series []Bucket) {
	const maxBar = 24
	max := 0
	labelW := 0
	for _, s := range series {
		if s.N > max {
			max = s.N
		}
		if len(s.Label) > labelW {
			labelW = len(s.Label)
		}
	}
	for _, s := range series {
		bar := barString(s.N, max, maxBar)
		b.WriteString("  " + statLabelStyle.Render(fmt.Sprintf("%-*s", labelW, s.Label)) +
			"  " + statBarStyle.Render(bar) + fmt.Sprintf(" %d\n", s.N))
	}
}

// barString は n / max を maxBar 幅の棒にする。0 件は薄い "░" 1 個で「その日も表示した」ことを示す。
func barString(n, max, maxBar int) string {
	if n == 0 {
		return "░"
	}
	if max <= 0 {
		return ""
	}
	w := n * maxBar / max
	if w < 1 {
		w = 1
	}
	return strings.Repeat("█", w)
}
