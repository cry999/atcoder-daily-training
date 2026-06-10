package ui

import (
	"strings"
	"testing"
)

// parseCommand はナビゲーションコマンド (別名含む) を正規化し、既存コマンドは不変。
func TestParseCommandNav(t *testing.T) {
	cases := []struct{ in, name, arg string }{
		{"next", "next", ""},
		{"n", "next", ""},
		{"prev", "prev", ""},
		{"p", "prev", ""},
		{"fwd", "fwd", ""},
		{"f", "fwd", ""},
		{"back", "back", ""},
		{"b", "back", ""},
		{"e f", "e", "f"},
		{"e abc500_d", "e", "abc500_d"},
		{"edit g", "e", "g"},
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
		{command{name: "next"}, NavRequest{Kind: NavLetterNext}, true},
		{command{name: "prev"}, NavRequest{Kind: NavLetterPrev}, true},
		{command{name: "fwd"}, NavRequest{Kind: NavContestNext}, true},
		{command{name: "back"}, NavRequest{Kind: NavContestPrev}, true},
		{command{name: "e", arg: "abc500_d"}, NavRequest{Kind: NavExplicit, Spec: "abc500_d"}, true},
		{command{name: "e"}, NavRequest{Kind: NavExplicit}, true},
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
	m := &chatModel{header: ChatHeader{NavEnabled: true}, mode: modeCommand}
	_, cmd := m.execNav(command{name: "e", arg: "abc458_f"})
	if m.mode != modeInsert {
		t.Fatalf("mode = %v, want modeInsert", m.mode)
	}
	if cmd == nil {
		t.Fatal("expected a NavMsg command, got nil")
	}
	nav, ok := cmd().(NavMsg)
	if !ok {
		t.Fatalf("cmd() = %T, want NavMsg", cmd())
	}
	if nav.Req.Kind != NavExplicit || nav.Req.Spec != "abc458_f" {
		t.Errorf("Req = %+v, want {NavExplicit abc458_f}", nav.Req)
	}
}

// NavEnabled が偽 (test --interactive 単体) なら execNav は E492 を出し NavMsg を発火しない。
func TestExecNavDisabledIsUnknown(t *testing.T) {
	m := &chatModel{header: ChatHeader{NavEnabled: false}, mode: modeCommand}
	_, cmd := m.execNav(command{name: "next"})
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
