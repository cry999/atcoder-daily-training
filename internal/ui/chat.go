package ui

import (
	"bufio"
	"fmt"
	"math"
	"os/exec"
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
	// SubmitCheck は Ctrl+S の提出前チェック (要件 044)。非 nil なら提出準備の前に
	// サンプルを実行し、クリーンでなければ理由を出して y/N 確認を挟む。composition
	// root が注入する (internal/ui は testexec/layout を知らないため)。
	SubmitCheck SubmitCheckFunc
	TaskDir     string   // cache の <contest>/<task> dir。非空なら :w でケースを tests-extra に保存できる (要件 024)
	Tolerance   float64  // ライブ検証の許容誤差 (0 なら既定 1e-6)
	NavEnabled  bool     // true なら :task next|prev / :contest next|prev / :e で問題ナビ可 (start 分割画面限定。要件 027)
	Edit        EditFunc // 非 nil なら Ctrl+E で解答ファイルをエディタで開ける。composition root が注入する (要件 038)

	// PrevInputs は同じ問題の前回 chat 起動で子へ送った入力行。:replay の cross-run
	// フォールバック (今回まだ何も打っていない初回起動でのみ使う)。composition root が
	// chatlog.LoadLastSession で先読みして渡す (要件 039)。
	PrevInputs []string
	// RecordInput は子へ送った各行を永続化するフック。非 nil なら submitLines が各行で呼ぶ。
	// internal/ui は filesystem/XDG を知らないため composition root が注入する (Submit/Edit と同じ層境界)。
	RecordInput func(line string)

	// MetaShow / MetaSet は :meta コマンド (要件 055) で meta.toml を表示・編集するフック。
	// 両方とも非 nil なら chat 内から url / time_limit を確認・上書きできる。internal/ui は
	// testexec/layout を知らないため、読み書き・検証・整形は composition root に逃がす
	// (Submit/Edit と同じ層境界)。
	//
	// MetaShow は表示行を返す。field="" なら全体 (url/time limit/samples)、field="url"/"time_limit"
	// なら当該フィールドのみ。未キャッシュ等は error。
	MetaShow func(field string) (lines []string, err error)
	// MetaSet は field ("url"/"time_limit") を value で上書きし、結果行と (time_limit を更新した
	// ときの) 新しい time_limit_ms を返す。検証失敗・未キャッシュは error。
	MetaSet func(field, value string) (lines []string, newTimeLimitMs int, err error)
	// MetaFetch は :meta fetch (要件 057) で meta.toml の url (override 優先) から
	// サンプル + Time Limit を再取得するフック。結果行と (Time Limit が変わったときの)
	// 新しい time_limit_ms を返す。ネットワーク呼び出しを伴うため chat は tea.Cmd で
	// 非同期に呼ぶ (Ctrl+E の editDoneMsg と同型)。composition root が
	// testexec.EnsureTests(refresh=true) をサイレント reporter で実行する
	// (internal/ui は testexec を知らないため)。
	MetaFetch func() (lines []string, newTimeLimitMs int, err error)
}

// EditPlan は Ctrl+E のエディタ起動計画。composition root の EditFunc が返す (要件 038)。
//   - Exec 非 nil: 端末を奪ってエディタを起動する (nvim 外)。chat は tea.ExecProcess で回す。
//   - Exec nil:    端末を奪わず即完了したケース (nvim へ remote 送信済み or 失敗)。Message を 1 行表示。
type EditPlan struct {
	Exec    *exec.Cmd
	Message string
	IsError bool
}

// EditFunc は chat の Ctrl+E で呼ばれるエディタ起動フック。解答パスを受け取り EditPlan を返す。
// internal/ui は cmd/atcoder を import できないため、composition root が注入する。
type EditFunc func(path string) EditPlan

// editDoneMsg は tea.ExecProcess (端末を奪うエディタ起動) の完了通知。
type editDoneMsg struct{ err error }

