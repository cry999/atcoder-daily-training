package ui

import (
	"strconv"
	"strings"

	"github.com/charmbracelet/bubbles/textarea"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/cry999/atcoder-daily-training/internal/extracase"
)

// chatMode は chat の入力モード (vim 風)。要件 024。
//
//	insert  : 既定。textinput にフォーカスし Enter で子に送信 (従来の chat)。
//	command : ex-command line (`:…`)。コマンドを 1 行打って Enter で実行。
//	builder : ケースビルダー (input/expected の textarea 2 ペイン)。
type chatMode int

const (
	modeInsert chatMode = iota
	modeCommand
	modeBuilder
)

// caseBuilder は `:case` で開く入出力ケースの作成画面。input/expected の
// 2 ペインを Tab で行き来する。子プロセスには一切触れない (作成中も会話は生きたまま)。
type caseBuilder struct {
	in    textarea.Model
	out   textarea.Model
	focus int // 0=input, 1=expected
}

// verifier はライブ検証の状態。expected を順序どおり子 stdout と突き合わせる。
type verifier struct {
	expected []string // 期待出力の行
	pos      int      // 次に照合する expected 行の index
	tol      float64
}

// newCommandInput は command モードの `:` 行用 textinput を作る。
func newCommandInput() textinput.Model {
	ti := textinput.New()
	ti.Prompt = ":"
	ti.Placeholder = "case | w [name] | set verify | debug | replay | cheat | q"
	return ti
}

// newCaseBuilder は input を現セッションの送信入力で前埋めしたビルダーを作る。
func newCaseBuilder(prefillIn []string) *caseBuilder {
	in := textarea.New()
	in.SetValue(strings.Join(prefillIn, "\n"))
	in.SetHeight(5)
	out := textarea.New()
	out.SetHeight(5)
	b := &caseBuilder{in: in, out: out, focus: 0}
	b.in.Focus()
	return b
}

func (b *caseBuilder) setWidth(w int) {
	if w < 10 {
		w = 10
	}
	b.in.SetWidth(w)
	b.out.SetWidth(w)
}

// active は今フォーカスされているペインを返す。
func (b *caseBuilder) active() *textarea.Model {
	if b.focus == 1 {
		return &b.out
	}
	return &b.in
}

// toggleFocus は input ⇄ expected のフォーカスを入れ替える。
func (b *caseBuilder) toggleFocus() {
	if b.focus == 0 {
		b.focus = 1
		b.in.Blur()
		b.out.Focus()
	} else {
		b.focus = 0
		b.out.Blur()
		b.in.Focus()
	}
}

// command は ex-command line をパースした結果 (純粋関数 parseCommand が返す)。
type command struct {
	name string // case / w / set / q / "" (空入力) / unknown
	arg  string // w の name、set の verify/noverify など
}

// parseCommand は `:` を除いたコマンド文字列を解釈する純粋関数。
// 別名 (c=case) を正規化し、最初の語を name、残りを arg にする。
func parseCommand(s string) command {
	f := strings.Fields(strings.TrimSpace(s))
	if len(f) == 0 {
		return command{name: ""}
	}
	name := f[0]
	arg := strings.TrimSpace(strings.TrimPrefix(strings.TrimSpace(s), name))
	switch name {
	case "c", "case":
		return command{name: "case", arg: arg}
	case "w", "write":
		return command{name: "w", arg: arg}
	case "set":
		return command{name: "set", arg: arg}
	case "q", "quit":
		return command{name: "q", arg: arg}
	case "task":
		// :task next|prev (n|p) で記号移動、:task <letter> で直指定。arg に第 2 トークンを載せる。
		return command{name: "task", arg: arg}
	case "contest":
		// :contest next|prev (n|p) で番号移動、:contest <num|id> で直指定。arg に第 2 トークンを載せる。
		return command{name: "contest", arg: arg}
	case "e", "edit":
		// :e <spec> — 任意ジャンプ。arg に spec を載せる (解決は親 Navigate)。
		return command{name: "e", arg: arg}
	case "debug":
		// :debug — Debug 表示 (-d 相当) をトグル。
		return command{name: "debug", arg: arg}
	case "cheat", "help", "?":
		// :cheat / :help / :? — 利用可能なコマンド一覧を表示。
		return command{name: "cheat", arg: arg}
	case "replay":
		// :replay — 同じ問題の前回セッション入力を、子をリスタートして順送 (要件 039)。
		return command{name: "replay", arg: arg}
	default:
		return command{name: "unknown", arg: name}
	}
}

