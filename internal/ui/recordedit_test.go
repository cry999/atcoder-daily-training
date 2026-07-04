package ui

import (
	"strings"
	"testing"
	"time"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cry999/atcoder-daily-training/internal/solvestat"
)

// key はテスト用に tea.KeyMsg を組む小ヘルパー。
func key(t tea.KeyType) tea.KeyMsg { return tea.KeyMsg{Type: t} }

// runeKey は 1 文字の入力キーを組む。
func runeKey(r rune) tea.KeyMsg { return tea.KeyMsg{Type: tea.KeyRunes, Runes: []rune{r}} }

// baseStat は編集元の Stat。started_at/solved_at/target と各値を持つ。
func baseStat() solvestat.Stat {
	start := time.Date(2026, 7, 1, 16, 0, 0, 0, time.UTC)
	solved := time.Date(2026, 7, 1, 16, 25, 30, 0, time.UTC) // 秒を持たせて duration 桁落ちを検証
	st := solvestat.Empty()
	st.StartedAt = start
	st.SolvedAt = solved
	st.DurationMs = 1530500 // 25m30.5s
	st.TargetMs = 2100000
	st.AC = solvestat.BoolPtr(true)
	st.Editorial = solvestat.BoolPtr(false)
	st.Score = solvestat.Score{Knowledge: 2, Translation: 3, Complexity: 2, Impl: 3, Verify: 1}
	return st
}

// 未編集フィールドは保存時に元値を温存する (特に duration は ms 単位で桁落ちしない)。
// 保全フィールド (started_at/solved_at/target_ms) も引き継ぐ。
func TestRecordEdit_PreservesUntouched(t *testing.T) {
	st := baseStat()
	m := newRecordEditModel("abc457_d", st, st.TargetMs, false)
	m.handleKey(key(tea.KeyCtrlS)) // 何も編集せず保存
	if !m.saved || !m.done {
		t.Fatalf("saved=%v done=%v", m.saved, m.done)
	}
	got := m.resultStat()
	if got.DurationMs != st.DurationMs {
		t.Errorf("duration 桁落ち: got=%d want=%d", got.DurationMs, st.DurationMs)
	}
	if !got.StartedAt.Equal(st.StartedAt) || !got.SolvedAt.Equal(st.SolvedAt) || got.TargetMs != st.TargetMs {
		t.Errorf("保全フィールドが変わった: %+v", got)
	}
	if got.AC == nil || !*got.AC || got.Editorial == nil || *got.Editorial {
		t.Errorf("ac/editorial が変わった: ac=%v ed=%v", got.AC, got.Editorial)
	}
	if got.Score != st.Score {
		t.Errorf("score が変わった: %+v", got.Score)
	}
}

// カーソル移動 + 値の書き換え: ac を false に、editorial を未記録に、impl を 1 に変える。
func TestRecordEdit_EditFields(t *testing.T) {
	st := baseStat()
	m := newRecordEditModel("abc457_d", st, st.TargetMs, false)

	// state(0) → ac(1): 1 つ下げる (要件 068 で state 行が先頭に増えた)。
	m.handleKey(key(tea.KeyDown))
	if m.cur().label != "ac" {
		t.Fatalf("cursor=%q want ac", m.cur().label)
	}
	// ac (row 1): 'n' で false。
	m.handleKey(runeKey('n'))
	// editorial (row 2): Backspace で未記録。
	m.handleKey(key(tea.KeyDown))
	m.handleKey(key(tea.KeyBackspace))
	// impl (row 7): 数字 1。ed(2) から下へ 5 つ (dur,knowledge,translation,complexity,impl)。
	for i := 0; i < 5; i++ {
		m.handleKey(key(tea.KeyDown))
	}
	if m.cur().label != "impl" {
		t.Fatalf("cursor=%q want impl", m.cur().label)
	}
	m.handleKey(runeKey('1'))
	m.handleKey(key(tea.KeyCtrlS))

	got := m.resultStat()
	if got.AC == nil || *got.AC {
		t.Errorf("ac want false got %v", got.AC)
	}
	if got.Editorial != nil {
		t.Errorf("editorial want 未記録(nil) got %v", *got.Editorial)
	}
	if got.Score.Impl != 1 {
		t.Errorf("impl want 1 got %d", got.Score.Impl)
	}
	// 触っていない knowledge は温存。
	if got.Score.Knowledge != 2 {
		t.Errorf("knowledge want 2 got %d", got.Score.Knowledge)
	}
}

