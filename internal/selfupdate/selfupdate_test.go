package selfupdate

import (
	"os"
	"runtime/debug"
	"strings"
	"testing"
	"time"
)

func TestPseudoSha(t *testing.T) {
	cases := []struct {
		version string
		want    string
	}{
		{"v0.0.0-20260609084444-44f73cc537c7", "44f73cc537c7"},
		{"v0.0.0-20260101000000-abcdef012345", "abcdef012345"},
		{"v1.2.3", ""},        // タグ版: sha なし
		{"v1.2.3-rc1", ""},    // プレリリース: 末尾が 12 桁 hex でない
		{"v0.0.0-44f73c", ""}, // 短すぎる
		{"", ""},
	}
	for _, c := range cases {
		if got := pseudoSha(c.version); got != c.want {
			t.Errorf("pseudoSha(%q) = %q, want %q", c.version, got, c.want)
		}
	}
}

func TestShortSha(t *testing.T) {
	if got := shortSha("44f73cc537c7abcdef"); got != "44f73cc537c7" {
		t.Errorf("shortSha = %q, want 44f73cc537c7", got)
	}
	if got := shortSha("abc"); got != "abc" {
		t.Errorf("shortSha(short) = %q, want abc", got)
	}
}

func TestAvailable(t *testing.T) {
	t0 := time.Date(2026, 6, 5, 0, 0, 0, 0, time.UTC)
	t1 := time.Date(2026, 6, 9, 0, 0, 0, 0, time.UTC)
	latest := Latest{Version: "v0.0.0-20260609000000-def567890abc", Sha: "def567890abc", Time: t1}

	cases := []struct {
		name string
		cur  Current
		l    Latest
		want bool
	}{
		{"unknown current -> available", Current{Known: false}, latest, true},
		{"dirty build -> available", Current{Known: true, Revision: "def567890abcffff", Time: t1, Modified: true}, latest, true},
		{"same sha -> up to date", Current{Known: true, Revision: "def567890abcffff", Time: t1}, latest, false},
		{"older time, diff sha -> available", Current{Known: true, Revision: "abc123abc123ffff", Time: t0}, latest, true},
		{"newer time than latest -> up to date", Current{Known: true, Revision: "fff000fff000ffff", Time: t1.Add(time.Hour)}, latest, false},
	}
	for _, c := range cases {
		if got := Available(c.cur, c.l); got != c.want {
			t.Errorf("%s: Available = %v, want %v", c.name, got, c.want)
		}
	}
}

func TestLocalUpdate(t *testing.T) {
	rev := "44f73cc537c7abcdef0123456789abcdef012345"
	cur := Current{Known: true, Revision: rev}
	cases := []struct {
		name    string
		cur     Current
		local   LocalSource
		wantAv  bool
		wantSub string // reason に含まれるべき断片
	}{
		{"not a repo", cur, LocalSource{Known: false}, false, "not in a repo"},
		{"dirty wins over sha match", cur, LocalSource{Known: true, Revision: rev, Dirty: true}, true, "uncommitted"},
		{"installed unknown", Current{Known: false}, LocalSource{Known: true, Revision: rev}, true, "unknown"},
		{"modified build", Current{Known: true, Revision: rev, Modified: true}, LocalSource{Known: true, Revision: rev}, true, "modified tree"},
		{"local ahead", cur, LocalSource{Known: true, Revision: "ffffffffffffffff0000000000000000ffffffff"}, true, "ahead"},
		{"matches", cur, LocalSource{Known: true, Revision: rev}, false, "matches"},
	}
	for _, c := range cases {
		gotAv, reason := LocalUpdate(c.cur, c.local)
		if gotAv != c.wantAv {
			t.Errorf("%s: available = %v, want %v", c.name, gotAv, c.wantAv)
		}
		if !strings.Contains(reason, c.wantSub) {
			t.Errorf("%s: reason = %q, want substring %q", c.name, reason, c.wantSub)
		}
	}
}

func TestClassifyRemote(t *testing.T) {
	t0 := time.Date(2026, 6, 5, 0, 0, 0, 0, time.UTC)
	t1 := time.Date(2026, 6, 9, 0, 0, 0, 0, time.UTC)
	latest := Latest{Version: "v0.0.0-20260609000000-def567890abc", Sha: "def567890abc", Time: t1}
	cases := []struct {
		name string
		cur  Current
		want RemoteState
	}{
		{"unknown -> indeterminate", Current{Known: false}, RemoteIndeterminate},
		{"same sha -> up to date", Current{Known: true, Revision: "def567890abcffff", Time: t0}, RemoteUpToDate},
		{"older time -> update available", Current{Known: true, Revision: "abc123abc123ffff", Time: t0}, RemoteUpdateAvailable},
		{"newer time -> installed newer", Current{Known: true, Revision: "fff000fff000ffff", Time: t1.Add(time.Hour)}, RemoteInstalledNewer},
		{"dirty but newer time -> installed newer", Current{Known: true, Revision: "fff000fff000ffff", Time: t1.Add(time.Hour), Modified: true}, RemoteInstalledNewer},
		{"equal time -> up to date", Current{Known: true, Revision: "fff000fff000ffff", Time: t1}, RemoteUpToDate},
	}
	for _, c := range cases {
		if got := ClassifyRemote(c.cur, latest); got != c.want {
			t.Errorf("%s: ClassifyRemote = %v, want %v", c.name, got, c.want)
		}
	}
}

