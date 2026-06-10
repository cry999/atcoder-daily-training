package cliargs

import (
	"reflect"
	"testing"
)

func TestSplit(t *testing.T) {
	cases := []struct {
		name    string
		args    []string
		flags   []string
		posArgs []string
	}{
		{
			name:    "位置引数が先頭 (従来の並び)",
			args:    []string{"abc457", "--task", "d"},
			flags:   []string{"--task", "d"},
			posArgs: []string{"abc457"},
		},
		{
			name:    "フラグが先頭・位置引数が後ろ",
			args:    []string{"--task", "d", "abc457"},
			flags:   []string{"--task", "d"},
			posArgs: []string{"abc457"},
		},
		{
			name:    "フラグと位置引数が混在",
			args:    []string{"-s", "abc457", "--task", "d", "--timeout", "5s"},
			flags:   []string{"-s", "--task", "d", "--timeout", "5s"},
			posArgs: []string{"abc457"},
		},
		{
			name:    "値内包 --task=d は次を消費しない",
			args:    []string{"--task=d", "abc457"},
			flags:   []string{"--task=d"},
			posArgs: []string{"abc457"},
		},
		{
			name:    "bool フラグの直後は独立に位置引数",
			args:    []string{"--refresh", "abc457", "--task", "d"},
			flags:   []string{"--refresh", "--task", "d"},
			posArgs: []string{"abc457"},
		},
		{
			name:    "stdin marker - は --in の値 (位置引数にしない)",
			args:    []string{"abc457", "--in", "-", "--task", "d"},
			flags:   []string{"--in", "-", "--task", "d"},
			posArgs: []string{"abc457"},
		},
		{
			name:    "-- 終端: 以降は位置引数",
			args:    []string{"--task", "d", "--", "-weird", "abc457"},
			flags:   []string{"--task", "d"},
			posArgs: []string{"-weird", "abc457"},
		},
		{
			name:    "短フラグ -c は値を取る",
			args:    []string{"-c", "01", "abc457"},
			flags:   []string{"-c", "01"},
			posArgs: []string{"abc457"},
		},
		{
			name:    "未知フラグは bool 扱い (次を消費しない)",
			args:    []string{"--bogus", "abc457"},
			flags:   []string{"--bogus"},
			posArgs: []string{"abc457"},
		},
		{
			name:    "value-flag の値欠落 (末尾) でも壊れない",
			args:    []string{"abc457", "--task"},
			flags:   []string{"--task"},
			posArgs: []string{"abc457"},
		},
		{
			name:    "複数位置引数は出現順を保持",
			args:    []string{"set", "--", "x"},
			flags:   nil,
			posArgs: []string{"set", "x"},
		},
		{
			name:    "空",
			args:    nil,
			flags:   nil,
			posArgs: nil,
		},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			gotFlags, gotPos := Split(c.args)
			if !reflect.DeepEqual(gotFlags, c.flags) {
				t.Errorf("flags = %#v, want %#v", gotFlags, c.flags)
			}
			if !reflect.DeepEqual(gotPos, c.posArgs) {
				t.Errorf("positionals = %#v, want %#v", gotPos, c.posArgs)
			}
		})
	}
}

func TestTakesValue(t *testing.T) {
	for _, f := range []string{"--task", "-c", "--timeout", "--tolerance", "-l"} {
		if !TakesValue(f) {
			t.Errorf("TakesValue(%q) = false, want true", f)
		}
	}
	for _, f := range []string{"--refresh", "-s", "--watch", "--bogus", "abc457"} {
		if TakesValue(f) {
			t.Errorf("TakesValue(%q) = true, want false", f)
		}
	}
}
