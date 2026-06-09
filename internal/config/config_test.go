package config

import (
	"os"
	"path/filepath"
	"testing"
)

// writeConfig は XDG_CONFIG_HOME を temp dir に向け、その下に config.toml を書く。
// 内容が "" のときはファイルを作らない (不在ケース)。
func writeConfig(t *testing.T, content string) {
	t.Helper()
	base := t.TempDir()
	t.Setenv("XDG_CONFIG_HOME", base)
	if content == "" {
		return
	}
	dir := filepath.Join(base, AppName)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, FileName), []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

// ファイルが無いのは正常: ゼロ値 Config + nil error。
func TestLoadMissingReturnsZeroValue(t *testing.T) {
	writeConfig(t, "")
	cfg, err := Load()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cfg.Test.SideBySide {
		t.Fatal("expected SideBySide to default to false when no config file exists")
	}
}

// [test] side_by_side = true を読める。
func TestLoadSideBySide(t *testing.T) {
	writeConfig(t, "[test]\nside_by_side = true\n")
	cfg, err := Load()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !cfg.Test.SideBySide {
		t.Fatal("expected SideBySide to be true")
	}
}

// 未知のキー/セクションは無視して継続 (前方/後方互換)。
func TestLoadIgnoresUnknownKeys(t *testing.T) {
	writeConfig(t, "[test]\nside_by_side = true\nfuture_key = 1\n\n[run]\nsomething = \"x\"\n")
	cfg, err := Load()
	if err != nil {
		t.Fatalf("unexpected error for unknown keys: %v", err)
	}
	if !cfg.Test.SideBySide {
		t.Fatal("expected SideBySide to be true even with unknown keys present")
	}
}

// TOML 文法エラーは error を返す (呼び出し側で exit 2)。
func TestLoadParseError(t *testing.T) {
	writeConfig(t, "[test]\nside_by_side = \n") // 値が無い不正な TOML
	if _, err := Load(); err == nil {
		t.Fatal("expected a parse error for malformed TOML")
	}
}
