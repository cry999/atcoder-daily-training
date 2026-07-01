package atcoder

import (
	"context"
	"io"
	"net/http"
	"net/http/cookiejar"
	"regexp"
	"strings"
	"time"
)

// userAgent は既存 fetch (internal/testexec/fetch.go, internal/contestmeta/fetch.go)
// と揃えた User-Agent。認証経路でも同じ規約を踏襲する。
const userAgent = "atcoder-test/0.1 (+https://github.com/cry999/atcoder-daily-training)"

// validateURL は login-gated な安定ページ。未認証だと /login へリダイレクトされる。
const validateURL = "https://atcoder.jp/settings"

// NewRequest は cookie と標準 User-Agent を付けた *http.Request を作る。
// 将来の submit/status など認証付き経路の唯一の入口 (層境界)。cookie は
// AddCookie でヘッダに載せ、環境変数や ps から漏れる経路を通さない。
func (s *Session) NewRequest(ctx context.Context, method, url string, body io.Reader) (*http.Request, error) {
	req, err := http.NewRequestWithContext(ctx, method, url, body)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", userAgent)
	req.Header.Set("Accept-Language", "ja,en-US;q=0.9,en;q=0.8")
	if s.RevelSession != "" {
		req.AddCookie(&http.Cookie{Name: "REVEL_SESSION", Value: s.RevelSession})
	}
	return req, nil
}

// userLinkRe はページ内のユーザ本人ページへのリンク (/users/<name>) から
// ユーザ名を取るための正規表現 (ベストエフォート)。
var userLinkRe = regexp.MustCompile(`/users/([A-Za-z0-9_-]+)`)

// Validate は cookie で login-gated ページ (/settings) を GET し、ログイン状態と
// ユーザ名を返す。未認証/期限切れは ErrUnauthenticated、Cloudflare チャレンジは
// ErrChallenge、ネットワーク失敗はそのままの error。検証 GET は 1 回のみ
// (ポーリング・連投はしない。rate limit 配慮)。
func Validate(revelSession string) (username string, err error) {
	s := &Session{RevelSession: revelSession}
	// 検証専用に cookie jar 付きクライアントを組む。リダイレクトは標準挙動に任せ、
	// 最終 URL が /login を含むかで未認証を判定する。
	jar, err := cookiejar.New(nil)
	if err != nil {
		return "", err
	}
	client := &http.Client{Jar: jar, Timeout: 15 * time.Second}

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	req, err := s.NewRequest(ctx, http.MethodGet, validateURL, nil)
	if err != nil {
		return "", err
	}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(io.LimitReader(resp.Body, 1<<20))

	// Cloudflare チャレンジ検出 (best-effort)。cookie 失効・不正時に返りうる。
	if isChallenge(resp, body) {
		return "", ErrChallenge
	}
	// 未認証だと /login?continue=... へリダイレクトされる。最終 URL で判定する。
	if resp.Request != nil && resp.Request.URL != nil && strings.Contains(resp.Request.URL.Path, "/login") {
		return "", ErrUnauthenticated
	}
	if resp.StatusCode != http.StatusOK {
		return "", ErrUnauthenticated
	}
	// ログイン時はページ内にユーザ本人のリンク (/users/<name>) が出る。取れなければ
	// ログイン状態を確証できないので未認証扱いにする (不確かなセッションを保存しない)。
	name := extractUsername(body)
	if name == "" {
		return "", ErrUnauthenticated
	}
	return name, nil
}

// extractUsername は /settings ページ本文からユーザ名を取る (ベストエフォート)。
func extractUsername(body []byte) string {
	m := userLinkRe.FindSubmatch(body)
	if m == nil {
		return ""
	}
	return string(m[1])
}

// isChallenge は応答が Cloudflare チャレンジっぽいかを判定する (best-effort)。
func isChallenge(resp *http.Response, body []byte) bool {
	if resp.Request != nil && resp.Request.URL != nil {
		if strings.Contains(resp.Request.URL.Host, "challenges.cloudflare.com") {
			return true
		}
	}
	if resp.StatusCode == http.StatusForbidden || resp.StatusCode == http.StatusServiceUnavailable {
		if strings.Contains(strings.ToLower(resp.Header.Get("Server")), "cloudflare") {
			return true
		}
	}
	b := string(body)
	return strings.Contains(b, "challenge-platform") || strings.Contains(b, "cf-challenge") || strings.Contains(b, "cf_chl_")
}