// enterCommandMode は insert / builder から command モード (`:` 行) へ移る。
func (m *chatModel) enterCommandMode() tea.Cmd {
	m.mode = modeCommand
	m.cmdInput = newCommandInput()
	m.cmdCandidates = nil
	return m.cmdInput.Focus()
}

// updateCommand は command モードのキー処理。Enter で実行、Esc でキャンセル、Tab で補完。
func (m *chatModel) updateCommand(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	switch msg.Type {
	case tea.KeyEnter:
		cmd := parseCommand(m.cmdInput.Value())
		m.cmdCandidates = nil
		return m.execCommand(cmd)
	case tea.KeyPgUp:
		// scrollback を 1 ページ上へ (要件 033)。以降の出力で最下部に引き戻さない。
		m.scrollUp()
		return m, nil
	case tea.KeyPgDown:
		// 1 ページ下へ。最下部に達したら追従を再開する。
		m.scrollDown()
		return m, nil
	case tea.KeyEsc:
		// キャンセル: builder が開いていれば編集に戻る、なければ insert へ。
		// command モードを抜けるので上スクロールは解除し最下部 (最新) に戻す (要件 033)。
		m.cmdCandidates = nil
		m.scrolled = false
		m.viewport.GotoBottom()
		if m.builder != nil {
			m.mode = modeBuilder
		} else {
			m.mode = modeInsert
		}
		return m, nil
	case tea.KeyTab:
		// Tab 補完 (要件 031): 現トークンを最長共通プレフィックス/一意候補まで埋める。
		// 子プロセス・stdout には触れず `:` 行の文字列だけを編集する。
		repl, cands := completeCommandLine(m.cmdInput.Value(), m.header.NavEnabled)
		if repl != m.cmdInput.Value() {
			m.cmdInput.SetValue(repl)
			m.cmdInput.CursorEnd()
		}
		m.cmdCandidates = cands
		return m, nil
	default:
		// タイプ中は候補行を消す (補完は Tab を押した直後だけ出す)。
		m.cmdCandidates = nil
		var c tea.Cmd
		m.cmdInput, c = m.cmdInput.Update(msg)
		return m, c
	}
}

// renderCommandLine は command モードの `:` 行を返す。Tab 補完で複数候補があるときは
// その候補一覧を `:` 行直下に dim で 1 行添える (要件 031)。
func (m *chatModel) renderCommandLine() string {
	line := m.cmdInput.View()
	if len(m.cmdCandidates) == 0 {
		return line
	}
	return line + "\n" + caseBuilderHintStyle.Render("  "+strings.Join(m.cmdCandidates, "  "))
}

// execCommand は確定したコマンドを実行する。実行後のモード遷移もここで決める。
func (m *chatModel) execCommand(cmd command) (tea.Model, tea.Cmd) {
	// コマンド実行で command モードを抜けるので、上スクロールは解除して最下部へ戻す
	// (末尾の refreshViewport が GotoBottom する。要件 033)。
	m.scrolled = false
	switch cmd.name {
	case "": // 空コマンド → 何もせず元のモードへ
		if m.builder != nil {
			m.mode = modeBuilder
		} else {
			m.mode = modeInsert
		}
	case "case":
		m.builder = newCaseBuilder(m.sessionInputs)
		m.builder.setWidth(m.width)
		m.mode = modeBuilder
		return m, m.builder.in.Focus()
	case "w":
		m.saveBuilder(cmd.arg)
	case "q":
		// builder 中なら破棄して閉じる、そうでなければ chat 終了 (Ctrl+D 相当)。
		if m.builder != nil {
			m.closeBuilder()
		} else {
			if m.handle != nil {
				_ = m.handle.Kill()
			}
			return m, tea.Quit
		}
	case "set":
		setCmd := m.applySet(cmd.arg)
		if m.builder != nil {
			m.mode = modeBuilder
		} else {
			m.mode = modeInsert
		}
		m.refreshViewport()
		return m, setCmd
	case "debug":
		debugCmd := m.toggleDebug()
		m.returnFromCommand()
		m.refreshViewport()
		return m, debugCmd
	case "cheat":
		m.showCheat()
		m.returnFromCommand()
		m.refreshViewport()
		return m, nil
	case "replay":
		return m.execReplay()
	case "task", "contest", "e":
		return m.execNav(cmd)
	default: // unknown
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "E492: unknown command :" + cmd.arg})
		m.mode = modeInsert
	}
	m.refreshViewport()
	return m, nil
}

