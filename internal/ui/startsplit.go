package ui

import (
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/viewport"
	"github.com/charmbracelet/lipgloss"
	"github.com/charmbracelet/x/ansi"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/watch"
)

// CaseVerdict は 1 サンプルケースの判定結果 (watch ペインの per-case 表示用)。
type CaseVerdict struct {
	Name  string // ケース名 (例 "01")
	Label string // "AC" / "WA" / "TLE" / "RE"
	OK    bool   // AC (Pass) なら true。色分けに使う
	// 詳細表示 (Ctrl+G) 用。失敗ケース (OK==false) のときだけ start.go がセットする
	// (AC は空)。判定の I/O は CaseResult が既に持つものを運ぶだけ。要件 034。
	Input    string
	Expected string
	Actual   string
	Stderr   string        // RE のみ
	Elapsed  time.Duration // 実行時間
}

// SampleSummary は分割画面 watch ペインのコンパクト要約 (diff は含まない)。
type SampleSummary struct {
	Passed, Total int
	Cases         []CaseVerdict // ケース名順の per-case verdict
	AllPassed     bool          // 全通過 (Total>0 && Passed==Total かつ判定成功)
	At            time.Time     // 判定時刻
	Err           error         // 判定自体が失敗 (テスト無し等)
}

// StartTarget は分割画面 1 つ分のターゲット (初期起動・再ターゲット共通)。要件 027。
// layout 解決・着手 (空ファイル生成)・runner spawn は cmd/atcoder が済ませて組み立てる
// (internal/ui は cmd/atcoder を import できない層境界を保つ)。
type StartTarget struct {
	ContestID, Task string
	SolutionPath    string
	Spawn           Spawner                        // chat 用の子プロセス起動 (auto-restart)
	Header          ChatHeader                     // NavEnabled=true で渡す
	RunSamples      func(debug bool) SampleSummary // サンプル再判定 (stdout に書かない)。debug は live Debug 値 (要件 034)
	Watcher         *watch.Watcher                 // 解答ファイルの保存検知
	InfoLines       []string                       // 再ターゲット時に chat へ出す案内行 (移動先 + 着手)
}

// Navigate は現ターゲットと要求から次のターゲットを解決する (cmd/atcoder が注入)。
// 境界・非対応・不正 spec は error (TUI 内 1 行表示に使う)。internal/ui は中身を知らない。
type Navigate func(contestID, task string, req NavRequest) (StartTarget, error)

// StartSplitConfig は分割画面の起動設定。初期ターゲット (Initial) と、コマンドモードの
// ナビゲーション解決 (Navigate) を受け取る。Navigate が nil ならナビは無効。
type StartSplitConfig struct {
	Initial   StartTarget   // 起動時の問題
	Navigate  Navigate      // :task/:contest/:e の解決 (nil ならナビ無効)
	UntilPass bool          // 全通過で終了
	Poll      time.Duration // 保存検知のポーリング間隔 (0 → 既定)
}

// 分割画面のレイアウト予約行数。
const (
	splitTopLines  = 3 // watch ペイン: タイトル + 要約 + 区切り線
	splitHelpLines = 1 // 最下部のキーヘルプ
)

type splitTickMsg struct{}

// DebugMsg は chat ペインが親 (startSplitModel) に Debug 変化を伝える tea.Msg (要件 034)。
// chat の :debug / :set debug|nodebug (要件 030) が発火し、親は watch ペインの live Debug を
// 更新して再判定する。分割画面でない単体 chat (test --interactive) では受け手がいないので無害。
type DebugMsg struct{ On bool }

// splitSampleMsg は非同期サンプル判定の結果。epoch は発行時の再ターゲット世代で、
// 現行と不一致なら旧ターゲットの遅延結果として破棄する (要件 027 の target epoch)。
type splitSampleMsg struct {
	summary SampleSummary
	epoch   int
}

