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
	"github.com/mattn/go-runewidth"

	"github.com/cry999/atcoder-daily-training/internal/runner"
	"github.com/cry999/atcoder-daily-training/internal/watch"
)

// ChatHeader は TUI ヘッダに出すメタ情報 + 起動オプション。
type ChatHeader struct {
	Task        string
	Contest     string
	TimeLimitMs int
	Debug       bool       // true なら子の stdout 行のうち [DEBUG] プレフィックスを持つものを別カテゴリで表示する
	AutoRestart bool       // true なら起動時から sticky auto-restart (子終了のたびに再起動する)
	WatchPath   string     // 非空なら解答ファイルを監視し、保存検知で子を最新ファイルで再 spawn する
	Submit      SubmitFunc // 非 nil なら Ctrl+S で提出準備を呼べる。composition root が注入する
	TaskDir     string     // cache の <contest>/<task> dir。非空なら :w でケースを tests-extra に保存できる (要件 024)
	Tolerance   float64    // ライブ検証の許容誤差 (0 なら既定 1e-6)
	NavEnabled  bool       // true なら :next/:prev/:fwd/:back/:e で問題ナビ可 (start 分割画面限定。要件 027)
}

// SubmitResult は chat の Ctrl+S 提出準備の結果。chat はこれを 1 行に整形して表示する。
type SubmitResult struct {
	Message string // 表示文 (例 "クリップボードにコピー abc457/d.py / 提出ページを開きました")
	IsError bool   // true なら err 行で表示
}

// SubmitFunc は chat の Ctrl+S で呼ばれる提出準備フック。
// internal/ui は cmd/atcoder を import できないため、composition root が注入する。
// 提出準備の中身 (解答コピー + 提出ページ起動) はこの先で行い、結果文を返す。
type SubmitFunc func() SubmitResult

// chat の watch (解答ファイル保存検知でリロード) のポーリング間隔と debounce。
// test --watch / start と同値。
const (
	chatWatchInterval = 200 * time.Millisecond
	chatWatchDebounce = 120 * time.Millisecond
)

// Spawner は子プロセスを (再) 起動するためのファクトリ。
// chat TUI は連続テスト用にこれを複数回呼び出すことがある。
type Spawner func() (*runner.ChatHandle, error)