// execNav はナビゲーションコマンド (:task / :contest / :e) を処理する。
// NavEnabled が真 (start 分割画面) なら NavRequest を組んで親へ NavMsg を発火する
// (layout 解決・着手・再ターゲットは親 startSplitModel + 注入 Navigate が握る)。
// 偽 (test --interactive 単体) なら従来どおり未知コマンド扱い (E492) にする。
func (m *chatModel) execNav(cmd command) (tea.Model, tea.Cmd) {
	m.mode = modeInsert
	if !m.header.NavEnabled {
		// test --interactive 単体: ナビ無効 → 未知コマンド扱い。
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "E492: unknown command :" + cmd.name})
		m.refreshViewport()
		return m, nil
	}
	if req, ok := navRequestFor(cmd); ok {
		return m, func() tea.Msg { return NavMsg{Req: req} }
	}
	// :task / :contest の第 2 トークンが欠落 → 利用法を案内 (再ターゲットせず継続)。
	m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "E492: :" + cmd.name + " next|prev (n|p) または直指定"})
	m.refreshViewport()
	return m, nil
}

// applySet は `:set verify` / `:set noverify` / `:set debug|nodebug` を処理する。
// debug/nodebug は Debug を切り替えるので、watch ペインへ伝える DebugMsg の Cmd を返す
// (要件 034)。他のオプションは表示だけなので nil を返す。
func (m *chatModel) applySet(arg string) tea.Cmd {
	switch strings.TrimSpace(arg) {
	case "verify":
		if len(m.lastExpected) == 0 {
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(検証する期待出力がありません — :case で expected を定義してください)"})
			return nil
		}
		m.enableVerify(m.lastExpected)
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(ライブ検証 on)"})
		return nil
	case "noverify":
		m.verify = nil
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(ライブ検証 off)"})
		return nil
	case "debug":
		return m.setDebug(true)
	case "nodebug":
		return m.setDebug(false)
	default:
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "E518: unknown option :set " + arg})
		return nil
	}
}

// returnFromCommand は command で副作用だけ起こすコマンド (:set/:debug/:cheat) の
// 後に元のモードへ戻す。builder を開いていれば編集に、なければ insert に戻る。
func (m *chatModel) returnFromCommand() {
	if m.builder != nil {
		m.mode = modeBuilder
	} else {
		m.mode = modeInsert
	}
}

// setDebug は Debug 表示 (-d 相当、子 stdout の [DEBUG] 行を別カテゴリに振り分け) を
// on/off する。以後届く行に反映され、既に描画済みの行は遡及して変えない (要件 030)。
// 分割画面 (start) では親 startSplitModel が DebugMsg を受けて watch ペインを live Debug で
// 再判定する (要件 034)。単体 chat (test --interactive) では受け手がいないので無害に無視される。
func (m *chatModel) setDebug(on bool) tea.Cmd {
	m.header.Debug = on
	state := "off"
	if on {
		state = "on"
	}
	m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(debug " + state + " — 以降の [DEBUG] 行に反映)"})
	return func() tea.Msg { return DebugMsg{On: on} }
}

// toggleDebug は Debug 表示を反転する (:debug)。DebugMsg の Cmd を伝播する。
func (m *chatModel) toggleDebug() tea.Cmd {
	return m.setDebug(!m.header.Debug)
}

// showCheat は今この画面で使える command 一覧を info 行で積む (:cheat / :help / :?)。
// ナビ系 (:task/:contest/:e) は NavEnabled (start 分割画面) のときだけ載せる。
func (m *chatModel) showCheat() {
	lines := []string{
		"利用可能なコマンド (Esc で command モード):",
		"  :case (:c)            入出力ケース作成画面を開く",
		"  :w [name]             追加ケースを tests-extra に保存",
		"  :set verify|noverify  ライブ検証 on/off",
		"  :debug                Debug 表示 (-d) を切替 (:set debug|nodebug)",
		"  :replay               前回セッションの入力をリスタートして再送",
		"  :cheat (:help :?)     このコマンド一覧",
		"  :q                    chat 終了 (作成画面中は破棄)",
	}
	if m.header.NavEnabled {
		lines = append(lines,
			"  :task next|prev|<letter>   記号を移動 / 直指定 (例 :task f)",
			"  :contest next|prev|<num>   コンテスト移動 / 直指定 (例 :contest 123)",
			"  :e <spec>                  任意の問題へジャンプ (例 :e abc500_d)",
		)
	}
	for _, l := range lines {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: l})
	}
}

