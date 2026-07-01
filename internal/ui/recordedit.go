package ui

import (
	"fmt"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/cry999/atcoder-daily-training/internal/solvestat"
)

// recordEdit は既存の solve-stat ブロックを全画面フォームで訂正する (要件 066)。
// ac / editorial / duration / 5 軸だけを編集対象にし、started_at / solved_at / target_ms は
// 表示も編集もせず保存時に元値を温存する。internal/ui は layout/config/file I/O を知らない
// 層境界を保つため、フォームは solvestat.Stat (純データ) だけを入出力し、読み書きは
// composition root (cmd/atcoder) が握る (Meta/Gen/Record と同じフック委譲)。

// recEditKind はフォーム 1 行の編集ロジックの種別。
type recEditKind int

const (
	recFieldTriBool  recEditKind = iota // ac / editorial (未記録 / true / false)
	recFieldScore                       // 5 軸 (未記録 / 0..3)
	recFieldDuration                    // 実装時間 (テキスト編集)
)

// recordEditField はフォームの 1 行。kind ごとに boolVal / scoreVal / dur* を使い分ける。
type recordEditField struct {
	label string // 表示ラベル (= solve-stat のキー)
	kind  recEditKind

	boolVal  *bool // recFieldTriBool: 未記録=nil
	scoreVal int   // recFieldScore: 未記録=-1, 0..3

	durBuf    string // recFieldDuration: 編集用テキストバッファ
	durMs     int64  // 元の duration_ms (未編集なら保存時にそのまま温存)
	durEdited bool   // duration を 1 度でも編集したか
}

// RecordEditResult は編集結果 (保存された Stat と保存可否)。取消なら Saved=false。
type RecordEditResult struct {
	Stat  solvestat.Stat
	Saved bool
}

// recordEditModel は全画面編集フォームの bubbletea モデル。standalone (CLI) では
// tea.NewProgram で回し、chat では embedded=true で埋め込みモードとして駆動する
// (done を見て親が閉じる。tea.Quit は standalone のときだけ返す)。
type recordEditModel struct {
	title    string
	targetMs int64
	orig     solvestat.Stat // started_at / solved_at / target_ms を保全するための元 Stat
	fields   []recordEditField
	cursor   int
	embedded bool
	done     bool
	saved    bool
	errMsg   string // duration の解釈失敗など、保存を止めた理由
	width    int
	height   int
}

// newRecordEditModel は st から編集対象 8 フィールドを組んだフォームを作る。
func newRecordEditModel(title string, st solvestat.Stat, targetMs int64, embedded bool) *recordEditModel {
	fields := []recordEditField{
		{label: "ac", kind: recFieldTriBool, boolVal: st.AC, scoreVal: -1},
		{label: "editorial", kind: recFieldTriBool, boolVal: st.Editorial, scoreVal: -1},
		{label: "duration", kind: recFieldDuration, durMs: st.DurationMs, durBuf: seedDurBuf(st.DurationMs), scoreVal: -1},
		{label: "knowledge", kind: recFieldScore, scoreVal: st.Score.Knowledge},
		{label: "translation", kind: recFieldScore, scoreVal: st.Score.Translation},
		{label: "complexity", kind: recFieldScore, scoreVal: st.Score.Complexity},
		{label: "impl", kind: recFieldScore, scoreVal: st.Score.Impl},
		{label: "verify", kind: recFieldScore, scoreVal: st.Score.Verify},
	}
	return &recordEditModel{
		title:    title,
		targetMs: targetMs,
		orig:     st,
		fields:   fields,
		embedded: embedded,
	}
}

// seedDurBuf は duration_ms を分単位の compact 表記でバッファに前埋めする (0 は空)。
// 未編集なら durMs をそのまま温存するので、この分丸め表示による桁落ちは保存に影響しない。
func seedDurBuf(ms int64) string {
	if ms <= 0 {
		return ""
	}
	return fmtDurMsUI(ms)
}

func (m *recordEditModel) Init() tea.Cmd { return nil }

// Update は standalone (tea.NewProgram) 用。キーは handleKey に委ね、done で tea.Quit する。
func (m *recordEditModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.setWidth(msg.Width)
		m.height = msg.Height
	case tea.KeyMsg:
		m.handleKey(msg)
		if m.done && !m.embedded {
			return m, tea.Quit
		}
	}
	return m, nil
}

func (m *recordEditModel) setWidth(w int) {
	if w < 1 {
		w = 1
	}
	m.width = w
}

