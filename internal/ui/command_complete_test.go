package ui

import (
	"reflect"
	"testing"
)

func TestCompleteCommandLine(t *testing.T) {
	cases := []struct {
		name      string
		line      string
		nav       bool
		wantRepl  string
		wantCands []string
	}{
		// --- 第 1 トークン (コマンド名) ---
		{"unique prefix completes (no arg)", "ca", true, "case", nil},
		{"unique prefix appends space for arg cmd", "se", true, "set ", nil},
		{"unique nav cmd appends space", "ta", true, "task ", nil},
		{"unique nav cmd contest", "co", true, "contest ", nil},
		{"debug unique (no arg)", "de", true, "debug", nil},
		{"cheat unique (no arg)", "ch", true, "cheat", nil},
		{"replay unique (no arg)", "re", true, "replay", nil},
		{"r prefix unique to replay", "r", true, "replay", nil},
		{"test unique appends space for arg cmd", "te", true, "test ", nil},
		{"t ambiguous with nav (task/test)", "t", true, "t", []string{"task", "test"}},
		{"t unique to test without nav", "t", false, "test ", nil}, // task は nav 限定なので消える
		{"ambiguous keeps LCP and lists", "c", true, "c", []string{"case", "cheat", "contest"}},
		{"empty lists all (nav)", "", true, "", []string{"case", "cheat", "contest", "debug", "e", "q", "replay", "set", "task", "test", "w"}},
		{"empty lists base only (no nav)", "", false, "", []string{"case", "cheat", "debug", "q", "replay", "set", "test", "w"}},
		{"no match no change", "zzz", true, "zzz", nil},
		// nav コマンドは navEnabled=false では候補に出ない。
		{"task hidden without nav", "ta", false, "ta", nil},
		{"e hidden without nav", "e", false, "e", nil},
		{"w unique without nav", "w", false, "w", nil}, // w は引数任意なので空白を付けない

		// --- 第 2 トークン (サブトークン) ---
		{"set space lists args", "set ", true, "set ", []string{"debug", "nodebug", "noverify", "verify"}},
		{"set verify unique", "set v", true, "set verify", nil},
		{"set debug unique", "set d", true, "set debug", nil},
		{"set no is ambiguous", "set no", true, "set no", []string{"nodebug", "noverify"}},
		{"set n is ambiguous (nodebug/noverify)", "set n", true, "set no", []string{"nodebug", "noverify"}},
		{"task space lists next/prev", "task ", true, "task ", []string{"next", "prev"}},
		{"task next unique", "task n", true, "task next", nil},
		{"task prev unique", "task p", true, "task prev", nil},
		{"contest next unique", "contest n", true, "contest next", nil},
		{"cmd without subtokens no change", "case ", true, "case ", nil},
		{"q has no subtokens", "q ", true, "q ", nil},

		// --- 第 3 トークン以降は補完しない ---
		{"third token no completion", "set verify ", true, "set verify ", nil},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			repl, cands := completeCommandLine(c.line, c.nav)
			if repl != c.wantRepl {
				t.Errorf("completeCommandLine(%q, nav=%v) replacement = %q, want %q", c.line, c.nav, repl, c.wantRepl)
			}
			if !reflect.DeepEqual(cands, c.wantCands) {
				t.Errorf("completeCommandLine(%q, nav=%v) candidates = %v, want %v", c.line, c.nav, cands, c.wantCands)
			}
		})
	}
}

func TestLongestCommonPrefix(t *testing.T) {
	cases := []struct {
		in   []string
		want string
	}{
		{[]string{"next", "prev"}, ""},
		{[]string{"case", "contest"}, "c"},
		{[]string{"case", "cheat", "contest"}, "c"},
		{[]string{"nodebug", "noverify"}, "no"},
		{[]string{"verify"}, "verify"},
		{nil, ""},
	}
	for _, c := range cases {
		if got := longestCommonPrefix(c.in); got != c.want {
			t.Errorf("longestCommonPrefix(%v) = %q, want %q", c.in, got, c.want)
		}
	}
}
