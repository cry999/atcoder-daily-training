package atcoder

import "testing"

func TestNormalizeCookie(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want string
	}{
		{"値だけ", "abc123def", "REVEL_SESSION=abc123def"},
		{"name=value 形", "REVEL_SESSION=abc123def", "REVEL_SESSION=abc123def"},
		{"属性付きをそのまま貼った", "REVEL_SESSION=abc123def; Path=/; HttpOnly", "REVEL_SESSION=abc123def"},
		{"前後空白", "  abc123def  ", "REVEL_SESSION=abc123def"},
		{"引用符付き", `"abc123def"`, "REVEL_SESSION=abc123def"},
		{"他 cookie に紛れていても抽出", "foo=bar; REVEL_SESSION=abc; baz=qux", "REVEL_SESSION=abc"},
		{"空", "", ""},
		{"空白のみ", "   ", ""},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := normalizeCookie(c.in); got != c.want {
				t.Fatalf("normalizeCookie(%q) = %q, want %q", c.in, got, c.want)
			}
		})
	}
}
