package review

import (
	"bytes"
	"strings"
	"testing"
	"time"

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

func ids(items []MissedItem) []string {
	out := make([]string, len(items))
	for i, it := range items {
		out[i] = it.ID
	}
	return out
}
