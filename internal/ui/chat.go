package ui

import (
	"bufio"
	"fmt"
	"strings"

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
}

// RunChat は与えられた ChatHandle で対話 TUI を駆動し、子プロセスが終了したら
// runner.ProcessResult を返す。利用側 (runexec) はその結果を Reporter に流す。
func RunChat(handle *runner.ChatHandle, header ChatHeader) (*runner.ProcessResult, error) {
	prog := tea.NewProgram(initialChatModel(handle, header))
	if _, err := prog.Run(); err != nil {
		return nil, err
	}
	// Run() が返った時点で TUI は終了している。Wait() で終了コードと経過時間を得る。
	return handle.Wait(), nil
}

const (
	kindIn    = "in"
	kindOut   = "out"
	kindErr   = "err"
	kindInfo  = "info"
	kindEnded = "ended"
)

type chatLineMsg struct {
	kind string
	text string
}

type streamEndMsg struct {
	kind string // "out" or "err"
}

type chatLine struct {
	kind string
	text string
}

type chatModel struct {
	handle      *runner.ChatHandle
	header      ChatHeader
	input       textinput.Model
	viewport    viewport.Model
	msgs        []chatLine
	history     []string
	historyPos  int // history[historyPos] = 次に Up で出す候補。len(history) なら未編集状態。
	stdinClosed bool
	outScanner  *bufio.Scanner
	errScanner  *bufio.Scanner
	endedOut    bool
	endedErr    bool
	width       int
	height      int
	ready       bool
}

func initialChatModel(handle *runner.ChatHandle, header ChatHeader) *chatModel {
	ti := textinput.New()
	ti.Placeholder = "Enter で送信  /  Ctrl+D で stdin を閉じる  /  Ctrl+C で中断"
	ti.Focus()
	ti.Prompt = "" // プロンプト記号は View 側で描画する

	outScan := bufio.NewScanner(handle.Stdout)
	outScan.Buffer(make([]byte, 64*1024), 1024*1024)
	errScan := bufio.NewScanner(handle.Stderr)
	errScan.Buffer(make([]byte, 64*1024), 1024*1024)

	return &chatModel{
		handle:     handle,
		header:     header,
		input:      ti,
		historyPos: 0,
		outScanner: outScan,
		errScanner: errScan,
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
			return chatLineMsg{kind: kind, text: scanner.Text()}
		}
		return streamEndMsg{kind: kind}
	}
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
		switch msg.Type {
		case tea.KeyCtrlC:
			_ = m.handle.Kill()
			return m, tea.Quit
		case tea.KeyCtrlD:
			if !m.stdinClosed {
				_ = m.handle.Stdin.Close()
				m.stdinClosed = true
				m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(stdin closed)"})
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
		m.msgs = append(m.msgs, chatLine{kind: msg.kind, text: msg.text})
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
	parts = append(parts, m.renderInputLine())
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

func (m *chatModel) refreshViewport() {
	if !m.ready {
		return
	}
	var sb strings.Builder
	for _, msg := range m.msgs {
		switch msg.kind {
		case kindIn:
			sb.WriteString(chatInPromptStyle.Render("→") + " " + chatInTextStyle.Render(msg.text))
		case kindOut:
			sb.WriteString(chatOutPromptStyle.Render("←") + " " + msg.text)
		case kindErr:
			sb.WriteString(chatErrPromptStyle.Render("✖") + " " + chatErrTextStyle.Render(msg.text))
		case kindInfo:
			sb.WriteString(infoStyle.Render(msg.text))
		}
		sb.WriteString("\n")
	}
	content := sb.String()
	m.viewport.SetContent(content)

	// 高さを content の行数に合わせる (上限は端末高 - ヘッダ - 入力)。
	// これで scrollback が少ないうちは入力ボックスが画面の上の方に出て、
	// メッセージが増えてくると下に拡がり、上限に達したら viewport が scroll する。
	lines := strings.Count(content, "\n")
	if lines < 1 {
		lines = 1
	}
	if max := m.maxViewportHeight(); lines > max {
		lines = max
	}
	m.viewport.Height = lines
	m.viewport.GotoBottom()
}

// maxViewportHeight は scrollback (viewport) に割ける最大行数。
// 端末高 - header 行数 - 入力行 (1) を返す。下限は 1。
func (m *chatModel) maxViewportHeight() int {
	if m.height <= 0 {
		return 1
	}
	headerH := strings.Count(m.renderHeader(), "\n") + 1
	inputH := 1
	h := m.height - headerH - inputH
	if h < 1 {
		h = 1
	}
	return h
}

// chat 専用のスタイル (style.go に置いてもよいが chat だけで使うので近くに置く)。
var (
	chatInputPromptStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSapphire)).Bold(true)
	chatInPromptStyle    = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaBlue)).Bold(true)
	chatInTextStyle      = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaText))
	chatOutPromptStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaGreen)).Bold(true)
	chatErrPromptStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)
	chatErrTextStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaMaroon))
)
