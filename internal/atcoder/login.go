package atcoder

import (
	"fmt"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"strings"
	"time"

	"github.com/antchfx/htmlquery"
	"golang.org/x/net/html"
)

const (
	baseURL   = "https://atcoder.jp"
	loginURL  = baseURL + "/login"
	userAgent = "atcoder-status/0.1 (+https://github.com/cry999/atcoder-daily-training)"
)

// Login は username/password で AtCoder にログインし、認証済み Session を返す。
// パスワードは内部でのみ使い、戻り値には含めない (cookie だけを保持する)。
//
// フロー (online-judge-tools と同方式):
//  1. GET /login で pre-auth の REVEL_SESSION を受け、隠し csrf_token を抽出。
//  2. POST /login に username/password/csrf_token を form 送信 (同 jar)。
//  3. ログイン必須ページが /login へ 302 されないことでログイン成否を判定。
//  4. jar の REVEL_SESSION を取り出して Session にする。
func Login(user, password string) (*Session, error) {
	jar, err := cookiejar.New(nil)
	if err != nil {
		return nil, err
	}
	// リダイレクトは自前で見たいので追従しない (302 でも Set-Cookie は jar に入る)。
	client := &http.Client{
		Jar:     jar,
		Timeout: 20 * time.Second,
		CheckRedirect: func(*http.Request, []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}

	csrf, err := fetchCSRFToken(client)
	if err != nil {
		return nil, err
	}

	form := url.Values{
		"username":   {user},
		"password":   {password},
		"csrf_token": {csrf},
	}
	req, err := http.NewRequest(http.MethodPost, loginURL, strings.NewReader(form.Encode()))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("User-Agent", userAgent)
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("ログインリクエストに失敗: %w", err)
	}
	resp.Body.Close()

	// 成否判定: ログイン必須ページが 200 で返れば成功、/login へ 302 なら失敗。
	if ok, err := loggedIn(client); err != nil {
		return nil, err
	} else if !ok {
		return nil, fmt.Errorf("ログインに失敗しました (ユーザ名かパスワードが違う可能性があります)")
	}

	cookie := revelSession(jar)
	if cookie == "" {
		return nil, fmt.Errorf("ログインに失敗しました (セッション cookie を取得できませんでした)")
	}
	return &Session{
		User:          user,
		SessionCookie: cookie,
		SavedAt:       time.Now(),
	}, nil
}

// fetchCSRFToken は GET /login からフォームの隠し csrf_token を抽出する。
func fetchCSRFToken(client *http.Client) (string, error) {
	req, err := http.NewRequest(http.MethodGet, loginURL, nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("User-Agent", userAgent)
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("ログインページの取得に失敗: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("ログインページの取得に失敗: 予期しないステータス %d", resp.StatusCode)
	}

	doc, err := htmlquery.Parse(resp.Body)
	if err != nil {
		return "", fmt.Errorf("ログインページの解析に失敗: %w", err)
	}
	return extractCSRF(doc)
}

// extractCSRF はパース済みのログインフォームから隠し csrf_token を取り出す純粋関数。
// HTTP 依存が無いため単体テストしやすい (fetchCSRFToken から分離)。
func extractCSRF(doc *html.Node) (string, error) {
	node := htmlquery.FindOne(doc, `//input[@name="csrf_token"]`)
	if node == nil {
		return "", fmt.Errorf("csrf_token が見つかりませんでした")
	}
	token := htmlquery.SelectAttr(node, "value")
	if token == "" {
		return "", fmt.Errorf("csrf_token が空でした")
	}
	return token, nil
}

// loggedIn は client (jar 込み) がログイン状態かを、ログイン必須ページ
// (/settings) が 200 で返るか /login へ 302 されるかで判定する。
func loggedIn(client *http.Client) (bool, error) {
	req, err := http.NewRequest(http.MethodGet, baseURL+"/settings", nil)
	if err != nil {
		return false, err
	}
	req.Header.Set("User-Agent", userAgent)
	resp, err := client.Do(req)
	if err != nil {
		return false, fmt.Errorf("ログイン状態の確認に失敗: %w", err)
	}
	defer resp.Body.Close()
	// 未ログインだと /login へ 302。ログイン済みなら 200。
	return resp.StatusCode == http.StatusOK, nil
}

// revelSession は jar から atcoder.jp の REVEL_SESSION を "name=value" 形で返す。
func revelSession(jar *cookiejar.Jar) string {
	u, _ := url.Parse(baseURL)
	for _, c := range jar.Cookies(u) {
		if c.Name == "REVEL_SESSION" {
			return c.Name + "=" + c.Value
		}
	}
	return ""
}
