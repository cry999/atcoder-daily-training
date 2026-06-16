package main

import (
	"strings"
	"testing"
)

func TestPlanEdit(t *testing.T) {
	cases := []struct {
		name                          string
		nvimSock, override, env, path string
		wantRemote                    bool
		wantArgv                      string // "|" 区切り
	}{
		{"in nvim → remote (override/env は無視)", "/tmp/nvim.123.sock", "code -w", "vim", "a.py",
			true, "nvim|--server|/tmp/nvim.123.sock|--remote-tab|a.py"},
		{"outside nvim → config override が勝つ", "", "code -w", "vim", "a.py",
			false, "code|-w|a.py"},
		{"outside nvim → $EDITOR フォールバック", "", "", "vim -p", "a.py",
			false, "vim|-p|a.py"},
		{"outside nvim → 既定 nvim", "", "", "", "a.py",
			false, "nvim|a.py"},
		{"override が空白のみなら $EDITOR へ", "", "   ", "vi", "a.py",
			false, "vi|a.py"},
		{"全部空なら nvim", "", "", "", "x/y.py",
			false, "nvim|x/y.py"},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got := planEdit(c.nvimSock, c.override, c.env, c.path)
			if got.remote != c.wantRemote {
				t.Errorf("remote = %v, want %v", got.remote, c.wantRemote)
			}
			if joined := strings.Join(got.argv, "|"); joined != c.wantArgv {
				t.Errorf("argv = %q, want %q", joined, c.wantArgv)
			}
		})
	}
}
