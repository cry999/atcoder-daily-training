package config

import (
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// Keys は既知キーを返す (少なくとも test.side_by_side を含む)。
func TestKeysContainsSideBySide(t *testing.T) {
	found := false
	for _, k := range Keys() {
		if k == "test.side_by_side" {
			found = true
		}
	}
	if !found {
		t.Fatalf("Keys() should contain test.side_by_side, got %v", Keys())
	}
}

// set した値が get で読め、config.toml にも書かれている。
func TestSetThenGet(t *testing.T) {
	writeConfig(t, "")
	if err := Set("test.side_by_side", "true"); err != nil {
		t.Fatalf("Set failed: %v", err)
	}
	v, err := Get("test.side_by_side")
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}
	if v != "true" {
		t.Fatalf("expected get to return true, got %q", v)
	}
	// ファイルが作られている。
	if _, err := os.Stat(Path()); err != nil {
		t.Fatalf("expected config.toml to be created: %v", err)
	}
}

// set は config.toml が無くても親 dir ごと作成する。
func TestSetCreatesFile(t *testing.T) {
	base := t.TempDir()
	t.Setenv("XDG_CONFIG_HOME", base)
	if _, err := os.Stat(Path()); !os.IsNotExist(err) {
		t.Fatalf("precondition: config.toml should not exist yet")
	}
	if err := Set("test.side_by_side", "true"); err != nil {
		t.Fatalf("Set failed: %v", err)
	}
	if _, err := os.Stat(Path()); err != nil {
		t.Fatalf("config.toml should exist after Set: %v", err)
	}
}

// set は既存の未知キー・他セクションを保全する (前方/後方互換)。
func TestSetPreservesUnknownKeys(t *testing.T) {
	writeConfig(t, "[test]\nfuture_key = 42\n\n[other]\nx = \"keep\"\n")
	if err := Set("test.side_by_side", "true"); err != nil {
		t.Fatalf("Set failed: %v", err)
	}
	raw, err := os.ReadFile(Path())
	if err != nil {
		t.Fatal(err)
	}
	s := string(raw)
	for _, want := range []string{"future_key", "other", "keep", "side_by_side"} {
		if !strings.Contains(s, want) {
			t.Fatalf("expected written config to preserve %q, got:\n%s", want, s)
		}
	}
}

// 未知キーは ErrUnknownKey。
func TestGetSetUnknownKey(t *testing.T) {
	writeConfig(t, "")
	if _, err := Get("bogus.key"); !errors.Is(err, ErrUnknownKey) {
		t.Fatalf("Get bogus.key: expected ErrUnknownKey, got %v", err)
	}
	if err := Set("bogus.key", "x"); !errors.Is(err, ErrUnknownKey) {
		t.Fatalf("Set bogus.key: expected ErrUnknownKey, got %v", err)
	}
}

// bool キーに非 bool を set すると ErrInvalidValue。
func TestSetInvalidValue(t *testing.T) {
	writeConfig(t, "")
	if err := Set("test.side_by_side", "notabool"); !errors.Is(err, ErrInvalidValue) {
		t.Fatalf("expected ErrInvalidValue, got %v", err)
	}
}

// 既存 config が文法エラーのとき set は ErrParse。
func TestSetParseErrorOnBrokenFile(t *testing.T) {
	writeConfig(t, "[test]\nside_by_side = \n")
	if err := Set("test.side_by_side", "true"); !errors.Is(err, ErrParse) {
		t.Fatalf("expected ErrParse, got %v", err)
	}
}

// ValueCandidates は bool キーで true/false を返す。
func TestValueCandidates(t *testing.T) {
	got := ValueCandidates("test.side_by_side")
	if len(got) != 2 {
		t.Fatalf("expected 2 candidates for a bool key, got %v", got)
	}
	if ValueCandidates("bogus.key") != nil {
		t.Fatal("expected nil candidates for unknown key")
	}
}

// All は全キー × 現在値を返す。
func TestAll(t *testing.T) {
	writeConfig(t, "[test]\nside_by_side = true\n")
	kvs, err := All()
	if err != nil {
		t.Fatal(err)
	}
	if len(kvs) != len(Keys()) {
		t.Fatalf("All should return one entry per key: got %d, keys %d", len(kvs), len(Keys()))
	}
	for _, kv := range kvs {
		if kv.Key == "test.side_by_side" && kv.Value != "true" {
			t.Fatalf("expected test.side_by_side = true, got %q", kv.Value)
		}
	}
}

// 念のため: Path は AppName/FileName を含む。
func TestPathShape(t *testing.T) {
	base := t.TempDir()
	t.Setenv("XDG_CONFIG_HOME", base)
	want := filepath.Join(base, AppName, FileName)
	if Path() != want {
		t.Fatalf("Path() = %q, want %q", Path(), want)
	}
}