// execReplay は入力を再生する (:replay。要件 039)。再生対象は **今回の起動で送った入力
// (runInputs)** を優先し、まだ何も送っていなければ **前回セッションの入力 (PrevInputs)** に
// フォールバックする。これでコード修正後に同じ入力を流し直す主用途 (= 今回分の再送) と、
// 開いた直後に前回の続きを再開する用途の両方をカバーする。子をリスタートしてクリーンな
// 状態を作り、対象を submitLines で順送する。どちらも空なら info 行のみで子は起動しない。
func (m *chatModel) execReplay() (tea.Model, tea.Cmd) {
	m.returnFromCommand()
	lines := m.runInputs // 今回の起動で送った入力を優先
	if len(lines) == 0 {
		lines = m.header.PrevInputs // 未入力なら前回セッションへフォールバック
	}
	if len(lines) == 0 {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(再生できる入力がありません — まだ何も送っていない初回起動です)"})
		m.refreshViewport()
		return m, nil
	}
	// lines は m.runInputs / m.header.PrevInputs を指しうるので、送信前にスナップショット
	// する (submitLines は record=false でこれらを変更しないが、参照の安全のため)。
	snap := append([]string(nil), lines...)

	var cmds []tea.Cmd
	// クリーンな状態から再現するため、動作中でも子を作り直す (restart は同期 spawn し
	// running=true にして読み取り Cmd を返す)。
	cmds = append(cmds, m.restart())
	if !m.running {
		// spawn 失敗 (restart が tea.Quit を返した)。送らない。
		m.refreshViewport()
		return m, tea.Batch(cmds...)
	}
	// record=false: 再生行は runInputs / chatlog に積まない。積むと次の :replay が再生行を
	// 巻き込んで膨らみ「手入力したセッション」ではなく過去の再生値を流してしまう (要件 039)。
	m.submitLines(snap, &cmds, false)
	m.refreshViewport()
	return m, tea.Batch(cmds...)
}

// enableVerify はライブ検証を (再) 開始する。pos は現在の出力位置から始める
// (既に出ている出力は照合済み扱いにせず、これ以降の stdout を expected[0] から見る)。
func (m *chatModel) enableVerify(expected []string) {
	m.verify = &verifier{expected: expected, pos: 0, tol: m.verifyTol()}
}

func (m *chatModel) verifyTol() float64 {
	if m.header.Tolerance > 0 {
		return m.header.Tolerance
	}
	return defaultVerifyTol
}

const defaultVerifyTol = 1e-6

// saveBuilder は builder の内容を tests-extra に保存する。成功で builder を閉じて
// chat に戻る。失敗なら builder は開いたままエラー行を出す。
func (m *chatModel) saveBuilder(name string) {
	if m.builder == nil {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(:w は :case で作成画面を開いてから)"})
		m.mode = modeInsert
		return
	}
	if m.header.TaskDir == "" {
		m.msgs = append(m.msgs, chatLine{kind: kindErr, text: "(保存先 (tests-extra) が不明なため保存できません)"})
		m.mode = modeBuilder
		return
	}
	inBytes := normalizeForSave(m.builder.in.Value())
	outBytes := normalizeForSave(m.builder.out.Value())
	saved, err := extracase.Save(m.header.TaskDir, strings.TrimSpace(name), inBytes, outBytes)
	if err != nil {
		m.msgs = append(m.msgs, chatLine{kind: kindErr, text: "(保存に失敗: " + err.Error() + ")"})
		m.mode = modeBuilder // 開いたままにして直せるように
		return
	}
	m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(saved tests-extra/x" + saved + ")"})
	m.closeBuilder()
}

// closeBuilder は builder を閉じて chat (insert) に戻る。expected が空でなければ
// それを記憶し、ライブ検証を自動で有効化する (ファイル保存の有無に依らない — 要件 024)。
func (m *chatModel) closeBuilder() {
	if m.builder != nil {
		exp := splitLines(m.builder.out.Value())
		if len(exp) > 0 {
			m.lastExpected = exp
			m.enableVerify(exp)
		}
	}
	m.builder = nil
	m.mode = modeInsert
}