// metaFetchDoneMsg は :meta fetch (要件 057) の非同期再取得の完了通知。
// lines は表示する結果行 (fetched/url/time limit/samples)、newTimeLimitMs は
// Time Limit が変わったときの新値 (> 0 ならヘッダに反映)、err は取得失敗。
type metaFetchDoneMsg struct {
	lines          []string
	newTimeLimitMs int
	err            error
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

// SubmitCheck は提出前チェックの結果 (要件 044)。Clean ならそのまま提出してよく、
// そうでなければ Reasons を確認プロンプトに添えて y/N を問う。
type SubmitCheck struct {
	Clean   bool     // true なら確認不要でそのまま提出してよい
	Reasons []string // Clean=false のとき、確認を促す理由 (各 1 行)
}

// SubmitCheckFunc は chat の Ctrl+S で提出準備の前に呼ばれるチェックフック。
// サンプルを実行して提出可否を判定する。composition root が注入する (testexec を回す)。
type SubmitCheckFunc func() SubmitCheck

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

// tracebackHeader は Python の未捕捉例外 (= Runtime Error) traceback の先頭行。
const tracebackHeader = "Traceback (most recent call last):"

// classifyTraceback は統合ストリーム (stdout+stderr を 1 本に束ねた出力, StartChat 参照) の
// 1 行が Python traceback (= stderr 由来の Runtime Error) の一部かを、行内容と直前までの状態
// から判定する。順序保証のため stream の由来情報が失われるので、traceback ブロックを行内容
// から復元して kindErr に色付けし直すために使う。isErr が真ならその行は err 扱い、next は
// 次行へ引き継ぐ traceback 状態。
func classifyTraceback(inTraceback bool, line string) (isErr, next bool) {
	// 連鎖例外 (__cause__ / __context__) のブリッジ行。traceback ブロックを跨いで続く。
	bridge := line == "During handling of the above exception, another exception occurred:" ||
		line == "The above exception was the direct cause of the following exception:"
	switch {
	case strings.HasPrefix(line, tracebackHeader) || bridge:
		// traceback の開始 (または連鎖の継続)。
		return true, true
	case inTraceback:
		// ブロック中。非空・非インデントの行 = 例外メッセージ行でブロックは終わる
		// (それ自体は err 表示)。インデント行 (フレーム) や空行は継続。
		if line != "" && line[0] != ' ' && line[0] != '\t' {
			return true, false
		}
		return true, true
	default:
		return false, false
	}
}

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
	inTraceback   bool           // 統合ストリーム上で Python traceback (= stderr 由来) ブロックの途中か。kindErr 色を復元するための状態 (セッションごとに restart でリセット)
	running       bool           // 子プロセスが生きているか。遅延起動 / 入力での再実行を制御する
	ctrlDArmed    bool           // 直前のキーが Ctrl+D (= 次の Ctrl+D で chat 終了)。KeyMsg ごとに先頭でクリアし Ctrl+D 1 回目だけ立て直す (要件 030)
	scrolled      bool           // scrollback を上にスクロール中 (= 出力到着で最下部に引き戻さない)。command/insert 双方で使う。最下部復帰で false (要件 033/040)
	submitConfirm bool           // 提出前チェックでリスクが見つかり y/N 確認待ち (要件 044)。次の打鍵を回答として消費する
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
	mode              chatMode        // insert (既定) / command / builder
	cmdInput          textinput.Model // command モードの `:` 行
	cmdCandidates     []string        // Tab 補完の候補一覧 (複数一致時に `:` 行直下へ表示。要件 031)
	builder           *caseBuilder    // 非 nil ならケースビルダーを開いている
	verify            *verifier       // 非 nil ならライブ検証中
	lastExpected      []string        // 直近のビルダーで入力した expected (`:set verify` の対象)
	sessionInputs     []string        // 現 (子) セッションで送信した入力行 (`:case` の .in 前埋め / :replay の第一候補。子リスタートで nil)
	prevSessionInputs []string        // 直前に完了した (空でない) 子セッションの入力行 (:replay のフォールバック。要件 039)
	lastTest          *testReplay     // 直近に :test で流したサンプルケース。:replay が「直近の操作」として再送 + 再検証する (今回の起動内でのみ保持。要件 048)
	lastOpWasTest     bool            // 直近の「再生対象となる操作」が :test ケースなら true、手入力なら false。:replay が手入力/テストを判定する手がかり。:replay 自身はこれを変えない (連続 :replay で対象が遡らないように。要件 048 / バグ報告)
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
	m.scrolled = false // 中断・リセット・再起動時は最下部に戻して追従再開 (要件 040)
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
	m.inTraceback = false      // 新セッションは traceback 検出状態を頭からやり直す
	m.stopAwaiting()           // 新セッションでは出力待ちをリセット (旧 tick は世代不一致で止まる)
	m.lastEventAt = time.Now() // 新セッション開始を経過時間の基準にリセット
	m.beginNewSession()        // 直前セッションの入力を prevSessionInputs に退避し sessionInputs をリセット
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

// submitPrep は Ctrl+S の提出準備。SubmitCheck が注入されていれば先にサンプルを
// 実行してチェックし (要件 044)、リスクがあれば理由を出して確認モード (submitConfirm)
// に入る。クリーン or チェック未注入なら doSubmit で即提出する。フック未注入なら利用
// 不可を伝える。stdout には書かない (TUI を壊さないため)。
func (m *chatModel) submitPrep() {
	if m.header.Submit == nil {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(提出準備は利用できません)"})
		return
	}
	if m.header.SubmitCheck != nil {
		check := m.header.SubmitCheck()
		if !check.Clean {
			for _, r := range check.Reasons {
				m.msgs = append(m.msgs, chatLine{kind: kindErr, text: "提出前チェック: " + r})
			}
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "このまま提出準備しますか? [y/N]"})
			m.submitConfirm = true
			return
		}
	}
	m.doSubmit()
}

