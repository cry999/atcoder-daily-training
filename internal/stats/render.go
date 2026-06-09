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

	// 時系列。--graph 指定時は草グリッド、そうでなければ簡易バー。
	switch {
	case len(r.Graph) > 0:
		b.WriteString("\n" + statSectStyle.Render("contribution graph (shade = Σ letter weight/day; a=1…g=7)") + "\n")
		writeGraph(&b, r.Graph)
		if r.GraphOmitted > 0 {
			b.WriteString("  " + statInfoStyle.Render(fmt.Sprintf("…and %d older week(s) omitted", r.GraphOmitted)) + "\n")
		}
	case len(r.Series) > 0:
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

// shadeGlyphs は濃淡レベル 0..4 のマス文字。縦長に見える陰影ブロック (░▒▓█) は
// 読みづらいので、活動あり (1..4) は GitHub 同様の四角 ■ で揃え、濃淡は色で表す。
// 空 (level 0) だけは小さな · にして、色が出ない非 TTY でも「活動した日/しない日」が
// 判別できるようにする。
var shadeGlyphs = [5]string{"·", "■", "■", "■", "■"}

// grassStyles はレベル別の着色 (緑のグラデーション、暗→明で濃さを表す)。TTY のみ効く。
// 1..4 は GitHub のダークモード contribution graph と同じ緑ランプ。暗背景で知覚的に
// 均等に段階が上がるよう調整されている。0 (空) は周辺 UI に馴染む Catppuccin の薄灰。
var grassStyles = [5]lipgloss.Style{
	lipgloss.NewStyle().Foreground(lipgloss.Color("#45475a")), // 0: 空 (薄灰)
	lipgloss.NewStyle().Foreground(lipgloss.Color("#0e4429")), // 1: 最も暗い緑
	lipgloss.NewStyle().Foreground(lipgloss.Color("#006d32")), // 2
	lipgloss.NewStyle().Foreground(lipgloss.Color("#26a641")), // 3
	lipgloss.NewStyle().Foreground(lipgloss.Color("#39d353")), // 4: 最も明るい緑 (最も濃い活動)
}

// ShadeGlyph はレベル 0..4 のマス文字を着色して返す。stats --graph と review が
// 同じ濃淡記号・色ランプを共有するための公開ヘルパ。level 0 は薄灰の `·`
// (未活動/未解)、1..4 は暗→明の緑 `■`。範囲外の値は端に丸める。
func ShadeGlyph(level int) string {
	if level < 0 {
		level = 0
	}
	if level > 4 {
		level = 4
	}
	return grassStyles[level].Render(shadeGlyphs[level])
}

// weekdayLabels は左端の曜日ラベル (Mon..Sun)。
var weekdayLabels = [7]string{"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}

// writeGraph は草グリッドを「月ラベル行 + 曜日 7 行 + 凡例」で描く。
// 列 = 週 (月曜始まり)、行 = 曜日。マス 1 つは "<glyph> " の 2 文字幅。
func writeGraph(b *strings.Builder, cols []GraphColumn) {
	const labelW = 3 // "Mon"
	prefix := strings.Repeat(" ", labelW+1)

	// 月ラベル行: 列の月が前列から変わった最初の列にその月の略称を置く。
	month := buildMonthHeader(cols, prefix)
	if strings.TrimSpace(month) != "" {
		b.WriteString("  " + statLabelStyle.Render(month) + "\n")
	}

	// 曜日 7 行。
	for wd := 0; wd < 7; wd++ {
		b.WriteString("  " + statLabelStyle.Render(weekdayLabels[wd]) + " ")
		for _, col := range cols {
			cell := col.Cells[wd]
			if !cell.InRange {
				b.WriteString("  ") // 範囲外パディング (空白 2 文字)
				continue
			}
			b.WriteString(grassStyles[cell.Level].Render(shadeGlyphs[cell.Level]) + " ")
		}
		b.WriteString("\n")
	}

	// 凡例。各レベルを 1 マスずつ離して 0..4 の 5 段階が読めるようにする。
	var legend strings.Builder
	for lvl := 0; lvl < 5; lvl++ {
		if lvl > 0 {
			legend.WriteString(" ")
		}
		legend.WriteString(grassStyles[lvl].Render(shadeGlyphs[lvl]))
	}
	b.WriteString("\n  " + statInfoStyle.Render("less ") + legend.String() + statInfoStyle.Render(" more") + "\n")
}

// buildMonthHeader は列に揃えた月ラベル行を作る。各列は 2 文字幅。
// 月が変わった最初の列の位置に月略称 (3 文字) を書き込む (GitHub と同様、まばら)。
func buildMonthHeader(cols []GraphColumn, prefix string) string {
	width := len(prefix) + len(cols)*2
	row := []byte(strings.Repeat(" ", width))
	prevMonth := -1
	for i, col := range cols {
		m := int(col.Monday.Month())
		if m == prevMonth {
			continue
		}
		prevMonth = m
		// 各月の最初の月曜は必ず 1〜7 日。Day>7 はグリッド先頭の部分週なので
		// ラベルを置かない (隣の月ラベルと重なるのを防ぐ)。
		if col.Monday.Day() > 7 {
			continue
		}
		label := col.Monday.Format("Jan")
		x := len(prefix) + i*2
		for k := 0; k < len(label) && x+k < len(row); k++ {
			row[x+k] = label[k]
		}
	}
	return string(row)
}