// updateBuilder は builder モードのキー処理。Tab でペイン切替、Esc で command 行へ。
func (m *chatModel) updateBuilder(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	switch msg.Type {
	case tea.KeyTab:
		m.builder.toggleFocus()
		return m, nil
	case tea.KeyEsc:
		// 編集を抜けて command 行へ (:w で保存 / :q で破棄)。
		m.builder.in.Blur()
		m.builder.out.Blur()
		return m, m.enterCommandMode()
	default:
		var c tea.Cmd
		if m.builder.focus == 1 {
			m.builder.out, c = m.builder.out.Update(msg)
		} else {
			m.builder.in, c = m.builder.in.Update(msg)
		}
		return m, c
	}
}

// applyVerify は子の stdout 行 1 つに対しライブ検証の判定を付ける。
// verify が無効 or expected を使い切っていれば何もしない (判定なし)。
func (m *chatModel) applyVerify(line *chatLine) {
	v := m.verify
	if v == nil || v.pos >= len(v.expected) {
		return
	}
	exp := v.expected[v.pos]
	v.pos++
	if tokensMatch(exp, line.text, v.tol) {
		line.verdict = verdictOK
	} else {
		line.verdict = verdictNG
		line.verdictExp = exp
	}
}

const (
	verdictOK = "ok"
	verdictNG = "ng"
)

// tokensMatch は expected と actual を空白区切りトークン列として比較する純粋関数。
// トークン数が違えば不一致。各トークンは文字列一致、または両方が float として
// 解釈でき差が tol 以内なら一致とみなす (judge と同じ許容誤差の考え方)。
func tokensMatch(expected, actual string, tol float64) bool {
	ef := strings.Fields(expected)
	af := strings.Fields(actual)
	if len(ef) != len(af) {
		return false
	}
	for i := range ef {
		if ef[i] == af[i] {
			continue
		}
		x, ex := strconv.ParseFloat(ef[i], 64)
		y, ey := strconv.ParseFloat(af[i], 64)
		if ex != nil || ey != nil {
			return false
		}
		d := x - y
		if d < 0 {
			d = -d
		}
		if d > tol {
			return false
		}
	}
	return true
}

// renderBuilder は builder モード (と builder 付き command モード) の画面を組む。
func (m *chatModel) renderBuilder() string {
	title := caseBuilderTitleStyle.Render("new case")
	inLabel := caseBuilderLabelStyle.Render("input (.in)")
	outLabel := caseBuilderLabelStyle.Render("expected (.out)")
	if m.builder.focus == 0 {
		inLabel = caseBuilderFocusLabelStyle.Render("input (.in) ◀")
	} else {
		outLabel = caseBuilderFocusLabelStyle.Render("expected (.out) ◀")
	}
	hint := caseBuilderHintStyle.Render("Tab でペイン切替  /  Esc → :w で保存・:q で取消")
	parts := []string{
		title,
		inLabel,
		m.builder.in.View(),
		outLabel,
		m.builder.out.View(),
		hint,
	}
	if m.mode == modeCommand {
		parts = append(parts, m.renderCommandLine())
	}
	return strings.Join(parts, "\n")
}

// normalizeForSave はペインの内容を保存用に整える (末尾改行を 1 つだけ保証)。
// 空入力は空バイト列のまま (空 .out を許容する)。
func normalizeForSave(s string) []byte {
	if s == "" {
		return nil
	}
	if !strings.HasSuffix(s, "\n") {
		s += "\n"
	}
	return []byte(s)
}

// splitLines は textarea の内容を行スライスにする (末尾の空行は落とす)。
func splitLines(s string) []string {
	s = strings.TrimRight(s, "\n")
	if s == "" {
		return nil
	}
	return strings.Split(s, "\n")
}

var (
	caseBuilderTitleStyle      = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSapphire)).Bold(true)
	caseBuilderLabelStyle      = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay1))
	caseBuilderFocusLabelStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaGreen)).Bold(true)
	caseBuilderHintStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0))
	chatVerdictOKStyle         = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaGreen)).Bold(true)
	chatVerdictNGStyle         = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)
)

// verdictSuffix は出力行に添える検証インジケーター ("  ✓" / "  ✗ expected 8")。
// 判定の無い行は空文字。
func verdictSuffix(line chatLine) string {
	switch line.verdict {
	case verdictOK:
		return "  " + chatVerdictOKStyle.Render("✓")
	case verdictNG:
		return "  " + chatVerdictNGStyle.Render("✗ expected "+line.verdictExp)
	default:
		return ""
	}
}