// doSubmit は注入された Submit フックを呼んで提出準備を実行し、結果を 1 行に積む。
func (m *chatModel) doSubmit() {
	res := m.header.Submit()
	kind := kindInfo
	if res.IsError {
		kind = kindErr
	}
	m.msgs = append(m.msgs, chatLine{kind: kind, text: "(提出準備: " + res.Message + ")"})
}

// editFile は Ctrl+E のエディタ起動。注入された Edit フックに解答パス (WatchPath) を渡す。
// nvim 内 (remote 送信) など端末を奪わないケースは結果を 1 行表示して nil を返す。nvim 外で
// 端末を奪うケースは tea.ExecProcess の tea.Cmd を返す (呼び出し側が return する)。
func (m *chatModel) editFile() tea.Cmd {
	if m.header.Edit == nil {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(エディタ起動は利用できません)"})
		return nil
	}
	if m.header.WatchPath == "" {
		m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(エディタで開く解答ファイルが不明です)"})
		return nil
	}
	plan := m.header.Edit(m.header.WatchPath)
	if plan.Exec != nil {
		// 端末を奪ってエディタを起動 (nvim 外)。終了後に editDoneMsg で復帰結果を出す。
		return tea.ExecProcess(plan.Exec, func(err error) tea.Msg { return editDoneMsg{err: err} })
	}
	// remote 送信済み or 失敗: 結果を 1 行表示。
	kind := kindInfo
	if plan.IsError {
		kind = kindErr
	}
	m.msgs = append(m.msgs, chatLine{kind: kind, text: "(" + plan.Message + ")"})
	return nil
}

// beginNewSession は子セッションの境界 (restart) で呼ぶ。終わった子セッションの入力を
// prevSessionInputs に退避し (空セッションでは上書きしない — 直前の実入力を残す)、
// sessionInputs をリセットする。:replay は「直前の (child) セッションだけ」を再生するため、
// 起動を通した累積ではなく 1 セッション分だけを保持する (要件 039)。
func (m *chatModel) beginNewSession() {
	if len(m.sessionInputs) > 0 {
		m.prevSessionInputs = m.sessionInputs
	}
	m.sessionInputs = nil
}

