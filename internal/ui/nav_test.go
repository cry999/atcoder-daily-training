package ui

import (
	"strings"
	"testing"
)

// parseCommand は :task / :contest / :e を正規化し、既存コマンドと旧文法は不変。
func TestParseCommandNav(t *testing.T) {
	cases := []struct{ in, name, arg string }{
		{"task next", "task", "next"},
		{"task n", "task", "n"},
		{"task prev", "task", "prev"},
		{"task p", "task", "p"},
		{"task", "task", ""},
		{"contest next", "contest", "next"},
		{"contest p", "contest", "p"},
		{"contest", "contest", ""},
		{"e f", "e", "f"},
		{"e abc500_d", "e", "abc500_d"},
		{"edit g", "e", "g"},
		// 旧単一動詞文法は廃止 → 未知コマンド扱い。
		{"next", "unknown", "next"},
		{"prev", "unknown", "prev"},
		{"fwd", "unknown", "fwd"},
		{"back", "unknown", "back"},
		// 既存コマンドは不変。
		{"case", "case", ""},
		{"c", "case", ""},
		{"w extra", "w", "extra"},
		{"set verify", "set", "verify"},
		{"q", "q", ""},
		{"zzz", "unknown", "zzz"},
	}
	for _, c := range cases {
		got := parseCommand(c.in)
		if got.name != c.name || got.arg != c.arg {
			t.Errorf("parseCommand(%q) = {name:%q arg:%q}, want {name:%q arg:%q}", c.in, got.name, got.arg, c.name, c.arg)
		}
	}
}

func TestNavRequestFor(t *testing.T) {
	cases := []struct {
		cmd  command
		want NavRequest
		ok   bool
	}{
		{command{name: "task", arg: "next"}, NavRequest{Kind: NavLetterNext}, true},
		{command{name: "task", arg: "n"}, NavRequest{Kind: NavLetterNext}, true},
		{command{name: "task", arg: "prev"}, NavRequest{Kind: NavLetterPrev}, true},
		{command{name: "task", arg: "p"}, NavRequest{Kind: NavLetterPrev}, true},
		{command{name: "contest", arg: "next"}, NavRequest{Kind: NavContestNext}, true},
		{command{name: "contest", arg: "n"}, NavRequest{Kind: NavContestNext}, true},
		{command{name: "contest", arg: "prev"}, NavRequest{Kind: NavContestPrev}, true},
		{command{name: "contest", arg: "p"}, NavRequest{Kind: NavContestPrev}, true},
		{command{name: "e", arg: "abc500_d"}, NavRequest{Kind: NavExplicit, Spec: "abc500_d"}, true},
		{command{name: "e"}, NavRequest{Kind: NavExplicit}, true},
		// 第 2 トークン欠落・不正は ok=false。
		{command{name: "task"}, NavRequest{}, false},
		{command{name: "task", arg: "foo"}, NavRequest{}, false},
		{command{name: "contest"}, NavRequest{}, false},
		{command{name: "case"}, NavRequest{}, false},
		{command{name: "unknown", arg: "zzz"}, NavRequest{}, false},
	}
	for _, c := range cases {
		got, ok := navRequestFor(c.cmd)
		if ok != c.ok || got != c.want {
			t.Errorf("navRequestFor(%+v) = (%+v, %v), want (%+v, %v)", c.cmd, got, ok, c.want, c.ok)
		}
	}
}

// NavEnabled が真なら execNav は NavMsg を発火し、insert に戻る。
func TestExecNavEnabledEmitsNavMsg(t *testing.T) {
	cases := []struct {
		cmd  command
		want NavKind
	}{
		{command{name: "task", arg: "next"}, NavLetterNext},
		{command{name: "contest", arg: "p"}, NavContestPrev},
		{command{name: "e", arg: "abc458_f"}, NavExplicit},
	}
	for _, c := range cases {
		m := &chatModel{header: ChatHeader{NavEnabled: true}, mode: modeCommand}
		_, cmd := m.execNav(c.cmd)
		if m.mode != modeInsert {
			t.Fatalf("mode = %v, want modeInsert", m.mode)
		}
		if cmd == nil {
			t.Fatalf("execNav(%+v): expected a NavMsg command, got nil", c.cmd)
		}
		nav, ok := cmd().(NavMsg)
		if !ok {
			t.Fatalf("execNav(%+v): cmd() = %T, want NavMsg", c.cmd, cmd())
		}
		if nav.Req.Kind != c.want {
			t.Errorf("execNav(%+v): Req.Kind = %v, want %v", c.cmd, nav.Req.Kind, c.want)
		}
	}
}

// :task / :contest の第 2 トークンが欠落・不正なら NavMsg を発火せず利用法を案内する。
func TestExecNavBadSubShowsUsage(t *testing.T) {
	m := &chatModel{header: ChatHeader{NavEnabled: true}, mode: modeCommand}
	_, cmd := m.execNav(command{name: "task"})
	if cmd != nil {
		t.Errorf("expected nil cmd for bare :task, got non-nil")
	}
	if len(m.msgs) == 0 || !strings.Contains(m.msgs[len(m.msgs)-1].text, ":task next|prev") {
		t.Errorf("expected usage hint, msgs = %+v", m.msgs)
	}
}

// NavEnabled が偽 (test --interactive 単体) なら execNav は E492 を出し NavMsg を発火しない。
func TestExecNavDisabledIsUnknown(t *testing.T) {
	m := &chatModel{header: ChatHeader{NavEnabled: false}, mode: modeCommand}
	_, cmd := m.execNav(command{name: "task", arg: "next"})
	if cmd != nil {
		t.Errorf("expected nil cmd when nav disabled, got non-nil")
	}
	if m.mode != modeInsert {
		t.Errorf("mode = %v, want modeInsert", m.mode)
	}
	if len(m.msgs) == 0 || !strings.Contains(m.msgs[len(m.msgs)-1].text, "E492") {
		t.Errorf("expected E492 line, msgs = %+v", m.msgs)
	}
}
