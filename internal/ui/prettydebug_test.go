package ui

import "testing"

func TestPrettifyDebug(t *testing.T) {
	cases := []struct {
		name string
		in   string
		want string
	}{
		{"empty passes through", "", ""},
		{
			// valid JSON object → 2-space indent, [DEBUG] prefix kept on line 1 only.
			name: "object formatted",
			in:   `[DEBUG] {"n": 5}`,
			want: "[DEBUG] {\n  \"n\": 5\n}",
		},
		{
			// nested array likewise expands.
			name: "nested array formatted",
			in:   `[DEBUG] [[0,1],[2,3]]`,
			want: "[DEBUG] [\n  [\n    0,\n    1\n  ],\n  [\n    2,\n    3\n  ]\n]",
		},
		{
			// labelled payload ("dp = {...}") is NOT valid JSON as a whole → passthrough.
			name: "labelled line untouched",
			in:   `[DEBUG] dp = {"a": 1}`,
			want: `[DEBUG] dp = {"a": 1}`,
		},
		{
			// scalar payloads are out of scope (must start with { or [).
			name: "scalar untouched",
			in:   `[DEBUG] 42`,
			want: `[DEBUG] 42`,
		},
		{
			// broken JSON stays as-is (best effort, never errors).
			name: "invalid json untouched",
			in:   `[DEBUG] {"n": }`,
			want: `[DEBUG] {"n": }`,
		},
		{
			// a non-[DEBUG] line is left verbatim.
			name: "non-debug line untouched",
			in:   `plain line {"x":1}`,
			want: `plain line {"x":1}`,
		},
		{
			// mixed: only the valid-JSON line is reformatted; the other is passthrough.
			name: "mixed lines",
			in:   "[DEBUG] {\"n\":5}\n[DEBUG] dp = {...}",
			want: "[DEBUG] {\n  \"n\": 5\n}\n[DEBUG] dp = {...}",
		},
		{
			// key order and number literals are preserved (json.Indent, not Unmarshal+Marshal).
			name: "key order and number literal preserved",
			in:   `[DEBUG] {"z": 1e9, "a": 0.50}`,
			want: "[DEBUG] {\n  \"z\": 1e9,\n  \"a\": 0.50\n}",
		},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := prettifyDebug(c.in); got != c.want {
				t.Errorf("prettifyDebug(%q) =\n%q\nwant\n%q", c.in, got, c.want)
			}
		})
	}
}
