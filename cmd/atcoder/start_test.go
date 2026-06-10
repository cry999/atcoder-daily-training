package main

import "testing"

func TestKeyToAction(t *testing.T) {
	cases := []struct {
		b    byte
		want startAction
	}{
		{'q', actQuit},
		{'Q', actQuit},
		{0x03, actQuit}, // Ctrl+C (raw モードではバイトで届く)
		{'i', actInteractive},
		{'I', actInteractive},
		{'r', actNone},
		{'\n', actNone},
		{' ', actNone},
		{'x', actNone},
	}
	for _, c := range cases {
		if got := keyToAction(c.b); got != c.want {
			t.Errorf("keyToAction(%q=0x%02x) = %d, want %d", c.b, c.b, got, c.want)
		}
	}
}