// ←→ で tri-bool を循環し、score を端で止める。
func TestRecordEdit_CycleAndClamp(t *testing.T) {
	st := baseStat()
	m := newRecordEditModel("abc457_d", st, st.TargetMs, false)

	// ac=true から Right → false → 未記録 → true (ac は state 行の下、row 1)。
	f := &m.fields[1]
	f.cycle(+1)
	if f.boolVal == nil || *f.boolVal {
		t.Fatalf("cycle+1 from true want false")
	}
	f.cycle(+1)
	if f.boolVal != nil {
		t.Fatalf("cycle+1 from false want 未記録")
	}
	f.cycle(+1)
	if f.boolVal == nil || !*f.boolVal {
		t.Fatalf("cycle+1 from 未記録 want true")
	}

	// score=2 (knowledge, row 4) を Right 連打で 3 に張り付く。
	s := &m.fields[4]
	s.cycle(+1) // 3
	s.cycle(+1) // 3 のまま
	if s.scoreVal != 3 {
		t.Fatalf("score clamp high want 3 got %d", s.scoreVal)
	}
	for i := 0; i < 6; i++ {
		s.cycle(-1)
	}
	if s.scoreVal != -1 {
		t.Fatalf("score clamp low want -1 got %d", s.scoreVal)
	}
}

// duration を編集すると ParseDuration で解釈し、不正なら保存を止める。
func TestRecordEdit_DurationEditAndValidate(t *testing.T) {
	st := baseStat()
	m := newRecordEditModel("abc457_d", st, st.TargetMs, false)
	// duration は row 3 (state 行の分だけ下がった)。
	m.handleKey(key(tea.KeyDown))
	m.handleKey(key(tea.KeyDown))
	m.handleKey(key(tea.KeyDown))
	if m.cur().label != "duration" {
		t.Fatalf("cursor=%q want duration", m.cur().label)
	}
	// バッファを全消しして "10m" を打つ。
	for i := 0; i < 12; i++ {
		m.handleKey(key(tea.KeyBackspace))
	}
	for _, r := range "10m" {
		m.handleKey(runeKey(r))
	}
	m.handleKey(key(tea.KeyCtrlS))
	if !m.saved {
		t.Fatalf("valid duration should save")
	}
	if got := m.resultStat().DurationMs; got != int64(10*time.Minute/time.Millisecond) {
		t.Errorf("duration want 600000 got %d", got)
	}

	// 不正な duration は保存を止める。
	m2 := newRecordEditModel("abc457_d", st, st.TargetMs, false)
	m2.handleKey(key(tea.KeyDown))
	m2.handleKey(key(tea.KeyDown))
	m2.handleKey(key(tea.KeyDown))
	for i := 0; i < 12; i++ {
		m2.handleKey(key(tea.KeyBackspace))
	}
	for _, r := range "99" { // 単位なし → ParseDuration 失敗
		m2.handleKey(runeKey(r))
	}
	m2.handleKey(key(tea.KeyCtrlS))
	if m2.saved || m2.done {
		t.Fatalf("invalid duration should not save: saved=%v done=%v", m2.saved, m2.done)
	}
	if m2.errMsg == "" {
		t.Fatalf("errMsg should be set for invalid duration")
	}
}

