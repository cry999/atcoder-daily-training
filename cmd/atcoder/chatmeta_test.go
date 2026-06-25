package main

import (
	"strings"
	"testing"

	"github.com/cry999/atcoder-daily-training/internal/testexec"
)

const metaTestContest, metaTestTask = "fixture", "meta"

// seedMeta は一時 XDG_CACHE_HOME に meta.toml を用意する。
func seedMeta(t *testing.T, m *testexec.Meta) {
	t.Helper()
	t.Setenv("XDG_CACHE_HOME", t.TempDir())
	if err := testexec.SaveMeta(metaTestContest, metaTestTask, m); err != nil {
		t.Fatal(err)
	}
}

// MetaShow は CLI meta show と同じラベルで url / time limit / samples を返す。
func TestChatMetaShowFunc(t *testing.T) {
	seedMeta(t, &testexec.Meta{Contest: metaTestContest, Task: metaTestTask, URL: "https://x", TimeLimitMs: 2000})
	show := chatMetaShowFunc(metaTestContest, metaTestTask)

	lines, err := show("")
	if err != nil {
		t.Fatal(err)
	}
	if len(lines) != 3 || !strings.Contains(lines[0], "https://x") || !strings.Contains(lines[1], "2000 ms") {
		t.Fatalf("lines=%v", lines)
	}

	urlOnly, _ := show("url")
	if len(urlOnly) != 1 || !strings.Contains(urlOnly[0], "https://x") {
		t.Fatalf("url-only lines=%v", urlOnly)
	}
}

// 未キャッシュの MetaShow は error を返す (chat は err 行で吸収する)。
func TestChatMetaShowFunc_Uncached(t *testing.T) {
	t.Setenv("XDG_CACHE_HOME", t.TempDir())
	show := chatMetaShowFunc("nope", "nope")
	if _, err := show(""); err == nil {
		t.Fatal("want error for uncached meta")
	}
}

// MetaSet url は override を書き込み、結果行と (変えない) time_limit を返す。
func TestChatMetaSetFunc_URL(t *testing.T) {
	seedMeta(t, &testexec.Meta{Contest: metaTestContest, Task: metaTestTask, TimeLimitMs: 2000})
	set := chatMetaSetFunc(metaTestContest, metaTestTask)

	const url = "https://atcoder.jp/contests/abc111/tasks/arc103_b"
	lines, tl, err := set("url", url)
	if err != nil {
		t.Fatal(err)
	}
	if tl != 2000 {
		t.Fatalf("time_limit changed to %d on url edit, want 2000", tl)
	}
	if len(lines) != 1 || !strings.Contains(lines[0], "(none) -> "+url) {
		t.Fatalf("lines=%v", lines)
	}
	if m, _ := testexec.LoadMeta(metaTestContest, metaTestTask); m.URL != url {
		t.Fatalf("persisted url=%q, want %q", m.URL, url)
	}
}

// url override はスロット未キャッシュでも記録できる (空 meta を作る)。
func TestChatMetaSetFunc_URLUncached(t *testing.T) {
	t.Setenv("XDG_CACHE_HOME", t.TempDir())
	set := chatMetaSetFunc(metaTestContest, metaTestTask)
	if _, _, err := set("url", "https://atcoder.jp/contests/abc1/tasks/abc1_a"); err != nil {
		t.Fatalf("url on uncached slot should succeed: %v", err)
	}
}

// AtCoder URL でない値は弾く (書き込まない)。
func TestChatMetaSetFunc_URLInvalid(t *testing.T) {
	seedMeta(t, &testexec.Meta{Contest: metaTestContest, Task: metaTestTask, TimeLimitMs: 2000})
	set := chatMetaSetFunc(metaTestContest, metaTestTask)
	if _, _, err := set("url", "not-a-url"); err == nil {
		t.Fatal("want error for non-AtCoder url")
	}
}

// MetaSet time_limit は duration を ms に変換して書き込み、新しい ms を返す。
func TestChatMetaSetFunc_TimeLimit(t *testing.T) {
	seedMeta(t, &testexec.Meta{Contest: metaTestContest, Task: metaTestTask, TimeLimitMs: 2000})
	set := chatMetaSetFunc(metaTestContest, metaTestTask)

	lines, tl, err := set("time_limit", "5s")
	if err != nil {
		t.Fatal(err)
	}
	if tl != 5000 {
		t.Fatalf("new time_limit=%d, want 5000", tl)
	}
	if len(lines) != 1 || !strings.Contains(lines[0], "2000 ms -> 5000 ms") {
		t.Fatalf("lines=%v", lines)
	}
	if m, _ := testexec.LoadMeta(metaTestContest, metaTestTask); m.TimeLimitMs != 5000 {
		t.Fatalf("persisted time_limit=%d, want 5000", m.TimeLimitMs)
	}
}

// 不正な duration / 非正の値は弾く。
func TestChatMetaSetFunc_TimeLimitInvalid(t *testing.T) {
	seedMeta(t, &testexec.Meta{Contest: metaTestContest, Task: metaTestTask, TimeLimitMs: 2000})
	set := chatMetaSetFunc(metaTestContest, metaTestTask)
	for _, v := range []string{"abc", "0", "-1s"} {
		if _, _, err := set("time_limit", v); err == nil {
			t.Fatalf("want error for time_limit %q", v)
		}
	}
}

// time_limit は未キャッシュでは error (url と違いキャッシュ前提)。
func TestChatMetaSetFunc_TimeLimitUncached(t *testing.T) {
	t.Setenv("XDG_CACHE_HOME", t.TempDir())
	set := chatMetaSetFunc("nope", "nope")
	if _, _, err := set("time_limit", "5s"); err == nil {
		t.Fatal("want error for time_limit on uncached slot")
	}
}
