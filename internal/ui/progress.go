package ui

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/bubbles/progress"
	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

// caseState は 1 ケースのライブ表示上の状態。
type caseState int

const (
	statePending caseState = iota // まだワーカーに拾われていない
	stateRunning                  // 実行中 (スピナー表示)
	stateDone                     // 完了 (バッジ表示)
)

// caseStartedMsg / caseFinishedMsg は testexec のワーカーから program.Send 経由で
// 届くイベント。bubbletea のイベントループ内でのみ model を更新する。
type caseStartedMsg struct{ name string }
type caseFinishedMsg struct{ cr testexec.CaseResult }

// progressModel は実行中のライブ表示 (ケース一覧 + プログレスバー) を司る
// bubbletea モデル。完了後の詳細 (diff/stderr) は描画せず、TestReporter.End が
// プログラム終了後に通常出力する。
type progressModel struct {
	names   []string
	idx     map[string]int
	state   []caseState
	results []testexec.CaseResult
	done    int
	total   int
	jobs    int
	spinner spinner.Model
	prog    progress.Model
}

func newProgressModel(names []string, jobs int) progressModel {
	idx := make(map[string]int, len(names))
	for i, n := range names {
		idx[n] = i
	}
	s := spinner.New()
	s.Spinner = spinner.MiniDot
	s.Style = spinnerStyle
	p := progress.New(
		progress.WithWidth(28),
		progress.WithoutPercentage(),
		progress.WithGradient(mochaSapphire, mochaGreen),
	)
	return progressModel{
		names:   names,
		idx:     idx,
		state:   make([]caseState, len(names)),
		results: make([]testexec.CaseResult, len(names)),
		total:   len(names),
		jobs:    jobs,
		spinner: s,
		prog:    p,
	}
}

func (m progressModel) Init() tea.Cmd {
	return m.spinner.Tick
}

func (m progressModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case caseStartedMsg:
		if i, ok := m.idx[msg.name]; ok && m.state[i] == statePending {
			m.state[i] = stateRunning
		}
		return m, nil
	case caseFinishedMsg:
		if i, ok := m.idx[msg.cr.Name]; ok && m.state[i] != stateDone {
			m.state[i] = stateDone
			m.results[i] = msg.cr
			m.done++
		}
		return m, nil
	case spinner.TickMsg:
		var cmd tea.Cmd
		m.spinner, cmd = m.spinner.Update(msg)
		return m, cmd
	case tea.KeyMsg:
		if msg.String() == "ctrl+c" {
			return m, tea.Quit
		}
	}
	return m, nil
}

func (m progressModel) View() string {
	var b strings.Builder
	b.WriteString(runningHeaderStyle.Render(fmt.Sprintf("Running tests (jobs=%d)", m.jobs)))
	b.WriteString("\n\n")
	for i := range m.names {
		b.WriteString(m.rowView(i))
		b.WriteByte('\n')
	}
	b.WriteByte('\n')
	pct := 0.0
	if m.total > 0 {
		pct = float64(m.done) / float64(m.total)
	}
	b.WriteString("  " + m.prog.ViewAs(pct) + "  " + countStyle.Render(fmt.Sprintf("%d/%d", m.done, m.total)))
	b.WriteByte('\n')
	return b.String()
}

func (m progressModel) rowView(i int) string {
	label := caseLabelStyle.Render("[" + m.names[i] + "]")
	switch m.state[i] {
	case statePending:
		return "  " + label + "  " + pendingStyle.Render("· pending")
	case stateRunning:
		return "  " + label + " " + m.spinner.View() + " " + runningStyle.Render("running...")
	default:
		return "  " + caseLineString(m.results[i])
	}
}