type startSplitModel struct {
	chat         *chatModel
	contestID    string // 現ターゲットの contest_id (ナビ解決の起点)
	task         string // 現ターゲットの task_id (ナビ解決の起点)
	solutionPath string
	runSamples   func(debug bool) SampleSummary
	changed      func() bool
	navigate     Navigate // nil ならナビ無効
	untilPass    bool
	poll         time.Duration
	debug        bool // live Debug 値 (chat の :debug で変わる)。watch 再判定の Debug に渡す (要件 034)

	summary        SampleSummary
	haveSummary    bool
	sampleInFlight bool
	epoch          int // 再ターゲット世代。旧ターゲットの遅延サンプル結果を破棄する

	detail   bool           // 詳細オーバーレイ表示中 (Ctrl+G)。失敗ケースの diff を出す。要件 034
	detailVP viewport.Model // 詳細表示のスクロール viewport

	width, height int
	ready         bool
}

var (
	splitWatchTitleStyle = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#74c7ec"))
	splitPassStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color("#a6e3a1"))
	splitFailStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color("#f38ba8"))
	splitRuleStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color("#45475a"))
	splitHelpStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color("#7f849c")).Italic(true)
	// [debug] バッジ。chat の debug 色 (mochaLavender) に揃えて Debug の一貫性を示す (要件 034)。
	splitDebugBadgeStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaLavender)).Bold(true)
)

// RunStartSplit は上下分割の bubbletea プログラムを駆動する。
// 終了コード: Ctrl+C / Ctrl+D / --until-pass 全通過 = 0。
func RunStartSplit(cfg StartSplitConfig) (int, error) {
	poll := cfg.Poll
	if poll <= 0 {
		poll = 250 * time.Millisecond
	}
	t := cfg.Initial
	// 下ペインの chat は遅延起動 (入力が来るまで子を起動しない)。
	m := &startSplitModel{
		chat:         initialChatModel(t.Header, t.Spawn),
		contestID:    t.ContestID,
		task:         t.Task,
		solutionPath: t.SolutionPath,
		runSamples:   t.RunSamples,
		changed:      changedFunc(t.Watcher),
		navigate:     cfg.Navigate,
		untilPass:    cfg.UntilPass,
		poll:         poll,
		debug:        t.Header.Debug, // 起動時 -d を初期 live Debug にする (要件 034)
	}
	if _, err := tea.NewProgram(m, tea.WithAltScreen()).Run(); err != nil {
		return 1, err
	}
	return 0, nil
}

// changedFunc は watcher の保存検知 closure を返す (watcher が nil なら nil)。
func changedFunc(w *watch.Watcher) func() bool {
	if w == nil {
		return nil
	}
	return w.Changed
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
	debug := m.debug // 発行時の live Debug を焼き込む (再判定はこの Debug で行う。要件 034)
	epoch := m.epoch // 発行時の世代を焼き込む (再ターゲット後の遅延結果を破棄するため)
	return func() tea.Msg { return splitSampleMsg{summary: run(debug), epoch: epoch} }
}

// retarget は移動先ターゲットに watch ペイン・chat ペインを切り替える (要件 027)。
// 旧 chat の子を片付け、chat を新ターゲットで作り直し (遅延起動を維持)、watch 要約を
// リセットして 1 回サンプル判定する。epoch を進めて旧ターゲットの遅延結果は破棄する。
func (m *startSplitModel) retarget(t StartTarget) tea.Cmd {
	m.chat.shutdown() // 旧問題の子プロセスを kill+wait

	m.contestID = t.ContestID
	m.task = t.Task
	m.solutionPath = t.SolutionPath
	m.runSamples = t.RunSamples
	m.changed = changedFunc(t.Watcher)

	// chat を新ターゲットで作り直す (遅延起動: 入力が来るまで子は起動しない)。
	// live Debug (実行中の :debug トグル結果) を引き継ぐ。t.Header.Debug は起動時 -d の
	// 値なので、上書きして chat 表示と watch 判定の Debug を揃える (要件 034)。
	t.Header.Debug = m.debug
	m.chat = initialChatModel(t.Header, t.Spawn)
	var cmds []tea.Cmd
	if m.ready {
		// 現在のウィンドウサイズで再レイアウトする (chat を ready にして viewport を作る)。
		cm, cmd := m.chat.Update(tea.WindowSizeMsg{Width: m.width, Height: m.chatHeight()})
		m.chat = cm.(*chatModel)
		cmds = append(cmds, cmd)
	}
	cmds = append(cmds, m.chat.Init())
	for _, line := range t.InfoLines {
		m.chat.addInfoLine(line)
	}
	m.chat.refreshViewport()

	// watch 要約を未判定に戻し、新ターゲットで 1 回判定する (初回判定で lazy fetch)。
	m.summary = SampleSummary{}
	m.haveSummary = false
	m.epoch++
	m.sampleInFlight = true
	cmds = append(cmds, m.runSamplesCmd())
	return tea.Batch(cmds...)
}

