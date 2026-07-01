package stats

import (
	"testing"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/solvestat"
)

func sc(k, tr, c, i, v int) solvestat.Score {
	return solvestat.Score{Knowledge: k, Translation: tr, Complexity: c, Impl: i, Verify: v}
}

func statSolve(day int, ac, editorial bool, durMs, targetMs int64, score solvestat.Score) Solve {
	st := solvestat.Empty()
	st.AC = solvestat.BoolPtr(ac)
	st.Editorial = solvestat.BoolPtr(editorial)
	st.DurationMs = durMs
	st.TargetMs = targetMs
	st.Score = score
	return Solve{
		Date:     time.Date(2026, 6, day, 0, 0, 0, 0, time.Local),
		File:     "abc457_d.py",
		Category: "abc",
		Contest:  "abc457",
		Letter:   "d",
		HasStat:  true,
		Stat:     st,
	}
}

func TestComputeRecord(t *testing.T) {
	solves := []Solve{
		statSolve(1, true, false, 10*60000, 35*60000, sc(2, 3, 2, 3, 1)),                                                     // AC, self, hit
		statSolve(2, true, true, 40*60000, 35*60000, sc(1, 1, 1, 1, 1)),                                                      // AC, not self, miss
		statSolve(3, false, false, 20*60000, 0, sc(0, 0, 0, 0, 0)),                                                           // WA
		{Date: time.Date(2026, 6, 4, 0, 0, 0, 0, time.Local), File: "x.py", Category: "abc", Contest: "abc457", Letter: "e"}, // 記録なし
	}
	rep := Compute(solves, Options{Now: time.Date(2026, 6, 5, 0, 0, 0, 0, time.Local)})
	rec := rep.Record
	if rec == nil {
		t.Fatal("Record should be non-nil")
	}
	if rec.Total != 4 || rec.WithStats != 3 {
		t.Fatalf("total/withstats mismatch: %d %d", rec.Total, rec.WithStats)
	}
	if rec.ACNum != 2 || rec.ACDen != 3 {
		t.Fatalf("ac mismatch: %d/%d", rec.ACNum, rec.ACDen)
	}
	if rec.SelfNum != 1 || rec.SelfDen != 3 {
		t.Fatalf("self mismatch: %d/%d", rec.SelfNum, rec.SelfDen)
	}
	if rec.EdNum != 1 || rec.EdDen != 3 {
		t.Fatalf("editorial mismatch: %d/%d", rec.EdNum, rec.EdDen)
	}
	// duration: 3 件 (10m,40m,20m) → median 20m, min 10m, max 40m
	if rec.DurN != 3 || rec.MedianMs != 20*60000 || rec.MinMs != 10*60000 || rec.MaxMs != 40*60000 {
		t.Fatalf("duration agg mismatch: n=%d median=%d min=%d max=%d", rec.DurN, rec.MedianMs, rec.MinMs, rec.MaxMs)
	}
	// target: 2 件が目標付き (35m)。10m<=35m hit, 40m>35m miss → 1/2
	if rec.TargetNum != 1 || rec.TgtDen != 2 {
		t.Fatalf("target mismatch: %d/%d", rec.TargetNum, rec.TgtDen)
	}
	// score knowledge: (2+1+0)/3 = 1.0
	if rec.ScoreN[0] != 3 || rec.ScoreAvg[0] != 1.0 {
		t.Fatalf("score[knowledge] mismatch: n=%d avg=%f", rec.ScoreN[0], rec.ScoreAvg[0])
	}
}

func TestComputeRecordNilWhenNoStats(t *testing.T) {
	solves := []Solve{
		{Date: time.Date(2026, 6, 1, 0, 0, 0, 0, time.Local), File: "a.py", Category: "abc", Contest: "abc1", Letter: "a"},
	}
	rep := Compute(solves, Options{Now: time.Date(2026, 6, 2, 0, 0, 0, 0, time.Local)})
	if rep.Record != nil {
		t.Fatalf("Record should be nil when no solve-stat, got %+v", rep.Record)
	}
}

func TestComputeRecordScoreUnsetAxisExcluded(t *testing.T) {
	// knowledge のみ未記録 (-1) の solve は knowledge 平均から除外される。
	s := statSolve(1, true, false, 10*60000, 0, sc(-1, 2, 2, 2, 2))
	rep := Compute([]Solve{s}, Options{Now: time.Date(2026, 6, 2, 0, 0, 0, 0, time.Local)})
	if rep.Record.ScoreN[0] != 0 {
		t.Fatalf("unset knowledge should be excluded, n=%d", rep.Record.ScoreN[0])
	}
	if rep.Record.ScoreN[1] != 1 || rep.Record.ScoreAvg[1] != 2.0 {
		t.Fatalf("translation should be 2.0 n=1, got n=%d avg=%f", rep.Record.ScoreN[1], rep.Record.ScoreAvg[1])
	}
}