// replayLines は :replay の対象とする入力行を返す。優先順位は
//  1. 現セッションの入力 (sessionInputs)        — いま打っている / 直前に打ったセッション
//  2. 直前に完了したセッション (prevSessionInputs) — reload 直後など現セッションが空のとき
//  3. 前回 chat 起動の入力 (header.PrevInputs)   — 今回まだ何も打っていない初回起動
//
// いずれも「直前の 1 セッション分」で、起動を通した手入力すべての累積ではない (要件 039)。
func (m *chatModel) replayLines() []string {
	if len(m.sessionInputs) > 0 {
		return m.sessionInputs
	}
	if len(m.prevSessionInputs) > 0 {
		return m.prevSessionInputs
	}
	return m.header.PrevInputs
}

// submitLines は lines を順に子 stdin へ送る (各 Fprintln + kindIn echo + 履歴)。
// 単一行 Enter と複数行ペースト ([034]) で共有する送信ロジック。子が居なければ最初の
// 送信を機に (再) 起動し (遅延起動)、1 行でも送れたら最後に出力待ちを 1 回起動する。
// 必要な tea.Cmd (restart / startAwaiting) は cmds に追記する。
//
// record は「この入力を手入力として覚えるか」。手入力 (Enter / ペースト) は true で、
// sessionInputs (現セッションの :replay 対象・:case 前埋め) と chatlog (セッション横断の
// 永続化) に積む。:replay の再送は false — 再生行をこれらに積むと、次の :replay が再生値を
// 巻き込んで膨らみ「手入力したセッション」ではなく過去の再生値を流してしまう (要件 039)。
// 子への送信・echo・履歴 (Up/Down)・出力待ちは record に依らず行う。
func (m *chatModel) submitLines(lines []string, cmds *[]tea.Cmd, record bool) {
	if len(lines) == 0 {
		return
	}
	m.scrolled = false // 送信したら最下部 (live view) に戻して追従再開 (要件 040)
	if !m.running {
		// 子が居なければ入力を機に (再) 起動する (遅延起動 / 子終了後の再実行)。
		*cmds = append(*cmds, m.restart())
	}
	if !m.running {
		return // spawn 失敗 (restart が tea.Quit を返した)。送らない。
	}
	sent := false
	for _, txt := range lines {
		if _, err := fmt.Fprintln(m.handle.Stdin, txt); err != nil {
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(write failed: " + err.Error() + ")"})
			break // 書き込み失敗以降は送らない
		}
		m.msgs = append(m.msgs, chatLine{kind: kindIn, text: txt})
		if record {
			// 手入力のみ現セッションの入力として覚える (:case 前埋め / :replay 対象)。
			m.sessionInputs = append(m.sessionInputs, txt)
			m.lastOpWasTest = false // 直近の操作は手入力 → :replay は手入力を再生 (要件 048)
			if m.header.RecordInput != nil {
				m.header.RecordInput(txt) // セッション横断の永続化 (:replay の cross-run フォールバック用。要件 039)。best-effort
			}
		}
		if txt != "" && (len(m.history) == 0 || m.history[len(m.history)-1] != txt) {
			// 直前と同じ内容は履歴に積まない (連続重複の抑制)
			m.history = append(m.history, txt)
		}
		sent = true
	}
	if sent {
		m.lastEventAt = time.Now() // 直近の送信時刻 = 次の出力の経過時間の基準
		m.historyPos = len(m.history)
		// 送信成功 → 出力待ち。スピナー + 経過時間をライブ表示する (バッチで 1 回)。
		*cmds = append(*cmds, m.startAwaiting())
	}
}

