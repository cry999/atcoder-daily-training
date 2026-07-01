package main

import "testing"

// TestNormalizeCookie は貼り付けられた cookie の正規化 (空白除去・REVEL_SESSION= 接頭辞
// 剥がし) を固定する。
func TestNormalizeCookie(t *testing.T) {
	cases := []struct{ in, want string }{
		{"abc123", "abc123"},
		{"  abc123\n", "abc123"},
		{"REVEL_SESSION=abc123", "abc123"},
		{"  REVEL_SESSION=abc123  \n", "abc123"},
		{"", ""},
		{"   \n", ""},
	}
	for _, c := range cases {
		if got := normalizeCookie(c.in); got != c.want {
			t.Fatalf("normalizeCookie(%q) = %q, want %q", c.in, got, c.want)
		}
	}
}
