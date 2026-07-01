package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// fakeLayout は buildSubmitSource のテスト用に固定パスを返す最小 Layout。
type fakeLayout struct{ path string }

func (fakeLayout) Name() string                                          { return "fake" }
func (l fakeLayout) SolutionPath(contestID, task string) (string, error) { return l.path, nil }

// TestBuildSubmitSourceStripsSolveStat は提出される中身 (Body) から solve-stat ブロックが
// 除去され、DEBUG コメントアウトと両立することを固定する (要件 063)。解答ファイル本体は不変。
func TestBuildSubmitSourceStripsSolveStat(t *testing.T) {
	src := `# >>> atcoder-stat >>>
# started_at  = 2026-07-01T16:00:00+09:00
# duration_ms = 1500000
# ac          = true
# <<< atcoder-stat <<<
n = int(input())
print(f"[DEBUG] n={n}")
print(n * 2)
`
	dir := t.TempDir()
	path := filepath.Join(dir, "abc457_d.py")
	if err := os.WriteFile(path, []byte(src), 0o644); err != nil {
		t.Fatal(err)
	}
	lay := fakeLayout{path: path}

	// keepDebug=false: solve-stat 除去 + DEBUG コメントアウト。
	got, err := buildSubmitSource("abc457", "d", lay, false)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(got.Body, "atcoder-stat") || strings.Contains(got.Body, "duration_ms") {
		t.Fatalf("solve-stat block must be stripped from Body, got:\n%s", got.Body)
	}
	if !strings.Contains(got.Body, "# print(f\"[DEBUG] n={n}\")") {
		t.Fatalf("DEBUG print should be commented out, got:\n%s", got.Body)
	}
	if got.DebugCommented != 1 {
		t.Fatalf("DebugCommented = %d, want 1", got.DebugCommented)
	}

	// keepDebug=true: solve-stat は除去、DEBUG は温存。
	kept, err := buildSubmitSource("abc457", "d", lay, true)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(kept.Body, "atcoder-stat") {
		t.Fatalf("solve-stat must be stripped even with keepDebug, got:\n%s", kept.Body)
	}
	if !strings.Contains(kept.Body, "print(f\"[DEBUG] n={n}\")") || strings.Contains(kept.Body, "# print(f\"[DEBUG]") {
		t.Fatalf("DEBUG print should be kept verbatim with keepDebug, got:\n%s", kept.Body)
	}

	// 解答ファイル本体は不変 (読み取りのみ)。
	after, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if string(after) != src {
		t.Fatalf("solution file must be untouched\nwant:\n%s\ngot:\n%s", src, after)
	}
}

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