// j/k で上下移動し、Enter で保存できる (要件 066 のキー変更)。
func TestRecordEdit_JKMoveEnterSave(t *testing.T) {
	st := baseStat()
	m := newRecordEditModel("abc457_d", st, st.TargetMs, false)

	// j 連打で impl (row 7) まで下げ、k で 1 つ戻して complexity (row 6) に置く
	// (state 行が先頭に増えて各行が 1 つ下がった)。
	for i := 0; i < 7; i++ {
		m.handleKey(runeKey('j'))
	}
	if m.cur().label != "impl" {
		t.Fatalf("after j*7 cursor=%q want impl", m.cur().label)
	}
	m.handleKey(runeKey('k'))
	if m.cur().label != "complexity" {
		t.Fatalf("after k cursor=%q want complexity", m.cur().label)
	}
	// 端 (row 0 = state) を越えて k しても止まる。
	for i := 0; i < 10; i++ {
		m.handleKey(runeKey('k'))
	}
	if m.cursor != 0 {
		t.Fatalf("k clamp top want 0 got %d", m.cursor)
	}

	// Enter で保存できる。
	m.handleKey(key(tea.KeyEnter))
	if !m.saved || !m.done {
		t.Fatalf("Enter should save: saved=%v done=%v", m.saved, m.done)
	}
}

// Esc は取消 (saved=false, done=true)、ファイルは書かない前提。
func TestRecordEdit_Cancel(t *testing.T) {
	st := baseStat()
	m := newRecordEditModel("abc457_d", st, st.TargetMs, false)
	m.handleKey(runeKey('n')) // 何か編集しても
	m.handleKey(key(tea.KeyEsc))
	if m.saved || !m.done {
		t.Fatalf("Esc should cancel: saved=%v done=%v", m.saved, m.done)
	}
}

// クリアした tri-bool/score は Overwrite で当該キーが落ちる (未記録に戻る)。
func TestRecordEdit_ClearDropsKeys(t *testing.T) {
	st := baseStat()
	m := newRecordEditModel("abc457_d", st, st.TargetMs, false)
	// ac(1) と knowledge(4) を未記録へ (state 行の分だけ下がった)。
	m.handleKey(key(tea.KeyDown))      // state(0) → ac(1)
	m.handleKey(key(tea.KeyBackspace)) // ac 未記録
	for i := 0; i < 3; i++ {
		m.handleKey(key(tea.KeyDown))
	}
	m.handleKey(key(tea.KeyBackspace)) // knowledge 未記録
	m.handleKey(key(tea.KeyCtrlS))

	out, err := solvestat.Overwrite(nil, m.resultStat())
	if err != nil {
		t.Fatal(err)
	}
	s := string(out)
	if strings.Contains(s, "\n# ac ") || strings.Contains(s, "ac          =") {
		t.Errorf("ac キーが残っている:\n%s", s)
	}
	if strings.Contains(s, "knowledge") {
		t.Errorf("knowledge キーが残っている:\n%s", s)
	}
	// editorial は残る (false のまま)。
	if !strings.Contains(s, "editorial") {
		t.Errorf("editorial キーが落ちている:\n%s", s)
	}
}

// state 行は started_at/solved_at から状態を導出する (要件 068)。
func TestRecordEditState_Derive(t *testing.T) {
	if got := newRecordEditModel("t", baseStat(), 0, false).state(); got != stStopped {
		t.Errorf("started+solved want stStopped got %d", got)
	}
	run := solvestat.Empty()
	run.StartedAt = time.Now()
	if got := newRecordEditModel("t", run, 0, false).state(); got != stRunning {
		t.Errorf("started only want stRunning got %d", got)
	}
	if got := newRecordEditModel("t", solvestat.Empty(), 0, false).state(); got != stIdle {
		t.Errorf("empty want stIdle got %d", got)
	}
}

