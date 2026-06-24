package layout

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
		{"a", -1, "", ErrLetterBound}, // 下限
		{"z", 1, "", ErrLetterBound},  // 上限
		{"xy", 1, "", ErrLetterShape}, // 複数文字
		{"", 1, "", ErrLetterShape},   // 空
		{"D", 1, "", ErrLetterShape},  // 非小文字
		{"1", 1, "", ErrLetterShape},  // 非英字
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
		{"abc099", 1, "abc100", nil}, // ゼロ詰め幅は桁数を下限に保持
		{"abc009", 1, "abc010", nil},
		{"abc1", -1, "", ErrContestBound},   // 1 未満
		{"abc1", 1, "abc2", nil},            // 下限境界 +1
		{"abc", 1, "", ErrContestShape},     // 数字なし
		{"dp", 1, "", ErrContestShape},      // 数字なし
		{"", 1, "", ErrContestShape},        // 空
		{"abc457x", 1, "", ErrContestShape}, // 末尾が数字でない
		{"arc183", 1, "arc184", nil},        // abc 以外の接頭辞
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
		{"abc457", 5, "abc005", nil},     // 桁数 (ゼロ詰め幅) は元を下限に保持
		{"abc457", 1000, "abc1000", nil}, // 桁数は下限なので超過は伸びる
		{"abc457", 1, "abc001", nil},
		{"abc457", 0, "", ErrContestBound}, // 1 未満
		{"abc457", -3, "", ErrContestBound},
		{"arc183", 7, "arc007", nil},   // abc 以外の接頭辞も可
		{"dp", 1, "", ErrContestShape}, // 数字接尾辞なし
		{"", 1, "", ErrContestShape},   // 空
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

func TestContestNum(t *testing.T) {
	cases := []struct {
		in     string
		want   string
		wantOK bool
	}{
		{"abc457", "457", true},
		{"abc099", "099", true},
		{"arc100", "", false}, // abc 以外
		{"xyz", "", false},    // 数字なし
		{"abc", "", false},    // 数字なし
		{"", "", false},
	}
	for _, c := range cases {
		got, ok := ContestNum(c.in)
		if got != c.want || ok != c.wantOK {
			t.Errorf("ContestNum(%q) = (%q, %v), want (%q, %v)", c.in, got, ok, c.want, c.wantOK)
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
		{"arc170", "d", "", true}, // 非 ABC
		{"abc", "d", "", true},    // 数字なし
		{"abc457", "", "", true},  // 空 task
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