// handleKey はフォームの 1 打鍵を処理する (standalone / chat 埋め込みで共有)。
// カーソル移動 (↑↓ / j/k)・値の変更 (h/l)・保存 (Enter / Ctrl+S)・取消 (Esc/Ctrl+C) をここで完結させる。
func (m *recordEditModel) handleKey(msg tea.KeyMsg) {
	switch msg.Type {
	case tea.KeyUp:
		if m.cursor > 0 {
			m.cursor--
		}
	case tea.KeyDown:
		if m.cursor < len(m.fields)-1 {
			m.cursor++
		}
	case tea.KeyEnter, tea.KeyCtrlS:
		m.save()
	case tea.KeyEsc, tea.KeyCtrlC:
		m.saved = false
		m.done = true
	case tea.KeySpace:
		m.cur().cycle(+1)
	case tea.KeyBackspace:
		m.cur().backspace()
	case tea.KeyRunes:
		// j/k は上下移動、h/l は値の変更 (vim 風)。それ以外の文字は現在フィールドへ入力する。
		// ただし duration フィールドでは 'h' が時間単位の入力文字なので、そちらを優先する。
		for _, r := range msg.Runes {
			switch r {
			case 'j':
				if m.cursor < len(m.fields)-1 {
					m.cursor++
				}
			case 'k':
				if m.cursor > 0 {
					m.cursor--
				}
			case 'h':
				if m.cur().kind == recFieldDuration {
					m.cur().typeRune(r)
				} else {
					m.cur().cycle(-1)
				}
			case 'l':
				m.cur().cycle(+1)
			default:
				m.cur().typeRune(r)
			}
		}
	}
	// 打鍵したら以前のエラーは伏せる (再度保存キーで検証し直す)。
	if msg.Type != tea.KeyCtrlS && msg.Type != tea.KeyEnter {
		m.errMsg = ""
	}
}

// cur は現在選択中のフィールドへのポインタ。
func (m *recordEditModel) cur() *recordEditField {
	return &m.fields[m.cursor]
}

// cycle は tri-bool / score を dir (+1/-1) 方向へ 1 段回す。duration は無視。
func (f *recordEditField) cycle(dir int) {
	switch f.kind {
	case recFieldTriBool:
		// 未記録(nil) → true → false → 未記録 の 3 状態を循環する。
		order := []*bool{nil, boolPtr(true), boolPtr(false)}
		idx := 0
		if f.boolVal != nil {
			if *f.boolVal {
				idx = 1
			} else {
				idx = 2
			}
		}
		idx = (idx + dir + 3) % 3
		f.boolVal = order[idx]
	case recFieldScore:
		// 未記録(-1), 0, 1, 2, 3 を端で止める (循環しない)。
		v := f.scoreVal + dir
		if v < -1 {
			v = -1
		}
		if v > 3 {
			v = 3
		}
		f.scoreVal = v
	}
}

// backspace は tri-bool/score を未記録へ、duration は末尾 1 文字削除。
func (f *recordEditField) backspace() {
	switch f.kind {
	case recFieldTriBool:
		f.boolVal = nil
	case recFieldScore:
		f.scoreVal = -1
	case recFieldDuration:
		if f.durBuf != "" {
			f.durBuf = f.durBuf[:len(f.durBuf)-1]
		}
		f.durEdited = true
	}
}

// typeRune は文字入力を処理する。score は 0-3、tri-bool は y/n/-、duration は数字と h/m/s。
func (f *recordEditField) typeRune(r rune) {
	switch f.kind {
	case recFieldTriBool:
		switch r {
		case 'y', 'Y', 't', 'T':
			f.boolVal = boolPtr(true)
		case 'n', 'N', 'f', 'F':
			f.boolVal = boolPtr(false)
		case '-':
			f.boolVal = nil
		}
	case recFieldScore:
		switch {
		case r >= '0' && r <= '3':
			f.scoreVal = int(r - '0')
		case r == '-':
			f.scoreVal = -1
		}
	case recFieldDuration:
		if (r >= '0' && r <= '9') || r == 'h' || r == 'm' || r == 's' {
			f.durBuf += string(r)
			f.durEdited = true
		}
	}
}

// save は現在の入力を検証し、問題なければ done+saved を立てる。duration が不正なら
// errMsg を立ててフォームに留まる (done を立てない)。
func (m *recordEditModel) save() {
	// duration の検証を先に済ませ、不正なら保存を中断する。
	for i := range m.fields {
		f := &m.fields[i]
		if f.kind != recFieldDuration || !f.durEdited {
			continue
		}
		if strings.TrimSpace(f.durBuf) == "" {
			continue // 空 = 未計測 (0)。正当。
		}
		if _, err := time.ParseDuration(strings.TrimSpace(f.durBuf)); err != nil {
			m.errMsg = fmt.Sprintf("duration が不正です (例 25m, 1h5m): %q", f.durBuf)
			return
		}
	}
	m.saved = true
	m.done = true
}

// resultStat は編集後の Stat を組む。started_at / solved_at / target_ms は元 Stat から
// 温存し、8 フィールドだけを上書きする。duration は未編集なら元 ms をそのまま使う。
func (m *recordEditModel) resultStat() solvestat.Stat {
	out := m.orig // started_at / solved_at / target_ms を温存
	for i := range m.fields {
		f := &m.fields[i]
		switch f.label {
		case "ac":
			out.AC = f.boolVal
		case "editorial":
			out.Editorial = f.boolVal
		case "duration":
			if f.durEdited {
				out.DurationMs = parseDurBuf(f.durBuf)
			} else {
				out.DurationMs = f.durMs
			}
		case "knowledge":
			out.Score.Knowledge = f.scoreVal
		case "translation":
			out.Score.Translation = f.scoreVal
		case "complexity":
			out.Score.Complexity = f.scoreVal
		case "impl":
			out.Score.Impl = f.scoreVal
		case "verify":
			out.Score.Verify = f.scoreVal
		}
	}
	return out
}