// トグルは 未計測 → 計測中(start) → 停止(stop) → 未計測(reset) の 1 方向サイクル。
// start で started_at、stop で solved_at + target スナップショット、reset で全クリア。
func TestRecordEditState_ToggleCycle(t *testing.T) {
	m := newRecordEditModel("t", solvestat.Empty(), 2100000, false)

	m.toggleState() // idle → running
	if m.state() != stRunning || m.startedAt.IsZero() {
		t.Fatalf("start: state=%d started=%v", m.state(), m.startedAt)
	}
	if !m.solvedAt.IsZero() {
		t.Fatalf("start should clear solved_at")
	}

	m.toggleState() // running → stopped
	if m.state() != stStopped || m.solvedAt.IsZero() {
		t.Fatalf("stop: state=%d solved=%v", m.state(), m.solvedAt)
	}
	if m.recordTargetMs != 2100000 {
		t.Fatalf("stop should snapshot target want 2100000 got %d", m.recordTargetMs)
	}

	m.toggleState() // stopped → idle (reset)
	if m.state() != stIdle || !m.startedAt.IsZero() || !m.solvedAt.IsZero() || m.recordTargetMs != 0 {
		t.Fatalf("reset: state=%d started=%v solved=%v target=%d", m.state(), m.startedAt, m.solvedAt, m.recordTargetMs)
	}
}

// stop は now - started_at で duration を確定し、resultStat に反映する。
func TestRecordEditState_StopComputesDuration(t *testing.T) {
	run := solvestat.Empty()
	run.StartedAt = time.Now().Add(-10 * time.Minute)
	m := newRecordEditModel("t", run, 2100000, false)
	if m.state() != stRunning {
		t.Fatalf("want running got %d", m.state())
	}
	m.toggleState() // stop
	got := m.resultStat()
	if got.SolvedAt.IsZero() {
		t.Fatalf("solved_at should be set")
	}
	if got.DurationMs < int64(9*time.Minute/time.Millisecond) {
		t.Errorf("duration want ~10m got %d", got.DurationMs)
	}
	if got.TargetMs != 2100000 {
		t.Errorf("target snapshot want 2100000 got %d", got.TargetMs)
	}
}

// reset (停止 → 未計測) は時刻・duration・target・ac/editorial・5 軸すべてを空へ落とす。
func TestRecordEditState_ResetClearsEverything(t *testing.T) {
	m := newRecordEditModel("t", baseStat(), 2100000, false) // stopped から
	m.toggleState()                                          // stopped → idle (reset)
	got := m.resultStat()
	if !got.StartedAt.IsZero() || !got.SolvedAt.IsZero() {
		t.Errorf("times not cleared: started=%v solved=%v", got.StartedAt, got.SolvedAt)
	}
	if got.DurationMs != 0 || got.TargetMs != 0 {
		t.Errorf("dur/target not cleared: dur=%d target=%d", got.DurationMs, got.TargetMs)
	}
	if got.AC != nil || got.Editorial != nil {
		t.Errorf("ac/editorial not cleared: ac=%v ed=%v", got.AC, got.Editorial)
	}
	want := solvestat.Score{Knowledge: -1, Translation: -1, Complexity: -1, Impl: -1, Verify: -1}
	if got.Score != want {
		t.Errorf("score not cleared: %+v", got.Score)
	}
}

// Tab は state 行では状態を前進させる (要件 068)。
func TestRecordEditState_TabOnStateAdvances(t *testing.T) {
	m := newRecordEditModel("t", solvestat.Empty(), 0, false)
	if m.cur().kind != recFieldState {
		t.Fatalf("cursor should start on state row")
	}
	m.handleKey(key(tea.KeyTab))
	if m.state() != stRunning {
		t.Fatalf("Tab from idle should start, got %d", m.state())
	}
}

