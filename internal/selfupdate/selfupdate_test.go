package selfupdate

import (
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

func TestReadCurrentModuleFallback(t *testing.T) {
	// テストバイナリは VCS 情報の有無が環境依存だが、ReadCurrent は必ず
	// 非空の Module を返す (取得不能なら DefaultModule)。
	cur := ReadCurrent()
	if cur.Module == "" {
		t.Errorf("ReadCurrent().Module is empty, want non-empty (fallback to %q)", DefaultModule)
	}
}
