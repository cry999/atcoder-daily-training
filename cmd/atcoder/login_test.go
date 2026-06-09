package main

import "testing"

func TestSanitizeSecret(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want string
	}{
		{"普通の記号入りはそのまま", `p@ss%w0rd$!`, `p@ss%w0rd$!`},
		{"前後の空白は除去", "  abc123==  ", `abc123==`},
		{"内側のスペースは保持", `a b c`, `a b c`},
		{"ブラケットペーストのラッパを除去", "\x1b[200~tok%en==\x1b[201~", `tok%en==`},
		{"先頭だけのブラケット開始も除去", "\x1b[200~secret", "secret"},
		{"NUL など C0 制御は除去", "ab\x00cd\x01", "abcd"},
		{"DEL も除去", "ab\x7fcd", "abcd"},
		{"日本語など印字可能 multibyte は保持", "パス㊙word", "パス㊙word"},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := sanitizeSecret(c.in); got != c.want {
				t.Fatalf("sanitizeSecret(%q) = %q, want %q", c.in, got, c.want)
			}
		})
	}
}
