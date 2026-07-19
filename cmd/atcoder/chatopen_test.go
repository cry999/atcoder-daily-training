package main

import (
	"testing"

	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

func TestChatProblemURLDefault(t *testing.T) {
	t.Setenv("XDG_CACHE_HOME", t.TempDir())
	got := chatProblemURL("abc457", "abc457_d")
	want := "https://atcoder.jp/contests/abc457/tasks/abc457_d"
	if got != want {
		t.Fatalf("chatProblemURL default = %q, want %q", got, want)
	}
}

func TestChatProblemURLPrefersMetaURL(t *testing.T) {
	t.Setenv("XDG_CACHE_HOME", t.TempDir())
	const contest, task = "abc111", "abc111_d"
	const url = "https://atcoder.jp/contests/abc111/tasks/arc103_b"
	if err := testexec.SaveMeta(contest, task, &testexec.Meta{Contest: contest, Task: task, URL: url, TimeLimitMs: 2000}); err != nil {
		t.Fatal(err)
	}
	if got := chatProblemURL(contest, task); got != url {
		t.Fatalf("chatProblemURL override = %q, want %q", got, url)
	}
}