func TestGoEnvSetsGoprivate(t *testing.T) {
	const mod = "github.com/cry999/atcoder-daily-training"
	get := func(env []string) (string, bool) {
		for _, kv := range env {
			if strings.HasPrefix(kv, "GOPRIVATE=") {
				return strings.TrimPrefix(kv, "GOPRIVATE="), true
			}
		}
		return "", false
	}

	// GOPRIVATE 未設定なら新規に自モジュールを入れる。
	os.Unsetenv("GOPRIVATE")
	if v, ok := get(goEnv(mod)); !ok || v != mod {
		t.Errorf("unset case: GOPRIVATE=%q (ok=%v), want %q", v, ok, mod)
	}

	// 既存の GOPRIVATE は保全して追記する。
	t.Setenv("GOPRIVATE", "example.com/foo")
	if v, _ := get(goEnv(mod)); v != "example.com/foo,"+mod {
		t.Errorf("append case: GOPRIVATE=%q, want %q", v, "example.com/foo,"+mod)
	}

	// 既に含まれていれば重複させない。
	t.Setenv("GOPRIVATE", mod)
	if v, _ := get(goEnv(mod)); v != mod {
		t.Errorf("dedup case: GOPRIVATE=%q, want %q", v, mod)
	}
}

func TestReadCurrentModuleFallback(t *testing.T) {
	// テストバイナリは VCS 情報の有無が環境依存だが、ReadCurrent は必ず
	// 非空の Module を返す (取得不能なら DefaultModule)。
	cur := ReadCurrent()
	if cur.Module == "" {
		t.Errorf("ReadCurrent().Module is empty, want non-empty (fallback to %q)", DefaultModule)
	}
}

func TestPseudoTime(t *testing.T) {
	got, ok := pseudoTime("v0.0.0-20260609101134-4c7e3b9c0d74")
	want := time.Date(2026, 6, 9, 10, 11, 34, 0, time.UTC)
	if !ok || !got.Equal(want) {
		t.Errorf("pseudoTime = %v (ok=%v), want %v", got, ok, want)
	}
	if _, ok := pseudoTime("v1.2.3"); ok {
		t.Errorf("pseudoTime(tag) ok=true, want false")
	}
}

func TestCurrentFromBuildInfo(t *testing.T) {
	const mod = "github.com/cry999/atcoder-daily-training"

	// 1) 作業ツリービルド: vcs.* スタンプから読む (フル sha)。
	vcs := &debug.BuildInfo{
		Main: debug.Module{Path: mod, Version: "(devel)"},
		Settings: []debug.BuildSetting{
			{Key: "vcs.revision", Value: "4c7e3b9c0d748e8738f908effec6678ddb328223"},
			{Key: "vcs.time", Value: "2026-06-09T10:11:34Z"},
			{Key: "vcs.modified", Value: "false"},
		},
	}
	if c := currentFromBuildInfo(vcs); !c.Known || c.ShortRev() != "4c7e3b9c0d74" || c.Modified {
		t.Errorf("vcs build: %+v (short=%s), want known 4c7e3b9c0d74 clean", c, c.ShortRev())
	}

	// 2) `go install @latest` ビルド: vcs.* が無く pseudo-version から補う。
	pseudo := &debug.BuildInfo{
		Main: debug.Module{Path: mod, Version: "v0.0.0-20260609101134-4c7e3b9c0d74"},
	}
	c := currentFromBuildInfo(pseudo)
	if !c.Known {
		t.Fatalf("pseudo build: Known=false, want true (fallback to Main.Version)")
	}
	if c.ShortRev() != "4c7e3b9c0d74" {
		t.Errorf("pseudo build: ShortRev=%s, want 4c7e3b9c0d74", c.ShortRev())
	}
	if want := time.Date(2026, 6, 9, 10, 11, 34, 0, time.UTC); !c.Time.Equal(want) {
		t.Errorf("pseudo build: Time=%v, want %v", c.Time, want)
	}

	// 同じ pseudo を最新と比べたら「最新」(update 後の再インストール無限ループを防ぐ)。
	latest := Latest{Sha: "4c7e3b9c0d74", Time: c.Time}
	if Available(c, latest) {
		t.Errorf("pseudo build vs same latest: Available=true, want false (already up to date)")
	}
}
