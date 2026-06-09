package layout

import (
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

func TestABCSolutionPath(t *testing.T) {
	cases := []struct {
		contest, task, want string
		wantErr             bool
	}{
		{"abc457", "d", "abc/457/d.py", false},
		{"abc457", "abc457_d", "abc/457/d.py", false},
		{"abc457", "D", "abc/457/d.py", false},
		{"abc999", "g", "abc/999/g.py", false},
		{"arc170", "d", "", true},          // 非 ABC
		{"abc", "d", "", true},             // 数字なし
		{"abc457", "", "", true},           // 空 task
	}
	for _, c := range cases {
		got, err := ABC{}.SolutionPath(c.contest, c.task)
		if c.wantErr {
			if err == nil {
				t.Errorf("ABC.SolutionPath(%q, %q) = %q, want error", c.contest, c.task, got)
			}
			continue
		}
		if err != nil {
			t.Errorf("ABC.SolutionPath(%q, %q) returned unexpected error: %v", c.contest, c.task, err)
		}
		if got != c.want {
			t.Errorf("ABC.SolutionPath(%q, %q) = %q, want %q", c.contest, c.task, got, c.want)
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
	for _, n := range []string{"", "junk", "ABC", "arc"} {
		if Known(n) {
			t.Errorf("Known(%q) = true, want false", n)
		}
	}
}

func TestResolve(t *testing.T) {
	cases := []struct {
		name                         string
		flag, env, cfg, contest      string
		wantName, wantValue, wantSrc string
		wantErr                      bool
	}{
		// precedence: flag > env > config > auto。
		{"flag wins", "abc", "exercise", "exercise", "arc170", "abc", "abc", "flag", false},
		{"env over config", "", "exercise", "abc", "abc457", "exercise", "exercise", "env", false},
		{"config when no flag/env", "", "", "abc", "arc170", "abc", "abc", "config", false},
		{"empty env ignored", "", "", "exercise", "abc457", "exercise", "exercise", "config", false},
		{"all empty -> auto abc", "", "", "", "abc457", "abc", "auto", "default", false},
		{"all empty -> auto exercise", "", "", "", "arc170", "exercise", "auto", "default", false},
		{"auto flag explicit", "auto", "abc", "abc", "arc170", "exercise", "auto", "flag", false},
		{"invalid flag", "junk", "", "", "abc457", "", "junk", "flag", true},
		{"invalid env", "", "junk", "", "abc457", "", "junk", "env", true},
		{"invalid config", "", "", "junk", "abc457", "", "junk", "config", true},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			lay, value, source, err := Resolve(c.flag, c.env, c.cfg, c.contest)
			if value != c.wantValue {
				t.Errorf("value = %q, want %q", value, c.wantValue)
			}
			if source != c.wantSrc {
				t.Errorf("source = %q, want %q", source, c.wantSrc)
			}
			if c.wantErr {
				if err == nil {
					t.Errorf("Resolve(...) = %v, want error", lay)
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if lay.Name() != c.wantName {
				t.Errorf("layout = %q, want %q", lay.Name(), c.wantName)
			}
		})
	}
}

func TestParse(t *testing.T) {
	cases := []struct {
		name, contest, wantName string
		wantErr                 bool
	}{
		{"", "abc457", "abc", false},
		{"auto", "abc457", "abc", false},
		{"auto", "arc170", "exercise", false},
		{"abc", "anything", "abc", false},
		{"exercise", "abc457", "exercise", false},
		{"junk", "abc457", "", true},
	}
	for _, c := range cases {
		lay, err := Parse(c.name, c.contest)
		if c.wantErr {
			if err == nil {
				t.Errorf("Parse(%q, %q) = %v, want error", c.name, c.contest, lay)
			}
			continue
		}
		if err != nil {
			t.Errorf("Parse(%q, %q) returned unexpected error: %v", c.name, c.contest, err)
		}
		if lay.Name() != c.wantName {
			t.Errorf("Parse(%q, %q).Name() = %q, want %q", c.name, c.contest, lay.Name(), c.wantName)
		}
	}
}
