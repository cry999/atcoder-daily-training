package review

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
)

// RunTUI は Report をページに収まるスクロール表示で見せる (TTY 用)。
// タイトル・列ヘッダ・凡例は固定し、コンテストの行だけを viewport で縦スクロールする。
// ↑/↓・PgUp/PgDn でスクロール、q/esc/Ctrl+C で終了。
func RunTUI(rep Report) error {
	_, err := tea.NewProgram(newReviewModel(rep), tea.WithAltScreen()).Run()
	return err
}

// reviewModel は固定ヘッダ + スクロール本体 (viewport) からなる TUI。
type reviewModel struct {
	title  string // ヘッダ (件数 / 期間ラベル付き)
	header string // 列ヘッダ行
	legend string // recency 凡例
	footer string // 件数フッタ
	body   string // 行をまとめた viewport の中身
	vp     viewport.Model
	ready  bool
}

// chromeHeight は viewport の上下に固定表示する行数 (高さ計算用)。
//   title(1) + blank(1) + header(1) ＝ 上 3 行
//   blank(1) + legend(1) + footer(1) ＝ 下 3 行
const chromeHeight = 6

func newReviewModel(rep Report) reviewModel {
	contestW := rep.contestWidth()
	return reviewModel{
		title:  rep.titleLine(),
		header: rep.columnHeaderLine(contestW),
		legend: rep.legendLine(),
		footer: rep.footerLine(),
		body:   strings.Join(rep.rowLines(contestW), "\n"),
	}
}

func (m reviewModel) Init() tea.Cmd { return nil }

func (m reviewModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "esc", "ctrl+c":
			return m, tea.Quit
		}
	case tea.WindowSizeMsg:
		h := msg.Height - chromeHeight
		if h < 1 {
			h = 1
		}
		if !m.ready {
			m.vp = viewport.New(msg.Width, h)
			m.vp.SetContent(m.body)
			m.ready = true
		} else {
			m.vp.Width = msg.Width
			m.vp.Height = h
		}
		return m, nil
	}

	if !m.ready {
		return m, nil
	}
	var cmd tea.Cmd
	m.vp, cmd = m.vp.Update(msg)
	return m, cmd
}

func (m reviewModel) View() string {
	if !m.ready {
		return "\n  読み込み中…"
	}
	help := revInfoStyle.Render(fmt.Sprintf("↑/↓ scroll · PgUp/PgDn page · q quit · %3.0f%%", m.vp.ScrollPercent()*100))
	return m.title + "\n\n" +
		m.header + "\n" +
		m.vp.View() + "\n" +
		m.legend + "\n" +
		m.footer + "   " + help
}
