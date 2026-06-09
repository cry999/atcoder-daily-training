// Package atcoder は AtCoder への認証付きアクセス (ログイン・セッション保存・
// 提出一覧の取得) を担う。提出の取得元は Source インターフェースで抽象化し、
// 当面は認証あり (/submissions/me) を実装する。将来 no-auth (kenkoooo API) を
// 別実装として差し替えられるようにしてある。
//
// セキュリティ方針:
//   - パスワードは保存しない。ログイン時のみ使い、cookie 取得後は破棄する。
//   - 保存するのは REVEL_SESSION cookie と user 名のみ。session.json は 0600。
package atcoder

import (
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/cry999/atcoder-daily-training/internal/config"
)

// ErrNoSession は session.json が存在しない (未ログイン) ことを表す。
var ErrNoSession = errors.New("not logged in")

// Session は保存された認証情報。パスワードは含めない。
type Session struct {
	User          string    `json:"user"`
	SessionCookie string    `json:"session_cookie"` // "REVEL_SESSION=..." の 1 本
	SavedAt       time.Time `json:"saved_at"`
}

// LoadSession は session.json を読む。ファイルが無ければ ErrNoSession を返す。
func LoadSession() (*Session, error) {
	path := config.SessionPath()
	b, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return nil, ErrNoSession
		}
		return nil, fmt.Errorf("セッションの読み込みに失敗: %s: %w", path, err)
	}
	var s Session
	if err := json.Unmarshal(b, &s); err != nil {
		return nil, fmt.Errorf("セッションの解析に失敗: %s: %w", path, err)
	}
	if s.SessionCookie == "" {
		return nil, ErrNoSession
	}
	return &s, nil
}

// SaveSession は session.json を 0600 / 親 dir 0700 で書き込む。
func SaveSession(s *Session) error {
	path := config.SessionPath()
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return fmt.Errorf("設定 dir の作成に失敗: %w", err)
	}
	b, err := json.MarshalIndent(s, "", "  ")
	if err != nil {
		return err
	}
	// 0600 で作成。既存ファイルがあっても権限を絞り直す。
	if err := os.WriteFile(path, b, 0o600); err != nil {
		return fmt.Errorf("セッションの保存に失敗: %s: %w", path, err)
	}
	return os.Chmod(path, 0o600)
}

// DeleteSession は session.json を削除する。無ければ no-op (nil)。
func DeleteSession() error {
	path := config.SessionPath()
	if err := os.Remove(path); err != nil && !os.IsNotExist(err) {
		return fmt.Errorf("セッションの削除に失敗: %s: %w", path, err)
	}
	return nil
}
