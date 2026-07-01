package solvestat

import (
	"strings"
	"testing"
	"time"
)

func mustParse(t *testing.T, src string) (Stat, bool) {
	t.Helper()
	st, found, err := Parse([]byte(src))
	if err != nil {
		t.Fatalf("Parse error: %v", err)
	}
	return st, found
}

func TestParseNoBlock(t *testing.T) {
	src := "L, R = map(int, input().split())\nprint(L + R)\n"
	st, found := mustParse(t, src)
	if found {
		t.Fatalf("expected no block, got found=true")
	}
	if st.Score.Knowledge != -1 {
		t.Fatalf("empty stat should have Score -1, got %d", st.Score.Knowledge)
	}
}

func TestParseFull(t *testing.T) {
	src := `# >>> atcoder-stat >>>
# started_at  = 2026-07-01T16:00:00+09:00
# solved_at   = 2026-07-01T16:25:00+09:00
# duration_ms = 1500000
# target_ms   = 2100000
# ac          = true
# editorial   = false
# knowledge   = 2
# translation = 3
# complexity  = 0
# impl        = 3
# verify      = 1
# <<< atcoder-stat <<<
print("hi")
`
	st, found := mustParse(t, src)
	if !found {
		t.Fatal("expected block found")
	}
	if st.DurationMs != 1500000 || st.TargetMs != 2100000 {
		t.Fatalf("duration/target mismatch: %d %d", st.DurationMs, st.TargetMs)
	}
	if st.AC == nil || !*st.AC {
		t.Fatalf("ac should be true")
	}
	if st.Editorial == nil || *st.Editorial {
		t.Fatalf("editorial should be false")
	}
	if st.Score.Complexity != 0 {
		t.Fatalf("complexity 0 must survive (not treated as unset), got %d", st.Score.Complexity)
	}
	if st.Score.Knowledge != 2 || st.Score.Verify != 1 {
		t.Fatalf("score mismatch: %+v", st.Score)
	}
	if st.StartedAt.IsZero() || st.SolvedAt.IsZero() {
		t.Fatalf("times should be parsed")
	}
}

func TestMergeInsertAtTop(t *testing.T) {
	code := "a, b = map(int, input().split())\nprint(a + b)\n"
	started := time.Date(2026, 7, 1, 16, 0, 0, 0, time.FixedZone("JST", 9*3600))
	patch := Empty()
	patch.StartedAt = started

	out, err := Merge([]byte(code), patch)
	if err != nil {
		t.Fatal(err)
	}
	s := string(out)
	if !strings.HasPrefix(s, startMarker) {
		t.Fatalf("block should be at top, got:\n%s", s)
	}
	if !strings.HasSuffix(s, code) {
		t.Fatalf("original code should be preserved at end, got:\n%s", s)
	}
	if strings.Contains(s, "solved_at") || strings.Contains(s, "knowledge") {
		t.Fatalf("only started_at should render, got:\n%s", s)
	}
	// Round-trip.
	st, found := mustParse(t, s)
	if !found || !st.StartedAt.Equal(started) {
		t.Fatalf("round-trip failed: %+v", st)
	}
}

func TestMergePartialUpdate(t *testing.T) {
	base := `# >>> atcoder-stat >>>
# started_at  = 2026-07-01T16:00:00+09:00
# <<< atcoder-stat <<<
print(1)
`
	// stop: add solved_at + duration, preserve started_at.
	patch := Empty()
	patch.SolvedAt = time.Date(2026, 7, 1, 16, 25, 0, 0, time.FixedZone("JST", 9*3600))
	patch.DurationMs = 1500000
	patch.AC = BoolPtr(true)

	out, err := Merge([]byte(base), patch)
	if err != nil {
		t.Fatal(err)
	}
	st, found := mustParse(t, string(out))
	if !found {
		t.Fatal("block lost")
	}
	if st.StartedAt.IsZero() {
		t.Fatal("started_at must be preserved on partial update")
	}
	if st.SolvedAt.IsZero() || st.DurationMs != 1500000 {
		t.Fatal("solved_at/duration must be set")
	}
	if st.AC == nil || !*st.AC {
		t.Fatal("ac must be set")
	}
	if !strings.HasSuffix(string(out), "print(1)\n") {
		t.Fatalf("code must be preserved, got:\n%s", out)
	}
}

func TestMergeScoreZeroPreserved(t *testing.T) {
	base := `# >>> atcoder-stat >>>
# knowledge   = 0
# <<< atcoder-stat <<<
`
	// Patch only sets impl; knowledge=0 must survive re-render.
	patch := Empty()
	patch.Score.Impl = 2
	out, err := Merge([]byte(base), patch)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(out), "knowledge   = 0") {
		t.Fatalf("knowledge=0 should be preserved, got:\n%s", out)
	}
	if !strings.Contains(string(out), "impl        = 2") {
		t.Fatalf("impl=2 should be added, got:\n%s", out)
	}
}

func TestParseWhitespaceVariance(t *testing.T) {
	// Irregular spacing around '=' and after '#'.
	src := "# >>> atcoder-stat >>>\n#ac=true\n#   knowledge=3\n# <<< atcoder-stat <<<\n"
	st, found := mustParse(t, src)
	if !found {
		t.Fatal("block should be found")
	}
	if st.AC == nil || !*st.AC {
		t.Fatal("ac should parse despite tight spacing")
	}
	if st.Score.Knowledge != 3 {
		t.Fatalf("knowledge should be 3, got %d", st.Score.Knowledge)
	}
}

func TestParseUnknownKeySkipped(t *testing.T) {
	src := "# >>> atcoder-stat >>>\n# future_key = 42\n# ac         = false\n# <<< atcoder-stat <<<\n"
	st, found := mustParse(t, src)
	if !found {
		t.Fatal("block should be found")
	}
	if st.AC == nil || *st.AC {
		t.Fatal("ac should be false; unknown key must not break parse")
	}
}

func TestParseCorruptedMarkers(t *testing.T) {
	cases := []string{
		"# >>> atcoder-stat >>>\n# ac = true\n",                                    // no end
		"# ac = true\n# <<< atcoder-stat <<<\n",                                    // no start
		"# >>> atcoder-stat >>>\n# >>> atcoder-stat >>>\n# <<< atcoder-stat <<<\n", // duplicate start
		"# <<< atcoder-stat <<<\n# >>> atcoder-stat >>>\n",                         // end before start
	}
	for i, src := range cases {
		if _, _, err := Parse([]byte(src)); err == nil {
			t.Fatalf("case %d: expected corruption error, got nil", i)
		}
	}
}

func TestParseBadValueErrors(t *testing.T) {
	src := "# >>> atcoder-stat >>>\n# duration_ms = not-a-number\n# <<< atcoder-stat <<<\n"
	if _, _, err := Parse([]byte(src)); err == nil {
		t.Fatal("expected error for bad duration_ms")
	}
}

func TestMergeCorruptedRefused(t *testing.T) {
	base := "# >>> atcoder-stat >>>\n# ac = true\n" // missing end marker
	patch := Empty()
	patch.Editorial = BoolPtr(true)
	if _, err := Merge([]byte(base), patch); err == nil {
		t.Fatal("Merge should refuse to write over a corrupted block")
	}
}
