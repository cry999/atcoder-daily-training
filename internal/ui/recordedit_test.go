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

	// ac (row 0): 'n' で false。
	m.handleKey(runeKey('n'))
	// editorial (row 1): Backspace で未記録。
	m.handleKey(key(tea.KeyDown))
	m.handleKey(key(tea.KeyBackspace))
	// impl (row 6): 数字 1。ac(0)→ed(1) から下へ 5 つ (dur,knowledge,translation,complexity,impl)。
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

	// ac=true から Right → false → 未記録 → true。
	f := &m.fields[0]
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

	// score=2 (knowledge, row 3) を Right 連打で 3 に張り付く。
	s := &m.fields[3]
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
	// duration は row 2。
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
	// ac(0) と knowledge(3) を未記録へ。
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
