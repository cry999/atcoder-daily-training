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

// Render は Report を人間向けテーブルとして w に書き出す (非 TTY / 一括出力用)。
// TTY ではページに収まるスクロール表示 (RunTUI) を使う。マスは recency で着色。
func Render(w io.Writer, r Report) error {
	var b strings.Builder

	b.WriteString(r.titleLine() + "\n\n")
	if r.Contests == 0 {
		b.WriteString(revInfoStyle.Render("no "+r.Category+" solves found in exercise/ for "+r.periodPhrase()) + "\n")
		_, err := io.WriteString(w, b.String())
		return err
	}

	contestW := r.contestWidth()
	b.WriteString(r.columnHeaderLine(contestW) + "\n")
	for _, line := range r.rowLines(contestW) {
		b.WriteString(line + "\n")
	}
	b.WriteString("\n" + r.legendLine() + "\n")
	b.WriteString(r.footerLine() + "\n")

	_, err := io.WriteString(w, b.String())
	return err
}

// titleLine はヘッダ行を作る。全期間は件数、期間指定は期間ラベル、0 件は素のタイトル。
func (r Report) titleLine() string {
	title := "exercise " + r.Category + " review"
	switch {
	case r.Contests == 0:
		if !r.AllTime {
			title += " — " + r.Label
		}
	case r.AllTime:
		title += " — " + countWord(r.Contests, "contest") + ", " + countWord(r.Solves, "solve")
	default:
		title += " — " + r.Label
	}
	return revTitleStyle.Render(title)
}

// contestWidth は contest 列の幅 (ラベル "contest" と最長 contest_id の広い方)。
func (r Report) contestWidth() int {
	w := len("contest")
	for _, row := range r.Rows {
		if len(row.Contest) > w {
			w = len(row.Contest)
		}
	}
	return w
}

// columnHeaderLine は "  contest   a b c …   last solved" の列ヘッダ行。
func (r Report) columnHeaderLine(contestW int) string {
	letters := strings.Join(r.Columns, " ")
	return "  " + revHeadStyle.Render(fmt.Sprintf("%-*s   %s   last solved", contestW, "contest", letters))
}

// rowLines は各コンテスト 1 行ぶんの描画済み文字列を返す (マスは recency で着色)。
func (r Report) rowLines(contestW int) []string {
	lines := make([]string, 0, len(r.Rows))
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
		lines = append(lines, "  "+revContestSt.Render(fmt.Sprintf("%-*s", contestW, row.Contest))+
			"   "+cells.String()+"   "+revHeadStyle.Render(row.LastSolved.Format("2006-01-02")))
	}
	return lines
}

// legendLine は recency の凡例行。
func (r Report) legendLine() string {
	return "  " + revInfoStyle.Render("older ") + recencyLegend() +
		revInfoStyle.Render(" newer   ") + stats.ShadeGlyph(0) + revInfoStyle.Render("=未着手")
}

// footerLine は件数フッタ行。
func (r Report) footerLine() string {
	return "  " + revInfoStyle.Render(countWord(r.Contests, "contest"))
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
