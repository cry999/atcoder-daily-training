package ui

import (
	"bufio"
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

// ChatHeader は TUI ヘッダに出すメタ情報。
type ChatHeader struct {
	Task        string
	Contest     string
	TimeLimitMs int
	Debug       bool // true なら子の stdout 行のうち [DEBUG] プレフィックスを持つものを別カテゴリで表示する
}

// Spawner は子プロセスを (再) 起動するためのファクトリ。
// chat TUI は連続テスト用にこれを複数回呼び出すことがある。
type Spawner func() (*runner.ChatHandle, error)

// RunChat は spawner で子プロセスを起動し、対話 TUI を駆動する。
// TUI 内でユーザーが [r] を押すと spawner が再呼び出され、新セッションが始まる。
// 最終的に最後の (= 現在の) セッションの ProcessResult を返す。
func RunChat(spawn Spawner, header ChatHeader) (*runner.ProcessResult, error) {
	handle, err := spawn()
	if err != nil {
		return nil, err
	}
	model := initialChatModel(handle, header, spawn)
	finalModel, err := tea.NewProgram(model).Run()
	if err != nil {
		return nil, err
	}
	cm, ok := finalModel.(*chatModel)
	if !ok || cm.handle == nil {
		return handle.Wait(), nil
	}
	return cm.handle.Wait(), nil
}

const (
	kindIn    = "in"
	kindOut   = "out"
	kindDebug = "debug" // [DEBUG] プレフィックスを持つ stdout 行 (Debug が true のときだけ振り分け)
	kindErr   = "err"
	kindInfo  = "info"
	kindEnded = "ended"
)

// debugPrefix は子の stdout 行を debug 出力として扱うかの判定マーカー。
// runexec の splitDebug と同じ規約 (test/run の batch モードと整合させる)。
const debugPrefix = "[DEBUG]"

type chatLineMsg struct {
	kind string
	text string
	at   time.Time // 行を読み出した時刻 (出力行の経過時間算出に使う)
}

type streamEndMsg struct {
	kind string // "out" or "err"
}

type chatLine struct {
	kind   string
	text   string
	dur    time.Duration // 直前イベントからの経過時間 (出力行のみ)
	hasDur bool          // dur が有効か (入力行 / 情報行は false)
}

type chatModel struct {
	handle          *runner.ChatHandle
	spawn           Spawner // 再起動時に呼ぶ。nil なら再起動不可
	header          ChatHeader
	input           textinput.Model
	viewport        viewport.Model
	msgs            []chatLine
	history         []string
	historyPos      int // history[historyPos] = 次に Up で出す候補。len(history) なら未編集状態。
	stdinClosed     bool
	outScanner      *bufio.Scanner
	errScanner      *bufio.Scanner
	endedOut        bool
	endedErr        bool
	awaitingRestart bool      // 子終了後の "press [r] to restart / any other key to quit" 待ち状態
	autoRestart     bool      // R 押下後の sticky モード。以後 streamEndMsg は自動で restart() を発火
	autoHintShown   bool      // auto-restart 突入時のヒント表示済みフラグ
	quitOnChildExit bool      // Ctrl+D で auto-restart を解除したあと、次の child 終了で素直に Quit する
	sessionN        int       // 1 始まり。restart で incr して区切りに番号を出す
	lastEventAt     time.Time // 最後の入力送信 or 出力受信の時刻 (出力行の経過時間の基準)
	width           int
	height          int
	ready           bool
}

func initialChatModel(handle *runner.ChatHandle, header ChatHeader, spawn Spawner) *chatModel {
	ti := textinput.New()
	ti.Placeholder = "Enter で送信  /  Ctrl+D で stdin を閉じる  /  Ctrl+C で中断"
	ti.Focus()
	ti.Prompt = "" // プロンプト記号は View 側で描画する

	outScan := bufio.NewScanner(handle.Stdout)
	outScan.Buffer(make([]byte, 64*1024), 1024*1024)
	errScan := bufio.NewScanner(handle.Stderr)
	errScan.Buffer(make([]byte, 64*1024), 1024*1024)

	return &chatModel{
		handle:      handle,
		spawn:       spawn,
		header:      header,
		input:       ti,
		historyPos:  0,
		outScanner:  outScan,
		errScanner:  errScan,
		sessionN:    1,
		lastEventAt: time.Now(),
	}
}

func (m *chatModel) Init() tea.Cmd {
	return tea.Batch(
		textinput.Blink,
		readLineCmd(m.outScanner, kindOut),
		readLineCmd(m.errScanner, kindErr),
	)
}

// readLineCmd は scanner から 1 行 (or EOF) を読み、対応する msg を返す tea.Cmd。
// 各行読み出しごとに自身を再発行することで継続的に stream を吸い出す
// (Update 側が chatLineMsg を受けたら readLineCmd を Cmd として返す)。
func readLineCmd(scanner *bufio.Scanner, kind string) tea.Cmd {
	return func() tea.Msg {
		if scanner.Scan() {
			// 経過時間を正確にするため、行が読めた瞬間の時刻を記録する
			// (Update 側の処理遅延を含めない)。
			return chatLineMsg{kind: kind, text: scanner.Text(), at: time.Now()}
		}
		return streamEndMsg{kind: kind}
	}
}

// restart は spawner で新しい子プロセスを起動し、TUI 側の状態をリセットする。
// scrollback は保持し、区切り行 (── session #N ──) を追加してから新セッションを始める。
func (m *chatModel) restart() tea.Cmd {
	// 前セッションのハンドルを reap (既に終了しているのですぐ返る)。
	if m.handle != nil {
		_ = m.handle.Wait()
	}
	newHandle, err := m.spawn()
	if err != nil {
		m.msgs = append(m.msgs, chatLine{kind: kindErr, text: "restart failed: " + err.Error()})
		m.refreshViewport()
		return tea.Quit
	}
	m.handle = newHandle
	m.outScanner = bufio.NewScanner(newHandle.Stdout)
	m.outScanner.Buffer(make([]byte, 64*1024), 1024*1024)
	m.errScanner = bufio.NewScanner(newHandle.Stderr)
	m.errScanner.Buffer(make([]byte, 64*1024), 1024*1024)
	m.endedOut = false
	m.endedErr = false
	m.stdinClosed = false
	m.awaitingRestart = false
	m.lastEventAt = time.Now() // 新セッション開始を経過時間の基準にリセット
	m.sessionN++
	m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: fmt.Sprintf("─── session #%d ───", m.sessionN)})
	// auto-restart 突入時の一回だけヒントを出す。
	if m.autoRestart && !m.autoHintShown {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(auto-restart on — Ctrl+D to stop after current session, Ctrl+C to abort)"})
		m.autoHintShown = true
	}
	m.refreshViewport()
	return tea.Batch(
		readLineCmd(m.outScanner, kindOut),
		readLineCmd(m.errScanner, kindErr),
	)
}

