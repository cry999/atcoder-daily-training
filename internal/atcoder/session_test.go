package atcoder

import (
	"context"
	"errors"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"testing"
	"time"
)

// TestPathUnderDataHome は session.toml が $XDG_DATA_HOME/atcoder-tools/ 配下に
// 組み立てられることを固定する。
func TestPathUnderDataHome(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", "/tmp/xyz")
	got, err := Path()
	if err != nil {
		t.Fatalf("Path() error: %v", err)
	}
	want := filepath.Join("/tmp/xyz", AppName, FileName)
	if got != want {
		t.Fatalf("Path() = %q, want %q", got, want)
	}
}

// TestLoadNoSession は未ログイン (ファイル無し) で ErrNoSession を返すことを固定する。
func TestLoadNoSession(t *testing.T) {
	t.Setenv("XDG_DATA_HOME", t.TempDir())
	if _, err := Load(); !errors.Is(err, ErrNoSession) {
		t.Fatalf("Load() error = %v, want ErrNoSession", err)
	}
}

// TestSaveLoadRoundTrip は Save → Load でフィールドが往復すること、ファイルが 0600 で
// 作られること、Clear が冪等に消せることを固定する。
func TestSaveLoadRoundTrip(t *testing.T) {
	dir := t.TempDir()
	t.Setenv("XDG_DATA_HOME", dir)

	at := time.Date(2026, 7, 1, 12, 34, 56, 0, time.FixedZone("JST", 9*3600))
	in := &Session{RevelSession: "secret-cookie", Username: "cry999", LoggedInAt: at}
	if err := Save(in); err != nil {
		t.Fatalf("Save() error: %v", err)
	}

	path, _ := Path()
	if runtime.GOOS != "windows" {
		fi, err := os.Stat(path)
		if err != nil {
			t.Fatalf("stat session.toml: %v", err)
		}
		if perm := fi.Mode().Perm(); perm != 0o600 {
			t.Fatalf("session.toml perm = %o, want 600", perm)
		}
	}

	got, err := Load()
	if err != nil {
		t.Fatalf("Load() error: %v", err)
	}
	if got.RevelSession != in.RevelSession || got.Username != in.Username {
		t.Fatalf("round trip mismatch: got %+v, want %+v", got, in)
	}
	if !got.LoggedInAt.Equal(at) {
		t.Fatalf("LoggedInAt = %v, want %v", got.LoggedInAt, at)
	}

	// Clear は存在すれば消し、再度呼んでも no-op (冪等)。
	if err := Clear(); err != nil {
		t.Fatalf("Clear() error: %v", err)
	}
	if err := Clear(); err != nil {
		t.Fatalf("Clear() (idempotent) error: %v", err)
	}
	if _, err := Load(); !errors.Is(err, ErrNoSession) {
		t.Fatalf("after Clear Load() = %v, want ErrNoSession", err)
	}
}

// TestNewRequestSetsCookieAndUA は認証リクエストが REVEL_SESSION cookie と標準
// User-Agent を載せることを固定する (cookie は環境変数ではなくヘッダで運ぶ)。
func TestNewRequestSetsCookieAndUA(t *testing.T) {
	s := &Session{RevelSession: "abc123"}
	req, err := s.NewRequest(context.Background(), http.MethodGet, "https://atcoder.jp/settings", nil)
	if err != nil {
		t.Fatalf("NewRequest() error: %v", err)
	}
	c, err := req.Cookie("REVEL_SESSION")
	if err != nil {
		t.Fatalf("cookie REVEL_SESSION missing: %v", err)
	}
	if c.Value != "abc123" {
		t.Fatalf("cookie value = %q, want abc123", c.Value)
	}
	if req.Header.Get("User-Agent") != userAgent {
		t.Fatalf("User-Agent = %q, want %q", req.Header.Get("User-Agent"), userAgent)
	}
}

// TestNewRequestNoCookieWhenEmpty は cookie 未設定なら Cookie ヘッダを付けないことを固定する。
func TestNewRequestNoCookieWhenEmpty(t *testing.T) {
	s := &Session{}
	req, err := s.NewRequest(context.Background(), http.MethodGet, "https://atcoder.jp/", nil)
	if err != nil {
		t.Fatalf("NewRequest() error: %v", err)
	}
	if _, err := req.Cookie("REVEL_SESSION"); err == nil {
		t.Fatalf("expected no REVEL_SESSION cookie for empty session")
	}
}

// TestExtractUsername は /users/<name> リンクからユーザ名を取れることを固定する。
func TestExtractUsername(t *testing.T) {
	cases := []struct{ body, want string }{
		{`<a href="/users/cry999" class="username">cry999</a>`, "cry999"},
		{`no user link here`, ""},
		{`<a href="/users/user_name-1">x</a>`, "user_name-1"},
	}
	for _, c := range cases {
		if got := extractUsername([]byte(c.body)); got != c.want {
			t.Fatalf("extractUsername(%q) = %q, want %q", c.body, got, c.want)
		}
	}
}
