package config

import (
	"errors"
	"testing"
	"time"
)

func TestTargetSetGetUnset(t *testing.T) {
	writeConfig(t, "")
	if err := Set("target.abc.d", "35m"); err != nil {
		t.Fatalf("Set failed: %v", err)
	}
	v, err := Get("target.abc.d")
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}
	if v != "35m" {
		t.Fatalf("expected 35m, got %q", v)
	}
	// TargetDuration ヘルパで duration が引ける。
	cfg, err := Load()
	if err != nil {
		t.Fatal(err)
	}
	d, ok := cfg.TargetDuration("abc", "d")
	if !ok || d != 35*time.Minute {
		t.Fatalf("TargetDuration mismatch: %v %v", d, ok)
	}
	// 未設定は ok=false。
	if _, ok := cfg.TargetDuration("arc", "d"); ok {
		t.Fatal("unset target should be ok=false")
	}
	// Unset で消える。
	if err := Unset("target.abc.d"); err != nil {
		t.Fatalf("Unset failed: %v", err)
	}
	if _, err := Get("target.abc.d"); !errors.Is(err, ErrUnknownKey) {
		t.Fatalf("expected ErrUnknownKey after unset, got %v", err)
	}
}

func TestTargetInvalidDuration(t *testing.T) {
	writeConfig(t, "")
	if err := Set("target.abc.d", "soon"); !errors.Is(err, ErrInvalidValue) {
		t.Fatalf("expected ErrInvalidValue for bad duration, got %v", err)
	}
}

func TestTargetMalformedKey(t *testing.T) {
	writeConfig(t, "")
	// letter が 2 文字 / 階層不足はキー形不正 (exit 2 相当)。
	if err := Set("target.abc.dd", "35m"); !errors.Is(err, ErrInvalidValue) {
		t.Fatalf("expected ErrInvalidValue for bad letter, got %v", err)
	}
	if err := Set("target.abc", "35m"); !errors.Is(err, ErrInvalidValue) {
		t.Fatalf("expected ErrInvalidValue for missing letter, got %v", err)
	}
}

func TestTargetPreservesOtherKeys(t *testing.T) {
	writeConfig(t, "")
	if err := Set("test.side_by_side", "true"); err != nil {
		t.Fatal(err)
	}
	if err := Set("target.abc.d", "35m"); err != nil {
		t.Fatal(err)
	}
	if err := Set("target.arc.c", "1h"); err != nil {
		t.Fatal(err)
	}
	// typed キーが保全されている。
	if v, _ := Get("test.side_by_side"); v != "true" {
		t.Fatalf("typed key clobbered: %q", v)
	}
	// All() に target が両方含まれる。
	kvs, err := All()
	if err != nil {
		t.Fatal(err)
	}
	seen := map[string]string{}
	for _, kv := range kvs {
		seen[kv.Key] = kv.Value
	}
	if seen["target.abc.d"] != "35m" || seen["target.arc.c"] != "1h" {
		t.Fatalf("All() missing target entries: %v", seen)
	}
}