func (m *chatModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmds []tea.Cmd

	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		if !m.ready {
			m.viewport = viewport.New(m.width, 1)
			m.ready = true
		} else {
			m.viewport.Width = m.width
		}
		m.input.Width = m.width - 4
		// viewport の高さは refreshViewport の中で content 行数 + maxViewportHeight()
		// から動的に決定する (空のあいだは入力ボックスを画面の上の方に出す)。
		m.refreshViewport()

	case tea.KeyMsg:
		// 子プロセス終了後の "press [r] to restart / any other key to quit" 待ちは
		// 通常のキー処理より先に処理する。
		// R 押下は sticky モードに突入: 以後は子終了するたびに自動再起動し、
		// 抜けるには現セッションで Ctrl+D (graceful) または Ctrl+C (kill) を使う。
		if m.awaitingRestart {
			for _, r := range msg.Runes {
				if r == 'r' || r == 'R' {
					m.autoRestart = true
					return m, m.restart()
				}
			}
			return m, tea.Quit
		}
		switch msg.Type {
		case tea.KeyCtrlC:
			_ = m.handle.Kill()
			return m, tea.Quit
		case tea.KeyCtrlD:
			if !m.stdinClosed {
				_ = m.handle.Stdin.Close()
				m.stdinClosed = true
				// auto-restart 中の Ctrl+D は「もう連続実行は不要、子が綺麗に
				// 終わったら quit」というシグナル。autoRestart を解除して
				// quitOnChildExit を立てる。
				if m.autoRestart {
					m.autoRestart = false
					m.quitOnChildExit = true
					m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(stdin closed; auto-restart disabled, exiting after this session)"})
				} else {
					m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(stdin closed)"})
				}
				m.refreshViewport()
			}
		case tea.KeyEnter:
			txt := m.input.Value()
			if m.stdinClosed {
				// stdin を閉じた後は送れない。
				m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(stdin closed; cannot send)"})
			} else {
				if _, err := fmt.Fprintln(m.handle.Stdin, txt); err != nil {
					m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(write failed: " + err.Error() + ")"})
				} else {
					m.msgs = append(m.msgs, chatLine{kind: kindIn, text: txt})
					m.lastEventAt = time.Now() // 入力を受け付けた時刻 = 次の出力の経過時間の基準
					if txt != "" {
						m.history = append(m.history, txt)
					}
					m.historyPos = len(m.history)
				}
			}
			m.input.SetValue("")
			m.refreshViewport()
		case tea.KeyUp:
			if len(m.history) > 0 && m.historyPos > 0 {
				m.historyPos--
				m.input.SetValue(m.history[m.historyPos])
				m.input.CursorEnd()
			}
		case tea.KeyDown:
			if m.historyPos < len(m.history)-1 {
				m.historyPos++
				m.input.SetValue(m.history[m.historyPos])
				m.input.CursorEnd()
			} else if m.historyPos == len(m.history)-1 {
				m.historyPos++
				m.input.SetValue("")
			}
		default:
			var cmd tea.Cmd
			m.input, cmd = m.input.Update(msg)
			cmds = append(cmds, cmd)
		}

	case chatLineMsg:
		kind, text := msg.kind, msg.text
		// -d 指定時のみ、stdout 行のうち [DEBUG] プレフィックスを持つものは
		// kindDebug に振り分け、プレフィックス (とその直後の半角空白 1 つ) を剥がす。
		// 表示側で独自のインジケーター・色を当てるため、prefix は冗長になる。
		if m.header.Debug && kind == kindOut && strings.HasPrefix(text, debugPrefix) {
			kind = kindDebug
			text = strings.TrimPrefix(text, debugPrefix)
			text = strings.TrimPrefix(text, " ")
		}
		line := chatLine{kind: kind, text: text}
		// 出力行 (stdout / debug / stderr) には直前イベントからの経過時間を添える。
		if kind == kindOut || kind == kindDebug || kind == kindErr {
			at := msg.at
			if at.IsZero() {
				at = time.Now()
			}
			d := at.Sub(m.lastEventAt)
			if d < 0 {
				d = 0
			}
			line.dur = d
			line.hasDur = true
			m.lastEventAt = at
		}
		m.msgs = append(m.msgs, line)
		m.refreshViewport()
		// 同じ stream の次行を読む Cmd を再発行して継続的に吸い出す。
		switch msg.kind {
		case kindOut:
			cmds = append(cmds, readLineCmd(m.outScanner, kindOut))
		case kindErr:
			cmds = append(cmds, readLineCmd(m.errScanner, kindErr))
		}

	case streamEndMsg:
		switch msg.kind {
		case kindOut:
			m.endedOut = true
		case kindErr:
			m.endedErr = true
		}
		if m.endedOut && m.endedErr {
			// 優先度: quitOnChildExit > autoRestart > prompt > fallback quit。
			if m.quitOnChildExit {
				return m, tea.Quit
			}
			if m.autoRestart && m.spawn != nil {
				// プロンプト無しでそのまま再起動。
				return m, m.restart()
			}
			if m.spawn != nil {
				m.awaitingRestart = true
				m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(child exited; press [r] to run again, any other key to quit)"})
				m.refreshViewport()
				return m, nil
			}
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(child process exited; press any key to close)"})
			m.refreshViewport()
			return m, tea.Quit
		}
	}

	return m, tea.Batch(cmds...)
}

