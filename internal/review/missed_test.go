package review

import (
	"bytes"
	"strings"
	"testing"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/reviewrule"
	"github.com/cry999/atcoder-daily-training/internal/solvestat"
	"github.com/cry999/atcoder-daily-training/internal/stats"
)

func missedSolve(date time.Time, file string, ac, editorial *bool) stats.Solve {
	st := solvestat.Empty()
	st.AC = ac
	st.Editorial = editorial
	return stats.Solve{
		Date:     date,
		File:     file,
		Path:     "exercise/2026/07/22/" + file,
		Category: "abc",
		Contest:  strings.TrimSuffix(file, "_d.py"),
		Letter:   strings.TrimSuffix(strings.TrimPrefix(file, "abc999_"), ".py"),
		HasStat:  true,
		Stat:     st,
	}
}

func TestBuildMissedIncludesACFalseAndEditorialTrue(t *testing.T) {
	target := d(2026, 7, 22)
	truep, falsep := solvestat.BoolPtr(true), solvestat.BoolPtr(false)
	solves := []stats.Solve{
		missedSolve(target, "abc100_d.py", falsep, falsep),                // ac=false
		missedSolve(target, "abc101_d.py", truep, truep),                  // editorial=true
		missedSolve(target, "abc102_d.py", truep, falsep),                 // 自力AC
		missedSolve(target.AddDate(0, 0, -1), "abc103_d.py", falsep, nil), // 対象日外
	}
	rep := BuildMissed(solves, target)
	got := ids(rep.Items)
	want := []string{"abc100_d", "abc101_d"}
	if strings.Join(got, ",") != strings.Join(want, ",") {
		t.Fatalf("missed ids = %v, want %v", got, want)
	}
}

func TestBuildMissedWithRuleUsesConfiguredConditions(t *testing.T) {
	target := d(2026, 7, 22)
	truep := solvestat.BoolPtr(true)
	selfAC := missedSolve(target, "abc102_d.py", truep, solvestat.BoolPtr(false))
	selfAC.Stat.Score.Impl = 1
	highImpl := missedSolve(target, "abc103_d.py", truep, solvestat.BoolPtr(false))
	highImpl.Stat.Score.Impl = 3
	rule, err := reviewrule.Parse("any", []string{"score.impl<=1"})
	if err != nil {
		t.Fatal(err)
	}
	rep := BuildMissedWithRule([]stats.Solve{selfAC, highImpl}, target, rule)
	got := ids(rep.Items)
	want := []string{"abc102_d"}
	if strings.Join(got, ",") != strings.Join(want, ",") {
		t.Fatalf("configured missed ids = %v, want %v", got, want)
	}
}

func TestBuildMissedInRangeIncludesBoundariesAndSortsByDateThenID(t *testing.T) {
	start, end := d(2026, 7, 20), d(2026, 7, 22)
	falsep := solvestat.BoolPtr(false)
	solves := []stats.Solve{
		missedSolve(end, "abc102_d.py", falsep, nil),
		missedSolve(start, "abc100_d.py", falsep, nil),
		missedSolve(start, "abc099_d.py", falsep, nil),
		missedSolve(end.AddDate(0, 0, 1), "abc103_d.py", falsep, nil),
	}
	rep := BuildMissedInRangeWithRule(solves, start, end, mustDefaultRule(t))
	got := ids(rep.Items)
	want := []string{"abc099_d", "abc100_d", "abc102_d"}
	if strings.Join(got, ",") != strings.Join(want, ",") {
		t.Fatalf("range missed ids = %v, want %v", got, want)
	}
	if !rep.Start.Equal(start) || !rep.End.Equal(end) {
		t.Fatalf("range = %s through %s, want %s through %s", rep.Start, rep.End, start, end)
	}
}

func TestFindMissedReportsAmbiguousIDAcrossRange(t *testing.T) {
	start, end := d(2026, 7, 20), d(2026, 7, 21)
	falsep := solvestat.BoolPtr(false)
	rep := BuildMissedInRangeWithRule([]stats.Solve{
		missedSolve(start, "abc100_d.py", falsep, nil),
		missedSolve(end, "abc100_d.py", falsep, nil),
	}, start, end, mustDefaultRule(t))
	if _, err := rep.FindMissed("abc100_d"); err == nil || !strings.Contains(err.Error(), "ambiguous") {
		t.Fatalf("FindMissed range error = %v, want ambiguous", err)
	}
}