// Tab は state 以外のフィールドでは、その場の値をトグルし state は動かさない (要件 068 の挙動変更)。
func TestRecordEditState_TabTogglesFocusedField(t *testing.T) {
	m := newRecordEditModel("t", solvestat.Empty(), 0, false)
	m.handleKey(key(tea.KeyDown)) // state(0) → ac(1)
	if m.cur().label != "ac" || m.cur().boolVal != nil {
		t.Fatalf("cursor=%q ac=%v want ac/nil", m.cur().label, m.cur().boolVal)
	}
	m.handleKey(key(tea.KeyTab)) // ac をトグル (nil → true)
	if m.cur().boolVal == nil || !*m.cur().boolVal {
		t.Fatalf("Tab on ac want true got %v", m.cur().boolVal)
	}
	if m.state() != stIdle {
		t.Fatalf("Tab off state row should not advance state, got %d", m.state())
	}

	// score 行でも前方 cycle (-1 → 0)。
	for i := 0; i < 3; i++ {
		m.handleKey(key(tea.KeyDown)) // ac(1) → knowledge(4)
	}
	if m.cur().label != "knowledge" {
		t.Fatalf("cursor=%q want knowledge", m.cur().label)
	}
	m.handleKey(key(tea.KeyTab))
	if m.cur().scoreVal != 0 {
		t.Fatalf("Tab on knowledge want 0 got %d", m.cur().scoreVal)
	}
}

// state 行では space で前進、Backspace で未計測へリセットできる (reset は確認を挟む。要件 069)。
func TestRecordEditState_SpaceAndBackspaceOnRow(t *testing.T) {
	m := newRecordEditModel("t", solvestat.Empty(), 0, false)
	if m.cur().kind != recFieldState {
		t.Fatalf("cursor should start on state row")
	}
	m.handleKey(key(tea.KeySpace)) // idle → running
	if m.state() != stRunning {
		t.Fatalf("space on state should start, got %d", m.state())
	}
	m.handleKey(key(tea.KeyBackspace)) // Backspace は即リセットせず確認待ちへ (要件 069)
	if !m.pendingReset {
		t.Fatalf("backspace on state should request reset confirm")
	}
	if m.state() != stRunning {
		t.Fatalf("state should stay until confirmed, got %d", m.state())
	}
	m.handleKey(runeKey('y')) // 確認 → reset 実行
	if m.pendingReset {
		t.Fatalf("y should clear pending reset")
	}
	if m.state() != stIdle {
		t.Fatalf("backspace+y on state should reset to idle, got %d", m.state())
	}
}

// reset は確認を挟み、y/Y のときだけ全クリアする (要件 069)。停止からのトグル reset も同様。
func TestRecordEditReset_ConfirmExecutes(t *testing.T) {
	// 停止 → 未計測 トグル: 停止状態で Tab を押すと即リセットせず確認待ちに入る。
	m := newRecordEditModel("t", baseStat(), 2100000, false) // stopped から
	if m.state() != stStopped {
		t.Fatalf("want stopped got %d", m.state())
	}
	m.handleKey(key(tea.KeyTab)) // 停止トグル → 確認待ち (即リセットしない)
	if !m.pendingReset {
		t.Fatalf("tab on stopped state should request reset confirm")
	}
	if m.state() != stStopped {
		t.Fatalf("state should stay stopped until confirmed, got %d", m.state())
	}
	m.handleKey(runeKey('Y')) // 大文字 Y でも確定
	if m.pendingReset || m.state() != stIdle {
		t.Fatalf("Y should confirm reset: pending=%v state=%d", m.pendingReset, m.state())
	}
	got := m.resultStat()
	if !got.StartedAt.IsZero() || !got.SolvedAt.IsZero() || got.DurationMs != 0 || got.AC != nil {
		t.Errorf("reset should clear everything: %+v", got)
	}
}

