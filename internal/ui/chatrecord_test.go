package ui

import (
	"errors"
	"reflect"
	"strings"
	"testing"
	"time"
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
// :record stop で消灯し、以降ヘッダにマーカーが出ない。
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
	if h := m.renderHeader(); !strings.Contains(h, "REC") || !strings.Contains(h, "●") {
		t.Fatalf("ヘッダに記録マーカーが無い: %q", h)
	}
	genAfterStart := m.recordGen

	// stop: recording が下り、世代が進み (走っている tick を止める)、ヘッダにマーカーが出ない。
	if cmd := m.execRecord("stop"); cmd != nil {
		t.Fatal("stop は tick Cmd を返さない")
	}
	if m.recording {
		t.Fatal("stop 後に recording が true")
	}
	if m.recordGen == genAfterStart {
		t.Fatal("stop で recordGen が進んでいない (旧 tick を止められない)")
	}
	if h := m.renderHeader(); strings.Contains(h, "REC") {
		t.Fatalf("stop 後もヘッダに記録マーカーが残る: %q", h)
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
