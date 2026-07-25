package mode

import (
	"errors"
	"testing"
	"time"
)

func TestTaskID(t *testing.T) {
	cases := []struct {
		contest, task, want string
	}{
		{"abc457", "d", "abc457_d"},
		{"abc457", "abc457_d", "abc457_d"},
		{"adt_2026_06_15_2000", "g", "adt_2026_06_15_2000_g"},
	}
	for _, c := range cases {
		if got := TaskID(c.contest, c.task); got != c.want {
			t.Errorf("TaskID(%q, %q) = %q, want %q", c.contest, c.task, got, c.want)
		}
	}
}

func TestParseTaskURL(t *testing.T) {
	cases := []struct {
		in          string
		wantContest string
		wantTask    string
		wantOK      bool
	}{
		{"https://atcoder.jp/contests/abc457/tasks/abc457_d", "abc457", "abc457_d", true},
		{"http://atcoder.jp/contests/abc457/tasks/abc457_d", "abc457", "abc457_d", true},
		{"atcoder.jp/contests/abc457/tasks/abc457_d", "abc457", "abc457_d", true},
		{"https://atcoder.jp/contests/abc457/tasks/abc457_d?lang=ja", "abc457", "abc457_d", true},
		{"https://atcoder.jp/contests/abc457/tasks/abc457_d#sample", "abc457", "abc457_d", true},
		{"https://atcoder.jp/contests/typical90/tasks/typical90_a", "typical90", "typical90_a", true},
		{"https://atcoder.jp/contests/abc457", "", "", false},
		{"abc457", "", "", false},
		{"", "", "", false},
	}
	for _, c := range cases {
		gotC, gotT, gotOK := ParseTaskURL(c.in)
		if gotOK != c.wantOK || gotC != c.wantContest || gotT != c.wantTask {
			t.Errorf("ParseTaskURL(%q) = (%q, %q, %v), want (%q, %q, %v)",
				c.in, gotC, gotT, gotOK, c.wantContest, c.wantTask, c.wantOK)
		}
	}
}

func TestIsTaskURL(t *testing.T) {
	cases := []struct {
		in   string
		want bool
	}{
		{"https://atcoder.jp/contests/abc457/tasks/abc457_d", true},
		{"atcoder.jp/contests/abc457/tasks/abc457_d", true},
		{"http://example.com", true},
		{"abc457", false},
		{"d", false},
		{"", false},
	}
	for _, c := range cases {
		if got := IsTaskURL(c.in); got != c.want {
			t.Errorf("IsTaskURL(%q) = %v, want %v", c.in, got, c.want)
		}
	}
}