// 確認待ち中に y 以外のキーを押すと取消され、リセットも本来の操作も起きない (要件 069)。
func TestRecordEditReset_CancelWithOtherKey(t *testing.T) {
	m := newRecordEditModel("t", baseStat(), 2100000, false) // stopped
	m.handleKey(key(tea.KeyBackspace))                       // 確認待ちへ
	if !m.pendingReset {
		t.Fatalf("backspace should request reset confirm")
	}
	m.handleKey(runeKey('n')) // 'n' で取消
	if m.pendingReset {
		t.Fatalf("n should clear pending reset")
	}
	if m.state() != stStopped {
		t.Fatalf("cancel should keep state stopped, got %d", m.state())
	}
	// 取消キーは吸収される: カーソルは動かず (Down を押しても確認取消として消費する例)。
	m.handleKey(key(tea.KeyBackspace)) // もう一度確認待ちへ
	m.handleKey(key(tea.KeyDown))      // 確認待ち中の Down は取消として吸収 (移動しない)
	if m.pendingReset {
		t.Fatalf("down should cancel pending reset")
	}
	if m.cursor != 0 {
		t.Fatalf("cursor should not move while resolving confirm, got %d", m.cursor)
	}
	if m.state() != stStopped {
		t.Fatalf("cancel should keep state stopped, got %d", m.state())
	}
}

// start / stop トグルは破壊的でないので確認を挟まず即実行する (要件 069)。
func TestRecordEditReset_StartStopNoConfirm(t *testing.T) {
	m := newRecordEditModel("t", solvestat.Empty(), 0, false)
	m.handleKey(key(tea.KeyTab)) // idle → running (start)
	if m.pendingReset {
		t.Fatalf("start should not request confirm")
	}
	if m.state() != stRunning {
		t.Fatalf("start should be immediate, got %d", m.state())
	}
	m.handleKey(key(tea.KeyTab)) // running → stopped (stop)
	if m.pendingReset {
		t.Fatalf("stop should not request confirm")
	}
	if m.state() != stStopped {
		t.Fatalf("stop should be immediate, got %d", m.state())
	}
}

// chat の :record edit で計測中を保存すると ● REC が点灯し tick Cmd が返る (要件 068)。
func TestRecordEditChatSyncsRecordingOn(t *testing.T) {
	var saved solvestat.Stat
	m := &chatModel{
		mode: modeRecordEdit,
		header: ChatHeader{
			Task: "abc457_d",
			RecordEditSave: func(st solvestat.Stat) ([]string, error) {
				saved = st
				return []string{"記録を更新しました"}, nil
			},
		},
	}
	m.editForm = newRecordEditModel("abc457_d", solvestat.Empty(), 0, true)

	m.updateRecordEdit(key(tea.KeySpace))           // state 行 (row 0) で idle → running
	_, cmd := m.updateRecordEdit(key(tea.KeyEnter)) // 保存
	if !m.recording {
		t.Fatal("running を保存したら REC 点灯すべき")
	}
	if cmd == nil {
		t.Fatal("running 保存で毎秒 tick の Cmd を返すべき")
	}
	if saved.StartedAt.IsZero() || !saved.SolvedAt.IsZero() {
		t.Fatalf("保存 Stat が running でない: %+v", saved)
	}
	if !m.recordStart.Equal(saved.StartedAt) {
		t.Errorf("recordStart は started_at 基準にすべき: %v != %v", m.recordStart, saved.StartedAt)
	}
}

// 計測中の記録を停止して保存すると ● REC が消灯する (要件 068)。
func TestRecordEditChatSyncsRecordingOff(t *testing.T) {
	run := solvestat.Empty()
	run.StartedAt = time.Now()
	m := &chatModel{
		mode:      modeRecordEdit,
		recording: true, // 点灯中から始める
		header: ChatHeader{
			RecordEditSave: func(st solvestat.Stat) ([]string, error) { return nil, nil },
		},
	}
	m.editForm = newRecordEditModel("t", run, 0, true) // running

	m.updateRecordEdit(key(tea.KeySpace))           // running → stopped
	_, cmd := m.updateRecordEdit(key(tea.KeyEnter)) // 保存
	if m.recording {
		t.Fatal("stopped を保存したら REC 消灯すべき")
	}
	if cmd != nil {
		t.Fatal("stopped 保存では tick Cmd を返さない")
	}
}
