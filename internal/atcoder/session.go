// Package atcoder は AtCoder の認証セッション (REVEL_SESSION cookie) を
// 取り込み・検証・永続化し、認証付きリクエストを組み立てる (要件 062)。
// login / logout / 将来の submit・status がここを経由する層境界であり、
// セッションの消費側はこのパッケージの公開 API だけを入口にする。
//
// セッションは秘匿情報 (認証 cookie) なので、キャッシュ (cachepath) や設定
// (config) とは分離し、データ領域 ($XDG_DATA_HOME/atcoder-tools/session.toml)
// に 0600 で置く。永続化の規約は usagelog / chatlog を踏襲する。
package atcoder

import (
	"errors"
	"os"
	"path/filepath"
	"time"

	"github.com/BurntSushi/toml"
)

// AppName はデータ領域のアプリ識別子 (internal/cachepath / usagelog / chatlog と揃える)。
const AppName = "atcoder-tools"

// FileName はセッションファイル名。
const FileName = "session.toml"

// Session はログイン済みセッション (cookie + メタ)。TOML タグは session.toml の
// スキーマ (要件 062) に対応する。後続機能がフィールドを足しても後方互換に読める。
type Session struct {
	RevelSession string    `toml:"revel_session"` // REVEL_SESSION cookie 値 (秘匿。表示・ログ出力しない)
	Username     string    `toml:"username"`      // login 時に解決したユーザ名
	LoggedInAt   time.Time `toml:"logged_in_at"`  // login 実行時刻
}

var (
	// ErrNoSession は保存済みセッションが無い (未ログイン) ことを表す。
	ErrNoSession = errors.New("no session")
	// ErrUnauthenticated は cookie が無効・期限切れ (login ページへリダイレクト) を表す。
	ErrUnauthenticated = errors.New("cookie invalid or expired")
	// ErrChallenge は応答が Cloudflare チャレンジだったことを表す。
	ErrChallenge = errors.New("cloudflare challenge")
)

// dataBase は XDG_DATA_HOME (未設定なら ~/.local/share、最終 fallback ./.local/share)。
// キャッシュ (cachepath) と違い、セッションは再生成不能な秘匿情報なので消えない領域に置く。
func dataBase() string {
	if d := os.Getenv("XDG_DATA_HOME"); d != "" {
		return d
	}
	if home, err := os.UserHomeDir(); err == nil {
		return filepath.Join(home, ".local", "share")
	}
	return filepath.Join(".local", "share")
}

// Path は session.toml の保存先 ($XDG_DATA_HOME/atcoder-tools/session.toml) を返す。
// パスは存在するとは限らない。error 返しは将来の解決失敗に備えた層境界の約束で、
// 現状は常に nil。
func Path() (string, error) {
	return filepath.Join(dataBase(), AppName, FileName), nil
}

// Load は保存済みセッションを読む。無ければ (nil, ErrNoSession)。
func Load() (*Session, error) {
	path, err := Path()
	if err != nil {
		return nil, err
	}
	var s Session
	if _, err := toml.DecodeFile(path, &s); err != nil {
		if os.IsNotExist(err) {
			return nil, ErrNoSession
		}
		return nil, err
	}
	return &s, nil
}

// Save は session.toml に書く。親ディレクトリは 0700、ファイルは 0600 で作る
// (cookie は秘匿情報。同一マシンの別ユーザから読めないようにする)。既存があれば上書き。
func Save(s *Session) error {
	path, err := Path()
	if err != nil {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}
	f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0o600)
	if err != nil {
		return err
	}
	defer f.Close()
	// 既存ファイルを上書きするときは O_CREATE の mode が効かないので明示的に締め直す。
	if err := f.Chmod(0o600); err != nil {
		return err
	}
	return toml.NewEncoder(f).Encode(s)
}

// Clear は session.toml を削除する (無ければ no-op)。
func Clear() error {
	path, err := Path()
	if err != nil {
		return err
	}
	if err := os.Remove(path); err != nil && !os.IsNotExist(err) {
		return err
	}
	return nil
}
