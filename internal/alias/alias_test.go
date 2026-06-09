package alias

import (
	"reflect"
	"testing"
)

func TestExpand(t *testing.T) {
	builtins := map[string]bool{"update": true, "test": true, "status": true}
	isBuiltin := func(s string) bool { return builtins[s] }

	cases := []struct {
		name    string
		args    []string
		aliases map[string]string
		want    []string
	}{
		{
			"simple expansion",
			[]string{"upd-lo"},
			map[string]string{"upd-lo": "update --local"},
			[]string{"update", "--local"},
		},
		{
			"extra args appended",
			[]string{"upd-lo", "--check"},
			map[string]string{"upd-lo": "update --local"},
			[]string{"update", "--local", "--check"},
		},
		{
			"builtin wins over alias of same name",
			[]string{"test", "abc457"},
			map[string]string{"test": "update --local"},
			[]string{"test", "abc457"},
		},
		{
			"unknown name passes through untouched",
			[]string{"nope", "x"},
			map[string]string{"upd-lo": "update --local"},
			[]string{"nope", "x"},
		},
		{
			"recursive alias -> alias",
			[]string{"u"},
			map[string]string{"u": "upd-lo", "upd-lo": "update --local"},
			[]string{"update", "--local"},
		},
		{
			"no aliases at all",
			[]string{"status", "abc457"},
			map[string]string{},
			[]string{"status", "abc457"},
		},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got, err := Expand(c.args, c.aliases, isBuiltin)
			if err != nil {
				t.Fatalf("Expand error: %v", err)
			}
			if !reflect.DeepEqual(got, c.want) {
				t.Errorf("Expand(%v) = %v, want %v", c.args, got, c.want)
			}
		})
	}
}

func TestExpandLoop(t *testing.T) {
	isBuiltin := func(string) bool { return false }
	// a -> b -> a のループは検出して error。
	_, err := Expand([]string{"a"}, map[string]string{"a": "b", "b": "a"}, isBuiltin)
	if err == nil {
		t.Errorf("Expand on a<->b loop returned nil error, want loop error")
	}
	// 自己ループ a -> "a x"。
	if _, err := Expand([]string{"a"}, map[string]string{"a": "a x"}, isBuiltin); err == nil {
		t.Errorf("Expand on self-loop returned nil error, want loop error")
	}
}

func TestExpandEmptyAlias(t *testing.T) {
	isBuiltin := func(s string) bool { return s == "test" }
	if _, err := Expand([]string{"x"}, map[string]string{"x": "   "}, isBuiltin); err == nil {
		t.Errorf("empty alias returned nil error, want error")
	}
}

func TestExpandNoArgs(t *testing.T) {
	got, err := Expand(nil, map[string]string{"x": "test"}, func(string) bool { return false })
	if err != nil || len(got) != 0 {
		t.Errorf("Expand(nil) = %v, %v; want empty, nil", got, err)
	}
}