func (m *startSplitModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width, m.height = msg.Width, msg.Height
		m.ready = true
		// chat には watch + help を引いた高さを渡す。
		cm, cmd := m.chat.Update(tea.WindowSizeMsg{Width: msg.Width, Height: m.chatHeight()})
		m.chat = cm.(*chatModel)
		if m.detail { // 詳細オーバーレイ表示中ならそのサイズも追従させる。
			m.detailVP.Width = maxInt(m.width, 1)
			m.detailVP.Height = maxInt(m.height-detailChromeLines, 1)
			m.detailVP.SetContent(m.buildDetailContent())
		}
		return m, cmd

	case tea.KeyMsg:
		// 詳細オーバーレイ表示中はキーを横取りする (chat には渡さない)。要件 034。
		if m.detail {
			switch msg.Type {
			case tea.KeyCtrlG, tea.KeyEsc:
				m.detail = false // 閉じて分割画面へ戻る
			case tea.KeyPgUp:
				m.detailVP.ViewUp()
			case tea.KeyPgDown:
				m.detailVP.ViewDown()
			case tea.KeyUp:
				m.detailVP.LineUp(1)
			case tea.KeyDown:
				m.detailVP.LineDown(1)
			}
			return m, nil // 他のキーは無視 (chat に渡さない)
		}
		// 分割画面: Ctrl+G で詳細を開く。それ以外は従来どおり chat に委譲。
		if msg.Type == tea.KeyCtrlG {
			m.openDetail()
			return m, nil
		}
		cm, cmd := m.chat.Update(msg)
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
		if msg.epoch != m.epoch {
			return m, nil // 旧ターゲットの遅延サンプル結果 → 破棄
		}
		m.summary = msg.summary
		m.haveSummary = true
		m.sampleInFlight = false
		if m.detail { // 詳細表示中に再判定が来たら最新の失敗ケースで作り直す。
			m.detailVP.SetContent(m.buildDetailContent())
		}
		if m.untilPass && msg.summary.AllPassed {
			return m, tea.Quit
		}
		return m, nil

	case NavMsg:
		// コマンドモードのナビゲーション (要件 027)。注入された Navigate で移動先を解決し、
		// 成功なら再ターゲット、失敗 (境界・非対応・不正 spec) は chat に 1 行出して継続する。
		if m.navigate == nil {
			return m, nil
		}
		target, err := m.navigate(m.contestID, m.task, msg.Req)
		if err != nil {
			m.chat.addErrLine("(" + err.Error() + ")")
			m.chat.refreshViewport()
			return m, nil
		}
		return m, m.retarget(target)

	case DebugMsg:
		// chat の :debug トグル (要件 030) を watch ペインへ波及させる (要件 034)。live Debug を
		// 更新し、新 Debug で即再判定する。in-flight の旧判定 (旧 Debug) は epoch を進めて破棄し、
		// stale な結果で上書きされないようにする (要件 027 の target epoch を Debug 変化に流用)。
		if m.debug == msg.On {
			return m, nil // 値が変わっていなければ再判定しない
		}
		m.debug = msg.On
		m.epoch++
		m.sampleInFlight = true
		return m, m.runSamplesCmd()

	default:
		// KeyMsg / chatLineMsg / streamEndMsg などは chat に委譲し、Cmd を伝播する。
		// chat が Ctrl+C/Ctrl+D で tea.Quit を返したら全体が終了する。
		cm, cmd := m.chat.Update(msg)
		m.chat = cm.(*chatModel)
		return m, cmd
	}
}