// RunChat は spawner で子プロセスを起動し、対話 TUI を駆動する。
// header.AutoRestart が真なら、子が終了するたびに spawner を再呼び出して新セッション
// を始める (sticky)。偽なら子終了で TUI を閉じる。最終的に最後の (= 現在の) セッション
// の ProcessResult を返す。
func RunChat(spawn Spawner, header ChatHeader) (*runner.ProcessResult, error) {
	// 遅延起動: 開いた時点では子を起動しない。最初の入力で spawn する。
	model := initialChatModel(header, spawn)
	finalModel, err := tea.NewProgram(model).Run()
	if err != nil {
		return nil, err
	}
	cm, ok := finalModel.(*chatModel)
	if !ok || cm.handle == nil {
		return &runner.ProcessResult{}, nil // 子を 1 度も起動しなかった (入力なしで終了)
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
	kind  string
	text  string
	at    time.Time // 行を読み出した時刻 (出力行の経過時間算出に使う)
	epoch int       // 発行時の sessionN。現行と不一致なら破棄 (旧 scanner の残響)
}

type streamEndMsg struct {
	kind  string // "out" or "err"
	epoch int    // chatLineMsg と同様、現行 sessionN と不一致なら破棄
}

// fileChangedMsg は watch ポーリングの結果。changed が真なら解答ファイルが保存された。
type fileChangedMsg struct{ changed bool }

// spinnerTickMsg は出力待ちスピナーのアニメ tick。gen が現行 spinGen と不一致なら破棄。
type spinnerTickMsg struct{ gen int }

// spinnerFrames は待機スピナーのコマ (braille)。spinnerInterval ごとに 1 コマ進める。
var spinnerFrames = []string{"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"}

const spinnerInterval = 100 * time.Millisecond

// waitStatus はスピナーのコマと経過時間を 1 行にする純粋関数 (例 "⠹ 0.4s")。
// 経過は出力行の経過時間カラムと揃えるため formatDur を流用する。
func waitStatus(frame int, elapsed time.Duration) string {
	f := spinnerFrames[((frame%len(spinnerFrames))+len(spinnerFrames))%len(spinnerFrames)]
	return f + " " + formatDur(elapsed)
}

type chatLine struct {
	kind       string
	text       string
	dur        time.Duration // 直前イベントからの経過時間 (出力行のみ)
	hasDur     bool          // dur が有効か (入力行 / 情報行は false)
	verdict    string        // ライブ検証の判定 ("" / verdictOK / verdictNG)。出力行のみ
	verdictExp string        // verdictNG のときの期待値 (表示用)
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
	running       bool           // 子プロセスが生きているか。遅延起動 / 入力での再実行を制御する
	ctrlDArmed    bool           // 直前のキーが Ctrl+D (= 次の Ctrl+D で chat 終了)。KeyMsg ごとに先頭でクリアし Ctrl+D 1 回目だけ立て直す (要件 030)
	autoRestart   bool           // sticky モード。起動フラグ (--auto-restart) で初期化。子終了後は「入力で再実行」になる
	autoHintShown bool           // auto-restart ヒント表示済みフラグ
	watcher       *watch.Watcher // 非 nil なら解答ファイルを監視 (保存検知で reload)。nil なら watch-reload 無効
	sessionN      int            // 1 始まり。restart で incr して区切りに番号を出す (epoch も兼ねる)
	lastEventAt   time.Time      // 最後の入力送信 or 出力受信の時刻 (出力行の経過時間の基準)
	awaiting      bool           // 送信後・次の出力待ちなら true (スピナー + 経過時間を出す)
	awaitSince    time.Time      // 待機開始時刻 (経過時間の基準)
	spinnerFrame  int            // スピナーのコマ index
	spinGen       int            // スピナー tick の世代。Enter/restart で更新し旧 tick を無効化
	width         int
	height        int
	ready         bool

	// ケース作成 + ライブ検証 (要件 024)。
	mode          chatMode        // insert (既定) / command / builder
	cmdInput      textinput.Model // command モードの `:` 行
	cmdCandidates []string        // Tab 補完の候補一覧 (複数一致時に `:` 行直下へ表示。要件 031)
	builder       *caseBuilder    // 非 nil ならケースビルダーを開いている
	verify        *verifier       // 非 nil ならライブ検証中
	lastExpected  []string        // 直近のビルダーで入力した expected (`:set verify` の対象)
	sessionInputs []string        // 現セッションで送信した入力行 (`:case` の .in 前埋め)
}

// initialChatModel は遅延起動の chat モデルを作る。子プロセスは開いた時点では
// 起動せず (handle=nil・running=false)、最初の入力 (Enter) で初めて spawn する。
func initialChatModel(header ChatHeader, spawn Spawner) *chatModel {
	submitHint := ""
	if header.Submit != nil {
		submitHint = "  /  Ctrl+S で提出準備"
	}
	ti := textinput.New()
	ti.Placeholder = "Enter で送信  /  Ctrl+C で中断・再起動  /  Ctrl+D でリセット・2回で終了" + submitHint
	ti.Focus()
	ti.Prompt = "" // プロンプト記号は View 側で描画する

	m := &chatModel{
		spawn:       spawn,
		header:      header,
		input:       ti,
		historyPos:  0,
		sessionN:    0, // 最初の入力での spawn で 1 になる
		lastEventAt: time.Now(),
		autoRestart: header.AutoRestart && spawn != nil,
	}
	// 解答ファイルが指定され、再 spawn 可能なときだけ watch-reload を有効にする。
	if header.WatchPath != "" && spawn != nil {
		m.watcher = watch.New(header.WatchPath, chatWatchInterval, chatWatchDebounce)
	}
	// 遅延起動なので「入力で起動する」ことを案内する。子はまだ動いていないので
	// auto-restart のヒントは初回 spawn 時 (restart) に出す。
	m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(入力を送ると解答プログラムを起動します — Ctrl+C で中断・再起動 / Ctrl+D でリセット・2回で終了" + submitHint + ")"})
	return m
}

func (m *chatModel) Init() tea.Cmd {
	// 遅延起動: 子はまだ無いので stream 読み出しは始めない。入力 (Enter) で spawn し、
	// そのとき restart() が readLineCmd を発行する。
	return tea.Batch(textinput.Blink, m.pollWatchCmd())
}

// readLineCmd は scanner から 1 行 (or EOF) を読み、対応する msg を返す tea.Cmd。
// 各行読み出しごとに自身を再発行することで継続的に stream を吸い出す
// (Update 側が chatLineMsg を受けたら readLineCmd を Cmd として返す)。
// epoch は発行時の sessionN。リロードで scanner を差し替えた後に届く旧 scanner の
// 残響を Update 側で破棄するために持たせる。
func readLineCmd(scanner *bufio.Scanner, kind string, epoch int) tea.Cmd {
	return func() tea.Msg {
		if scanner.Scan() {
			// 経過時間を正確にするため、行が読めた瞬間の時刻を記録する
			// (Update 側の処理遅延を含めない)。
			return chatLineMsg{kind: kind, text: scanner.Text(), at: time.Now(), epoch: epoch}
		}
		return streamEndMsg{kind: kind, epoch: epoch}
	}
}

// pollWatchCmd は watcher を持つときだけ、interval 後に 1 回 poll して fileChangedMsg
// を返す tea.Cmd。fileChangedMsg を受けるたびに再発行して継続ポーリングする。
func (m *chatModel) pollWatchCmd() tea.Cmd {
	w := m.watcher
	if w == nil {
		return nil
	}
	return func() tea.Msg {
		time.Sleep(chatWatchInterval)
		return fileChangedMsg{changed: w.Changed()}
	}
}

// spinnerTickCmd は spinnerInterval 後に世代タグ付きの spinnerTickMsg を返す tea.Cmd。
func (m *chatModel) spinnerTickCmd() tea.Cmd {
	gen := m.spinGen
	return tea.Tick(spinnerInterval, func(time.Time) tea.Msg { return spinnerTickMsg{gen: gen} })
}

// startAwaiting は出力待ちを開始し、スピナー tick を 1 本起動する Cmd を返す。
// 世代 (spinGen) を更新するので、連続送信でも tick ループは常に 1 本だけになる。
func (m *chatModel) startAwaiting() tea.Cmd {
	m.awaiting = true
	m.awaitSince = time.Now()
	m.spinnerFrame = 0
	m.spinGen++
	return m.spinnerTickCmd()
}

// stopAwaiting は出力待ちを終える (スピナーを消す)。tick は世代不一致で自然に止まる。
func (m *chatModel) stopAwaiting() {
	m.awaiting = false
}

// restart は spawner で子プロセスを (再) 起動し、TUI 側の状態をリセットする。
// 遅延起動の初回も再実行 (watch-reload / 子終了後の入力) も同じ経路を通る。
// scrollback は保持し、2 回目以降は区切り行 (── session #N ──) を入れる。
func (m *chatModel) restart() tea.Cmd {
	// 既存の子が居れば片付ける。watch-reload では実行中の子を差し替えるため Kill →
	// Wait で reap する (終了済み・初回 nil なら Kill はスキップ/無害)。
	if m.handle != nil {
		_ = m.handle.Kill()
		_ = m.handle.Wait()
	}
	newHandle, err := m.spawn()
	if err != nil {
		m.msgs = append(m.msgs, chatLine{kind: kindErr, text: "spawn failed: " + err.Error()})
		m.refreshViewport()
		return tea.Quit
	}
	m.handle = newHandle
	m.running = true
	m.outScanner = bufio.NewScanner(newHandle.Stdout)
	m.outScanner.Buffer(make([]byte, 64*1024), 1024*1024)
	m.errScanner = bufio.NewScanner(newHandle.Stderr)
	m.errScanner.Buffer(make([]byte, 64*1024), 1024*1024)
	m.endedOut = false
	m.endedErr = false
	m.stopAwaiting()           // 新セッションでは出力待ちをリセット (旧 tick は世代不一致で止まる)
	m.lastEventAt = time.Now() // 新セッション開始を経過時間の基準にリセット
	m.sessionInputs = nil      // :case の .in 前埋めは現セッション分のみ
	if m.verify != nil {       // 新セッションは expected を頭から照合し直す
		m.verify.pos = 0
	}
	m.sessionN++
	// 初回 spawn (session #1) は区切り線を出さない。再実行以降だけ仕切る。
	if m.sessionN > 1 {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: fmt.Sprintf("─── session #%d ───", m.sessionN)})
	}
	// auto-restart 指定時は初回 spawn で一度だけ「子終了後も入力で再実行する」旨を出す。
	if m.autoRestart && !m.autoHintShown {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(auto-restart on — 子終了後も入力で再実行 / Ctrl+C で中断・再起動 / Ctrl+D でリセット・2回で終了)"})
		m.autoHintShown = true
	}
	m.refreshViewport()
	return tea.Batch(
		readLineCmd(m.outScanner, kindOut, m.sessionN),
		readLineCmd(m.errScanner, kindErr, m.sessionN),
	)
}

