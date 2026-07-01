package ui

import (
	"errors"
	"reflect"
	"strings"
	"testing"
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
