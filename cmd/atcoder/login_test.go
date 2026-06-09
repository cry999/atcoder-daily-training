package main

import "testing"

func TestSanitizePassword(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want string
	}{
		{"普通の記号入りはそのまま", `p@ss%w0rd$!`, `p@ss%w0rd$!`},
		{"内側のスペースは保持", `a b c`, `a b c`},
		{"ブラケットペーストのラッパを除去", "\x1b[200~p@ss%w0rd$!\x1b[201~", `p@ss%w0rd$!`},
		{"先頭だけのブラケット開始も除去", "\x1b[200~secret", "secret"},
		{"NUL など C0 制御は除去", "ab\x00cd\x01", "abcd"},
		{"DEL も除去", "ab\x7fcd", "abcd"},
		{"TAB は保持", "a\tb", "a\tb"},
		{"日本語など印字可能 multibyte は保持", "パス㊙word", "パス㊙word"},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := sanitizePassword(c.in); got != c.want {
				t.Fatalf("sanitizePassword(%q) = %q, want %q", c.in, got, c.want)
			}
		})
	}
}
