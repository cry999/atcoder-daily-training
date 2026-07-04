package ui

import (
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/textarea"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/cry999/atcoder-daily-training/internal/extracase"
	"github.com/cry999/atcoder-daily-training/internal/solvestat"
)

// chatMode は chat の入力モード (vim 風)。要件 024。
//
//	insert     : 既定。textinput にフォーカスし Enter で子に送信 (従来の chat)。
//	command    : ex-command line (`:…`)。コマンドを 1 行打って Enter で実行。
//	builder    : ケースビルダー (input/expected の textarea 2 ペイン)。
//	recordEdit : solve-stat の全画面編集フォーム (:record edit。要件 066)。
type chatMode int

const (
	modeInsert chatMode = iota
	modeCommand
	modeBuilder
	modeRecordEdit
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

// testReplay は直近に :test で流したサンプルケースのスナップショット (要件 048)。
// :replay が「直近の操作」を再生する際、現セッションに手入力が無ければ input を
// 再送し expected で再検証する。input/expected は実行時にコピーして持つので、
// sessionInputs の退避・リセットには影響されない。
type testReplay struct {
	id       string   // 表示用ケース ID ("01" / "x01")
	input    []string // 流した .in の行
	expected []string // .out の行 (空なら検証なし)
}

// newCommandInput は command モードの `:` 行用 textinput を作る。
func newCommandInput() textinput.Model {
	ti := textinput.New()
	ti.Prompt = ":"
	ti.Placeholder = "case | test [case] | w [name] | set verify | meta | debug | replay | cheat | q"
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
	case "pp":
		// :pp — valid JSON の [DEBUG] ペイロード整形 (要件 047) をトグル。:debug と直交。
		return command{name: "pp", arg: arg}
	case "cheat", "help", "?":
		// :cheat / :help / :? — 利用可能なコマンド一覧を表示。
		return command{name: "cheat", arg: arg}
	case "replay":
		// :replay — 直近の操作 (手入力セッション or 直近の :test ケース) を、子をリスタート
		// して順送する (要件 039 / 048)。
		return command{name: "replay", arg: arg}
	case "t", "test":
		// :test [case] — キャッシュ済みサンプルケースを子リスタート後に順送 + ライブ検証 (要件 045)。
		return command{name: "test", arg: arg}
	case "meta":
		// :meta [fetch|url|time_limit [value]] — meta.toml の url / time_limit を表示・編集 (要件 055)、
		// :meta fetch で url から再取得 (要件 057)。
		return command{name: "meta", arg: arg}
	case "gen":
		// :gen — 制約 / 入力形式からランダム入力を 1 つ生成し insert 欄へ前埋め (要件 060)。
		return command{name: "gen", arg: arg}
	case "record":
		// :record [start|stop] [flags] — solve-stat の計測・記録 (要件 064)。
		// arg にサブコマンド + フラグ (start/stop/ac/noac/ed/noed/score=…/time=…) を載せる。
		return command{name: "record", arg: arg}
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
	case tea.KeyCtrlP:
		// Ctrl+P = 1 行上 (vim/emacs の previous。要件 067)。
		m.scrollLineUp()
		return m, nil
	case tea.KeyCtrlN:
		// Ctrl+N = 1 行下 (next)。最下部に達したら追従を再開する。
		m.scrollLineDown()
		return m, nil
	case tea.KeyCtrlU:
		// Ctrl+U = 半ページ上 (vim。要件 067)。
		m.scrollHalfUp()
		return m, nil
	case tea.KeyCtrlD:
		// Ctrl+D = 半ページ下 (vim)。最下部に達したら追従を再開する。
		// insert モードの Ctrl+D (リセット→終了、要件 051) とは別で、command モード限定。
		m.scrollHalfDown()
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
	case "pp":
		m.togglePP()
		m.returnFromCommand()
		m.refreshViewport()
		return m, nil
	case "cheat":
		m.showCheat()
		m.returnFromCommand()
		m.refreshViewport()
		return m, nil
	case "replay":
		return m.execReplay()
	case "test":
		return m.execTest(cmd.arg)
	case "meta":
		return m, m.execMeta(cmd.arg)
	case "gen":
		return m, m.execGen()
	case "record":
		return m, m.execRecord(cmd.arg)
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

// execMeta は `:meta` (要件 055) を処理する。引数なしで meta.toml の全体 (url/time limit/
// samples) を、`:meta url` / `:meta time_limit` で当該フィールドの現在値を表示し、
// `:meta url <url>` / `:meta time_limit <dur>` で上書きする。meta の読み書き・検証・整形は
// composition root が注入する MetaShow / MetaSet フックに委譲する (internal/ui は testexec/
// layout を知らない層境界。Submit/Edit と同じ)。time_limit を更新したらヘッダ表示にも反映する。
func (m *chatModel) execMeta(arg string) tea.Cmd {
	m.returnFromCommand()
	if m.header.MetaShow == nil || m.header.MetaSet == nil {
		m.addInfoLine("(メタ編集はこの画面では使えません)")
		m.refreshViewport()
		return nil
	}
	f := strings.Fields(arg)
	switch {
	case len(f) == 0: // :meta → 全体表示
		m.metaShow("")
	case f[0] == "fetch": // :meta fetch → 再取得 (非同期。要件 057)
		// fetch はネットワーク呼び出しを伴うため tea.Cmd で非同期に回す。
		// metaFetch が「(再取得中…)」行を積んで viewport を更新済み。
		return m.metaFetch()
	case f[0] != "url" && f[0] != "time_limit":
		m.addInfoLine("E518: unknown meta field :meta " + f[0])
	case len(f) == 1: // :meta url / :meta time_limit → 当該フィールド表示
		m.metaShow(f[0])
	default: // :meta <field> <value> → 編集
		m.metaSet(f[0], strings.Join(f[1:], " "))
	}
	m.refreshViewport()
	return nil
}

// metaFetch は `:meta fetch` (要件 057) を処理する。meta.toml の url (override 優先) から
// サンプル + Time Limit を再取得するフック (MetaFetch) を tea.Cmd で非同期に呼ぶ。
// 即「(再取得中…)」を 1 行積んで UI をブロックせず、完了は metaFetchDoneMsg で受ける
// (applyMetaFetchDone)。Ctrl+E の editDoneMsg と同型。
func (m *chatModel) metaFetch() tea.Cmd {
	if m.header.MetaFetch == nil {
		// 念のため (execMeta 冒頭で MetaShow/MetaSet は確認済み。3 つは一括注入される)。
		m.addInfoLine("(メタ編集はこの画面では使えません)")
		m.refreshViewport()
		return nil
	}
	m.addInfoLine("(再取得中…)")
	m.refreshViewport()
	fetch := m.header.MetaFetch
	return func() tea.Msg {
		lines, ms, err := fetch()
		return metaFetchDoneMsg{lines: lines, newTimeLimitMs: ms, err: err}
	}
}

// applyMetaFetchDone は :meta fetch の非同期完了を反映する。成功なら結果行を info 行で積み、
// Time Limit が変わっていれば (> 0) ヘッダの TimeLimitMs を更新する (続く :test の TLE 判定に効く)。
// 失敗は err 行で 1 本積み、chat は継続する (キャッシュ・ヘッダは変えない)。
func (m *chatModel) applyMetaFetchDone(msg metaFetchDoneMsg) {
	if msg.err != nil {
		m.addErrLine("(" + msg.err.Error() + ")")
		return
	}
	for _, l := range msg.lines {
		m.addInfoLine(l)
	}
	if msg.newTimeLimitMs > 0 {
		m.header.TimeLimitMs = msg.newTimeLimitMs
	}
}

// execGen は :gen (要件 060) を処理する。制約 / 入力形式からランダム入力を 1 つ
// 生成して insert 入力欄へ前埋めするフック (Gen) を tea.Cmd で非同期に呼ぶ。初回は
// gen.toml を fetch しうるため即「(生成中…)」を積み、完了は genDoneMsg で受ける
// (applyGenDone)。:meta fetch と同型。
func (m *chatModel) execGen() tea.Cmd {
	m.returnFromCommand()
	if m.header.Gen == nil {
		m.addInfoLine("(入力生成はこの画面では使えません)")
		m.refreshViewport()
		return nil
	}
	m.addInfoLine("(生成中…)")
	m.refreshViewport()
	genFn := m.header.Gen
	return func() tea.Msg {
		input, warnings, err := genFn()
		return genDoneMsg{input: input, warnings: warnings, err: err}
	}
}

// applyGenDone は :gen の非同期生成の完了を反映する。成功なら生成入力を insert 欄へ
// 前埋めし (送信はユーザの Enter に委ねる)、取りこぼし警告を info 行で積む。失敗は
// err 行を 1 本積み chat は継続する (入力欄は触らない)。
func (m *chatModel) applyGenDone(msg genDoneMsg) {
	if msg.err != nil {
		m.addErrLine("(" + msg.err.Error() + ")")
		return
	}
	for _, w := range msg.warnings {
		m.addInfoLine("warning: " + w)
	}
	m.input.SetValue(strings.TrimRight(msg.input, "\n"))
	m.input.CursorEnd()
	m.addInfoLine("(生成入力を入力欄に前埋めしました。Enter で送信 / 編集可)")
}

// execRecord は :record (要件 064) を処理する。arg (start/stop/フラグ) を空白で分け、
// 注入された Record フックへそのまま渡し、返った行を info 行で積む (失敗は err 行 1 本)。
// solve-stat の読み書き・計測・検証・layout 解決は composition root (cmd/atcoder) に
// 委譲する (internal/ui は solvestat/layout を知らない層境界。:meta/:gen と同じ)。
// ローカル I/O のみなので同期実行する (:gen/:meta fetch のような非同期化はしない)。
// :record start/stop が成功したら記録インジケーター (ヘッダの ● REC + 経過) を切り替え、
// start では毎秒 tick する tea.Cmd を返す (失敗・その他は nil)。
func (m *chatModel) execRecord(arg string) tea.Cmd {
	m.returnFromCommand()
	fields := strings.Fields(arg)
	if len(fields) >= 1 && fields[0] == "edit" {
		// :record edit → 全画面編集フォームへ (要件 066)。
		m.enterRecordEdit()
		return nil
	}
	if m.header.Record == nil {
		m.addInfoLine("(記録はこの画面では使えません)")
		m.refreshViewport()
		return nil
	}
	lines, err := m.header.Record(fields)
	if err != nil {
		m.addErrLine("(" + err.Error() + ")")
		m.refreshViewport()
		return nil
	}
	for _, l := range lines {
		m.addInfoLine(l)
	}
	// :record start で記録中インジケーターを点灯し、start した時点を経過の基準にする。
	// :record stop で消灯 (recordGen を進めて走っている tick を世代不一致で止める)。
	// スピナー tick と同型で、重複 tick を防ぐため世代 (recordGen) を都度更新する。
	var cmd tea.Cmd
	if len(fields) >= 1 {
		switch fields[0] {
		case "start":
			m.recording = true
			m.recordStart = time.Now()
			m.recordDone = false
			m.recordDuration = 0
			m.recordGen++
			cmd = m.recordTickCmd()
		case "stop":
			m.recording = false
			m.recordGen++
			// stop 直後の solve-stat (solved_at / duration 確定) を読み直して「終了」表示へ
			// 同期する。フック未注入 or 読取失敗時は開始時刻からの経過で代替する。
			m.syncRecordDoneFromStat()
		}
	}
	m.refreshViewport()
	return cmd
}

// restoreRecordingFromStat は現在ターゲットの solve-stat を読み、● REC 表示をディスク上の
// 計測状態へ同期する。started_at あり・solved_at 空 (計測中) なら点灯し started_at 基準で
// 経過表示 + tick を再開、それ以外・記録なし・フック未注入・読取失敗は消灯する。
// recordGen を進めて走っている旧 tick を世代不一致で止める (:record start/stop と同型)。
// ナビ再ターゲット (要件 027) で chat を作り直すと recording 状態が落ち REC が消えるため、
// 移動先タスクの計測状態を復元するのに使う (要件 064 / バグ: 移動で REC が消える)。
func (m *chatModel) restoreRecordingFromStat() tea.Cmd {
	m.recordGen++
	m.recording = false
	m.recordDone = false
	m.recordDuration = 0
	if m.header.RecordEditLoad == nil {
		return nil
	}
	st, _, found, err := m.header.RecordEditLoad()
	if err != nil || !found {
		return nil
	}
	if !st.StartedAt.IsZero() && st.SolvedAt.IsZero() {
		m.recording = true
		m.recordStart = st.StartedAt
		return m.recordTickCmd()
	}
	m.applyRecordDoneState(st)
	return nil
}

// syncRecordDoneFromStat は :record stop 直後にディスクの solve-stat を読み直し、終了表示
// (✓ + かかった時間) へ同期する。フックが未注入 or 読取失敗 or 記録なしのときは、開始時刻
// (recordStart) からの経過を代替の所要時間として表示する。
func (m *chatModel) syncRecordDoneFromStat() {
	if m.header.RecordEditLoad != nil {
		if st, _, found, err := m.header.RecordEditLoad(); err == nil && found {
			m.applyRecordDoneState(st)
			return
		}
	}
	if !m.recordStart.IsZero() {
		m.recordDone = true
		m.recordDuration = time.Since(m.recordStart)
	}
}

// applyRecordDoneState は計測中でない stat を終了/未開始表示へ反映する。solved_at が確定して
// いれば「終了」(かかった時間を保持) とし、それ以外 (未記録 / started のみ) は「未開始」に落とす。
func (m *chatModel) applyRecordDoneState(st solvestat.Stat) {
	if !st.SolvedAt.IsZero() {
		m.recordDone = true
		m.recordDuration = recordStatDuration(st)
		return
	}
	m.recordDone = false
	m.recordDuration = 0
}

// recordStatDuration は終了済み stat のかかった時間を返す。記録された duration_ms を優先し、
// 無ければ started_at→solved_at の差で補う (どちらも無ければ 0)。
func recordStatDuration(st solvestat.Stat) time.Duration {
	if st.DurationMs > 0 {
		return time.Duration(st.DurationMs) * time.Millisecond
	}
	if !st.StartedAt.IsZero() && !st.SolvedAt.IsZero() {
		return st.SolvedAt.Sub(st.StartedAt)
	}
	return 0
}

// enterRecordEdit は :record edit (要件 066) で全画面編集フォームへ入る。RecordEditLoad で
// 現在の solve-stat を読み込み、記録があればフォームを開いて modeRecordEdit へ遷移する。
// 記録が無い / フックが未注入なら info 行で案内するだけ (insert に留まる)。solve-stat の
// 読み書きは composition root に委譲し、UI には Stat (純データ) だけ渡す (Record と同じ層境界)。
func (m *chatModel) enterRecordEdit() {
	if m.header.RecordEditLoad == nil || m.header.RecordEditSave == nil {
		m.addInfoLine("(記録の編集はこの画面では使えません)")
		m.refreshViewport()
		return
	}
	st, targetMs, found, err := m.header.RecordEditLoad()
	if err != nil {
		m.addErrLine("(" + err.Error() + ")")
		m.refreshViewport()
		return
	}
	if !found {
		m.addInfoLine("(まだ記録がありません。:record start で計測を開始できます)")
		m.refreshViewport()
		return
	}
	m.editForm = newRecordEditModel(m.header.Task, st, targetMs, true)
	m.editForm.setWidth(m.width - 2)
	m.mode = modeRecordEdit
}

// updateRecordEdit は modeRecordEdit のキー処理。フォームに打鍵を委ね、確定/取消 (done) で
// 抜ける。確定 (saved) なら RecordEditSave で全置換保存し結果行を、取消なら中止行を積む。
func (m *chatModel) updateRecordEdit(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	m.editForm.handleKey(msg)
	if !m.editForm.done {
		return m, nil
	}
	saved := m.editForm.saved
	result := m.editForm.resultStat()
	m.editForm = nil
	m.returnFromCommand() // builder が開いていれば編集へ、なければ insert へ戻す
	var cmd tea.Cmd
	if saved {
		lines, err := m.header.RecordEditSave(result)
		if err != nil {
			m.addErrLine("(" + err.Error() + ")")
		} else {
			for _, l := range lines {
				m.addInfoLine(l)
			}
			// state トグルを保存したら ● REC を保存内容へ同期する (要件 068)。started_at あり・
			// solved_at 空なら点灯し started_at 基準で経過表示 + tick 再開、それ以外は消灯。
			// recordGen を進めて走行中の tick を世代不一致で止める (:record start/stop と同型)。
			m.recordGen++
			if !result.StartedAt.IsZero() && result.SolvedAt.IsZero() {
				m.recording = true
				m.recordStart = result.StartedAt
				m.recordDone = false
				m.recordDuration = 0
				cmd = m.recordTickCmd()
			} else {
				m.recording = false
				m.applyRecordDoneState(result)
			}
		}
	} else {
		m.addInfoLine("(編集を取消しました)")
	}
	m.refreshViewport()
	return m, cmd
}

// metaShow は MetaShow フックを呼び、返ってきた行を info 行で積む。失敗は err 行で 1 本。
func (m *chatModel) metaShow(field string) {
	lines, err := m.header.MetaShow(field)
	if err != nil {
		m.addErrLine("(" + err.Error() + ")")
		return
	}
	for _, l := range lines {
		m.addInfoLine(l)
	}
}

// metaSet は MetaSet フックを呼んで meta.toml を上書きし、結果行を info 行で積む。
// time_limit を更新したときはヘッダの Time Limit 表示も新値に揃える (続く :test の TLE 判定に効く)。
// 検証失敗・未キャッシュ・I/O 失敗は err 行で 1 本積み、chat は継続する。
func (m *chatModel) metaSet(field, value string) {
	lines, newTimeLimitMs, err := m.header.MetaSet(field, value)
	if err != nil {
		m.addErrLine("(" + err.Error() + ")")
		return
	}
	for _, l := range lines {
		m.addInfoLine(l)
	}
	if field == "time_limit" {
		m.header.TimeLimitMs = newTimeLimitMs
	}
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
	case "pp":
		m.setPP(true)
		return nil
	case "nopp":
		m.setPP(false)
		return nil
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

// setPP は pp 表示 (valid JSON の [DEBUG] ペイロード整形。要件 047) を on/off する。
// :debug と直交し、以降届く [DEBUG] 行にだけ反映される (既描画行は遡及しない)。
// debug 自体が off なら整形対象が無いので info 行に補足を添える。watch ペインへの
// 波及 (DebugMsg 相当) は将来スコープなので Cmd は返さない (cosmetic のみ)。
func (m *chatModel) setPP(on bool) {
	m.header.PP = on
	state := "off"
	if on {
		state = "on"
	}
	text := "(pp " + state + ")"
	if on && !m.header.Debug {
		text = "(pp on — :debug を on にすると整形結果が見えます)"
	}
	m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: text})
}

// togglePP は pp 表示を反転する (:pp)。
func (m *chatModel) togglePP() {
	m.setPP(!m.header.PP)
}

// showCheat は今この画面で使える command 一覧を info 行で積む (:cheat / :help / :?)。
// ナビ系 (:task/:contest/:e) は NavEnabled (start 分割画面) のときだけ載せる。
func (m *chatModel) showCheat() {
	lines := []string{
		"利用可能なコマンド (Esc で command モード):",
		"  :case (:c)            入出力ケース作成画面を開く",
		"  :test [case] (:t)     サンプルケースを実行 + ライブ検証 (:test で一覧)",
		"  :w [name]             追加ケースを tests-extra に保存",
		"  :set verify|noverify  ライブ検証 on/off",
		"  :debug                Debug 表示 (-d) を切替 (:set debug|nodebug)",
		"  :pp                   [DEBUG] の valid JSON を整形表示 (:set pp|nopp)",
		"  :replay               直近に流した入力 (手入力 / :test ケース) を再送 + 再検証",
		"  :meta [url|time_limit [値]]  meta の url / time_limit を表示・編集",
		"  :meta fetch           url からサンプル + Time Limit を再取得",
		"  :gen                  制約 / 入力形式からランダム入力を生成し入力欄へ前埋め",
		"  :record [start|stop|edit|<flags>]  実装時間/AC/5 軸を記録 (:record で現在値表示 / edit で編集フォーム)",
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

// execReplay は **直近の操作** を再生する (:replay。要件 039 / 048)。優先順位は:
//  1. 直近の操作が :test ケース (lastOpWasTest) → lastTest を再送し expected で再検証する
//  2. それ以外 (直近の操作が手入力) → 現セッションの手入力 (sessionInputs)
//  3. 直前に完了したセッション (prevSessionInputs)
//  4. 前回 chat 起動の手入力 (PrevInputs)
//
// 「直近の操作が手入力か :test ケースか」は lastOpWasTest で判定する (手入力時に false、
// :test 実行時に true を立て、:replay 自身は変えない)。sessionInputs の空・非空で判定すると、
// :replay 自身が flowInput→restart で sessionInputs を退避・リセットして空にするため、連続
// :replay の 2 回目以降に手入力からテストケースへ遡ってしまう (バグ報告)。子をリスタート
// してクリーンな状態を作り、対象を順送する。何も無ければ info 行のみで子は起動しない。
func (m *chatModel) execReplay() (tea.Model, tea.Cmd) {
	m.returnFromCommand()
	// 直近の操作が :test ケースなら、それを最優先で再送 + 再検証する。
	if m.lastOpWasTest && m.lastTest != nil {
		t := m.lastTest
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: fmt.Sprintf("(case %s を再生 — input %d行 / expected %d行)", t.id, len(t.input), len(t.expected))})
		return m.flowInput(t.input, t.expected)
	}
	lines := m.replayLines()
	if len(lines) == 0 {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(再生できる入力がありません — まだ何も送っていない初回起動です)"})
		m.refreshViewport()
		return m, nil
	}
	// lines は sessionInputs / prevSessionInputs / PrevInputs を指しうる。flowInput 内の
	// restart() が sessionInputs を退避・リセットするため、送信前にスナップショットを取る。
	snap := append([]string(nil), lines...)
	// 手入力の再生は検証状態を変えない (expected を渡さない)。
	return m.flowInput(snap, nil)
}

// flowInput は snap の入力をクリーンな子で順送する共通処理 (:test / :replay 共有)。
// expected が非空ならライブ検証を (再) 有効化し :set verify の対象 (lastExpected) も更新する。
// 順送は record=false なので sessionInputs / chatlog ([039]) を汚さない。snap は呼び出し側で
// スナップショットを取っておくこと (restart が sessionInputs を退避・リセットするため)。
func (m *chatModel) flowInput(snap, expected []string) (tea.Model, tea.Cmd) {
	// expected があればライブ検証を (再) 開始し、:set verify の対象も更新する。
	// 空 expected のケースは検証を付けず出力だけ見る (既存 verify は据え置き)。
	if len(expected) > 0 {
		m.lastExpected = expected
		m.enableVerify(expected)
	}
	var cmds []tea.Cmd
	// クリーンな状態から流すため、動作中でも子を作り直す (restart は同期 spawn し
	// running=true にして読み取り Cmd を返す)。
	cmds = append(cmds, m.restart())
	if !m.running {
		// spawn 失敗 (restart が tea.Quit を返した)。送らない。
		m.refreshViewport()
		return m, tea.Batch(cmds...)
	}
	m.submitLines(snap, &cmds, false)
	m.refreshViewport()
	return m, tea.Batch(cmds...)
}

// execTest は **キャッシュ済みサンプルケースを 1 つ実行**する (:test [case]。要件 045)。
// 引数があれば公式 (tests/ = "01") / 追加 (tests-extra/ = "x01") のケースを解決し、子を
// リスタートしてその .in をクリーンな状態から順送しつつ、.out でライブ検証 ([024]) する。
// 引数が無ければ利用可能なケース ID の一覧を表示するだけ (実行しない)。順送は :replay と
// 同じ record=false なので sessionInputs / chatlog ([039]) を汚さない。流したケースは
// lastTest に覚え、直後の :replay が「直近の操作」としてこのケースを再送 + 再検証できる
// ([048])。:test 自身は fetch しない (キャッシュ済みファイルを読むだけ)。
func (m *chatModel) execTest(arg string) (tea.Model, tea.Cmd) {
	m.returnFromCommand()
	if m.header.TaskDir == "" {
		// 保存先 (:w と同じ TaskDir) が未注入だとケースの場所が分からない。
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(ケースの場所が不明なため :test は使えません)"})
		m.refreshViewport()
		return m, nil
	}
	ref := strings.TrimSpace(arg)
	if ref == "" {
		// 引数省略: 利用可能なケース ID を一覧表示 (実行はしない)。
		ids := listSampleCases(m.header.TaskDir)
		if len(ids) == 0 {
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(利用可能なサンプルがありません — atcoder test で取得、または :w で追加)"})
		} else {
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(利用可能なケース: " + strings.Join(ids, " ") + ")"})
		}
		m.refreshViewport()
		return m, nil
	}
	in, out, id, ok := resolveSampleCase(m.header.TaskDir, ref)
	if !ok {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(ケース " + ref + " が見つかりません — :test で一覧)"})
		m.refreshViewport()
		return m, nil
	}
	m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: fmt.Sprintf("(case %s を実行 — input %d行 / expected %d行)", id, len(in), len(out))})
	// 直近の :test として覚える: :replay が「直近の操作」としてこのケースを再送 + 再検証する ([048])。
	// in/out は resolveSampleCase が返した fresh なスライスなのでそのまま保持してよい。
	m.lastTest = &testReplay{id: id, input: in, expected: out}
	m.lastOpWasTest = true // 直近の操作は :test ケース → :replay はこのケースを再生 (要件 048)
	// 検証有効化 → 子リスタート → 順送 (record=false) は :replay と共通 (flowInput)。
	return m.flowInput(in, out)
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
