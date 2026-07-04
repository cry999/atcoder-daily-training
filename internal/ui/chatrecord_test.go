package ui

import (
	"errors"
	"reflect"
	"strings"
	"testing"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/solvestat"
)

// :record は parseCommand で name="record" になり、サブコマンド + フラグは arg に載る (要件 064)。
func TestParseCommandRecord(t *testing.T) {
	cases := []struct {
		in      string
		wantArg string
	}{
		{"record", ""},
		{"record start", "start"},
		{"record start restart", "start restart"},
		{"record stop ac", "stop ac"},
		{"record ac score=2,3,2,3,1", "ac score=2,3,2,3,1"},
	}
	for _, c := range cases {
		got := parseCommand(c.in)
		if got.name != "record" || got.arg != c.wantArg {
			t.Errorf("parseCommand(%q) = {name:%q arg:%q}, want {record %q}", c.in, got.name, got.arg, c.wantArg)
		}
	}
}

// execRecord は arg を空白で分けて Record フックへ渡し、返った行を info 行で積む。
func TestExecRecordDelegates(t *testing.T) {
	var gotArgs []string
	m := &chatModel{header: ChatHeader{
		Record: func(args []string) ([]string, error) {
			gotArgs = args
			return []string{"記録しました: abc/457/d.py", "  ac=true  editorial=false"}, nil
		},
	}}

	m.execRecord("ac score=2,3,2,3,1")

	if want := []string{"ac", "score=2,3,2,3,1"}; !reflect.DeepEqual(gotArgs, want) {
		t.Fatalf("Record args = %v, want %v", gotArgs, want)
	}
	got := lastN(m, 2)
	for i, want := range []string{"記録しました: abc/457/d.py", "  ac=true  editorial=false"} {
		if got[i].kind != kindInfo || got[i].text != want {
			t.Fatalf("line %d = {%q %q}, want {info %q}", i, got[i].kind, got[i].text, want)
		}
	}
}

// 引数なし :record は Record を空 args で呼ぶ (現在値表示。フックが表示行を返す)。
func TestExecRecordNoArgs(t *testing.T) {
	called := false
	m := &chatModel{header: ChatHeader{
		Record: func(args []string) ([]string, error) {
			called = true
			if len(args) != 0 {
				t.Fatalf("args = %v, want empty", args)
			}
			return []string{"  実装 23m / 目標 35m (-12m, 達成)"}, nil
		},
	}}

	m.execRecord("")

	if !called {
		t.Fatal("Record フックが呼ばれていない")
	}
	if last := m.msgs[len(m.msgs)-1]; last.kind != kindInfo || !strings.Contains(last.text, "達成") {
		t.Fatalf("line = {%q %q}", last.kind, last.text)
	}
}

// Record が error を返したら err 行で表示し、chat は継続する。
func TestExecRecordError(t *testing.T) {
	m := &chatModel{header: ChatHeader{
		Record: func([]string) ([]string, error) {
			return nil, errors.New("解答ファイルがありません。先に :record start してください")
		},
	}}

	m.execRecord("stop")

	if last := m.msgs[len(m.msgs)-1]; last.kind != kindErr || !strings.Contains(last.text, "解答ファイルがありません") {
		t.Fatalf("line = {%q %q}, want err with reason", last.kind, last.text)
	}
}

// Record 未注入 (nil) のとき :record は「使えません」を 1 行出すだけ (パニックしない)。
func TestExecRecordUnavailable(t *testing.T) {
	m := &chatModel{header: ChatHeader{}} // フック nil

	m.execRecord("start")

	if last := m.msgs[len(m.msgs)-1]; last.kind != kindInfo || !strings.Contains(last.text, "使えません") {
		t.Fatalf("text=%q", last.text)
	}
}

// formatRecElapsed は経過を mm:ss (1h 以上は h:mm:ss)、負値は 00:00 に整形する。
func TestFormatRecElapsed(t *testing.T) {
	cases := []struct {
		d    time.Duration
		want string
	}{
		{-5 * time.Second, "00:00"},
		{0, "00:00"},
		{9 * time.Second, "00:09"},
		{75 * time.Second, "01:15"},
		{59*time.Minute + 59*time.Second, "59:59"},
		{time.Hour + 2*time.Minute + 3*time.Second, "1:02:03"},
	}
	for _, c := range cases {
		if got := formatRecElapsed(c.d); got != c.want {
			t.Errorf("formatRecElapsed(%v) = %q, want %q", c.d, got, c.want)
		}
	}
}