func TestBuildMissedCarriesReviewedAt(t *testing.T) {
	target := d(2026, 7, 22)
	st := solvestat.Empty()
	st.AC = solvestat.BoolPtr(false)
	st.ReviewedAt = time.Date(2026, 7, 23, 7, 30, 0, 0, time.Local)
	rep := BuildMissed([]stats.Solve{{
		Date: target, File: "abc100_d.py", Path: "exercise/2026/07/22/abc100_d.py",
		Category: "abc", Contest: "abc100", Letter: "d", HasStat: true, Stat: st,
	}}, target)
	if len(rep.Items) != 1 || rep.Items[0].Reviewed.IsZero() {
		t.Fatalf("ReviewedAt not carried: %+v", rep.Items)
	}
}

func TestFindMissedAcceptsStemAndContestSlashLetter(t *testing.T) {
	target := d(2026, 7, 22)
	falsep := solvestat.BoolPtr(false)
	rep := BuildMissed([]stats.Solve{{
		Date: target, File: "abc357_d.py", Path: "exercise/2026/07/22/abc357_d.py",
		Category: "abc", Contest: "abc357", Letter: "d", HasStat: true,
		Stat: solvestat.Stat{AC: falsep, Score: solvestat.Empty().Score},
	}}, target)
	for _, id := range []string{"abc357_d", "abc357/d", "abc357_d.py"} {
		it, err := rep.FindMissed(id)
		if err != nil {
			t.Fatalf("FindMissed(%q): %v", id, err)
		}
		if it.Path == "" || it.ID != "abc357_d" {
			t.Fatalf("FindMissed(%q) = %+v", id, it)
		}
	}
}

func TestRenderMissedShowsCheckState(t *testing.T) {
	target := d(2026, 7, 22)
	falsep := solvestat.BoolPtr(false)
	st := solvestat.Empty()
	st.AC = falsep
	st.ReviewedAt = time.Date(2026, 7, 23, 7, 30, 0, 0, time.Local)
	rep := BuildMissed([]stats.Solve{{
		Date: target, File: "abc100_d.py", Path: "exercise/2026/07/22/abc100_d.py",
		Category: "abc", Contest: "abc100", Letter: "d", HasStat: true, Stat: st,
	}}, target)
	var buf bytes.Buffer
	if err := RenderMissed(&buf, rep); err != nil {
		t.Fatal(err)
	}
	out := buf.String()
	if !strings.Contains(out, "[x] abc100_d") || !strings.Contains(out, "1 missed, 1 reviewed") {
		t.Fatalf("unexpected output:\n%s", out)
	}
}

func TestRenderMissedRangeShowsDates(t *testing.T) {
	start, end := d(2026, 7, 20), d(2026, 7, 21)
	falsep := solvestat.BoolPtr(false)
	rep := BuildMissedInRangeWithRule([]stats.Solve{
		missedSolve(start, "abc100_d.py", falsep, nil),
		missedSolve(end, "abc101_d.py", falsep, nil),
	}, start, end, mustDefaultRule(t))
	var buf bytes.Buffer
	if err := RenderMissed(&buf, rep); err != nil {
		t.Fatal(err)
	}
	out := buf.String()
	if !strings.Contains(out, "2026-07-20 through 2026-07-21") || !strings.Contains(out, "2026-07-20  abc100_d") {
		t.Fatalf("unexpected range output:\n%s", out)
	}
}

func mustDefaultRule(t *testing.T) reviewrule.Rule {
	t.Helper()
	rule, err := reviewrule.Parse("", nil)
	if err != nil {
		t.Fatal(err)
	}
	return rule
}

func ids(items []MissedItem) []string {
	out := make([]string, len(items))
	for i, it := range items {
		out[i] = it.ID
	}
	return out
}