func (m *chatModel) View() string {
	if !m.ready {
		return ""
	}
	// メッセージが無いときは viewport を描画せず、入力ボックスをヘッダの真下に置く。
	// 1 件でも出力 / 入力があれば viewport を含めてレンダリングする。
	parts := []string{m.renderHeader()}
	if len(m.msgs) > 0 {
		parts = append(parts, m.viewport.View())
	}
	parts = append(parts, m.renderInputBox())
	return strings.Join(parts, "\n")
}

func (m *chatModel) renderHeader() string {
	parts := []string{
		headerTitleStyle.Render(m.header.Task),
		keyStyle.Render("contest=") + valueStyle.Render(m.header.Contest),
		keyStyle.Render("time_limit=") + valueStyle.Render(fmt.Sprintf("%dms", m.header.TimeLimitMs)),
		infoStyle.Render("(interactive)"),
	}
	return strings.Join(parts, "  ")
}

func (m *chatModel) renderInputLine() string {
	prompt := chatInputPromptStyle.Render("» ")
	return prompt + m.input.View()
}

// renderInputBox は入力行を上下の罫線 (─) で挟んで返す (3 行)。
// Claude Code 風の subtle なボーダーで入力エリアを視覚的に区切る。
func (m *chatModel) renderInputBox() string {
	w := m.width
	if w < 1 {
		w = 1
	}
	rule := chatInputBorderStyle.Render(strings.Repeat("─", w))
	return rule + "\n" + m.renderInputLine() + "\n" + rule
}

