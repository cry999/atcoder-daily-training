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

func TestEffectiveScreenName(t *testing.T) {
	cases := []struct {
		name, task, urlOverride, want string
	}{
		// override 無し: task をそのまま screen name に使う。
		{"no override", "abc258_d", "", "abc258_d"},
		// task URL override: その task_id が screen name (例: abc107 の D = arc101_b)。
		{"override differs", "abc107_d", "https://atcoder.jp/contests/arc101/tasks/arc101_b", "arc101_b"},
		// クエリ付き URL でも task_id を取り出せる。
		{"override with query", "abc107_d", "https://atcoder.jp/contests/arc101/tasks/arc101_b?lang=ja", "arc101_b"},
		// task URL として解釈できない override は無視して task を使う。
		{"override unparsable", "abc258_d", "not-a-url", "abc258_d"},
	}
	for _, c := range cases {
		if got := effectiveScreenName(c.task, c.urlOverride); got != c.want {
			t.Fatalf("%s: effectiveScreenName(%q,%q) = %q, want %q", c.name, c.task, c.urlOverride, got, c.want)
		}
	}
}
