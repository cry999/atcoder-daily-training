package ui

import (
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/x/ansi"

	tea "github.com/charmbracelet/bubbletea"
)

// CaseVerdict は 1 サンプルケースの判定結果 (watch ペインの per-case 表示用)。
type CaseVerdict struct {
	Name  string // ケース名 (例 "01")
	Label string // "AC" / "WA" / "TLE" / "RE"
	OK    bool   // AC (Pass) なら true。色分けに使う
}

// SampleSummary は分割画面 watch ペインのコンパクト要約 (diff は含まない)。
type SampleSummary struct {
	Passed, Total int
	Cases         []CaseVerdict // ケース名順の per-case verdict
	AllPassed     bool          // 全通過 (Total>0 && Passed==Total かつ判定成功)
	At            time.Time     // 判定時刻
	Err           error         // 判定自体が失敗 (テスト無し等)
}

// StartSplitConfig は分割画面の起動設定。ui は testexec / watch に依存しないため、
// サンプル判定 (RunSamples) と保存検知 (Changed) は closure として受け取る。
type StartSplitConfig struct {
	SolutionPath string
	Spawn        Spawner              // chat 用の子プロセス起動 (auto-restart)
	Header       ChatHeader           // AutoRestart=true で渡す
	RunSamples   func() SampleSummary // 保存検知時のサンプル再判定 (stdout に書かない)
	Changed      func() bool          // 解答ファイルの保存検知 (watch.Changed)
	UntilPass    bool                 // 全通過で終了
	Poll         time.Duration        // 保存検知のポーリング間隔 (0 → 既定)
}

// 分割画面のレイアウト予約行数。
const (
	splitTopLines  = 3 // watch ペイン: タイトル + 要約 + 区切り線
	splitHelpLines = 1 // 最下部のキーヘルプ
)

type splitTickMsg struct{}
type splitSampleMsg struct{ summary SampleSummary }

type startSplitModel struct {
	chat         *chatModel
	solutionPath string
	runSamples   func() SampleSummary
	changed      func() bool
	untilPass    bool
	poll         time.Duration

	summary        SampleSummary
	haveSummary    bool
	sampleInFlight bool

	width, height int
	ready         bool
}

var (
	splitWatchTitleStyle = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#74c7ec"))
	splitPassStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color("#a6e3a1"))
	splitFailStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color("#f38ba8"))
	splitRuleStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color("#45475a"))
	splitHelpStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color("#7f849c")).Italic(true)
)

// RunStartSplit は上下分割の bubbletea プログラムを駆動する。
// 終了コード: Ctrl+C / Ctrl+D / --until-pass 全通過 = 0。
func RunStartSplit(cfg StartSplitConfig) (int, error) {
	poll := cfg.Poll
	if poll <= 0 {
		poll = 250 * time.Millisecond
	}
	// 下ペインの chat は遅延起動 (入力が来るまで子を起動しない)。
	m := &startSplitModel{
		chat:         initialChatModel(cfg.Header, cfg.Spawn),
		solutionPath: cfg.SolutionPath,
		runSamples:   cfg.RunSamples,
		changed:      cfg.Changed,
		untilPass:    cfg.UntilPass,
		poll:         poll,
	}
	if _, err := tea.NewProgram(m, tea.WithAltScreen()).Run(); err != nil {
		return 1, err
	}
	return 0, nil
}

// chatHeight は chat ペインに割り当てる高さ (端末高さから watch + help を引く)。
func (m *startSplitModel) chatHeight() int {
	h := m.height - splitTopLines - splitHelpLines
	if h < 1 {
		h = 1
	}
	return h
}

func (m *startSplitModel) Init() tea.Cmd {
	m.sampleInFlight = true // 起動時に 1 回判定する
	return tea.Batch(m.chat.Init(), m.runSamplesCmd(), m.tickCmd())
}

func (m *startSplitModel) tickCmd() tea.Cmd {
	return tea.Tick(m.poll, func(time.Time) tea.Msg { return splitTickMsg{} })
}

func (m *startSplitModel) runSamplesCmd() tea.Cmd {
	run := m.runSamples
	return func() tea.Msg { return splitSampleMsg{summary: run()} }
}