// :record start で記録インジケーターが点灯し (ヘッダに ● REC が出る)、tick Cmd を返す。
// :record stop で計測中マーカー (● REC) は消え、終了マーカー (✓ かかった時間) へ切り替わる。
func TestExecRecordTogglesIndicator(t *testing.T) {
	m := &chatModel{header: ChatHeader{
		Task: "d.py", Contest: "abc457", TimeLimitMs: 2000,
		Record: func([]string) ([]string, error) { return []string{"計測を開始しました: abc/457/d.py"}, nil },
	}}

	// start: recording が立ち、tick Cmd が返り、ヘッダにマーカーが出る。
	cmd := m.execRecord("start")
	if !m.recording {
		t.Fatal("start 後に recording が false")
	}
	if cmd == nil {
		t.Fatal("start は毎秒 tick の Cmd を返すべき")
	}
	if h := m.renderHeader(); !strings.Contains(h, "● REC") {
		t.Fatalf("ヘッダに計測中マーカー (● REC) が無い: %q", h)
	}
	genAfterStart := m.recordGen

	// stop: recording が下り、世代が進み (走っている tick を止める)、計測中マーカーは消えて
	// 終了マーカー (✓ かかった時間) へ切り替わる。
	if cmd := m.execRecord("stop"); cmd != nil {
		t.Fatal("stop は tick Cmd を返さない")
	}
	if m.recording {
		t.Fatal("stop 後に recording が true")
	}
	if m.recordGen == genAfterStart {
		t.Fatal("stop で recordGen が進んでいない (旧 tick を止められない)")
	}
	if h := m.renderHeader(); strings.Contains(h, "● REC") {
		t.Fatalf("stop 後もヘッダに計測中マーカー (● REC) が残る: %q", h)
	}
	if h := m.renderHeader(); !m.recordDone || !strings.Contains(h, "✓") {
		t.Fatalf("stop 後は終了マーカー (✓ かかった時間) を出すべき: %q", h)
	}
}

// 記録中に届いた recordTickMsg は、世代が一致すれば再 tick の Cmd を返して継続する。
// 世代不一致 (stop 後の残響) や停止済みなら再アームしない。
func TestRecordTickMsgReArmsOnlyWhileRecording(t *testing.T) {
	m := &chatModel{header: ChatHeader{
		Record: func([]string) ([]string, error) { return []string{"計測を開始しました"}, nil },
	}}
	m.execRecord("start")

	// 現行世代の tick → 継続 (Cmd 非 nil)。
	if _, cmd := m.Update(recordTickMsg{gen: m.recordGen}); cmd == nil {
		t.Fatal("記録中の tick は再 tick すべき")
	}
	// 旧世代の tick → 破棄 (Cmd nil)。
	if _, cmd := m.Update(recordTickMsg{gen: m.recordGen - 1}); cmd != nil {
		t.Fatal("旧世代の tick は破棄すべき")
	}
	// stop 後の tick → 破棄。
	m.execRecord("stop")
	if _, cmd := m.Update(recordTickMsg{gen: m.recordGen}); cmd != nil {
		t.Fatal("停止後の tick は破棄すべき")
	}
}

// ヘッダの記録マーカーは 3 状態を出し分ける: 未開始は "○ REC --:--"、計測中は "● REC 経過"、
// 終了済み (solved_at 確定) は "✓ かかった時間"。restoreRecordingFromStat が solve-stat から
// これを復元する。
func TestRecordIndicatorThreeStates(t *testing.T) {
	// 未開始: 記録なし → ○ REC --:-- (計測中/終了マーカーは出ない)。
	idle := &chatModel{header: ChatHeader{Task: "d.py", Contest: "abc457", TimeLimitMs: 2000}}
	if h := idle.renderHeader(); !strings.Contains(h, "○ REC --:--") {
		t.Fatalf("未開始は ○ REC --:-- を出すべき: %q", h)
	}
	if h := idle.renderHeader(); strings.Contains(h, "● REC") || strings.Contains(h, "✓") {
		t.Fatalf("未開始で計測中/終了マーカーが出ている: %q", h)
	}

	// 終了済み: started_at・solved_at 確定・duration_ms=125000 (2:05) → ✓ 02:05。
	started := time.Now().Add(-10 * time.Minute)
	done := &chatModel{header: ChatHeader{
		Task: "d.py", Contest: "abc457", TimeLimitMs: 2000,
		RecordEditLoad: func() (solvestat.Stat, int64, bool, error) {
			return solvestat.Stat{StartedAt: started, SolvedAt: started.Add(125 * time.Second), DurationMs: 125000}, 0, true, nil
		},
	}}
	done.restoreRecordingFromStat()
	if done.recording || !done.recordDone {
		t.Fatalf("終了済み stat は recordDone=true・recording=false にすべき: recording=%v done=%v", done.recording, done.recordDone)
	}
	if h := done.renderHeader(); !strings.Contains(h, "✓ 02:05") {
		t.Fatalf("終了済みは ✓ かかった時間 (02:05) を出すべき: %q", h)
	}
	if h := done.renderHeader(); strings.Contains(h, "REC") {
		t.Fatalf("終了済みで REC マーカーが残っている: %q", h)
	}

	// duration_ms が無い終了済みは started_at→solved_at 差でかかった時間を補う (3:00)。
	noDur := &chatModel{header: ChatHeader{
		RecordEditLoad: func() (solvestat.Stat, int64, bool, error) {
			return solvestat.Stat{StartedAt: started, SolvedAt: started.Add(3 * time.Minute)}, 0, true, nil
		},
	}}
	noDur.restoreRecordingFromStat()
	if h := noDur.renderHeader(); !strings.Contains(h, "✓ 03:00") {
		t.Fatalf("duration_ms 無しは started_at 差 (03:00) で補うべき: %q", h)
	}
}