// detailChromeLines は詳細オーバーレイのヘッダ + フッタの行数 (viewport 高さの控除分)。
const detailChromeLines = 2

// openDetail は詳細オーバーレイを開く。現在の summary の失敗ケースから内容を組み、
// 詳細用 viewport に流して先頭から見せる。要件 034。
func (m *startSplitModel) openDetail() {
	m.detail = true
	m.detailVP = viewport.New(maxInt(m.width, 1), maxInt(m.height-detailChromeLines, 1))
	m.detailVP.SetContent(m.buildDetailContent())
	m.detailVP.GotoTop()
}

// buildDetailContent は失敗ケース (WA/TLE/RE) の詳細を 1 つの文字列に組む。
// WA/TLE は renderDiff (期待 vs 実際)、RE は stderr。AC は省略。表示のみ (純粋)。
func (m *startSplitModel) buildDetailContent() string {
	if !m.haveSummary {
		return splitHelpStyle.Render("  (まだ判定結果がありません)")
	}
	if m.summary.Err != nil {
		return splitFailStyle.Render("  (判定できません: " + m.summary.Err.Error() + ")")
	}
	var b strings.Builder
	fails := 0
	for _, c := range m.summary.Cases {
		if c.OK {
			continue // AC は省略
		}
		if fails > 0 {
			b.WriteString("\n\n")
		}
		fails++
		b.WriteString(splitFailStyle.Render("["+c.Name+"] "+c.Label) + splitHelpStyle.Render("  "+formatDur(c.Elapsed)) + "\n")
		if c.Label == "RE" {
			st := strings.TrimRight(c.Stderr, "\n")
			if st == "" {
				st = "(stderr なし)"
			}
			for _, ln := range strings.Split(st, "\n") {
				b.WriteString("  " + ln + "\n")
			}
		} else {
			b.WriteString(renderDiff(c.Expected, c.Actual, true))
		}
	}
	if fails == 0 {
		return splitHelpStyle.Render("  (失敗ケースはありません)")
	}
	return b.String()
}

// renderDetailView は詳細オーバーレイ (ヘッダ + 詳細 viewport + フッタ) を描画する。
func (m *startSplitModel) renderDetailView() string {
	title := splitWatchTitleStyle.Render("詳細 (失敗ケース)") + "  " + splitHelpStyle.Render(m.task)
	footer := splitHelpStyle.Render("Ctrl+G/Esc で戻る · PageUp/PageDown/↑/↓ でスクロール")
	return lipgloss.JoinVertical(lipgloss.Left, title, m.detailVP.View(), footer)
}

func (m *startSplitModel) View() string {
	if !m.ready {
		return ""
	}
	if m.detail {
		return m.renderDetailView()
	}
	// chat ペインは割り当て高さにパディングして、ヘルプを最下部に固定する。
	chatPane := lipgloss.NewStyle().Height(m.chatHeight()).MaxHeight(m.chatHeight()).Render(m.chat.View())
	return lipgloss.JoinVertical(lipgloss.Left,
		m.renderWatchPane(),
		chatPane,
		splitHelpStyle.Render("Enter 送信 · Ctrl+G 詳細 · Ctrl+D/Ctrl+C 終了 · 保存で上ペイン再判定"),
	)
}

// renderWatchPane は watch ペイン (splitTopLines 行: タイトル + 要約 + 区切り線) を返す。
func (m *startSplitModel) renderWatchPane() string {
	title := splitWatchTitleStyle.Render("watch") + "  " + splitHelpStyle.Render(m.solutionPath)
	if m.debug {
		// live Debug on を示すバッジ (chat の :debug と同期。要件 034)。タイトル行内に収め、
		// watch ペインを 3 行 (splitTopLines) に保つ。
		title += "  " + splitDebugBadgeStyle.Render("[debug]")
	}
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