func (m *startSplitModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width, m.height = msg.Width, msg.Height
		m.ready = true
		// chat には watch + help を引いた高さを渡す。
		cm, cmd := m.chat.Update(tea.WindowSizeMsg{Width: msg.Width, Height: m.chatHeight()})
		m.chat = cm.(*chatModel)
		return m, cmd

	case splitTickMsg:
		cmds := []tea.Cmd{m.tickCmd()} // 常に再アーム
		if !m.sampleInFlight && m.changed != nil && m.changed() {
			m.sampleInFlight = true
			cmds = append(cmds, m.runSamplesCmd())
		}
		return m, tea.Batch(cmds...)

	case splitSampleMsg:
		m.summary = msg.summary
		m.haveSummary = true
		m.sampleInFlight = false
		if m.untilPass && msg.summary.AllPassed {
			return m, tea.Quit
		}
		return m, nil

	default:
		// KeyMsg / chatLineMsg / streamEndMsg などは chat に委譲し、Cmd を伝播する。
		// chat が Ctrl+C/Ctrl+D で tea.Quit を返したら全体が終了する。
		cm, cmd := m.chat.Update(msg)
		m.chat = cm.(*chatModel)
		return m, cmd
	}
}

func (m *startSplitModel) View() string {
	if !m.ready {
		return ""
	}
	// chat ペインは割り当て高さにパディングして、ヘルプを最下部に固定する。
	chatPane := lipgloss.NewStyle().Height(m.chatHeight()).MaxHeight(m.chatHeight()).Render(m.chat.View())
	return lipgloss.JoinVertical(lipgloss.Left,
		m.renderWatchPane(),
		chatPane,
		splitHelpStyle.Render("Enter 送信 · Ctrl+D/Ctrl+C 終了 · 保存で上ペイン再判定"),
	)
}

// renderWatchPane は watch ペイン (splitTopLines 行: タイトル + 要約 + 区切り線) を返す。
func (m *startSplitModel) renderWatchPane() string {
	title := splitWatchTitleStyle.Render("watch") + "  " + splitHelpStyle.Render(m.solutionPath)
	rule := splitRuleStyle.Render(strings.Repeat("─", maxInt(m.width, 1)))
	return strings.Join([]string{title, m.renderSummaryLine(), rule}, "\n")
}

// renderSummaryLine は現在のサンプル要約 1 行を着色して返す。ペイン幅を超えたら
// 末尾を … で切り詰めて 1 行を保つ (上ペインの行数を増やさない)。
func (m *startSplitModel) renderSummaryLine() string {
	if !m.haveSummary {
		return splitHelpStyle.Render("  judging…")
	}
	line := "  " + formatSampleSummary(m.summary)
	return ansi.Truncate(line, maxInt(m.width, 1), "…")
}

// formatSampleSummary は SampleSummary を per-case verdict 付きの 1 行に整える純粋関数。
//
//	例: "✗ 2/4   01 AC  02 WA  03 TLE  04 AC   · 12:35:10"
//
// AC は緑、WA/TLE/RE は赤。着色は lipgloss で当て、非 TTY (テスト) では素のテキストに落ちる。
func formatSampleSummary(s SampleSummary) string {
	if s.Err != nil {
		return splitFailStyle.Render("判定不可: " + s.Err.Error())
	}
	var b strings.Builder
	// 全体グリフ + passed/total。全 AC なら緑 ✓、未達なら赤 ✗。
	overall := fmt.Sprintf("%d/%d", s.Passed, s.Total)
	if s.AllPassed {
		b.WriteString(splitPassStyle.Render("✓ " + overall))
	} else {
		b.WriteString(splitFailStyle.Render("✗ " + overall))
	}
	// per-case verdict。
	for _, c := range s.Cases {
		b.WriteString("  " + splitHelpStyle.Render(c.Name) + " ")
		if c.OK {
			b.WriteString(splitPassStyle.Render(c.Label))
		} else {
			b.WriteString(splitFailStyle.Render(c.Label))
		}
	}
	if !s.At.IsZero() {
		b.WriteString(splitHelpStyle.Render("  · " + s.At.Format("15:04:05")))
	}
	return b.String()
}

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}
