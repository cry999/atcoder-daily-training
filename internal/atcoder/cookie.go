package atcoder

import (
	"fmt"
	"io"
	"net/http"
	"regexp"
	"strings"
	"time"
)

// SessionFromCookie は、ブラウザからコピーした REVEL_SESSION の値から Session を
// 作り、認証が有効かを /settings で検証する。user が空なら認証済みページから
// ユーザ名を best-effort で導出する。
//
// AtCoder のログインページは Cloudflare Turnstile で保護されており username/
// password の programmatic ログインはできない。ログイン後の通常ページは cookie で
// アクセスできるため、ブラウザでログイン (Turnstile はブラウザが解決) して得た
// REVEL_SESSION を取り込む、というのが本関数の役割。
func SessionFromCookie(raw, user string) (*Session, error) {
	cookie := normalizeCookie(raw)
	if cookie == "" {
		return nil, fmt.Errorf("REVEL_SESSION の値を読み取れませんでした")
	}
	ok, derivedUser, err := validateSession(cookie)
	if err != nil {
		return nil, fmt.Errorf("セッションの検証に失敗: %w", err)
	}
	if !ok {
		return nil, fmt.Errorf("このセッション cookie は無効か失効しています (ブラウザでログイン済みの REVEL_SESSION を貼り付けてください)")
	}
	if user == "" {
		user = derivedUser
	}
	return &Session{User: user, SessionCookie: cookie, SavedAt: time.Now()}, nil
}

// normalizeCookie は貼り付けられた入力を "REVEL_SESSION=<value>" 形に整える。
// 入力が値だけ・"REVEL_SESSION=..." 形・"REVEL_SESSION=...; Path=/" 形のいずれでも受ける。
func normalizeCookie(raw string) string {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return ""
	}
	if i := strings.Index(raw, "REVEL_SESSION="); i >= 0 {
		raw = raw[i+len("REVEL_SESSION="):]
	}
	// 末尾の cookie 属性 (; Path=...) や紛れたトークンを落とす。
	if i := strings.IndexAny(raw, "; \t"); i >= 0 {
		raw = raw[:i]
	}
	raw = strings.Trim(raw, `"'`)
	if raw == "" {
		return ""
	}
	return "REVEL_SESSION=" + raw
}

var userScreenNameRe = regexp.MustCompile(`userScreenName\s*=\s*"([^"]+)"`)

// validateSession は cookie でログイン必須ページ (/settings) が 200 を返すか
// (= 認証有効か) を確認し、認証済みページからユーザ名を導出する。
func validateSession(cookie string) (ok bool, user string, err error) {
	status, _, err := getWithCookie(baseURL+"/settings", cookie)
	if err != nil {
		return false, "", err
	}
	if status != http.StatusOK {
		return false, "", nil // 302 (→/login) など = 失効/無効
	}
	// ユーザ名は best-effort (取れなくてもログインは成立させる)。
	if _, body, err := getWithCookie(baseURL+"/", cookie); err == nil {
		if m := userScreenNameRe.FindStringSubmatch(body); m != nil {
			return true, m[1], nil
		}
	}
	return true, "", nil
}

// getWithCookie は cookie を載せて GET し、ステータスと本文を返す (リダイレクト非追従)。
func getWithCookie(url, cookie string) (int, string, error) {
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return 0, "", err
	}
	req.Header.Set("User-Agent", userAgent)
	req.Header.Set("Cookie", cookie)
	client := &http.Client{
		Timeout: 20 * time.Second,
		CheckRedirect: func(*http.Request, []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}
	resp, err := client.Do(req)
	if err != nil {
		return 0, "", err
	}
	defer resp.Body.Close()
	b, _ := io.ReadAll(resp.Body)
	return resp.StatusCode, string(b), nil
}