// submitPrep は Ctrl+S の提出準備。注入された Submit フックを呼び、結果を chat の
// 1 行 (成功=info / 失敗=err) に積む。フック未注入なら利用不可を伝える。stdout には
// 書かない (TUI を壊さないため)。
func (m *chatModel) submitPrep() {
	if m.header.Submit == nil {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(提出準備は利用できません)"})
		return
	}
	res := m.header.Submit()
	kind := kindInfo
	if res.IsError {
		kind = kindErr
	}
	m.msgs = append(m.msgs, chatLine{kind: kind, text: "(提出準備: " + res.Message + ")"})
}

// addInfoLine は親 (startSplitModel) が chat に情報行を 1 つ積むためのヘルパー。
// 再ターゲット時の移動案内・着手メッセージを新しい chat に出すのに使う (要件 027)。
func (m *chatModel) addInfoLine(text string) {
	m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: text})
}

// addErrLine は親が chat にエラー行を 1 つ積むためのヘルパー。ナビゲーションの
// 境界・非対応・不正 spec を 1 行で通知するのに使う (chat は継続。要件 027)。
func (m *chatModel) addErrLine(text string) {
	m.msgs = append(m.msgs, chatLine{kind: kindErr, text: text})
}

// shutdown は走っている子プロセスを kill+wait する。再ターゲットで chat を作り直す前に
// 旧問題の子を片付けるために親が呼ぶ (要件 027)。
func (m *chatModel) shutdown() {
	if m.handle != nil {
		_ = m.handle.Kill()
		_ = m.handle.Wait()
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
		if m.builder != nil {
			m.builder.setWidth(m.width - 2)
		}
		// viewport の高さは refreshViewport の中で content 行数 + maxViewportHeight()
		// から動的に決定する (空のあいだは入力ボックスを画面の上の方に出す)。
		m.refreshViewport()

	case tea.KeyMsg:
		// Ctrl+D の連続押下判定 (要件 030): どのキーでもまず武装を解き、Ctrl+D の
		// 1 回目だけ立て直す。出力到着等の非キー msg では解かない (この case に来ない)。
		wasArmedD := m.ctrlDArmed
		m.ctrlDArmed = false

		// command / builder モードはキーを横取りする (要件 024)。insert モードは従来どおり。
		switch m.mode {
		case modeCommand:
			return m.updateCommand(msg)
		case modeBuilder:
			return m.updateBuilder(msg)
		}
		switch msg.Type {
		case tea.KeyEsc:
			// insert → command モード (`:` 行)。vim 風 (ADR 0007)。
			return m, m.enterCommandMode()
		case tea.KeyCtrlC:
			// Ctrl+C = プログラム中断・再起動 (要件 025)。走っている子を kill して
			// 新しいプロセスでやり直す (新セッション)。chat には留まる。chat 終了
			// (Ctrl+D) とは区別する。auto-restart の ON/OFF を問わず同じ挙動。
			// 遅延起動で子が居なくても restart() が新規 spawn する (明示操作なのでループ源にならない)。
			if m.spawn == nil {
				// 再起動できない経路では中断後に会話を続けられないので、従来どおり
				// kill して終了にフォールバックする。
				if m.handle != nil {
					_ = m.handle.Kill()
				}
				return m, tea.Quit
			}
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(プログラムを中断しました — 再起動します)"})
			return m, m.restart()
		case tea.KeyCtrlD:
			// Ctrl+D = 1 回目: プログラムをリセット (Ctrl+C 相当の restart()。chat に留まる)
			// + 「もう一度で終了」を武装。2 回連続: chat を終了 (子 kill → quit)。要件 030。
			// 「連続」は間に他のキーが挟まらないこと (wasArmedD)。子に EOF は送らない (要件 021)。
			if wasArmedD {
				if m.handle != nil {
					_ = m.handle.Kill()
				}
				return m, tea.Quit
			}
			m.ctrlDArmed = true
			if m.spawn == nil {
				// 再起動できない経路ではリセットできないので武装のみ。
				m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(もう一度 Ctrl+D で chat を終了)"})
				return m, nil
			}
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(プログラムをリセットしました — もう一度 Ctrl+D で chat を終了)"})
			return m, m.restart()
		case tea.KeyCtrlS:
			// Ctrl+S = 提出準備 (test --submit 相当: 解答コピー + 提出ページ起動)。
			// 子は kill せず chat に留まる。結果は画面内の 1 行で示す (stdout には書かない)。
			m.submitPrep()
			m.refreshViewport()
		case tea.KeyEnter:
			txt := m.input.Value()
			// 子が居なければ入力を機に (再) 起動する (遅延起動 / 子終了後の再実行)。
			// これにより、入力を読まず即終了する解答でも無限ループにならない。
			if !m.running {
				cmds = append(cmds, m.restart())
			}
			if !m.running {
				// spawn 失敗 (restart が tea.Quit を返した)。入力は送らない。
			} else if _, err := fmt.Fprintln(m.handle.Stdin, txt); err != nil {
				m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(write failed: " + err.Error() + ")"})
			} else {
				m.msgs = append(m.msgs, chatLine{kind: kindIn, text: txt})
				m.lastEventAt = time.Now()                     // 入力を受け付けた時刻 = 次の出力の経過時間の基準
				m.sessionInputs = append(m.sessionInputs, txt) // :case の .in 前埋め用 (現セッション分)
				if txt != "" {
					m.history = append(m.history, txt)
				}
				m.historyPos = len(m.history)
				// 送信成功 → 出力待ち。スピナー + 経過時間をライブ表示する。
				cmds = append(cmds, m.startAwaiting())
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
		if msg.epoch != m.sessionN {
			break // リロードで差し替えた旧 scanner の残響 → 破棄 (再発行もしない)
		}
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
			m.stopAwaiting() // 出力が返ったので待機解除 (スピナーを消す)
		}
		// ライブ検証: stdout 行を expected と順に突き合わせ、判定を行に添える (要件 024)。
		if kind == kindOut {
			m.applyVerify(&line)
		}
		m.msgs = append(m.msgs, line)
		m.refreshViewport()
		// 同じ stream の次行を読む Cmd を再発行して継続的に吸い出す。
		switch msg.kind {
		case kindOut:
			cmds = append(cmds, readLineCmd(m.outScanner, kindOut, m.sessionN))
		case kindErr:
			cmds = append(cmds, readLineCmd(m.errScanner, kindErr, m.sessionN))
		}

	case spinnerTickMsg:
		if msg.gen != m.spinGen || !m.awaiting {
			break // 古い世代 or 待機解除済み → 止める (再アームしない)
		}
		m.spinnerFrame++
		m.refreshViewport() // 最後尾のスピナー行をアニメ更新
		return m, m.spinnerTickCmd()

	case streamEndMsg:
		if msg.epoch != m.sessionN {
			break // リロードで kill した旧セッションの stream 終了 → 破棄
		}
		m.stopAwaiting()    // 子が終了したら待機解除
		m.refreshViewport() // 最後尾のスピナー行を消す
		switch msg.kind {
		case kindOut:
			m.endedOut = true
		case kindErr:
			m.endedErr = true
		}
		if m.endedOut && m.endedErr {
			m.running = false
			// 子終了で即再 spawn はしない (入力を読まず終了する解答の無限ループを断つ)。
			// auto-restart は「子終了後、次の入力で再実行」を意味する。
			if m.autoRestart && m.spawn != nil {
				m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(解答が終了しました — 入力を送ると再実行します)"})
				m.refreshViewport()
				return m, nil
			}
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(child process exited)"})
			m.refreshViewport()
			return m, tea.Quit
		}

	case fileChangedMsg:
		// 解答ファイルが保存された: 実行中の子だけ最新ファイルで差し替える。
		// 子が居ない (入力待ち) ときは何もしない — 次の入力で最新ファイルを起動する。
		if msg.changed && m.running {
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(解答ファイルが更新されました — 新しいプログラムを起動します)"})
			return m, tea.Batch(m.restart(), m.pollWatchCmd())
		}
		// 変化なし or 子なしでも、次の保存を拾うためポーリングは続ける。
		return m, m.pollWatchCmd()
	}

	return m, tea.Batch(cmds...)
}

func (m *chatModel) View() string {
	if !m.ready {
		return ""
	}
	// ケースビルダーを開いている間 (builder / builder 付き command) は、その画面を
	// ヘッダの下に重ねて出す (子の出力は止めず裏で流れ続けるが画面はビルダー優先)。
	if m.builder != nil {
		return strings.Join([]string{m.renderHeader(), m.renderBuilder()}, "\n")
	}
	// メッセージが無いときは viewport を描画せず、入力ボックスをヘッダの真下に置く。
	// 1 件でも出力 / 入力があれば viewport を含めてレンダリングする。
	parts := []string{m.renderHeader()}
	if len(m.msgs) > 0 || m.awaiting {
		parts = append(parts, m.viewport.View())
	}
	// command モード (builder 無し) は入力ボックスの代わりに `:` 行 (+ 補完候補) を出す。
	if m.mode == modeCommand {
		parts = append(parts, m.renderCommandLine())
	} else {
		parts = append(parts, m.renderInputBox())
	}
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
	// 出力待ちスピナーは入力ボックスの下ではなく出力の最後尾 (refreshViewport) に出す。
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
		// 各メッセージは viewport 幅で折り返し、継続行はインデントを揃えて
		// 折り返しマーカー (↪) を付ける (長い出力がクリップされて途切れるのを防ぐ)。
		sb.WriteString(renderMsgBlock(msg, m.width))
	}
	content := sb.String()
	// 出力待ち中はスピナー + 経過時間を出力の **最後尾** に 1 行足す
	// (入力ボックスの下ではなく scrollback の末尾に「次の出力をロード中」を出す)。
	if m.awaiting {
		spin := chatWaitStyle.Render(waitStatus(m.spinnerFrame, time.Since(m.awaitSince)))
		if content != "" {
			content += "\n" + spin
		} else {
			content = spin
		}
	}
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

// leadColW は行頭カラム (経過時間 + 区切りスペース) の表示幅。継続行のインデントに使う。
const leadColW = durWidth + 1

// wrapMarker は折り返しの継続行を示すマーカー (矢印カラムに dim で置く)。
const wrapMarker = "↪"

// renderMsgBlock は 1 メッセージを viewport 幅で折り返した複数行ブロックにする。
//   - 1 行目: 経過時間カラム + 矢印 + 本文の先頭チャンク
//   - 継続行: leadColW 分の空白 + 折り返しマーカー (↪) + 本文の続き
//
// 経過時間カラム (leadColW) も矢印/マーカーのカラムも全行で揃うので、入力・出力・
// 折り返し継続のインデントが一致する。kindInfo は矢印を持たないので幅で折り返すだけ。
func renderMsgBlock(msg chatLine, width int) string {
	if width < 1 {
		width = 1
	}
	if msg.kind == kindInfo {
		chunks := hardWrap(msg.text, width)
		for i := range chunks {
			chunks[i] = infoStyle.Render(chunks[i])
		}
		return strings.Join(chunks, "\n")
	}

	var arrow string
	var promptStyle, textStyle lipgloss.Style
	switch msg.kind {
	case kindIn:
		arrow, promptStyle, textStyle = "→", chatInPromptStyle, chatInTextStyle
	case kindOut:
		arrow, promptStyle, textStyle = "←", chatOutPromptStyle, chatOutTextStyle
	case kindDebug:
		arrow, promptStyle, textStyle = "*", chatDebugPromptStyle, chatDebugTextStyle
	case kindErr:
		arrow, promptStyle, textStyle = "✖", chatErrPromptStyle, chatErrTextStyle
	}

	// 本文の開始カラム = leadColW + 矢印(1) + スペース(1)。残り幅で折り返す。
	avail := width - (leadColW + 2)
	if avail < 1 {
		avail = 1
	}
	chunks := hardWrap(msg.text, avail)
	contIndent := strings.Repeat(" ", leadColW)
	out := make([]string, 0, len(chunks))
	for i, c := range chunks {
		if i == 0 {
			// 1 行目の末尾にライブ検証の判定 (✓ / ✗ expected …) を添える。
			out = append(out, leadCol(msg)+promptStyle.Render(arrow)+" "+textStyle.Render(c)+verdictSuffix(msg))
		} else {
			out = append(out, contIndent+chatWrapStyle.Render(wrapMarker)+" "+textStyle.Render(c))
		}
	}
	return strings.Join(out, "\n")
}

// hardWrap は s を表示幅 width 以下のチャンクに分割する (語境界に依らないハード折り返し)。
// 競プロ出力は空白を含まない長い数列・文字列もあるため、語折り返しでなく桁で切る。
// CJK 等の全角は runewidth で 2 桁として数える。空文字列は [""] を返す (1 行確保)。
func hardWrap(s string, width int) []string {
	if width < 1 {
		width = 1
	}
	var out []string
	var b strings.Builder
	w := 0
	for _, r := range s {
		rw := runewidth.RuneWidth(r)
		if rw == 0 {
			rw = 1 // 制御文字等の保険
		}
		if w+rw > width && b.Len() > 0 {
			out = append(out, b.String())
			b.Reset()
			w = 0
		}
		b.WriteRune(r)
		w += rw
	}
	out = append(out, b.String())
	return out
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
	chatDebugTextStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0)) // debug 本文は補助情報なので最も dim な overlay 色に落とす
	chatErrPromptStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)
	chatErrTextStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaMaroon))
	// 出力行に添える経過時間。種別の色を邪魔しないよう最も dim な overlay 色。
	chatTimeStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0))
	// 折り返し継続行のマーカー (↪)。本文を邪魔しないよう dim な overlay 色。
	chatWrapStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0))
	// 出力待ちスピナー + 経過時間。注意を引きつつ主張しすぎない sapphire 系。
	chatWaitStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSapphire))
)