func TestLetter(t *testing.T) {
	cases := []struct {
		in, want string
		wantErr  bool
	}{
		{"d", "d", false},
		{"D", "d", false},
		{"abc457_d", "d", false},
		{"abc457_D", "d", false},
		{"abc457_", "", true},
		{"", "", true},
	}
	for _, c := range cases {
		got, err := Letter(c.in)
		if c.wantErr {
			if err == nil {
				t.Errorf("Letter(%q) = %q, want error", c.in, got)
			}
			continue
		}
		if err != nil {
			t.Errorf("Letter(%q) returned unexpected error: %v", c.in, err)
		}
		if got != c.want {
			t.Errorf("Letter(%q) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestShiftLetter(t *testing.T) {
	cases := []struct {
		in      string
		delta   int
		want    string
		wantErr error
	}{
		{"d", 1, "e", nil},
		{"d", -1, "c", nil},
		{"a", 1, "b", nil},
		{"z", -1, "y", nil},
		{"a", 0, "a", nil},
		{"a", -1, "", ErrLetterBound},
		{"z", 1, "", ErrLetterBound},
		{"xy", 1, "", ErrLetterShape},
		{"", 1, "", ErrLetterShape},
		{"D", 1, "", ErrLetterShape},
		{"1", 1, "", ErrLetterShape},
	}
	for _, c := range cases {
		got, err := ShiftLetter(c.in, c.delta)
		if c.wantErr != nil {
			if !errors.Is(err, c.wantErr) {
				t.Errorf("ShiftLetter(%q, %d) err = %v, want %v", c.in, c.delta, err, c.wantErr)
			}
			continue
		}
		if err != nil {
			t.Errorf("ShiftLetter(%q, %d) returned unexpected error: %v", c.in, c.delta, err)
		}
		if got != c.want {
			t.Errorf("ShiftLetter(%q, %d) = %q, want %q", c.in, c.delta, got, c.want)
		}
	}
}

func TestShiftContest(t *testing.T) {
	cases := []struct {
		in      string
		delta   int
		want    string
		wantErr error
	}{
		{"abc457", 1, "abc458", nil},
		{"abc457", -1, "abc456", nil},
		{"ABC457", 1, "abc458", nil},
		{"abc099", 1, "abc100", nil},
		{"abc009", 1, "abc010", nil},
		{"abc1", -1, "", ErrContestBound},
		{"abc1", 1, "abc2", nil},
		{"abc", 1, "", ErrContestShape},
		{"dp", 1, "", ErrContestShape},
		{"", 1, "", ErrContestShape},
		{"abc457x", 1, "", ErrContestShape},
		{"arc183", 1, "arc184", nil},
		{"agc065", 1, "agc066", nil},
	}
	for _, c := range cases {
		got, err := ShiftContest(c.in, c.delta)
		if c.wantErr != nil {
			if !errors.Is(err, c.wantErr) {
				t.Errorf("ShiftContest(%q, %d) err = %v, want %v", c.in, c.delta, err, c.wantErr)
			}
			continue
		}
		if err != nil {
			t.Errorf("ShiftContest(%q, %d) returned unexpected error: %v", c.in, c.delta, err)
		}
		if got != c.want {
			t.Errorf("ShiftContest(%q, %d) = %q, want %q", c.in, c.delta, got, c.want)
		}
	}
}

func TestWithContestNum(t *testing.T) {
	cases := []struct {
		in      string
		n       int
		want    string
		wantErr error
	}{
		{"abc457", 123, "abc123", nil},
		{"abc457", 5, "abc005", nil},
		{"abc457", 1000, "abc1000", nil},
		{"abc457", 1, "abc001", nil},
		{"ABC457", 5, "abc005", nil},
		{"abc457", 0, "", ErrContestBound},
		{"abc457", -3, "", ErrContestBound},
		{"arc183", 7, "arc007", nil},
		{"dp", 1, "", ErrContestShape},
		{"", 1, "", ErrContestShape},
	}
	for _, c := range cases {
		got, err := WithContestNum(c.in, c.n)
		if c.wantErr != nil {
			if !errors.Is(err, c.wantErr) {
				t.Errorf("WithContestNum(%q, %d) err = %v, want %v", c.in, c.n, err, c.wantErr)
			}
			continue
		}
		if err != nil {
			t.Errorf("WithContestNum(%q, %d) unexpected error: %v", c.in, c.n, err)
		}
		if got != c.want {
			t.Errorf("WithContestNum(%q, %d) = %q, want %q", c.in, c.n, got, c.want)
		}
	}
}

func TestSplitContestID(t *testing.T) {
	cases := []struct {
		in         string
		wantPrefix string
		wantNum    string
		wantOK     bool
	}{
		{"abc457", "abc", "457", true},
		{"ABC099", "abc", "099", true},
		{"arc100", "arc", "100", true},
		{"xyz", "", "", false},
		{"abc", "", "", false},
		{"adt_2026_06_15_2000", "", "", false},
		{"", "", "", false},
	}
	for _, c := range cases {
		gotP, gotN, gotOK := SplitContestID(c.in)
		if gotP != c.wantPrefix || gotN != c.wantNum || gotOK != c.wantOK {
			t.Errorf("SplitContestID(%q) = (%q, %q, %v), want (%q, %q, %v)",
				c.in, gotP, gotN, gotOK, c.wantPrefix, c.wantNum, c.wantOK)
		}
	}
}

func TestContestSolutionPath(t *testing.T) {
	cases := []struct {
		contest, task, want string
		wantErr             bool
	}{
		{"abc457", "d", "abc/457/d.py", false},
		{"abc457", "abc457_d", "abc/457/d.py", false},
		{"ABC457", "D", "abc/457/d.py", false},
		{"abc999", "g", "abc/999/g.py", false},
		{"arc170", "d", "arc/170/d.py", false},
		{"agc065", "a", "agc/065/a.py", false},
		{"abc", "d", "", true},
		{"adt_2026_06_15_2000", "g", "", true},
		{"abc457", "", "", true},
	}
	for _, c := range cases {
		got, err := Contest{}.SolutionPath(c.contest, c.task)
		if c.wantErr {
			if err == nil {
				t.Errorf("Contest.SolutionPath(%q, %q) = %q, want error", c.contest, c.task, got)
			}
			continue
		}
		if err != nil {
			t.Errorf("Contest.SolutionPath(%q, %q) returned unexpected error: %v", c.contest, c.task, err)
		}
		if got != c.want {
			t.Errorf("Contest.SolutionPath(%q, %q) = %q, want %q", c.contest, c.task, got, c.want)
		}
	}
}

func TestExerciseSolutionPath(t *testing.T) {
	fixed := time.Date(2026, 6, 9, 12, 0, 0, 0, time.Local)
	e := Exercise{Today: fixed}
	got, err := e.SolutionPath("abc457", "d")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	want := "exercise/2026/06/09/abc457_d.py"
	if got != want {
		t.Errorf("Exercise.SolutionPath = %q, want %q", got, want)
	}
}

func TestKnown(t *testing.T) {
	for _, n := range Names() {
		if !Known(n) {
			t.Errorf("Known(%q) = false, want true (Names に含まれる)", n)
		}
	}
	for _, n := range []string{"", "junk", "auto", "abc", "ABC", "arc"} {
		if Known(n) {
			t.Errorf("Known(%q) = true, want false", n)
		}
	}
}

func TestResolve(t *testing.T) {
	cases := []struct {
		name                         string
		flag, env, cfg               string
		wantName, wantValue, wantSrc string
		wantErr                      bool
	}{
		{"flag wins", "contest", "exercise", "exercise", "contest", "contest", "flag", false},
		{"env over config", "", "exercise", "contest", "exercise", "exercise", "env", false},
		{"config when no flag/env", "", "", "contest", "contest", "contest", "config", false},
		{"empty env ignored", "", "", "contest", "contest", "contest", "config", false},
		{"all empty -> exercise", "", "", "", "exercise", "exercise", "default", false},
		{"invalid flag", "junk", "", "", "", "junk", "flag", true},
		{"invalid env", "", "junk", "", "", "junk", "env", true},
		{"invalid config", "", "", "junk", "", "junk", "config", true},
		{"auto removed", "auto", "", "", "", "auto", "flag", true},
		{"abc removed", "abc", "", "", "", "abc", "flag", true},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			m, value, source, err := Resolve(c.flag, c.env, c.cfg)
			if value != c.wantValue {
				t.Errorf("value = %q, want %q", value, c.wantValue)
			}
			if source != c.wantSrc {
				t.Errorf("source = %q, want %q", source, c.wantSrc)
			}
			if c.wantErr {
				if err == nil {
					t.Errorf("Resolve(...) = %v, want error", m)
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if m.Name() != c.wantName {
				t.Errorf("mode = %q, want %q", m.Name(), c.wantName)
			}
		})
	}
}

func TestParse(t *testing.T) {
	cases := []struct {
		name, wantName string
		wantErr        bool
	}{
		{"", "exercise", false},
		{"exercise", "exercise", false},
		{"contest", "contest", false},
		{"auto", "", true},
		{"abc", "", true},
		{"junk", "", true},
	}
	for _, c := range cases {
		m, err := Parse(c.name)
		if c.wantErr {
			if err == nil {
				t.Errorf("Parse(%q) = %v, want error", c.name, m)
			}
			continue
		}
		if err != nil {
			t.Errorf("Parse(%q) returned unexpected error: %v", c.name, err)
		}
		if m.Name() != c.wantName {
			t.Errorf("Parse(%q).Name() = %q, want %q", c.name, m.Name(), c.wantName)
		}
	}
}
