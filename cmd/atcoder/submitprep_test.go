package main

import "testing"

func TestSubmitURLFor(t *testing.T) {
	cases := []struct {
		contest, task, want string
	}{
		{"abc258", "abc258_d", "https://atcoder.jp/contests/abc258/submit?taskScreenName=abc258_d"},
		{"arc180", "arc180_c", "https://atcoder.jp/contests/arc180/submit?taskScreenName=arc180_c"},
	}
	for _, c := range cases {
		if got := submitURLFor(c.contest, c.task); got != c.want {
			t.Fatalf("submitURLFor(%q,%q) = %q, want %q", c.contest, c.task, got, c.want)
		}
	}
}
