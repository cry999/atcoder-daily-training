package reviewrule

import (
	"testing"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/solvestat"
)

func statWith(ac, ed *bool) solvestat.Stat {
	st := solvestat.Empty()
	st.AC = ac
	st.Editorial = ed
	return st
}

func TestParseDefaultRule(t *testing.T) {
	r, err := Parse("", nil)
	if err != nil {
		t.Fatal(err)
	}
	if r.Mode != ModeAny || len(r.Conditions) != 2 {
		t.Fatalf("default rule = %+v, want any + 2 conditions", r)
	}
	if !r.Match(statWith(solvestat.BoolPtr(false), solvestat.BoolPtr(false))) {
		t.Fatal("default rule should match ac=false")
	}
	if !r.Match(statWith(solvestat.BoolPtr(true), solvestat.BoolPtr(true))) {
		t.Fatal("default rule should match editorial=true")
	}
	if r.Match(statWith(solvestat.BoolPtr(true), solvestat.BoolPtr(false))) {
		t.Fatal("default rule should not match self AC")
	}
}

func TestParseModeAll(t *testing.T) {
	r, err := Parse("all", []string{"ac=false", "editorial=true"})
	if err != nil {
		t.Fatal(err)
	}
	if r.Match(statWith(solvestat.BoolPtr(false), solvestat.BoolPtr(false))) {
		t.Fatal("all rule should not match only ac=false")
	}
	if !r.Match(statWith(solvestat.BoolPtr(false), solvestat.BoolPtr(true))) {
		t.Fatal("all rule should match both conditions")
	}
}

func TestScoreConditions(t *testing.T) {
	st := solvestat.Empty()
	st.Score.Impl = 1
	r, err := Parse("any", []string{"score.impl<=1"})
	if err != nil {
		t.Fatal(err)
	}
	if !r.Match(st) {
		t.Fatal("score.impl<=1 should match impl=1")
	}
	st.Score.Impl = -1
	if r.Match(st) {
		t.Fatal("unset score should not match")
	}
}

func TestDurationConditions(t *testing.T) {
	st := solvestat.Empty()
	st.DurationMs = int64((45 * time.Minute).Milliseconds())
	st.TargetMs = int64((30 * time.Minute).Milliseconds())
	r, err := Parse("any", []string{"duration>target"})
	if err != nil {
		t.Fatal(err)
	}
	if !r.Match(st) {
		t.Fatal("duration>target should match 45m > 30m")
	}
	r, err = Parse("any", []string{"duration>=45m"})
	if err != nil {
		t.Fatal(err)
	}
	if !r.Match(st) {
		t.Fatal("duration>=45m should match")
	}
	st.TargetMs = 0
	r, _ = Parse("any", []string{"duration>target"})
	if r.Match(st) {
		t.Fatal("missing target should not match")
	}
}

func TestInvalidConditions(t *testing.T) {
	cases := [][]string{
		{"ac<=true"},
		{"score.bad<=1"},
		{"score.impl<=4"},
		{"duration>soon"},
		{"difficulty>=800"},
	}
	for _, conds := range cases {
		if _, err := Parse("any", conds); err == nil {
			t.Fatalf("Parse(%v) should fail", conds)
		}
	}
	if _, err := Parse("some", []string{"ac=false"}); err == nil {
		t.Fatal("invalid mode should fail")
	}
}

func TestParseListAndFormatList(t *testing.T) {
	got := ParseList("ac=false, editorial=true,, score.impl<=1")
	want := []string{"ac=false", "editorial=true", "score.impl<=1"}
	if len(got) != len(want) {
		t.Fatalf("ParseList = %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("ParseList = %v, want %v", got, want)
		}
	}
	if s := FormatList(got); s != "ac=false,editorial=true,score.impl<=1" {
		t.Fatalf("FormatList = %q", s)
	}
}
