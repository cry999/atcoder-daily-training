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

// layout キーは set → get で round-trip し、config.toml に書かれる。
func TestLayoutSetThenGet(t *testing.T) {
	writeConfig(t, "")
	if err := Set("layout", "abc"); err != nil {
		t.Fatalf("Set layout failed: %v", err)
	}
	v, err := Get("layout")
	if err != nil {
		t.Fatalf("Get layout failed: %v", err)
	}
	if v != "abc" {
		t.Fatalf("expected layout = abc, got %q", v)
	}
}

// 未設定の layout は get / show 上 auto に見える (実効既定値)。
func TestLayoutDefaultsToAuto(t *testing.T) {
	writeConfig(t, "")
	v, err := Get("layout")
	if err != nil {
		t.Fatalf("Get layout failed: %v", err)
	}
	if v != "auto" {
		t.Fatalf("expected unset layout to read as auto, got %q", v)
	}
}

// 不正なレイアウト値は ErrInvalidValue (書き込まない)。
func TestLayoutInvalidValue(t *testing.T) {
	writeConfig(t, "")
	if err := Set("layout", "junk"); !errors.Is(err, ErrInvalidValue) {
		t.Fatalf("expected ErrInvalidValue, got %v", err)
	}
}

// layout は enum キーなので ValueCandidates が auto/abc/exercise を返す。
func TestLayoutValueCandidates(t *testing.T) {
	got := ValueCandidates("layout")
	want := []string{"abc", "auto", "exercise"} // ソート済み
	if len(got) != len(want) {
		t.Fatalf("ValueCandidates(layout) = %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("ValueCandidates(layout) = %v, want %v", got, want)
		}
	}
}

// layout はトップレベルキーなので、set しても [test] セクションを壊さない。
func TestLayoutPreservesTestSection(t *testing.T) {
	writeConfig(t, "[test]\nside_by_side = true\n")
	if err := Set("layout", "exercise"); err != nil {
		t.Fatalf("Set layout failed: %v", err)
	}
	v, err := Get("test.side_by_side")
	if err != nil {
		t.Fatalf("Get test.side_by_side failed: %v", err)
	}
	if v != "true" {
		t.Fatalf("expected test.side_by_side preserved as true, got %q", v)
	}
}

// editor_nvim_remote は set → get で round-trip する (要件 041)。
func TestEditorNvimRemoteSetThenGet(t *testing.T) {
	writeConfig(t, "")
	if err := Set("editor_nvim_remote", "tab"); err != nil {
		t.Fatalf("Set editor_nvim_remote failed: %v", err)
	}
	v, err := Get("editor_nvim_remote")
	if err != nil {
		t.Fatalf("Get editor_nvim_remote failed: %v", err)
	}
	if v != "tab" {
		t.Fatalf("expected editor_nvim_remote = tab, got %q", v)
	}
}

// 未設定の editor_nvim_remote は get 上 current に見える (実効既定値)。
func TestEditorNvimRemoteDefaultsToCurrent(t *testing.T) {
	writeConfig(t, "")
	v, err := Get("editor_nvim_remote")
	if err != nil {
		t.Fatalf("Get editor_nvim_remote failed: %v", err)
	}
	if v != "current" {
		t.Fatalf("expected unset editor_nvim_remote to read as current, got %q", v)
	}
}

// current/tab 以外は ErrInvalidValue (書き込まない)。
func TestEditorNvimRemoteInvalidValue(t *testing.T) {
	writeConfig(t, "")
	if err := Set("editor_nvim_remote", "window"); !errors.Is(err, ErrInvalidValue) {
		t.Fatalf("expected ErrInvalidValue, got %v", err)
	}
}

// editor_nvim_remote は enum キーなので ValueCandidates が current/tab を返す。
func TestEditorNvimRemoteValueCandidates(t *testing.T) {
	got := ValueCandidates("editor_nvim_remote")
	want := []string{"current", "tab"} // ソート済み
	if len(got) != len(want) {
		t.Fatalf("ValueCandidates(editor_nvim_remote) = %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("ValueCandidates(editor_nvim_remote) = %v, want %v", got, want)
		}
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

// alias.<name> は set → get で往復でき、config.toml の [alias] に書かれる。
func TestAliasSetGetUnset(t *testing.T) {
	writeConfig(t, "")
	if err := Set("alias.upd-lo", "update --local"); err != nil {
		t.Fatalf("Set alias failed: %v", err)
	}
	v, err := Get("alias.upd-lo")
	if err != nil || v != "update --local" {
		t.Fatalf("Get alias = %q, %v; want %q", v, err, "update --local")
	}
	// Aliases() に反映される。
	aliases, err := Aliases()
	if err != nil || aliases["upd-lo"] != "update --local" {
		t.Fatalf("Aliases() = %v, %v", aliases, err)
	}
	// show (All) に alias.<name> が出る。
	all, _ := All()
	var sawAlias bool
	for _, kv := range all {
		if kv.Key == "alias.upd-lo" && kv.Value == "update --local" {
			sawAlias = true
		}
	}
	if !sawAlias {
		t.Errorf("All() should include alias.upd-lo; got %v", all)
	}
	// unset で消える。
	if err := Unset("alias.upd-lo"); err != nil {
		t.Fatalf("Unset alias failed: %v", err)
	}
	if _, err := Get("alias.upd-lo"); !errors.Is(err, ErrUnknownKey) {
		t.Errorf("Get after unset err = %v, want ErrUnknownKey", err)
	}
}

// 既存の typed セクションを保全しつつ alias を足す。
func TestAliasPreservesTypedKeys(t *testing.T) {
	writeConfig(t, "[test]\nside_by_side = true\n")
	if err := Set("alias.t", "test"); err != nil {
		t.Fatalf("Set alias failed: %v", err)
	}
	if v, _ := Get("test.side_by_side"); v != "true" {
		t.Errorf("typed key clobbered by alias set: side_by_side = %q, want true", v)
	}
}

// 不正な alias 名は ErrInvalidValue。
func TestAliasInvalidName(t *testing.T) {
	writeConfig(t, "")
	for _, key := range []string{"alias.", "alias.a.b", "alias.has space", "alias.dot.dot"} {
		if err := Set(key, "test"); !errors.Is(err, ErrInvalidValue) {
			t.Errorf("Set(%q) err = %v, want ErrInvalidValue", key, err)
		}
	}
}

// 未定義 alias の unset / get は ErrUnknownKey。
func TestAliasUnsetUnknown(t *testing.T) {
	writeConfig(t, "")
	if err := Unset("alias.nope"); !errors.Is(err, ErrUnknownKey) {
		t.Errorf("Unset(alias.nope) err = %v, want ErrUnknownKey", err)
	}
}
