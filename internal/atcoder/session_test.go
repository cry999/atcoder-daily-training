package atcoder

import (
	"errors"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/config"
)

func TestSession_RoundTrip(t *testing.T) {
	t.Setenv("XDG_CONFIG_HOME", t.TempDir())

	// 未保存なら ErrNoSession。
	if _, err := LoadSession(); !errors.Is(err, ErrNoSession) {
		t.Fatalf("LoadSession before save = %v, want ErrNoSession", err)
	}

	want := &Session{
		User:          "takeharak999",
		SessionCookie: "REVEL_SESSION=abc123",
		SavedAt:       time.Now().Truncate(time.Second),
	}
	if err := SaveSession(want); err != nil {
		t.Fatalf("SaveSession: %v", err)
	}

	got, err := LoadSession()
	if err != nil {
		t.Fatalf("LoadSession: %v", err)
	}
	if got.User != want.User || got.SessionCookie != want.SessionCookie {
		t.Fatalf("LoadSession = %+v, want %+v", got, want)
	}
}

func TestSession_FilePermIs0600(t *testing.T) {
	t.Setenv("XDG_CONFIG_HOME", t.TempDir())
	if err := SaveSession(&Session{User: "u", SessionCookie: "REVEL_SESSION=x"}); err != nil {
		t.Fatalf("SaveSession: %v", err)
	}
	fi, err := os.Stat(config.SessionPath())
	if err != nil {
		t.Fatalf("stat: %v", err)
	}
	if perm := fi.Mode().Perm(); perm != 0o600 {
		t.Fatalf("session.json perm = %o, want 600", perm)
	}
}

func TestSession_DeleteThenLoad(t *testing.T) {
	t.Setenv("XDG_CONFIG_HOME", t.TempDir())
	if err := SaveSession(&Session{User: "u", SessionCookie: "REVEL_SESSION=x"}); err != nil {
		t.Fatalf("SaveSession: %v", err)
	}
	if err := DeleteSession(); err != nil {
		t.Fatalf("DeleteSession: %v", err)
	}
	if _, err := LoadSession(); !errors.Is(err, ErrNoSession) {
		t.Fatalf("LoadSession after delete = %v, want ErrNoSession", err)
	}
	// 二重削除は no-op。
	if err := DeleteSession(); err != nil {
		t.Fatalf("DeleteSession (二重): %v", err)
	}
}

func TestSession_EmptyCookieIsNoSession(t *testing.T) {
	t.Setenv("XDG_CONFIG_HOME", t.TempDir())
	path := config.SessionPath()
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	// cookie 空のファイルは未ログイン扱い。
	if err := os.WriteFile(path, []byte(`{"user":"u","session_cookie":""}`), 0o600); err != nil {
		t.Fatalf("write: %v", err)
	}
	if _, err := LoadSession(); !errors.Is(err, ErrNoSession) {
		t.Fatalf("LoadSession with empty cookie = %v, want ErrNoSession", err)
	}
}
