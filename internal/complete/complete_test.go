package complete

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

// setup は補完用の一時リポジトリルートを作る。キャッシュは空の一時 dir に逃がして
// (XDG_CACHE_HOME)、テストが手元のキャッシュに依存しないようにする。
func setup(t *testing.T) string {
	t.Helper()
	root := t.TempDir()
	// abc/457/{a,b}.py を用意 (contest 候補 + letter 候補のソース)。
	mustMkdir(t, filepath.Join(root, "abc", "457"))
	mustTouch(t, filepath.Join(root, "abc", "457", "a.py"))
	mustTouch(t, filepath.Join(root, "abc", "457", "b.py"))
	mustMkdir(t, filepath.Join(root, "arc", "180"))
	t.Setenv("XDG_CACHE_HOME", t.TempDir())  // キャッシュは空に
	t.Setenv("XDG_CONFIG_HOME", t.TempDir()) // config (alias 等) も空に隔離
	return root
}

func mustMkdir(t *testing.T, p string) {
	t.Helper()
	if err := os.MkdirAll(p, 0o755); err != nil {
		t.Fatal(err)
	}
}

func mustTouch(t *testing.T, p string) {
	t.Helper()
	if err := os.WriteFile(p, nil, 0o644); err != nil {
		t.Fatal(err)
	}
}

func TestComplete(t *testing.T) {
	root := setup(t)
	tests := []struct {
		name  string
		words []string
		want  []string
	}{
		{"empty -> all subcommands", nil, Subcommands()},
		{"subcommand prefix", []string{"te"}, []string{"test"}},
		{"subcommand prefix s", []string{"s"}, []string{"start", "stats"}},
		{"start takes a contest", []string{"start", "ab"}, []string{"abc457"}},
		{"flag prefix", []string{"test", "--la"}, []string{"--layout"}},
		{"layout values", []string{"test", "abc457", "--layout", ""}, []string{"auto", "abc", "exercise"}},
		{"contest from dirs", []string{"test", "ab"}, []string{"abc457"}},
		{"contest arc", []string{"test", "ar"}, []string{"arc180"}},
		{"task letters from files", []string{"test", "abc457", "--task", ""}, []string{"a", "b"}},
		{"task default when unknown", []string{"test", "abc999", "--task", ""}, []string{"a", "b", "c", "d", "e", "f", "g"}},
		{"completion shells", []string{"completion", ""}, []string{"bash", "zsh", "fish"}},
		{"new mode", []string{"new", ""}, []string{"abc"}},
		{"new contest after abc", []string{"new", "abc", "ab"}, []string{"abc457"}},
		{"stats has no contest", []string{"stats", "ab"}, nil},
		{"subcommand prefix up -> update", []string{"up"}, []string{"update"}},
		{"subcommand prefix ver -> version", []string{"ver"}, []string{"version"}},
		{"update --check flag", []string{"update", "--ch"}, []string{"--check"}},
		{"version has no flags/contest", []string{"version", "ab"}, nil},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got := values(Complete(root, tc.words))
			if !reflect.DeepEqual(got, tc.want) {
				t.Errorf("Complete(%q) = %v, want %v", tc.words, got, tc.want)
			}
		})
	}
}

// TestCompleteDescriptions は静的候補に説明が付き、動的候補は説明なしであることを確認する。
func TestCompleteDescriptions(t *testing.T) {
	root := setup(t)

	// サブコマンドは説明付き。
	for _, c := range Complete(root, []string{"te"}) {
		if c.Value == "test" && c.Desc == "" {
			t.Errorf("subcommand %q has empty Desc, want a description", c.Value)
		}
	}
	// フラグは説明付き。
	for _, c := range Complete(root, []string{"test", "--la"}) {
		if c.Value == "--layout" && c.Desc == "" {
			t.Errorf("flag %q has empty Desc, want a description", c.Value)
		}
	}
	// stats の --last (010 で追加) がフラグ候補に居て説明を持つ。
	var sawLast bool
	for _, c := range Complete(root, []string{"stats", "--l"}) {
		if c.Value == "--last" {
			sawLast = true
			if c.Desc == "" {
				t.Errorf("--last has empty Desc, want a description")
			}
		}
	}
	if !sawLast {
		t.Errorf("stats flags should include --last")
	}
	// 動的候補 (contest_id) は説明なし。
	for _, c := range Complete(root, []string{"test", "ab"}) {
		if c.Value == "abc457" && c.Desc != "" {
			t.Errorf("dynamic candidate %q should have empty Desc, got %q", c.Value, c.Desc)
		}
	}
}

func TestCompleteNeverPanics(t *testing.T) {
	root := setup(t)
	// 壊れた / 想定外のトークン列でも panic せず候補 (nil 可) を返す。
	for _, words := range [][]string{
		{"test"},
		{"test", "abc457", "--task"},
		{"--", "weird"},
		{"completion"},
	} {
		_ = Complete(root, words)
	}
}

// alias がサブコマンド候補に出て、config unset とそのキー補完が効くこと。
func TestCompleteAliasAndUnset(t *testing.T) {
	root := setup(t)
	cfgDir := filepath.Join(os.Getenv("XDG_CONFIG_HOME"), "atcoder-daily-training")
	mustMkdir(t, cfgDir)
	if err := os.WriteFile(filepath.Join(cfgDir, "config.toml"),
		[]byte("[alias]\nupd-lo = \"update --local\"\n"), 0o644); err != nil {
		t.Fatal(err)
	}

	// サブコマンド位置に alias 名が説明付きで出る。
	var sawAlias bool
	for _, c := range Complete(root, []string{"up"}) {
		if c.Value == "upd-lo" {
			sawAlias = true
			if c.Desc == "" {
				t.Errorf("alias candidate missing description")
			}
		}
	}
	if !sawAlias {
		t.Errorf("subcommand completion should include alias 'upd-lo'")
	}

	// config の sub-subcommand に unset が出る。
	if got := values(Complete(root, []string{"config", "un"})); !reflect.DeepEqual(got, []string{"unset"}) {
		t.Errorf("config 'un' completion = %v, want [unset]", got)
	}

	// config unset のキー補完に alias.upd-lo が出る。
	var sawKey bool
	for _, c := range Complete(root, []string{"config", "unset", "alias."}) {
		if c.Value == "alias.upd-lo" {
			sawKey = true
		}
	}
	if !sawKey {
		t.Errorf("config unset key completion should include alias.upd-lo")
	}
}
