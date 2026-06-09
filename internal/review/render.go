package review

import (
	"fmt"
	"io"
	"strings"

	"github.com/charmbracelet/lipgloss"

	"github.com/cry999/atcoder-daily-training/internal/stats"
)

// Catppuccin 系の最小配色。非 TTY では lipgloss が自動で素のテキストに落とす。
var (
	revTitleStyle = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#74c7ec"))
	revHeadStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#7f849c"))
	revContestSt  = lipgloss.NewStyle().Foreground(lipgloss.Color("#89b4fa"))
	revInfoStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color("#7f849c")).Italic(true)
)

// Render は Report を人間向けテーブルとして w に書き出す。マスは recency で着色。
func Render(w io.Writer, r Report) error {
	var b strings.Builder

	// ヘッダ: 全期間は件数、期間指定は期間ラベルを添える。
	title := "exercise " + r.Category + " review"
	switch {
	case r.Contests == 0:
		if !r.AllTime {
			title += " — " + r.Label
		}
		b.WriteString(revTitleStyle.Render(title) + "\n\n")
		b.WriteString(revInfoStyle.Render("no "+r.Category+" solves found in exercise/ for "+r.periodPhrase()) + "\n")
		_, err := io.WriteString(w, b.String())
		return err
	case r.AllTime:
		title += " — " + countWord(r.Contests, "contest") + ", " + countWord(r.Solves, "solve")
	default:
		title += " — " + r.Label
	}
	b.WriteString(revTitleStyle.Render(title) + "\n\n")

	// 列幅: contest 列はラベル "contest" と最長 contest_id の広い方。
	contestW := len("contest")
	for _, row := range r.Rows {
		if len(row.Contest) > contestW {
			contestW = len(row.Contest)
		}
	}

	// 列ヘッダ。
	letters := strings.Join(r.Columns, " ")
	b.WriteString("  " + revHeadStyle.Render(fmt.Sprintf("%-*s   %s   last solved", contestW, "contest", letters)) + "\n")

	// 行。
	for _, row := range r.Rows {
		var cells strings.Builder
		for i, col := range r.Columns {
			if i > 0 {
				cells.WriteString(" ")
			}
			if solved, ok := row.Solved[col]; ok {
				cells.WriteString(stats.ShadeGlyph(recencyLevel(solved, r.Now)))
			} else {
				cells.WriteString(stats.ShadeGlyph(0)) // 未解は ·
			}
		}
		b.WriteString("  " + revContestSt.Render(fmt.Sprintf("%-*s", contestW, row.Contest)) +
			"   " + cells.String() + "   " + revHeadStyle.Render(row.LastSolved.Format("2006-01-02")) + "\n")
	}

	// 凡例 + フッタ。
	b.WriteString("\n  " + revInfoStyle.Render("older ") + recencyLegend() +
		revInfoStyle.Render(" newer   ") + stats.ShadeGlyph(0) + revInfoStyle.Render("=未着手") + "\n")
	b.WriteString("  " + revInfoStyle.Render(countWord(r.Contests, "contest")) + "\n")

	_, err := io.WriteString(w, b.String())
	return err
}

// countWord は "1 contest" / "3 contests" のように単複を整えた語句を返す。
func countWord(n int, word string) string {
	if n == 1 {
		return fmt.Sprintf("%d %s", n, word)
	}
	return fmt.Sprintf("%d %ss", n, word)
}

// periodPhrase は 0 件メッセージ用の期間語句 ("all time" / 期間ラベル)。
func (r Report) periodPhrase() string {
	if r.AllTime {
		return "all time"
	}
	return r.Label
}

// recencyLegend は recency レベル 1..4 を 1 マスずつ離して描く (暗→明の緑)。
func recencyLegend() string {
	var b strings.Builder
	for lvl := 1; lvl <= 4; lvl++ {
		if lvl > 1 {
			b.WriteString(" ")
		}
		b.WriteString(stats.ShadeGlyph(lvl))
	}
	return b.String()
}