// splitPasteLines は現在の入力値 current にペースト pasted を末尾結合し、改行
// (\r\n / \r を \n に正規化) で分割する。send は改行で終わった完全な行 (子へ逐次
// 送信)、remainder は末尾の未改行テキスト (入力欄に残す)。純粋関数 ([034])。
func splitPasteLines(current, pasted string) (send []string, remainder string) {
	combined := current + pasted
	combined = strings.ReplaceAll(combined, "\r\n", "\n")
	combined = strings.ReplaceAll(combined, "\r", "\n")
	parts := strings.Split(combined, "\n")
	return parts[:len(parts)-1], parts[len(parts)-1]
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
			m.viewport = viewport.New(m.contentWidth(), 1)
			m.ready = true
		} else {
			m.viewport.Width = m.contentWidth()
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

		// 提出前チェックの確認待ち (要件 044): 次の打鍵を y/N の回答として消費する。
		// y/Y なら提出準備、それ以外 (n/Esc/その他) は中止して chat を続ける。
		if m.submitConfirm {
			m.submitConfirm = false
			switch msg.String() {
			case "y", "Y":
				m.doSubmit()
			default:
				m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(提出準備を中止しました)"})
			}
			m.refreshViewport()
			return m, nil
		}

		// command / builder モードはキーを横取りする (要件 024)。insert モードは従来どおり。
		switch m.mode {
		case modeCommand:
			return m.updateCommand(msg)
		case modeBuilder:
			return m.updateBuilder(msg)
		}
		// 複数行ペースト (bracketed paste): 各改行を Enter 扱いで完全行を逐次送信し、
		// 末尾の未改行テキストは入力欄に残す (要件 034)。改行を含まない通常ペースト・
		// 打鍵は従来どおり下の switch (default で textinput) に流す。
		if msg.Paste && strings.ContainsAny(string(msg.Runes), "\r\n") {
			send, remainder := splitPasteLines(m.input.Value(), string(msg.Runes))
			m.submitLines(send, &cmds, true) // 手入力 (ペースト) → :replay/永続化の対象
			m.input.SetValue(remainder)
			m.input.CursorEnd()
			m.refreshViewport()
			return m, tea.Batch(cmds...)
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
		case tea.KeyCtrlE:
			// Ctrl+E = 解答ファイルをエディタで開く (要件 038)。nvim 内なら親へ remote 送信
			// (端末を奪わない)、外なら tea.ExecProcess で起動。子は kill せず chat に留まる。
			ecmd := m.editFile()
			m.refreshViewport()
			if ecmd != nil {
				return m, ecmd
			}
		case tea.KeyEnter:
			// 現在行を 1 行送信する (複数行ペーストと送信ロジックを共有)。
			m.submitLines([]string{m.input.Value()}, &cmds, true) // 手入力 (Enter) → :replay/永続化の対象
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
		case tea.KeyPgUp, tea.KeyCtrlB:
			// scrollback を 1 ページ上へ (要件 040)。以降の出力で最下部に引き戻さない。
			// Ctrl+B は textinput の既定カーソル移動を横取りする (← で代替可)。
			m.scrollUp()
		case tea.KeyPgDown, tea.KeyCtrlF:
			// 1 ページ下へ。最下部に達したら追従を再開する (要件 040)。
			m.scrollDown()
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
		// stdout/stderr は 1 本に統合して読む (順序保証, StartChat 参照) ため stream の由来が
		// 失われる。Python traceback (= Runtime Error) を行内容から検出して kindErr に戻し、
		// 赤い色付けを復元する。DEBUG 行 (kindDebug) は stdout 由来なので対象外。
		if kind == kindOut {
			isErr, next := classifyTraceback(m.inTraceback, text)
			m.inTraceback = next
			if isErr {
				kind = kindErr
			}
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

	case editDoneMsg:
		// tea.ExecProcess (端末を奪ったエディタ) の復帰。結果を 1 行示して分割画面へ戻る。
		if msg.err != nil {
			m.msgs = append(m.msgs, chatLine{kind: kindErr, text: "(エディタ終了: " + msg.err.Error() + ")"})
		} else {
			m.msgs = append(m.msgs, chatLine{kind: kindInfo, text: "(エディタを閉じました)"})
		}
		m.refreshViewport()
		return m, nil
	case metaFetchDoneMsg:
		// :meta fetch (要件 057) の非同期再取得の完了。結果行 / err 行を積み、
		// Time Limit が変わればヘッダに反映する。
		m.applyMetaFetchDone(msg)
		m.refreshViewport()
		return m, nil
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
		parts = append(parts, m.renderViewport())
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
		sb.WriteString(renderMsgBlock(msg, m.contentWidth()))
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
	// command モードで上にスクロール中は、出力到着で最下部に引き戻さないよう
	// 現在のスクロール位置 (YOffset) を退避し、content 差し替え後に復元する (要件 032)。
	savedOffset := m.viewport.YOffset
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
	if m.scrolled {
		m.viewport.SetYOffset(savedOffset) // 上スクロール位置を維持 (SetYOffset は範囲内にクランプ)
	} else {
		m.viewport.GotoBottom()
	}
}

// scrollUp は scrollback を 1 ページ上へ送り、追従を止める (出力到着で最下部に
// 引き戻さない)。command / insert モードで共有する (要件 033/040)。
func (m *chatModel) scrollUp() {
	m.viewport.ViewUp()
	m.scrolled = true
}

// scrollDown は scrollback を 1 ページ下へ送る。最下部に達したら追従を再開する。
func (m *chatModel) scrollDown() {
	m.viewport.ViewDown()
	if m.viewport.AtBottom() {
		m.scrolled = false
	}
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

// powerline の角丸キャップ。debug ピルの左右の縁に使う (要 powerline / Nerd Font)。
const (
	plRoundLeft  = "" //  左の半円キャップ (U+E0B6)
	plRoundRight = "" //  右の半円キャップ (U+E0B4)
)

// debugPillWidth は debug ピルの表示幅: 左キャップ(1) + "DEBUG"(5) + 右キャップ(1)。
const debugPillWidth = 7

// debugPill は debug 行の行頭に置く角丸ピル (チップ) を描画する。
func debugPill() string {
	return chatDebugPillCapStyle.Render(plRoundLeft) +
		chatDebugPillTextStyle.Render("DEBUG") +
		chatDebugPillCapStyle.Render(plRoundRight)
}

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

	// prompt = 行頭インディケーター (描画済み文字列)、promptW = その表示幅。
	// debug 行だけは powerline の角丸キャップで囲んだ DEBUG ピル (幅 debugPillWidth) にする。
	var prompt string
	var promptW int
	var textStyle lipgloss.Style
	switch msg.kind {
	case kindIn:
		prompt, promptW, textStyle = chatInPromptStyle.Render("→"), 1, chatInTextStyle
	case kindOut:
		prompt, promptW, textStyle = chatOutPromptStyle.Render("←"), 1, chatOutTextStyle
	case kindDebug:
		prompt, promptW, textStyle = debugPill(), debugPillWidth, chatDebugTextStyle
	case kindErr:
		prompt, promptW, textStyle = chatErrPromptStyle.Render("✖"), 1, chatErrTextStyle
	}

	// 本文の開始カラム = leadColW + インディケーター幅 + スペース(1)。残り幅で折り返す。
	avail := width - (leadColW + promptW + 1)
	if avail < 1 {
		avail = 1
	}
	chunks := hardWrap(msg.text, avail)
	// 継続行のマーカー (↪) はインディケーター末尾カラムに置き、本文カラムを 1 行目と揃える。
	contIndent := strings.Repeat(" ", leadColW+promptW-1)
	out := make([]string, 0, len(chunks))
	for i, c := range chunks {
		if i == 0 {
			// 1 行目の末尾にライブ検証の判定 (✓ / ✗ expected …) を添える。
			out = append(out, leadCol(msg)+prompt+" "+textStyle.Render(c)+verdictSuffix(msg))
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

// chatScrollbarWidth は scrollback 右端に確保するスクロールバー gutter の幅 (列)。
const chatScrollbarWidth = 1

// contentWidth は本文 (折り返し) に使える幅。右端 1 列をスクロールバー gutter に
// 常時確保し、overflow の開始/終了で折り返しがリフローしないようにする (要件 056)。
func (m *chatModel) contentWidth() int {
	if m.width >= 2 {
		return m.width - chatScrollbarWidth
	}
	if m.width >= 1 {
		return m.width
	}
	return 1
}

// renderViewport は viewport の表示に右端スクロールバー列を重ねて返す (要件 056)。
// viewport.View() は各行を contentWidth まで pad するので、その右に gutter 1 列を連結する。
func (m *chatModel) renderViewport() string {
	body := m.viewport.View()
	if m.width < 2 {
		return body // gutter を確保できない狭い端末ではスクロールバー無し
	}
	lines := strings.Split(body, "\n")
	col := m.scrollbarColumn(len(lines))
	for i := range lines {
		lines[i] += col[i]
	}
	return strings.Join(lines, "\n")
}

// scrollbarColumn は h 行分の gutter 文字列 (スタイル適用済み) を返す。scrollback が
// スクロール可能なら track の上に thumb を重ね、収まっているなら全て空白にする (要件 056)。
func (m *chatModel) scrollbarColumn(h int) []string {
	col := make([]string, h)
	total := m.viewport.TotalLineCount()
	// total <= h は「1 画面に収まる」= スクロール不要。gutter は空白にする。
	// (viewport.ScrollPercent は total <= h で 1.0 を返すので、ここで先にゲートする)
	if h <= 0 || total <= h {
		for i := range col {
			col[i] = " "
		}
		return col
	}
	// thumb の長さ = 表示高 × 表示高 / 総行数 (下限 1・上限 h)。
	thumb := int(math.Round(float64(h*h) / float64(total)))
	if thumb < 1 {
		thumb = 1
	}
	if thumb > h {
		thumb = h
	}
	// thumb の開始行 = スクロール率 × (h - thumb)。
	start := int(math.Round(m.viewport.ScrollPercent() * float64(h-thumb)))
	if start < 0 {
		start = 0
	}
	if start > h-thumb {
		start = h - thumb
	}
	for i := 0; i < h; i++ {
		if i >= start && i < start+thumb {
			col[i] = chatScrollThumbStyle.Render("█")
		} else {
			col[i] = chatScrollTrackStyle.Render("│")
		}
	}
	return col
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
	// debug 行のインディケーターは powerline の角丸キャップ ( / ) で
	// ラベンダー背景の "DEBUG" を挟んだ角丸ピル (チップ) にしてポップに見せる。
	// キャップは「ピル背景色」を foreground にして端末既定背景の上に描くことで丸い縁になる。
	chatDebugPillCapStyle  = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaLavender))
	chatDebugPillTextStyle = lipgloss.NewStyle().Background(lipgloss.Color(mochaLavender)).Foreground(lipgloss.Color(mochaBase)).Bold(true)
	chatDebugTextStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0)) // debug 本文は補助情報なので最も dim な overlay 色に落とす
	chatErrPromptStyle     = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaRed)).Bold(true)
	chatErrTextStyle       = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaMaroon))
	// 出力行に添える経過時間。種別の色を邪魔しないよう最も dim な overlay 色。
	chatTimeStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0))
	// 折り返し継続行のマーカー (↪)。本文を邪魔しないよう dim な overlay 色。
	chatWrapStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay0))
	// 出力待ちスピナー + 経過時間。注意を引きつつ主張しすぎない sapphire 系。
	chatWaitStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSapphire))
	// scrollback 右端のスクロールバー (要件 056)。track はレールなので最も dim な
	// surface1、thumb は現在地なので一段明るい overlay1 にして本文を邪魔しない。
	chatScrollTrackStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaSurface1))
	chatScrollThumbStyle = lipgloss.NewStyle().Foreground(lipgloss.Color(mochaOverlay1))
)
