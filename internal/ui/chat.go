package ui

import (
	"bufio"
	"fmt"
	"math"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/cry999/atcoder-daily-training/internal/runner"
)

// ChatHeader は TUI ヘッダに出すメタ情報 + 起動オプション。
type ChatHeader struct {
	Task        string
	Contest     string
	TimeLimitMs int
	Debug       bool // true なら子の stdout 行のうち [DEBUG] プレフィックスを持つものを別カテゴリで表示する
	AutoRestart bool // true なら起動時から sticky auto-restart (子終了のたびに再起動する)
}

// Spawner は子プロセスを (再) 起動するためのファクトリ。
// chat TUI は連続テスト用にこれを複数回呼び出すことがある。
type Spawner func() (*runner.ChatHandle, error)

// RunChat は spawner で子プロセスを起動し、対話 TUI を駆動する。
// header.AutoRestart が真なら、子が終了するたびに spawner を再呼び出して新セッション
// を始める (sticky)。偽なら子終了で TUI を閉じる。最終的に最後の (= 現在の) セッション
// の ProcessResult を返す。
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
	handle        *runner.ChatHandle
	spawn         Spawner // 再起動時に呼ぶ。nil なら再起動不可
	header        ChatHeader
	input         textinput.Model
	viewport      viewport.Model
	msgs          []chatLine
	history       []string
	historyPos    int // history[historyPos] = 次に Up で出す候補。len(history) なら未編集状態。
	outScanner    *bufio.Scanner
	errScanner    *bufio.Scanner
	endedOut      bool
	endedErr      bool
	autoRestart   bool      // sticky モード。起動フラグ (--auto-restart) で初期化。streamEndMsg は自動で restart() を発火
	autoHintShown bool      // auto-restart ヒント表示済みフラグ
	sessionN      int       // 1 始まり。restart で incr して区切りに番号を出す
	lastEventAt   time.Time // 最後の入力送信 or 出力受信の時刻 (出力行の経過時間の基準)
	width         int
	height        int
	ready         bool
}

func initialChatModel(handle *runner.ChatHandle, header ChatHeader, spawn Spawner) *chatModel {
	ti := textinput.New()
	ti.Placeholder = "Enter で送信  /  Ctrl+C か Ctrl+D で終了"
	ti.Focus()
	ti.Prompt = "" // プロンプト記号は View 側で描画する

	outScan := bufio.NewScanner(handle.Stdout)
	outScan.Buffer(make([]byte, 64*1024), 1024*1024)
	errScan := bufio.NewScanner(handle.Stderr)
	errScan.Buffer(make([]byte, 64*1024), 1024*1024)

	m := &chatModel{
		handle:      handle,
		spawn:       spawn,
		header:      header,
		input:       ti,
		historyPos:  0,
		outScanner:  outScan,
		errScanner:  errScan,
		sessionN:    1,
		lastEventAt: time.Now(),
		autoRestart: header.AutoRestart && spawn != nil,
	}
	// auto-restart 指定時は起動直後に一度だけヒントを出す。
	if m.autoRestart {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(auto-restart on — Ctrl+C or Ctrl+D to stop)"})
		m.autoHintShown = true
	}
	return m
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
	m.lastEventAt = time.Now() // 新セッション開始を経過時間の基準にリセット
	m.sessionN++
	m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: fmt.Sprintf("─── session #%d ───", m.sessionN)})
	// auto-restart 突入時の一回だけヒントを出す。
	if m.autoRestart && !m.autoHintShown {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(auto-restart on — Ctrl+C or Ctrl+D to stop)"})
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
		switch msg.Type {
		case tea.KeyCtrlC, tea.KeyCtrlD:
			// Ctrl+C / Ctrl+D はどちらも chat の終了。子を kill して quit する
			// (子に EOF は送らない)。両キーに区別は無い (要件 022)。auto-restart 中も
			// 即 quit (現セッションの完了は待たない)。
			_ = m.handle.Kill()
			return m, tea.Quit
		case tea.KeyEnter:
			txt := m.input.Value()
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
			// 再起動するかどうかは起動フラグ (--auto-restart) で確定済みなので、
			// ここで対話的に選ばせることはしない (終了後プロンプトは廃止)。
			if m.autoRestart && m.spawn != nil {
				// プロンプト無しでそのまま再起動。
				return m, m.restart()
			}
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(child process exited)"})
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
			sb.WriteString(leadCol(msg) + chatInPromptStyle.Render("→") + " " + chatInTextStyle.Render(msg.text))
		case kindOut:
			sb.WriteString(leadCol(msg) + chatOutPromptStyle.Render("←") + " " + chatOutTextStyle.Render(msg.text))
		case kindDebug:
			sb.WriteString(leadCol(msg) + chatDebugPromptStyle.Render("*") + " " + chatDebugTextStyle.Render(msg.text))
		case kindErr:
			sb.WriteString(leadCol(msg) + chatErrPromptStyle.Render("✖") + " " + chatErrTextStyle.Render(msg.text))
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

// durWidth は経過時間を右寄せで揃える固定幅 (最大は "9999ms" の 6 桁)。
const durWidth = 6

// leadCol は行頭の固定幅カラムを返す。出力行は dim な経過時間を右寄せで、
// 経過情報の無い行 (入力 →) は同じ幅の空白で埋めて、矢印の桁を揃える。
// いずれも末尾にスペース 1 つを足して矢印と区切る。
func leadCol(line chatLine) string {
	if !line.hasDur {
		return strings.Repeat(" ", durWidth) + " "
	}
	return chatTimeStyle.Render(fmt.Sprintf("%*s", durWidth, formatDur(line.dur))) + " "
}

// formatDur は経過時間を「最大単位のみ・それ以下は四捨五入」で表す。負値は 0 に丸める。
// ただし 10,000ms 未満は s ではなく ms で出す (1100ms は "1100ms"、10s は "10s")。
//
//	>= 10s        → "10s"   (秒に四捨五入)
//	1ms 〜 <10s   → "1100ms" (ms に四捨五入)
//	1µs 〜 <1ms   → "340µs"  (µs に四捨五入)
//	< 1µs         → "0" / "830ns"
func formatDur(d time.Duration) string {
	if d < 0 {
		d = 0
	}
	switch {
	case d == 0:
		return "0"
	case d >= 10*time.Second:
		return fmt.Sprintf("%ds", int64(math.Round(d.Seconds())))
	case d >= time.Millisecond:
		return fmt.Sprintf("%dms", int64(math.Round(float64(d)/float64(time.Millisecond))))
	case d >= time.Microsecond:
		return fmt.Sprintf("%dµs", int64(math.Round(float64(d)/float64(time.Microsecond))))
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