func (m *chatModel) refreshViewport() {
	if !m.ready {
		return
	}
	// Note: メッセージ間は "\n" でつなぐが、末尾に "\n" は **付けない**。
	// viewport は content を strings.Split で行分割するため、末尾 "\n" があると
	// "空行" が 1 つカウントされて GotoBottom() がそこに飛び、本来の最終行
	// (= 直近で入力 / 出力したテキスト) が画面外に押し出される。
	var sb strings.Builder
	for i, msg := range m.msgs {
		if i > 0 {
			sb.WriteString("\n")
		}
		switch msg.kind {
		case kindIn:
			sb.WriteString(chatInPromptStyle.Render("→") + " " + chatInTextStyle.Render(msg.text))
		case kindOut:
			sb.WriteString(chatOutPromptStyle.Render("←") + " " + durPrefix(msg) + chatOutTextStyle.Render(msg.text))
		case kindDebug:
			sb.WriteString(chatDebugPromptStyle.Render("*") + " " + durPrefix(msg) + chatDebugTextStyle.Render(msg.text))
		case kindErr:
			sb.WriteString(chatErrPromptStyle.Render("✖") + " " + durPrefix(msg) + chatErrTextStyle.Render(msg.text))
		case kindInfo:
			sb.WriteString(infoStyle.Render(msg.text))
		}
	}
	content := sb.String()
	m.viewport.SetContent(content)

	// 高さを content の表示行数に合わせる。content が "" なら 1 行確保。
	// (msg.text 自体に "\n" を含むケースに備えて Count + 1 で数える)
	lines := 1
	if content != "" {
		lines = strings.Count(content, "\n") + 1
	}
	if max := m.maxViewportHeight(); lines > max {
		lines = max
	}
	m.viewport.Height = lines
	m.viewport.GotoBottom()
}

// durWidth は経過時間を右寄せで揃える固定幅 (例 "340µs" / "2.34s" が収まる)。
const durWidth = 7

// durPrefix は出力行の頭に添える dim な経過時間 (固定幅・末尾スペース付き)。
// 経過情報が無い行 (理論上ここには来ない) では空文字を返す。
func durPrefix(line chatLine) string {
	if !line.hasDur {
		return ""
	}
	return chatTimeStyle.Render(fmt.Sprintf("%*s", durWidth, formatDur(line.dur))) + " "
}

// formatDur は経過時間をコンパクトな適応書式にする。負値は 0 に丸める。
//
//	>= 1s        → "2.34s"
//	1ms 〜 1s    → "12ms" / 1 桁台は "1.2ms"
//	1µs 〜 1ms   → "340µs"
//	< 1µs        → "0" / "830ns"
func formatDur(d time.Duration) string {
	if d < 0 {
		d = 0
	}
	switch {
	case d >= time.Second:
		return fmt.Sprintf("%.2fs", d.Seconds())
	case d >= time.Millisecond:
		ms := float64(d) / float64(time.Millisecond)
		if ms < 10 {
			return fmt.Sprintf("%.1fms", ms)
		}
		return fmt.Sprintf("%.0fms", ms)
	case d >= time.Microsecond:
		return fmt.Sprintf("%dµs", d.Microseconds())
	case d == 0:
		return "0"
	default:
		return fmt.Sprintf("%dns", d.Nanoseconds())
	}
}

// maxViewportHeight は scrollback (viewport) に割ける最大行数。
// 端末高 - header 行数 - 入力エリア (上罫線 + 入力 + 下罫線 = 3 行) を返す。下限は 1。
func (m *chatModel) maxViewportHeight() int {
	if m.height <= 0 {
		return 1
	}
	headerH := strings.Count(m.renderHeader(), "\n") + 1
	inputH := 3 // top rule + input line + bottom rule
	h := m.height - headerH - inputH
	if h < 1 {
		h = 1
	}
	return h
}

// chat 専用のスタイル (style.go に置いてもよいが chat だけで使うので近くに置く)。
// インディケーターは行種別の「カテゴリ」を色で示し (Blue / Green / Red)、
// 本文は luminance のコントラストで「読みやすさの優先度」を表す:
//
//	入力 (自分で打ったもの)    : 本文を dim な overlay 色に落として控えめに
//	出力 (解答が返してきた内容): 本文を default text 色で最も明るく
//	エラー (stderr)             : Maroon 系を維持
//
// 入力 vs 出力 を色 (Blue vs Green) だけで分けようとすると、寒色同士で輪郭が
// 鈍るので、明暗差で組み合わせる。
var (
	chatInputPromptStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSapphire)).Bold(true)
	chatInputBorderStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0)) // 入力欄を上下から挟む subtle な罫線
	chatInPromptStyle    = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaBlue)).Bold(true)
	chatInTextStyle      = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay1)).Italic(true)
	chatOutPromptStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaGreen)).Bold(true)
	chatOutTextStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaText))
	chatDebugPromptStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaLavender)).Bold(true)
	chatDebugTextStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaLavender))
	chatErrPromptStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)
	chatErrTextStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaMaroon))
	// 出力行に添える経過時間。種別の色を邪魔しないよう最も dim な overlay 色。
	chatTimeStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0))
)