// parseDurBuf は編集後の duration バッファを ms にする。空 / 不正は 0 (未計測)。
// 保存前に save() で検証済みだが、防御的に無効値は 0 に落とす。
func parseDurBuf(buf string) int64 {
	buf = strings.TrimSpace(buf)
	if buf == "" {
		return 0
	}
	d, err := time.ParseDuration(buf)
	if err != nil {
		return 0
	}
	return d.Milliseconds()
}

// View はフォームの全画面表示を組む (standalone / chat 埋め込みで共有)。
func (m *recordEditModel) View() string {
	var b strings.Builder
	b.WriteString(recEditTitleStyle.Render("record edit  "+m.title) + "\n\n")
	for i := range m.fields {
		f := &m.fields[i]
		marker := "  "
		label := recEditLabelStyle.Render(fmt.Sprintf("%-11s", f.label))
		val := f.display(i == m.cursor)
		if i == m.cursor {
			marker = recEditCursorStyle.Render("> ")
			label = recEditFocusLabelStyle.Render(fmt.Sprintf("%-11s", f.label))
		}
		b.WriteString(marker + label + "  " + val + "\n")
	}
	b.WriteString("\n")
	if m.targetMs > 0 {
		b.WriteString(recEditHintStyle.Render("目標 "+fmtDurMsUI(m.targetMs)) + "\n")
	}
	if m.errMsg != "" {
		b.WriteString(recEditErrStyle.Render(m.errMsg) + "\n")
	}
	b.WriteString(recEditHintStyle.Render("j/k 移動   h/l 変更   0-3・y/n 入力   Backspace 未記録   Enter 保存   Esc 取消"))
	return b.String()
}

// display はフィールドの値部分 (角括弧で囲んだ current 値) を返す。focus 中の duration は
// カーソル (▏) を末尾に添える。
func (f *recordEditField) display(focus bool) string {
	switch f.kind {
	case recFieldTriBool:
		return recEditValueStyle.Render("[ " + triBoolStr(f.boolVal) + " ]")
	case recFieldScore:
		return recEditValueStyle.Render("[ " + scoreDisplay(f.scoreVal) + " ]")
	case recFieldDuration:
		txt := f.durBuf
		if txt == "" {
			txt = "未計測"
		}
		if focus {
			txt += "▏"
		}
		return recEditValueStyle.Render("[ " + txt + " ]")
	}
	return ""
}

// triBoolStr は *bool を true / false / — で表す。
func triBoolStr(b *bool) string {
	if b == nil {
		return "—"
	}
	if *b {
		return "true"
	}
	return "false"
}

// scoreDisplay は score (-1..3) を — / 0..3 で表す。
func scoreDisplay(n int) string {
	if n < 0 {
		return "—"
	}
	return fmt.Sprintf("%d", n)
}

// boolPtr は *bool の生成ヘルパー (solvestat.BoolPtr と同義。ui 内で完結させる)。
func boolPtr(b bool) *bool { return &b }

// fmtDurMsUI は ms を分単位に丸めた compact 表記 ("23m" / "1h5m") にする
// (cmd/atcoder の fmtDurMs の ui 版。負値は絶対値表記)。
func fmtDurMsUI(ms int64) string {
	if ms < 0 {
		ms = -ms
	}
	mins := int(time.Duration(ms) * time.Millisecond / time.Minute)
	if mins < 60 {
		return fmt.Sprintf("%dm", mins)
	}
	return fmt.Sprintf("%dh%dm", mins/60, mins%60)
}

// RunRecordEdit は standalone (CLI record edit) で全画面フォームを起動し、確定/取消の
// 結果を返す。保存 (OverwriteFile) は呼び出し側 (composition root) が行う。
func RunRecordEdit(title string, st solvestat.Stat, targetMs int64) (RecordEditResult, error) {
	m := newRecordEditModel(title, st, targetMs, false)
	fm, err := tea.NewProgram(m).Run()
	if err != nil {
		return RecordEditResult{}, err
	}
	rm, ok := fm.(*recordEditModel)
	if !ok {
		return RecordEditResult{}, nil
	}
	return RecordEditResult{Stat: rm.resultStat(), Saved: rm.saved}, nil
}

var (
	recEditTitleStyle      = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSapphire)).Bold(true)
	recEditLabelStyle      = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay1))
	recEditFocusLabelStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaGreen)).Bold(true)
	recEditCursorStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaGreen)).Bold(true)
	recEditValueStyle      = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaText))
	recEditHintStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0))
	recEditErrStyle        = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed))
)
